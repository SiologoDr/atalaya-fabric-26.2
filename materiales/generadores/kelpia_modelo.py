"""
Kelpia y sus formas (14-10-2026). Juan, al guardar a Murena: «sigue con otro boss diferente»; y antes: «si debes usar
animales usalos; monstruos, leyendas, mitologias… pero que no sea igual, tenemos que poner nuestro toque».

Kelpia, la Acechadora del Lago (APROBADA el 14-10-2026, solo la C): un monstruo del lago inventado, cargado de
hombros, con una joroba de hueso de la que le caen las algas como una cortina y la cabeza baja con las fauces abiertas
que arden en ambar. Salio del kelpie de las leyendas escocesas; del caballo le quedan la crin de algas y las pezunas.
Juan: «ahora si me gusto, excelente trabajo, este si se acerco a lo que busco». La ficha esta en
materiales/fichas/bosses/kelpia/.

La primera ficha tenia tres caballos de agua (la piel oscura y mojada, la cabeza larga de caballo con las fauces de
monstruo, la crin y la cola de cintas de alga con vejigas que brillan). La A y la B se descartaron y siguen en caballo();
la C se rehizo como monstruo en acechadora().

Las tres formas de la primera ficha:

    A  la Kelpia       encabritada sobre las patas de atras, con las de delante plegadas en alto; verde de agua
    B  el Hipocampo    la parte de atras es una cola de pez que se enrosca en el suelo, con la aleta alzada; las patas
                       de delante acaban en aletas; carmesi
    C  la Acechadora   ya no es un caballo (Juan, 14-10: «me gusta su diseño pero no su anatomia… debes crear
                       monstruos; esta bien usar referencias pero no hacerlas iguales»): un monstruo del lago cargado de
                       hombros, con una joroba de hueso de la que le caen las algas como una cortina, los brazos largos
                       (uno alzado), las patas cortas, las pezunas partidas en tres garras y la cabeza ancha, con cuatro
                       ojos, colgando por delante; ambar
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
ESCALA = 0.62
CABEZA = 1.15
DIENTES = _r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2')

VARIANTES = {
    'A': dict(
        clave='A', nombre='la Kelpia', corto='kelpia',
        piel=_r('06100e', '0c1a16', '142620', '1e342c', '2a463c'),
        mancha=_r('16302a', '22423a', '30564c', '427060', '5a8a7a'),
        alga=_r('1c1206', '30200a', '4a3410', '684a18', '8a6624'),
        casco=_r('16180e', '242818', '363a26', '4c5036', '64684a'),
        neon=('eafff6', '3affb0', '045a3a'),
    ),
    'B': dict(
        clave='B', nombre='el Hipocampo', corto='hipocampo',
        piel=_r('100608', '1a0a0e', '281016', '381820', '4c222c'),
        mancha=_r('321a20', '46262c', '5e343c', '784850', '946068'),
        alga=_r('0c1406', '16220a', '22340e', '304a14', '42621c'),
        casco=_r('080606', '100c0c', '1a1414', '261e1e', '342a2a'),
        neon=('ffe2e6', 'ff2a46', '6a0410'),
    ),
    'C': dict(
        clave='C', nombre='la Acechadora', corto='acechadora',
        piel=_r('0e0a06', '18120a', '241a10', '322418', '443222'),
        mancha=_r('302418', '443424', '5a4632', '745c44', '927658'),
        alga=_r('061410', '0a221c', '10342a', '184a3c', '226250'),
        casco=_r('1a140c', '2a2014', '3c301e', '52422a', '6a5838'),
        hueso=_r('2a2216', '3c3220', '524430', '6a5a40', '847252'),
        neon=('fff2d6', 'ffb02a', '6a3a04'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'kel%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def piel(tw, th, cara, s):
        """La piel mojada: lisa y oscura, con el canto de luz y el de sombra; la tripa, un tono mas clara; y por los
        lados, el agua que le chorrea: hilos claros que bajan desde arriba y acaban en una gota."""
        idx = _bisel(np.full((th, tw), 3 if cara == 'abajo' else 2), 1, 1)
        if cara not in ('arriba', 'abajo') and tw >= 4 and th >= 6:
            rng = random.Random(s * 31 + tw * 7 + th)
            for _ in range(max(1, tw // 12)):
                x = rng.randrange(1, tw - 1)
                largo = rng.randint(max(2, th // 6), max(3, th // 2))
                idx[1:1 + largo, x] = 3
                if 1 + largo < th - 1:
                    idx[1 + largo, x] = 4
        return _imagen(idx, V['piel']), None
    reg('piel', piel)
    reg('casco', jm.liso(V['casco'], 2, 1, 1))

    def hueso(tw, th, cara, s):
        """El hueso de la joroba y de la cara: como el cuerno, en capas de traves, con el canto de arriba claro."""
        ys = np.arange(th)[:, None] + np.zeros((1, tw), int)
        idx = np.where(ys % 4 == 3, 2, 3)
        return _imagen(_bisel(idx, 1, 1), V.get('hueso', V['casco'])), None
    reg('hueso', hueso)
    reg('escama', lambda tw, th, c, s: (_imagen(_bisel(sm._escamas_cara(tw, th, c), 1, 1), V['piel']), None))

    def alga(tw, th, cara, s):
        """La cinta de alga (de traves sobre la lamina): el nervio en medio, que brilla un poco, las bandas y el canto
        oscuro, con una arruga cada pocos pixeles."""
        ys, xs = np.mgrid[0:th, 0:tw]
        u = np.abs((xs + 0.5) / tw - 0.5) * 2
        idx = np.where(u < 0.2, 4, np.where(u < 0.6, 3, np.where(u < 0.86, 2, 1)))
        idx = np.where((ys % 6 == 0) & (u >= 0.2) & (u < 0.86), idx - 1, idx)
        t = _imagen(np.clip(idx, 0, 4), V['alga'])
        nervio = u < 0.2
        t[nervio, :3] = nm._hex(V['neon'][2])
        return t, _emis(t, nervio, 150)
    reg('alga', alga)

    def aleta(tw, th, cara, s):
        """La tela de las aletas: en bandas claras y oscuras, con un radio claro cada pocos pixeles."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 2) % 2 == 0, 3, 2)
        idx = np.where((xs % 6) == 0, 4, idx)
        return _imagen(idx, V['alga']), None
    reg('aleta', aleta)

    def ojo(tw, th, cara, s):
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot((xs - cx) / max(tw / 2, 1), (ys - cy) / max(th / 2, 1))
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((r < 0.5)[..., None], np.array(c_n), np.where((r < 0.9)[..., None], np.array(c_m), np.array(c_h)))
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r < 0.9, 235)
    reg('ojo', ojo)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def boca(tw, th, cara, s):
        """El suelo de la boca: la encia oscura por los bordes, el hondo del neon y un surco claro en medio, con
        arrugas de traves; brilla menos que el paladar para que no parezca un tubo de luz."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        u = (xs + 0.5) / tw
        dd = np.minimum(u, 1 - u) * 2
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        encia = np.array(V['piel'][1])
        col = np.where((dd < 0.34)[..., None], encia,
                       np.where((dd < 0.66)[..., None], np.array(c_h),
                                np.where((dd < 0.86)[..., None], np.array(qm._mezcla(c_h, c_m, 0.55)), np.array(c_m))))
        arruga = (ys.astype(int) % 5 == 0) & (dd >= 0.34)
        col = np.where(arruga[..., None], np.array(c_h), col)
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, dd >= 0.34, 95)
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

    def _hojas_de_dientes(tw, th, colgando):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTES]
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
        return t, None
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, False))

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


def cinta(out, P, ctrl, ancho, giro=0.4, vejigas=2, semilla=0, n=12):
    """Una cinta de alga: una tira a lo largo de la curva que se retuerce poco a poco y se afina en la punta, con
    algunas vejigas que brillan pegadas a ella."""
    ctrl = [np.asarray(c, float) for c in ctrl]
    pts, _, ts = jm.a_lo_largo(ctrl, n, ((0.0, 1.0), (1.0, 1.0)))
    filas = []
    for k, p in enumerate(pts):
        a = pts[min(k + 1, n)] - pts[max(k - 1, 0)]
        t_ = _u(a)
        lado = np.cross(t_, (0.0, 1.0, 0.0))
        if np.linalg.norm(lado) < 0.2:
            lado = np.cross(t_, (1.0, 0.0, 0.0))
        lado = _u(lado)
        normal = np.cross(lado, t_)
        ang = giro * TAU * ts[k]
        lado = lado * math.cos(ang) + normal * math.sin(ang)
        w = ancho / 2 * (0.7 + 0.3 * math.sin(math.pi * min(1.0, ts[k] * 1.4))) * (1.0 if ts[k] < 0.75 else 1.0 - (ts[k] - 0.75) * 3.2)
        filas.append((p - lado * w, p + lado * w))
    for k in range(n):
        (a0, b0), (a1, b1) = filas[k], filas[k + 1]
        L = max(float(np.linalg.norm(pts[k + 1] - pts[k])), 0.4)
        W_ = max(float(np.linalg.norm(b0 - a0)), 0.4)
        lamina(out, (a0, b0, b1, a1), P['alga'], W_, L, semilla=semilla)
        lamina(out, (a1, b1, b0, a0), P['alga'], W_, L, semilla=semilla)
    for j in range(vejigas):
        q = pts[int((0.35 + 0.3 * j) * n)]
        caja(out, vr.T(*q), -0.6, 0.6, -0.6, 0.6, -0.6, 0.6, P['luz'], semilla=semilla + 1)
    return pts


def casco(out, P, a, b, semilla=0):
    """La cuartilla de a (el menudillo) a b y el casco en b: plano en el suelo si toca tierra, o a lo largo de la
    cuartilla si la pata va en el aire."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    jm.tubo(out, [a, b], [1.15, 1.05], [P['piel']], semilla=semilla)
    if b[1] < 1.2:
        caja(out, vr.T(b[0], 0.0, b[2]), -1.7, 1.7, 0.0, 2.1, -1.6, 1.9, P['casco'], semilla=semilla + 1)
    else:
        d = b - a
        M = em.marco(b, d, up=(0.0, 1.0, 0.0) if abs(_u(d)[1]) < 0.8 else (0.0, 0.0, 1.0))
        caja(out, M, -1.45, 1.45, -1.3, 1.6, -0.6, 2.0, P['casco'], semilla=semilla + 1)


def aleta_de_pata(out, P, a, b, semilla=0):
    """En el Hipocampo, la pata de delante acaba en una aleta: cuatro radios abiertos en abanico con la tela entre ellos."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = _u(b - a)
    e = _u(np.cross((1.0, 0.0, 0.0), d))
    tips = [a + _u(d * math.cos(g * D) + e * math.sin(g * D)) * 6.5 for g in (-45, -15, 15, 45)]
    for q in tips:
        jm.tubo(out, [a, q], [0.45, 0.2], [P['casco']], semilla=semilla)
    for t0, t1 in zip(tips, tips[1:]):
        lamina(out, (a, a, t1, t0), P['aleta'], 2.4, 6.0, semilla=semilla + 1)
        lamina(out, (a, a, t0, t1), P['aleta'], 2.4, 6.0, semilla=semilla + 1)


def pata(out, P, puntos, radios, final='casco', semilla=0):
    """Una pata de caballo por los puntos (cadera u hombro, babilla o codo, corvejon o rodilla, menudillo, casco): los
    tubos de bloques, las juntas y al final el casco (o la aleta)."""
    puntos = [np.asarray(p, float) for p in puntos]
    jm.tubo(out, puntos[:-1], radios[:-1], [P['piel']] * (len(puntos) - 2), semilla=semilla)
    for p, r in zip(puntos[1:-1], radios[1:-1]):
        caja(out, vr.T(*p), -r, r, -r, r, -r, r, P['piel'], semilla=semilla + 1)
    if final == 'aleta':
        aleta_de_pata(out, P, puntos[-2], puntos[-1], semilla=semilla + 2)
        return
    casco(out, P, puntos[-2], puntos[-1], semilla=semilla + 2)


def cabeza(out, Mh, P, abre=32.0, orejas='punta', semilla=0):
    """La cabeza de caballo, con el hocico hacia +z y la boca en y=0: la frente con su hueso en la nariz, la cara larga
    que se afina y el morro con los ollares abiertos; los ojos encendidos a los lados bajo una ceja de hueso; las orejas
    echadas atras. Abajo, la quijada con la carrillera redonda de los caballos. Y las fauces de monstruo, abiertas
    desde muy atras: el paladar encendido en escalones, los dientes en hojas, los colmillos, el suelo de la boca
    encendido y el nucleo al fondo. Devuelve la boca."""
    p = P['piel']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -2.5, 0.0, -4.2, 5.0, 4.8, 5.2, p, caras=F, semilla=semilla)                   # la frente
    bm.cubo(out, Mh, -2.1, 0.3, 1.0, 4.2, 3.9, 4.8, p, caras=F, semilla=semilla + 1)               # la cara
    bm.cubo(out, Mh, -1.85, 0.6, 5.8, 3.7, 3.0, 4.0, p, caras=F, semilla=semilla + 2)              # el morro
    bm.cubo(out, Mh, -1.95, 1.0, 8.6, 3.9, 2.9, 1.4, p, caras=F, semilla=semilla + 3)              # la punta, con los ollares
    bm.cubo(out, Mh, -1.3, 4.0, -1.0, 2.6, 0.8, 6.4, p, semilla=semilla + 4)                       # el hueso de la nariz
    bm.cubo(out, Mh, -1.6, 4.8, -3.6, 3.2, 0.6, 3.0, p, semilla=semilla + 4)                       # la nuca
    for s in (1, -1):
        x0 = 2.4 if s > 0 else -2.8
        bm.cubo(out, Mh, x0, 2.6, -2.2, 0.4, 1.3, 1.9, P['ojo'], semilla=semilla + 5)              # los ojos
        bm.cubo(out, Mh, x0 - 0.15 * s, 3.9, -2.8, 0.7, 0.7, 3.0, p, semilla=semilla + 6)          # la ceja
        if orejas == 'aleta':                                                                      # las orejas, aletas
            b = pt(Mh, (s * 1.7, 4.8, -2.6))
            tips = [pt(Mh, (s * 2.4, 9.0, -4.2)), pt(Mh, (s * 3.0, 8.0, -6.6)), pt(Mh, (s * 3.3, 6.0, -8.0)), pt(Mh, (s * 3.2, 4.0, -8.2))]
            for q in tips:
                jm.tubo(out, [b, q], [0.35, 0.15], [P['casco']], semilla=semilla + 7)
            for t0, t1 in zip(tips, tips[1:]):
                lamina(out, (b, b, t1, t0), P['aleta'], 2.4, 5.0, semilla=semilla + 7)
                lamina(out, (b, b, t0, t1), P['aleta'], 2.4, 5.0, semilla=semilla + 7)
        else:
            Mo = Mh @ vr.T(s * 1.5, 5.0, -3.0) @ vr.Rz(-s * 14 * D) @ vr.Rx(-38 * D)              # las orejas, en punta
            caja(out, Mo, -0.7, 0.7, 0.0, 1.6, -0.45, 0.45, p, semilla=semilla + 7)
            caja(out, Mo, -0.95, 0.95, 1.4, 3.2, -0.5, 0.5, p, semilla=semilla + 7)
            caja(out, Mo, -0.5, 0.5, 3.0, 4.6, -0.35, 0.35, p, semilla=semilla + 7)
            caja(out, Mo, -0.2, 0.2, 4.4, 5.4, -0.25, 0.25, p, semilla=semilla + 7)
        x1 = 1.95 if s > 0 else -2.35
        bm.cubo(out, Mh, x1, 2.0, 8.8, 0.4, 1.1, 1.0, P['casco'], semilla=semilla + 8)             # los ollares
    hilera(out, Mh, [(-1.85, 0.0), (-1.85, 9.9), (1.85, 9.9), (1.85, 0.0)], 0.6, -1.1, P['dientes_arriba'], semilla=semilla + 9)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.3, 0.6, 9.2), 2.6, 0.8, (0, -1, 0.05), P, semilla=semilla + 10)
    caja(out, Mh, -1.8, 1.8, -1.6, 0.2, -2.5, -2.2, P['nucleo'], semilla=semilla + 11)
    Mj = Mh @ vr.T(0.0, 0.0, -3.0) @ vr.Rx(abre * D)                                                # la quijada de abajo
    bm.cubo(out, Mj, -2.6, -4.2, -1.2, 5.2, 4.2, 5.6, p, caras={'arriba': P['boca']}, semilla=semilla + 12)   # la carrillera
    bm.cubo(out, Mj, -1.8, -1.6, 4.0, 3.6, 1.6, 8.6, p, caras={'arriba': P['boca']}, semilla=semilla + 13)
    hilera(out, Mj, [(-1.6, 3.0), (-1.6, 12.4), (1.6, 12.4), (1.6, 3.0)], 0.0, 1.0, P['dientes_abajo'], semilla=semilla + 14)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.2, 0.0, 11.8), 2.1, 0.7, (0, 1, 0.05), P, semilla=semilla + 15)
    return pt(Mh, (0.0, -0.6, 4.0))


def crin(out, P, cresta, radios, dorso, estilo='cortina', largo=19.0, semilla=0):
    """La crin de algas, de tres maneras:
       'cortina'  cintas anchas que nacen en la cresta, le caen pegadas por los dos lados del cuello y luego cuelgan
                  sueltas y onduladas, como una melena mojada (la Acechadora, sobre su cuello corto);
       'viento'   las cintas se echan atras y abajo, sobre el lomo, como si la arrastrara la corriente (la Kelpia);
       'aleta'    una aleta alta de la nuca a la cruz, con las cintas cortas colgando del canto (el Hipocampo)."""
    n = len(cresta)
    frente = -np.asarray(dorso, float)
    atras = np.asarray(dorso, float)
    if estilo == 'aleta':
        bordes = []
        for j in range(n):
            q = np.asarray(cresta[j], float)
            t = j / max(n - 1, 1)
            h = 3.0 + 4.5 * math.sin(math.pi * (0.15 + 0.7 * t))
            bordes.append((q - atras * 0.8, q + atras * h + np.array((0.0, 0.6, 0.0))))
        for (a0, a1), (b0, b1) in zip(bordes, bordes[1:]):
            L_ = max(float(np.linalg.norm(b0 - a0)), 0.4)
            H_ = max(float(np.linalg.norm(a1 - a0)), 0.4)
            lamina(out, (a0, b0, b1, a1), P['aleta'], L_, H_, semilla=semilla)
            lamina(out, (b0, a0, a1, b1), P['aleta'], L_, H_, semilla=semilla)
        for k, (a0, a1) in enumerate(bordes):
            jm.tubo(out, [a0, a1], [0.4, 0.18], [P['casco']], semilla=semilla + 1)
            if k % 2 == 1:
                for s in (1, -1):
                    ctrl = [a1, a1 + np.array((s * 1.5, -1.0, 0.0)) + atras * 1.0, a1 + np.array((s * 2.6, -6.0, 0.0)) + atras * 1.5,
                            a1 + np.array((s * 3.0, -10.0, 0.0)) + atras * 1.0]
                    cinta(out, P, ctrl, 2.4, giro=0.25, vejigas=1, semilla=semilla + k % 3)
        return
    for j in range(n):
        q = np.asarray(cresta[j], float)
        r = radios[j]
        t = j / max(n - 1, 1)
        for s in (1, -1):
            L = largo * (1.0 - 0.3 * t) * (1.0 if (j + (s > 0)) % 2 else 0.82)
            x = np.array((s, 0.0, 0.0))
            if estilo == 'viento':
                w = 2.0 + 3.5 * (1.0 - t)
                ctrl = [q, q + x * (r * 0.6 + 1.0) + atras * 2.5 + np.array((0.0, 1.0, 0.0)),
                        q + x * (r * 0.6 + w * 0.7) + atras * L * 0.45 + np.array((0.0, -L * 0.2, 0.0)),
                        q + x * (r * 0.6 + w) + atras * L * 0.75 + np.array((0.0, -L * 0.45 + (j % 2) * 2.0, 0.0)),
                        q + x * (r * 0.6 + w * 1.1) + atras * L * 0.95 + np.array((0.0, -L * 0.75, 0.0))]
            else:
                p1 = q + x * (r * 0.8 + 0.5) + frente * r * 0.35 + np.array((0.0, -0.4, 0.0))
                p2 = q + x * (r * 0.85 + 0.9) + frente * r * 1.0 + np.array((0.0, -L * 0.3, 0.0))
                p3 = p2 + x * 1.3 + frente * 0.6 * (j % 2) + np.array((0.0, -L * 0.35, 0.0))
                p4 = p3 + x * 0.6 - frente * 0.9 + np.array((0.0, -L * 0.35, 0.0))
                ctrl = [q, p1, p2, p3, p4]
            cinta(out, P, ctrl, 3.2, giro=0.25, vejigas=1 + (j + (s > 0)) % 2, semilla=semilla + j % 3)


def cola(out, P, base, n=7, largo=22.0, ola=False, semilla=0):
    """La cola de algas: cintas que caen de la grupa abiertas en abanico y se arrastran por el suelo (o que ondean
    atras, con ola=True)."""
    base = np.asarray(base, float)
    for j in range(n):
        x = (j - (n - 1) / 2) * 1.0
        L = largo * (0.75 + 0.25 * ((j * 7) % 4) / 3)
        if ola:
            ctrl = [base, base + np.array((x, 1.5, -4.0)), base + np.array((x * 2.4, 0.5, -L * 0.55)),
                    base + np.array((x * 3.2, -1.0 + (j % 2) * 2.5, -L))]
        else:
            y0 = base[1]
            ctrl = [base, base + np.array((x, 0.5, -3.0)), base + np.array((x * 2.2, -y0 * 0.5, -6.0)),
                    base + np.array((x * 3.0, -y0 + 0.6, -8.0 - (j % 3) * 1.5)), base + np.array((x * 3.6, -y0 + 0.4, -L * 0.75))]
        cinta(out, P, ctrl, 2.8, giro=0.3, vejigas=1, semilla=semilla + j % 3)


def _cabeza_en(out, P, nuca, mira, abre, orejas='punta', semilla=0):
    """Pone la cabeza con la nuca (el punto (0, 4.8, -3.4) de la cabeza) en el punto dado, mirando hacia mira."""
    R = em.marco((0.0, 0.0, 0.0), _u(np.array(mira, float)), up=(0.0, 1.0, 0.0))
    o = np.asarray(nuca, float) - pt(R, np.array((0.0, 4.8, -3.4)) * CABEZA)
    Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
    bm.PPB = PPB / CABEZA
    boca = cabeza(out, Mh, P, abre=abre, orejas=orejas, semilla=semilla)
    bm.PPB = PPB
    return Mh, boca


def _flequillo(out, P, Mh, semilla=0):
    """El copete: dos cintas que salen entre las orejas y le caen por los lados de la cara, enmarcandola."""
    for s in (1, -1):
        q = pt(Mh, (s * 0.9, 5.3, -2.6))
        a = pt(Mh, (s * 2.6, 5.0, 0.5))
        b = pt(Mh, (s * 3.4, 2.0, 2.5))
        c = pt(Mh, (s * 3.8, -2.0, 1.5))
        cinta(out, P, [q, a, b, c], 2.4, giro=0.15, vejigas=1, semilla=semilla)


# ======================================================================
#  LA ACECHADORA: un monstruo nuestro, no un caballo
# ======================================================================
def cabeza_bestia(out, Mh, P, abre=34.0, semilla=0):
    """La cabeza de la Acechadora, con el hocico hacia +z y la boca en y=0: ancha, alta y corta, con dos cejas de hueso
    en pico, de mal genio, sobre los ojos, y unos nudos de hueso por el hocico; cuatro ojos encendidos, dos por lado (uno
    grande arriba y uno pequeno en el hocico); las narices arriba, unas placas de hueso en las mejillas y dos barbos de
    alga que le cuelgan de las comisuras. Abajo, la quijada honda con dos alas de hueso a
    los lados. Las fauces, abiertas desde muy atras: el paladar encendido en escalones, los dientes en hojas, dos pares
    de colmillos arriba y uno abajo, el suelo de la boca encendido y el nucleo al fondo. Devuelve la boca."""
    p, h = P['piel'], P['hueso']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -3.2, 0.0, -4.0, 6.4, 5.0, 5.0, p, caras=F, semilla=semilla)                   # el craneo
    bm.cubo(out, Mh, -2.8, 0.3, 1.0, 5.6, 4.0, 3.8, p, caras=F, semilla=semilla + 1)               # el hocico
    bm.cubo(out, Mh, -2.4, 0.6, 4.8, 4.8, 3.2, 1.8, p, caras=F, semilla=semilla + 2)               # la punta
    bm.cubo(out, Mh, -2.4, 4.8, -3.8, 4.8, 0.7, 3.4, p, semilla=semilla + 4)                       # la coronilla
    bm.cubo(out, Mh, -1.0, 5.3, -3.6, 2.0, 0.9, 2.4, h, semilla=semilla + 4)                       # y su bulto de hueso
    for k, z in enumerate((1.6, 3.0, 4.3)):                                                        # los nudos del hocico
        a = 0.55 - 0.1 * k
        bm.cubo(out, Mh, -a, 4.2 - 0.35 * k, z, 2 * a, 0.7 - 0.1 * k, 1.0, h, semilla=semilla + 4)
    bm.cubo(out, Mh, -1.9, 0.6, 6.6, 3.8, 2.4, 0.7, p, caras=F, semilla=semilla + 2)               # el morro, que se afina
    for s in (1, -1):
        Mc = Mh @ vr.T(s * 2.0, 4.5, -0.4) @ vr.Rz(s * 0.32)                                       # las cejas, en pico
        caja(out, Mc, -1.9, 1.9, -0.45, 0.65, -1.6, 1.2, h, semilla=semilla + 3)
        caja(out, Mc, s * 0.9 - 0.7, s * 0.9 + 0.7, 0.5, 1.2, -1.2, 0.4, h, semilla=semilla + 3)
        bm.cubo(out, Mh, 2.9 if s > 0 else -3.3, 2.6, -1.4, 0.4, 1.5, 1.7, P['ojo'], semilla=semilla + 5)   # el ojo grande
        bm.cubo(out, Mh, 2.55 if s > 0 else -2.9, 2.0, 2.6, 0.35, 0.9, 0.9, P['ojo'], semilla=semilla + 5)  # y el pequeno
        bm.cubo(out, Mh, s * 1.1 - 0.35, 3.6, 5.4, 0.7, 0.2, 0.9, P['casco'], semilla=semilla + 6)          # las narices, arriba
        bm.cubo(out, Mh, 2.9 if s > 0 else -3.5, 0.2, -3.6, 0.6, 2.2, 2.4, h, semilla=semilla + 7)        # la placa de la mejilla
    for s in (1, -1):                                                                              # los barbos de alga
        q = pt(Mh, (s * 2.5, 1.0, 5.4))
        x = _u(Mh[:3, 0]) * s
        cinta(out, P, [q, q + x * 1.6 + np.array((0.0, -1.6, 0.6)), q + x * 1.0 + np.array((0.0, -4.0, 0.2)),
                       q + x * 2.4 + np.array((0.0, -6.4, -0.4)), q + x * 1.4 + np.array((0.0, -8.6, 0.2)),
                       q + x * 2.2 + np.array((0.0, -10.4, -0.2))], 1.2, giro=0.5, vejigas=0, semilla=semilla + 16, n=12)
    hilera(out, Mh, [(-2.6, 0.2), (-2.6, 6.4), (2.6, 6.4), (2.6, 0.2)], 0.6, -1.2, P['dientes_arriba'], semilla=semilla + 8)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.7, 0.6, 5.9), 3.0, 0.9, (0, -1, 0.1), P, semilla=semilla + 9)
        colmillo(out, Mh, (s * 2.4, 0.6, 2.4), 2.2, 0.8, (0, -1, 0.0), P, semilla=semilla + 9)
    caja(out, Mh, -2.2, 2.2, -2.0, 0.2, -2.9, -2.6, P['nucleo'], semilla=semilla + 10)
    Mj = Mh @ vr.T(0.0, 0.0, -3.2) @ vr.Rx(abre * D)                                                # la quijada de abajo
    bm.cubo(out, Mj, -3.0, -4.2, -0.8, 6.0, 4.2, 5.0, p, caras={'arriba': P['boca']}, semilla=semilla + 11)
    bm.cubo(out, Mj, -2.7, -2.6, 4.2, 5.4, 2.6, 5.2, p, caras={'arriba': P['boca']}, semilla=semilla + 12)
    for s in (1, -1):                                                                              # las alas de hueso
        bm.cubo(out, Mj, 2.8 if s > 0 else -3.6, -3.6, 0.0, 0.8, 2.6, 4.6, h, semilla=semilla + 13)
        bm.cubo(out, Mj, 3.0 if s > 0 else -3.8, -4.8, 0.6, 0.8, 1.4, 2.4, h, semilla=semilla + 13)
    hilera(out, Mj, [(-2.4, 3.4), (-2.4, 9.2), (2.4, 9.2), (2.4, 3.4)], 0.0, 1.1, P['dientes_abajo'], semilla=semilla + 14)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.7, 0.0, 8.7), 2.4, 0.8, (0, 1, 0.08), P, semilla=semilla + 15)
    return pt(Mh, (0.0, -0.8, 3.0))


def garras(out, P, base, adelante, abajo=(0.0, -1.0, 0.0), curva=1.0, semilla=0):
    """La pezuna partida en tres garras de cuerno, abiertas hacia delante y con la punta en gancho hacia abajo."""
    base, adelante, abajo = (np.asarray(v, float) for v in (base, adelante, abajo))
    e = _u(np.cross((0.0, 1.0, 0.0), adelante)) if abs(adelante[1]) < 0.9 else np.array((1.0, 0.0, 0.0))
    for g in (-34, 0, 34):
        d = _u(adelante * math.cos(g * D) + e * math.sin(g * D))
        p0 = base + d * 0.6
        p1 = p0 + d * (2.0 if g == 0 else 1.6) + abajo * 0.3 * curva
        p2 = p1 + d * 0.9 + abajo * 1.3 * curva
        jm.tubo(out, [p0, p1, p2], [0.8, 0.6, 0.15], [P['casco'], P['casco']], semilla=semilla)


def extremidad(out, P, puntos, radios, adelante, abajo=(0.0, -1.0, 0.0), semilla=0):
    """Un brazo o una pata de la Acechadora: los tubos de bloques por los puntos (hombro o cadera, codo o rodilla,
    muneca o tobillo, mano), las juntas, la palma y las tres garras."""
    puntos = [np.asarray(p, float) for p in puntos]
    jm.tubo(out, puntos, radios, [P['piel']] * (len(puntos) - 1), semilla=semilla)
    for p, r in zip(puntos[1:-1], radios[1:-1]):
        caja(out, vr.T(*p), -r, r, -r, r, -r, r, P['piel'], semilla=semilla + 1)
    m = puntos[-1]
    caja(out, vr.T(*m), -1.7, 1.7, -1.0, 1.0, -1.4, 1.6, P['piel'], semilla=semilla + 2)
    garras(out, P, m + _u(adelante) * 0.8, _u(adelante), abajo, semilla=semilla + 3)


def _cabeza_bestia_en(out, P, nuca, mira, abre, semilla=0):
    """Pone la cabeza de la Acechadora con la coronilla (el punto (0, 4.6, -3.6) de la cabeza) en el punto dado."""
    R = em.marco((0.0, 0.0, 0.0), _u(np.array(mira, float)), up=(0.0, 1.0, 0.0))
    o = np.asarray(nuca, float) - pt(R, np.array((0.0, 4.6, -3.6)) * CABEZA)
    Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
    bm.PPB = PPB / CABEZA
    boca = cabeza_bestia(out, Mh, P, abre=abre, semilla=semilla)
    bm.PPB = PPB
    return Mh, boca


def acechadora(out, P):
    """La Acechadora: un monstruo del lago, cargado de hombros, con la joroba de hueso de la que le crecen las algas
    y le caen como una cortina por los dos lados; los brazos largos, uno alzado, y las patas cortas, con las pezunas
    partidas en tres garras de cuerno; el cuello corto y bajo y la cabeza colgando por delante, hacia ti, con las fauces
    abiertas. Del kelpie le quedan la crin de algas y las pezunas. Devuelve la boca."""
    grupa, pecho = np.array((0.0, 12.5, -13.0)), np.array((0.0, 18.5, 6.0))
    eje_t = _u(pecho - grupa)
    ps, rs, _ = jm.a_lo_largo([grupa - eje_t * 2.5, (grupa + pecho) / 2, pecho + eje_t * 1.5], 9,
                              ((0.0, 3.6), (0.15, 4.8), (0.45, 4.6), (0.75, 6.2), (1.0, 5.2)))
    jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=10, achata=1.2)
    # la joroba de los hombros, con su cresta de hueso
    jctrl = [np.array((0.0, 20.5, -7.0)), np.array((0.0, 24.5, -1.0)), np.array((0.0, 23.0, 5.0))]
    jps, jrs, _ = jm.a_lo_largo(jctrl, 6, ((0.0, 3.0), (0.5, 5.4), (1.0, 3.6)))
    jm.tubo(out, jps, jrs, [P['piel']] * (len(jps) - 1), semilla=12)
    for k in range(1, len(jps) - 1):
        q = np.asarray(jps[k], float) + np.array((0.0, jrs[k] * 0.9, 0.0))
        alto = 1.6 + 1.6 * math.sin(math.pi * k / (len(jps) - 1))
        M = vr.T(*q) @ vr.Rx(-0.35)
        caja(out, M, -0.9, 0.9, 0.0, alto, -1.0, 1.0, P['hueso'], semilla=13)
        caja(out, M, -0.5, 0.5, alto - 0.1, alto + 0.9, -0.6, 0.4, P['hueso'], semilla=13)
    # el cuello, corto, que baja
    cuello = [np.array((0.0, 19.5, 7.0)), np.array((0.0, 18.0, 11.0)), np.array((0.0, 15.0, 14.5))]
    cps, crs, _ = jm.a_lo_largo(cuello, 5, ((0.0, 4.4), (1.0, 3.4)))
    eje = _u(cuello[-1] - cuello[0])
    dorso = _u(np.cross(np.cross(eje, (0.0, 0.0, 1.0)), eje))
    dorso = -dorso if dorso[1] < 0 else dorso
    jm.tubo(out, cps, crs, [P['piel']] * (len(cps) - 1), semilla=11, arriba=dorso, achata=1.2)
    # la cabeza, colgando por delante
    Mh, boca = _cabeza_bestia_en(out, P, cuello[-1] + dorso * 1.6 + eje * 0.8, (0.0, -0.5, 1.0), 34.0, semilla=20)
    # los brazos: uno apoyado y otro alzado, con las garras hacia abajo
    for s in (1, -1):
        h = np.array((s * 5.0, 17.5, 5.0))
        if s > 0:
            ptos = [h, (s * 7.5, 11.0, 2.5), (s * 7.5, 3.4, 7.5), (s * 7.6, 1.4, 9.1)]
            extremidad(out, P, ptos, [3.0, 2.5, 2.2, 1.8], (0.15, 0.0, 1.0), semilla=30)
        else:
            ptos = [h, (s * 7.5, 12.5, 4.0), (s * 7.5, 10.5, 12.0), (s * 7.6, 8.0, 13.9)]
            extremidad(out, P, ptos, [3.0, 2.5, 2.2, 1.8], (0.0, -0.45, 1.0), semilla=30)
    # las patas de atras, cortas
    for s in (1, -1):
        atras = 0.0 if s > 0 else 1.5
        ptos = [np.array((s * 4.2, 11.5, -11.5)), (s * 6.0, 8.0, -6.5 - atras), (s * 6.0, 4.0, -12.5 - atras), (s * 6.0, 1.4, -10.6 - atras)]
        extremidad(out, P, ptos, [3.6, 2.4, 1.7, 1.4], (0.1 * s, 0.0, 1.0), semilla=50)
    # la cola: un munon del que salen las algas
    base = grupa - eje_t * 3.0 + np.array((0.0, 1.0, 0.0))
    jm.tubo(out, [base + eje_t * 1.5, base, base + np.array((0.0, -1.5, -3.0))], [3.0, 2.4, 1.4], [P['piel'], P['piel']], semilla=60)
    cola(out, P, base + np.array((0.0, -1.5, -3.0)), semilla=60)
    # la cortina de algas: de los dos lados de la joroba hasta casi el suelo
    for k, z in enumerate(np.linspace(-7.0, 2.0, 7)):
        y_top = 20.5 + 4.0 * math.sin(math.pi * (z + 7.0) / 12.0)
        for s in (1, -1):
            q = np.array((s * 3.6, y_top + 1.6, z))
            L = q[1] - 3.0 - (k % 2) * 2.0
            ctrl = [q, q + np.array((s * 2.6, -1.0, 0.2)), q + np.array((s * 4.6, -L * 0.35, 0.6 - (k % 2))),
                    q + np.array((s * 5.6, -L * 0.7, -0.3 + (k % 3) * 0.5)), q + np.array((s * 5.2, -L, 0.4))]
            cinta(out, P, ctrl, 3.2, giro=0.25, vejigas=1 + (k + (s > 0)) % 2, semilla=70 + k % 3)
    # y por delante, sobre el cuello, enmarcando la cabeza
    cresta = [p + dorso * r * 1.1 for p, r in zip(cps[:-1], crs[:-1])]
    crin(out, P, cresta, crs[:-1], dorso, estilo='cortina', largo=14.0, semilla=75)
    # el copete: cae por los lados de la cara, por detras de los ojos
    for s in (1, -1):
        q = pt(Mh, (s * 1.4, 5.2, -3.0))
        cinta(out, P, [q, pt(Mh, (s * 3.6, 4.8, -2.6)), pt(Mh, (s * 4.2, 1.0, -2.4)), pt(Mh, (s * 4.4, -3.5, -1.6))], 2.6, giro=0.15,
              vejigas=1, semilla=80)
    return boca


# ======================================================================
#  KELPIA
# ======================================================================
def kelpia(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        if tipo == 'C':
            boca = acechadora(out, P)
        else:
            boca = caballo(out, P, tipo)
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -y0, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def caballo(out, P, tipo):
    """La Kelpia y el Hipocampo: el caballo de agua, encabritado o con la cola de pez. Devuelve la boca."""
    if tipo == 'A':                                                       # encabritada
        grupa, pecho = np.array((0.0, 15.0, -12.0)), np.array((0.0, 31.0, 3.0))
        cuello = [np.array((0.0, 33.0, 2.5)), np.array((0.0, 40.5, 4.5)), np.array((0.0, 45.0, 9.5))]
        mira, abre = (0.0, -0.75, 1.0), 30.0
    elif tipo == 'B':                                                     # el Hipocampo, erguido sobre su cola
        grupa, pecho = np.array((0.0, 17.0, -5.0)), np.array((0.0, 30.0, 3.0))
        cuello = [np.array((0.0, 32.0, 2.5)), np.array((0.0, 38.5, 5.5)), np.array((0.0, 42.0, 10.0))]
        mira, abre = (0.0, -0.45, 1.0), 32.0
    # el tronco, mas hondo que ancho
    eje_t = _u(pecho - grupa)
    ps, rs, _ = jm.a_lo_largo([grupa - eje_t * 3.0, (grupa + pecho) / 2, pecho + eje_t * 1.5], 9,
                              ((0.0, 3.8), (0.12, 5.3), (0.35, 4.9), (0.68, 5.8), (0.9, 5.4), (1.0, 4.2)))
    jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=10, achata=1.15)
    # el cuello, alto y estrecho
    cps, crs, _ = jm.a_lo_largo(cuello, 8, ((0.0, 3.9), (1.0, 2.6)))
    eje = _u(cuello[-1] - cuello[0])
    dorso = _u(np.cross(np.cross(eje, (0.0, 0.0, 1.0)), eje))
    dorso = -dorso if dorso[2] > 0 else dorso
    jm.tubo(out, cps, crs, [P['piel']] * (len(cps) - 1), semilla=11, arriba=dorso, achata=1.35)
    cresta = [p + dorso * r * 1.2 for p, r in zip(cps[:-1], crs[:-1])]
    # la cabeza
    Mh, boca = _cabeza_en(out, P, cuello[-1] + dorso * 1.5 + eje * 1.0, mira, abre, orejas='aleta' if tipo == 'B' else 'punta',
                          semilla=20)
    # las patas de delante
    for s in (1, -1):
        h = pecho + np.array((s * 3.6, -2.5, 0.5))
        if tipo == 'A':
            if s > 0:                                                     # una, golpeando hacia delante
                ptos = [h, h + (s * 0.4, -4.5, 2.0), h + (s * 0.4, 0.5, 10.5), h + (s * 0.4, -4.0, 15.5),
                        h + (s * 0.4, -6.2, 17.0)]
            else:                                                         # y la otra plegada en alto
                ptos = [h, h + (s * 0.4, -4.5, 2.0), h + (s * 0.4, 3.0, 9.5), h + (s * 0.4, -4.5, 10.5),
                        h + (s * 0.4, -7.0, 9.0)]
        else:
            ptos = [h, h + (s * 0.6, -3.5, 2.0), h + (s * 1.2, -2.0 - s, 7.0), h + (s * 1.6, -3.0 - s, 9.5)]
        pata(out, P, ptos, [3.0, 2.2, 1.5, 1.2, 1.2], final='aleta' if tipo == 'B' else 'casco', semilla=30)
    # lo de atras
    if tipo == 'B':                                                       # la cola de pez, enroscada en el suelo
        ctrl = [grupa + (0.0, 2.0, 1.0), grupa, grupa + (0.0, -6.0, -2.0), (0.0, 5.0, -8.5), (0.0, 1.6, -3.0),
                (0.0, 3.0, 2.5), (0.0, 6.5, 2.0), (0.0, 7.0, -1.5), (0.0, 5.0, -3.0)]
        tps, trs, _ = jm.a_lo_largo(ctrl, 22, ((0.0, 5.2), (0.15, 4.8), (0.45, 3.4), (0.8, 1.8), (1.0, 1.0)))
        jm.tubo(out, tps, trs, [P['escama']] * (len(tps) - 1), semilla=40, arriba=(1.0, 0.0, 0.0))
        fin = int(len(tps) * 0.55)                                        # la aleta del lomo, por fuera de la cola
        bordes = []
        for k in range(1, fin + 1):
            t_ = _u(np.asarray(tps[min(k + 1, len(tps) - 1)], float) - np.asarray(tps[k - 1], float))
            n_ = _u(np.cross((1.0, 0.0, 0.0), t_))
            h_ = 4.5 * math.sin(math.pi * k / (fin + 1)) + 0.8
            q = np.asarray(tps[k], float)
            bordes.append((q + n_ * trs[k] * 0.7, q + n_ * (trs[k] + h_)))
        for (a0, a1), (b0, b1) in zip(bordes, bordes[1:]):
            L = max(float(np.linalg.norm(b0 - a0)), 0.4)
            H = max(float(np.linalg.norm(a1 - a0)), 0.4)
            lamina(out, (a0, b0, b1, a1), P['aleta'], L, H, semilla=41)
            lamina(out, (b0, a0, a1, b1), P['aleta'], L, H, semilla=41)
        for a0, a1 in bordes[::2]:
            jm.tubo(out, [a0, a1], [0.35, 0.15], [P['casco']], semilla=42)
    else:
        for s in (1, -1):
            c = grupa + np.array((s * 3.4, -1.0, 1.5))
            adel = 0.0 if s > 0 else -2.5                                 # bajo el cuerpo, sosteniendolo
            ptos = [c, (s * 4.0, 9.5, -5.0 + adel), (s * 4.0, 7.0, -12.0 + adel), (s * 4.0, 1.8, -10.0 + adel),
                    (s * 4.0, 0.0, -7.6 + adel)]
            pata(out, P, ptos, [3.8, 2.4, 1.5, 1.2, 1.2], semilla=50)
        cola(out, P, grupa - eje_t * 4.0 + np.array((0.0, 2.5, -2.5)), semilla=60)
    crin(out, P, cresta, crs[:-1], dorso, estilo='viento' if tipo == 'A' else 'aleta', semilla=70)
    _flequillo(out, P, Mh, semilla=80)
    return boca


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

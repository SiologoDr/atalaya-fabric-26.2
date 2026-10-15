"""
Aklutara y sus tipos (15-10-2026). Juan, al guardar a Ayunara: «guardalo me gusto, y crea otro boss». Antes se probo
a Mirmara (un hormiga-leon que asoma de su embudo de arena) y se aparco sin ensenarla: con las patas de insecto se leia
como una arana (Hilandra ya se descarto por eso) y no imponia.

Aklutara, la Loba del Mar Helado: sale del akhlut de los inuit, el espiritu que es orca en el mar y lobo en tierra, y
que deja huellas de lobo que se meten en el agua. Del akhlut le quedan rastros: la piel de orca, negra y lisa, con las
manchas blancas limpias (el vientre, los flancos, la mancha sobre el ojo); la aleta del lomo; la cola de orca; y las
patas y las orejas de lobo. Lo nuestro: sale del mar al hielo, con medio cuerpo fuera del agua, las patas de delante
apoyadas en el borde del tempano y la cola alzada detras; y la aleta del lomo se alza detras de la cabeza como una
hoja y la enmarca. La cabeza manda: ancha, con la frente redonda de la orca y el hocico de lobo, y las fauces abiertas
que arden (el paladar en escalones, los dientes en hojas, los colmillos y el nucleo al fondo).

Los tres tipos tienen la misma pose (saliendo del agua al tempano, rugiendo) y cambian la aleta:

    A  la Alta           una aleta recta y alta, como la del macho viejo; aguamarina
    B  la Mellada        una aleta curva hacia atras, mordida por el borde; coral
    C  la de Tres Aletas tres aletas seguidas por el lomo, de mayor a menor; amarillo
"""
import math
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
import kelpia_modelo as km
from kelpia_modelo import hilera, colmillo, _u

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4
ESCALA = 0.62
CABEZA = 1.5
NEGRO = _r('050608', '0a0c10', '101318', '181c24', '222832')
BLANCO = _r('6a7480', '9aa4b0', 'c4ccd6', 'e2e8ee', 'f6f9fc')
HIELO = _r('4a6070', '6c8496', '94acbc', 'bcd2de', 'e2f0f6')

VARIANTES = {
    'A': dict(clave='KA', nombre='la Alta', corto='alta', aleta='alta',
              casco=_r('141210', '201c18', '2e2822', '3e362e', '524840'),
              neon=('e6fff8', '2affd0', '045a46')),
    'B': dict(clave='KB', nombre='la Mellada', corto='mellada', aleta='mellada',
              casco=_r('141210', '201c18', '2e2822', '3e362e', '524840'),
              neon=('fff0ea', 'ff6a4a', '6a1a0a')),
    'C': dict(clave='KC', nombre='la de Tres Aletas', corto='tres', aleta='tres',
              casco=_r('141210', '201c18', '2e2822', '3e362e', '524840'),
              neon=('fffbe0', 'ffd21a', '6a5004')),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    """Los de Kelpia para lo comun (el ojo, el paladar, los dientes, el nucleo, las unas) y los propios: la piel de
    orca, negra por arriba y blanca por abajo, con el borde limpio; el blanco de las manchas; la aleta; y el hielo."""
    W = dict(V, piel=NEGRO, alga=NEGRO, mancha=NEGRO, hueso=BLANCO)
    P = km.pintores(W)
    k = V['clave']

    def reg(nombre, fn):
        fn.__name__ = 'akl%s_%s' % (k, nombre)
        P[nombre] = fn
        return fn

    def piel(tw, th, cara, s):
        """La piel de orca: negra y lisa, con un brillo arriba; el vientre blanco; y en los lados, la parte de abajo
        blanca con el borde limpio."""
        ys, xs = np.mgrid[0:th, 0:tw]
        if cara == 'abajo':
            return _imagen(_bisel(np.full((th, tw), 3), 1, 1), BLANCO), None
        t = _imagen(_bisel(np.full((th, tw), 2), 1, 1), NEGRO)
        if cara in ('der', 'izq', 'frente', 'atras'):
            blanco = ys > th * 0.62
            t[blanco] = _imagen(np.full((th, tw), 3), BLANCO)[blanco]
        return t, None
    reg('piel', piel)
    reg('negro', jm.liso(NEGRO, 2, 1, 1))
    reg('blanco', jm.liso(BLANCO, 3, 1, 1))
    reg('hielo', jm.liso(HIELO, 3, 2, 1))

    def aleta(tw, th, cara, s):
        """La aleta: negra, con un canto un poco mas claro y unas vetas que bajan."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(xs % 7 == 0, 3, 2)
        idx = np.where(ys < 1, 4, idx)
        return _imagen(idx, NEGRO), None
    reg('aleta', aleta)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def placa(out, P, puntos, pintor, semilla=0):
    """Una placa plana (la aleta): un abanico de laminas del primer punto a los demas, por las dos caras, con el canto."""
    puntos = [np.asarray(p, float) for p in puntos]
    c = puntos[0]
    for a, b in zip(puntos[1:], puntos[2:]):
        L = max(float(np.linalg.norm(b - a)), 0.4)
        H = max(float(np.linalg.norm((a + b) / 2 - c)), 0.4)
        lamina(out, (c, c, b, a), pintor, L, H, semilla=semilla)
        lamina(out, (c, c, a, b), pintor, L, H, semilla=semilla)


def aleta_lomo(out, P, base0, base1, alto, atras, curva=0.0, mordiscos=(), escala=1.0, semilla=0):
    """Una aleta del lomo, de base0 (delante) a base1 (detras): el canto de delante sube hasta la punta (alto, echada
    atras), y el de detras baja curvo; mordiscos son los tramos del borde que se meten (la Mellada)."""
    base0, base1 = np.asarray(base0, float), np.asarray(base1, float)
    up = np.array((0.0, 1.0, 0.0))
    back = _u(base1 - base0)
    punta = base0 + up * alto * escala + back * atras * escala
    borde = []
    n = 6
    for i in range(n + 1):                                              # el canto de delante, un poco curvo
        t = i / n
        p = base0 + (punta - base0) * t + back * math.sin(math.pi * t) * -0.8 * escala
        borde.append(p)
    for i in range(1, n + 1):                                           # el de detras, curvo hacia dentro
        t = i / n
        p = punta + (base1 - punta) * t + back * math.sin(math.pi * t) * (-1.2 - curva) * escala
        for (m0, m1) in mordiscos:
            if m0 <= t <= m1:
                p = p - back * 1.4 * escala + up * -0.4 * escala
        borde.append(p)
    centro = (base0 + base1) / 2 + up * 0.5
    placa(out, P, [centro] + borde, P['aleta'], semilla=semilla)
    jm.tubo(out, borde[:n + 1], [0.45 * escala] * (n + 1), [P['negro']] * n, semilla=semilla + 1)
    jm.tubo(out, [base0, base1], [0.9 * escala, 0.9 * escala], [P['negro']], semilla=semilla + 2)


def cabeza(out, Mh, P, abre=40.0, semilla=0):
    """La cabeza de Aklutara, con el hocico hacia +z y la boca en y=0: la frente redonda y alta de la orca, el hocico
    de lobo, la mancha blanca sobre cada ojo, la barbilla blanca y dos orejas de lobo echadas atras. Las fauces,
    abiertas desde muy atras: el paladar encendido en escalones, los dientes en hojas, dos colmillos arriba y dos
    abajo, el suelo de la boca encendido y el nucleo al fondo. Devuelve la boca."""
    p = P['negro']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -3.4, 0.0, -4.0, 6.8, 4.6, 5.4, p, caras=F, semilla=semilla)                   # el craneo
    bm.cubo(out, Mh, -2.8, 4.6, -3.6, 5.6, 1.2, 4.6, p, semilla=semilla + 1)                       # la frente de orca
    bm.cubo(out, Mh, -2.2, 5.8, -3.0, 4.4, 0.6, 3.4, p, semilla=semilla + 1)
    bm.cubo(out, Mh, -2.6, 0.3, 1.4, 5.2, 3.6, 3.8, p, caras=F, semilla=semilla + 2)               # el hocico de lobo
    bm.cubo(out, Mh, -1.9, 0.6, 5.2, 3.8, 2.6, 1.6, p, caras=F, semilla=semilla + 3)
    bm.cubo(out, Mh, -1.0, 2.4, 6.6, 2.0, 0.9, 0.3, P['casco'], semilla=semilla + 4)               # la nariz
    for s in (1, -1):
        x0 = 3.0 if s > 0 else -3.5
        bm.cubo(out, Mh, x0, 2.6, -0.6, 0.5, 1.0, 1.2, P['ojo'], semilla=semilla + 5)              # los ojos
        bm.cubo(out, Mh, 3.05 if s > 0 else -3.45, 3.4, -3.0, 0.4, 1.4, 2.8, P['blanco'], semilla=semilla + 6)  # la mancha blanca
        Mo = Mh @ vr.T(s * 2.2, 5.4, -3.0) @ vr.Rz(-s * 0.25) @ vr.Rx(-0.7)                        # las orejas de lobo
        caja(out, Mo, -0.9, 0.9, 0.0, 1.6, -0.5, 0.5, p, semilla=semilla + 7)
        caja(out, Mo, -0.5, 0.5, 1.5, 3.0, -0.35, 0.35, p, semilla=semilla + 7)
    hilera(out, Mh, [(-2.4, 0.2), (-2.4, 6.6), (2.4, 6.6), (2.4, 0.2)], 0.6, -1.1, P['dientes_arriba'], semilla=semilla + 8)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.6, 0.6, 6.0), 3.0, 0.9, (0, -1, 0.05), P, semilla=semilla + 9)
    caja(out, Mh, -2.6, 2.6, -2.0, 0.2, -3.3, -3.0, P['nucleo'], semilla=semilla + 10)
    Mj = Mh @ vr.T(0.0, 0.0, -3.4) @ vr.Rx(abre * D)                                                # la quijada de abajo, blanca por debajo
    bm.cubo(out, Mj, -3.2, -3.0, -0.6, 6.4, 3.0, 4.8, p, caras={'arriba': P['boca'], 'abajo': P['blanco']}, semilla=semilla + 11)
    bm.cubo(out, Mj, -2.4, -2.0, 4.2, 4.8, 2.0, 5.0, p, caras={'arriba': P['boca'], 'abajo': P['blanco']}, semilla=semilla + 12)
    hilera(out, Mj, [(-2.1, 3.2), (-2.1, 9.0), (2.1, 9.0), (2.1, 3.2)], 0.0, 1.0, P['dientes_abajo'], semilla=semilla + 13)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.6, 0.0, 8.5), 2.5, 0.8, (0, 1, 0.05), P, semilla=semilla + 14)
    return pt(Mh, (0.0, -0.8, 2.8))


def zarpa(out, P, base, adelante, semilla=0):
    """Una zarpa de lobo palmeada, apoyada en el hielo: la palma, cuatro dedos con su una y la membrana entre ellos."""
    base, f = np.asarray(base, float), _u(adelante)
    e = _u(np.cross((0.0, 1.0, 0.0), f))
    caja(out, vr.T(*base) @ em.marco((0, 0, 0), f, up=(0.0, 1.0, 0.0)), -2.0, 2.0, -0.6, 0.9, -1.6, 2.0, P['negro'], semilla=semilla)
    puntas = []
    for k, x in enumerate((-1.5, -0.5, 0.5, 1.5)):
        b = base + e * x + f * 1.8
        t = b + _u(f + e * x * 0.25) * 2.2 + np.array((0.0, -0.3, 0.0))
        jm.tubo(out, [b, t], [0.6, 0.45], [P['negro']], semilla=semilla + 1)
        jm.tubo(out, [t, t + _u(f) * 0.9 + np.array((0.0, -0.6, 0.0))], [0.35, 0.08], [P['casco']], semilla=semilla + 2)
        puntas.append(t)
    for a, b in zip(puntas, puntas[1:]):                                # la membrana entre los dedos
        c = base + f * 1.6
        placa(out, P, [c, a, b], P['aleta'], semilla=semilla + 3)


# ======================================================================
#  AKLUTARA
# ======================================================================
def aklutara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        # el tempano, a sus pies
        for k, (x0, x1, z0, z1, h) in enumerate(((-15.0, 15.0, 4.0, 22.0, 2.4), (-18.0, -9.0, 8.0, 18.0, 2.0), (9.0, 17.0, 6.0, 20.0, 2.2),
                                                  (-10.0, 10.0, 19.0, 25.0, 1.8))):
            caja(out, np.eye(4), x0, x1, -1.6, h, z0, z1, P['hielo'], semilla=k)
        # el cuerpo, que sale del agua arqueado
        cuerpo = [np.array((0.0, -3.0, -20.0)), np.array((0.0, 1.5, -14.0)), np.array((0.0, 7.0, -6.0)), np.array((0.0, 11.0, 1.0)),
                  np.array((0.0, 13.5, 5.0))]
        ps, rs, _ = jm.a_lo_largo(cuerpo, 8, ((0.0, 4.4), (0.3, 6.6), (0.6, 7.4), (0.9, 6.6), (1.0, 5.4)))
        jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=10, achata=1.05)
        # la cola de orca, alzada detras
        cola = [np.array((0.0, -3.0, -20.0)), np.array((0.0, -1.0, -26.0)), np.array((0.0, 4.0, -31.0))]
        cps, crs, _ = jm.a_lo_largo(cola, 4, ((0.0, 4.4), (1.0, 2.0)))
        jm.tubo(out, cps, crs, [P['piel']] * (len(cps) - 1), semilla=11)
        b = np.asarray(cps[-1], float)
        for s in (1, -1):
            placa(out, P, [b, b + np.array((s * 1.5, 0.6, -1.5)), b + np.array((s * 6.5, 2.4, -3.0)), b + np.array((s * 8.0, 2.6, -6.0)),
                           b + np.array((s * 5.0, 1.6, -5.4)), b + np.array((s * 1.0, 0.6, -4.0))], P['aleta'], semilla=12)
        # la mancha gris detras de la aleta (la montura)
        for k in (3, 4):
            q = np.asarray(ps[k], float)
            caja(out, vr.T(*q), -rs[k] * 0.5, rs[k] * 0.5, rs[k] * 0.62, rs[k] * 0.78, -1.2, 1.2, P['blanco'], semilla=13)
        # las aletas del lomo
        def lomo(t):                                                    # un punto del lomo, a lo largo del cuerpo
            f = t * (len(ps) - 1)
            i = min(int(f), len(ps) - 2)
            w = f - i
            q = np.asarray(ps[i], float) * (1 - w) + np.asarray(ps[i + 1], float) * w
            r = rs[i] * (1 - w) + rs[i + 1] * w
            return q + np.array((0.0, r * 0.9, 0.0))
        if V['aleta'] == 'alta':
            aleta_lomo(out, P, lomo(0.74), lomo(0.40), 17.0, 3.0, semilla=20)
        elif V['aleta'] == 'mellada':
            aleta_lomo(out, P, lomo(0.74), lomo(0.40), 12.5, 8.0, curva=1.2, mordiscos=((0.25, 0.38), (0.55, 0.68)), semilla=20)
        else:
            for k, (t0, t1, a) in enumerate(((0.80, 0.62, 11.0), (0.60, 0.44, 9.0), (0.42, 0.28, 7.0))):
                aleta_lomo(out, P, lomo(t0), lomo(t1), a, 3.5, semilla=20 + k)
        # el cuello y la cabeza
        cuello = [np.array((0.0, 13.0, 5.0)), np.array((0.0, 16.0, 8.5))]
        jm.tubo(out, cuello, [5.0, 4.2], [P['piel']], semilla=14)
        R = em.marco((0.0, 0.0, 0.0), _u(np.array((0.0, -0.3, 1.0))), up=(0.0, 1.0, 0.0))
        nuca = np.array((0.0, 20.5, 8.0))
        o = nuca - pt(R, np.array((0.0, 5.0, -3.4)) * CABEZA)
        Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
        bm.PPB = PPB / CABEZA
        boca = cabeza(out, Mh, P, abre=40.0, semilla=30)
        bm.PPB = PPB
        # las patas de lobo, apoyadas en el tempano
        for s in (1, -1):
            hombro, codo, muneca = np.array((s * 5.4, 11.0, 3.0)), np.array((s * 8.0, 6.5, 6.0)), np.array((s * 8.4, 3.6, 11.0))
            jm.tubo(out, [hombro, codo, muneca], [3.2, 2.2, 1.7], [P['piel'], P['piel']], semilla=40)
            caja(out, vr.T(*codo), -2.2, 2.2, -2.2, 2.2, -2.2, 2.2, P['piel'], semilla=41)
            for k in range(3):                                          # el pelo de lobo del codo
                q = codo + np.array((s * 1.8, -0.5 - k * 0.6, -1.0))
                jm.tubo(out, [q, q + np.array((s * 1.2, -1.8, -1.6))], [0.5, 0.1], [P['negro']], semilla=42)
            zarpa(out, P, np.array((s * 8.6, 3.1, 12.0)), (s * 0.12, 0.0, 1.0), semilla=43)
    finally:
        bm.PPB = ppb
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, 0.6, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

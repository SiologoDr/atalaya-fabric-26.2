"""
Zotzara y sus formas (14-10-2026). Juan, tras Volutara: «no me gusto pero se ve bien… sigamos con otro boss». La
leccion de Volutara: que imponga el monstruo, no lo que lleva encima.

Zotzara, la Murcielaga de Xibalba: sale de Camazotz, el murcielago de la muerte de los mayas, el que cortaba cabezas en
la casa de los murcielagos del inframundo. Del murcielago le quedan rastros: las alas de membrana, las orejas enormes,
la hoja de la nariz y la costumbre de colgarse boca abajo. Todo lo demas es nuestro: una figura alta, encorvada y
flaca, sobre dos patas de garras; la hoja de la nariz es un cuchillo de pedernal, como el de los sacrificios, que se
alza entre las dos orejas y con ellas le enmarca la cabeza; el cuello lleva un collar de pelo tieso; y la cabeza manda,
con las fauces abiertas que arden (el paladar en escalones, los dientes en hojas, los colmillos largos y el nucleo al
fondo). Las alas son oscuras, en bandas, con el borde libre encendido.

Juan la aprobo el 14-10-2026 con una condicion: «que todos tengan la misma pose; recuerda que esto de los tipos es de
un solo boss, una misma pose pero diferentes». Las tres van agachadas, con las alas abiertas del todo, chillando (la
pose de la Abierta, la que mas imponia), y cambian lo que le enmarca la cabeza y el borde de las alas:

    A  la Pedernal    dos orejas altas en punta, el cuchillo de pedernal en la nariz y las alas en festones lisos; jade
    B  la Desgarrada  las orejas con una muesca mordida, dos cuchillos abiertos en V y las alas rotas, con desgarros
                      y el borde mellado; sangre
    C  la Coronada    cuatro orejas (dos altas y dos que se abren a los lados, como una corona), la nariz en herradura
                      con una punta en medio y un garfio de cuerno en la punta de cada dedo; oro

Las otras dos poses de la primera ficha (la Encapuchada, con las alas cerradas como una capa, y la Colgada, boca abajo
de un arbol muerto) siguen como opciones: pose='capa' y pose='colgada'.
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
CABEZA = 1.45

VARIANTES = {
    'A': dict(
        clave='ZA', nombre='la Pedernal', corto='pedernal', pose='abierta', orejas='altas', nariz='cuchillo', alas='festones',
        piel=_r('08090a', '101214', '181b1e', '22262a', '2e3338'),
        membrana=_r('060708', '0c0e10', '141719', '1e2226', '2a3036'),
        pelo=_r('0a0c0c', '141818', '1e2424', '2a3232', '384242'),
        pedernal=_r('3a3530', '5a534a', '7e766a', 'a49a8a', 'c8bfae'),
        casco=_r('16140e', '262218', '383224', '4e4634', '665c46'),
        neon=('eafff2', '2aff9a', '045a32'),
    ),
    'B': dict(
        clave='ZB', nombre='la Desgarrada', corto='desgarrada', pose='abierta', orejas='muesca', nariz='doble', alas='rotas',
        piel=_r('0e0808', '181010', '241818', '322222', '422e2e'),
        membrana=_r('0a0606', '140c0c', '1e1414', '2a1c1c', '382626'),
        pelo=_r('100a0a', '1c1212', '2a1c1c', '3a2828', '4c3434'),
        pedernal=_r('34302c', '524a42', '766c60', '9a9080', 'beb4a2'),
        casco=_r('16120e', '261e18', '382c22', '4e3e30', '665240'),
        neon=('ffe4e4', 'ff2a3a', '6a0410'),
    ),
    'C': dict(
        clave='ZC', nombre='la Coronada', corto='coronada', pose='abierta', orejas='corona', nariz='herradura', alas='garfios',
        piel=_r('0a0a0e', '121218', '1a1a22', '24242e', '30303c'),
        membrana=_r('08080a', '0e0e12', '16161c', '202028', '2c2c36'),
        pelo=_r('0c0c10', '16161c', '202028', '2c2c36', '3a3a46'),
        pedernal=_r('3a3630', '5a544a', '7e776a', 'a49b8a', 'c8c0ae'),
        casco=_r('18160e', '282418', '3a3424', '504834', '6a5e46'),
        neon=('fff8e0', 'ffc21a', '6a4a04'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
def pintores(V):
    """Los de Kelpia para lo comun (la piel, el ojo, el paladar, los dientes, el nucleo, la garra) y los propios: la
    membrana de las alas (en bandas, con el borde libre encendido), la de las orejas, el pelo del collar y el pedernal."""
    W = dict(V, alga=V['membrana'], hueso=V['pedernal'], mancha=V['piel'])
    P = km.pintores(W)
    k = V['clave']
    nuc, neo, hon = V['neon']

    def reg(nombre, fn):
        fn.__name__ = 'zot%s_%s' % (k, nombre)
        P[nombre] = fn
        return fn

    def membrana(tw, th, cara, s, borde=True):
        """La membrana: oscura, en bandas que bajan hacia la muneca, con un nervio un poco mas claro cada pocos pixeles; y
        arriba (el borde libre) una tira encendida."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 3) % 2 == 0, 2, 1)
        idx = np.where(xs % 9 == 4, 3, idx)
        t = _imagen(idx, V['membrana'])
        if not borde:
            return t, None
        filo = ys < max(1, th // 16)
        c_m, c_h = nm._hex(neo), nm._hex(hon)
        t[filo, :3] = c_m
        t[(ys == max(1, th // 16)), :3] = c_h
        return t, _emis(t, filo, 225)
    reg('membrana', membrana)
    reg('membrana_lisa', lambda tw, th, c, s: membrana(tw, th, c, s, borde=False))

    def oreja(tw, th, cara, s):
        """La oreja por dentro: la piel con los pliegues de traves, mas claros."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(ys % 5 == 0, 3, np.where(ys % 5 == 1, 1, 2))
        return _imagen(idx, V['piel']), None
    reg('oreja', oreja)

    def pelo(tw, th, cara, s):
        """El pelo tieso del collar: mechones de arriba abajo, con la punta oscura."""
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((xs // 2) % 3 == 0, 3, 2)
        idx = np.where(ys > th * 0.75, 1, idx)
        return _imagen(idx, V['pelo']), None
    reg('pelo', pelo)

    def pedernal(tw, th, cara, s):
        """El cuchillo de pedernal: las lascas en arcos, como se tallaba, con el filo claro."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        d = np.hypot(xs - tw / 2, (ys - th) * 0.6)
        idx = np.where((d // 3).astype(int) % 2 == 0, 3, 2)
        idx = np.where((xs < 1) | (xs > tw - 2), 4, idx)
        return _imagen(idx, V['pedernal']), None
    reg('pedernal', pedernal)
    return P


# ----------------------------------------------------------------------
#  Piezas
# ----------------------------------------------------------------------
def membrana(out, P, apice, a, b, pintor, semilla=0):
    """Un triangulo de membrana del apice (muneca o axila) al borde a-b, con las dos caras."""
    apice, a, b = (np.asarray(v, float) for v in (apice, a, b))
    L = max(float(np.linalg.norm(b - a)), 0.5)
    m = (a + b) / 2
    H = max(float(np.linalg.norm(m - apice)), 0.5)
    lamina(out, (apice, apice, b, a), pintor, L, H, semilla=semilla)
    lamina(out, (apice, apice, a, b), pintor, L, H, semilla=semilla)


def borde(out, P, apice, a, b, estilo, k=0, semilla=0):
    """La membrana del apice al borde libre a-b: en festones (el borde se mete un poco en medio) o rota (el borde
    mellado a dientes de sierra y, en algunas, un desgarro del apice al borde)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    L = float(np.linalg.norm(b - a))
    if estilo != 'rotas':
        m = (a + b) / 2 + _u(np.asarray(apice, float) - (a + b) / 2) * L * 0.18
        membrana(out, P, apice, a, m, P['membrana'], semilla=semilla)
        membrana(out, P, apice, m, b, P['membrana'], semilla=semilla)
        return
    entra = (0.0, 0.34, 0.06, 0.44, 0.12, 0.0) if k % 2 == 0 else (0.0, 0.1, 0.4, 0.04, 0.3, 0.0)
    n = len(entra) - 1
    pts = [a + (b - a) * (i / n) + _u(np.asarray(apice, float) - (a + (b - a) * (i / n))) * L * f for i, f in enumerate(entra)]
    hueco = (k * 2 + 1) % n
    for i in range(n):
        if i == hueco and k != 3:                                       # el desgarro
            continue
        membrana(out, P, apice, pts[i], pts[i + 1], P['membrana'], semilla=semilla)


def ala(out, P, hombro, codo, muneca, dedos, pie, estilo='festones', semilla=0):
    """Un ala: el brazo (hombro, codo, muneca) con el pulgar en garra, los cuatro dedos largos (cada uno con su
    nudillo y su punta) y la membrana entre ellos, con el borde libre encendido; y la membrana del ultimo dedo hasta el
    pie. El estilo cambia el borde: 'festones', 'rotas' (desgarrada) o 'garfios' (festones y un garfio de cuerno en la
    punta de cada dedo)."""
    hombro, codo, muneca = (np.asarray(v, float) for v in (hombro, codo, muneca))
    jm.tubo(out, [hombro, codo, muneca], [2.4, 1.6, 1.2], [P['piel'], P['piel']], semilla=semilla)
    caja(out, vr.T(*codo), -1.7, 1.7, -1.7, 1.7, -1.7, 1.7, P['piel'], semilla=semilla + 1)
    caja(out, vr.T(*muneca), -1.4, 1.4, -1.4, 1.4, -1.4, 1.4, P['piel'], semilla=semilla + 1)
    d_pulgar = _u(muneca - codo)
    pul = [muneca, muneca + d_pulgar * 2.2, muneca + d_pulgar * 3.2 + np.array((0.0, -1.2, 0.0))]
    jm.tubo(out, pul, [0.7, 0.5, 0.12], [P['casco'], P['casco']], semilla=semilla + 2)       # el pulgar, en garra
    puntas = []
    for k, (nudillo, punta) in enumerate(dedos):
        nudillo, punta = np.asarray(nudillo, float), np.asarray(punta, float)
        jm.tubo(out, [muneca, nudillo, punta], [0.55, 0.32, 0.12], [P['piel'], P['piel']], semilla=semilla + 3)
        puntas.append(punta)
        if estilo == 'garfios':                                         # el garfio de cuerno de la punta
            d = _u(punta - nudillo)
            jm.tubo(out, [punta, punta + d * 2.0, punta + d * 2.8 + np.array((0.0, -1.6, 0.0))], [0.6, 0.4, 0.1],
                    [P['casco'], P['casco']], semilla=semilla + 8)
    for k, (a, b) in enumerate(zip(puntas, puntas[1:])):                # la membrana entre los dedos
        borde(out, P, muneca, a, b, estilo, k, semilla=semilla + 4)
    membrana(out, P, hombro, muneca, puntas[0], P['membrana_lisa'], semilla=semilla + 5)    # la de delante, del hombro
    axila = hombro + (np.asarray(pie, float) - hombro) * 0.25
    borde(out, P, axila, puntas[-1], np.asarray(pie, float), estilo, 3, semilla=semilla + 6)
    membrana(out, P, axila, muneca, puntas[-1], P['membrana_lisa'], semilla=semilla + 7)


def oreja(out, P, Mh, s, atras=0.0, forma='altas', semilla=0):
    """Una oreja enorme, en punta, que sube y se abre hacia fuera (o se echa atras, en la Colgada): el borde de piel y
    la membrana de dentro. Con forma='muesca', el borde de atras lleva un mordisco; con forma='corona', sale ademas
    otra oreja mas pequena que se abre hacia el lado."""
    if forma == 'corona':
        piv = np.array((s * 2.4, 3.8, -1.9))
        M2 = Mh @ vr.T(*piv) @ vr.Rz(-s * 62 * D) @ vr.Ry(s * 10 * D) @ np.diag([0.72, 0.72, 0.72, 1.0]) @ vr.T(*(-piv))
        oreja(out, P, M2, s, atras=atras, forma='altas', semilla=semilla + 2)
    Mo = Mh @ vr.T(0.0, 4.0, -1.8) @ vr.Rx(-atras * D) @ vr.T(0.0, -4.0, 1.8)
    base_a, base_b = pt(Mo, (s * 1.4, 4.2, -0.6)), pt(Mo, (s * 3.2, 3.4, -3.2))
    punta = pt(Mo, (s * 6.4, 13.0, -3.6))
    medio_f = pt(Mo, (s * 4.4, 9.0, -0.6))
    medio_t = pt(Mo, (s * 5.2, 8.0, -4.8))
    if forma == 'muesca':                                               # el mordisco del borde de atras
        mordisco = medio_t + (punta - medio_t) * 0.5
        mordisco = mordisco + (medio_f - mordisco) * 0.5
        atras_ = [base_b, medio_t, mordisco, punta]
        caras = ((base_a, base_b, medio_t), (base_a, medio_t, medio_f), (medio_f, medio_t, mordisco), (medio_f, mordisco, punta))
    else:
        atras_ = [base_b, medio_t, punta]
        caras = ((base_a, base_b, medio_t), (base_a, medio_t, medio_f), (medio_f, medio_t, punta))
    for tramo in ([base_a, medio_f, punta], atras_):
        jm.tubo(out, tramo, [0.8] + [0.6] * (len(tramo) - 2) + [0.15], [P['piel']] * (len(tramo) - 1), semilla=semilla)
    for a, b, c in caras:
        membrana(out, P, a, b, c, P['oreja'], semilla=semilla + 1)


def cuchillo(out, Mh, P, dx=0.0, giro=0.0, escala=1.0, semilla=0):
    """El cuchillo de pedernal plano, de cara, ancho abajo y en punta arriba, echado un poco atras, con su nervio; dx lo
    corre a un lado y giro lo abre hacia fuera."""
    piv = np.array((dx, 3.4, 4.4))
    M = Mh @ vr.T(*piv) @ vr.Rz(giro) @ np.diag([escala, escala, escala, 1.0]) @ vr.T(*(-np.array((0.0, 3.4, 4.4))))
    b0, b1 = pt(M, (-1.3, 3.4, 4.4)), pt(M, (1.3, 3.4, 4.4))
    m0, m1 = pt(M, (-1.7, 5.4, 3.7)), pt(M, (1.7, 5.4, 3.7))
    punta = pt(M, (0.0, 9.0, 2.6))
    for q in ((b0, b1, m1, m0), (b1, b0, m0, m1)):
        lamina(out, q, P['pedernal'], 3.4, 2.1, semilla=semilla)
    for q in ((m0, m1, punta, punta), (m1, m0, punta, punta)):
        lamina(out, q, P['pedernal'], 3.4, 3.8, semilla=semilla)
    jm.tubo(out, [pt(M, (0.0, 3.4, 4.3)), pt(M, (0.0, 8.4, 2.8))], [0.35, 0.15], [P['pedernal']], semilla=semilla)


def herradura(out, Mh, P, semilla=0):
    """La nariz en herradura: una placa de cuerno en U alrededor de las narices y un cuchillo corto de pedernal encima."""
    for x0, x1, y0, y1 in ((-1.7, -1.15, 1.7, 3.9), (1.15, 1.7, 1.7, 3.9), (-1.7, 1.7, 1.3, 1.9)):
        caja(out, Mh, x0, x1, y0, y1, 5.6, 5.95, P['casco'], semilla=semilla)
    cuchillo(out, Mh, P, escala=0.7, semilla=semilla + 1)


def cabeza(out, Mh, P, abre=40.0, orejas_atras=0.0, orejas='altas', nariz='cuchillo', semilla=0):
    """La cabeza de Zotzara, con el hocico hacia +z y la boca en y=0: ancha y corta, con el morro chato y vuelto hacia
    arriba; la hoja de la nariz (el cuchillo de pedernal, dos en V o la herradura) que se alza del morro entre las
    orejas; los ojos pequenos y encendidos; las orejas enormes (altas, con muesca o en corona). Las fauces, abiertas desde muy atras: el paladar encendido en escalones, los dientes en hojas, dos colmillos
    largos arriba y dos abajo, el suelo de la boca encendido y el nucleo al fondo. Devuelve la boca."""
    p = P['piel']
    F = {'abajo': P['fauces']}
    bm.cubo(out, Mh, -3.0, 0.0, -3.8, 6.0, 4.4, 5.0, p, caras=F, semilla=semilla)                   # el craneo
    bm.cubo(out, Mh, -2.4, 0.3, 1.2, 4.8, 3.2, 3.2, p, caras=F, semilla=semilla + 1)               # el morro
    bm.cubo(out, Mh, -2.0, 1.4, 4.4, 4.0, 2.4, 1.2, p, caras=F, semilla=semilla + 2)               # chato, vuelto arriba
    for s in (1, -1):
        bm.cubo(out, Mh, s * 1.0 - 0.4, 3.0, 5.4, 0.8, 0.6, 0.3, P['casco'], semilla=semilla + 3)      # las narices
        bm.cubo(out, Mh, 2.2 if s > 0 else -2.6, 2.6, 0.4, 0.4, 1.0, 1.0, P['ojo'], semilla=semilla + 4)  # los ojos
        bm.cubo(out, Mh, 2.0 if s > 0 else -2.6, 3.5, -0.2, 0.6, 0.6, 1.8, p, semilla=semilla + 5)        # la ceja
        oreja(out, P, Mh, s, atras=orejas_atras, forma=orejas, semilla=semilla + 6)
    if nariz == 'doble':                                                # la hoja de la nariz
        for s in (1, -1):
            cuchillo(out, Mh, P, dx=s * 1.1, giro=-s * 0.38, escala=0.85, semilla=semilla + 7)
    elif nariz == 'herradura':
        herradura(out, Mh, P, semilla=semilla + 7)
    else:
        cuchillo(out, Mh, P, semilla=semilla + 7)
    hilera(out, Mh, [(-2.2, 0.2), (-2.2, 5.4), (2.2, 5.4), (2.2, 0.2)], 0.6, -1.1, P['dientes_arriba'], semilla=semilla + 8)
    for s in (1, -1):
        colmillo(out, Mh, (s * 1.6, 0.6, 4.8), 3.8, 1.0, (0, -1, 0.05), P, semilla=semilla + 9)
    caja(out, Mh, -2.2, 2.2, -2.0, 0.2, -3.1, -2.8, P['nucleo'], semilla=semilla + 10)
    Mj = Mh @ vr.T(0.0, 0.0, -3.2) @ vr.Rx(abre * D)                                                # la quijada de abajo
    bm.cubo(out, Mj, -2.8, -3.2, -0.6, 5.6, 3.2, 4.6, p, caras={'arriba': P['boca']}, semilla=semilla + 11)
    bm.cubo(out, Mj, -2.3, -2.0, 4.0, 4.6, 2.0, 4.6, p, caras={'arriba': P['boca']}, semilla=semilla + 12)
    hilera(out, Mj, [(-2.0, 3.2), (-2.0, 8.4), (2.0, 8.4), (2.0, 3.2)], 0.0, 1.0, P['dientes_abajo'], semilla=semilla + 13)
    for s in (1, -1):
        colmillo(out, Mj, (s * 1.5, 0.0, 7.9), 3.0, 0.9, (0, 1, 0.05), P, semilla=semilla + 14)
    return pt(Mh, (0.0, -0.8, 2.6))


def collar(out, P, centro, eje, r, n=12, semilla=0):
    """El collar de pelo tieso alrededor del cuello: mechones de bloques que salen hacia fuera y abajo."""
    centro, eje = np.asarray(centro, float), _u(eje)
    a = _u(np.cross(eje, (1.0, 0.0, 0.0)))
    b = np.cross(eje, a)
    for i in range(n):
        g = TAU * i / n
        d = a * math.cos(g) + b * math.sin(g)
        base = centro + d * r * 0.8
        punta = base + d * r * 0.9 - eje * r * 0.9
        jm.tubo(out, [base, punta], [r * 0.45, r * 0.12], [P['pelo']], semilla=semilla + i % 3)


def pata(out, P, cadera, rodilla, tobillo, pie, semilla=0):
    """Una pata de garras: el muslo, la canilla que va hacia atras, el tarso y el pie con tres garras de cuerno."""
    pts = [np.asarray(v, float) for v in (cadera, rodilla, tobillo, pie)]
    jm.tubo(out, pts, [2.8, 2.0, 1.4, 1.2], [P['piel']] * 3, semilla=semilla)
    for q, r in zip(pts[1:3], (2.0, 1.5)):
        caja(out, vr.T(*q), -r, r, -r, r, -r, r, P['piel'], semilla=semilla + 1)
    caja(out, vr.T(*pts[3]), -1.6, 1.6, -0.9, 0.9, -1.4, 1.6, P['piel'], semilla=semilla + 2)
    km.garras(out, P, pts[3] + np.array((0.0, 0.0, 1.0)), (0.0, 0.0, 1.0), semilla=semilla + 3)


def _cabeza_en(out, P, nuca, mira, abre, V, semilla=0):
    R = em.marco((0.0, 0.0, 0.0), _u(np.array(mira, float)), up=(0.0, 1.0, 0.0))
    o = np.asarray(nuca, float) - pt(R, np.array((0.0, 4.4, -3.4)) * CABEZA)
    Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
    bm.PPB = PPB / CABEZA
    boca = cabeza(out, Mh, P, abre=abre, orejas=V.get('orejas', 'altas'), nariz=V.get('nariz', 'cuchillo'), semilla=semilla)
    bm.PPB = PPB
    return Mh, boca


def arbol(out, P, alto, x_tronco, x_punta, semilla=0):
    """El arbol muerto de la Colgada: el tronco nudoso que se tuerce, la rama gruesa que sale de lado y se dobla (de
    ella se cuelga) y otras ramas que suben, partidas, con las raices al aire."""
    tronco = [np.array((x_tronco, 0.0, -4.0)), np.array((x_tronco + 2.5, alto * 0.35, -5.0)), np.array((x_tronco - 1.0, alto * 0.75, -3.5)),
              np.array((x_tronco - 3.0, alto + 3.0, -3.0))]
    ps, rs, _ = jm.a_lo_largo(tronco, 7, ((0.0, 5.6), (0.5, 4.0), (1.0, 3.0)))
    jm.tubo(out, ps, rs, [P['corteza']] * (len(ps) - 1), semilla=semilla)
    for q, r in list(zip(ps, rs))[1:-1:2]:                              # los nudos
        caja(out, vr.T(*q) @ vr.Ry(0.6), -r * 1.15, r * 1.15, -r * 0.6, r * 0.6, -r * 1.1, r * 1.1, P['corteza'], semilla=semilla + 1)
    rama = [np.array((x_tronco - 2.0, alto + 0.5, -3.0)), np.array(((x_tronco + x_punta) * 0.5, alto + 4.0, -1.5)),
            np.array((x_punta + 3.0, alto + 2.5, -0.5)), np.array((x_punta - 2.0, alto + 6.5, 0.5))]
    ps, rs, _ = jm.a_lo_largo(rama, 8, ((0.0, 3.0), (0.6, 2.0), (1.0, 0.6)))
    jm.tubo(out, ps, rs, [P['corteza']] * (len(ps) - 1), semilla=semilla + 2)
    for k, (a, b, c) in enumerate((((x_tronco - 2.5, alto + 2.5, -3.0), (x_tronco + 3.0, alto + 12.0, -5.0), (x_tronco + 7.0, alto + 15.0, -4.0)),
                                   ((x_tronco - 3.0, alto + 3.0, -3.0), (x_tronco - 6.0, alto + 11.0, -1.0), (x_tronco - 5.0, alto + 16.0, 1.0)),
                                   ((x_tronco + 1.5, alto * 0.6, -4.0), (x_tronco + 8.0, alto * 0.72, -2.0), (x_tronco + 11.0, alto * 0.85, -3.0)))):
        jm.tubo(out, [np.array(a), np.array(b), np.array(c)], [1.6, 1.0, 0.3], [P['corteza'], P['corteza']], semilla=semilla + 3 + k)
    for k in range(4):                                                  # las raices
        g = k * 1.6 + 0.3
        a = np.array((x_tronco, 1.2, -4.0))
        jm.tubo(out, [a, a + np.array((math.cos(g) * 4.0, 1.0, math.sin(g) * 4.0)), a + np.array((math.cos(g) * 8.0, -0.8, math.sin(g) * 8.0))],
                [2.4, 1.4, 0.5], [P['corteza'], P['corteza']], semilla=semilla + 6)


# ======================================================================
#  ZOTZARA
# ======================================================================
def zotzara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    P['corteza'] = jm.liso(_r('0e0c0a', '181410', '221c16', '2e261e', '3c3228'), 2, 1, 1)
    P['corteza'].__name__ = 'zot%s_corteza' % V['clave']
    pose = V['pose']
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        if pose == 'abierta':                                           # agachada
            pelvis, pecho = np.array((0.0, 14.0, -2.0)), np.array((0.0, 24.0, 3.0))
            mira, abre = (0.0, -0.1, 1.0), 44.0
        else:
            pelvis, pecho = np.array((0.0, 18.0, -1.0)), np.array((0.0, 29.0, 3.0))
            mira, abre = (0.0, -0.4 if pose == 'capa' else 0.35, 1.0), 40.0
        # el tronco: flaco, encorvado, con el pecho hondo
        ps, rs, _ = jm.a_lo_largo([pelvis, (pelvis + pecho) / 2 + np.array((0.0, 0.0, -1.0)), pecho], 6,
                                  ((0.0, 3.4), (0.45, 2.8), (0.85, 4.6), (1.0, 4.2)))
        jm.tubo(out, ps, rs, [P['piel']] * (len(ps) - 1), semilla=10, achata=1.1)
        cuello = [pecho + np.array((0.0, 1.5, 0.5)), pecho + np.array((0.0, 4.5, 2.5))]
        jm.tubo(out, cuello, [3.0, 2.4], [P['piel']], semilla=11)
        collar(out, P, cuello[0] + np.array((0.0, 0.5, 0.0)), cuello[1] - cuello[0], 4.0, semilla=12)
        if pose != 'colgada':
            Mh, boca = _cabeza_en(out, P, cuello[1] + np.array((0.0, 2.2, -0.5)), mira, abre, V, semilla=20)
        # las patas
        for s in (1, -1):
            c = pelvis + np.array((s * 3.0, -0.5, 0.0))
            if pose == 'abierta':
                pata(out, P, c, (s * 6.5, 9.0, 4.5), (s * 6.5, 4.0, -2.5), (s * 6.8, 1.0, 1.0), semilla=30)
            else:
                pata(out, P, c, (s * 4.2, 10.5, 3.0), (s * 4.2, 4.5, -2.0), (s * 4.5, 1.0, 1.6), semilla=30)
        # las alas
        for s in (1, -1):
            hombro = pecho + np.array((s * 3.8, 0.5, -0.5))
            if pose == 'abierta':
                codo = np.array((s * 11.0, 27.0, 0.0))
                muneca = np.array((s * 19.0, 31.0, 2.0))
                dedos = [((s * 24.0, 36.0, 3.0), (s * 31.0, 40.0, 4.0)), ((s * 25.5, 31.0, 2.5), (s * 33.0, 29.0, 3.0)),
                         ((s * 23.5, 26.0, 2.0), (s * 29.0, 18.0, 2.0)), ((s * 20.0, 23.0, 1.0), (s * 22.0, 10.0, 0.0))]
                pie = (s * 6.6, 3.0, -2.0)
            else:                                                       # cerradas por delante, como una capa
                codo = hombro + np.array((s * 3.5, -6.0, -3.0))
                muneca = hombro + np.array((s * 2.6, 7.0, 1.0))
                dedos = [(muneca + (s * 2.5, -9.0, 5.5), (s * 3.2, 5.0, 10.5)), (muneca + (s * 4.5, -10.0, 4.0), (s * 7.5, 2.5, 8.5)),
                         (muneca + (s * 5.5, -10.0, 1.5), (s * 10.0, 2.5, 3.5)), (muneca + (s * 5.0, -10.0, -2.0), (s * 9.0, 3.5, -3.0))]
                pie = (s * 4.5, 3.0, -2.0)
            ala(out, P, hombro, codo, muneca, dedos, pie, estilo=V.get('alas', 'festones'), semilla=40)
    finally:
        bm.PPB = ppb
    if pose == 'colgada':                                               # boca abajo, colgada de la rama por los pies
        alto = 50.0
        G = vr.T(0.0, alto, 0.0) @ vr.Rz(math.pi)
        out = qm.transformar(out, G)
        bm.PPB = PPB
        try:                                                            # la cabeza, derecha, debajo del cuello
            nuca = pt(G, cuello[1]) + np.array((0.0, 1.0, 1.0))
            R = em.marco((0.0, 0.0, 0.0), _u(np.array((0.0, -0.05, 1.0))), up=(0.0, 1.0, 0.0))
            o = nuca - pt(R, np.array((0.0, 4.4, -3.4)) * CABEZA)
            Mh = vr.T(*o) @ R @ np.diag([CABEZA] * 3 + [1.0])
            bm.PPB = PPB / CABEZA
            boca = cabeza(out, Mh, P, abre=40.0, orejas_atras=75.0, orejas=V.get('orejas', 'altas'), nariz=V.get('nariz', 'cuchillo'),
                          semilla=20)
            bm.PPB = PPB
            arbol(out, P, alto - 1.0, 18.0, -10.0, semilla=60)
        finally:
            bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0.0, -min(y0, 0.0) if pose == 'colgada' else -y0, 0.0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

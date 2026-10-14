"""
Melenara, la Manticora (13-10-2026). Juan, tras rechazar Almenara: «vamos con otro... ya no de
este monstruo sino otro y sus variables».

Una manticora: el monstruo de siempre que ya es tres bichos (cuerpo de leon, alas de murcielago
y cola de escorpion), con su giro: la melena no es de pelo sino una GORGUERA de membrana tendida
entre puas de quitina que brillan en la punta, y enmarca una cabeza enorme que ruge de frente:
la cara de hueso palido (ceja, hocico y menton), los ojos rasgados y encendidos, y la boca ancha
y roma con TRES HILERAS de dientes (dibujados en hojas), dos colmillos de sable y la garganta
encendida de un solo neon. Plantada de pie, con el pecho alto y la cabeza mirando abajo, al
jugador; la cola sube en arco por encima de la melena con el aguijon apuntando hacia delante.

Hecha con lo aprendido en Lumara: la cabeza manda (se hace sin escala y se pone agrandada), pocas
piezas y gordas, la cara clara sobre lo oscuro (como la mandibula lila de Lumara), los dientes van
en hojas, la piel esta dibujada a mano (la tesela de manchas de Lumara), la cola es de tambores
de una pieza, y las fotos van sin letras y con el borde blanco. Para no parecerse a Lumara, la
boca no es de pentagono (es ancha y roma) y se ve de frente, no de perfil.

Los tres tipos cambian de FORMA:

    A  Alada                alas de murcielago alzadas en V, con el borde libre encendido; la
                            gorguera de membrana; una cola de escorpion; piel ciruela; magenta
    B  de las Puas          sin alas y sin membrana: una corona de puas en vez de gorguera, todo
                            el lomo erizado de puas y la cola acaba en una maza de puas; musgo; lima
    C  de las Tres Colas    sin alas: tres colas de escorpion abiertas en abanico alrededor de la
                            cabeza, cada una con su aguijon; la gorguera mas corta; azul noche; cian
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
from sierpe_modelo import _bisel, lamina, bola
from riscara_modelo import bloque
from lumara_modelo import _dir, _tesela

TAU = math.tau
D = vr.D2R
_r = bm._r
bm.PPB = 8

DIENTE = _r('5e5a52', '8e887c', 'bdb6a6', 'ddd8ca', 'f4f1e8')
VARIANTES = {
    'A': dict(
        clave='A', nombre='Alada', color='Dorada',
        piel=_r('1a120a', '2a1e12', '3e2c1a', '584028', '7a5a3a'),
        hueso=_r('5a4630', '86704e', 'b49a72', 'd8c49c', 'f2e6c8'),
        quitina=_r('160e06', '26180c', '3a2614', '563a1e', '7a5428'),
        garra=_r('0e0a06', '1a140c', '2a2014', '3c2e1e', '54422c'),
        membrana=_r('140c06', '26180c', '3c2814', '5c3e1e', '86602c'),
        ala=_r('140c04', '24160a', '3a2410', '563618', '7a4e22'),
        neon=('fff6dc', 'ffb52e', '7a3a06'),
    ),
    'B': dict(
        clave='B', nombre='de las Puas', color='Sangre',
        piel=_r('140a0a', '221212', '341c1a', '4c2a26', '6a3c36'),
        hueso=_r('5e5448', '8a7e70', 'b8ac9c', 'dcd2c2', 'f6f0e4'),
        quitina=_r('120808', '221010', '361a18', '502624', '6e3634'),
        garra=_r('0c0808', '181010', '261a1a', '382828', '4e3a3a'),
        membrana=_r('100808', '1e0e0e', '2e1616', '422020', '5a2c2c'),
        ala=_r('100808', '1e0e0e', '2e1616', '422020', '5a2c2c'),
        neon=('ffe4dc', 'ff3324', '6a0806'),
    ),
    'C': dict(
        clave='C', nombre='de las Tres Colas', color='Ceniza',
        piel=_r('1c1c1e', '2c2c2e', '424244', '5c5c5e', '7c7a7a'),
        hueso=_r('64625e', '8e8c86', 'b8b6ae', 'dcdad2', 'f6f6f0'),
        quitina=_r('141416', '222224', '343436', '4a4a4c', '666668'),
        garra=_r('0c0c0e', '18181a', '262628', '38383a', '4e4e50'),
        membrana=_r('121214', '1e1e20', '2c2c2e', '3e3e40', '545456'),
        ala=_r('121214', '1e1e20', '2c2c2e', '3e3e40', '545456'),
        neon=('fffdf6', 'f2ead6', '6a6458'),
    ),
}


def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'mel%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']
    c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)

    def piel(tw, th, cara, s):
        """La piel: oscura, con las manchas grandes de la tesela dibujada a mano, apagadas."""
        idx = np.array([0, 1, 1, 2, 2])[_tesela(tw, th, s)]
        return _imagen(_bisel(idx), V['piel']), None
    reg('piel', piel)

    def hueso(tw, th, cara, s):
        """La cara de hueso palido (ceja, hocico y menton): lisa, con su canto y una veta clara."""
        idx = np.full((th, tw), 2)
        if tw >= 6:
            idx[:, 1] = 3
        if th >= 6:
            idx[1, :] = 3
        return _imagen(_bisel(idx), V['hueso']), None
    reg('hueso', hueso)

    def quitina(tw, th, cara, s):
        """La quitina de la cola y de las puas: anillos oscuros cada cuatro pixeles y el canto claro."""
        ys, xs = np.mgrid[0:th, 0:tw]
        largo_x = tw >= th
        a = xs if largo_x else ys
        idx = np.where((a % 4) == 0, 1, 2)
        if largo_x and th >= 3:
            idx[0, :] = np.maximum(idx[0, :], 3)
            idx[1, :] = np.where(idx[1, :] == 2, 3, idx[1, :])
        elif tw >= 3:
            idx[:, 0] = np.maximum(idx[:, 0], 3)
        return _imagen(idx, V['quitina']), None
    reg('quitina', quitina)

    def garra(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if tw >= th and th >= 2:
            idx[0, :] = 4
            idx[-1, :] = 1
        elif tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 1
        return _imagen(idx, V['garra']), None
    reg('garra', garra)

    def nariz(tw, th, cara, s):
        idx = np.full((th, tw), 1)
        if th >= 3:
            idx[0, :] = 2
        return _imagen(idx, V['garra']), None
    reg('nariz', nariz)

    def punta(tw, th, cara, s):
        """La punta de cada pua y el aguijon: el neon, casi blanco en el centro."""
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('punta', punta, pleno=True)

    def ojo(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo', ojo, pleno=True)

    def _hojas_de_dientes(tw, th, colgando):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTE]
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

    def colmillos(tw, th, cara, s):
        """Los dientes de arriba, dibujados en una hoja que cuelga (no cubos)."""
        return _hojas_de_dientes(tw, th, True)
    reg('colmillos', colmillos)

    def dientes(tw, th, cara, s):
        """Los dientes de abajo, en una hoja de pie."""
        return _hojas_de_dientes(tw, th, False)
    reg('dientes', dientes)

    def sable(tw, th, cara, s):
        """Un colmillo de sable dibujado en una hoja: ancho en la raiz (arriba de la textura) y en
        punta, claro por el centro y con el filo oscuro."""
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTE]
        for y in range(th):
            f = y / max(th - 1, 1)
            ancho = max(1.0, tw * 0.94 * (1 - f) ** 0.75)
            x0 = int(round((tw - ancho) / 2))
            x1 = max(x0, int(round((tw + ancho) / 2)) - 1)
            for x in range(max(x0, 0), min(x1 + 1, tw)):
                u = (x - x0) / max(x1 - x0, 1)
                t[y, x] = c[3] if u < 0.4 else (c[4] if u < 0.7 else c[2])
            t[y, max(x0, 0)] = c[2]
            if x1 > x0:
                t[y, min(x1, tw - 1)] = c[1]
        m = t[0, :, 3] > 0
        t[0, m] = c[1]
        return t, None
    reg('sable', sable)

    def encia(tw, th, cara, s):
        """Por dentro de la boca, donde no llega la luz: el neon hondo, casi negro."""
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = qm._mezcla(c_h, (8, 4, 8), 0.55)
        t[..., 3] = 255
        return t, None
    reg('encia', encia)

    def fauces(tw, th, cara, s):
        """El paladar y la bandeja de abajo: hondo junto a los dientes y cada vez mas claro hacia la
        garganta, en escalones, con las estrias del paladar. Arriba de la textura, los dientes."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            f = y / max(th - 1, 1)
            if f > 0.86:
                c = c_n
            elif f > 0.66:
                c = qm._mezcla(c_m, c_n, 0.45)
            elif f > 0.42:
                c = c_m
            elif f > 0.2:
                c = qm._mezcla(c_h, c_m, 0.5)
            else:
                c = c_h
            t[y, :] = (*c, 255)
            if y % 3 == 2 and f < 0.86:
                t[y, :] = (*qm._mezcla(c_h, (0, 0, 0), 0.3), 255)
        if tw >= 3:
            t[:, 0] = (*c_h, 255)
            t[:, -1] = (*c_h, 255)
        return t, _emis(t, np.ones((th, tw), bool), 225)
    reg('fauces', fauces)

    def garganta(tw, th, cara, s):
        """El fondo de la boca: un resplandor redondo, blanco en el centro, con el cerco hondo."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot((xs - cx) / max(tw / 2, 1), (ys - cy) / max(th / 2, 1))
        col = np.where((r < 0.3)[..., None], np.array(c_n),
                       np.where((r < 0.55)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)),
                                np.where((r < 0.8)[..., None], np.array(c_m), np.array(c_h))))
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r < 0.8, 240)
    reg('garganta', garganta)

    def lengua(tw, th, cara, s):
        """La lengua: el neon hondo, con el surco del medio mas oscuro."""
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = qm._mezcla(c_h, c_m, 0.4)
        t[..., 3] = 255
        if tw >= 4:
            t[:, tw // 2 - 1:tw // 2 + 1, :3] = c_h
        return t, _emis(t, np.ones((th, tw), bool), 110)
    reg('lengua', lengua)

    def gorguera(tw, th, cara, s):
        """La gorguera: la membrana lisa, oscura junto a la raiz y mas clara hacia fuera, con dos
        venas finas que salen de la cara; cerca del borde libre (arriba de la textura), una banda de
        hueso, y el borde en dientes de sierra."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        v = ys / max(th - 1, 1)                                   # 0 en el borde libre, 1 en la raiz
        idx = np.where(v > 0.68, 0, np.where(v > 0.34, 1, 2))
        for g in (0.33, 0.67):
            idx = np.where(np.abs(xs - g * (tw - 1)) < 0.6, np.maximum(idx - 1, 0), idx)
        img = _imagen(idx, V['membrana'])
        A = max(2.0, th * 0.11)
        fase = (xs % 6 + 0.5) / 6
        borde = A * np.abs(fase * 2 - 1)                          # el diente acaba en punta arriba
        banda = (ys >= borde + 1) & (ys < borde + 1 + max(2.0, th * 0.08))
        img[banda] = (*V['hueso'][3], 255)
        img[(ys >= borde) & (ys < borde + 1)] = (*V['hueso'][1], 255)
        dentro = ys >= borde
        t[dentro] = img[dentro]
        return t, None
    reg('gorguera', gorguera)

    def ala(tw, th, cara, s):
        """El ala de avispa: larga, estrecha en la raiz (abajo) y redonda en la punta (arriba); la
        membrana lisa en dos tonos, mas clara hacia el borde de atras; tres venas finas a lo largo y
        cuatro de traves que hacen pocas celdas grandes; un brillo; el borde de delante (a la
        izquierda) grueso; y la mancha de la punta, encendida."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        v = 1 - ys / max(th - 1, 1)                               # 0 en la raiz, 1 en la punta
        u = (xs + 0.5) / tw                                       # 0 en el borde de delante
        semi = np.where(v < 0.6, 0.2 + 0.8 * np.clip(v / 0.6, 0, 1) ** 0.5,
                        np.sqrt(np.clip(1 - ((v - 0.6) / 0.4) ** 2, 0, 1)))
        dentro = u <= semi
        w = np.maximum(semi, 1e-3)
        f = u / w                                                 # 0 delante, 1 en el borde de atras
        idx = np.where(f < 0.5, 2, 3)
        idx = np.where(v < 0.2, 1, idx)
        img = _imagen(idx, V['ala'])
        px = 1.0 / tw

        def linea(g, v0, v1):
            return (np.abs(f - g) * w < 0.6 * px) & (v >= v0) & (v <= v1)
        vena = linea(0.28, 0.0, 0.74) | linea(0.56, 0.0, 0.96) | linea(0.8, 0.0, 0.62)
        fila = ys.astype(int)
        for vv, g0, g1 in ((0.32, 0.28, 0.56), (0.5, 0.56, 0.8), (0.62, 0.28, 0.56), (0.74, 0.56, 1.0)):
            vena |= (fila == int(round((1 - vv) * (th - 1)))) & (f >= g0) & (f <= g1)
        vena |= (f > 0.95)
        costa = xs < max(2.0, tw * 0.1)
        img[linea(0.42, 0.36, 0.6)] = (*V['ala'][4], 255)        # el brillo
        img[vena] = (*V['ala'][0], 255)
        img[costa] = (*V['quitina'][1], 255)
        mancha = (v > 0.76) & (v < 0.87) & (f < 0.34) & ~costa      # el pterostigma
        img[mancha] = (*c_m, 255)
        t[dentro] = img[dentro]
        return t, _emis(t, mancha & dentro, 200)
    reg('ala', ala)
    return P


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
def _garra(out, p, d, largo, grueso, P, semilla=0, curva=(0.0, -1.0, 0.3)):
    """Una garra de dos tramos que se dobla hacia 'curva'."""
    p = np.asarray(p, float)
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    q = p + d * largo * 0.6
    viga(out, p, q, grueso, grueso, P['garra'], extra=grueso * 0.3, semilla=semilla)
    c = np.asarray(curva, float)
    c = c / np.linalg.norm(c)
    pua(out, em.marco(q, c) @ vr.Rx(90 * D), grueso * 0.42, largo * 0.55, P['garra'], semilla=semilla + 1)


def _zarpa(out, p, P, s, semilla=0, ancho=2.0):
    """La zarpa en el suelo: el pie de piel y cuatro garras que se clavan delante."""
    p = np.asarray(p, float)
    bloque(out, vr.T(p[0], p[1] + 0.5, p[2]), ancho, 1.0, ancho * 1.1, P['piel'], semilla=semilla)
    for j in range(4):
        f = (j - 1.5) / 1.5
        q = p + np.array((f * ancho * 0.38, 0.35, ancho * 0.5))
        _garra(out, q, (f * 0.25, 0.0, 1.0), 0.9, 0.3, P, semilla=semilla + 2 + j, curva=(0.0, -1.0, 0.3))


def _pua(out, base, d, largo, grueso, P, semilla=0):
    """Una pua: el asta de quitina en dos tramos (se afina) y la punta que brilla."""
    base = np.asarray(base, float)
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    m = base + d * largo * 0.45
    q = base + d * largo * 0.72
    viga(out, base, m, grueso, grueso, P['quitina'], extra=grueso * 0.25, semilla=semilla)
    viga(out, m, q, grueso * 0.7, grueso * 0.7, P['quitina'], extra=grueso * 0.15, semilla=semilla + 1)
    pua(out, em.marco(q, d) @ vr.Rx(90 * D), grueso * 0.42, largo * 0.32, P['punta'], semilla=semilla + 2)


def _cola(out, ctrl, radios, P, semilla=0):
    """Una cola de escorpion: segmentos gordos de quitina, de una pieza y un poco abombados (como
    cuentas), con una junta oscura entre uno y otro; devuelve las juntas."""
    curva, _ = em.catmull(ctrl, 400)
    curva = [np.asarray(p, float) for p in curva]
    L = [0.0]
    for a, b in zip(curva, curva[1:]):
        L.append(L[-1] + float(np.linalg.norm(b - a)))
    total = L[-1]

    def en(m):
        i = min(max(int(np.searchsorted(L, m)), 1), len(curva) - 1)
        f = (m - L[i - 1]) / max(L[i] - L[i - 1], 1e-9)
        return curva[i - 1] + (curva[i] - curva[i - 1]) * min(max(f, 0.0), 1.0)

    def radio(m):
        return float(np.interp(m / total, (0.0, 1.0), radios))

    cortes = [0.0]
    while True:
        largo = max(1.4, 2.5 * radio(cortes[-1]))
        if cortes[-1] + largo > total - 0.8:
            break
        cortes.append(cortes[-1] + largo)
    cortes.append(total)
    pts = [en(m) for m in cortes]
    for j in range(len(pts) - 1):
        d = pts[j + 1] - pts[j]
        Ld = float(np.linalg.norm(d))
        r = radio((cortes[j] + cortes[j + 1]) / 2)
        M = em.marco(pts[j], d, up=(1.0, 0.0, 0.0)) if abs(d[0]) < 0.2 * Ld else em.marco(pts[j], d)
        bloque(out, M @ vr.T(0, 0, Ld / 2), 2 * r, 2 * r * 0.94, Ld + 0.15, P['quitina'], semilla=semilla + j, redondeo=0.72)
        cubo(out, M, -r * 0.78, -r * 0.78, -0.2, 1.56 * r, 1.56 * r, 0.4, P['garra'], semilla=semilla + 30 + j)
    return pts


def _aguijon(out, p, d, P, semilla=0, g=1.0):
    """El aguijon: el bulbo gordo de quitina y la punta larga y curva que brilla, en tres tramos que
    se doblan hacia abajo y hacia atras."""
    p = np.asarray(p, float)
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    M = em.marco(p, d)
    bloque(out, M @ vr.T(0, -0.1 * g, 1.3 * g), 2.5 * g, 2.3 * g, 2.9 * g, P['quitina'], semilla=semilla)
    q = punto(M, (0, -0.25 * g, 2.6 * g))
    tramos = (((0.0, -0.45, 1.0), 0.72, 1.2, P['quitina']), ((0.0, -1.0, 0.55), 0.52, 1.1, P['punta']),
              ((0.0, -1.0, -0.25), 0.36, 0.9, P['punta']))
    for k_, (dd, gr, lg, pin) in enumerate(tramos):
        dd = _dir(M, dd)
        dd = dd / np.linalg.norm(dd)
        q2 = q + dd * lg * g
        viga(out, q, q2, gr * g, gr * g, pin, extra=0.08, semilla=semilla + 1 + k_)
        q = q2
    pua(out, em.marco(q, dd) @ vr.Rx(90 * D), 0.18 * g, 0.75 * g, P['punta'], semilla=semilla + 5)


def _tronco(out, M, z0, z1, atras, delante, pintores, semilla=0):
    """Un tronco a lo largo de z en el marco M: la seccion de atras (en z0) y la de delante (en z1)
    son rectangulos (x0, x1, y0, y1). Se lee menos a caja que un cubo porque se afina. pintores
    dice el de cada cara: 'arriba', 'abajo', 'lados', 'frente' y 'atras' (sin pintor, no se dibuja)."""
    (bx0, bx1, by0, by1), (fx0, fx1, fy0, fy1) = atras, delante
    B = lambda x, y: punto(M, (x, y, z0))
    F = lambda x, y: punto(M, (x, y, z1))
    caras = []
    if pintores.get('arriba'):
        caras.append(((B(bx0, by1), B(bx1, by1), F(fx1, fy1), F(fx0, fy1)), pintores['arriba']))
    if pintores.get('abajo'):
        caras.append(((F(fx0, fy0), F(fx1, fy0), B(bx1, by0), B(bx0, by0)), pintores['abajo']))
    if pintores.get('lados'):
        caras.append(((B(bx0, by0), F(fx0, fy0), F(fx0, fy1), B(bx0, by1)), pintores['lados']))
        caras.append(((F(fx1, fy0), B(bx1, by0), B(bx1, by1), F(fx1, fy1)), pintores['lados']))
    if pintores.get('frente'):
        caras.append(((F(fx0, fy0), F(fx1, fy0), F(fx1, fy1), F(fx0, fy1)), pintores['frente']))
    if pintores.get('atras'):
        caras.append(((B(bx1, by0), B(bx0, by0), B(bx0, by1), B(bx1, by1)), pintores['atras']))
    for k, (P4, pin) in enumerate(caras):
        p0, p1, p2, p3 = P4
        ancho = float(max(np.linalg.norm(p1 - p0), np.linalg.norm(p2 - p3), 0.05))
        alto = float(max(np.linalg.norm(p3 - p0), np.linalg.norm(p2 - p1), 0.05))
        lamina(out, P4, pin, ancho, alto, semilla + k)


def _planta(a_atras, a_delante, z0, z1, chaflan):
    """La planta de una mandibula que se afina, con la punta roma y las esquinas cortadas (no en
    pentagono, como Lumara): de atras-izquierda, por delante, a atras-derecha."""
    c = min(chaflan, a_delante * 0.9, (z1 - z0) * 0.9)
    return [(-a_atras, z0), (-a_delante, z1 - c), (-a_delante + c, z1), (a_delante - c, z1), (a_delante, z1 - c), (a_atras, z0)]


def _tapa(out, M, y, a0, a1, z0, z1, pintor, semilla=0):
    """Una tapa en trapecio a la altura y del marco M: ancha atras (z0) y mas estrecha delante (z1).
    La fila de arriba de la textura va delante (en los dientes) y la de abajo, al fondo."""
    P4 = (punto(M, (-a0 / 2, y, z0)), punto(M, (a0 / 2, y, z0)), punto(M, (a1 / 2, y, z1)), punto(M, (-a1 / 2, y, z1)))
    lamina(out, P4, pintor, max(a0, a1), z1 - z0, semilla)


def _hilera(out, M, planta, y, alto, pintor, semilla=0):
    """Una hilera de dientes en hojas, una por cada tramo de la planta: con alto negativo
    cuelgan y con alto positivo estan de pie."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(planta, planta[1:])):
        A, B = punto(M, (x0, y, z0)), punto(M, (x1, y, z1))
        A2, B2 = punto(M, (x0, y + alto, z0)), punto(M, (x1, y + alto, z1))
        lado = float(np.linalg.norm(B - A))
        if lado < 0.3:
            continue
        if alto < 0:
            lamina(out, (A2, B2, B, A), pintor, lado, abs(alto), semilla + j)      # arriba de la textura, la raiz
        else:
            lamina(out, (A, B, B2, A2), pintor, lado, abs(alto), semilla + j)      # arriba de la textura, las puntas


def _pata(out, p0, p1, r0, r1, pintor, semilla=0):
    """Un tramo de pata que se afina: un tronco de seccion cuadrada de p0 (medio lado r0) a p1 (r1)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    M = em.marco(p0, p1 - p0)
    todo = {'arriba': pintor, 'abajo': pintor, 'lados': pintor, 'frente': pintor, 'atras': pintor}
    _tronco(out, M, -r0 * 0.35, L + r1 * 0.35, (-r0, r0, -r0, r0), (-r1, r1, -r1, r1), todo, semilla=semilla)


def _sable(out, raiz, hacia, u, v, largo, ancho, pintor, semilla=0):
    """Un colmillo de sable en dos hojas cruzadas (se ve de frente y de lado), de la raiz hacia
    'hacia'."""
    raiz = np.asarray(raiz, float)
    hacia = np.asarray(hacia, float)
    hacia = hacia / np.linalg.norm(hacia)
    for k, e in enumerate((u, v)):
        e = np.asarray(e, float)
        e = e / np.linalg.norm(e)
        a, b = raiz - e * ancho / 2, raiz + e * ancho / 2
        lamina(out, (a + hacia * largo, b + hacia * largo, b, a), pintor, ancho, largo, semilla + k)


# ----------------------------------------------------------------------
#  El cuerpo de leon, plantado de pie con el pecho alto
# ----------------------------------------------------------------------
def cuerpo(out, V, P):
    """De pie y plantada: las ancas mas bajas, la cintura que sube y el pecho alto y ancho; las
    patas de delante rectas y abiertas, las de atras dobladas; el cuello ancho que sube."""
    bloque(out, vr.T(0, 6.0, -5.4) @ vr.Rx(-12 * D), 4.8, 4.2, 4.4, P['piel'], semilla=1)               # las ancas
    bloque(out, vr.T(0, 7.4, -2.4) @ vr.Rx(-22 * D), 4.0, 3.8, 4.2, P['piel'], semilla=3)               # la cintura
    bloque(out, vr.T(0, 8.8, 0.8) @ vr.Rx(-28 * D), 5.4, 5.0, 4.8, P['piel'], semilla=5)                # el pecho
    for s in (1, -1):
        bloque(out, vr.T(s * 2.5, 9.4, 1.3) @ vr.Rx(-20 * D), 2.2, 3.4, 3.0, P['piel'], semilla=7)      # el hombro
        hom, codo, mun = np.array((s * 2.7, 9.0, 1.6)), np.array((s * 3.0, 5.2, 2.1)), np.array((s * 3.0, 1.3, 2.9))
        _pata(out, hom, codo, 1.4, 1.05, P['piel'], semilla=8)
        _pata(out, codo, mun, 1.05, 0.85, P['piel'], semilla=9)
        _zarpa(out, np.array((s * 3.0, 0.0, 3.4)), P, s, semilla=10)
        bloque(out, vr.T(s * 2.35, 5.4, -5.0) @ vr.Rx(-10 * D), 2.3, 3.6, 3.4, P['piel'], semilla=16)   # el muslo
        cad, rod, cor = np.array((s * 2.45, 5.0, -4.9)), np.array((s * 2.85, 3.3, -2.4)), np.array((s * 2.75, 1.9, -6.4))
        _pata(out, cad, rod, 1.4, 1.0, P['piel'], semilla=17)
        _pata(out, rod, cor, 0.95, 0.72, P['piel'], semilla=18)
        _pata(out, cor, np.array((s * 2.75, 0.6, -5.0)), 0.75, 0.68, P['piel'], semilla=19)
        _zarpa(out, np.array((s * 2.75, 0.0, -4.7)), P, s, semilla=20, ancho=1.8)
    viga(out, np.array((0.0, 10.2, 2.0)), np.array((0.0, 12.4, 4.4)), 3.3, 3.3, P['piel'], extra=0.5, semilla=30)   # el cuello


# ----------------------------------------------------------------------
#  La cabeza (se hace sin escala; melenara() la pone agrandada)
# ----------------------------------------------------------------------
def cabeza(out, Mh, V, P):
    """La cabeza que ruge de frente, de pocas piezas y gordas: el craneo oscuro que se ensancha
    hacia los pomulos; la ceja de hueso en V y, debajo, los ojos rasgados y encendidos; el hocico
    de hueso, romo, con la nariz oscura; la boca abierta de par en par con TRES HILERAS de dientes
    (en hojas) arriba y abajo, dos colmillos de sable y dos de abajo; el menton de hueso; y al
    fondo, la garganta encendida y el paladar en escalones de luz."""
    oscuro = {'arriba': P['piel'], 'abajo': P['piel'], 'lados': P['piel'], 'frente': P['piel'], 'atras': P['piel']}
    _tronco(out, Mh, -3.0, 0.7, (-1.8, 1.8, 0.4, 3.3), (-2.4, 2.4, -0.3, 3.5), oscuro, semilla=1)        # el craneo
    for s in (1, -1):
        Mc = Mh @ vr.T(s * 0.15, 2.85, 0.6) @ vr.Rz(s * 18 * D)                                       # la ceja
        cubo(out, Mc, 0.0 if s > 0 else -2.45, -0.36, -0.55, 2.45, 0.72, 1.1, P['hueso'], semilla=3)
        Mo = Mh @ vr.T(s * 1.2, 2.2, 0.7) @ vr.Rz(s * 14 * D)                                         # el ojo
        cubo(out, Mo, -0.82, -0.34, 0.0, 1.64, 0.68, 0.08, P['garra'], semilla=4)
        cubo(out, Mo, -0.66, -0.21, 0.08, 1.32, 0.42, 0.03, None, caras={'frente': P['ojo']}, semilla=5)
    # el hocico de hueso, que se afina hacia la nariz
    Mu = Mh @ vr.T(0, 0.15, 0.2) @ vr.Rx(-3 * D)
    ZA, ZD = -0.6, 3.6
    AA, AD = 2.0, 1.45
    _tronco(out, Mu, ZA, ZD, (-AA, AA, -0.05, 1.75), (-AD, AD, -0.05, 1.15),
            {'arriba': P['hueso'], 'lados': P['hueso'], 'frente': P['hueso'], 'abajo': P['encia']}, semilla=6)
    zn = ZD + 0.04                                                                                       # la nariz, en trapecio
    lamina(out, (punto(Mu, (-0.32, 0.62, zn)), punto(Mu, (0.32, 0.62, zn)), punto(Mu, (0.9, 1.16, zn)), punto(Mu, (-0.9, 1.16, zn))),
           P['nariz'], 1.8, 0.56, semilla=9)
    cubo(out, Mu, -0.9, 0.95, ZD - 0.5, 1.8, 0.32, 0.5, P['nariz'], semilla=10)                         # su lomo
    lamina(out, (punto(Mu, (-0.07, -0.05, zn)), punto(Mu, (0.07, -0.05, zn)), punto(Mu, (0.07, 0.62, zn)), punto(Mu, (-0.07, 0.62, zn))),
           P['nariz'], 0.14, 0.67, semilla=11)                                                           # el surco
    for s in (1, -1):                                                                                    # los belfos
        bloque(out, Mu @ vr.T(s * (AD - 0.25), 0.3, ZD - 0.75), 1.0, 0.9, 1.3, P['hueso'], semilla=12)
    # el paladar en escalones de luz y las tres hileras de arriba
    Z0 = 0.5
    a_z0 = AA + (AD - AA) * (Z0 - ZA) / (ZD - ZA)
    _tapa(out, Mu, -0.08, 2 * a_z0 - 0.4, 2 * AD - 0.4, Z0, ZD - 0.25, P['fauces'], semilla=11)
    for k, (mete, alto) in enumerate(((0.12, -0.95), (0.48, -0.8), (0.84, -0.66))):
        _hilera(out, Mu, _planta(a_z0 - mete, AD - mete, Z0, ZD - mete, 0.6), -0.08 - 0.01 * k, alto, P['colmillos'],
                semilla=12 + 5 * k)
    for s in (1, -1):                                                                                    # los sables
        raiz = punto(Mu, (s * (AD - 0.45), -0.08, ZD - 0.7))
        _sable(out, raiz, _dir(Mu, (0.0, -1.0, 0.12)), _dir(Mu, (1, 0, 0)), _dir(Mu, (0, 0, 1)), 2.6, 0.66, P['sable'],
               semilla=28 + (s > 0) * 2)
    # la de abajo, abierta de par en par, con el menton de hueso
    Ml = Mh @ vr.T(0, 0.05, 0.0) @ vr.Rx(48 * D)
    LA, LD, BA, BD = -0.4, 3.4, 1.9, 1.35
    _tronco(out, Ml, LA, LD, (-BA, BA, -1.2, 0.0), (-BD, BD, -0.85, 0.0),
            {'abajo': P['hueso'], 'lados': P['hueso'], 'frente': P['hueso'], 'arriba': P['encia']}, semilla=30)
    b_z0 = BA + (BD - BA) * (Z0 - LA) / (LD - LA)
    _tapa(out, Ml, 0.04, 2 * b_z0 - 0.4, 2 * BD - 0.4, Z0, LD - 0.25, P['fauces'], semilla=37)
    _tronco(out, Ml, Z0 + 0.1, LD - 0.7, (-0.78, 0.78, 0.04, 0.36), (-0.6, 0.6, 0.04, 0.3),
            {'arriba': P['lengua'], 'lados': P['lengua'], 'frente': P['lengua']}, semilla=38)               # la lengua
    for k, (mete, alto) in enumerate(((0.12, 0.8), (0.48, 0.64), (0.84, 0.5))):
        _hilera(out, Ml, _planta(b_z0 - mete, BD - mete, Z0, LD - mete, 0.6), 0.04 + 0.01 * k, alto, P['dientes'],
                semilla=40 + 5 * k)
    for s in (1, -1):                                                                                    # los de abajo
        raiz = punto(Ml, (s * (BD - 0.42), 0.04, LD - 0.55))
        _sable(out, raiz, _dir(Ml, (0.0, 1.0, 0.05)), _dir(Ml, (1, 0, 0)), _dir(Ml, (0, 0, 1)), 1.15, 0.5, P['sable'],
               semilla=56 + (s > 0) * 2)
    # al fondo, la garganta: la pared que va del paladar a la bandeja, encendida
    pa, pb = (a_z0 - 0.2), (b_z0 - 0.2)
    q0, q1, q2, q3 = punto(Ml, (-pb, 0.04, Z0)), punto(Ml, (pb, 0.04, Z0)), punto(Mu, (pa, -0.08, Z0)), punto(Mu, (-pa, -0.08, Z0))
    lamina(out, (q0, q1, q2, q3), P['garganta'], 2 * pa, float(np.linalg.norm(q3 - q0)), semilla=60)
    # las comisuras: la piel oscura que va de una mandibula a la otra por los lados
    for s in (1, -1):
        a = punto(Mu, (s * (a_z0 - 0.05), -0.05, Z0 - 0.1))
        b = punto(Mu, (s * (a_z0 - 0.3), -0.05, 1.9))
        c = punto(Ml, (s * (b_z0 - 0.3), 0.0, 1.8))
        d = punto(Ml, (s * (b_z0 - 0.05), 0.0, Z0 - 0.1))
        lamina(out, (d, c, b, a), P['encia'], float(np.linalg.norm(b - a)), float(np.linalg.norm(c - b)), semilla=62)


def gorguera(out, Mh, P, escala=1.0):
    """A y C: la melena de membrana, como la de un lagarto de gorguera: varillas de quitina que
    salen de detras de la cara en abanico (no por debajo de la barbilla), con la punta encendida,
    y entre ellas la membrana en rayas, con una banda de hueso y el borde en sierra."""
    c0 = np.array((0.0, 1.5, -1.9))
    n = 13
    raices, puntas = [], []
    for j in range(n):
        th = (-48.0 + j * 276.0 / (n - 1)) * D
        c, s_ = math.cos(th), math.sin(th)
        raiz = punto(Mh, c0 + np.array((c * 2.3, s_ * 2.2, 0.0)))
        d = _dir(Mh, (c, s_, -0.5))
        d = d / np.linalg.norm(d)
        largo = (4.2 + (0.6 if s_ > 0.5 else 0.0) - (1.0 if s_ < -0.2 else 0.0) + (0.35 if j % 2 == 0 else -0.35)) * escala
        _pua(out, raiz, d, largo, 0.62, P, semilla=70 + j % 5)
        raices.append(raiz)
        puntas.append(raiz + d * largo * 0.86)
    for j in range(n - 1):
        lamina(out, (raices[j], raices[j + 1], puntas[j + 1], puntas[j]), P['gorguera'],
               float(np.linalg.norm(puntas[j + 1] - puntas[j])), float(np.linalg.norm(puntas[j] - raices[j])),
               semilla=80 + j % 5)


def corona_de_puas(out, Mh, P):
    """B: en vez de gorguera, una corona de puas gruesas en dos cercos, sin membrana."""
    c0 = np.array((0.0, 1.5, -1.9))
    for anillo, (n, r, largo, grueso, atras, desfase) in enumerate(((15, 2.3, 4.6, 0.7, 0.5, 0.0), (12, 1.9, 3.0, 0.6, 0.2, 0.5))):
        for j in range(n):
            th = (-50.0 + (j + desfase) * 280.0 / (n - 1)) * D
            c, s_ = math.cos(th), math.sin(th)
            if s_ < -0.8:
                continue
            raiz = punto(Mh, c0 + np.array((c * r, s_ * r, 0.3 * anillo)))
            d = _dir(Mh, (c, s_, -atras))
            l = largo + (0.6 if s_ > 0.5 else 0.0) - (0.9 if s_ < -0.2 else 0.0) + (0.4 if j % 2 == 0 else -0.3)
            _pua(out, raiz, d, l, grueso, P, semilla=70 + (j + anillo) % 5)


# ----------------------------------------------------------------------
#  Lo de cada tipo
# ----------------------------------------------------------------------
def _pano(out, raiz, a, b, pintor, semilla=0):
    raiz, a, b = np.asarray(raiz, float), np.asarray(a, float), np.asarray(b, float)
    lamina(out, (raiz, raiz, b, a), pintor, float(np.linalg.norm(b - a)), float(np.linalg.norm((a + b) / 2 - raiz)), semilla)


def alas(out, P):
    """A: dos pares de alas de avispa que salen de detras de los hombros, alzadas en V y de cara al
    que mira: largas y estrechas, con las venas en celdas y la mancha de la punta encendida; el
    borde de delante lleva una varilla de quitina."""
    for s in (1, -1):
        for j, (raiz, d, largo, ancho) in enumerate((((s * 1.2, 11.0, -0.6), (s * 0.66, 0.72, -0.2), 14.6, 3.0),
                                                     ((s * 1.2, 10.2, -1.6), (s * 0.94, 0.26, -0.25), 11.6, 2.6))):
            raiz = np.array(raiz)
            d = np.array(d)
            d = d / np.linalg.norm(d)
            atras = np.cross(d, np.array((0.0, 0.0, 1.0))) * s          # en el plano de la foto, hacia fuera y abajo
            atras = atras - d * (atras @ d)
            atras = atras / np.linalg.norm(atras) + np.array((0.0, 0.0, -0.18))
            atras = atras / np.linalg.norm(atras)
            P0, P3 = raiz, raiz + d * largo
            lamina(out, (P0, P0 + atras * ancho, P3 + atras * ancho, P3), P['ala'], ancho, largo, semilla=90 + j + 4 * (s > 0))
            viga(out, raiz, raiz + d * largo * 0.93, 0.36, 0.36, P['quitina'], extra=0.1, semilla=96 + j)
        bloque(out, vr.T(s * 1.3, 10.7, -1.0), 1.6, 1.6, 1.8, P['quitina'], semilla=98)                  # el encaje


COLA = [(0.0, 6.4, -7.4), (0.0, 10.0, -10.8), (0.0, 15.6, -12.0), (0.0, 21.6, -10.4), (0.0, 26.0, -6.4), (0.0, 27.8, -1.4),
        (0.0, 27.2, 3.2)]


def cola_escorpion(out, P, giro=0.0, escala=1.0, abre=0.0, semilla=100):
    """Una cola de escorpion que sale de las ancas, sube en arco sobre el lomo y apunta el aguijon
    hacia delante, por encima de la cabeza ('giro' la vuelve hacia un lado y 'abre' la separa)."""
    base = np.array(COLA[0])
    R = vr.Ry(giro * D)
    pts_c = []
    for p in COLA:
        q = (np.array(p) - base) * escala
        q = (R @ np.array((q[0], q[1], q[2], 1.0)))[:3]
        if giro:
            q = q + np.array((math.copysign(abre, giro) * (q[1] / 20.0), 0.0, 0.0))
        pts_c.append(tuple(base + q))
    pts = _cola(out, pts_c, (1.55 * escala, 0.8 * escala), P, semilla=semilla)
    d = pts[-1] - pts[-2]
    _aguijon(out, pts[-1], d, P, semilla=semilla + 50, g=escala)


def lomo_de_puas(out, P):
    """B: el lomo erizado de puas, de las ancas a los hombros, en cuatro filas que se abren hacia
    arriba y atras y crecen hacia la cabeza."""
    a, b = np.array((0.0, 8.4, -6.8)), np.array((0.0, 11.4, -0.4))
    for j in range(8):
        t = j / 7
        p = a + (b - a) * t
        for k, x in enumerate((-1.8, -0.65, 0.65, 1.8)):
            d = np.array((x * 0.35, 0.8, -0.95))
            largo = (2.6 + 1.6 * t) * (1.0 if k in (1, 2) else 0.78)
            _pua(out, p + np.array((x, 0.0, 0.0)), d, largo, 0.5, P, semilla=120 + (j + k) % 7)


def cola_maza(out, P):
    """B: una cola corta que sube y acaba en una maza erizada de puas."""
    pts = _cola(out, [(0.0, 6.4, -7.4), (0.0, 9.4, -10.4), (0.0, 13.2, -11.6), (0.0, 16.6, -10.4)], (1.5, 0.95), P, semilla=140)
    fin = pts[-1]
    bola(out, vr.T(*fin), 1.7, P['quitina'], semilla=150)
    for j in range(14):
        th = j * TAU / 14
        for fi in (-0.6, 0.3, 1.1):
            if j % 2 and fi > 0.5:
                continue
            d = np.array((math.cos(th) * math.cos(fi), math.sin(fi), math.sin(th) * math.cos(fi)))
            _pua(out, fin + d * 1.4, d, 1.7, 0.32, P, semilla=152 + j % 5)


# ======================================================================
#  MELENARA
# ======================================================================
ESC_CABEZA = 1.45
ESC_CUERPO = 1.25                 # el cuerpo, mas grande que la cabeza sola pedia: que no parezca un perro
CABEZA = np.array((0.0, 13.2, 5.6))   # donde va la cabeza (en las medidas del cuerpo)
MIRA = (0.0, -0.36, 1.0)              # hacia donde mira: abajo, al jugador


def melenara(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    out = []
    cuerpo_q = []
    ppb = bm.PPB
    bm.PPB = ppb / ESC_CUERPO
    try:
        cuerpo(cuerpo_q, V, P)
        if tipo == 'A':
            alas(cuerpo_q, P)
            cola_escorpion(cuerpo_q, P)
        elif tipo == 'B':
            lomo_de_puas(cuerpo_q, P)
            cola_maza(cuerpo_q, P)
        else:
            cola_escorpion(cuerpo_q, P, semilla=100)
            for g in (-50.0, 50.0):
                cola_escorpion(cuerpo_q, P, giro=g, escala=0.82, abre=3.0, semilla=200 + (g > 0) * 100)
    finally:
        bm.PPB = ppb
    out += qm.transformar(cuerpo_q, np.diag([ESC_CUERPO, ESC_CUERPO, ESC_CUERPO, 1.0]))
    Hc = CABEZA * ESC_CUERPO
    cab = []
    Mh0 = em.marco(np.zeros(3), MIRA)
    ppb = bm.PPB
    bm.PPB = ppb / ESC_CABEZA
    try:
        cabeza(cab, Mh0, V, P)
        if tipo == 'B':
            corona_de_puas(cab, Mh0, P)
        else:
            gorguera(cab, Mh0, P, escala=0.85 if tipo == 'C' else 1.0)
    finally:
        bm.PPB = ppb
    Mpon = vr.T(*Hc) @ np.diag([ESC_CABEZA, ESC_CABEZA, ESC_CABEZA, 1.0])
    out += qm.transformar(cab, Mpon)
    Mh = Mpon @ Mh0
    return out, {'cabeza': Mh, 'boca': punto(Mh, (0.0, -0.5, 2.4))}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

"""
La cabeza y el cuerpo de mujer de las jefas de Atalaya (13-10-2026), compartidos por Vulpina y la
Gorgona. Juan: «a lo que me referia con mas femenino era a su anatomia de su cara, cuerpo y con lo
que le vayas a poner para que sea un boss»; y sobre la cara de Vulpina (una caja con la cara pintada):
«la cara esta rara, la anterior te salio mejor en forma» (la de Hilandra, con craneo, pomulos, nariz y
mandibula de verdad).

La cabeza (se hace sin escala y se pone agrandada): el craneo que se estrecha hacia la nuca, la cara
pintada a doble pixel arriba (cejas, ojos de pupila rasgada y encendidos, marcas), los pomulos y la
nariz en relieve, el labio de arriba con los colmillos y la mandibula abierta con la barbilla en punta;
dentro, la boca encendida de su color. El cuerpo: caderas, cintura estrecha, pecho con el busto,
hombros caidos, cuello largo; brazos finos con manos de garras; piernas largas.
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
from lumara_modelo import _dir
from melenara_modelo import _tronco, _planta, _tapa, _hilera, _sable

TAU = math.tau
D = vr.D2R

DIENTE = bm._r('6a645e', '9a948c', 'c6c0b6', 'e4e0d8', 'faf8f2')


def pintores_dama(V, P, reg):
    """Los pintores de la dama: la piel, la cara pintada (con los ojos y las marcas de cada jefa), los
    labios, los dientes y colmillos, la boca encendida, la lengua y las garras."""
    nuc, neo, hon = V['neon']
    c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)

    def piel(tw, th, cara_, s):
        return _imagen(_bisel(np.full((th, tw), 2)), V['piel']), None
    reg('piel', piel)

    def cara(tw, th, cara_, s):
        """La cara, pintada a doble pixel: la piel con la sombra de los lados; las cejas que bajan hacia
        dentro (enfado); los ojos almendrados con la raya de las pestanas, el iris encendido y la pupila
        rasgada, como de fiera; y las marcas de cada una (las de zorra en los carrillos, o las escamas
        de las sienes)."""
        t = np.zeros((th, tw, 4), np.uint8)
        pi = [(*c, 255) for c in V['piel']]
        t[:, :] = pi[3]
        t[:, :1] = pi[2]
        t[:, tw - 1:] = pi[2]
        brillo = np.zeros((th, tw), bool)
        oscuro = (20, 12, 16, 255)
        COL = {'k': oscuro, 'r': (*nm._hex(V['labios'][1]), 255), 'w': (236, 230, 222, 255), 'i': (*c_m, 255),
               'n': (*c_n, 255), 'P': (*c_h, 255), 'h': (255, 255, 255, 255), 's': pi[2], 'b': (*V['ceja'], 255),
               'e': (*V['escama'][0], 255), 'E': (*V['escama'][1], 255), 'm': (*nm._hex(V['labios'][1]), 255),
               'M': (*c_n, 255)}
        BRILLA = set('inhM')

        def sprite(filas, x0, y0, espejo=False):
            for fy, fila in enumerate(filas):
                ancho = len(fila)
                for fx, ch in enumerate(fila):
                    if ch == '.':
                        continue
                    x = x0 + (ancho - 1 - fx if espejo else fx)
                    y = y0 + fy
                    if 0 <= x < tw and 0 <= y < th:
                        t[y, x] = COL[ch]
                        if ch in BRILLA:
                            brillo[y, x] = True
        if V['ojos'] == 'zorro':
            OJO = ("rrkk........",
                   "..kkkkkkkk..",
                   "..kwiiPinwk.",
                   "...kiiPihk..",
                   "....ksPsk...",
                   "............")
        else:
            OJO = (".kk.........",
                   "..kkkkkkkk..",
                   "..kiiiPiink.",
                   "...kiiPihk..",
                   "....kkPkk...",
                   "............")
        CEJA = ("bbb.......",
                "...bbbb...",
                ".......bb.")
        ye = int(round(th * 0.5))
        ancho_ojo = len(OJO[0])
        sep = max(2, int(round(tw * 0.07)))
        xl = tw // 2 - sep - ancho_ojo + 2
        xr = tw - xl - ancho_ojo
        sprite(OJO, xl, ye)
        sprite(OJO, xr, ye, espejo=True)
        sprite(CEJA, xl + 1, ye - 4)
        sprite(CEJA, xr + 1, ye - 4, espejo=True)
        if V.get('marcas') == 'zorro':                              # las marcas rojas de zorra
            for j, fy in enumerate((0.66, 0.71, 0.76)):
                y = int(round(th * fy))
                for dx in range(4 - (j == 1)):
                    for x in (1 + dx, tw - 2 - dx):
                        if 0 <= y - (dx // 2) < th:
                            t[y - (dx // 2) * (1 if j != 1 else 0), x] = COL['m']
            sprite(("..M..", ".MnM.", ".MnM.", "..M.."), tw // 2 - 2, int(round(th * 0.22)))
        elif V.get('marcas') == 'escamas':                          # las escamas de las sienes y los carrillos
            for y in range(int(round(th * 0.3)), int(round(th * 0.8))):
                for x in range(0, 6):
                    lado = (x + (y // 2)) % 3
                    if (y % 2 == 0 and lado == 0) and x < 6 - (y - th * 0.3) / (th * 0.5) * 3:
                        for xx in (x, tw - 1 - x):
                            t[y, xx] = COL['e']
                            if y + 1 < th:
                                t[y + 1, xx] = COL['E']
        return t, _emis(t, brillo, 245)
    reg('cara', cara)

    def cuenca(tw, th, cara_, s):
        """La banda de los ojos: la piel en sombra (hundida)."""
        return _imagen(np.full((th, tw), 1), V['piel']), None
    reg('cuenca', cuenca)

    def pestana(tw, th, cara_, s):
        """El parpado con las pestanas, la ceja y el rabillo: casi negro, con un brillo arriba."""
        idx = np.full((th, tw), 0)
        if th >= 2:
            idx[0, :] = 1
        return _imagen(idx, ((14, 8, 12), (34, 22, 28), (60, 40, 48), (90, 64, 72), (120, 90, 100))), None
    reg('pestana', pestana)

    def ojo3d(tw, th, cara_, s):
        """El ojo encendido (en su bloque, a triple pixel): el iris de su color, mas claro en el centro,
        con la pupila rasgada oscura en medio y un brillo blanco arriba."""
        t = qm._emisivo(nuc, neo, max(3, tw), max(3, th)).copy()
        th_, tw_ = t.shape[:2]
        cx = tw_ // 2
        t[:, cx] = (*c_h, 255)
        if th_ >= 4:
            t[0, :] = (*qm._mezcla(c_h, c_m, 0.4), 255)
        if tw_ >= 5:
            t[1 if th_ > 2 else 0, cx + 2] = (255, 255, 255, 255)
        return t, _emis(t, np.ones((th_, tw_), bool), 245)
    reg('ojo3d', ojo3d, pleno=False)

    def carrillo(tw, th, cara_, s):
        """El frente de los carrillos: la piel y las marcas de cada una (las de zorra o las escamas)."""
        t = _imagen(np.full((th, tw), 2), V['piel'])
        if V.get('marcas') == 'zorro':                              # tres rayas finas en cada carrillo
            rojo = (*nm._hex(V['labios'][1]), 255)
            for j, fy in enumerate((0.22, 0.36, 0.5)):
                y0 = int(round(th * fy))
                largo = max(3, tw // 8) - (1 if j == 1 else 0)
                for dx in range(largo):
                    y = y0 + (dx // 2 if j == 2 else (-(dx // 2) if j == 0 else 0))
                    for x in (1 + dx, tw - 2 - dx):
                        if 0 <= y < th:
                            t[y, x] = rojo
        elif V.get('marcas') == 'escamas':                          # escamas pequenas a los lados
            for y in range(0, int(th * 0.75)):
                for x in range(0, max(3, tw // 7)):
                    if (x + (y // 2)) % 3 == 0 and y % 2 == 0:
                        for xx in (x, tw - 1 - x):
                            t[y, xx] = (*V['escama'][0], 255)
                            if y + 1 < th:
                                t[y + 1, xx] = (*V['escama'][1], 255)
        return t, None
    reg('carrillo', carrillo)

    def labio(tw, th, cara_, s):
        idx = np.full((th, tw), 1)
        if th >= 2:
            idx[0, :] = 0
        lab = [nm._hex(c) for c in V['labios']]
        rampa = [lab[0], lab[0], lab[1], lab[2], lab[2]]
        return _imagen(idx, rampa), None
    reg('labio', labio)

    def encia(tw, th, cara_, s):
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = qm._mezcla(c_h, (6, 4, 6), 0.55)
        t[..., 3] = 255
        return t, None
    reg('encia', encia)

    def fauces(tw, th, cara_, s):
        """Por dentro de la boca: hondo junto a los dientes y cada vez mas claro hacia la garganta."""
        t = np.zeros((th, tw, 4), np.uint8)
        for y in range(th):
            f = y / max(th - 1, 1)
            c = c_n if f > 0.84 else (qm._mezcla(c_m, c_n, 0.45) if f > 0.62 else (c_m if f > 0.38 else
                                                                                 (qm._mezcla(c_h, c_m, 0.5) if f > 0.18 else c_h)))
            t[y, :] = (*c, 255)
        return t, _emis(t, np.ones((th, tw), bool), 215)
    reg('fauces', fauces)

    def garganta(tw, th, cara_, s):
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot((xs - cx) / max(tw / 2, 1), (ys - cy) / max(th / 2, 1))
        col = np.where((r < 0.35)[..., None], np.array(c_n),
                       np.where((r < 0.7)[..., None], np.array(c_m), np.array(c_h)))
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, r < 0.7, 235)
    reg('garganta', garganta)

    def _hojas(tw, th, colgando):
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTE]
        n = max(1, (tw + 1) // 4)
        x0 = (tw - (n * 4 - 1)) // 2
        for i in range(n):
            x = x0 + i * 4
            largo = th if i % 2 == 0 else max(2, int(round(th * 0.7)))
            for k_ in range(largo):
                y = k_ if colgando else th - 1 - k_
                f = k_ / max(largo - 1, 1)
                pix = ((x + 1, c[4]),) if f > 0.6 else ((x, c[2]), (x + 1, c[4]), (x + 2, c[1]))
                for xx, col in pix:
                    if 0 <= xx < tw:
                        t[y, xx] = col
        return t, None

    def dientes_arriba(tw, th, cara_, s):
        return _hojas(tw, th, True)
    reg('dientes_arriba', dientes_arriba)

    def dientes_abajo(tw, th, cara_, s):
        return _hojas(tw, th, False)
    reg('dientes_abajo', dientes_abajo)

    def colmillo(tw, th, cara_, s):
        """Un colmillo largo dibujado en una hoja: ancho en la raiz (arriba) y en punta."""
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in DIENTE]
        for y in range(th):
            f = y / max(th - 1, 1)
            ancho = max(1.0, tw * 0.9 * (1 - f) ** 0.8)
            x0 = int(round((tw - ancho) / 2))
            x1 = max(x0, int(round((tw + ancho) / 2)) - 1)
            for x in range(max(x0, 0), min(x1 + 1, tw)):
                t[y, x] = c[4] if x - x0 < max(1, (x1 - x0) * 0.6) else c[2]
        return t, None
    reg('colmillo', colmillo)

    def colmillo3d(tw, th, cara_, s):
        """Las barras de colmillo de la cara: hueso claro con el canto y la sombra."""
        idx = np.full((th, tw), 3)
        return _imagen(_bisel(idx), DIENTE), None
    reg('colmillo3d', colmillo3d)

    def lengua(tw, th, cara_, s):
        """La lengua: el color de los labios, oscuro, con el surco en medio."""
        lab = [nm._hex(c) for c in V['labios']]
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = lab[1]
        t[..., 3] = 255
        if tw >= 4:
            t[:, tw // 2 - 1:tw // 2 + 1, :3] = lab[0]
        return t, None
    reg('lengua', lengua)

    def garra(tw, th, cara_, s):
        """Las garras: negras y lustrosas, con el canto claro."""
        idx = np.full((th, tw), 1)
        if tw >= th and th >= 2:
            idx[0, :] = 3
        elif tw >= 2:
            idx[:, 0] = 3
        return _imagen(idx, V['garra']), None
    reg('garra', garra)


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
def seg(out, p0, p1, r0, r1, pintor, semilla=0, achata=1.0, arriba=None):
    """Un tramo que se afina, de p0 (medio lado r0) a p1 (r1)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    if L < 1e-4:
        return
    M = em.marco(p0, p1 - p0) if arriba is None else em.marco(p0, p1 - p0, up=arriba)
    todo = {'arriba': pintor, 'abajo': pintor, 'lados': pintor, 'frente': pintor, 'atras': pintor}
    _tronco(out, M, -r0 * 0.25, L + r1 * 0.25, (-r0, r0, -r0 * achata, r0 * achata), (-r1, r1, -r1 * achata, r1 * achata),
            todo, semilla=semilla)


def vertical(out, y0, y1, abajo, arriba, pintores, z=0.0, x=0.0, semilla=0):
    """Un tronco que sube de y0 a y1 con su seccion abajo y arriba: (medio ancho, medio fondo)."""
    Mv = vr.T(x, 0, z) @ vr.Rx(-90 * D)
    (ax, az), (bx, bz) = abajo, arriba
    _tronco(out, Mv, y0, y1, (-ax, ax, -az, az), (-bx, bx, -bz, bz), pintores, semilla=semilla)


def todo(p):
    return {'arriba': p, 'abajo': p, 'lados': p, 'frente': p, 'atras': p}


def curva(ctrl, n=60):
    c, _ = em.catmull([np.asarray(p, float) for p in ctrl], n)
    return [np.asarray(p, float) for p in c]


def tubo(out, pts, radios, pintores_por_tramo, semilla=0, arriba=(0.0, 0.0, 1.0)):
    """Un tubo a lo largo de pts que se afina segun radios, de seccion de ocho lados (dos troncos
    cruzados, uno girado 45 grados y algo menor)."""
    for j in range(len(pts) - 1):
        p0, p1 = pts[j], pts[j + 1]
        d = p1 - p0
        L = float(np.linalg.norm(d))
        if L < 1e-4:
            continue
        up = np.asarray(arriba, float)
        M = em.marco(p0, d, up=up) if abs(d @ up) < 0.9 * L * np.linalg.norm(up) else em.marco(p0, d)
        r0, r1 = radios[j], radios[j + 1]
        pin = pintores_por_tramo[j]
        tt = todo(pin)
        for giro, k_ in ((0.0, 1.0), (45.0, 0.84)):
            Mg = M @ vr.Rz(giro * D)
            _tronco(out, Mg, -0.05, L + 0.05, (-r0 * k_, r0 * k_, -r0 * k_, r0 * k_), (-r1 * k_, r1 * k_, -r1 * k_, r1 * k_), tt,
                    semilla=semilla + j % 4)


def a_lo_largo(ctrl, n, perfil, n_curva=80):
    """Los n+1 puntos repartidos por la curva y el radio de cada uno segun el perfil ((t, r), ...)."""
    c = curva(ctrl, n_curva)
    L = [0.0]
    for a, b in zip(c, c[1:]):
        L.append(L[-1] + float(np.linalg.norm(b - a)))
    total = L[-1]
    ts = [j / n for j in range(n + 1)]
    pts = [c[min(int(np.searchsorted(L, t * total)), len(c) - 1)] for t in ts]
    rs = [float(np.interp(t, [a for a, _ in perfil], [b for _, b in perfil])) for t in ts]
    return pts, rs, ts


# ----------------------------------------------------------------------
#  La cabeza (sin escala)
# ----------------------------------------------------------------------
def cara_esculpida(out, Mh, P, barras=True):
    """La cara esculpida en bloques con la forma y el tamano de la de Amuna (el cartel de Mitologias
    RPG que mando Juan): el craneo ancho; la frente; la banda de los ojos hundida y en sombra; el ceno de
    dos bloques gruesos e inclinados que sobresale y hace sombra, con la ceja; los ojos encendidos de pupila
    rasgada metidos en su cuenca oscura; la nariz grande de bloque (puente y punta ancha, con las aletas);
    los pomulos marcados; y a los lados de la boca, cuatro barras de colmillo que bajan hasta pasar la
    barbilla, con su escalon (como la mascara de Amuna)."""
    piel = P['piel']
    _tronco(out, Mh, -2.0, 0.88, (-1.15, 1.15, 0.95, 3.2), (-1.32, 1.32, 0.7, 3.42),
            {'arriba': piel, 'abajo': piel, 'lados': piel, 'atras': piel}, semilla=1)                       # el craneo
    cubo(out, Mh, -1.32, 2.42, 0.86, 2.64, 1.0, 0.14, piel, semilla=2)                                 # la frente
    cubo(out, Mh, -1.32, 1.82, 0.86, 2.64, 0.6, 0.06, P['cuenca'], semilla=3)                           # la banda de los ojos
    cubo(out, Mh, -1.32, 0.7, 0.86, 2.64, 1.12, 0.17, piel, caras={'frente': None}, semilla=4)         # los carrillos
    ppb = bm.PPB
    bm.PPB = ppb * 2
    try:
        cubo(out, Mh, -1.32, 0.7, 1.03, 2.64, 1.12, 0.0, None, caras={'frente': P['carrillo']}, semilla=4)
    finally:
        bm.PPB = ppb
    for s in (1, -1):
        Mo = Mh @ vr.T(s * 0.64, 2.1, 0.92) @ vr.Rz(s * 8 * D)
        cubo(out, Mo, -0.48, -0.25, -0.005, 0.96, 0.5, 0.02, P['pestana'], semilla=5)                   # la cuenca oscura
        bm.PPB = ppb * 3
        try:
            cubo(out, Mo, -0.38, -0.14, 0.015, 0.76, 0.28, 0.03, None, caras={'frente': P['ojo3d']}, semilla=5)   # el ojo
        finally:
            bm.PPB = ppb
        Mw = Mo @ vr.T(s * 0.44, 0.16, 0.0) @ vr.Rz(s * 28 * D)
        cubo(out, Mw, 0.0 if s > 0 else -0.3, -0.05, -0.01, 0.3, 0.1, 0.09, P['pestana'], semilla=7)       # el rabillo
        Mb = Mh @ vr.T(s * 0.62, 2.54, 0.92) @ vr.Rz(s * 16 * D)
        cubo(out, Mb, -0.64, -0.17, 0.0, 1.28, 0.34, 0.3, piel, semilla=9)                                # el ceno, grueso
        cubo(out, Mb, -0.6, 0.02, 0.3, 1.2, 0.1, 0.02, P['pestana'], semilla=10)                          # la ceja
        Mp = Mh @ vr.T(s * 0.9, 1.6, 1.02) @ vr.Rz(s * 12 * D)
        cubo(out, Mp, -0.4, -0.14, 0.0, 0.8, 0.28, 0.16, piel, semilla=11)                                # el pomulo
        if barras:                                                                                        # las barras de colmillo
            for k, (x, y1, y0) in enumerate(((0.62, 1.3, -0.5), (0.98, 1.4, -0.25))):
                xx = s * x
                cubo(out, Mh, xx - 0.09, y0 + 0.3, 1.04, 0.18, y1 - y0 - 0.3, 0.16, P['colmillo3d'], semilla=12 + k)
                cubo(out, Mh, xx - 0.06 + s * 0.02, y0, 1.06, 0.12, 0.32, 0.12, P['colmillo3d'], semilla=14 + k)
    cubo(out, Mh, -0.18, 1.38, 0.88, 0.36, 1.12, 0.24, piel, semilla=16)                                # el puente de la nariz
    _tronco(out, Mh @ vr.T(0, 1.3, 1.02), 0.0, 0.42, (-0.26, 0.26, 0.0, 0.38), (-0.22, 0.22, 0.03, 0.22), todo(piel), semilla=17)
    cubo(out, Mh, -0.2, 1.28, 1.32, 0.4, 0.06, 0.1, P['cuenca'], semilla=18)                            # las aletas


def cabeza_dama(out, Mh, P, abre=14.0, colmillos=0.55, lengua=0.0, colmillos_abajo=0.0):
    """La cabeza de mujer: el craneo, la cara pintada a doble pixel, los pomulos, la nariz fina, el
    labio de arriba con los dientes finos y los dos colmillos, y la mandibula abierta 'abre' grados con
    la barbilla en punta y el labio de abajo; dentro, la boca encendida. 'lengua' > 0 saca la lengua
    bifida (serpiente); 'colmillos_abajo' > 0 pone dos colmillos que suben de la mandibula (jabali)."""
    cara_esculpida(out, Mh, P)
    # la de arriba: el labio, los dientes finos y los colmillos; el paladar encendido
    Mu = Mh @ vr.T(0, 0.75, -0.45)
    Z0, ZD = 0.35, 1.3
    _tronco(out, Mu, -0.3, ZD, (-1.0, 1.0, 0.0, 0.62), (-0.7, 0.7, 0.0, 0.5),
            {'lados': P['piel'], 'frente': P['piel'], 'abajo': P['encia']}, semilla=5)
    cubo(out, Mu, -0.52, -0.03, ZD - 0.06, 1.04, 0.14, 0.12, P['labio'], semilla=6)                       # el labio
    _tapa(out, Mu, -0.04, 1.7, 1.15, Z0, ZD - 0.1, P['fauces'], semilla=7)
    _hilera(out, Mu, _planta(0.82, 0.55, Z0, ZD - 0.1, 0.25), -0.04, -0.22, P['dientes_arriba'], semilla=8)
    if colmillos > 0:
        for s in (1, -1):
            raiz = punto(Mu, (s * 0.44, -0.04, ZD - 0.2))
            _sable(out, raiz, _dir(Mu, (0.0, -1.0, 0.05)), _dir(Mu, (1, 0, 0)), _dir(Mu, (0, 0, 1)), colmillos, 0.16,
                   P['colmillo'], semilla=9 + (s > 0))
    # la de abajo, abierta, con la barbilla en punta
    Ml = Mh @ vr.T(0, 0.7, -0.45) @ vr.Rx(abre * D)
    _tronco(out, Ml, -0.3, 1.3, (-0.95, 0.95, -0.55, 0.0), (-0.3, 0.3, -0.42, 0.0),
            {'lados': P['piel'], 'frente': P['piel'], 'abajo': P['piel'], 'arriba': P['encia']}, semilla=11)
    _tapa(out, Ml, 0.04, 1.6, 0.6, Z0, 1.2, P['fauces'], semilla=12)
    _hilera(out, Ml, _planta(0.78, 0.3, Z0, 1.18, 0.2), 0.04, 0.18, P['dientes_abajo'], semilla=13)
    cubo(out, Ml, -0.32, -0.02, 1.14, 0.64, 0.12, 0.12, P['labio'], semilla=14)                          # el labio de abajo
    if colmillos_abajo > 0:                                                                              # colmillos de jabali
        for s in (1, -1):
            raiz = punto(Ml, (s * 0.62, 0.04, 0.95))
            _sable(out, raiz, _dir(Ml, (s * 0.25, 1.0, 0.25)), _dir(Ml, (1, 0, 0)), _dir(Ml, (0, 0, 1)), colmillos_abajo, 0.24,
                   P['colmillo'], semilla=15 + (s > 0))
    q0, q1 = punto(Ml, (-0.72, 0.04, Z0)), punto(Ml, (0.72, 0.04, Z0))
    q2, q3 = punto(Mu, (0.82, -0.04, Z0)), punto(Mu, (-0.82, -0.04, Z0))
    lamina(out, (q0, q1, q2, q3), P['garganta'], 1.64, float(np.linalg.norm(q3 - q0)), semilla=17)        # la garganta
    for s in (1, -1):                                                                                   # las comisuras
        a, b = punto(Mu, (s * 0.86, -0.02, Z0 - 0.1)), punto(Mu, (s * 0.76, -0.02, 0.95))
        c, d = punto(Ml, (s * 0.62, 0.0, 0.9)), punto(Ml, (s * 0.8, 0.0, Z0 - 0.1))
        lamina(out, (d, c, b, a), P['encia'], float(np.linalg.norm(b - a)), float(np.linalg.norm(c - b)), semilla=18)
    if lengua > 0:                                                                                      # la lengua bifida
        p = punto(Ml, (0.0, 0.1, 0.5))
        q = punto(Ml, (0.0, 0.18, 1.3 + lengua * 0.6))
        seg(out, p, q, 0.16, 0.12, P['lengua'], semilla=19, achata=0.4, arriba=_dir(Ml, (0, 1, 0)))
        for s in (1, -1):
            e = q + _dir(Ml, (s * 0.35, 0.05, 1.0)) * lengua * 0.5
            seg(out, q, e, 0.1, 0.03, P['lengua'], semilla=20, achata=0.5, arriba=_dir(Ml, (0, 1, 0)))
    return {'coronilla': punto(Mh, (0.0, 3.42, -0.5)), 'nuca': punto(Mh, (0.0, 2.0, -2.0))}


# ----------------------------------------------------------------------
#  El cuerpo de mujer (en bloques de mundo)
# ----------------------------------------------------------------------
def torso_dama(out, P, ropa):
    """El torso, de las caderas al cuello, con las proporciones de Amuna: las caderas anchas, la
    cintura estrecha, el pecho ancho, el BUSTO GRANDE en dos bloques que sobresalen mucho, los hombros
    anchos y el cuello grueso; 'ropa' dice el pintor de cada parte ('caderas', 'cintura', 'pecho', 'busto',
    'hombros', 'cuello'); lo que no se diga, de piel."""
    g = lambda k: ropa.get(k, P['piel'])
    vertical(out, 11.2, 14.0, (2.85, 1.8), (2.35, 1.5), todo(g('caderas')), semilla=40)
    vertical(out, 13.9, 16.2, (2.3, 1.48), (1.75, 1.25), todo(g('cintura')), semilla=41)
    vertical(out, 16.1, 17.2, (1.75, 1.25), (2.05, 1.32), todo(g('cintura')), semilla=42)
    vertical(out, 17.1, 19.8, (2.05, 1.32), (2.75, 1.42), todo(g('pecho')), semilla=43)
    for s in (1, -1):
        bloque(out, vr.T(s * 1.06, 18.4, 1.95), 2.06, 2.15, 1.75, g('busto'), semilla=44)
    vertical(out, 19.7, 20.8, (2.75, 1.4), (3.2, 1.15), todo(g('hombros')), semilla=45)
    seg(out, np.array((0.0, 20.5, 0.15)), np.array((0.0, 22.0, 0.35)), 0.72, 0.66, g('cuello'), semilla=46)
    return {'hombro': {s: np.array((s * 3.25, 20.1, 0.0)) for s in (1, -1)}, 'cuello': np.array((0.0, 22.0, 0.35)),
            'caderas': np.array((0.0, 12.6, 0.0))}


def brazo_dama(out, P, hombro, codo, muneca, palma, pintor=None, semilla=0, garras=1.0, abre=1.0):
    """El brazo grueso, como los de Amuna (el brazo y el antebrazo casi tan gruesos como medio ancho de la
    cara), y la mano grande de bloques: la palma, cuatro dedos gordos que acaban en garras negras y el
    pulgar; 'palma' es hacia donde mira la palma."""
    pin = pintor or P['piel']
    hombro, codo, muneca = (np.asarray(v, float) for v in (hombro, codo, muneca))
    seg(out, hombro, codo, 1.08, 0.95, pin, semilla=semilla)
    bola(out, vr.T(*codo), 0.98, pin, semilla=semilla + 1)
    seg(out, codo, muneca, 0.98, 0.86, pin, semilla=semilla + 2)
    d = muneca - codo
    d = d / np.linalg.norm(d)
    M = em.marco(muneca, d, up=palma)
    seg(out, punto(M, (0, 0, -0.2)), punto(M, (0, 0, 1.45)), 0.8, 0.86, P['piel'], semilla=semilla + 3, achata=0.55,
        arriba=_dir(M, (0, 1, 0)))
    for j in range(4):
        f = (j - 1.5) / 1.5
        b = punto(M, (f * 0.6, 0.1, 1.4))
        q = b + _dir(M, (f * 0.25 * abre, 0.35, 1.0)) * (0.95 - 0.12 * abs(f))
        seg(out, b, q, 0.21, 0.19, P['piel'], semilla=semilla + 4)
        e = q + _dir(M, (f * 0.2 * abre, 0.75, 1.0)) * 0.7 * garras
        seg(out, q, e, 0.17, 0.05, P['garra'], semilla=semilla + 5)
    lado = -1.0 if (np.cross(d, palma) @ np.array((0, 0, 1))) > 0 else 1.0
    b = punto(M, (lado * 0.72, 0.1, 0.45))
    e = b + _dir(M, (lado * 0.55, 0.5, 0.75)) * 0.8
    seg(out, b, e, 0.22, 0.17, P['piel'], semilla=semilla + 6)
    seg(out, e, e + _dir(M, (lado * 0.2, 0.8, 0.7)) * 0.45 * garras, 0.15, 0.04, P['garra'], semilla=semilla + 7)


def piernas_dama(out, P, pintor_muslo, pintor_pierna, pintor_pie, adelante=1):
    """Las piernas largas de mujer: el muslo, la rodilla, la pantorrilla, el tobillo fino y el pie;
    carga el peso en una y adelanta la otra rodilla."""
    for s in (1, -1):
        cad = np.array((s * 1.25, 12.8, 0.0))
        if s == adelante:
            rod, tob = np.array((s * 1.5, 7.3, 0.85)), np.array((s * 1.35, 1.25, 0.35))
        else:
            rod, tob = np.array((s * 1.15, 7.2, 0.1)), np.array((s * 1.05, 1.25, -0.05))
        m = cad + (rod - cad) * 0.45
        seg(out, cad, m, 1.4, 1.2, pintor_muslo, semilla=1)
        seg(out, m, rod, 1.2, 0.9, pintor_muslo, semilla=2)
        seg(out, rod, tob, 0.95, 0.6, pintor_pierna, semilla=3)
        pie = tob + np.array((s * 0.1, -0.85, 1.25))
        seg(out, tob, pie, 0.42, 0.3, pintor_pie, semilla=4, achata=0.7)


def huevo(out, M, rx, ry, rz, pintor, semilla=0):
    """Un huevo de pixeles: cinco cajas cruzadas a escalones (se lee redondo desde cualquier lado)."""
    for a, b, c in ((1.0, 0.55, 0.82), (0.92, 0.76, 0.9), (0.76, 0.92, 0.95), (0.52, 1.0, 0.78), (0.66, 0.66, 1.0)):
        cubo(out, M, -rx * a, -ry * b, -rz * c, 2 * rx * a, 2 * ry * b, 2 * rz * c, pintor, semilla=semilla)


# ----------------------------------------------------------------------
#  Piezas del traje en 3D (Juan: «todo no debe ser texturas», como Amuna)
# ----------------------------------------------------------------------
def placa(out, M, w, h, d, base, borde, semilla=0, rim=0.16, alto_rim=0.09):
    """Una placa con el borde en relieve: la placa (centrada en x e y del marco M, de z=0 a z=d) y, encima,
    el marco de cuatro listones algo mas altos, como las hombreras de Amuna."""
    cubo(out, M, -w / 2, -h / 2, 0.0, w, h, d, base, semilla=semilla)
    for (x0, y0, ww, hh) in ((-w / 2, -h / 2, w, rim), (-w / 2, h / 2 - rim, w, rim), (-w / 2, -h / 2, rim, h),
                             (w / 2 - rim, -h / 2, rim, h)):
        cubo(out, M, x0, y0, d, ww, hh, alto_rim, borde, semilla=semilla + 1)


def cuentas(out, pts, r, pintor, semilla=0):
    """Una sarta de cuentas (cubos), una en cada punto."""
    for p in pts:
        p = np.asarray(p, float)
        cubo(out, vr.T(*p), -r, -r, -r, 2 * r, 2 * r, 2 * r, pintor, semilla=semilla)


def gema(out, p, r, pintor_gema, pintor_engaste, normal=(0.0, 0.0, 1.0), semilla=0):
    """Una gema encendida en su engaste: el engaste de metal y la piedra que brilla encima."""
    M = em.marco(np.asarray(p, float), normal)
    cubo(out, M, -r * 1.35, -r * 1.35, 0.0, r * 2.7, r * 2.7, r * 0.5, pintor_engaste, semilla=semilla)
    cubo(out, M @ vr.Rz(45 * D), -r * 0.75, -r * 0.75, r * 0.5, r * 1.5, r * 1.5, r * 0.6, pintor_gema, semilla=semilla + 1)

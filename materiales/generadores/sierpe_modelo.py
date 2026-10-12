"""
Boceto de un solo jefe en tres tipos (12-10-2026). Juan, tras las Fauces: «esta vez
ninguno me gusto; esta bien que crees las texturas pero tienen que verse limpias,
texturas increibles como Ofidia y Espinara; los modelos no estan al nivel de Espinara
y Ofidia o de las cuatro Guaridas; creame una sola entidad con 3 tipos, asi tengo
opciones y veo cual me gusta o se acerca a Ofidia».

  Simara, la Sierpe de las Simas: sale de una sima, alzada como una columna de
  tambores cenidos por cinturones, con una cabeza de fauces enormes y dientes en peine
  y, al fondo de la garganta, un remolino que gira. La misma sierpe en tres tipos:

    A  Abisal      escamas con fotoforos, aletas en abanico, barbillones con un bulbo
                   de luz; remolino de agua; neon cian
    B  Volcanica   placas de obsidiana con grietas de magma, corona de cuernos,
                   latigos de lava; remolino de magma; neon naranja
    C  Espectral   vertebras de hueso con manchas de alma, astas de hueso, mortaja de
                   jirones, cadenas con farolillos; remolino de almas; neon magenta

Texturas limpias, como las de Ofidia: a 8 px por bloque, manchas grandes con su borde,
escamas, placas y remaches dibujados, sin ruido ni motas sueltas.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import cubo, viga, pua, punto, _imagen, _emis

TAU = math.tau
D = vr.D2R
_r = bm._r
bm.PPB = 8


# ----------------------------------------------------------------------
#  Utilidades de pixel: lo que deja la textura limpia
# ----------------------------------------------------------------------
def _borde_de(m):
    """Los pixeles de fuera que tocan la mascara por alguno de sus cuatro lados."""
    b = np.zeros_like(m)
    b[1:, :] |= m[:-1, :]
    b[:-1, :] |= m[1:, :]
    b[:, 1:] |= m[:, :-1]
    b[:, :-1] |= m[:, 1:]
    return b & ~m


def _limpiar(idx, veces=2):
    """Quita los pixeles sueltos: si los cuatro vecinos coinciden, el del centro se iguala."""
    th, tw = idx.shape
    if th < 3 or tw < 3:
        return idx
    out = idx.copy()
    for _ in range(veces):
        a, b, c, d = out[:-2, 1:-1], out[2:, 1:-1], out[1:-1, :-2], out[1:-1, 2:]
        igual = (a == b) & (b == c) & (c == d)
        centro = out[1:-1, 1:-1]
        centro[igual] = a[igual]
    return out


def _manchas(tw, th, s, celda=6.0, umbral=0.58, alto=0.77):
    """Manchas grandes y limpias como el marmol de Ofidia: fondo 2, mancha 3, centro 4 y
    el borde de la mancha en 1."""
    v = bm._ruido(tw, th, s, celda)
    idx = np.where(v > alto, 4, np.where(v > umbral, 3, 2))
    idx = _limpiar(idx)
    idx[_borde_de(idx >= 3)] = 1
    return idx


def _bisel(idx, luz=1, sombra=1):
    """El canto de la cara: un pixel claro arriba y a la izquierda, oscuro abajo y a la derecha."""
    idx = idx.copy()
    th, tw = idx.shape
    if th >= 3 and tw >= 3:
        idx[0, :] += luz
        idx[:, 0] += luz
        idx[-1, :] -= sombra
        idx[:, -1] -= sombra
    return np.clip(idx, 0, 4)


def _escamas(W, H, sw=6, sh=4):
    """Escamas imbricadas en U (de W x H), cada una con su canto oscuro y su brillo."""
    R = sw * 0.62
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    ys += 0.5
    xs += 0.5
    idx = np.full((H, W), 2)
    hecho = np.zeros((H, W), bool)
    for r in range(-1, H // sh + 3):
        cy = r * sh
        off = (sw / 2.0) * (r % 2)
        cx = np.round((xs - off) / sw) * sw + off
        dx, dy = xs - cx, ys - cy
        d = np.hypot(dx, dy * 1.1) / R
        m = (d < 1.0) & ~hecho
        t = np.where(d > 0.8, 1, np.where(d < 0.5, 3, 2))
        t = np.where((dx < -0.2) & (dy > -0.3) & (d > 0.25) & (d < 0.62), 4, t)
        idx[m] = t[m]
        hecho |= m
    return idx


def _escamas_cara(tw, th, cara):
    """Las escamas orientadas para que la punta de cada una mire a la cola."""
    if cara in ('der', 'izq'):
        idx = _escamas(th, tw).T
        return idx if cara == 'der' else idx[:, ::-1]
    idx = _escamas(tw, th)
    return idx[::-1, :] if cara == 'arriba' else idx


def _escudos(tw, th, alto=4):
    """Los escudos del vientre: bandas de lado a lado con su canto claro y su junta."""
    ys = np.arange(th)[:, None] * np.ones((1, tw), int)
    v = ys % alto
    idx = np.where(v == 0, 3, np.where(v == alto - 1, 1, 2))
    if tw >= 3:
        idx[:, 0] = 1
        idx[:, -1] = 1
    return idx


def _remaches(idx, cara, paso=4):
    """Remaches cuadrados de 2 x 2 (claro arriba a la izquierda) en fila por el medio de un cinturon."""
    th, tw = idx.shape
    idx = idx.copy()
    if cara in ('der', 'izq'):                 # el cinturon corre de arriba abajo
        x = max(0, tw // 2 - 1)
        for y in range(1, th - 2, paso):
            idx[y, x] = 4
            if x + 1 < tw:
                idx[y, x + 1] = 3
                idx[y + 1, x + 1] = 1
            idx[y + 1, x] = 3
    else:                                      # corre de izquierda a derecha
        y = max(0, th // 2 - 1)
        for x in range(1, tw - 2, paso):
            idx[y, x] = 4
            idx[y, x + 1] = 3
            if y + 1 < th:
                idx[y + 1, x] = 3
                idx[y + 1, x + 1] = 1
    return idx


def _degradado(th, tw, filas_a_luz, c_nucleo, c_neon, c_hondo, estrias=True):
    """El interior de las fauces: escalones de luz (blanco, neon, hondo) y estrias del paladar."""
    nuc, neo, hon = nm._hex(c_nucleo), nm._hex(c_neon), nm._hex(c_hondo)
    t = np.zeros((th, tw, 4), np.uint8)
    for y in range(th):
        k = y / max(th - 1, 1)
        k = k if filas_a_luz else 1 - k              # 1 = hacia la garganta
        if k > 0.82:
            c = nuc
        elif k > 0.6:
            c = qm._mezcla(neo, nuc, 0.45)
        elif k > 0.3:
            c = neo
        else:
            c = qm._mezcla(hon, neo, 0.55)
        t[y, :] = (*c, 255)
        if estrias and y % 3 == 2 and k < 0.82:
            t[y, :] = (*qm._mezcla(hon, neo, 0.3), 255)
    if tw >= 3:
        t[:, 0] = (*hon, 255)
        t[:, -1] = (*hon, 255)
    return t


# ----------------------------------------------------------------------
#  Los tres tipos
# ----------------------------------------------------------------------
TIPOS = {
    'A': dict(
        clave='A', nombre='Abisal',
        piel=_r('050c18', '0b1d33', '123352', '1e5276', '4a8cb2'),
        vientre=_r('122a33', '1f4a54', '346e78', '5c9ca2', '9ccccc'),
        cinto=_r('16121a', '332630', '5e4650', '96787a', 'd2b8ae'),
        diente=_r('4a5a62', '8ea2aa', 'c4d6da', 'e4f0f0', 'f8ffff'),
        aleta=_r('04141e', '0a2c3c', '125068', '22788e', '58b8cc'),
        neon=('f2ffff', '52e2ff', '0a5a7c'),
        foto='9af4ff',
    ),
    'B': dict(
        clave='B', nombre='Volcanica',
        piel=_r('060408', '100a10', '1c121a', '2c1e2a', '44303e'),
        vientre=_r('100a0a', '1e1414', '2e2020', '423030', '5c4442'),
        cinto=_r('0c0c0e', '1c1a1c', '302c30', '4a4448', '6e6468'),
        diente=_r('3a2c26', '6e5a50', 'a89080', 'd4c0ae', 'f2e6d8'),
        cuerno=_r('060408', '120c12', '22161e', '362630', '54404c'),
        neon=('fff4cc', 'ff9a1a', '8a2206'),
        grieta=('ffe08a', 'ff7a14'),
    ),
    'C': dict(
        clave='C', nombre='Espectral',
        piel=_r('3c3450', '625a7a', '8e86a8', 'bab2d0', 'e2def0'),
        vientre=_r('2a2436', '423a52', '5e566e', '80789a', 'a49cbc'),
        cinto=_r('1c120a', '3a2614', '5e4222', '86643a', 'b48e56'),
        diente=_r('5a5468', '9890a8', 'cbc4d8', 'e8e4f0', 'faf8ff'),
        tela=_r('08060e', '120c1c', '1e142c', '2c1e3e', '423058'),
        hierro=_r('0c0a10', '1c1820', '2e2834', '48404e', '6a6072'),
        neon=('fff0fc', 'ff4ad2', '6a0a52'),
        alma='c88aff',
    ),
}


def pintores(T):
    """Los pintores de un tipo, cada uno con su nombre (la cache de bestias_modelo va por nombre)."""
    k = T['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'sim%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = T['neon']

    # ---------------- la piel del cuerpo ----------------
    if k == 'A':
        def cuerpo(tw, th, cara, s):
            idx = _escamas_cara(tw, th, cara)
            tex = _imagen(idx, T['piel'])
            if cara in ('der', 'izq') and th >= 6 and tw >= 4:
                m = np.zeros((th, tw), bool)
                fila = int(th * 0.6)
                for x in range(2, tw - 2, 6):
                    m[fila:fila + 2, x:x + 2] = True
                tex[m] = (*nm._hex(T['foto']), 255)
                tex[_borde_de(m) & (np.indices((th, tw))[0] >= fila)] = (*T['piel'][1], 255)
                return tex, _emis(tex, m, 235)
            return tex, None
    elif k == 'B':
        def cuerpo(tw, th, cara, s):
            """Obsidiana: dos tonos en manchas grandes y, por encima, vetas de magma que siguen las
            curvas de nivel de un campo suave (lineas limpias que serpentean, no chispas)."""
            base = _manchas(tw, th, s, celda=7.0, umbral=0.6, alto=0.95)
            idx = np.array([1, 1, 2, 3, 3])[base]
            v = bm._ruido(tw, th, s + 11, 9.0)
            veta = np.abs(v - 0.5) < 0.035
            veta = _limpiar(veta.astype(int), 1).astype(bool)
            tex = _imagen(idx, T['piel'])
            if veta.any():
                c1, c2 = nm._hex(T['grieta'][0]), nm._hex(T['grieta'][1])
                orilla = _borde_de(veta)
                tex[orilla] = (*qm._mezcla(T['piel'][1], c2, 0.4), 255)
                tex[veta] = (*c2, 255)
                nucleo = veta & (np.abs(v - 0.5) < 0.012)
                tex[nucleo] = (*c1, 255)
                return tex, _emis(tex, veta, 235)
            return tex, None
    else:
        def cuerpo(tw, th, cara, s):
            idx = _manchas(tw, th, s, celda=6.5, umbral=0.6, alto=0.8)
            idx = np.array([3, 2, 3, 1, 0])[idx]          # hueso claro, borde medio, mancha oscura, centro de alma
            tex = _imagen(idx, T['piel'])
            alma = idx <= 1
            if alma.any():
                c = nm._hex(T['alma'])
                tex[idx == 0] = (*c, 255)
                tex[idx == 1] = (*qm._mezcla(T['piel'][1], c, 0.45), 255)
                return tex, _emis(tex, idx == 0, 120)
            return tex, None
    reg('cuerpo', cuerpo)

    def vientre(tw, th, cara, s):
        return _imagen(_escudos(tw, th), T['vientre']), None
    reg('vientre', vientre)

    def cinto(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if cara in ('der', 'izq'):
            idx[:, 0] = 3
            idx[:, -1] = 1
        else:
            idx[0, :] = 3
            idx[-1, :] = 1
        return _imagen(_remaches(idx, cara), T['cinto']), None
    reg('cinto', cinto)

    def diente(tw, th, cara, s):
        idx = np.full((th, tw), 3)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 2
        if th >= 3:
            idx[-1, :] = 2
        return _imagen(idx, T['diente']), None
    reg('diente', diente)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def remolino(tw, th, cara, s):
        """El remolino de la garganta: una espiral limpia, blanca en el centro, y lo de fuera de
        la circunferencia, transparente."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        a = np.arctan2(ys - cy, xs - cx)
        banda = (np.floor((a / TAU + r * 1.6) * 4) % 2) == 0
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        dentro = r < 1.0
        col = np.where(banda[..., None], np.array(c_m), np.array(qm._mezcla(c_h, c_m, 0.35)))
        col = np.where((r < 0.28)[..., None], np.array(c_n), col)
        col = np.where(((r > 0.86) & dentro)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = np.where(dentro, 255, 0)
        return t, _emis(t, dentro & (r < 0.86), 240)
    reg('remolino', remolino)

    def ojo(tw, th, cara, s):
        t = qm._emisivo(nuc, neo, max(2, tw), max(2, th))
        th2, tw2 = t.shape[:2]
        if tw2 >= 3:
            t[:, tw2 // 2] = (*nm._hex(hon), 255)
        return t, None
    reg('ojo', ojo, pleno=True)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)

    def fosa(tw, th, cara, s):
        return _imagen(np.zeros((th, tw), int), T['piel']), None
    reg('fosa', fosa)

    # ---------------- lo propio de cada tipo ----------------
    if k == 'A':
        def membrana(tw, th, cara, s):
            """Aleta: bandas de la raiz (abajo) a la punta (arriba), radios cada 3 pixeles y el
            borde de arriba en festones; lo de fuera, transparente."""
            t = np.zeros((th, tw, 4), np.uint8)
            ys, xs = np.mgrid[0:th, 0:tw]
            k_ = 1 - ys / max(th - 1, 1)                    # 1 arriba (la punta)
            idx = np.where(k_ > 0.66, 3, np.where(k_ > 0.33, 2, 1))
            radios = (xs % 3) == 1
            idx = np.where(radios, np.minimum(idx + 1, 4), idx)
            festo = 1 + (np.abs(np.sin((xs + 0.5) * math.pi / 3.0)) * 2).astype(int)
            fuera = ys < festo
            img = _imagen(idx, T['aleta'])
            t[~fuera] = img[~fuera]
            canto = (~fuera) & (ys <= festo)
            t[canto] = (*nm._hex(T['foto']), 255)
            return t, _emis(t, canto, 160)
        reg('membrana', membrana)

        def espina(tw, th, cara, s):
            return _imagen(_bisel(np.full((th, tw), 2)), T['aleta']), None
        reg('espina', espina)

    if k == 'B':
        def cuerno(tw, th, cara, s):
            idx = np.full((th, tw), 2)
            if cara in ('der', 'izq', 'frente', 'atras') and tw >= 3:
                idx[:, 1] = 3
            return _imagen(_bisel(idx), T['cuerno']), None
        reg('cuerno', cuerno)

        def magma(tw, th, cara, s):
            t = qm._emisivo(T['grieta'][0], T['grieta'][1], max(2, tw), max(2, th))
            return t, None
        reg('magma', magma, pleno=True)

        def costra(tw, th, cara, s):
            idx = np.full((th, tw), 1)
            if th >= 3:
                idx[0, :] = 2
            return _imagen(idx, T['cuerno']), None
        reg('costra', costra)

    if k == 'C':
        def tela(tw, th, cara, s):
            """Jirones: pliegues de tres pixeles con su cresta clara y el borde de abajo deshecho."""
            t = np.zeros((th, tw, 4), np.uint8)
            ys, xs = np.mgrid[0:th, 0:tw]
            idx = np.where(((xs // 3) % 2) == 0, 2, 1)
            idx = np.where((xs % 6) == 0, 3, idx)
            fin = th - 1 - ((xs * 7 + s) % 4) - ((xs // 3) % 2) * 2
            idx = np.where(ys > fin - 2, 0, idx)
            img = _imagen(idx, T['tela'])
            dentro = ys <= fin
            t[dentro] = img[dentro]
            return t, None
        reg('tela', tela)

        def hierro(tw, th, cara, s):
            return _imagen(_bisel(np.full((th, tw), 2)), T['hierro']), None
        reg('hierro', hierro)

        def hueso(tw, th, cara, s):
            idx = np.full((th, tw), 3)
            ys = np.arange(th)[:, None] * np.ones((1, tw), int)
            idx = np.where(ys % 5 == 4, 2, idx)
            return _imagen(_bisel(idx), T['piel']), None
        reg('hueso', hueso)
    return P


# ----------------------------------------------------------------------
#  Ayudas de forma
# ----------------------------------------------------------------------
def lamina(out, P4, pintor, ancho, alto, semilla=0):
    """Un cuadrilatero cualquiera (p0 abajo-izq, p1 abajo-der, p2 arriba-der, p3 arriba-izq) con
    una textura pintada a su medida."""
    mat = bm._material(pintor, 'frente', ancho, alto, semilla)
    P = [np.asarray(p, float) for p in P4]
    out.append(([P[3], P[2], P[1], P[0]], [(0, 0), (1, 0), (1, 1), (0, 1)], mat))


def bola(out, M, r, pintor, semilla=0):
    """Una esfera de pixel: tres cajas cruzadas."""
    for w, h in ((r, r * 0.55), (r * 0.78, r * 0.78), (r * 0.55, r)):
        cubo(out, M, -w, -h, -w, 2 * w, 2 * h, 2 * w, pintor, semilla=semilla)
    cubo(out, M, -r * 0.55, -r * 0.55, -r, r * 1.1, r * 1.1, 2 * r, pintor, semilla=semilla)


def cadena(out, p0, p1, eslabon, pintor, semilla=0):
    """Una cadena de p0 a p1: eslabones alternos (uno de canto y otro de plano)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    n = max(1, int(L / (eslabon * 0.8)))
    M = em.marco(p0, p1 - p0)
    for i in range(n):
        Mi = M @ vr.T(0, 0, i * L / n) @ vr.Rz((90 if i % 2 else 0) * D)
        g = eslabon * 0.22
        cubo(out, Mi, -eslabon * 0.32, -g / 2, 0, g, g, eslabon, pintor, semilla=semilla)
        cubo(out, Mi, eslabon * 0.32 - g, -g / 2, 0, g, g, eslabon, pintor, semilla=semilla)
        cubo(out, Mi, -eslabon * 0.32, -g / 2, 0, eslabon * 0.64, g, g, pintor, semilla=semilla)
        cubo(out, Mi, -eslabon * 0.32, -g / 2, eslabon - g, eslabon * 0.64, g, g, pintor, semilla=semilla)


# ----------------------------------------------------------------------
#  El cuerpo: tambores sobre una curva, con el lomo siempre hacia el mismo lado
# ----------------------------------------------------------------------
CAMINO = [(-2.0, -7.0, -9.0), (-2.6, 0.0, -8.0), (-1.4, 5.5, -7.0), (1.4, 9.8, -5.2), (2.4, 13.2, -2.4),
          (1.2, 15.4, 0.4), (0.2, 15.9, 2.6), (0.0, 15.7, 4.2)]


def _por_longitud(ctrl, paso):
    pts, _ = em.catmull(ctrl, 600)
    pts = [np.asarray(p, float) for p in pts]
    L = [0.0]
    for a, b in zip(pts, pts[1:]):
        L.append(L[-1] + float(np.linalg.norm(b - a)))
    n = max(2, int(round(L[-1] / paso)))
    out = []
    for k in range(n + 1):
        s = k * L[-1] / n
        i = min(int(np.searchsorted(L, s)), len(pts) - 1)
        if i == 0:
            out.append(pts[0])
            continue
        f = (s - L[i - 1]) / max(L[i] - L[i - 1], 1e-9)
        out.append(pts[i - 1] + (pts[i] - pts[i - 1]) * f)
    return out


def _marcos(pts, arriba0):
    """Marcos que viajan por la curva sin girar (el lomo sigue al lomo)."""
    M = []
    up = np.asarray(arriba0, float)
    for i in range(len(pts) - 1):
        t = pts[i + 1] - pts[i]
        t = t / np.linalg.norm(t)
        up = up - t * (up @ t)
        up = up / np.linalg.norm(up)
        x = np.cross(up, t)
        m = np.eye(4)
        m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, up, t, pts[i]
        M.append(m)
    return M


def radio(t):
    """El grueso a lo largo del cuerpo (t: 0 bajo tierra, 1 en el cuello)."""
    return 2.15 + 0.35 * math.sin(math.pi * min(1.0, t * 1.3)) - 0.62 * t


def simara(tipo='A', abre=40.0, semilla=1):
    T = TIPOS[tipo]
    P = pintores(T)
    rng = random.Random(semilla)
    out = []
    pts = _por_longitud(CAMINO, 3.1)
    marcos = _marcos(pts, (0, 0, -1))
    n = len(marcos)
    for i, M in enumerate(marcos):
        t = i / max(n - 1, 1)
        r = radio(t)
        L = float(np.linalg.norm(pts[i + 1] - pts[i]))
        cubo(out, M, -r, -r, -0.15, 2 * r, 2 * r, L + 0.3, P['cuerpo'], semilla=i)
        cubo(out, M, -r * 0.56, -r - 0.14, -0.15, r * 1.12, 0.3, L + 0.3, P['vientre'], semilla=i)       # la franja de escudos del vientre
        rb = r * 1.12
        cubo(out, M @ vr.T(0, 0, -0.28), -rb, -rb, 0, 2 * rb, 2 * rb, 0.56, P['cinto'], semilla=i)
        _lomo(out, M, r, L, t, i, T, P, rng)
    # la cabeza, al final del cuello, mirando al frente
    fin = pts[-1]
    Mh = em.marco(fin + np.array((0, -0.05, 1.3)), (0, -0.12, 1.0))
    cabeza(out, Mh, T, P, abre, rng)
    return out, {'cabeza': Mh}


def _lomo(out, M, r, L, t, i, T, P, rng):
    """Lo que lleva cada tambor en el lomo y en los costados, segun el tipo."""
    k = T['clave']
    if k == 'A':
        alto = 1.0 + 1.1 * math.sin(math.pi * min(1.0, 0.15 + t))
        Mt = M @ vr.T(0, r, L * 0.15) @ vr.Rx(-12 * D)
        cubo(out, Mt, -0.07, -0.1, 0, 0.14, alto, L * 0.8, None, caras={'der': P['membrana'], 'izq': P['membrana']}, semilla=i)
        cubo(out, Mt, -0.12, -0.1, 0, 0.24, 0.3, 0.24, P['espina'], semilla=i)
    elif k == 'B':
        for j, z in enumerate((0.25, 0.7)):
            h = (0.9 + 0.8 * math.sin(math.pi * min(1.0, 0.1 + t))) * (1.0 if j == 0 else 0.7)
            Mt = M @ vr.T(0, r - 0.1, L * z) @ vr.Rx(-30 * D)
            pua(out, Mt, 0.26 + 0.1 * (j == 0), h, P['cuerno'], semilla=i + j)
    else:
        Mt = M @ vr.T(0, r - 0.1, L * 0.3) @ vr.Rx(-28 * D)
        cubo(out, Mt, -0.14, 0, -0.35, 0.28, 0.9 + 0.7 * math.sin(math.pi * min(1.0, 0.1 + t)), 0.7, P['hueso'], semilla=i)
        if i % 2 == 0 and 0.15 < t < 0.9:
            for s in (1, -1):
                Ms = M @ vr.T(s * r * 1.13, r * 0.4, -0.1) @ vr.Ry(s * 90 * D)
                largo = 1.6 + (i % 3) * 0.5
                cubo(out, Ms @ vr.Rx(180 * D), -0.45, 0, -0.03, 0.9, largo, 0.06, None, caras={'frente': P['tela'], 'atras': P['tela']},
                     semilla=i)


# ----------------------------------------------------------------------
#  La cabeza: la misma en los tres tipos, con su corona y sus barbillones
# ----------------------------------------------------------------------
def cabeza(out, Mh, T, P, abre, rng):
    k = T['clave']
    # el craneo, la ceja y el hocico en dos tramos que afinan
    cubo(out, Mh, -1.7, -0.8, -2.0, 3.4, 2.4, 3.4, P['cuerpo'], caras={'abajo': P['vientre']}, semilla=1)
    cubo(out, Mh @ vr.T(0, 1.2, -0.2) @ vr.Rx(10 * D), -1.85, 0, 0, 3.7, 0.6, 2.0, P['cinto'], semilla=2)
    cubo(out, Mh, -1.4, -0.7, 1.3, 2.8, 1.85, 1.85, P['cuerpo'], caras={'abajo': P['fauces']}, semilla=3)
    Ms2 = Mh @ vr.T(0, 0, 3.05) @ vr.Rx(4 * D)
    cubo(out, Ms2, -1.1, -0.65, 0, 2.2, 1.5, 1.6, P['cuerpo'], caras={'abajo': P['fauces']}, semilla=4)
    for s in (1, -1):                                          # las fosas de la nariz
        cubo(out, Ms2, s * 0.5 - 0.17, 0.62, 1.35, 0.34, 0.2, 0.2, P['fosa'], semilla=5)
    for s in (1, -1):                                          # las placas de las mejillas
        x0 = 1.68 if s > 0 else -1.98
        cubo(out, Mh, x0, -0.75, -1.7, 0.3, 1.1, 2.1, P['cinto'], semilla=44)
    cubo(out, Mh, -0.45, 1.1, 1.3, 0.9, 0.28, 1.85, P['cinto'], semilla=45)       # la cresta del hocico
    cubo(out, Ms2, -0.35, 0.83, 0, 0.7, 0.24, 1.4, P['cinto'], semilla=46)
    # los ojos: dos por lado, debajo de la ceja
    for s in (1, -1):
        x0 = 1.7 if s > 0 else -1.76
        cubo(out, Mh, x0, 0.55, 0.55, 0.06, 0.42, 0.62, P['ojo'], semilla=6)
        cubo(out, Mh, x0, 0.08, 0.05, 0.06, 0.3, 0.42, P['ojo'], semilla=7)
    # los dientes de arriba, en peine, y los colmillos delante
    for s in (1, -1):
        for j in range(5):
            z = 1.5 + j * 0.36
            pua(out, Mh @ vr.T(s * 1.22, -0.7, z) @ vr.Rx(180 * D), 0.1, 0.95 + 0.25 * (j % 2), P['diente'], semilla=8 + j)
        for j in range(4):
            z = 0.2 + j * 0.38
            pua(out, Ms2 @ vr.T(s * 0.92, -0.65, z) @ vr.Rx(180 * D), 0.1, 0.9 + 0.2 * (j % 2), P['diente'], semilla=13 + j)
    for j in range(6):
        x = -0.75 + j * 0.3
        largo = 1.75 if j in (0, 5) else 1.0 + 0.25 * (j % 2)
        pua(out, Ms2 @ vr.T(x, -0.65, 1.45) @ vr.Rx(180 * D), 0.1 if j not in (0, 5) else 0.14, largo, P['diente'], semilla=17 + j)
    # la mandibula, abierta, con su peine de dientes
    Mj = Mh @ vr.T(0, -0.8, -1.5) @ vr.Rx(abre * D)
    cubo(out, Mj, -1.5, -0.95, 0, 3.0, 0.95, 3.6, P['cuerpo'], caras={'arriba': P['fauces'], 'abajo': P['vientre']}, semilla=23)
    Mj2 = Mj @ vr.T(0, 0, 3.55) @ vr.Rx(-8 * D)
    cubo(out, Mj2, -1.15, -0.85, 0, 2.3, 0.85, 2.6, P['cuerpo'], caras={'arriba': P['fauces'], 'abajo': P['vientre']}, semilla=24)
    for s in (1, -1):
        for j in range(8):
            pua(out, Mj @ vr.T(s * 1.32, 0, 0.55 + j * 0.38), 0.1, 0.8 + 0.2 * (j % 2), P['diente'], semilla=25 + j)
        for j in range(5):
            pua(out, Mj2 @ vr.T(s * 0.98, 0, 0.3 + j * 0.42), 0.1, 0.8 + 0.18 * (j % 2), P['diente'], semilla=33 + j)
    for j in range(5):
        x = -0.7 + j * 0.35
        largo = 1.5 if j in (0, 4) else 0.85
        pua(out, Mj2 @ vr.T(x, 0, 2.45), 0.13 if j in (0, 4) else 0.1, largo, P['diente'], semilla=38 + j)
    # al fondo de la garganta, el remolino
    Mv = Mh @ vr.T(0, -1.35, 0.9) @ vr.Rx(abre * 0.5 * D)
    cubo(out, Mv, -1.05, -1.05, 0, 2.1, 2.1, 0.05, None, caras={'frente': P['remolino']}, semilla=43)
    # lo de cada tipo
    if k == 'A':
        _corona_abisal(out, Mh, Mj, T, P)
    elif k == 'B':
        _corona_volcanica(out, Mh, Mj, T, P)
    else:
        _corona_espectral(out, Mh, Mj, T, P)


def _abanico(out, base, dirs, largos, P, semilla=0):
    """Un abanico de espinas con la membrana entre una y otra."""
    puntas = []
    for d, L in zip(dirs, largos):
        d = np.asarray(d, float)
        d = d / np.linalg.norm(d)
        fin = base + d * L
        viga(out, base, fin, 0.16, 0.16, P['espina'], semilla=semilla)
        puntas.append(fin)
    for a, b in zip(puntas, puntas[1:]):
        lamina(out, (base, base, b, a), P['membrana'], float(np.linalg.norm(b - a)), float(np.linalg.norm(a - base)), semilla)


def _corona_abisal(out, Mh, Mj, T, P):
    # el abanico de la nuca: siete espinas hacia atras y arriba, con su membrana
    base = punto(Mh, (0, 1.4, -1.3))
    dirs, largos = [], []
    for j in range(7):
        phi = math.radians(-66 + j * 22)
        dirs.append(punto(Mh, (math.sin(phi) * 0.9, math.cos(phi) * 0.75, -0.75)) - punto(Mh, (0, 0, 0)))
        largos.append(3.6 - abs(j - 3) * 0.35)
    _abanico(out, base, dirs, largos, P, semilla=1)
    # dos abanicos pequenos a los lados del cuello, como agallas
    for s in (1, -1):
        base = punto(Mh, (s * 1.6, 0.0, -1.6))
        dirs = [punto(Mh, (s * 1.0, 0.6 - j * 0.45, -0.8)) - punto(Mh, (0, 0, 0)) for j in range(4)]
        _abanico(out, base, dirs, (2.0, 2.3, 2.2, 1.8), P, semilla=2)
    # los barbillones de la barbilla, con su bulbo de luz
    for s in (1, -1):
        p = punto(Mj, (s * 0.85, -0.95, 2.6))
        for j, (d, g) in enumerate((((0, -1.0, 0.3), 0.2), ((0, -0.9, 0.6), 0.17), ((0, -0.35, 0.95), 0.14), ((0, 0.2, 0.8), 0.12))):
            q = p + np.array(d) * 1.05
            viga(out, p, q, g, g, P['espina'], semilla=3 + j)
            p = q
        bola(out, vr.T(*p), 0.42, P['luz'], semilla=7)


def _corona_volcanica(out, Mh, Mj, T, P):
    # los dos cuernos grandes, que salen de la ceja y se echan atras
    for s in (1, -1):
        p = punto(Mh, (s * 1.35, 1.75, 0.3))
        for j, (d, g) in enumerate((((s * 0.55, 1.0, -0.8), 0.72), ((s * 0.35, 0.8, -1.1), 0.56), ((s * 0.1, 0.45, -1.2), 0.42),
                                    ((0.0, 0.1, -1.0), 0.28))):
            q = p + (punto(Mh, d) - punto(Mh, (0, 0, 0))) * 1.1
            viga(out, p, q, g, g, P['cuerno'], extra=0.1, semilla=1 + j)
            p = q
        p = punto(Mh, (s * 1.7, 0.7, -0.9))                      # los dos pequenos de debajo
        for j, (d, g) in enumerate((((s * 0.8, 0.3, -0.7), 0.42), ((s * 0.4, 0.2, -0.9), 0.3))):
            q = p + (punto(Mh, d) - punto(Mh, (0, 0, 0))) * 1.0
            viga(out, p, q, g, g, P['cuerno'], extra=0.08, semilla=5 + j)
            p = q
    for j in range(4):                                            # puas por la frente
        pua(out, Mh @ vr.T(0, 1.75, 1.2 - j * 0.85) @ vr.Rx(-35 * D), 0.18, 0.8 - j * 0.1, P['cuerno'], semilla=7)
    # los latigos de lava de la quijada: costra y magma, y una gota encendida al final
    for s in (1, -1):
        p = punto(Mj, (s * 1.4, -0.4, 0.8))
        for j, d in enumerate(((s * 0.3, -1.0, 0.2), (s * 0.2, -1.0, 0.4), (0.0, -0.8, 0.7), (0.0, -0.4, 0.9), (0.0, 0.1, 0.8))):
            q = p + np.array(d) * 0.95
            viga(out, p, q, 0.24 - j * 0.025, 0.24 - j * 0.025, P['magma'] if j % 2 else P['costra'], semilla=8 + j)
            p = q
        bola(out, vr.T(*p), 0.3, P['magma'], semilla=13)


def _corona_espectral(out, Mh, Mj, T, P):
    # las astas de hueso, con sus puntas
    for s in (1, -1):
        p = punto(Mh, (s * 1.25, 1.75, 0.1))
        tramos = (((s * 0.7, 1.2, -0.4), 0.48), ((s * 0.8, 1.1, -0.7), 0.38), ((s * 0.5, 1.1, -0.8), 0.3))
        for j, (d, g) in enumerate(tramos):
            q = p + (punto(Mh, d) - punto(Mh, (0, 0, 0))) * 1.25
            viga(out, p, q, g, g, P['hueso'], extra=0.06, semilla=1 + j)
            punta = q + (punto(Mh, (s * 0.1, 0.9, 0.4)) - punto(Mh, (0, 0, 0))) * (1.2 - j * 0.2)
            viga(out, q, punta, g * 0.6, g * 0.6, P['hueso'], semilla=4 + j)
            p = q
    # la mortaja: tres jirones que caen de la nuca por el cuello
    for j, (x, largo, ancho) in enumerate(((0.0, 5.2, 2.6), (-1.6, 3.8, 1.6), (1.6, 3.8, 1.6))):
        arriba = punto(Mh, (x, 1.25 if x == 0 else 0.9, -1.2))
        Mt = em.marco(arriba, punto(Mh, (x * 0.3, -1.0, -0.55)) - punto(Mh, (0, 0, 0)), up=punto(Mh, (0, 0, -1)) - punto(Mh, (0, 0, 0)))
        Mt = Mt @ vr.Rx(-90 * D)
        cubo(out, Mt, -ancho / 2, -largo, -0.03, ancho, largo, 0.06, None, caras={'frente': P['tela'], 'atras': P['tela']}, semilla=7 + j)
    # las cadenas con sus farolillos de almas, colgando de la quijada
    for s in (1, -1):
        p0 = punto(Mj, (s * 1.45, -0.5, 1.2))
        p1 = p0 + np.array((s * 0.3, -3.2, 0.6))
        cadena(out, p0, p1, 0.42, P['hierro'], semilla=10)
        Mf = vr.T(*(p1 + np.array((0, -0.2, 0))))
        cubo(out, Mf, -0.4, -1.0, -0.4, 0.8, 0.12, 0.8, P['hierro'], semilla=11)
        cubo(out, Mf, -0.4, -0.12, -0.4, 0.8, 0.12, 0.8, P['hierro'], semilla=11)
        for (x, z) in ((-0.35, -0.35), (0.35, -0.35), (-0.35, 0.35), (0.35, 0.35)):
            cubo(out, Mf, x - 0.05, -1.0, z - 0.05, 0.1, 0.9, 0.1, P['hierro'], semilla=12)
        cubo(out, Mf, -0.26, -0.82, -0.26, 0.52, 0.6, 0.52, P['luz'], semilla=13)


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

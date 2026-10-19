"""
Los pintores limpios del bestiario (18-10-2026), para rehacer los mobs del DEDsafío como el Blaze, el Slime, el Trasgo,
el Fogonazo y el Coco (materiales/fichas/COMO_HACEMOS_LOS_MONSTRUOS.md). Como en ellos, se pinta a un texel por píxel
del modelo (16 por bloque, como los mobs de Minecraft): cada material con su paleta de 5 tonos y un dibujo de píxel
limpio (moteado en manchitas de dos píxeles como el del Blaze, bandas, placas, chapa con remaches, escamas en U...),
sin ruido ni motas sueltas.

El modelo del juego (bestiario.py) va a 32 texels por bloque (K = 2 por píxel de modelo): aquí se pinta en la
cuadrícula de 16 por bloque y se agranda 2 veces a vecino más cercano (grueso). Los dientes se pintan a 32 por bloque,
para que la punta salga fina.

  fondos     (de 16 por bloque, para componer) piel16, liso16, placas16, metal16, rayas16, vetas16, carne16,
             boca16, luz16
  pintores   piel, liso, placas, metal, rayas, escamas, manchas, vetas, carne, boca (el paladar en escalones de luz),
             ojo, luz, llama, diente (una hoja blanca en punta, «como hoja bond»), brizna, petalo, cara_creeper
  geometría  colmillo (un diente en dos hojas cruzadas), fila_dientes
"""
import math

import numpy as np

import bestiario as B

F = 2                      # texels del modelo (32 por bloque) por texel del dibujo (16 por bloque)


def H(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), float)


def rampa(*c):
    return np.array([H(x) for x in c])


def juntar(*rs):
    return np.vstack(rs)


def _img(idx, r, alfa=None):
    idx = np.clip(np.asarray(idx), 0, len(r) - 1).astype(int)
    out = np.zeros(idx.shape + (4,), np.uint8)
    out[..., :3] = np.clip(np.round(r[idx]), 0, 255)
    out[..., 3] = 255 if alfa is None else alfa
    return out


def _ajustar(a, th, tw):
    """Recorta o alarga (repitiendo el borde) a th x tw."""
    a = a[:th, :tw]
    if a.shape[0] < th:
        a = np.concatenate([a, np.repeat(a[-1:], th - a.shape[0], 0)], 0)
    if a.shape[1] < tw:
        a = np.concatenate([a, np.repeat(a[:, -1:], tw - a.shape[1], 1)], 1)
    return a


def grueso(nombre, fn16, pleno=False):
    """Un pintor del bestiario a partir de uno de 16 por bloque: fn16(tw, th, cara, s) -> (rgba, brillo o None)."""
    def fn(tw, th, cara, s):
        t16, h16 = max(1, int(round(tw / F))), max(1, int(round(th / F)))
        tex, emis = fn16(t16, h16, cara, s)
        tex = _ajustar(np.repeat(np.repeat(tex, F, 0), F, 1), th, tw)
        if emis is not None:
            emis = _ajustar(np.repeat(np.repeat(emis, F, 0), F, 1), th, tw)
        return tex, emis
    p = B.Pintor(nombre, fn, pleno=pleno)
    p.nativo = F
    return p


def _malla(tw, th):
    ys, xs = np.mgrid[0:th, 0:tw]
    return xs, ys


def _azar(xs, ys, s):
    """Un número fijo de 0 a 1 por cada manchita de dos píxeles (sin motas de un píxel)."""
    gx, gy = xs // 2, ys // 2
    h = (gx * 374761393 + gy * 668265263 + int(s) * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _bisel(idx, cara, luz=1, sombra=1):
    """El canto: la fila de arriba un tono más clara y la de abajo más oscura; arriba, toda más clara (y abajo, más
    oscura)."""
    idx = np.array(idx, copy=True)
    th, tw = idx.shape
    if cara == 'arriba':
        return idx + 1
    if cara == 'abajo':
        return idx - 1
    if th >= 3:
        idx[0, :] += luz
        idx[-1, :] -= sombra
    return idx


def _borde_de(m):
    b = np.zeros_like(m)
    b[1:, :] |= m[:-1, :]
    b[:-1, :] |= m[1:, :]
    b[:, 1:] |= m[:, :-1]
    b[:, :-1] |= m[:, 1:]
    return b & ~m


def _ruido(tw, th, semilla, celda):
    rng = np.random.default_rng(int(semilla) % (2 ** 31))
    gx, gy = int(tw / celda) + 3, int(th / celda) + 3
    g = rng.random((gy, gx))
    xs, ys = np.arange(tw) / celda, np.arange(th) / celda
    x0, y0 = np.floor(xs).astype(int), np.floor(ys).astype(int)
    fx, fy = xs - x0, ys - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = g[np.ix_(y0, x0)], g[np.ix_(y0, x0 + 1)]
    c, d = g[np.ix_(y0 + 1, x0)], g[np.ix_(y0 + 1, x0 + 1)]
    fx, fy = fx[None, :], fy[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def _limpiar(idx, veces=2):
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


# ======================================================================================================================
#  Los fondos (de 16 por bloque): devuelven (rgba, brillo o None) y sirven para componer (la cara va encima)
# ======================================================================================================================
def piel16(r, base=2, claro=0.16, oscuro=0.2, acento=0.0, r_acento=None, brilla_acento=False):
    """La piel moteada, como la de los mobs de Minecraft: el tono base en manchitas de dos píxeles, algunas un tono más
    claras y otras más oscuras, y (si se pide) alguna de otro color (r_acento), que puede brillar."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        a = _azar(xs, ys, s)
        idx = np.full((th, tw), base)
        idx[a < oscuro] = base - 1
        idx[a > 1 - claro] = base + 1
        tex = _img(_bisel(idx, cara), r)
        emis = None
        if acento > 0 and r_acento is not None:
            b = _azar(xs + 1, ys + 1, s * 3 + 7)
            m = (b < acento) & (a >= oscuro)
            ta = _img(np.where(b < acento * 0.4, 3, 2), r_acento)
            tex[m] = ta[m]
            if brilla_acento:
                emis = np.zeros_like(tex)
                emis[m] = tex[m]
        return tex, emis
    return fn


def liso16(r, base=2):
    def fn(tw, th, cara, s):
        return _img(_bisel(np.full((th, tw), base), cara), r), None
    return fn


def placas16(r, alto=4, base=2, vertical=False, moteado=True):
    """Placas en bandas: cada una con su canto claro arriba y su junta oscura abajo, y un moteado suave dentro."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        c = xs if vertical else ys
        idx = np.full((th, tw), base)
        if moteado:
            a = _azar(xs, ys, s)
            idx[a < 0.18] = base - 1
            idx[a > 0.86] = base + 1
        idx[(c % alto) == 0] = base + 1
        idx[(c % alto) == alto - 1] = base - 1
        if cara == 'arriba':
            idx = idx + 1
        return _img(idx, r), None
    return fn


def metal16(r, paso=6, base=2, remaches=True):
    """Chapa: paneles con su junta y un remache de 2 x 2 (claro arriba a la izquierda) en cada esquina."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        idx = np.full((th, tw), base)
        a = _azar(xs, ys, s)
        idx[a < 0.12] = base - 1
        idx[(xs % paso) == 0] = base - 1
        idx[(ys % paso) == 0] = base - 1
        if remaches:
            rx, ry = xs % paso, ys % paso
            idx[(rx == 1) & (ry == 1)] = base + 2
            idx[(rx == 2) & (ry == 1)] = base + 1
            idx[(rx == 1) & (ry == 2)] = base + 1
        return _img(_bisel(idx, cara), r), None
    return fn


def rayas16(r1, r2, ancho=3, gastado=0.0, r_gastado=None):
    """Rayas de peligro en diagonal (dos rampas), con su canto y, si se pide, la pintura saltada en los bordes."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        banda = ((xs + (th - 1 - ys)) // ancho) % 2 == 0
        idx = _bisel(np.full((th, tw), 2), cara)
        a = _azar(xs, ys, s)
        idx = idx - (a < 0.14)
        t1, t2 = _img(idx, r1), _img(idx, r2)
        t1[~banda] = t2[~banda]
        if gastado > 0 and r_gastado is not None:
            borde = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
            m = (borde < 2) & (_azar(xs + 1, ys, s + 5) < gastado)
            t1[m] = _img(np.full((th, tw), 1), r_gastado)[m]
        return t1, None
    return fn


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def piel(nombre, r, **kw):
    return grueso(nombre, piel16(r, **kw))


def liso(nombre, r, base=2):
    return grueso(nombre, liso16(r, base))


def placas(nombre, r, alto=4, base=2, vertical=False, moteado=True):
    return grueso(nombre, placas16(r, alto, base, vertical, moteado))


def metal(nombre, r, paso=6, base=2, remaches=True):
    return grueso(nombre, metal16(r, paso, base, remaches))


def rayas(nombre, r1, r2, ancho=3, gastado=0.0, r_gastado=None):
    return grueso(nombre, rayas16(r1, r2, ancho, gastado, r_gastado))


def manchas(nombre, r, r2, celda=7.0, umbral=0.6, base=2):
    """Manchas grandes de borde limpio (de otra rampa), con su borde un tono más oscuro."""
    def fn(tw, th, cara, s):
        v = _ruido(tw, th, s * 17 + 3, celda)
        m = _limpiar((v > umbral).astype(int)) > 0
        xs, ys = _malla(tw, th)
        a = _azar(xs, ys, s)
        idx = _bisel(np.full((th, tw), base) - (a < 0.15) + (a > 0.88), cara)
        tex = _img(idx, r)
        t2 = _img(np.where(_borde_de(~m) & m, 1, 3 if cara == 'arriba' else 2), r2)
        tex[m] = t2[m]
        return tex, None
    return grueso(nombre, fn)


def vetas16(r, rv, celda=6.0, brilla=True, base=1):
    """Piedra con vetas encendidas como curvas de nivel (magma, venas): fondo oscuro y las líneas de otra rampa."""
    def fn(tw, th, cara, s):
        v = _ruido(tw, th, s * 13 + 1, celda) * 0.75 + _ruido(tw, th, s * 13 + 7, celda / 2.2) * 0.25
        nivel = np.floor(v * 5)
        linea = np.zeros((th, tw), bool)
        linea[:, 1:] |= nivel[:, 1:] != nivel[:, :-1]
        linea[1:, :] |= nivel[1:, :] != nivel[:-1, :]
        xs, ys = _malla(tw, th)
        a = _azar(xs, ys, s)
        idx = _bisel(np.full((th, tw), base) + (nivel % 2 == 0) - (a < 0.12), cara)
        tex = _img(idx, r)
        tl = _img(np.where(_azar(xs, ys, s + 3) < 0.25, 4, 3), rv)
        tex[linea] = tl[linea]
        emis = None
        if brilla:
            emis = np.zeros_like(tex)
            emis[linea] = tex[linea]
        return tex, emis
    return fn


def vetas(nombre, r, rv, celda=6.0, brilla=True, base=1):
    return grueso(nombre, vetas16(r, rv, celda, brilla, base))


def escamas(nombre, r, sw=6, sh=4):
    """Escamas en U imbricadas, con su canto oscuro y su brillo."""
    def fn(tw, th, cara, s):
        Rr = sw * 0.62
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        ys += 0.5
        xs += 0.5
        idx = np.full((th, tw), 2)
        hecho = np.zeros((th, tw), bool)
        for fila in range(-1, th // sh + 3):
            cy = fila * sh
            off = (sw / 2.0) * (fila % 2)
            cx = np.round((xs - off) / sw) * sw + off
            dx, dy = xs - cx, ys - cy
            d = np.hypot(dx, dy * 1.1) / Rr
            m = (d < 1.0) & ~hecho
            t = np.where(d > 0.78, 1, np.where(d < 0.45, 3, 2))
            idx[m] = t[m]
            hecho |= m
        return _img(_bisel(idx, cara, 0, 0), r), None
    return grueso(nombre, fn)


def carne16(r, rv, base=2, venas=0.04, brilla=True):
    """Carne viva: fibras de músculo en bandas finas y venas gruesas (curvas, no motas), encendidas si 'brilla'."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        idx = np.where(((xs + ys // 3) % 3) == 0, base - 1, base)
        idx[((xs + ys // 3) % 3) == 1] = base + 1
        tex = _img(_bisel(idx, cara), r)
        v = _ruido(tw, th, s * 11 + 5, 6.0)
        vena = np.abs(v - 0.5) < venas
        tv = _img(np.full((th, tw), 3), rv)
        tex[vena] = tv[vena]
        if not brilla:
            return tex, None
        emis = np.zeros_like(tex)
        emis[vena] = tex[vena]
        return tex, emis
    return fn


def carne(nombre, r, rv, base=2, venas=0.04, brilla=True, pleno=False):
    return grueso(nombre, carne16(r, rv, base, venas, brilla), pleno=pleno)


def boca16(r, neon):
    """El paladar en escalones de luz: oscuro en el borde, el neón y, al fondo, casi blanco (todo encendido), con unas
    arrugas de través (los surcos del paladar)."""
    neon = H(neon)

    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        idx = np.clip(d, 0, len(r) - 1)
        tex = _img(idx, r)
        centro = d >= max(1, min(tw, th) // 4)
        tex[centro, :3] = neon * 0.8
        medio = d >= max(2, min(tw, th) // 3)
        tex[medio, :3] = neon
        fondo = d >= max(2, min(tw, th) // 2 - 1)
        tex[fondo, :3] = np.minimum(255, neon * 0.4 + 160)
        surco = centro & ((ys % 3) == 0)
        tex[surco, :3] = tex[surco, :3] * 0.72
        emis = tex.copy()
        emis[d < 1] = 0
        return tex, emis
    return fn


def boca(nombre, r, neon):
    return grueso(nombre, boca16(r, neon))


def ojo(nombre, borde, centro, nucleo='ffffff'):
    """Un ojo encendido: el borde del color, el centro y un punto de núcleo casi blanco."""
    rb, rc, rn = H(borde), H(centro), H(nucleo)

    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        tex[..., 3] = 255
        tex[..., :3] = rb
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        tex[d >= 1, :3] = rc
        cx, cy = (tw - 1) // 2, (th - 1) // 2
        tex[cy:cy + 1 + (th > 3), cx:cx + 1 + (tw > 3), :3] = rn
        return tex, tex.copy()
    return grueso(nombre, fn, pleno=True)


def luz16(r):
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        tex = _img(np.clip(1 + d, 1, len(r) - 1), r)
        return tex, tex.copy()
    return fn


def luz(nombre, r):
    """Lo que brilla entero: del borde (el neón) al centro (casi blanco), en escalones."""
    return grueso(nombre, luz16(r), pleno=True)


def llama(nombre, r):
    """La llama en hoja (a 32 por bloque): lenguas que suben desde la base (abajo en la textura), claras por dentro."""
    def fn(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        f = 1 - (ys + 0.5) / th
        u = (xs + 0.5) / tw
        alto = 0.45 + 0.55 * np.abs(np.cos((u - 0.5) * math.pi * 1.6 + s * 0.7)) ** 0.8
        alto = alto * (1.0 - np.abs(u - 0.5) * 1.1)
        dentro = f < alto
        img = np.zeros((th, tw, 4), np.uint8)
        img[dentro] = _img(np.full((th, tw), 2), r)[dentro]
        img[dentro & (f < alto * 0.6) & (np.abs(u - 0.5) < 0.3)] = _img(np.full((th, tw), 3), r)[0, 0]
        img[dentro & (f < alto * 0.3) & (np.abs(u - 0.5) < 0.16)] = _img(np.full((th, tw), 4), r)[0, 0]
        img[dentro & (f > alto - 0.12)] = _img(np.full((th, tw), 1), r)[0, 0]
        img[..., 3] = np.where(dentro, 255, 0)
        return img, img.copy()
    return B.Pintor(nombre, fn, pleno=True)


def diente(nombre, r=None):
    """Un diente en una hoja (a 32 por bloque): un triángulo blanco (la punta, la fila de arriba de la textura), claro
    de un lado y en sombra del otro, con la raíz un tono más oscura."""
    r = r if r is not None else rampa('5a5444', '9a927c', 'd6cfba', 'ece6d6', 'faf6ec')

    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        u = (xs + 0.5) / tw
        v = (ys + 0.5) / th
        dentro = np.abs(u - 0.5) < 0.5 * np.power(v, 0.85) + 0.02
        idx = np.where(u < 0.5, 4, 3)
        idx = np.where(v > 0.86, 2, idx)
        tex = _img(idx, r)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


def brizna(nombre, r):
    """Una brizna (o una hoja larga) en hoja, a 32 por bloque: en punta (la punta, la fila de arriba), con el nervio
    claro en medio, la punta más clara y la raíz en sombra."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        u = (xs + 0.5) / tw
        v = (ys + 0.5) / th
        dentro = np.abs(u - 0.5) < 0.5 * np.power(v, 0.6) + 0.03
        idx = np.where(u < 0.5, 3, 2)
        idx = np.where(np.abs(u - 0.5) < 0.12, 4, idx)
        idx = np.where(v < 0.22, np.minimum(idx + 1, 4), idx)
        idx = np.where(v > 0.88, 1, idx)
        tex = _img(idx, r)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


def petalo(nombre, r, brilla=False):
    """Un pétalo en hoja, a 32 por bloque: estrecho en la base (abajo), ancho en el medio y redondo en la punta (arriba),
    con el nervio y dos venas más oscuras y el borde en sombra."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        u = (xs + 0.5) / tw - 0.5
        v = 1 - (ys + 0.5) / th
        ancho = 0.5 * np.power(np.clip(np.sin(np.clip(v, 0, 1) * math.pi * 0.9 + 0.16), 0, 1), 0.65)
        dentro = np.abs(u) < ancho
        idx = np.full((th, tw), 3)
        idx[np.abs(u) > ancho * 0.72] = 2
        idx[(np.abs(u) < 0.05) | (np.abs(np.abs(u) - v * 0.22) < 0.035)] = 1
        idx[v < 0.12] = 1
        idx[(v > 0.8) & (np.abs(u) < ancho * 0.6)] = 4
        tex = _img(idx, r)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, (tex.copy() if brilla else None)
    return B.Pintor(nombre, fn)


# ======================================================================================================================
#  Los dientes (la geometría)
# ======================================================================================================================
def colmillo(m, parte, base, hacia, largo, ancho, pint, fila=(1.0, 0.0, 0.0), cruz=True):
    """Un diente en hoja desde 'base' hacia 'hacia' (de frente, de cara a lo que se le pone delante); con 'cruz', en dos
    hojas cruzadas, para que también se vea de lado (de canto, una sola hoja desaparece)."""
    base = np.asarray(base, float)
    y = B._u(np.asarray(hacia, float))
    x = np.asarray(fila, float)
    x = B._u(x - y * float(x @ y))
    z = np.cross(x, y)
    caras = {c: (pint if c in ('frente', 'atras') else None) for c in B.CARAS}
    for ex, ez in (((x, z), (z, -x)) if cruz else ((x, z),)):
        M = np.eye(4)
        M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = ex, y, ez, base
        m._caja(parte, M, -ancho / 2, 0.0, 0.0, ancho, largo, 0.0, None, dict(caras))


def fila_dientes(m, parte, a, b, n, largo, hacia, pint, ancho=None, varia=0.22, semilla=0, colmillos=1.4, cruz=True):
    """Una fila de dientes en hoja de a a b, apuntando hacia 'hacia', con largos que varían un poco y los de las
    puntas (los colmillos) más largos."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    paso = (b - a) / max(1, n - 1)
    ancho = ancho or max(1.0, float(np.linalg.norm(b - a)) / max(1, n) * 0.92)
    lado = b - a if np.linalg.norm(b - a) > 1e-6 else np.array((1.0, 0.0, 0.0))
    for i in range(n):
        f = 1.0 + varia * (((i * 7 + semilla) % 3) - 1)
        if i in (0, n - 1):
            f *= colmillos
        colmillo(m, parte, a + paso * i, hacia, largo * f, ancho * (1.12 if i in (0, n - 1) else 1.0), pint,
                 fila=lado, cruz=cruz)


# ======================================================================================================================
#  La cara de creeper
# ======================================================================================================================
CARA_CREEPER = [
    '........',
    '........',
    '.##..##.',
    '.##..##.',
    '...##...',
    '..####..',
    '..####..',
    '..#..#..',
]
_CELDAS = np.array([[ch == '#' for ch in fila] for fila in CARA_CREEPER])


def cara_creeper(nombre, fondo, hueco, ojo_c=None, filas=(0, 8), ojos=True, brillo_boca=None, rasgado=0.8,
                 cicatriz=None):
    """La cara de creeper (la de siempre, en su cuadrícula de 8 x 8) sobre la piel que pinta 'fondo' (un fondo de 16 por
    bloque). Los huecos, de 'hueco' (oscuro). Los ojos, encendidos de 'ojo_c' y rasgados: el ceño les corta la esquina de
    dentro de arriba ('rasgado', cuánto), con el centro claro y la fila de abajo en sombra; sin 'ojos', la piel (y, si
    hay 'cicatriz', una raya cosida de esa rampa donde estarían). La boca, con el fondo encendido de 'brillo_boca'.
    'filas': las filas de la cara que van en esta caja (la cabeza, o la quijada)."""
    oc = H(ojo_c) if ojo_c else None
    bb = H(brillo_boca) if brillo_boca else None

    def fn(tw, th, cara, s):
        tex, emis = fondo(tw, th, cara, s)
        if cara != 'frente':
            return tex, emis
        emis = np.zeros_like(tex) if emis is None else emis.copy()
        f0, f1 = filas
        n = f1 - f0
        xs, ys = _malla(tw, th)
        ci = np.minimum(7, (xs * 8) // tw)
        cj = f0 + np.minimum(n - 1, (ys * n) // th)
        celda = _CELDAS[cj, ci]
        es_ojo = celda & ((cj == 2) | (cj == 3))
        boca = celda & ~es_ojo
        th_ = _img(np.full((th, tw), 1), hueco)
        # La boca: el hueco oscuro, con el borde más oscuro y el fondo encendido.
        if boca.any():
            tex[boca] = th_[boca]
            borde = _borde_de(~boca) & boca
            tex[borde] = _img(np.full((th, tw), 0), hueco)[borde]
            if bb is not None:
                dentro = boca & ~borde
                tex[dentro, :3] = bb * 0.62
                emis[dentro] = tex[dentro]
        if es_ojo.any():
            # El sitio de cada ojo: u de 0 a 1 de fuera a dentro (hacia la nariz) y v de arriba abajo.
            x0 = np.where(ci < 4, np.round(1 * tw / 8), np.round(5 * tw / 8))
            x1 = np.where(ci < 4, np.round(3 * tw / 8), np.round(7 * tw / 8))
            fila2 = np.round((2 - f0) * th / n)
            fila4 = np.round((4 - f0) * th / n)
            u = (xs + 0.5 - x0) / np.maximum(1, x1 - x0)
            u = np.where(ci < 4, u, 1 - u)
            v = (ys + 0.5 - fila2) / np.maximum(1, fila4 - fila2)
            if not ojos:
                tex[es_ojo] = _img(np.full((th, tw), 1), hueco)[es_ojo] if cicatriz is None else tex[es_ojo]
                if cicatriz is not None:
                    raya = es_ojo & (np.abs(v - (0.62 - 0.3 * u)) < 0.16)
                    tex[raya] = _img(np.full((th, tw), 1), cicatriz)[raya]
                    punto = raya & ((xs % 2) == 0) & (np.abs(v - (0.62 - 0.3 * u)) < 0.08)
                    tex[punto] = _img(np.full((th, tw), 3), cicatriz)[punto]
            else:
                tex[es_ojo] = th_[es_ojo]
                corte = v < rasgado * u - 0.04 if rasgado else np.zeros_like(es_ojo)
                lit = es_ojo & ~corte
                if oc is not None:
                    tex[lit, :3] = oc
                    sombra = lit & (v > 0.76)
                    tex[sombra, :3] = oc * 0.55
                    nucleo = lit & (v > 0.3) & (v <= 0.76) & (u > 0.2) & (u < 0.75)
                    tex[nucleo, :3] = np.minimum(255, oc * 0.35 + 175)
                    chispa = lit & (v <= 0.3) & (u < 0.36)
                    tex[chispa, :3] = np.minimum(255, oc * 0.15 + 225)
                    emis[lit] = tex[lit]
        return tex, (emis if np.any(emis[..., 3]) else None)
    return grueso(nombre, fn)


# ======================================================================================================================
#  Lo suave (18-10-2026, Juan: «las texturas que se vean suaves»): el tono corre seguido por la rampa, sin escalones ni
#  motas, más claro arriba (la luz de arriba) y con manchas grandes y blandas
# ======================================================================================================================
def color_continuo(r, v):
    """El color de la rampa 'r' en el punto v (0 .. len - 1), mezclando los dos tonos de al lado."""
    v = np.clip(v, 0, len(r) - 1 - 1e-6)
    i = np.floor(v).astype(int)
    f = (v - i)[..., None]
    return r[i] * (1 - f) + r[np.minimum(i + 1, len(r) - 1)] * f


def _rgba(rgb, alfa=None):
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = np.clip(np.round(rgb), 0, 255)
    out[..., 3] = 255 if alfa is None else alfa
    return out


def tono_suave(tw, th, cara, s, base=2.0, luz=0.7, ruido=0.22, celda=7.0, canto=0.2, franja=(0.0, 1.0)):
    """El valor (posición en la rampa) de cada píxel de una cara: la luz de arriba abajo (en las caras de lado; 'franja',
    la parte del alto de la pieza que es esta caja), la cara de arriba más clara y la de abajo más oscura, y el ruido
    blando por encima."""
    xs, ys = _malla(tw, th)
    if cara == 'arriba':
        v = np.full((th, tw), base + luz * 0.55)
    elif cara == 'abajo':
        v = np.full((th, tw), base - luz * 0.75)
    else:
        f0, f1 = franja
        t = f0 + (ys + 0.5) / th * (f1 - f0)
        v = base + luz * (0.5 - t)
        if f0 == 0.0:
            v[0, :] += canto
    n = _ruido(tw, th, s * 7 + 1, celda) * 0.7 + _ruido(tw, th, s * 7 + 5, celda / 2.0) * 0.3
    return v + (n - 0.5) * 2 * ruido


def suave16(r, base=2.0, luz=0.7, ruido=0.22, celda=7.0, canto=0.2, franja=(0.0, 1.0)):
    """La piel suave (de 16 por bloque, para componer)."""
    def fn(tw, th, cara, s):
        return _rgba(color_continuo(r, tono_suave(tw, th, cara, s, base, luz, ruido, celda, canto, franja))), None
    return fn


def suave(nombre, r, **kw):
    return grueso(nombre, suave16(r, **kw))


def manchas_suaves16(r, r2, cuanto=0.35, celda=5.0, borde=0.08, **kw):
    """La piel suave con manchas blandas de otra rampa (musgo, nata, moho): el borde de la mancha se funde."""
    base = suave16(r, **kw)

    def fn(tw, th, cara, s):
        tex, _ = base(tw, th, cara, s)
        n = _ruido(tw, th, s * 11 + 3, celda)
        a = np.clip((n - (1 - cuanto)) / max(1e-3, borde), 0, 1)[..., None]
        v2 = tono_suave(tw, th, cara, s + 13, kw.get('base', 2.0) + 0.3, kw.get('luz', 0.7), 0.15, celda)
        rgb = tex[..., :3] * (1 - a) + color_continuo(r2, v2) * a
        return _rgba(rgb), None
    return fn


def vetas_suaves16(r, base=2.0, luz=0.6, paso=3.0, onda=0.6, fuerza=0.45, celda=7.0, vertical=True, franja=(0.0, 1.0)):
    """La madera, la corteza o las fibras: vetas blandas a lo largo (claras y oscuras que se funden), que se tuercen."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        v = tono_suave(tw, th, cara, s, base, luz, 0.12, celda, franja=franja)
        if cara not in ('arriba', 'abajo'):
            a, b = (xs, ys) if vertical else (ys, xs)
            n = _ruido(tw, th, s * 5 + 2, celda)
            v = v + np.sin((a + n * onda * paso * 2) / paso * math.pi) * fuerza
        return _rgba(color_continuo(r, v)), None
    return fn


def luz_suave16(r, centro=3.2):
    """Lo que brilla, suave: el borde del color y el centro casi blanco, fundidos (no en escalones)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        u = np.abs((xs + 0.5) / tw - 0.5) * 2
        v = np.abs((ys + 0.5) / th - 0.5) * 2
        d = 1 - np.maximum(u, v)
        tex = _rgba(color_continuo(r, 1.0 + d * centro))
        return tex, tex.copy()
    return fn


def luz_suave(nombre, r, centro=3.2):
    return grueso(nombre, luz_suave16(r, centro), pleno=True)

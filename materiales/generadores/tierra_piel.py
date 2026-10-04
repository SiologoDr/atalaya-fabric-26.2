"""
La piel de Rajang, pintada cara por cara.

En vez de repetir una loseta por todo el cuerpo, cada cara de cada caja recibe
su propia imagen (un texel por pixel de modelo, como el atlas del juego),
pintada segun donde cae esa cara en el cuerpo en reposo. Asi las rosetas, el
lomo oscuro, el vientre claro, el musgo y las grietas siguen al cuerpo entero
y pasan de una caja a otra sin cortes ni repeticiones.

- Mosaico: la piel esta hecha de teselas de jade de 4 pixeles, cada una con
  su tono y su bisel (canto de arriba claro, el de abajo oscuro), y alguna
  esmeralda clara o jade negro suelto: parece tallado en bloques.
- Las rosetas del jaguar se reparten por la superficie (Poisson en 3D):
  anillos rotos con el centro mas hondo y algun punto dentro en el lomo, los
  costados y las ancas; manchas macizas en las patas, la cabeza y el vientre.
- El jade: un tono que cambia despacio, vetas claras de piedra, el lomo mas
  oscuro, los costados bajos mas claros, el grano fino y la sombra de
  contacto donde una pieza toca a otra.
- Fase I: musgo en lo alto del lomo y colgando de los cantos. Fase II: seco.
- Grietas (fases II a IV): una red de fracturas que nace del sol del pecho y
  se extiende con cada fase; por dentro brillan.
- El oro: martillado, con el canto grabado; en las placas grandes, la espiral
  cuadrada de los templos; en las bandas, la greca escalonada. Se mancha con
  la maldicion.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm

_hex = nm._hex

# ----------------------------------------------------------------------
#  Ruido (todo vectorizado sobre puntos (N, 3) en pixeles de modelo)
# ----------------------------------------------------------------------


def _hash(ix, iy, iz, s):
    h = (ix.astype(np.int64) * 73856093) ^ (iy.astype(np.int64) * 19349663) ^ (iz.astype(np.int64) * 83492791) \
        ^ np.int64(s * 2654435761 % (1 << 31))
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return (h & 0xFFFFFF).astype(float) / float(0x1000000)


def ruido(p, escala, semilla=0):
    q = p / escala
    i = np.floor(q).astype(np.int64)
    f = q - i
    u = f * f * (3 - 2 * f)
    acc = np.zeros(len(p))
    for dx in (0, 1):
        wx = u[:, 0] if dx else 1 - u[:, 0]
        for dy in (0, 1):
            wy = u[:, 1] if dy else 1 - u[:, 1]
            for dz in (0, 1):
                wz = u[:, 2] if dz else 1 - u[:, 2]
                acc += wx * wy * wz * _hash(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, semilla)
    return acc


def fbm(p, escala, semilla=0, octavas=3):
    s, a, tot = 0.0, 1.0, 0.0
    for o in range(octavas):
        s = s + a * ruido(p, escala / 2 ** o, semilla + o * 17)
        tot += a
        a *= 0.5
    return s / tot


def grieta_red(p, celda, semilla):
    """Distancia al borde mas cercano de un Voronoi 3D y las dos celdas que lo
    forman (para encender solo algunos tramos)."""
    q = p / celda
    i = np.floor(q).astype(np.int64)
    n = len(p)
    d1 = np.full(n, 1e9); d2 = np.full(n, 1e9)
    f1 = np.zeros((n, 3)); f2 = np.zeros((n, 3))
    id1 = np.zeros(n); id2 = np.zeros(n)
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            for oz in (-1, 0, 1):
                c = i + np.array([ox, oy, oz])
                fp = c + np.stack([_hash(c[:, 0], c[:, 1], c[:, 2], semilla + k) for k in range(3)], 1) * 0.8 + 0.1
                d = np.linalg.norm(q - fp, axis=1)
                cid = _hash(c[:, 0], c[:, 1], c[:, 2], semilla + 7)
                m1 = d < d1
                m2 = ~m1 & (d < d2)
                d2 = np.where(m1, d1, np.where(m2, d, d2))
                f2 = np.where(m1[:, None], f1, np.where(m2[:, None], fp, f2))
                id2 = np.where(m1, id1, np.where(m2, cid, id2))
                d1 = np.where(m1, d, d1)
                f1 = np.where(m1[:, None], fp, f1)
                id1 = np.where(m1, cid, id1)
    eje = f2 - f1
    eje /= np.maximum(np.linalg.norm(eje, axis=1), 1e-6)[:, None]
    borde = np.abs(np.sum((q - (f1 + f2) / 2) * eje, axis=1)) * celda
    par = np.modf(np.sin((id1 + id2) * 91.7 + id1 * id2 * 317.3) * 43758.5453)[0]
    return borde, np.abs(par)


def _mezcla(R, t):
    R = np.asarray(R, float)
    t = np.clip(t, 0, 1) * (len(R) - 1)
    i = np.minimum(np.floor(t).astype(int), len(R) - 2)
    f = (t - i)[:, None]
    return R[i] * (1 - f) + R[i + 1] * f


def _rgb(h):
    return np.array(_hex(h), float)


# ----------------------------------------------------------------------
#  La superficie en reposo: cada cara con su sitio en el cuerpo
# ----------------------------------------------------------------------
PIEL = {'jade', 'jade_osc', 'vientre'}
PINTADOS = PIEL | {'oro', 'obsidiana', 'cristal', 'colmillo', 'boca'}


def region(nombre):
    if nombre.startswith(('cola', 'punta_cola')):
        return 'cola'
    if nombre.startswith(('cabeza', 'mandibula', 'oreja', 'ceno', 'sable')):
        return 'cabeza'
    if nombre.startswith(('brazo', 'muslo')):
        return 'anca'
    if nombre.startswith(('antebrazo', 'mano', 'tibia', 'tarso', 'pie')):
        return 'pata'
    if nombre.startswith(('cresta', 'hombro', 'corona')):
        return 'cristal'
    return 'tronco'


class Cara:
    __slots__ = ('clave', 'mat', 'nodo', 'region', 'a', 'b', 'O', 'eu', 'ev', 'n', 'Ol', 'eul', 'evl', 'caja', 'texeles')


def _matriz(off, rot, ex):
    r = [rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
    p = [off[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
    return vr.T(*p) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R) @ vr.S(ex.get('esc', 1.0))


def superficie(raiz, planos=()):
    """Las caras del esqueleto en reposo y las cajas (para la sombra de contacto
    y para no sembrar rosetas dentro de otra pieza)."""
    caras, cajas = [], []

    def visitar(n, M):
        nombre, off, rot, cs, hijos = n
        Mn = M @ _matriz(off, rot, {})
        for ib, (box, mat) in enumerate(cs):
            if mat in planos:
                continue
            x0, y0, z0, w, h, d = box
            inv = np.linalg.inv(Mn)
            cajas.append((Mn, inv, np.array([x0 + w / 2, y0 + h / 2, z0 + d / 2]), np.array([w / 2, h / 2, d / 2]),
                          nombre, ib))
            for ic, (pts, uv) in enumerate(nm.caja_mosaico(box)):
                c = Cara()
                c.clave, c.mat, c.nodo, c.region = (nombre, ib, ic), mat, nombre, region(nombre)
                c.a, c.b = uv[0][0] * 16, uv[2][1] * 16
                p0, p1, p2 = (np.array(pts[k], float) for k in (0, 1, 2))
                c.Ol, c.eul, c.evl = p1, (p0 - p1) / c.a, (p2 - p1) / c.b
                c.O = (Mn @ np.array([*p1, 1.0]))[:3]
                c.eu = Mn[:3, :3] @ c.eul
                c.ev = Mn[:3, :3] @ c.evl
                nn = np.cross(c.eu, c.ev)
                # la normal hacia fuera de la caja
                centro = (Mn @ np.array([x0 + w / 2, y0 + h / 2, z0 + d / 2, 1.0]))[:3]
                medio = c.O + c.eu * c.a / 2 + c.ev * c.b / 2
                if nn @ (medio - centro) < 0:
                    nn = -nn
                c.n = nn / max(np.linalg.norm(nn), 1e-9)
                c.caja = len(cajas) - 1
                caras.append(c)
        for hj in hijos:
            visitar(hj, Mn)

    visitar(raiz, np.eye(4))
    return caras, cajas


def _dentro_de_otra(P, cajas, propia, margen=0.4):
    fuera = np.ones(len(P), bool)
    Ph = np.c_[P, np.ones(len(P))]
    for k, (M, inv, c, h, _, _) in enumerate(cajas):
        if k == propia:
            continue
        L = (Ph @ inv.T)[:, :3]
        dentro = np.all(np.abs(L - c) < h - margen, axis=1)
        fuera &= ~dentro
    return ~fuera


# ----------------------------------------------------------------------
#  Rosetas: Poisson sobre la superficie
# ----------------------------------------------------------------------
REGLAS = {
    # region: (separacion minima, radio min, radio max, tipo); a escala de las
    # teselas, las rosetas son anillos rotos de teselas oscuras
    'tronco': (22.0, 7.0, 10.0, 'roseta'),
    'anca': (17.0, 6.0, 8.0, 'roseta'),
    'cola': (12.0, 4.0, 5.5, 'roseta'),
    'pata': (10.0, 2.6, 3.8, 'mancha'),
    'cabeza': (8.0, 2.2, 3.0, 'mancha'),
    'vientre': (18.0, 2.6, 3.6, 'mancha'),
}


def sembrar_rosetas(caras, cajas, semilla=5):
    r = random.Random(semilla)
    cand = []
    for c in caras:
        if c.mat not in PIEL or c.region == 'cristal':
            continue
        reg = 'vientre' if c.mat == 'vientre' else c.region
        sep, r0, r1, tipo = REGLAS[reg]
        n = c.a * c.b / (sep * sep) * 3.0
        k = int(n) + (1 if r.random() < n - int(n) else 0)
        for _ in range(k):
            u, v = r.uniform(0, c.a), r.uniform(0, c.b)
            cand.append((c.O + c.eu * u + c.ev * v, sep, r.uniform(r0, r1), tipo, c.caja))
    r.shuffle(cand)
    P = np.array([q[0] for q in cand])
    ocultas = np.zeros(len(cand), bool)
    for k in set(q[4] for q in cand):
        idx = [i for i, q in enumerate(cand) if q[4] == k]
        ocultas[idx] = _dentro_de_otra(P[idx], cajas, k)
    rejilla, out = {}, []
    for i, (p, sep, rad, tipo, _) in enumerate(cand):
        if ocultas[i]:
            continue
        g = tuple((p // 16).astype(int))
        cerca = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for (q, s2) in rejilla.get((g[0] + dx, g[1] + dy, g[2] + dz), ()):
                        if np.linalg.norm(p - q) < max(sep, s2):
                            cerca = True
                            break
                    if cerca:
                        break
                if cerca:
                    break
            if cerca:
                break
        if cerca:
            continue
        rejilla.setdefault(g, []).append((p, sep))
        out.append(dict(c=p, R=rad, tipo=tipo, k=r.randint(3, 5), fi=r.uniform(0, math.tau), fi2=r.uniform(0, math.tau),
                        puntos=[p + np.array([r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 1)]) * rad * 0.35
                                for _ in range(r.choice([0, 1, 1, 2]))] if tipo == 'roseta' else []))
    return out


# ----------------------------------------------------------------------
#  Los pintores
# ----------------------------------------------------------------------
SOL = np.array([0.0, -69.0, -119.0])     # el sol del pecho, en reposo
EXTENSION = {2: 52.0, 3: 150.0, 4: 1e9, 5: 1e9}  # hasta donde llegan las grietas
MUSGO = {1: ('263c12', '34501a', '46661f', '5a7e28', '6e9432'), 2: ('3e3a1a', '524a22', '665c2a', '7a6e34', '8e8040')}


def _texeles(c):
    """Los texeles de la cara: su rejilla propia (renders) o los del hueco del
    atlas del juego, si la cara los trae ya calculados (rajang_juego.py)."""
    dados = getattr(c, 'texeles', None)
    if dados is not None:
        return dados
    w, h = max(1, int(math.ceil(c.a - 1e-6))), max(1, int(math.ceil(c.b - 1e-6)))
    U, V = np.meshgrid((np.arange(w) + 0.5) * c.a / w, (np.arange(h) + 0.5) * c.b / h)
    U, V = U.ravel(), V.ravel()
    P = c.O + U[:, None] * c.eu + V[:, None] * c.ev
    L = c.Ol + U[:, None] * c.eul + V[:, None] * c.evl
    return w, h, U, V, P, L


def _grano(P, s):
    q = np.floor(P * 1.0 + 0.5).astype(np.int64)
    return _hash(q[:, 0], q[:, 1], q[:, 2], s)


def _contacto(P, c, cajas):
    """Sombra donde la cara pasa pegada a otra pieza (las juntas)."""
    ao = np.zeros(len(P))
    Ph = np.c_[P, np.ones(len(P))]
    centro = P.mean(axis=0)
    radio = np.linalg.norm(P - centro, axis=1).max() + 4
    for k, (M, inv, cc, hh, _, _) in enumerate(cajas):
        if k == c.caja:
            continue
        cm = (M @ np.array([*cc, 1.0]))[:3]
        if np.linalg.norm(cm - centro) > radio + np.linalg.norm(hh) + 4:
            continue
        L = (Ph @ inv.T)[:, :3]
        fuera = np.linalg.norm(np.maximum(np.abs(L - cc) - hh, 0), axis=1)
        ao = np.maximum(ao, np.clip(1 - fuera / 3.5, 0, 1) * (fuera > 0.05))
    return ao


def _rosetas_en(P, c, ros, tono, oscuro):
    """Pinta las rosetas que tocan esta cara. Devuelve el color oscurecido."""
    centro = P.mean(axis=0)
    radio = np.linalg.norm(P - centro, axis=1).max()
    for ro in ros:
        if np.linalg.norm(ro['c'] - centro) > radio + ro['R'] + 2.5:
            continue
        d = P - ro['c']
        r = np.linalg.norm(d, axis=1)
        if r.min() > ro['R'] + 2.0:
            continue
        th = np.arctan2(d @ c.ev, d @ c.eu)
        R = ro['R']
        if ro['tipo'] == 'mancha':
            borde = R * (1 + 0.22 * np.sin(2 * th + ro['fi']) + 0.12 * np.sin(5 * th + ro['fi2']))
            m = r < borde
            tono[m] = oscuro[m]
            continue
        rr = R * (1 + 0.1 * np.sin(3 * th + ro['fi']))
        grosor = 0.75 + 0.22 * R
        trozo = 0.5 + 0.5 * np.cos(ro['k'] * th + ro['fi2'])
        anillo = (np.abs(r - rr) < grosor * (0.45 + 0.55 * trozo)) & (trozo > 0.16)
        dentro = r < rr - grosor * 0.45
        tono[dentro] = tono[dentro] * 0.8 + oscuro[dentro] * 0.2
        tono[anillo] = oscuro[anillo]
        for q in ro['puntos']:
            pm = np.linalg.norm(P - q, axis=1) < 0.85
            tono[pm] = oscuro[pm]
    return tono


TESELA = 4.0
ESMERALDA = ('2a8a50', '3aa866', '58c886', '86e2a8')


def _piel(c, fase, pal, ros, cajas):
    w, h, U, V, P, L = _texeles(c)
    n = len(P)
    J, Vn = pal['jade'], pal['vientre']
    T = 3.0 if c.region in ('cabeza', 'pata') else TESELA
    # la tesela de cada texel y su centro en el cuerpo
    iu, iv = np.floor(U / T), np.floor(V / T)
    cu = np.minimum((iu + 0.5) * T, c.a - 0.01)
    cv = np.minimum((iv + 0.5) * T, c.b - 0.01)
    Pc = c.O + cu[:, None] * c.eu + cv[:, None] * c.ev
    clave = np.floor(Pc * 2 + 0.5).astype(np.int64)
    azar = _hash(clave[:, 0], clave[:, 1], clave[:, 2], 37)
    azar2 = _hash(clave[:, 0], clave[:, 1], clave[:, 2], 39)
    lu, lv = U - iu * T, V - iv * T
    tam_u = np.minimum(T, c.a - iu * T)
    tam_v = np.minimum(T, c.b - iv * T)
    lento = fbm(Pc, 42, 11, 2) - 0.5
    medio = fbm(Pc, 13, 23, 2) - 0.5
    grano = _grano(P, 31) - 0.5
    y = Pc[:, 1]
    if c.mat == 'vientre':
        t = 0.58 + 0.3 * lento + 0.16 * medio + 0.22 * (azar - 0.5)
        col = _mezcla(Vn, t)
        oscuro = _mezcla(J, np.full(n, 0.12)) * 0.75
    else:
        t = 0.55 + 0.3 * lento + 0.16 * medio + 0.16 * (azar - 0.5)
        if c.region in ('tronco', 'cola', 'anca'):
            # el lomo, mas oscuro; los costados bajos, mas claros
            t -= 0.18 * np.clip((-y - 92) / 18, 0, 1)
            t += 0.1 * np.clip((y + 66) / 22, 0, 1)
        if c.n[1] > 0.6:
            t -= 0.1
        if c.mat == 'jade_osc':
            t -= 0.3
        col = _mezcla(J, t)
        oscuro = _mezcla(J, np.full(n, 0.0)) * (0.5 if c.mat == 'jade' else 0.42)
        # alguna tesela de esmeralda clara y alguna de jade casi negro
        if c.mat == 'jade' and fase < 5:
            esm = azar2 > 0.94
            col[esm] = _mezcla([_rgb(x) for x in ESMERALDA], 0.3 + 0.7 * azar[esm]) * (0.85 - 0.08 * (fase - 1))
            negra = azar2 < 0.025
            col[negra] = col[negra] * 0.7
    # las rosetas: anillos rotos de teselas oscuras
    if c.region != 'cristal':
        col = _rosetas_en(Pc, c, ros, col, col * 0.4 + oscuro * 0.6 + (azar[:, None] - 0.5) * 10)
    # el bisel de cada tesela: canto de arriba y de la izquierda claros, de abajo y de la derecha oscuros
    k = np.ones(n)
    k[lv < 1] *= 1.16
    k[(lu < 1) & (lv >= 1)] *= 1.08
    k[lv >= tam_v - 1] *= 0.74
    k[(lu >= tam_u - 1) & (lv < tam_v - 1)] *= 0.86
    col *= (k + 0.05 * grano)[:, None]
    # sombra de contacto en las juntas
    ao = _contacto(P, c, cajas)
    col *= (1 - 0.32 * ao)[:, None]
    emis = np.zeros((n, 4))
    # el musgo: teselas enteras en lo alto (fase I verde, fase II seco)
    if fase in MUSGO and c.mat != 'vientre' and c.region in ('tronco', 'cabeza', 'cola', 'cristal', 'anca'):
        mg = fbm(Pc, 9, 51, 3)
        umbral = 0.56 if fase == 1 else 0.62
        if c.n[1] < -0.5:
            m = mg > umbral
        elif abs(c.n[1]) < 0.5:
            ytop = min(c.O[1], (c.O + c.eu * c.a)[1], (c.O + c.ev * c.b)[1], (c.O + c.eu * c.a + c.ev * c.b)[1])
            largo = 8 * np.clip((mg - 0.47) / 0.25, 0, 1) * (0.4 + 0.6 * azar)
            m = (y - ytop) < largo
        else:
            m = np.zeros(n, bool)
        if m.any():
            tm_ = 0.5 + 1.4 * (mg[m] - umbral) + 0.3 * (azar[m] - 0.5)
            col[m] = _mezcla([_rgb(x) for x in MUSGO[fase]], tm_) * k[m, None] * (1 - 0.25 * ao[m])[:, None]
    # las grietas de la maldicion
    if pal['grieta']:
        lejos = np.linalg.norm(P - SOL, axis=1) + 40 * (fbm(P, 34, 61, 2) - 0.5)
        peso = np.clip((EXTENSION[fase] - lejos) / 45, 0, 1)
        if peso.max() > 0:
            alabeo = np.stack([fbm(P, 9, 70 + k_, 2) - 0.5 for k_ in range(3)], 1) * 7
            celda = {2: 19, 3: 17, 4: 15, 5: 15}[fase]
            borde, par = grieta_red(P + alabeo, celda, 81)
            activa = par < {2: 0.2 + 0.3 * peso, 3: 0.18 + 0.27 * peso, 4: 0.3, 5: 0.2}[fase]
            ancho = {2: 0.5, 3: 0.6, 4: 0.66, 5: 0.7}[fase] * (0.55 + 0.45 * peso)
            nucleo = activa & (peso > 0) & (borde < ancho)
            halo = activa & (peso > 0) & (borde < ancho + 0.9) & ~nucleo
            gb, gc = _rgb(pal['grieta'][1]), _rgb(pal['grieta'][0])
            col[halo] = col[halo] * 0.72 + gb * 0.28
            col[nucleo] = col[nucleo] * 0.25 + gb * 0.35
            emis[halo] = np.c_[np.tile(gb, (halo.sum(), 1)), np.full(halo.sum(), 22 + 8 * min(fase, 4))]
            kk = np.clip(0.6 + 0.4 * peso[nucleo], 0, 1)
            centro_ = borde[nucleo] < ancho[nucleo] * 0.45
            colg = np.where(centro_[:, None], gc, gb)
            emis[nucleo] = np.c_[colg, (70 + 20 * fase if fase < 5 else 45) * kk]
    return w, h, col, emis


def espiral_cuadrada(w, h, paso=4, margen=2):
    """La espiral cuadrada de los templos (mascara de w x h): una tira de
    paso/2 que da vueltas hacia dentro."""
    m = np.zeros((h, w), bool)
    x, y = margen, h - 1 - margen
    W_, H_ = w - 1 - 2 * margen, h - 1 - 2 * margen
    largos = [H_, W_, H_]
    k = 1
    while True:
        largos.append(W_ - k * paso)
        largos.append(H_ - k * paso)
        k += 1
        if largos[-1] <= 0 or largos[-2] <= 0:
            break
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    g = max(1, paso // 2)
    for i, L_ in enumerate(largos):
        if L_ <= 0:
            break
        dx, dy = dirs[i % 4]
        for s_ in range(int(L_) + 1):
            px, py = x + dx * s_, y + dy * s_
            m[max(0, py):min(h, py + g), max(0, px):min(w, px + g)] = True
        x, y = x + dx * int(L_), y + dy * int(L_)
    return m


# --- la greca escalonada, en pixeles de la banda
def _greca(x, y, alto):
    """Dientes escalonados que se alternan arriba y abajo de una banda de 'alto'
    texeles (la greca de los templos)."""
    periodo = 2 * alto
    xm = np.mod(x, periodo)
    tri = alto - np.abs(xm - alto)
    esc = np.floor(tri / 2) * 2
    arriba = y < esc - 1
    tri2 = alto - np.abs(np.mod(x + alto, periodo) - alto)
    abajo = y >= alto - np.floor(tri2 / 2) * 2 + 1
    return arriba | abajo


def _rombo(iu, iv, w, h):
    """El rombo escalonado del centro de las placas grandes."""
    du, dv = np.abs(iu - (w - 1) / 2), np.abs(iv - (h - 1) / 2)
    r = np.floor((du + dv) / 2) * 2
    lado = min(w, h) / 2 - 7
    return ((r == np.floor(lado * 0.8 / 2) * 2) | (r == np.floor(lado * 0.4 / 2) * 2)) & (du + dv < lado)


def _oro(c, fase, pal, cajas):
    w, h, U, V, P, L = _texeles(c)
    n = len(P)
    O = pal['oro']
    grano = _grano(P, 91) - 0.5
    t = 0.62 + 0.3 * (fbm(P, 5, 93, 2) - 0.5) + 0.12 * grano
    # brillo arriba
    ys = np.array([c.O[1], (c.O + c.eu * c.a)[1], (c.O + c.ev * c.b)[1], (c.O + c.eu * c.a + c.ev * c.b)[1]])
    if ys.max() - ys.min() > 1:
        t += 0.2 * (ys.max() - P[:, 1]) / (ys.max() - ys.min()) - 0.1
    iu, iv = np.floor(U).astype(int), np.floor(V).astype(int)
    if min(w, h) >= 4:
        canto = (iu == 0) | (iv == 0) | (iu == w - 1) | (iv == h - 1)
        surco = ~canto & ((iu == 1) | (iv == 1) | (iu == w - 2) | (iv == h - 2))
        t[canto] += 0.16
        t[surco] -= 0.32
        if min(w, h) >= 12 and max(w, h) <= 2.2 * min(w, h):
            # placa: la espiral cuadrada en relieve (la tira clara, el surco oscuro)
            esp = espiral_cuadrada(w - 4, h - 4, 4, 0)
            dentro = (iu >= 2) & (iv >= 2) & (iu < w - 2) & (iv < h - 2)
            e = np.zeros(n, bool)
            e[dentro] = esp[np.clip(iv[dentro] - 2, 0, h - 5), np.clip(iu[dentro] - 2, 0, w - 5)]
            arriba = np.zeros(n, bool)
            arriba[dentro] = ~esp[np.clip(iv[dentro] - 3, 0, h - 5), np.clip(iu[dentro] - 2, 0, w - 5)] & e[dentro]
            t[dentro & ~e] -= 0.34
            t[e] += 0.06
            t[arriba] += 0.14
        elif min(w, h) >= 16:
            # placa grande: la greca corre por todo el borde y en el centro, el rombo
            hb = 5
            du = np.minimum(iu - 2, w - 3 - iu)
            dv = np.minimum(iv - 2, h - 3 - iv)
            enborde = (np.minimum(du, dv) >= 0) & (np.minimum(du, dv) < hb)
            x = np.where(du < dv, iv, iu)
            yb = np.minimum(du, dv)
            g = enborde & _greca(x, yb, hb)
            linea = (np.minimum(du, dv) == hb)
            t[g] -= 0.26
            t[linea] -= 0.3
            t[_rombo(iu, iv, w, h)] -= 0.26
        elif min(w, h) >= 7:
            largo_u = w >= h
            x = (iu - 2) if largo_u else (iv - 2)
            yb = (iv - 2) if largo_u else (iu - 2)
            alto = (h if largo_u else w) - 4
            dentro = (iu >= 2) & (iv >= 2) & (iu < w - 2) & (iv < h - 2)
            g = dentro & _greca(x, yb, alto)
            t[g] -= 0.24
    col = _mezcla(O, t)
    # la maldicion lo mancha
    if fase >= 2:
        mancha = fbm(P, 6, 97, 3)
        m = mancha > {2: 0.7, 3: 0.6, 4: 0.53, 5: 0.5}[fase]
        col[m] = col[m] * 0.45 + _rgb('2a3a24') * 0.35
    col *= (1 - 0.25 * _contacto(P, c, cajas))[:, None]
    return w, h, col, np.zeros((n, 4))


def _obsidiana(c, fase, pal, cajas):
    w, h, U, V, P, L = _texeles(c)
    n = len(P)
    t = 0.4 + 0.3 * (fbm(P, 3, 101, 2) - 0.5) + 0.2 * (_grano(P, 103) - 0.5)
    col = _mezcla([_rgb(x) for x in ('08070e', '110e1a', '1a1628', '262238', '3a3352')], t)
    veta = np.abs(np.mod(U - V * 0.7, 6) - 3) < 0.45
    col[veta] = col[veta] * 0.4 + _rgb('6a5a94') * 0.6
    return w, h, col, np.zeros((n, 4))


def _cristal(c, fase, pal, cajas):
    w, h, U, V, P, L = _texeles(c)
    n = len(P)
    a, b = _rgb(pal['cristal'][0]), _rgb(pal['cristal'][1])
    # la punta es -Y en el espacio del cristal
    ys = L[:, 1]
    k = np.clip((-ys) / max(1.0, -ys.min()), 0, 1) if ys.min() < -1 else np.full(n, 0.5)
    col = b[None] * (0.55 + 0.25 * k[:, None]) + a[None] * (0.18 + 0.35 * k[:, None])
    faceta = np.abs(np.mod(U * 0.8 + V * 0.45, 5) - 2.5) < 0.5
    col[faceta] = col[faceta] * 0.7 + a * 0.3
    iu, iv = np.floor(U).astype(int), np.floor(V).astype(int)
    canto = (iu == 0) | (iv == 0) | (iu == w - 1) | (iv == h - 1)
    col[canto] = col[canto] * 0.6 + a * 0.4
    col += (_grano(P, 107) - 0.5)[:, None] * 14
    fuerza = 0.12 + 0.05 * fase if fase < 5 else 0.06
    alfa = (fuerza * (0.45 + 0.55 * k) + 0.1 * faceta + 0.08 * canto) * 255
    emis = np.c_[np.tile(b, (n, 1)), np.clip(alfa, 0, 255)]
    return w, h, col, emis


def _colmillo(c, fase, pal, cajas):
    w, h, U, V, P, L = _texeles(c)
    n = len(P)
    base = [_rgb(x) for x in ('9aaa90', 'bccab0', 'd8e2cc', 'eef2e4', 'fffff4')]
    ly = L[:, 1]
    largo = 28.0 if not c.nodo.startswith('sable_punta') else 11.0
    k = np.clip(ly / largo, 0, 1)
    if c.nodo.startswith('sable_punta'):
        k = 0.75 + 0.25 * k
    t = 0.35 + 0.6 * k + 0.1 * (_hash(np.floor(U).astype(np.int64), np.zeros(n, np.int64), np.zeros(n, np.int64), 111) - 0.5) \
        + 0.08 * (_grano(P, 113) - 0.5)
    col = _mezcla(base, t)
    if not c.nodo.startswith('sable_punta'):
        encia = ly < 1.5
        col[encia] = _mezcla(pal['jade'], np.full(encia.sum(), 0.15))
    return w, h, col, np.zeros((n, 4))


def _boca(c, fase, pal, cajas):
    """Por dentro de la boca: jade casi negro y la maldicion que brilla desde la
    garganta, a manchas."""
    w, h, U, V, P, L = _texeles(c)
    n = len(P)
    a_, b_ = _rgb(pal['boca'][0]), _rgb(pal['boca'][1])
    r = fbm(P, 4, 121, 2)
    col = _mezcla([_rgb(x) for x in ('040c06', '0a1c0e', '123020')], r) + b_ * 0.12
    alfa = np.clip(40 + 150 * (r - 0.35) / 0.4, 30, 190) * (0.45 if fase == 5 else 1.0)
    emis = np.c_[np.where((r > 0.66)[:, None], a_, b_), alfa]
    return w, h, col, emis


PINTORES = {'oro': _oro, 'obsidiana': _obsidiana, 'cristal': _cristal, 'colmillo': _colmillo, 'boca': _boca}

_CACHE = {}


def texturas(raiz, fase, pal, planos=()):
    """{clave de cara: (textura RGBA, brillo RGBA o None)} para toda la piel."""
    clave_cache = fase
    if clave_cache in _CACHE:
        return _CACHE[clave_cache]
    caras, cajas = superficie(raiz, planos)
    ros = sembrar_rosetas(caras, cajas)
    out = {}
    for c in caras:
        if c.mat not in PINTADOS:
            continue
        if c.mat in PIEL:
            w, h, col, emis = _piel(c, fase, pal, ros, cajas)
        else:
            w, h, col, emis = PINTORES[c.mat](c, fase, pal, cajas)
        tex = np.zeros((h, w, 4), np.uint8)
        tex[..., :3] = np.clip(col, 0, 255).reshape(h, w, 3)
        tex[..., 3] = 255
        e = None
        if emis[:, 3].max() > 0:
            # premultiplicado: el halo de una grieta tine poco, el nucleo mucho
            k = emis[:, 3:4] / 255.0
            em = np.c_[emis[:, :3] * k, np.where(emis[:, 3] > 0, 255, 0)]
            e = np.clip(em, 0, 255).reshape(h, w, 4).astype(np.uint8)
        out[c.clave] = (tex, e)
    _CACHE[clave_cache] = out
    return out


# ----------------------------------------------------------------------
#  Cuadrilateros con su clave de cara
# ----------------------------------------------------------------------
UV_CARA = [(1, 0), (0, 0), (0, 1), (1, 1)]


def quads(raiz, pose, M, planos=()):
    out = []

    def visitar(n, Mp):
        nombre, off, rot, cs, hijos = n
        ex = pose.get(nombre, {})
        if ex.get('oculto'):
            return
        Mn = Mp @ _matriz(off, rot, ex)
        for ib, (box, mat) in enumerate(cs):
            caras = nm.caja_mosaico(box)
            if mat in planos:
                caras = caras[-1:]   # las piezas planas: una cara, con su imagen entera
            for ic, (pts, uv) in enumerate(caras):
                w = [(M @ Mn @ np.array([*q, 1.0]))[:3] for q in pts]
                out.append((w, UV_CARA if (mat in PINTADOS or mat in planos) else uv, mat, (nombre, ib, ic)))
        for hj in hijos:
            visitar(hj, Mn)

    visitar(raiz, np.eye(4))
    return out

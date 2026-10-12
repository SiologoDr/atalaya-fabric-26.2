"""
Los mini jefes en el juego: de los bocetos en voxeles (minijefes_modelo.py) a la malla que pinta el juego.

Como un mob de Minecraft (Juan, 11-10-2026: "su textura no parece ya mobs de minecraft"; antes cada voxel de un
pixel era geometria con la luz suavizada y parecia un render, no un mob): la FORMA va en bloques de 2 pixeles de
modelo, el DETALLE del boceto (cada voxel de un pixel) va pintado como textura de pixel en las caras de esos bloques
y la LUZ es plana por cara, como en vanilla y en los jefes (arriba clara, los lados a medias, abajo oscura).

Cada pieza pasa sus voxeles a celdas de 2x2x2 (con el desfase que deja menos celdas, para que las piezas finas no
engorden) y una celda va llena si tiene al menos dos voxeles. Las caras a la vista de las celdas se juntan en
rectangulos por plano, y cada texel de un rectangulo toma el voxel del boceto que se ve desde fuera en esa columna
de la celda: los ojos, las escamas, las runas y las plumas siguen ahi, pero pintados.

Sale para cada mini jefe:
  - assets/atalaya/minijefes/<nombre>.malla (gzip): las piezas (nombre, padre, origen y giro de reposo) y sus
    cuadrilateros, los de la piel y los que brillan, que lee MiniJefeMalla.java;
  - textures/entity/minijefes/<nombre>.png y <nombre>_brillo.png: el atlas y su capa de luz.

Con dos niveles de detalle: el de siempre y, de lejos, la forma en bloques de 4 (MiniJefeCuerpoLayer elige).

El reposo de cada pieza es su giro del boceto mas la postura de reposo (MOCTEZUMA_REPOSO...): las animaciones se
suman a el, asi que todas acaban en cero y se mezclan sin saltos.

Las capas, los faldones y la cola del fenix se separan en piezas (cadenas) para que ondeen; las juntas comparten
una fila de voxeles, y al doblarse no se abre hueco.

Uso: python minijefes_juego.py <raiz del proyecto> [carpeta de pruebas]
"""
import gzip
import math
import os
import struct
import sys

import numpy as np
from PIL import Image

import minijefes_modelo as mj
import vigia_render as vr

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
PRUEBAS = sys.argv[2] if len(sys.argv) > 2 else None

DIRS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
# Los niveles de detalle: (bloque en pixeles del boceto, voxeles que hacen falta para llenar una celda). El de cerca
# en bloques de 2; el de lejos en bloques de 4, cuando uno de 2 ya no llega a dos pixeles de la pantalla.
NIVELES = ((2, 2), (4, 3))
# Lo mas largo de un rectangulo (en celdas).
MAXIMO = 16
# Lo que se meten las UV hacia dentro de cada rectangulo (texels): que el borde no tome el texel de al lado.
MARGEN_UV = 0.01
# Desde cuanto brillo va un voxel a la capa de luz. El fenix se pinta entero a plena luz (es fuego), asi que solo
# lleva a esa capa lo que brilla de verdad; si no, la mitad de sus plumas se pintarian dos veces.
BRILLO_DESDE = {'xiuhquetzal': 0.5}


class Hueso:
    """Una pieza: su padre (indice, -1 la raiz), su origen en el marco del padre (pixeles, con la escala ya puesta),
    su giro de reposo (grados), la escala acumulada (va metida en la geometria) y sus voxeles sin escalar."""

    def __init__(self, nombre, padre, pivote, rot, esc, d, grupos=None):
        self.nombre = nombre
        self.padre = padre
        self.pivote = np.array(pivote, float)
        self.rot = np.array(rot, float)
        self.esc = esc
        self.d = dict(d)
        self.grupos = grupos or {}


def _idx(hs, nombre):
    for i, h in enumerate(hs):
        if h.nombre == nombre:
            return i
    raise KeyError(nombre)


def separar(hs, origen, nuevo, posiciones, pivote):
    """Pasa a una pieza nueva, hija de 'origen' y con su origen en 'pivote' (entero, en el marco de origen), los
    voxeles de 'posiciones'."""
    i = _idx(hs, origen)
    o = hs[i]
    pv = tuple(int(c) for c in pivote)
    d = {}
    for p in posiciones:
        if p in o.d:
            d[(p[0] - pv[0], p[1] - pv[1], p[2] - pv[2])] = o.d.pop(p)
    hs.append(Hueso(nuevo, i, np.array(pv, float) * o.esc, (0, 0, 0), o.esc, d))
    return hs[-1]


def cadena(hs, origen, nombres, cortes, eje=1, solape=1):
    """Parte una pieza en una cadena a lo largo de 'eje': cada corte (en el marco de 'origen') abre una pieza hija de
    la anterior con su origen en el corte. Las juntas comparten 'solape' filas (uno para todas o uno por junta)."""
    actual, base = origen, 0
    solapes = list(solape) if isinstance(solape, (list, tuple)) else [solape] * len(cortes)
    for nombre, corte, sol in zip(nombres, cortes, solapes):
        o = hs[_idx(hs, actual)]
        c = corte - base
        pos = [p for p in o.d if p[eje] >= c - sol]
        quedan = {p: o.d[p] for p in pos if p[eje] < c}
        piv = [0, 0, 0]
        piv[eje] = c
        separar(hs, actual, nombre, pos, piv)
        o.d.update(quedan)
        actual, base = nombre, corte


# Las piezas que se separan para que ondeen.
def _separa_moctezuma(hs):
    p = hs[_idx(hs, 'pelvis')]
    separar(hs, 'pelvis', 'faldon_frente', p.grupos['faldon_frente'], (0, 1, -5))
    separar(hs, 'pelvis', 'faldon_atras', p.grupos['faldon_atras'], (0, 1, 5))


def _separa_yiatzo(hs):
    # Flota: medio bloque por encima del suelo.
    hs[_idx(hs, 'raiz')].pivote += np.array([0.0, -8.0, 0.0])
    c = hs[_idx(hs, 'cuerpo')]
    separar(hs, 'cuerpo', 'capa', c.grupos['capa'], (0, -25, 7))
    cadena(hs, 'capa', ['capa2'], [22])
    # Los jirones del bajo, en dos piezas que cuelgan una de otra: ondean con la fisica (no es un pilar). La tunica
    # maciza (hasta y = 12) va con el cuerpo: antes el corte iba en y = 4 y, al balancearse, el bajo entero se
    # descolocaba de la pieza de arriba (Juan, 11-10-2026: "se descoloca de su pieza de arriba dando la sensacion que
    # no esta todo junto"). Las juntas comparten 2 y 3 filas: al ondear no se abre hueco.
    cadena(hs, 'cuerpo', ['falda', 'falda2'], [15, 23], solape=[2, 3])


def _separa_atlahua(hs):
    t = hs[_idx(hs, 'torso')]
    separar(hs, 'torso', 'capa', t.grupos['capa'], (0, -20, 6))
    cadena(hs, 'capa', ['capa2'], [19])


def _separa_xiuhquetzal(hs):
    # Vuela: el juego lo sube de verdad, asi que las garras van a la altura de sus pies (los de la entidad).
    hs[_idx(hs, 'raiz')].pivote = np.array([0.0, 8.0, 0.0])
    cadena(hs, 'cola', ['cola2', 'cola3'], [18, 38])


SEPARAR = {'moctezuma': _separa_moctezuma, 'yiatzo': _separa_yiatzo, 'atlahua': _separa_atlahua,
           'xiuhquetzal': _separa_xiuhquetzal}


def esqueleto(nombre):
    """Las piezas de un mini jefe, padres antes que hijos."""
    hacer, reposo, _ = mj.MINIJEFES[nombre]
    hs = []

    def visitar(nodo, padre, esc_padre):
        nom, off, rot, vox, hijos = nodo[:5]
        e = nodo[5] if len(nodo) > 5 else 1.0
        r = np.array(rot, float) + np.array(reposo.get(nom, {}).get('rot', (0, 0, 0)), float)
        hs.append(Hueso(nom, padre, np.array(off, float) * esc_padre, r, esc_padre * e,
                        vox.d if vox is not None else {}, vox.grupos if vox is not None else {}))
        i = len(hs) - 1
        for c in hijos:
            visitar(c, i, esc_padre * e)
    visitar(hacer(), -1, 1.0)
    SEPARAR[nombre](hs)
    # Padres antes que hijos (las separadas van al final, pero siempre despues de su padre).
    return hs


# ----------------------------------------------------------------------
#  Caras, rectangulos y atlas
# ----------------------------------------------------------------------
def _rgbe(c):
    if isinstance(c, str):
        rgb, e = mj.NOMBRADOS[c]
        return tuple(int(v) for v in rgb), 1.0
    return (int(c[0]), int(c[1]), int(c[2])), float(c[3])


def celdas(d, paso, minimo):
    """Los voxeles en celdas de paso x paso x paso, con el desfase que deja menos celdas (asi una asta de dos voxeles
    no se vuelve de cuatro). Una celda va llena si tiene 'minimo' voxeles o mas. Devuelve las celdas y el desfase."""
    mejor = None
    for ox in range(paso):
        for oy in range(paso):
            for oz in range(paso):
                cs = {}
                for (x, y, z) in d:
                    k = ((x + ox) // paso, (y + oy) // paso, (z + oz) // paso)
                    cs[k] = cs.get(k, 0) + 1
                llenas = {k for k, n in cs.items() if n >= minimo}
                if mejor is None or len(llenas) < len(mejor[0]):
                    mejor = (llenas, (ox, oy, oz))
    return mejor


def textura_cara(d, celda, off, paso, di):
    """Los paso x paso texels de la cara 'di' de una celda: en cada columna, el voxel del boceto que se ve desde fuera
    (el primero entrando por esa cara) o, si la columna esta vacia, el voxel de la celda mas cercano."""
    eje = di // 2
    ua, va = [a for a in range(3) if a != eje]
    base = [celda[a] * paso - off[a] for a in range(3)]
    fondo = range(paso - 1, -1, -1) if di % 2 == 0 else range(paso)
    finos = None
    tex = [[None] * paso for _ in range(paso)]
    for j in range(paso):
        for i in range(paso):
            p = [0, 0, 0]
            p[ua] = base[ua] + i
            p[va] = base[va] + j
            col = None
            for t in fondo:
                p[eje] = base[eje] + t
                if tuple(p) in d:
                    col = d[tuple(p)]
                    break
            if col is None:
                if finos is None:
                    finos = [(x, y, z) for x in range(base[0], base[0] + paso) for y in range(base[1], base[1] + paso)
                             for z in range(base[2], base[2] + paso) if (x, y, z) in d]
                p[eje] = base[eje] + fondo[0]
                col = d[min(finos, key=lambda f: (f[0] - p[0]) ** 2 + (f[1] - p[1]) ** 2 + (f[2] - p[2]) ** 2)]
            tex[j][i] = col
    return tex


def rectangulos(d, paso, minimo):
    """Las caras a la vista de las celdas, juntas en rectangulos por plano (hasta MAXIMO celdas por lado), con su
    textura (un texel por voxel del boceto), la normal plana de la cara y todo en pixeles del boceto: u, v y k son
    la esquina y el plano, w y h el tamano en texels."""
    llenas, off = celdas(d, paso, minimo)
    planos = {}
    for c in llenas:
        for di, (dx, dy, dz) in enumerate(DIRS):
            if (c[0] + dx, c[1] + dy, c[2] + dz) in llenas:
                continue
            eje = di // 2
            ua, va = [a for a in range(3) if a != eje]
            k = c[eje] + (1 if di % 2 == 0 else 0)
            planos.setdefault((di, k), {})[(c[ua], c[va])] = c
    rects = []
    for (di, k), plano in planos.items():
        eje = di // 2
        ua, va = [a for a in range(3) if a != eje]
        usadas = set()
        for (u, v) in sorted(plano, key=lambda t: (t[1], t[0])):
            if (u, v) in usadas:
                continue
            w = 1
            while w < MAXIMO and (u + w, v) in plano and (u + w, v) not in usadas:
                w += 1
            h = 1
            while h < MAXIMO and all((u + i, v + h) in plano and (u + i, v + h) not in usadas for i in range(w)):
                h += 1
            cols = [[None] * (w * paso) for _ in range(h * paso)]
            for i in range(w):
                for j in range(h):
                    usadas.add((u + i, v + j))
                    t = textura_cara(d, plano[(u + i, v + j)], off, paso, di)
                    for jj in range(paso):
                        cols[j * paso + jj][i * paso:(i + 1) * paso] = t[jj]
            ku, kv, kk = u * paso - off[ua], v * paso - off[va], k * paso - off[eje]
            pts = []
            for (cu, cv) in ((ku, kv), (ku + w * paso, kv), (ku + w * paso, kv + h * paso), (ku, kv + h * paso)):
                p = [0, 0, 0]
                p[eje], p[ua], p[va] = kk, cu, cv
                pts.append(p)
            uvl = [(0, 0), (w * paso, 0), (w * paso, h * paso), (0, h * paso)]
            n = np.array(DIRS[di], float)
            # Que la cara mire hacia fuera (en sentido antihorario visto desde fuera).
            pa = np.array(pts, float)
            if np.cross(pa[1] - pa[0], pa[2] - pa[0]) @ n < 0:
                pts, uvl = pts[::-1], uvl[::-1]
            rects.append({'w': w * paso, 'h': h * paso, 'cols': cols, 'pts': pts, 'nors': [n] * 4, 'uvl': uvl, 'di': di,
                          'k': kk, 'u': ku, 'v': kv, 'paso': 1})
    return rects


def empaquetar(todos):
    """Coloca los rectangulos en estantes; devuelve el ancho y el alto del atlas (y pone 'ax', 'ay' a cada uno)."""
    area = sum(r['w'] * r['h'] for r in todos)
    ancho = 64
    while ancho * ancho < area * 1.25:
        ancho *= 2
    orden = sorted(todos, key=lambda r: (-r['h'], -r['w']))
    x = y = alto_estante = 0
    for r in orden:
        if x + r['w'] > ancho:
            x, y, alto_estante = 0, y + alto_estante, 0
        r['ax'], r['ay'] = x, y
        x += r['w']
        alto_estante = max(alto_estante, r['h'])
    alto = y + alto_estante
    alto = (alto + 15) // 16 * 16
    return ancho, alto


def pintar(todos, ancho, alto, desde=0.05):
    base = np.zeros((alto, ancho, 4), np.uint8)
    brillo = np.zeros((alto, ancho, 4), np.uint8)
    for r in todos:
        r['brilla'] = False
        for j, fila in enumerate(r['cols']):
            for i, c in enumerate(fila):
                rgb, e = _rgbe(c)
                base[r['ay'] + j, r['ax'] + i] = (*rgb, 255)
                if e >= desde:
                    a = 255 if e >= 1 else int(round(min(1.0, e * 1.15) * 255))
                    brillo[r['ay'] + j, r['ax'] + i] = (*rgb, a)
                    r['brilla'] = True
    return base, brillo


def mascara(nombre, hs, ancho, alto):
    """La mascara de disolverse (la alfa de cada texel: lo que antes se va). Los de pie se deshacen de arriba abajo;
    el fenix, de las puntas de las alas y la cola hacia el pecho. Con grano, para que se vaya a trozos."""
    M = matrices(hs)
    valores = np.zeros((alto, ancho))
    hay = np.zeros((alto, ancho), bool)
    puntos = []
    for i, h in enumerate(hs):
        for r in [r for nivel in h.niveles for r in nivel]:
            eje = r['di'] // 2
            ua, va = [a for a in range(3) if a != eje]
            for j in range(r['h']):
                for ii in range(r['w']):
                    p = [0.0, 0.0, 0.0]
                    p[eje] = r['k']
                    p[ua] = r['u'] + ii + 0.5
                    p[va] = r['v'] + j + 0.5
                    q = M[i] @ np.array([*(np.array(p) * r['paso'] * h.esc), 1.0])
                    puntos.append((r['ay'] + j, r['ax'] + ii, q[0], q[1], q[2]))
    P = np.array(puntos)
    if nombre == 'xiuhquetzal':
        c = np.array([0.0, -2.0, 0.0])
        d = np.sqrt((P[:, 2] - c[0]) ** 2 + ((P[:, 3] - c[1]) * 1.4) ** 2 + (P[:, 4] - c[2]) ** 2)
        v = d / d.max()
    else:
        # Y hacia abajo: los de arriba (y pequena) antes.
        y = P[:, 3]
        v = 1.0 - (y - y.min()) / (y.max() - y.min() + 1e-9)
    rng = np.random.default_rng(len(nombre))
    grano = rng.random(len(v))
    v = np.clip(0.03 + 0.94 * (v * 0.82 + grano * 0.18), 0.03, 0.97)
    for (fy, fx, *_), val in zip(P, v):
        valores[int(fy), int(fx)] = val
        hay[int(fy), int(fx)] = True
    img = np.zeros((alto, ancho, 4), np.uint8)
    img[..., :3] = 255
    img[..., 3] = np.where(hay, np.round(valores * 255), 255).astype(np.uint8)
    return img


# ----------------------------------------------------------------------
#  La malla
# ----------------------------------------------------------------------
def malla(nombre):
    """Las piezas con sus rectangulos, el atlas y su capa de luz."""
    hs = esqueleto(nombre)
    todos = []
    for h in hs:
        h.niveles = []
        for paso, minimo in NIVELES:
            rs = rectangulos(h.d, paso, minimo) if h.d else []
            h.niveles.append(rs)
            todos += rs
        h.rects = h.niveles[0]
    ancho, alto = empaquetar(todos)
    base, brillo = pintar(todos, ancho, alto, BRILLO_DESDE.get(nombre, 0.05))
    return hs, ancho, alto, base, brillo


def _vertices(h, r, ancho, alto):
    """Los cuatro vertices de un rectangulo: posicion (pixeles del modelo, con la escala de la pieza), normal y UV en
    texels (metidas MARGEN_UV hacia dentro)."""
    out = []
    for p, n, (du, dv) in zip(r['pts'], r['nors'], r['uvl']):
        u = r['ax'] + du + (MARGEN_UV if du == 0 else -MARGEN_UV)
        v = r['ay'] + dv + (MARGEN_UV if dv == 0 else -MARGEN_UV)
        out.append((np.array(p, float) * r['paso'] * h.esc, n, (u, v)))
    return out


def escribir(nombre, hs, ancho, alto, ruta):
    """El fichero que lee MiniJefeMalla.java (gzip, enteros en big endian como DataInputStream):

        'MJM2', ancho y alto del atlas (u16), piezas (u16), niveles de detalle (u16)
        por pieza: nombre (u16 + utf-8), padre (i16), origen x y z (f32, pixeles), giro x y z (f32, grados) y, por
                   nivel, sus cuadrilateros de la piel (u32) y de los que brillan (u32)
        por nivel y por pieza, sus cuadrilateros (primero la piel, luego los que brillan), 4 vertices cada uno:
                   x y z (i16, 1/128 de pixel), normal (3 x i8, 1/127), u v (u16, 1/64 de texel)
    """
    cab = bytearray(b'MJM2')
    cab += struct.pack('>HHHH', ancho, alto, len(hs), len(NIVELES))
    cuerpo = bytearray()
    for h in hs:
        nb = h.nombre.encode('utf-8')
        cab += struct.pack('>H', len(nb)) + nb
        cab += struct.pack('>h3f3f', h.padre, *h.pivote, *h.rot)
        for rs in h.niveles:
            cab += struct.pack('>II', len(rs), sum(1 for r in rs if r['brilla']))
    for nivel in range(len(NIVELES)):
        for h in hs:
            rs = h.niveles[nivel]
            for r in rs + [r for r in rs if r['brilla']]:
                for p, n, (u, v) in _vertices(h, r, ancho, alto):
                    q = np.round(p * 128).astype(int)
                    assert np.all(np.abs(q) < 32767), (h.nombre, p)
                    nn = np.clip(np.round(n * 127), -127, 127).astype(int)
                    cuerpo += struct.pack('>3h3b2H', *q, *nn, int(round(u * 64)), int(round(v * 64)))
    with gzip.open(ruta, 'wb', compresslevel=9) as fh:
        fh.write(bytes(cab + cuerpo))


# ----------------------------------------------------------------------
#  Para las pruebas y las animaciones: las matrices de las piezas como en el juego
# ----------------------------------------------------------------------
def matrices(hs, pose=None):
    """La matriz de cada pieza (pixeles del modelo) con una pose que SE SUMA al reposo, como las animaciones del juego
    (rot en grados, pos en pixeles con Y hacia abajo, esc multiplicador)."""
    pose = pose or {}
    M = []
    for h in hs:
        ex = pose.get(h.nombre, {})
        r = h.rot + np.array(ex.get('rot', (0, 0, 0)), float)
        p = h.pivote + np.array(ex.get('pos', (0, 0, 0)), float)
        s = ex.get('esc', (1, 1, 1))
        L = vr.T(*p) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R) @ np.diag([s[0], s[1], s[2], 1])
        M.append(L if h.padre < 0 else M[h.padre] @ L)
    return M


def punto(hs, pose, pieza, local=(0, 0, 0)):
    """Un punto de una pieza (en sus voxeles sin escalar) en pixeles del modelo."""
    M = matrices(hs, pose)
    h = hs[_idx(hs, pieza)]
    q = M[_idx(hs, pieza)] @ np.array([*(np.array(local, float) * h.esc), 1.0])
    return q[:3]


def a_bloques(p, escala):
    """Pixeles del modelo -> bloques en el espacio del cuerpo (x a SU izquierda, y arriba desde los pies, z adelante),
    con la escala del mini jefe."""
    x, y, z = p
    return (x / 16.0 * escala, (24.0 - y) / 16.0 * escala, -z / 16.0 * escala)


LUCES = [((-0.5, 0.8, -0.6), (1.0, 0.97, 0.9), 0.85, 'llave'), ((0.6, 0.4, 0.7), (0.55, 0.7, 1.0), 0.45, 'contra')]


def dibujar(lz, cam, hs, M, ancho, alto, base, brillo, escala, guinada=0.0, x=0.0, y=0.0, z=0.0, luces=LUCES,
            ambiente=(0.42, 0.42, 0.46), nivel=0):
    """La malla tal cual la pinta el juego (con la luz de cada rectangulo plana: es una prueba)."""
    W = vr.entidad_a_mundo(x, y, z, guinada, escala)
    bf = base.astype(np.uint8)
    for i, h in enumerate(hs):
        if not h.niveles[nivel]:
            continue
        Mw = W @ M[i]
        for r in h.niveles[nivel]:
            vs = _vertices(h, r, ancho, alto)
            P = [(Mw @ np.array([*p, 1.0]))[:3] for p, _, _ in vs]
            n = (Mw[:3, :3] @ np.mean([nn for _, nn, _ in vs], axis=0))
            n /= np.linalg.norm(n) or 1.0
            UV = [(u / ancho, v / alto) for _, _, (u, v) in vs]
            luz = vr.iluminar(n, cam, np.mean(P, axis=0), luces, ambiente)
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [P[k] for k in tri], [UV[k] for k in tri], bf, luz, brillo if r['brilla'] else None)


def foto(hs, ancho, alto, base, brillo, nombre, pose=None, guinada=-25, W=520, H=600, ojo=None, objetivo=None, nivel=0):
    esc = mj.ESCALA[nombre]
    cam = vr.Camara(ojo=ojo or (-3.5, 3.4 * esc, -9.5 * esc), objetivo=objetivo or (0, 2.4 * esc, 0), fov=50, ancho=W, alto=H)
    lz = vr.Lienzo(W, H)
    dibujar(lz, cam, hs, matrices(hs, pose), ancho, alto, base, brillo, esc, guinada, nivel=nivel)
    col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.9, 0.91, 0.93]) * (1 - a)
    return Image.fromarray((arr * 255).astype(np.uint8))


# ----------------------------------------------------------------------
if __name__ == '__main__':
    solo = sys.argv[3].split(',') if len(sys.argv) > 3 else list(mj.MINIJEFES)
    DATOS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/minijefes')
    TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/minijefes')
    os.makedirs(DATOS, exist_ok=True)
    os.makedirs(TEX, exist_ok=True)
    for nombre in solo:
        hs, ancho, alto, base, brillo = malla(nombre)
        Image.fromarray(base).save(os.path.join(TEX, f'{nombre}.png'))
        Image.fromarray(brillo).save(os.path.join(TEX, f'{nombre}_brillo.png'))
        Image.fromarray(mascara(nombre, hs, ancho, alto)).save(os.path.join(TEX, f'{nombre}_disolver.png'))
        escribir(nombre, hs, ancho, alto, os.path.join(DATOS, f'{nombre}.malla'))
        nq = '/'.join(str(sum(len(h.niveles[k]) for h in hs)) for k in range(len(NIVELES)))
        nb = '/'.join(str(sum(sum(1 for r in h.niveles[k] if r['brilla']) for h in hs)) for k in range(len(NIVELES)))
        print(f'{nombre}: {len(hs)} piezas, {nq} cuadrilateros por nivel (+{nb} que brillan), atlas {ancho}x{alto}, '
              f'{os.path.getsize(os.path.join(DATOS, nombre + ".malla")) // 1024} KB', flush=True)
        if PRUEBAS:
            os.makedirs(PRUEBAS, exist_ok=True)
            fotos = [foto(hs, ancho, alto, base, brillo, nombre, guinada=g) for g in (-25, 155)]
            fotos += [foto(hs, ancho, alto, base, brillo, nombre, nivel=k) for k in range(1, len(NIVELES))]
            hoja = Image.new('RGB', (sum(f.width for f in fotos), fotos[0].height))
            for i, f in enumerate(fotos):
                hoja.paste(f, (i * f.width, 0))
            hoja.save(os.path.join(PRUEBAS, f'malla_{nombre}.jpg'), quality=90)

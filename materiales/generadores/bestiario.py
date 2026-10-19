"""
El bestiario (18-10-2026): la herramienta con la que se hacen los mobs nuevos del menú de los mobs (los del DEDsafío 2,
3 y 4, con nuestro diseño). Juan: «haz todos los mobs con su misma funcionalidad pero con un diseño diferente mucho
mejor, hazlo con calma cada diseño y mecánica, sonidos, etc.».

Cada mob se escribe en su script (bestiario_<familia>.py) con esto:

  Modelo          las partes que se mueven (cada una con su marco) y sus cajas (cada caja con su marco: una caja de
                  ModelPart no se gira sola, así que cada una va en su propia pieza, como en el Fogonazo y el Coco)
  pintores        los materiales: una paleta de cinco tonos y un dibujo limpio (escamas en U, placas en bandas,
                  manchas de borde limpio, pelo en trazos, quitina con su brillo...), sin ruido ni motas sueltas
  Anim            las animaciones en keyframes (las de vanilla: AnimationDefinition), en los ejes del boceto
  exportar        assets/atalaya/bestiario/<id>.json (lo lee BestiaDatos en el mod), su textura y la de lo que brilla
  vista           la malla del juego con su textura, de vuelta al boceto, en una foto (para revisar sin abrir el juego)
  huevo, retrato  el huevo generador (16 x 16) y el retrato del menú (32 x 32)
  particula       los sprites de sus partículas

El boceto: Y arriba, el frente en +Z y la unidad el píxel de Minecraft (16 por bloque); los pies en y = 0. En el juego
(ModelPart): Y abajo desde la altura 24 y el frente en -Z (C = diag(1, -1, -1)).
"""
import collections
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr  # noqa: E402

RAIZ = '../..'
ASSETS = 'src/main/resources/assets/atalaya'
# El tamaño del píxel de la textura, en píxeles del modelo (None: como lo pintan los pintores). Con el modelo al
# doble y la escala 0,55, un píxel de 2 es el de Minecraft (16 por bloque): Juan, 18-10-2026, «en mc ya hay un
# determinado tamaño para un píxel».
TEXEL = None
C = np.diag([1.0, -1.0, -1.0, 1.0])
A = vr.T(0.0, 24.0, 0.0) @ C
T, Rx, Ry, Rz = vr.T, vr.Rx, vr.Ry, vr.Rz
CARAS = ('frente', 'atras', 'der', 'izq', 'arriba', 'abajo')
D = math.pi / 180.0


def ruta(*partes):
    return os.path.join(RAIZ, *partes)


# ======================================================================================================================
#  Colores y pintores
# ======================================================================================================================
def H(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), float)


def rampa(*colores):
    return np.array([H(c) for c in colores], float)


class Pintor:
    """Un material: pinta una cara de tw x th píxeles y devuelve (rgba, brillo o None). El nombre dice si dos cajas
    pueden compartir el mismo trozo de textura."""

    def __init__(self, nombre, fn, pleno=False):
        self.nombre, self.fn, self.pleno = nombre, fn, pleno
        self.nativo = 1          # píxeles de la textura por cada píxel que pinta (2 en los de 16 por bloque)

    def __call__(self, tw, th, cara, semilla):
        tex, emis = self.fn(tw, th, cara, semilla)
        if self.pleno:
            emis = tex.copy()
        return tex, emis


def _img(idx, r, alfa=None):
    idx = np.clip(np.asarray(idx), 0, len(r) - 1).astype(int)
    out = np.zeros(idx.shape + (4,), np.uint8)
    out[..., :3] = np.clip(np.round(r[idx]), 0, 255)
    out[..., 3] = 255 if alfa is None else alfa
    return out


def _malla(tw, th):
    ys, xs = np.mgrid[0:th, 0:tw]
    return xs, ys


def _bisel(idx, tw, th, cara, claro=1, oscuro=1):
    """La luz de los cantos: la fila de arriba un tono más clara y la de abajo más oscura (en las caras de lado)."""
    if cara in ('arriba', 'abajo') or th < 3:
        return idx
    idx = idx.copy()
    idx[0, :] += claro
    idx[th - 1, :] -= oscuro
    return idx


def _azar(semilla):
    return np.random.default_rng(int(semilla) * 7919 + 17)


def liso(nombre, r, base=2):
    """Liso: el tono base con el bisel de los cantos; arriba más claro, abajo más oscuro."""
    def fn(tw, th, cara, s):
        idx = np.full((th, tw), base)
        if cara == 'arriba':
            idx[...] = base + 1
        elif cara == 'abajo':
            idx[...] = base - 1
        return _img(_bisel(idx, tw, th, cara), r), None
    return Pintor(nombre, fn)


def escamas(nombre, r, tam=4, base=2):
    """Escamas en U: filas desplazadas, cada escama con su arco claro arriba y su borde oscuro abajo."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        fila = ys // tam
        x = xs + (fila % 2) * (tam // 2)
        cx = (x % tam) - (tam - 1) / 2
        cy = (ys % tam)
        idx = np.full((th, tw), base)
        borde = (cy == tam - 1) | ((np.abs(cx) > tam / 2 - 0.6) & (cy > tam / 2))
        idx[borde] = base - 1
        idx[(cy == 0) & (np.abs(cx) < tam / 2 - 0.6)] = base + 1
        if cara == 'arriba':
            idx += 1
        if cara == 'abajo':
            idx -= 1
        return _img(idx, r), None
    return Pintor(nombre, fn)


def placas(nombre, r, alto=4, base=2, vertical=False):
    """Placas en bandas: cada banda con su canto claro y su junta oscura (vertical: bandas de lado a lado)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        c = xs if vertical else ys
        idx = np.full((th, tw), base)
        idx[(c % alto) == 0] = base + 1
        idx[(c % alto) == alto - 1] = base - 1
        if cara == 'arriba':
            idx += 1
        return _img(idx, r), None
    return Pintor(nombre, fn)


def anillos(nombre, r, paso=3, base=2):
    """Segmentos a lo largo (patas, colas, antenas): una junta oscura cada pocos píxeles."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        idx = np.full((th, tw), base)
        if cara in ('arriba', 'abajo'):
            idx[...] = base + (1 if cara == 'arriba' else -1)
        else:
            idx[(ys % paso) == paso - 1] = base - 1
            idx[:, 0] = np.minimum(idx[:, 0] + 1, len(r) - 1)
        return _img(idx, r), None
    return Pintor(nombre, fn)


def manchas(nombre, r, r2, cuantas=0.025, radio=(1.5, 3.2), base=2):
    """Manchas grandes de borde limpio (círculos de otro tono, fijos por caja)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        g = _azar(s + tw * 31 + th * 7 + hash(cara) % 97)
        idx = np.full((th, tw), base)
        if cara == 'arriba':
            idx[...] = base + 1
        n = max(1, int(tw * th * cuantas))
        mancha = np.zeros((th, tw), bool)
        for _ in range(n):
            cx, cy = g.uniform(0, tw), g.uniform(0, th)
            rr = g.uniform(*radio)
            mancha |= (xs - cx) ** 2 + ((ys - cy) * 1.15) ** 2 < rr * rr
        tex = _img(_bisel(idx, tw, th, cara), r)
        t2 = _img(np.where(cara == 'arriba', 3, 2) * np.ones((th, tw), int), r2)
        tex[mancha] = t2[mancha]
        return tex, None
    return Pintor(nombre, fn)


def pelaje(nombre, r, base=2, largo=3):
    """Pelo en trazos: rayas cortas de un tono más claro y más oscuro, en filas desplazadas (nada de ruido)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        idx = np.full((th, tw), base)
        fila = ys // largo
        col = (xs + fila * 2) % 4
        idx[(col == 0) & ((ys % largo) < largo - 1)] = base + 1
        idx[(col == 2) & ((ys % largo) == largo - 1)] = base - 1
        if cara == 'arriba':
            idx += 1
        elif cara == 'abajo':
            idx -= 1
        return _img(_bisel(idx, tw, th, cara, 0, 1), r), None
    return Pintor(nombre, fn)


def quitina(nombre, r, base=2):
    """Quitina: lisa y oscura, con una veta de brillo en diagonal y los cantos más oscuros."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        idx = np.full((th, tw), base)
        diag = (xs + ys * 0.8) % max(6, tw)
        idx[(diag >= 1) & (diag < 2)] = base + 2
        idx[(diag >= 2) & (diag < 3)] = base + 1
        idx[:, 0] -= 1
        idx[:, tw - 1] -= 1
        if cara == 'abajo':
            idx -= 1
        return _img(_bisel(idx, tw, th, cara, 1, 1), r), None
    return Pintor(nombre, fn)


def hueso(nombre, r, base=3):
    """Hueso: claro, con dos o tres grietas finas y el canto más oscuro."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        g = _azar(s + tw + th * 3)
        idx = np.full((th, tw), base)
        for _ in range(max(1, (tw * th) // 60)):
            x0, y0 = g.integers(0, tw), g.integers(0, th)
            for k in range(g.integers(2, 5)):
                x, y = x0 + k, y0 + (k * g.integers(0, 2))
                if 0 <= x < tw and 0 <= y < th:
                    idx[y, x] = base - 2
        return _img(_bisel(idx, tw, th, cara), r), None
    return Pintor(nombre, fn)


def metal(nombre, r, panel=8, base=2):
    """Metal: paneles con su junta y un remache de 2 x 2 en cada esquina."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        idx = np.full((th, tw), base)
        idx[(xs % panel) == 0] = base - 1
        idx[(ys % panel) == 0] = base - 1
        remache = ((xs % panel) in (2, 3)) if False else (((xs % panel) >= 2) & ((xs % panel) <= 3) & ((ys % panel) >= 2) & ((ys % panel) <= 3))
        idx[remache] = base + 2
        if cara == 'arriba':
            idx += 1
        return _img(_bisel(idx, tw, th, cara), r), None
    return Pintor(nombre, fn)


def piedra(nombre, r, base=2, celda=5):
    """Piedra en losas: losas irregulares con su junta oscura y el canto de arriba claro."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        g = _azar(s + 99)
        n = max(2, (tw * th) // (celda * celda))
        cx = g.uniform(0, tw, n)
        cy = g.uniform(0, th, n)
        d = (xs[..., None] - cx) ** 2 + (ys[..., None] - cy) ** 2
        orden = np.sort(d, axis=-1)
        junta = (np.sqrt(orden[..., 1]) - np.sqrt(orden[..., 0])) < 0.9
        tono = (np.argmin(d, axis=-1) % 2)
        idx = np.full((th, tw), base) + tono * 0
        idx[tono == 1] = base + 1 if cara == 'arriba' else base
        idx[junta] = base - 1
        return _img(_bisel(idx, tw, th, cara), r), None
    return Pintor(nombre, fn)


def pluma(nombre, r, base=2, alto=5):
    """Plumas: filas de puntas en V hacia abajo, cada una con su raquis claro."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        fila = ys // alto
        x = (xs + (fila % 2) * 2) % 4
        y = ys % alto
        idx = np.full((th, tw), base)
        idx[x == 0] = base + 1
        idx[(y == alto - 1) & (x != 0)] = base - 1
        return _img(_bisel(idx, tw, th, cara), r), None
    return Pintor(nombre, fn)


def membrana(nombre, r, borde=None, base=1):
    """Una membrana (alas, aletas): oscura en bandas, con el borde libre (la fila de abajo) encendido si se pide."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        idx = np.full((th, tw), base)
        idx[(xs % 5) == 0] = base + 1
        tex = _img(idx, r)
        emis = None
        if borde is not None:
            m = ys >= th - 1
            tex[m, :3] = borde
            emis = np.zeros_like(tex)
            emis[m] = tex[m]
        return tex, emis
    return Pintor(nombre, fn)


def luz(nombre, r):
    """Lo que brilla: en escalones del borde (el neón) al centro (casi blanco), sin degradado suave."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        return _img(np.clip(1 + d, 1, len(r) - 1), r), None
    return Pintor(nombre, fn, pleno=True)


def ojo(nombre, iris, pupila='0a0606', ranura=True):
    """Un ojo que brilla: el iris en escalones y la pupila (una raja vertical o un punto) oscura."""
    p = H(pupila)

    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        tex = _img(np.clip(1 + d, 1, len(iris) - 1), iris)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        if ranura:
            m = (np.abs(xs - cx) < max(0.6, tw * 0.12)) & (np.abs(ys - cy) < th * 0.42)
        else:
            m = (np.abs(xs - cx) < max(0.6, tw * 0.2)) & (np.abs(ys - cy) < max(0.6, th * 0.2))
        tex[m, :3] = p
        emis = tex.copy()
        emis[m] = 0
        return tex, emis
    return Pintor(nombre, fn)


def boca(nombre, r_boca, neon):
    """Dentro de la boca: oscuro con escalones de luz hacia el fondo (el neón de la garganta)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        idx = np.clip(d, 0, len(r_boca) - 1)
        tex = _img(idx, r_boca)
        centro = d >= max(1, min(tw, th) // 3)
        tex[centro, :3] = neon
        emis = np.zeros_like(tex)
        emis[centro] = tex[centro]
        return tex, emis
    return Pintor(nombre, fn)


def diente(nombre, r=None):
    """Un diente (en una hoja): blanco hueso, la base más oscura."""
    r = r if r is not None else rampa('6a6250', 'a89c80', 'd8ccb0', 'f2ead8', 'fffcf2')

    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        idx = np.full((th, tw), 3)
        idx[ys < max(1, th // 4)] = 2
        idx[:, tw - 1] = 2
        return _img(idx, r), None
    return Pintor(nombre, fn)


def brizna(nombre, r, ancho_base=1.0):
    """Una brizna (o una hoja larga) en una hoja del modelo: puntiaguda (lo de fuera, transparente) y con el nervio
    claro en medio."""
    def fn(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        u = (xs + 0.5) / tw
        v = (ys + 0.5) / th
        dentro = np.abs(u - 0.5) < 0.5 * ancho_base * (0.15 + 0.85 * v)
        idx = np.where(np.abs(u - 0.5) < 0.12, 4, np.where(u < 0.5, 3, 2))
        idx = np.where(v > 0.85, 1, idx)
        tex = _img(idx, r)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return Pintor(nombre, fn)


def petalo(nombre, r):
    """Una flor de cuatro pétalos redondos en una hoja (lo de fuera, transparente), el centro más oscuro."""
    def fn(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        u = (xs + 0.5) / tw - 0.5
        v = (ys + 0.5) / th - 0.5
        a = np.arctan2(v, u)
        rr = np.hypot(u, v)
        dentro = rr < 0.22 + 0.26 * np.abs(np.cos(2 * a))
        idx = np.where(rr < 0.14, 1, np.where(rr < 0.3, 3, 2))
        tex = _img(idx, r)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return Pintor(nombre, fn)


def grietas(tw, th, s, cara='frente', cuantas=None, largo=None, giro=0.35, ramas=0.06):
    """Líneas quebradas y continuas (grietas, venas, raíces): cada una avanza de píxel en píxel torciendo un poco
    (giro) y a veces echa un ramal; nada de motas sueltas. Devuelve la máscara (th x tw)."""
    g = _azar(s * 13 + CARAS.index(cara) * 101 + tw * 7 + th)
    m = np.zeros((th, tw), bool)
    cuantas = cuantas if cuantas is not None else max(1, (tw * th) // 90)
    pendientes = []
    for _ in range(cuantas):
        pendientes.append((g.uniform(0, tw), g.uniform(0, th), g.uniform(0, math.tau),
                           largo or int(g.integers(max(4, min(tw, th) // 2), max(6, max(tw, th)) + 1))))
    while pendientes:
        x, y, ang, L = pendientes.pop()
        for _ in range(L):
            xi, yi = int(round(x)), int(round(y))
            if not (0 <= xi < tw and 0 <= yi < th):
                break
            m[yi, xi] = True
            ang += g.normal(0, giro)
            x, y = x + math.cos(ang), y + math.sin(ang)
            if g.random() < ramas and L > 4:
                pendientes.append((x, y, ang + g.choice((-1, 1)) * g.uniform(0.6, 1.2), max(2, L // 3)))
    return m


def vecinos(m):
    """Los píxeles que tocan a los de la máscara (sin contarlos): el halo de una grieta, el borde de una mancha."""
    v = np.zeros_like(m)
    v[1:, :] |= m[:-1, :]
    v[:-1, :] |= m[1:, :]
    v[:, 1:] |= m[:, :-1]
    v[:, :-1] |= m[:, 1:]
    return v & ~m


def trazo(nombre, fn_idx, r, brilla=None):
    """Un pintor a medida: fn_idx(xs, ys, tw, th, cara, s) -> índices de la rampa (y, si brilla, la máscara)."""
    def fn(tw, th, cara, s):
        xs, ys = _malla(tw, th)
        res = fn_idx(xs, ys, tw, th, cara, s)
        if isinstance(res, tuple):
            idx, mascara = res
        else:
            idx, mascara = res, None
        tex = _img(idx, r)
        emis = None
        if mascara is not None and np.any(mascara):
            emis = np.zeros_like(tex)
            emis[mascara] = tex[mascara]
        return tex, emis
    return Pintor(nombre, fn)


# ======================================================================================================================
#  El modelo
# ======================================================================================================================
def _u(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def euler_zyx(R):
    """(x, y, z) en radianes con R = Rz(z) Ry(y) Rx(x), como ModelPart."""
    sy = max(-1.0, min(1.0, -R[2, 0]))
    y = math.asin(sy)
    if abs(math.cos(y)) > 1e-6:
        x = math.atan2(R[2, 1], R[2, 2])
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        z = 0.0
    return x, y, z


def girar(rot):
    """La matriz de un giro en grados (x, y, z), en el orden de ModelPart (Z·Y·X)."""
    rx, ry, rz = (a * D for a in rot)
    return Rz(rz) @ Ry(ry) @ Rx(rx)


class Parte:
    def __init__(self, nombre, padre, marco):
        self.nombre, self.padre, self.marco = nombre, padre, np.asarray(marco, float)
        self.cajas = []


def _a_tamano(a, th, tw):
    """Recorta o alarga (repitiendo el borde) a th x tw."""
    a = a[:th, :tw]
    if a.shape[0] < th:
        a = np.concatenate([a, np.repeat(a[-1:], th - a.shape[0], 0)], 0)
    if a.shape[1] < tw:
        a = np.concatenate([a, np.repeat(a[:, -1:], tw - a.shape[1], 1)], 1)
    return a


class Modelo:
    """Un mob en piezas. Todo en coordenadas del boceto (absolutas): Y arriba, el frente en +Z, píxeles de Minecraft."""

    def __init__(self, ident, K=2, ancho=128):
        self.id = ident
        self.K = K
        self.ancho = ancho
        self.partes = collections.OrderedDict()
        self.anims = collections.OrderedDict()
        self.mira = []
        self.escala = 1.0
        self.paso = 2.0
        self.semilla = 1
        self.texel = TEXEL

    # ------------------------------------------------------------------
    #  Las partes y las cajas
    # ------------------------------------------------------------------
    def parte(self, nombre, padre=None, pivote=(0, 0, 0), rot=(0, 0, 0)):
        """Una parte que se mueve: su pivote (donde gira) y su giro de reposo, en el boceto."""
        assert nombre not in self.partes, nombre
        self.partes[nombre] = Parte(nombre, padre, T(*pivote) @ girar(rot))
        return nombre

    def _caja(self, parte, M, x0, y0, z0, w, h, d, pint, caras=None):
        if isinstance(pint, dict):
            caras, pint = pint, None
        pc = {c: (caras or {}).get(c, pint) for c in CARAS}
        self.semilla += 1
        self.partes[parte].cajas.append((np.asarray(M, float), x0, y0, z0, w, h, d, pc, self.semilla))

    def caja(self, parte, centro, tam, pint, rot=(0, 0, 0), caras=None):
        """Una caja centrada en ese punto del boceto, con su giro (grados) alrededor de su centro."""
        w, h, d = tam
        self._caja(parte, T(*centro) @ girar(rot), -w / 2, -h / 2, -d / 2, w, h, d, pint, caras)

    def caja_desde(self, parte, base, tam, pint, rot=(0, 0, 0), caras=None):
        """Una caja que crece hacia arriba desde ese punto (el centro de su cara de abajo), con su giro."""
        w, h, d = tam
        self._caja(parte, T(*base) @ girar(rot), -w / 2, 0.0, -d / 2, w, h, d, pint, caras)

    def viga(self, parte, a, b, grueso, pint, ancho=None, caras=None, extra=0.0, rodar=0.0):
        """Una caja de a a b (su eje largo de un punto al otro), de ese grueso (y ancho)."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        eje = _u(b - a)
        largo = float(np.linalg.norm(b - a)) + extra
        ref = np.array((0.0, 0.0, 1.0)) if abs(eje[2]) < 0.9 else np.array((1.0, 0.0, 0.0))
        x = _u(np.cross(eje, ref))
        z = np.cross(x, eje)
        M = np.eye(4)
        M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, eje, z, (a + b) / 2
        if rodar:
            M = M @ Ry(rodar * D)
        w = ancho if ancho is not None else grueso
        self._caja(parte, M, -w / 2, -largo / 2, -grueso / 2, w, largo, grueso, pint, caras)

    def hoja(self, parte, centro, ancho, alto, pint, rot=(0, 0, 0), dos_caras=True):
        """Una hoja sin grosor (un diente, una membrana, una aleta): solo las caras de delante y de detrás."""
        caras = {c: (pint if c in ('frente', 'atras') and (dos_caras or c == 'frente') else None) for c in CARAS}
        self._caja(parte, T(*centro) @ girar(rot), -ancho / 2, -alto / 2, 0.0, ancho, alto, 0.0, None, caras)

    def ovalo(self, parte, centro, radios, pint, rot=(0, 0, 0), capas=3, caras=None):
        """Un cuerpo redondeado sin que se vean los escalones: tres cajas cruzadas (la del medio, la más larga)."""
        rx, ry, rz = radios
        M = T(*centro) @ girar(rot)
        for k in range(capas):
            f = 1.0 - 0.18 * k
            g = 0.62 + 0.19 * k
            self._caja(parte, M, -rx * f, -ry * g, -rz * f, 2 * rx * f, 2 * ry * g, 2 * rz * f, pint, caras)
            self._caja(parte, M, -rx * g, -ry * f, -rz * g, 2 * rx * g, 2 * ry * f, 2 * rz * g, pint, caras)

    def esfera(self, parte, centro, r, pintor_de, cortes=None):
        """Una bola sin que se vean los escalones: rebanadas horizontales del ancho del círculo a su altura, cada una con
        dos cajas cruzadas (octogonal vista desde arriba). pintor_de(k, n) da el pintor de la rebanada k de n (0, la de
        abajo), para que la luz baje de arriba a abajo como en una bola."""
        cx, cy, cz = centro
        n = cortes or max(5, int(round(r * 1.4)) | 1)
        h = 2.0 * r / n
        for k in range(n):
            y = -r + h * (k + 0.5)
            w = math.sqrt(max(0.0, r * r - y * y)) * 1.03
            p = pintor_de(k, n)
            self.caja(parte, (cx, cy + y, cz), (2 * w, h + 0.02, 2 * w * 0.74), p)
            self.caja(parte, (cx, cy + y, cz), (2 * w * 0.74, h + 0.02, 2 * w), p)
        return n

    def dientes(self, parte, a, b, cuantos, largo, hacia, pint, ancho=None):
        """Una hilera de dientes (hojas) de a a b, que apuntan hacia 'hacia' (un vector del boceto)."""
        a, b = np.asarray(a, float), np.asarray(b, float)
        hacia = _u(hacia)
        paso = (b - a) / max(1, cuantos - 1)
        ancho = ancho or max(0.6, float(np.linalg.norm(b - a)) / max(1, cuantos) * 0.8)
        lado = _u(b - a)
        z = _u(np.cross(lado, hacia))
        for i in range(cuantos):
            base = a + paso * i
            M = np.eye(4)
            M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = lado, hacia, z, base
            caras = {c: (pint if c in ('frente', 'atras') else None) for c in CARAS}
            l = largo * (1.0 if i in (0, cuantos - 1) else 0.75)
            self._caja(parte, M, -ancho / 2, 0.0, 0.0, ancho, l, 0.0, None, caras)

    # ------------------------------------------------------------------
    #  Lo que mira y las animaciones
    # ------------------------------------------------------------------
    def mirar(self, *pares):
        """Las partes que siguen la mirada y cuánto: mirar(('cabeza', 0.8), ('cuello', 0.3))."""
        self.mira = [list(p) for p in pares]

    def anim(self, nombre, largo, bucle=False):
        a = Anim(self, nombre, largo, bucle)
        self.anims[nombre] = a
        return a

    # ------------------------------------------------------------------
    #  A Minecraft
    # ------------------------------------------------------------------
    def local_mc(self, nombre):
        p = self.partes[nombre]
        if p.padre is None:
            return A @ p.marco @ C
        return C @ np.linalg.inv(self.partes[p.padre].marco) @ p.marco @ C

    def caja_mc(self, p, caja):
        M, x0, y0, z0, w, h, d = caja[:7]
        B = C @ np.linalg.inv(p.marco) @ M @ C
        return B, (x0, -(y0 + h), -(z0 + d), w, h, d)

    @staticmethod
    def pose(L):
        x, y, z = euler_zyx(L[:3, :3])
        return tuple(float(v) for v in L[:3, 3]), (x, y, z)

    def _clave(self, caja):
        w, h, d, pc, s = caja[4], caja[5], caja[6], caja[7], caja[8]
        nombres = tuple(pc[c].nombre if pc[c] else '-' for c in CARAS)
        return (round(w, 2), round(h, 2), round(d, 2), nombres)

    @staticmethod
    def _tam(caja):
        w, h, d = caja[4], caja[5], caja[6]
        return int(math.ceil(2 * (d + w))) + 1, int(math.ceil(d + h)) + 1

    def empaquetar(self):
        unicas = collections.OrderedDict()
        for p in self.partes.values():
            for c in p.cajas:
                unicas.setdefault(self._clave(c), c)
        orden = sorted(unicas, key=lambda k: (-self._tam(unicas[k])[1], -self._tam(unicas[k])[0]))
        uv, x, y, fila = {}, 0, 0, 0
        for k in orden:
            w, h = self._tam(unicas[k])
            assert w <= self.ancho, ('caja demasiado ancha para la textura', k, w)
            if x + w > self.ancho:
                x, y, fila = 0, y + fila, 0
            uv[k] = (x, y)
            x += w
            fila = max(fila, h)
        alto = 1 << max(4, (y + fila - 1).bit_length())
        return uv, alto, unicas

    @staticmethod
    def huecos(u, v, w, h, d):
        return {'arriba': (u + d, v, w, d), 'abajo': (u + d + w, v, w, d), 'izq': (u, v + d, d, h),
                'frente': (u + d, v + d, w, h), 'der': (u + d + w, v + d, d, h), 'atras': (u + 2 * d + w, v + d, w, h)}

    def pintar_cara(self, f, tw, th, cara, s):
        """Una cara de tw x th píxeles de la textura. Con 'texel', el pintor pinta de verdad con píxeles de ese tamaño
        (en píxeles del modelo): cada píxel, un color suyo, como los de Minecraft; luego se agranda."""
        P = int(round(self.texel * self.K)) if self.texel else 1         # píxeles de la textura por píxel
        if P <= f.nativo:
            return f(tw, th, cara, s)
        n, m = max(1, -(-tw // P)), max(1, -(-th // P))                  # los píxeles de la cara (el último, partido)
        tex, emis = f(n * f.nativo, m * f.nativo, cara, s)
        k = P // f.nativo
        tex = _a_tamano(np.repeat(np.repeat(tex, k, 0), k, 1), th, tw)
        if emis is not None:
            emis = _a_tamano(np.repeat(np.repeat(emis, k, 0), k, 1), th, tw)
        return tex, emis

    def pintar(self, uv, alto, unicas):
        K = self.K
        base = np.zeros((alto * K, self.ancho * K, 4), np.uint8)
        brillo = np.zeros_like(base)
        hay_brillo = False
        tam_cara = {'frente': lambda w, h, d: (w, h), 'atras': lambda w, h, d: (w, h), 'der': lambda w, h, d: (d, h),
                    'izq': lambda w, h, d: (d, h), 'arriba': lambda w, h, d: (w, d), 'abajo': lambda w, h, d: (w, d)}
        for k, caja in unicas.items():
            u, v = uv[k]
            w, h, d, pc, s = caja[4], caja[5], caja[6], caja[7], caja[8]
            for cara, (fx, fy, fw, fh) in self.huecos(u, v, w, h, d).items():
                f = pc[cara]
                if f is None or fw <= 0 or fh <= 0:
                    continue
                X0, Y0 = int(round(fx * K)), int(round(fy * K))
                X1, Y1 = max(X0 + 1, int(round((fx + fw) * K))), max(Y0 + 1, int(round((fy + fh) * K)))
                tw, th = X1 - X0, Y1 - Y0
                tex, emis = self.pintar_cara(f, tw, th, cara, s)
                if cara == 'abajo':
                    tex = tex[::-1]
                    emis = emis[::-1] if emis is not None else None
                base[Y0:Y1, X0:X1] = tex
                if emis is not None and np.any(emis[..., 3]):
                    hay_brillo = True
                    a = emis[..., 3:4] / 255.0
                    brillo[Y0:Y1, X0:X1, :3] = np.maximum(brillo[Y0:Y1, X0:X1, :3], (emis[..., :3] * a).astype(np.uint8))
                    brillo[Y0:Y1, X0:X1, 3] = np.maximum(brillo[Y0:Y1, X0:X1, 3], (a[..., 0] > 0) * 255)
        return base, (brillo if hay_brillo else None)

    def datos(self, uv, alto, brillo):
        partes = []
        for n, p in self.partes.items():
            (px, py, pz), (rx, ry, rz) = self.pose(self.local_mc(n))
            cajas = []
            for caja in p.cajas:
                B, (x0, y0, z0, w, h, d) = self.caja_mc(p, caja)
                (bx, by, bz), (ax, ay, az) = self.pose(B)
                u, v = uv[self._clave(caja)]
                cajas.append([u, v] + [round(float(q), 4) for q in (x0, y0, z0, w, h, d, bx, by, bz)]
                             + [round(float(q) / D, 3) for q in (ax, ay, az)])
            partes.append({'n': n, 'p': p.padre, 'o': [round(q, 4) for q in (px, py, pz)],
                           'r': [round(q / D, 3) for q in (rx, ry, rz)], 'c': cajas})
        return {'textura': [self.ancho, alto], 'escala': self.escala, 'brillo': brillo is not None, 'paso': self.paso,
                'translucido': bool(getattr(self, 'translucido', False)), 'mira': self.mira, 'partes': partes,
                'anim': {n: a.json() for n, a in self.anims.items()}}

    def exportar(self, raiz=None, variantes=None):
        """Escribe el json de la malla y las animaciones, su textura y la de lo que brilla. variantes: una lista de
        funciones que cambian los pintores (para las texturas _1, _2...)."""
        global RAIZ
        if raiz:
            RAIZ = raiz
        uv, alto, unicas = self.empaquetar()
        base, brillo = self.pintar(uv, alto, unicas)
        carpeta = ruta(ASSETS, 'textures/entity/bestiario')
        os.makedirs(carpeta, exist_ok=True)
        if getattr(self, 'translucido', False):
            # Dos pasadas, como el slime: lo opaco en la textura de siempre (lo translúcido, vacío) y lo translúcido
            # (el gel) en la _gel, que el render pinta encima.
            semi = (base[..., 3] > 0) & (base[..., 3] < 255)
            gel = np.zeros_like(base)
            gel[semi] = base[semi]
            Image.fromarray(gel).save(os.path.join(carpeta, f'{self.id}_gel.png'))
            opaco = base.copy()
            opaco[semi, 3] = 0
            Image.fromarray(opaco).save(os.path.join(carpeta, f'{self.id}.png'))
        else:
            Image.fromarray(base).save(os.path.join(carpeta, f'{self.id}.png'))
        if brillo is not None:
            Image.fromarray(brillo).save(os.path.join(carpeta, f'{self.id}_brillo.png'))
        d = self.datos(uv, alto, brillo)
        if variantes:
            d['variantes'] = 1 + len(variantes)
        os.makedirs(ruta(ASSETS, 'bestiario'), exist_ok=True)
        with open(ruta(ASSETS, f'bestiario/{self.id}.json'), 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(d, fh, separators=(',', ':'))
        n = sum(len(p.cajas) for p in self.partes.values())
        print(f'{self.id}: {len(self.partes)} partes, {n} cajas ({len(unicas)} distintas), textura {self.ancho}x{alto} '
              f'(x{self.K}), {len(self.anims)} animaciones')
        self._uv, self._alto, self._base, self._brillo = uv, alto, base, brillo
        return uv, alto, base, brillo

    def textura_variante(self, nombre_archivo, cambio):
        """Otra textura con los pintores cambiados por cambio(pintor) -> pintor (las variantes de color)."""
        uv, alto, unicas = self._uv, self._alto, None
        unicas = collections.OrderedDict()
        for p in self.partes.values():
            for c in p.cajas:
                unicas.setdefault(self._clave(c), c)
        cambiadas = collections.OrderedDict()
        for k, c in unicas.items():
            pc = {cara: (cambio(f) if f else None) for cara, f in c[7].items()}
            cambiadas[k] = c[:7] + (pc, c[8])
        base, brillo = self.pintar(uv, alto, cambiadas)
        carpeta = ruta(ASSETS, 'textures/entity/bestiario')
        Image.fromarray(base).save(os.path.join(carpeta, f'{nombre_archivo}.png'))
        if brillo is not None:
            Image.fromarray(brillo).save(os.path.join(carpeta, f'{nombre_archivo}_brillo.png'))

    # ------------------------------------------------------------------
    #  La vista previa: la malla del juego, posada en un instante de una animación
    # ------------------------------------------------------------------
    def mundos(self, anim=None, t=0.0, extra=None):
        """La matriz de cada parte en el espacio del modelo de Minecraft (con la animación en ese instante)."""
        mund = {}
        for n, p in self.partes.items():
            (px, py, pz), (rx, ry, rz) = self.pose(self.local_mc(n))
            dpos, drot, desc = np.zeros(3), np.zeros(3), np.ones(3)
            for a in ([anim] if anim else []) + (extra or []):
                if a is None:
                    continue
                aa, tt = a if isinstance(a, tuple) else (a, t)
                dp, dr, de = aa.muestra(n, tt)
                dpos += dp
                drot += dr
                desc *= de
            L = T(px + dpos[0], py + dpos[1], pz + dpos[2]) @ Rz(rz + drot[2]) @ Ry(ry + drot[1]) @ Rx(rx + drot[0])
            L = L @ np.diag([desc[0], desc[1], desc[2], 1.0])
            mund[n] = (np.eye(4) if p.padre is None else mund[p.padre]) @ L
        return mund

    def quads(self, mat='bestia', anim=None, t=0.0, extra=None):
        uv, alto = self._uv, self._alto
        Ainv = np.linalg.inv(A)
        mund = self.mundos(anim, t, extra)
        out = []
        for n, p in self.partes.items():
            for caja in p.cajas:
                B, (x0, y0, z0, w, h, d) = self.caja_mc(p, caja)
                (bx, by, bz), (ax, ay, az) = self.pose(B)
                M = Ainv @ mund[n] @ T(bx, by, bz) @ Rz(az) @ Ry(ay) @ Rx(ax)
                u, v = uv[self._clave(caja)]
                x1, y1, z1 = x0 + w, y0 + h, z0 + d
                V = {0: (x0, y0, z0), 1: (x1, y0, z0), 2: (x1, y1, z0), 3: (x0, y1, z0),
                     4: (x0, y0, z1), 5: (x1, y0, z1), 6: (x1, y1, z1), 7: (x0, y1, z1)}
                f4, f5, f6, f7 = u, u + d, u + d + w, u + d + w + w
                f8, f9 = u + d + w + d, u + d + w + d + w
                f10, f11, f12 = v, v + d, v + d + h
                caras = [((5, 4, 0, 1), f5, f10, f6, f11), ((2, 3, 7, 6), f6, f11, f7, f10),
                         ((0, 4, 7, 3), f4, f11, f5, f12), ((1, 0, 3, 2), f5, f11, f6, f12),
                         ((5, 1, 2, 6), f6, f11, f8, f12), ((4, 5, 6, 7), f8, f11, f9, f12)]
                for idx, u1, v1, u2, v2 in caras:
                    P4 = [(M @ np.array([*V[i], 1.0]))[:3] / 16.0 for i in idx]
                    if np.linalg.norm(np.cross(P4[1] - P4[0], P4[3] - P4[0])) < 1e-9:
                        continue
                    UVs = [(u2 / self.ancho, v1 / alto), (u1 / self.ancho, v1 / alto), (u1 / self.ancho, v2 / alto),
                           (u2 / self.ancho, v2 / alto)]
                    out.append((P4, UVs, mat))
        return out

    def vista(self, archivo, ojo=(1.6, 1.0, 2.4), objetivo=(0.0, 0.6, 0.0), W=640, H_=420, fov=40, anim=None, t=0.0,
              fondo=(0.12, 0.13, 0.17), extra=None):
        """Una foto de la malla del juego (como se vera, con su luz plana de Minecraft) desde ese punto (en bloques)."""
        import quimeras_modelo as qm
        nombre = f'bestia_{self.id}'
        qm._reg(nombre, self._base, self._brillo, estira=True)
        cam = vr.Camara(np.array(ojo), np.array(objetivo), fov, W, H_)
        luces = [((-0.45, 0.8, 0.5), (1.0, 0.98, 0.95), 0.75, 'llave'), ((0.6, 0.3, -0.7), (0.7, 0.75, 0.9), 0.35, 'contra')]

        def foto(mat):
            lz = vr.Lienzo(W, H_)
            qm.dibujar(lz, cam, self.quads(mat, anim, t, extra), luces, (0.42, 0.42, 0.46), None, 1.0)
            return lz.color * lz.alfa[..., None] + np.array(fondo) * (1 - lz.alfa[..., None])
        arr = foto(nombre)
        if getattr(self, 'translucido', False):
            # Lo translúcido, como en el juego: lo de dentro (la pasada opaca) visto a través del gel.
            opaco = self._base.copy()
            semi = (opaco[..., 3] > 0) & (opaco[..., 3] < 255)
            opaco[semi, 3] = 0
            qm._reg(nombre + '_opaco', opaco, self._brillo, estira=True)
            arr = arr * 0.45 + foto(nombre + '_opaco') * 0.55
        im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
        if archivo:
            im.save(archivo)
        return im

    def hoja_vistas(self, archivo, poses=None, W=360, H_=300, alto_bloques=None):
        """Una hoja con el mob de frente, de lado, de tres cuartos y por detrás, y las animaciones que se pidan
        (poses: [(nombre de la animacion, instante), ...])."""
        alto = alto_bloques or max(0.8, self.altura() / 16.0)
        r = alto * 2.1 + 0.9
        cy = alto * 0.5
        vistas = [((r * 0.7, cy + alto * 0.2, r * 0.75), None, 0.0), ((0.0, cy + alto * 0.1, r), None, 0.0),
                  ((r, cy + alto * 0.1, 0.0), None, 0.0), ((-r * 0.6, cy + alto * 0.5, -r * 0.8), None, 0.0)]
        for nombre, tt in (poses or []):
            vistas.append(((r * 0.7, cy + alto * 0.2, r * 0.75), self.anims[nombre], tt))
        col = 4
        filas = (len(vistas) + col - 1) // col
        hoja = Image.new('RGB', (W * col, H_ * filas), (20, 20, 26))
        for i, (o, a, tt) in enumerate(vistas):
            im = self.vista(None, ojo=o, objetivo=(0, cy, 0), W=W, H_=H_, fov=38, anim=a, t=tt)
            hoja.paste(im, ((i % col) * W, (i // col) * H_))
        hoja.save(archivo)

    def altura(self):
        """Lo alto del mob en el boceto (píxeles): el punto más alto de sus cajas."""
        top = 0.0
        for p in self.partes.values():
            for caja in p.cajas:
                M, x0, y0, z0, w, h, d = caja[:7]
                for dx in (x0, x0 + w):
                    for dy in (y0, y0 + h):
                        for dz in (z0, z0 + d):
                            top = max(top, float((M @ np.array([dx, dy, dz, 1.0]))[1]))
        return top


# ======================================================================================================================
#  Las animaciones
# ======================================================================================================================
class Anim:
    """Una animación de keyframes. Los valores van en los ejes del boceto (giro en grados alrededor de X, Y, Z del
    boceto; movimiento en píxeles con Y arriba): al exportar se pasan a los de Minecraft (Y y Z al revés)."""

    def __init__(self, modelo, nombre, largo, bucle):
        self.m, self.nombre, self.largo, self.bucle = modelo, nombre, largo, bucle
        self.canales = []  # (parte, tipo 'r'|'m'|'e', [(t, x, y, z, suave)])

    def _canal(self, parte, tipo, claves):
        assert parte in self.m.partes, (self.nombre, parte)
        ks = []
        for k in claves:
            t, x, y, z = k[:4]
            suave = k[4] if len(k) > 4 else 1
            ks.append((float(t), float(x), float(y), float(z), int(suave)))
        ks.sort(key=lambda k: k[0])
        self.canales.append((parte, tipo, ks))
        return self

    def rot(self, parte, claves):
        return self._canal(parte, 'r', claves)

    def mov(self, parte, claves):
        return self._canal(parte, 'm', claves)

    def esc(self, parte, claves):
        return self._canal(parte, 'e', claves)

    def onda(self, parte, tipo, eje, amp, periodo=None, fase=0.0, base=0.0, pasos=8, forma=None):
        """Una oscilación (seno) en un eje (0, 1, 2) durante toda la animación: amp, fase (en vueltas) y base."""
        periodo = periodo or self.largo
        n = max(2, int(round(pasos * self.largo / periodo)))
        claves = []
        for i in range(n + 1):
            t = self.largo * i / n
            v = math.sin(math.tau * (t / periodo + fase))
            if forma:
                v = forma(v)
            val = base + amp * v
            xyz = [0.0, 0.0, 0.0] if tipo != 'e' else [1.0, 1.0, 1.0]
            xyz[eje] = val
            claves.append((t, *xyz))
        return self._canal(parte, tipo, claves)

    def json(self):
        canales = []
        for parte, tipo, ks in self.canales:
            k2 = []
            for (t, x, y, z, s) in ks:
                if tipo == 'e':
                    v = (x, y, z)
                elif tipo == 'r':
                    v = (x, -y, -z)
                else:
                    v = (x, -y, -z)
                k2.append([round(t, 4), round(v[0], 4), round(v[1], 4), round(v[2], 4), s])
            canales.append({'p': parte, 't': tipo, 'k': k2})
        return {'largo': self.largo, 'bucle': self.bucle, 'canales': canales}

    # La muestra (para la vista previa): igual que KeyframeAnimation (Catmull-Rom entre claves, o lineal).
    def muestra(self, parte, t):
        dp, dr, de = np.zeros(3), np.zeros(3), np.ones(3)
        if self.bucle and self.largo > 0:
            t = t % self.largo
        for p, tipo, ks in self.canales:
            if p != parte:
                continue
            v = self._interp(ks, t)
            if tipo == 'r':
                dr += np.array((v[0], -v[1], -v[2])) * D
            elif tipo == 'm':
                dp += np.array((v[0], -v[1], -v[2]))
            else:
                de *= np.array(v)
        return dp, dr, de

    @staticmethod
    def _interp(ks, t):
        if t <= ks[0][0]:
            return np.array(ks[0][1:4])
        if t >= ks[-1][0]:
            return np.array(ks[-1][1:4])
        for i in range(len(ks) - 1):
            a, b = ks[i], ks[i + 1]
            if a[0] <= t <= b[0]:
                f = (t - a[0]) / max(1e-6, b[0] - a[0])
                pa_, pb_ = np.array(a[1:4]), np.array(b[1:4])
                if not b[4]:
                    return pa_ + (pb_ - pa_) * f
                p0 = np.array(ks[max(0, i - 1)][1:4])
                p3 = np.array(ks[min(len(ks) - 1, i + 2)][1:4])
                f2, f3 = f * f, f * f * f
                return 0.5 * ((2 * pa_) + (-p0 + pb_) * f + (2 * p0 - 5 * pa_ + 4 * pb_ - p3) * f2 + (-p0 + 3 * pa_ - 3 * pb_ + p3) * f3)
        return np.array(ks[-1][1:4])


# ======================================================================================================================
#  El huevo, el retrato, el objeto y las partículas
# ======================================================================================================================
SILUETA = [(2, 6, 9), (3, 5, 10), (4, 4, 11), (5, 3, 12), (6, 3, 12), (7, 2, 13), (8, 2, 13), (9, 2, 13),
           (10, 2, 13), (11, 2, 13), (12, 2, 13), (13, 3, 12), (14, 4, 11), (15, 5, 10)]


def huevo(ident, piel, contorno, dibujo):
    """El huevo generador, al estilo de los del mod: la silueta del huevo de vanilla, la luz desde arriba a la izquierda,
    el contorno de dos tonos y el dibujo del mob (dibujo(px, filas, c): pinta sus señas). piel: 3 tonos (claro, medio,
    oscuro); contorno: 2 tonos."""
    def c(h):
        return (*[int(v) for v in H(h)], 255)
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    px = im.load()
    filas = {f: (a, b) for f, a, b in SILUETA}
    for f, (a, b) in filas.items():
        for x in range(a, b + 1):
            fuera_arriba = f - 1 in filas and not (filas[f - 1][0] <= x <= filas[f - 1][1])
            fuera_abajo = f + 1 in filas and not (filas[f + 1][0] <= x <= filas[f + 1][1])
            borde = x in (a, b) or f in (2, 15) or fuera_arriba or fuera_abajo
            luz_ = (x - a) / max(1, b - a) + (f - 2) / 13
            if borde:
                px[x, f] = c(contorno[1]) if luz_ > 0.9 else c(contorno[0])
            else:
                px[x, f] = c(piel[0]) if luz_ < 0.45 else c(piel[1]) if luz_ < 1.25 else c(piel[2])
    dibujo(px, filas, c)
    carpeta = ruta(ASSETS, 'textures/item')
    im.save(os.path.join(carpeta, f'huevo_{ident}.png'))
    return im


def objeto(ident, nombre_es, nombre_en):
    """El huevo como objeto (su modelo) y los nombres del mob y de su huevo en los dos idiomas."""
    base = ruta(ASSETS)
    with open(os.path.join(base, f'items/huevo_{ident}.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'model': {'type': 'minecraft:model', 'model': f'atalaya:item/huevo_{ident}'}}, fh, indent=2)
        fh.write('\n')
    with open(os.path.join(base, f'models/item/huevo_{ident}.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': f'atalaya:item/huevo_{ident}'}}, fh,
                  indent=2)
        fh.write('\n')
    for idioma, nombres in (('es_es', (nombre_es, f'Huevo generador de {nombre_es.lower()}')),
                            ('en_us', (nombre_en, f'{nombre_en} Spawn Egg'))):
        r = os.path.join(base, f'lang/{idioma}.json')
        d = json.load(open(r, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
        d[f'entity.atalaya.{ident}'] = nombres[0]
        d[f'item.atalaya.huevo_{ident}'] = nombres[1]
        with open(r, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False)
            fh.write('\n')


def retrato(m, ojo, objetivo, anim=None, t=0.0, fov=34, oscuro=(10, 6, 16)):
    """El retrato del menú (32 x 32, en el atlas de la interfaz: menu/mob/<id>): el mob desde ese punto, con su luz,
    reducido sin emborronar y con su contorno."""
    grande = m.vista(None, ojo=ojo, objetivo=objetivo, W=128, H_=128, fov=fov, anim=anim, t=t, fondo=(0, 0, 0))
    arr = np.asarray(grande).astype(float)
    # Lo que no es fondo (el fondo es negro puro): una máscara, reducida por mayoría.
    mascara = arr.sum(axis=-1) > 6
    peq = np.zeros((32, 32, 4), np.uint8)
    for y in range(32):
        for x in range(32):
            bloque = arr[y * 4:y * 4 + 4, x * 4:x * 4 + 4]
            mb = mascara[y * 4:y * 4 + 4, x * 4:x * 4 + 4]
            if mb.sum() >= 6:
                c = bloque[mb].mean(axis=0)
                peq[y, x, :3] = np.clip(c * 1.08, 0, 255)
                peq[y, x, 3] = 255
    a = peq[..., 3] > 0
    v = np.zeros_like(a)
    v[1:, :] |= a[:-1, :]
    v[:-1, :] |= a[1:, :]
    v[:, 1:] |= a[:, :-1]
    v[:, :-1] |= a[:, 1:]
    borde = v & ~a
    peq[borde, :3] = oscuro
    peq[borde, 3] = 255
    carpeta = ruta(ASSETS, 'textures/gui/sprites/menu/mob')
    os.makedirs(carpeta, exist_ok=True)
    Image.fromarray(peq).save(os.path.join(carpeta, f'{m.id}.png'))
    return Image.fromarray(peq)


def particula(ident, nombre, cuadros):
    """Los sprites de una partícula del mob (bestia_<id>_<nombre>): una lista de imágenes RGBA (8 x 8 o 16 x 16)."""
    carpeta = ruta(ASSETS, 'textures/particle')
    os.makedirs(carpeta, exist_ok=True)
    nombres = []
    for i, im in enumerate(cuadros):
        n = f'bestia_{ident}_{nombre}_{i}'
        im.save(os.path.join(carpeta, n + '.png'))
        nombres.append(f'atalaya:{n}')
    os.makedirs(ruta(ASSETS, 'particles'), exist_ok=True)
    with open(ruta(ASSETS, f'particles/bestia_{ident}_{nombre}.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump({'textures': nombres}, fh, indent=2)
        fh.write('\n')


def sprite(n, fn):
    """Un sprite de partícula de n x n píxeles pintado por fn(x, y) -> (r, g, b, a) en arrays (coordenadas 0..1)."""
    ys, xs = np.mgrid[0:n, 0:n].astype(float)
    x, y = (xs + 0.5) / n, (ys + 0.5) / n
    r, g, b, a = fn(x, y)
    out = np.zeros((n, n, 4), np.uint8)
    for i, c in enumerate((r, g, b, a)):
        out[..., i] = np.clip(np.broadcast_to(c, (n, n)), 0, 255)
    return Image.fromarray(out)

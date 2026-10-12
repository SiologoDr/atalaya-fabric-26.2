"""
Las animaciones de los cuatro mini jefes, escritas pose a pose sobre sus mallas del juego (minijefes_juego.py).

Juan (11-10-2026): "hagamos sus animaciones god tambien a su altura de sus disenos... teniendo en cuenta la anatomia
de cada uno". Cada uno se mueve como lo que es:
  - Moctezuma, guerrero: paso marcial con el escudo por delante, los pies plantados (IK) y el macuahuitl a dos tiempos;
  - Yiatzo, mago: no anda, flota; la capa y las losas de glifos le siguen con retraso;
  - Atlahua, rey del mar: paso lento y pesado, el tridente a plomo como un baston;
  - Xiuhquetzal, fenix: bate las alas con la mano del ala que se pliega al subir, el cuerpo que sube con cada batida,
    la cabeza quieta como la de un ave de presa y la cola de fuego que ondea.

Convenciones (todo SE SUMA a la postura de reposo de cada uno, la de su malla):
  rot   grados (x, y, z), como degreeVec. En las piernas y los brazos, x negativo los lleva hacia delante; en el torso
        y la cabeza, x positivo los inclina hacia delante; en el brazo izquierdo (el de x positiva) z negativo lo abre.
  pos   pixeles del modelo con Y hacia ABAJO (al exportar pasa a posVec)
  esc   multiplicadores (x, y, z)

Las capas, los faldones, el penacho y la cola del fenix no se animan a mano: los mueve la fisica (fisica()), un
pendulo por pieza que sigue a su padre con inercia y cae con su peso, simulado sobre la animacion ya hecha.

De aqui salen <Nombre>Animaciones.java (cliente) y <Nombre>Geometria.java (duraciones, ticks de cada golpe y puntos
para el servidor y la camara de la presentacion).

Uso: python minijefes_anim.py <raiz del proyecto> [carpeta de hojas] [nombre[:ANIM,ANIM]]
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

import minijefes_juego as mjj
import minijefes_modelo as mj
import vigia_render as vr

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
HOJAS = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
TICK = 0.05
NULO = {'rot': (0.0, 0.0, 0.0), 'pos': (0.0, 0.0, 0.0), 'esc': (1.0, 1.0, 1.0)}


# ----------------------------------------------------------------------
#  Poses
# ----------------------------------------------------------------------
def r(x=0.0, y=0.0, z=0.0):
    return {'rot': (x, y, z)}


def p(x=0.0, y=0.0, z=0.0):
    return {'pos': (x, y, z)}


def rp(rot, pos):
    return {'rot': tuple(rot), 'pos': tuple(pos)}


def sumar(*poses):
    """Suma poses (rotaciones y posiciones se suman; escalas se multiplican)."""
    out = {}
    for q in poses:
        if not q:
            continue
        for k, v in q.items():
            d = out.setdefault(k, {})
            for tipo, val in v.items():
                if tipo == 'esc':
                    d[tipo] = tuple(a * b for a, b in zip(d.get(tipo, (1, 1, 1)), val))
                else:
                    d[tipo] = tuple(a + b for a, b in zip(d.get(tipo, (0, 0, 0)), val))
    return out


def escalar(q, k):
    """Una pose por k (las escalas, hacia 1)."""
    out = {}
    for pieza, d in q.items():
        out[pieza] = {}
        for tipo, v in d.items():
            if tipo == 'esc':
                out[pieza][tipo] = tuple(1 + (c - 1) * k for c in v)
            else:
                out[pieza][tipo] = tuple(c * k for c in v)
    return out


def mezclar(a, b, k):
    """De la pose a a la b (k de 0 a 1)."""
    out = {}
    for pieza in set(a) | set(b):
        da, db = a.get(pieza, {}), b.get(pieza, {})
        d = {}
        for tipo in set(da) | set(db):
            va = np.array(da.get(tipo, NULO[tipo]), float)
            vb = np.array(db.get(tipo, NULO[tipo]), float)
            d[tipo] = tuple(va + (vb - va) * k)
        out[pieza] = d
    return out


def _suave(u):
    return u * u * (3 - 2 * u)


CURVAS = {
    'suave': _suave,
    'lineal': lambda u: u,
    'entra': lambda u: u * u,
    'sale': lambda u: 1 - (1 - u) ** 2,
    'golpe': lambda u: 1 - (1 - u) ** 4,
    'seco': lambda u: 1 - (1 - u) ** 6,
    'muelle': lambda u: 1 + 2.70158 * (u - 1) ** 3 + 1.70158 * (u - 1) ** 2,
    'cae': lambda u: u ** 3,
}


def linea(*claves):
    """Una sucesion de poses: (t, pose, curva con la que se llega a ella). Devuelve f(s) -> pose."""
    claves = sorted(claves, key=lambda c: c[0])

    def f(s):
        if s <= claves[0][0]:
            return claves[0][1]
        for (t0, a, _), (t1, b, curva) in zip(claves, claves[1:]):
            if s <= t1:
                u = (s - t0) / max(1e-9, t1 - t0)
                return mezclar(a, b, CURVAS[curva](min(1.0, max(0.0, u))))
        return claves[-1][1]
    return f


def ventana(s, t0, t1, sube=0.15, baja=0.15):
    """1 entre t0 y t1, con rampas suaves a los lados."""
    if s < t0 - sube or s > t1 + baja:
        return 0.0
    if s < t0:
        return _suave((s - (t0 - sube)) / sube)
    if s > t1:
        return 1.0 - _suave((s - t1) / baja)
    return 1.0


def temblor(s, t0, t1, amp, frec=22.0, fase=0.0):
    """Un temblor (de -amp a amp) entre t0 y t1, que se apaga al final."""
    if s < t0 or s > t1:
        return 0.0
    k = 1.0 - (s - t0) / max(1e-6, t1 - t0)
    return amp * k * math.sin(2 * math.pi * frec * (s - t0) + fase)


# ----------------------------------------------------------------------
#  Las piernas: IK de dos huesos en el plano del paso, con el pie plano
# ----------------------------------------------------------------------
class Pierna:
    """Una pierna humana (muslo, espinilla, pie), en el marco de la pelvis: el muslo cuelga en +Y."""

    def __init__(self, hs, lado):
        n = 'izq' if lado > 0 else 'der'
        self.lado = lado
        self.nombres = (f'pierna_{n}', f'espinilla_{n}', f'pie_{n}')
        g = {h.nombre: h for h in hs}
        self.cadera = g[self.nombres[0]].pivote.copy()
        self.l1 = float(g[self.nombres[1]].pivote[1])
        self.l2 = float(g[self.nombres[2]].pivote[1])

    def angulos(self, tobillo):
        """Los giros (x) del muslo, la espinilla y el pie para llevar el tobillo (en el marco de la pelvis, y, z) a su
        sitio con la rodilla hacia delante y el pie plano respecto a la pelvis."""
        dy = tobillo[0] - self.cadera[1]
        dz = tobillo[1] - self.cadera[2]
        d = min(math.hypot(dy, dz), self.l1 + self.l2 - 0.05)
        linea_ = math.atan2(dz, dy)
        ca = (self.l1 ** 2 + d ** 2 - self.l2 ** 2) / (2 * self.l1 * d)
        alfa = math.acos(max(-1.0, min(1.0, ca)))
        cg = (self.l1 ** 2 + self.l2 ** 2 - d ** 2) / (2 * self.l1 * self.l2)
        doblez = math.pi - math.acos(max(-1.0, min(1.0, cg)))
        muslo = linea_ - alfa
        return math.degrees(muslo), math.degrees(doblez), -math.degrees(muslo + doblez)

    def pose(self, tobillo, punta=0.0, abre=0.0):
        m, e, q = self.angulos(tobillo)
        return {self.nombres[0]: r(m, 0, abre * self.lado), self.nombres[1]: r(e), self.nombres[2]: r(q + punta)}

    def reposo(self):
        """Donde esta el tobillo de pie (y, z en el marco de la pelvis)."""
        return np.array([self.cadera[1] + self.l1 + self.l2, self.cadera[2]])


def en_pelvis(hs, pose, pelvis, punto):
    """Un punto del modelo (pixeles) en el marco de la pelvis con la pose dada (solo y, z)."""
    M = mjj.matrices(hs, pose)[mjj._idx(hs, pelvis)]
    q = np.linalg.inv(M) @ np.array([*punto, 1.0])
    return np.array([q[1], q[2]])


# ----------------------------------------------------------------------
#  Brazos y armas: se dice hacia donde apuntan y sale el giro (sumado al reposo)
# ----------------------------------------------------------------------
def absoluto(hs, pieza, x=None, y=None, z=None):
    """El giro (sumado al reposo) que deja una pieza con los giros totales dados (los que no se dan, como en reposo)."""
    h = hs[mjj._idx(hs, pieza)]
    obj = [h.rot[i] if v is None else v for i, v in enumerate((x, y, z))]
    return {pieza: r(*(np.array(obj) - h.rot))}


def apuntar(hs, pieza, arriba=0.0, fuera=0.0, delante=0.0, lado=1):
    """El giro (sumado al reposo) que lleva una pieza que cuelga en +Y (el brazo) a apuntar hacia esa direccion en el
    marco de su padre: arriba (-1 cuelga), fuera (hacia su lado: lado 1 el izquierdo, -1 el derecho) y delante."""
    d = np.array([fuera * lado, -arriba, -delante], float)
    d /= np.linalg.norm(d)
    a_ = math.degrees(math.asin(max(-1.0, min(1.0, d[2]))))
    c_ = math.degrees(math.atan2(-d[0], d[1]))
    return absoluto(hs, pieza, a_, 0.0, c_)


def brazo(hs, lado, arriba=-1.0, fuera=0.0, delante=0.0, codo=0.0, muneca=None, arma=None, nombre_arma=None):
    """Un brazo entero: el hombro apunta, el codo dobla 'codo' grados (negativo hacia delante) y, si se da, el arma
    queda girada 'arma' grados respecto a la mano (0: sigue al antebrazo)."""
    n = 'izq' if lado > 0 else 'der'
    q = sumar(apuntar(hs, f'hombro_{n}', arriba, fuera, delante, lado), absoluto(hs, f'antebrazo_{n}', codo, 0.0, 0.0))
    if muneca is not None:
        q = sumar(q, absoluto(hs, f'mano_{n}', *muneca))
    if arma is not None and nombre_arma:
        q = sumar(q, absoluto(hs, nombre_arma, arma, 0.0, 0.0))
    return q


# ----------------------------------------------------------------------
#  La fisica de lo que cuelga y ondea
# ----------------------------------------------------------------------
def _euler_zyx(R):
    """Los giros (x, y, z) en grados de R = Rz Ry Rx."""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    a = math.atan2(R[2, 1], R[2, 2])
    c = math.atan2(R[1, 0], R[0, 0])
    return np.degrees([a, b, c])


def _rot_entre(u, v):
    """La rotacion (3x3) mas corta que lleva el vector unitario u a v."""
    eje = np.cross(u, v)
    s = np.linalg.norm(eje)
    c = float(np.clip(u @ v, -1.0, 1.0))
    if s < 1e-9:
        return np.eye(3)
    eje /= s
    K = np.array([[0, -eje[2], eje[1]], [eje[2], 0, -eje[0]], [-eje[1], eje[0], 0]])
    ang = math.atan2(s, c)
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


class Muelle:
    """Una pieza que cuelga o ondea: un pendulo desde su origen hasta su centro (o hasta la siguiente de la cadena).
    rigidez: lo que guarda su pose respecto al padre (1, nada de peso; 0, cuelga a plomo); k y amort: el muelle
    que la lleva a su sitio (por segundo); limite: lo que se puede apartar de su pose (grados)."""

    def __init__(self, pieza, rigidez=0.5, k=60.0, amort=7.0, limite=50.0):
        self.pieza, self.rigidez, self.k, self.amort, self.limite = pieza, rigidez, k, amort, limite


def _brazo_de(hs, i):
    """De su origen a su centro (pixeles, en su marco): por donde tira el peso de una pieza."""
    h = hs[i]
    hijos = [j for j, g in enumerate(hs) if g.padre == i and g.d]
    if hijos and any(hs[j].nombre.startswith(h.nombre.rstrip('0123456789')) for j in hijos):
        j = [j for j in hijos if hs[j].nombre.startswith(h.nombre.rstrip('0123456789'))][0]
        return hs[j].pivote.copy()
    if not h.d:
        return np.array([0.0, 4.0, 0.0])
    a = np.array(list(h.d.keys()), float) + 0.5
    return a.mean(axis=0) * h.esc


def fisica(hs, poses, muelles, bucle=False):
    """Pasa la fisica a una animacion ya muestreada (una pose por tick): cada muelle sigue a su padre con inercia y
    cae con su peso. En los bucles se simulan tres vueltas y se queda la ultima (y se cierra con la primera)."""
    if not muelles:
        return poses
    n = len(poses)
    vueltas = 3 if bucle else 1
    idx = {h.nombre: i for i, h in enumerate(hs)}
    estado = {}
    salida = [dict(q) for q in poses]
    abajo = np.array([0.0, 1.0, 0.0])
    sub = 4
    dt = TICK / sub
    for v in range(vueltas):
        for k in range(n if not bucle else n - 1):
            pose = dict(poses[k])
            for m in muelles:
                i = idx[m.pieza]
                M = mjj.matrices(hs, pose)
                Mp = M[hs[i].padre]
                Mi = M[i]
                brazo = _brazo_de(hs, i)
                L = float(np.linalg.norm(brazo)) or 1.0
                d0 = brazo / L
                piv = Mi[:3, 3]
                dir_anim = Mi[:3, :3] @ d0
                dir_anim /= np.linalg.norm(dir_anim)
                obj = dir_anim * m.rigidez + abajo * (1 - m.rigidez)
                obj /= np.linalg.norm(obj)
                if m.pieza not in estado:
                    estado[m.pieza] = [piv + obj * L, np.zeros(3), piv.copy()]
                q, vel, piv_ant = estado[m.pieza]
                for s in range(sub):
                    pv = piv_ant + (piv - piv_ant) * (s + 1) / sub
                    meta = pv + obj * L
                    acc = (meta - q) * m.k - vel * m.amort
                    vel = vel + acc * dt
                    q = q + vel * dt
                    u = q - pv
                    q = pv + u / (np.linalg.norm(u) or 1.0) * L
                estado[m.pieza] = [q, vel, piv.copy()]
                u = (q - piv) / L
                # Lo que se aparta de su pose, con su limite.
                ang = math.degrees(math.acos(float(np.clip(u @ dir_anim, -1, 1))))
                if ang > m.limite:
                    eje = np.cross(dir_anim, u)
                    u = _rot_eje(eje, math.radians(m.limite)) @ dir_anim
                Rw = _rot_entre(dir_anim, u)
                Rp = Mp[:3, :3]
                Rp_n = Rp / np.cbrt(np.linalg.det(Rp))
                Rl = Mi[:3, :3]
                Rl_n = np.linalg.inv(Rp_n) @ Rw @ (Rl / np.cbrt(np.linalg.det(Rl)))
                eul = _euler_zyx(Rl_n)
                off = eul - hs[i].rot
                off = (off + 180) % 360 - 180
                d = dict(pose.get(m.pieza, {}))
                d['rot'] = tuple(off)
                pose[m.pieza] = d
            if v == vueltas - 1:
                salida[k] = pose
    if bucle:
        salida[-1] = salida[0]
        # Se cierra el bucle: en el ultimo cuarto lo que mueve la fisica va hacia la primera pose. Solo eso: lo demas ya
        # es periodico, y mezclado se estropeaba (las losas de Yiatzo, que dan una vuelta entera por ciclo, iban de 270
        # a 0 grados mezclando y giraban hacia atras al final de cada ciclo).
        m0 = max(1, (n - 1) // 4)
        for j in range(n - 1 - m0, n - 1):
            kk = (j - (n - 1 - m0)) / m0
            for m in muelles:
                d = mezclar({m.pieza: salida[j].get(m.pieza, {})}, {m.pieza: salida[0].get(m.pieza, {})}, _suave(kk) * 0.5)
                salida[j] = {**salida[j], **d}
    return salida


def _rot_eje(eje, ang):
    eje = np.asarray(eje, float)
    l = np.linalg.norm(eje)
    if l < 1e-9:
        return np.eye(3)
    eje = eje / l
    K = np.array([[0, -eje[2], eje[1]], [eje[2], 0, -eje[0]], [-eje[1], eje[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


# ----------------------------------------------------------------------
#  Animaciones: muestrear, simplificar y exportar
# ----------------------------------------------------------------------
class Anim:
    def __init__(self, nombre, dur, f, bucle=False, muelles=None):
        self.nombre, self.dur, self.f, self.bucle = nombre, dur, f, bucle
        self.muelles = muelles or []
        self._muestras = None

    def muestras(self, hs):
        if self._muestras is None:
            n = int(round(self.dur / TICK))
            poses = [self.f(min(self.dur, k * TICK)) for k in range(n + 1)]
            self._muestras = fisica(hs, poses, self.muelles, self.bucle)
        return self._muestras

    def en(self, hs, s):
        m = self.muestras(hs)
        if self.bucle:
            s %= self.dur
        k = min(len(m) - 1, max(0, s / TICK))
        i = int(k)
        j = min(len(m) - 1, i + 1)
        return mezclar(m[i], m[j], k - i)


def catmull(a, p0, p1, p2, p3):
    return 0.5 * (2 * p1 + (p2 - p0) * a + (2 * p0 - 5 * p1 + 4 * p2 - p3) * a * a + (3 * p1 - p0 - 3 * p2 + p3) * a ** 3)


def _catmull_vec(K, V, T):
    """Lo que da un canal (claves en K, valores V) en los tiempos T, como en el juego."""
    n = len(K)
    idx = np.searchsorted(K, T, side='left')
    prev = np.maximum(0, idx - 1)
    nxt = np.minimum(n - 1, prev + 1)
    den = np.where(nxt != prev, K[nxt] - K[prev], 1.0)
    al = np.clip((T - K[prev]) / den, 0.0, 1.0)[:, None]
    al = np.where((nxt != prev)[:, None], al, 0.0)
    p0, p1, p2, p3 = V[np.maximum(0, prev - 1)], V[prev], V[nxt], V[np.minimum(n - 1, nxt + 1)]
    return catmull(al, p0, p1, p2, p3)


def simplificar(ks, tol, paso=0.0125):
    """Quita las claves que sobran mientras la curva del juego no se aparte mas de tol de la muestreada."""
    K = np.array([k[0] for k in ks], float)
    V = np.array([k[1] for k in ks], float)
    # Se mide en una rejilla fina y ademas en cada clave y entre cada dos (las de entre ticks van mas juntas).
    T = np.unique(np.concatenate([np.arange(0.0, K[-1] + 1e-9, paso), K, (K[1:] + K[:-1]) / 2]))
    ref = np.array([np.interp(T, K, V[:, c]) for c in range(V.shape[1])]).T
    vivas = list(range(len(ks)))
    cambia = True
    while cambia:
        cambia = False
        j = 1
        while j < len(vivas) - 1:
            prueba = vivas[:j] + vivas[j + 1:]
            lo, hi = K[vivas[max(0, j - 2)]], K[vivas[min(len(vivas) - 1, j + 2)]]
            m = (T >= lo) & (T <= hi)
            err = np.abs(_catmull_vec(K[prueba], V[prueba], T[m]) - ref[m]).max()
            if err < tol:
                vivas = prueba
                cambia = True
            else:
                j += 1
    return [ks[i] for i in vivas]


TOL = {'rot': 0.35, 'pos': 0.06, 'esc': 0.005}


# ----------------------------------------------------------------------
#  Giros sin tirones: el juego va de una clave a la siguiente mezclando los tres angulos, asi que si un angulo salta
#  (de +170 a -170, que es casi lo mismo) la pieza da la vuelta entera por el camino largo en ese instante; y si en un
#  tick gira mucho, a medio tick pasa por donde no debe. Juan (11-10-2026) lo vio en la Tormenta de Moctezuma ("su mano
#  o su espada es media rara lo que mueve"); pasaba tambien en el Ciclon de Yiatzo y en los ataques de Atlahua.
# ----------------------------------------------------------------------
def _matriz(g):
    """La rotacion Rz Ry Rx de unos giros (x, y, z) en grados (como el juego)."""
    x, y, z = np.radians(np.asarray(g, float))
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def _cercano(g, ref, gemelo=False):
    """De los giros equivalentes a g (los mismos +-360 en cada eje y, si se pide, su gemelo (x+180, 180-y, z+180)),
    el mas cercano a ref. Sin el gemelo: sumar 360 a un eje no cambia nada aunque luego se le sumen otras animaciones
    (el reposo se mezcla por peso con los ataques); con el gemelo si (lo que se le sumara en y iria al reves)."""
    g = np.asarray(g, float)
    mejor = None
    for c in ((g, np.array([g[0] + 180.0, 180.0 - g[1], g[2] + 180.0])) if gemelo else (g,)):
        c = c + np.round((ref - c) / 360.0) * 360.0
        d = float(np.abs(c - ref).sum())
        if mejor is None or d < mejor[0]:
            mejor = (d, c)
    return mejor[1]


def _angulo(R0, R1):
    return math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(R0.T @ R1) - 1.0) / 2.0))))


def _a_medias(R0, R1):
    """La rotacion a medio camino entre R0 y R1 por el camino corto."""
    Rr = R0.T @ R1
    ang = math.acos(max(-1.0, min(1.0, (np.trace(Rr) - 1.0) / 2.0)))
    if ang < 1e-7:
        return R0
    eje = np.array([Rr[2, 1] - Rr[1, 2], Rr[0, 2] - Rr[2, 0], Rr[1, 0] - Rr[0, 1]])
    if np.linalg.norm(eje) < 1e-6:
        w, v = np.linalg.eigh((Rr + Rr.T) / 2.0)
        eje = v[:, int(np.argmax(w))]
    return R0 @ _rot_eje(eje, ang / 2.0)


def _giros(hs, poses):
    reposo = {h.nombre: np.asarray(h.rot, float) for h in hs}
    piezas = sorted({pz for q in poses for pz, d in q.items() if 'rot' in d})
    return reposo, piezas


def continuas(hs, poses):
    """Los giros de cada pieza sin saltos: en cada muestra, de los equivalentes, el mas cercano al de la anterior."""
    reposo, piezas = _giros(hs, poses)
    out = [{k: dict(v) for k, v in q.items()} for q in poses]
    for pz in piezas:
        prev = None
        for q in out:
            d = q.setdefault(pz, {})
            tot = reposo[pz] + np.asarray(d.get('rot', NULO['rot']), float)
            if prev is not None:
                tot = _cercano(tot, prev)
            prev = tot
            d['rot'] = tuple(tot - reposo[pz])
    return out


def entre_ticks(hs, ts, poses, tol=3.0, prof=3):
    """Pone claves entre dos muestras donde, mezclando los angulos, alguna pieza se apartaria mas de tol grados del
    camino corto: en esas claves cada pieza va por el camino corto (hasta 1/8 de tick)."""
    reposo, piezas = _giros(hs, poses)

    def total(q, pz):
        return reposo[pz] + np.asarray(q.get(pz, {}).get('rot', NULO['rot']), float)

    def medio(t0, q0, t1, q1, n):
        if n == 0:
            return []
        qm = mezclar(q0, q1, 0.5)
        peor = 0.0
        for pz in piezas:
            g0, g1 = total(q0, pz), total(q1, pz)
            if np.abs(g1 - g0).max() < 1e-6:
                continue
            Rm = _a_medias(_matriz(g0), _matriz(g1))
            gl = (g0 + g1) / 2.0
            peor = max(peor, _angulo(_matriz(gl), Rm))
            qm[pz] = {**qm.get(pz, {}), 'rot': tuple(_cercano(_euler_zyx(Rm), gl) - reposo[pz])}
        if peor <= tol:
            return []
        tm = (t0 + t1) / 2.0
        return medio(t0, q0, tm, qm, n - 1) + [(tm, qm)] + medio(tm, qm, t1, q1, n - 1)

    out = [(ts[0], poses[0])]
    for i in range(len(poses) - 1):
        out += medio(ts[i], poses[i], ts[i + 1], poses[i + 1], prof)
        out.append((ts[i + 1], poses[i + 1]))
    return [t for t, _ in out], [q for _, q in out]


def claves(hs, a):
    """Las poses que se exportan, con su tiempo: las muestras (una por tick) con los giros continuos y, donde hace falta,
    claves entre ticks."""
    if not hasattr(a, '_claves'):
        m = a.muestras(hs)
        poses = continuas(hs, m)
        if not a.bucle:
            # Las que no son bucle acaban en su reposo: que sigan acabando en cero (si no, al pasar a la siguiente
            # animacion la pieza daria la vuelta).
            for pz, d in poses[-1].items():
                fin = np.asarray(d.get('rot', NULO['rot']), float)
                resto = np.abs(fin - np.round(fin / 360.0) * 360.0).max()
                if resto > 1.0 and np.abs(np.asarray(m[-1].get(pz, {}).get('rot', NULO['rot']))).max() < 1.0:
                    raise ValueError(f'{a.nombre}: {pz} no vuelve a cero con los giros continuos ({d["rot"]})')
        a._claves = entre_ticks(hs, [k * TICK for k in range(len(poses))], poses)
    return a._claves


def canales(hs, a):
    """Los canales de una animacion: (pieza, tipo, [(t, valor)]), sin los que no se mueven."""
    if hasattr(a, '_canales'):
        return a._canales
    ts, m = claves(hs, a)
    nombres = {h.nombre for h in hs}
    usados = []
    for q in m:
        for pieza, d in q.items():
            for tipo in d:
                if (pieza, tipo) not in usados:
                    usados.append((pieza, tipo))
    out = []
    for pieza, tipo in usados:
        if pieza not in nombres:
            raise KeyError(f'{a.nombre}: no hay pieza {pieza}')
        ks = [(t, tuple(q.get(pieza, {}).get(tipo, NULO[tipo]))) for t, q in zip(ts, m)]
        if all(np.allclose(v, NULO[tipo], atol=1e-4) for _, v in ks):
            continue
        out.append((pieza, tipo, simplificar(ks, TOL[tipo])))
    a._canales = out
    return out


def fj(x):
    s = ('%.3f' % x).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s + 'F'


ORDEN = ('REPOSO', 'ANDAR', 'DORMIDO', 'DESPERTAR', 'NORMAL', 'AREA', 'ESPECIAL', 'MUERTE')


def clase(nombre):
    return nombre.capitalize()


def java_anims(nombre, hs, anims):
    C = clase(nombre) + 'Animaciones'
    L = ['package com.atalaya.client;', '',
         'import net.minecraft.client.animation.AnimationChannel;',
         'import net.minecraft.client.animation.AnimationDefinition;',
         'import net.minecraft.client.animation.Keyframe;',
         'import net.minecraft.client.animation.KeyframeAnimations;', '',
         '/**',
         f' * Las animaciones de {TITULO[nombre]}. GENERADO por materiales/generadores/minijefes_anim.py:',
         ' * no se editan a mano. Se suman a su postura de reposo (la de su malla) y acaban en ella.',
         f' * El servidor saca de las mismas poses los ticks de cada golpe ({clase(nombre)}Geometria).',
         ' */',
         f'public final class {C} {{', '']
    for n in ORDEN:
        L.append(f'    public static final AnimationDefinition {n} = {n.lower()}();')
    L += ['', f'    /** Las ocho, para el modelo. */',
          f'    public static final MiniJefeAnimaciones JUEGO = new MiniJefeAnimaciones({", ".join(ORDEN)});', '',
          f'    private {C}() {{', '    }', '',
          '    private static Keyframe rot(float t, float x, float y, float z) {',
          '        return new Keyframe(t, KeyframeAnimations.degreeVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);',
          '    }', '',
          '    private static Keyframe pos(float t, float x, float y, float z) {',
          '        return new Keyframe(t, KeyframeAnimations.posVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);',
          '    }', '',
          '    private static Keyframe esc(float t, float x, float y, float z) {',
          '        return new Keyframe(t, KeyframeAnimations.scaleVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);',
          '    }', '',
          '    private static AnimationChannel giro(Keyframe... k) {',
          '        return new AnimationChannel(AnimationChannel.Targets.ROTATION, k);', '    }', '',
          '    private static AnimationChannel mover(Keyframe... k) {',
          '        return new AnimationChannel(AnimationChannel.Targets.POSITION, k);', '    }', '',
          '    private static AnimationChannel escala(Keyframe... k) {',
          '        return new AnimationChannel(AnimationChannel.Targets.SCALE, k);', '    }', '']
    for n in ORDEN:
        a = anims[n]
        cs = canales(hs, a)
        # En trozos de pocos canales: cada metodo de Java tiene un tope de 64 KB.
        trozos = []
        actual, peso = [], 0
        for c in cs:
            if actual and peso + len(c[2]) > 220:
                trozos.append(actual)
                actual, peso = [], 0
            actual.append(c)
            peso += len(c[2])
        if actual:
            trozos.append(actual)
        L.append(f'    private static AnimationDefinition {n.lower()}() {{')
        L.append(f'        AnimationDefinition.Builder b = AnimationDefinition.Builder.withLength({fj(a.dur)})'
                 + ('.looping();' if a.bucle else ';'))
        for i in range(len(trozos)):
            L.append(f'        {n.lower()}{i}(b);')
        L.append('        return b.build();')
        L.append('    }')
        L.append('')
        for i, trozo in enumerate(trozos):
            L.append(f'    private static void {n.lower()}{i}(AnimationDefinition.Builder b) {{')
            for pieza, tipo, ks in trozo:
                fn = {'rot': ('rot', 'giro'), 'pos': ('pos', 'mover'), 'esc': ('esc', 'escala')}[tipo]
                partes = []
                for t, v in ks:
                    x, y, z = v
                    if tipo == 'pos':
                        y = -y
                    partes.append(f'{fn[0]}({fj(t)}, {fj(x)}, {fj(y)}, {fj(z)})')
                L.append(f'        b.addAnimation("{pieza}", {fn[1]}(' + ',\n                '.join(partes) + '));')
            L.append('    }')
            L.append('')
    L.append('}')
    return '\n'.join(L) + '\n'


# ----------------------------------------------------------------------
#  Puntos para el servidor y la camara
# ----------------------------------------------------------------------
def bloques(nombre, hs, pose, pieza, local=(0, 0, 0)):
    """Un punto de una pieza (en los voxeles de su boceto) en bloques del cuerpo (x a SU izquierda, y arriba desde
    los pies, z adelante), con su escala."""
    return mjj.a_bloques(mjj.punto(hs, pose, pieza, local), mj.ESCALA[nombre])


def al_suelo(hs, pose, suelo=24.0):
    """Lo que hay que bajar la raiz (pixeles, +Y hacia abajo) para que lo mas bajo del cuerpo en esta pose toque el
    suelo (y = 24 en el modelo: los pies de la entidad)."""
    M = mjj.matrices(hs, pose)
    bajo = -1e9
    for i, h in enumerate(hs):
        if not h.d:
            continue
        pts = np.array(list(h.d.keys()), float)[::3] * h.esc
        q = M[i] @ np.c_[pts, np.ones(len(pts))].T
        bajo = max(bajo, float(q[1].max()))
    return suelo - bajo


def tick(s):
    return int(round(s * 20))


# Las estelas de las armas: la base y la punta de la pieza en cada tick de la animacion (el cliente pinta la cinta
# entre los ultimos ticks donde va deprisa).
TRAZOS = {
    'moctezuma': {'NORMAL': ('macuahuitl', (0, 3, 0), (0, 31, 0)), 'AREA': ('macuahuitl', (0, 3, 0), (0, 31, 0))},
    'yiatzo': {'NORMAL': ('baston', (0, -34, 0), (0, -50, 0))},
    'atlahua': {'NORMAL': ('tridente', (0, -24, 0), (0, -45, 0)), 'AREA': ('tridente', (0, -24, 0), (0, -45, 0))},
    'xiuhquetzal': {'NORMAL': ('pico', (0, 0, -2), (0, 3, -7))},
}


def java_geometria(nombre, hs, anims, puntos, tiempos, anclas, extra=''):
    C = clase(nombre) + 'Geometria'
    L = ['package com.atalaya.entity;', '',
         'import net.minecraft.world.phys.Vec3;', '',
         '/**',
         f' * Medidas de {TITULO[nombre]} que comparten servidor y cliente. GENERADO por',
         ' * materiales/generadores/minijefes_anim.py desde las mismas poses que las animaciones.',
         ' *',
         ' * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda, y hacia',
         ' * arriba desde los pies, z hacia delante (puntoMundo los pasa al mundo con su giro).',
         ' * Las anclas son de los efectos del cliente: la pieza (su indice en la malla) y un punto',
         ' * suyo en pixeles de la malla.',
         ' */',
         f'public final class {C} {{', '',
         f'    private {C}() {{', '    }', '',
         '    /** Lo que mide el boceto en el mundo: el renderer escala la malla por esto (bloques por 16 pixeles). */',
         f'    public static final float ESCALA = {fj(mj.ESCALA[nombre])};', '']
    for k, (x, y, z) in puntos.items():
        L.append(f'    public static final Vec3 {k} = new Vec3({x:.3f}, {y:.3f}, {z:.3f});')
    L.append('')
    for k, v in tiempos.items():
        if isinstance(v, float):
            L.append(f'    public static final float {k} = {fj(v)};')
        else:
            L.append(f'    public static final int {k} = {v};')
    L.append('')
    for k, (pieza, local) in anclas.items():
        i = mjj._idx(hs, pieza)
        h = hs[i]
        x, y, z = (np.array(local, float) * h.esc)
        L.append(f'    /** {pieza} */')
        L.append(f'    public static final int {k}_PIEZA = {i};')
        L.append(f'    public static final float[] {k} = {{{fj(x)}, {fj(y)}, {fj(z)}}};')
    L.append('')
    for anim, (pieza, base, punta) in TRAZOS.get(nombre, {}).items():
        filas = []
        for k in range(tick(anims[anim].dur) + 1):
            pose = anims[anim].en(hs, k / 20.0)
            bx, by, bz = bloques(nombre, hs, pose, pieza, base)
            tx, ty, tz = bloques(nombre, hs, pose, pieza, punta)
            filas.append(f'{{{bx:.2f}F, {by:.2f}F, {bz:.2f}F, {tx:.2f}F, {ty:.2f}F, {tz:.2f}F}}')
        L.append(f'    /** La base y la punta de {pieza} en cada tick de {anim} (bloques, en el cuerpo): su estela. */')
        L.append(f'    public static final float[][] TRAZO_{anim} = {{' + ', '.join(filas) + '};')
    L.append('')
    despertar = anims['DESPERTAR']
    for nom, (pieza, local) in (('CABEZA', CABEZA[nombre]), ('PECHO', PECHO[nombre])):
        filas = []
        for k in range(0, tick(despertar.dur) + 1, 5):
            x, y, z = (round(v, 2) + 0.0 for v in bloques(nombre, hs, despertar.en(hs, k / 20.0), pieza, local))
            filas.append(f'{{{x:.2f}F, {y:.2f}F, {z:.2f}F}}')
        L.append(f'    /** {nom.capitalize()} en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */')
        L.append(f'    public static final float[][] {nom}_DESPERTAR = {{' + ', '.join(filas) + '};')
    L.append('')
    for nom in ('cabeza', 'pecho'):
        L.append(f'    public static Vec3 {nom}Despertar(float ticks) {{')
        L.append(f'        return tabla({nom.upper()}_DESPERTAR, ticks / 5.0F);')
        L.append('    }')
        L.append('')
    L += ['    private static Vec3 tabla(float[][] t, float f) {',
          '        int n = t.length - 1;',
          '        f = Math.max(0.0F, Math.min(n, f));',
          '        int i = Math.min((int) f, n - 1);',
          '        float k = f - i;',
          '        return new Vec3(t[i][0] + (t[i + 1][0] - t[i][0]) * k, t[i][1] + (t[i + 1][1] - t[i][1]) * k,',
          '                t[i][2] + (t[i + 1][2] - t[i][2]) * k);',
          '    }']
    if extra:
        L.append(extra)
    L.append('}')
    return '\n'.join(L) + '\n'


def zancada(nombre, hs, a, pie, local=(0, 2, -3), n=200):
    """Lo deprisa que va hacia atras el pie que apoya (bloques por tick a ritmo nominal): lo que tiene que avanzar el
    cuerpo para que no resbale."""
    T = a.dur
    ps = np.array([bloques(nombre, hs, a.en(hs, T * k / n), pie, local) for k in range(n + 1)])
    dz = np.diff(ps[:, 2]) / (T / n * 20)
    apoyo = ps[:-1, 1] < ps[:, 1].min() + 0.04
    return round(float(-dz[apoyo].mean()), 4)


# ----------------------------------------------------------------------
#  Hojas de control
# ----------------------------------------------------------------------
_LOSA = np.zeros((16, 16, 4), np.uint8)
_LOSA[...] = (190, 196, 190, 255)
_LOSA[0, :] = _LOSA[:, 0] = (150, 158, 150, 255)


def _suelo(lz, cam, n=7):
    for i in range(-n, n):
        for j in range(-n, n):
            P = [(i, 0, j), (i + 1, 0, j), (i + 1, 0, j + 1), (i, 0, j + 1)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [P[k] for k in tri], [((0, 0), (1, 0), (1, 1), (0, 1))[k] for k in tri], _LOSA,
                             np.array([0.95, 0.95, 0.95]))


def hoja(nombre, hs, malla, a, tiempos, out, guinadas=(-30, 60), W=300, H=360):
    ancho, alto, base, brillo = malla
    fotos = []
    esc = mj.ESCALA[nombre]
    for s in tiempos:
        pose = a.en(hs, s)
        for g in guinadas:
            cam = vr.Camara(ojo=(0, 3.4 * esc, -8.6 * esc), objetivo=(0, 2.7 * esc, 0), fov=58, ancho=W, alto=H)
            lz = vr.Lienzo(W, H)
            _suelo(lz, cam)
            mjj.dibujar(lz, cam, hs, mjj.matrices(hs, pose), ancho, alto, base, brillo, esc, g)
            col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
            al = lz.alfa[..., None]
            fondo = np.ones((H, W, 3)) * np.array([0.86, 0.87, 0.9])
            arr = col * al + fondo * (1 - al)
            im = Image.fromarray((arr * 255).astype(np.uint8))
            ImageDraw.Draw(im).text((6, 4), f'{a.nombre} {s:.2f}s', fill=(20, 20, 30))
            fotos.append(im)
    filas = len(guinadas)
    hojai = Image.new('RGB', (W * len(tiempos), H * filas), (255, 255, 255))
    for i, im in enumerate(fotos):
        hojai.paste(im, ((i // filas) * W, (i % filas) * H))
    hojai.save(os.path.join(out, f'{nombre}_{a.nombre.lower()}.jpg'), quality=88)


TITULO = {'moctezuma': 'Moctezuma, el Guerrero Aguila de Jade', 'yiatzo': 'Yiatzo, el Mago del Viento',
          'atlahua': 'Atlahua, el Triton de las Profundidades', 'xiuhquetzal': 'Xiuhquetzal, el Fenix de Llamas'}
# La cabeza (el centro de la cara) y el pecho de cada uno: la camara de la presentacion los sigue.
CABEZA = {'moctezuma': ('cabeza', (0, -7, -3)), 'yiatzo': ('capucha', (0, -6, -1)), 'atlahua': ('cabeza', (0, -6, -3)),
          'xiuhquetzal': ('cabeza', (0, -3.5, -1))}
PECHO = {'moctezuma': ('torso', (0, -12, -4)), 'yiatzo': ('cuerpo', (0, -18, -4)), 'atlahua': ('torso', (0, -13, -5)),
         'xiuhquetzal': ('cuerpo', (0, -9, -5))}

MINIJEFES = {}


def registrar(nombre):
    def deco(f):
        MINIJEFES[nombre] = f
        return f
    return deco


# ======================================================================
#  Moctezuma, el Guerrero Aguila de Jade
# ======================================================================
@registrar('moctezuma')
def moctezuma(hs):
    """Guerrero: el escudo por delante, el macuahuitl en la derecha. Anda con paso marcial (los pies plantados) y pega
    a dos tiempos; salta y cae con el escudo; invoca la tormenta con el arma alzada."""
    PI = Pierna(hs, 1)
    PD = Pierna(hs, -1)
    a = {}
    muelles = [Muelle('penacho', 1.0, 70, 8, 16), Muelle('faldon_frente', 0.35, 45, 6, 55),
               Muelle('faldon_atras', 0.35, 45, 6, 55), Muelle('hombrera_izq', 1.0, 110, 10, 8),
               Muelle('hombrera_der', 1.0, 110, 10, 8)]

    def piernas(baja=0.0, avanza=0.0, izq=(0.0, 0.0), der=(0.0, 0.0), punta_i=0.0, punta_d=0.0, abre=0.0):
        """Las dos piernas con los tobillos donde toca (en la pelvis, desplazados (dy, dz) de su sitio de pie) cuando
        la pelvis baja 'baja' pixeles y avanza 'avanza'."""
        bi = PI.reposo() + np.array([izq[0] - baja, izq[1] + avanza])
        bd = PD.reposo() + np.array([der[0] - baja, der[1] + avanza])
        return sumar(PI.pose(bi, punta_i, abre), PD.pose(bd, punta_d, abre), {'pelvis': p(0, baja, -avanza)})

    def arma(ang, arriba=-1.0, fuera=0.0, delante=0.0, codo=0.0, muneca=None):
        """El brazo del macuahuitl; ang: la hoja respecto al antebrazo (0 la sigue, negativo hacia delante)."""
        return brazo(hs, -1, arriba, fuera, delante, codo, muneca, ang, 'macuahuitl')

    def escudo(arriba=-1.0, fuera=0.0, delante=0.0, codo=0.0):
        return brazo(hs, 1, arriba, fuera, delante, codo)

    # --- Reposo: respira, cambia el peso de pierna, mira alrededor ---
    T_REP = 4.0

    def reposo(s):
        w = 2 * math.pi * s / T_REP
        return sumar(
            piernas(baja=0.5 + 0.5 * math.sin(w)),
            {'pelvis': r(0, 0, 1.2 * math.sin(w / 2))},
            {'torso': r(1.2 * math.sin(w + 0.6), 3 * math.sin(w / 2), -1.0 * math.sin(w / 2))},
            {'cabeza': r(-2 + 2 * math.sin(w + 1.2), 10 * math.sin(w / 2 + 0.8), 0)},
            {'hombro_izq': r(1.5 * math.sin(w + 0.9)), 'hombro_der': r(2 * math.sin(w + 1.1), 0, -1.5 * math.sin(w))},
            {'macuahuitl': r(3 * math.sin(w / 2), 0, 0), 'mano_der': r(0, 4 * math.sin(w / 2 + 0.4), 0)},
        )
    a['REPOSO'] = Anim('REPOSO', T_REP, reposo, True, muelles)

    # --- Andar: paso marcial; el tobillo hace su ciclo (apoyo hacia atras, vuelo en arco) ---
    T_AND = 1.2
    ZANC = 9.0      # medio paso (pixeles): el pie va de -ZANC (delante) a +ZANC en el apoyo
    APOYO = 0.58

    def ciclo_pie(f):
        """(dy, dz) del tobillo en la fase f (0-1): apoyo de 0 a APOYO (de delante atras), vuelo el resto."""
        f %= 1.0
        if f < APOYO:
            u = f / APOYO
            return 0.0, -ZANC + 2 * ZANC * u
        u = (f - APOYO) / (1 - APOYO)
        return -5.5 * math.sin(math.pi * u) ** 1.2, ZANC - 2 * ZANC * _suave(u)

    def andar(s):
        f = s / T_AND
        w = 2 * math.pi * f
        iy, iz = ciclo_pie(f)
        dy, dz = ciclo_pie(f + 0.5)
        # La pelvis baja al cargar cada pie (dos veces por ciclo) y gira con la pierna que avanza.
        baja = 1.4 + 1.0 * math.cos(2 * w)
        return sumar(
            piernas(baja=baja, izq=(iy, iz), der=(dy, dz),
                    punta_i=-10 * max(0.0, math.sin(w + 0.4)), punta_d=-10 * max(0.0, math.sin(w + math.pi + 0.4))),
            {'pelvis': r(2.0, 7 * math.sin(w), 2.0 * math.sin(w))},
            {'torso': r(4.0, -9 * math.sin(w), -1.5 * math.sin(w))},
            {'cabeza': r(-3.0, 2 * math.sin(w), 0)},
            # El brazo del arma va con el paso (contra la pierna derecha); el escudo, firme por delante.
            {'hombro_der': r(-14 * math.sin(w), 0, 0), 'antebrazo_der': r(-6 - 6 * math.sin(w))},
            {'hombro_izq': r(-6 + 4 * math.sin(w)), 'antebrazo_izq': r(-4)},
        )
    a['ANDAR'] = Anim('ANDAR', T_AND, andar, True, muelles)

    # --- Dormido: de rodilla (la derecha en el suelo), la cabeza gacha, el macuahuitl clavado delante ---
    def arrodillado(k=1.0):
        q = sumar(piernas(baja=11.0, izq=(0.0, -12.0), der=(0.6, 10.9), punta_d=50), {'pelvis': p(0, 0, 1.5)})
        return escalar(q, k)

    DORMIDO = sumar(
        arrodillado(),
        {'torso': r(16, -6, 0), 'cuello': r(10), 'cabeza': r(22, 0, 0)},
        arma(-8, arriba=-0.55, fuera=0.1, delante=0.83, codo=-6),
        escudo(arriba=-0.75, fuera=0.25, delante=0.6, codo=-50),
    )

    def dormido(s):
        w = 2 * math.pi * s / 5.0
        return sumar(DORMIDO, {'torso': r(1.2 * math.sin(w)), 'pelvis': p(0, 0.3 * math.sin(w), 0)})
    a['DORMIDO'] = Anim('DORMIDO', 5.0, dormido, True, muelles)

    # --- Despertar (7 s): abre los ojos, alza la cabeza, se levanta arrancando el arma del suelo, golpea el escudo
    #     dos veces, alza el macuahuitl al cielo y grita como un aguila; acaba en guardia ---
    ABRE, SE_ALZA, ALZADO, RUGE, DUR_D = 1.0, 2.2, 3.6, 4.9, 7.0
    escudo_frente = escudo(arriba=-0.15, fuera=0.25, delante=0.95, codo=-75)
    alzado = sumar(arma(-60, arriba=0.15, fuera=0.55, delante=0.6, codo=-65), escudo_frente,
                   {'torso': r(-4, 10, 0), 'cabeza': r(-6, -8)}, piernas(baja=1.5, izq=(0, -3), der=(0, 3)))
    arma_atras = sumar(arma(-40, arriba=0.75, fuera=0.6, delante=-0.1, codo=-80), escudo_frente,
                       {'torso': r(-3, 18, 0), 'cabeza': r(0, -10)}, piernas(baja=2.0, izq=(0, -3), der=(0, 3)))
    choque = sumar(arma(-70, arriba=0.05, fuera=-0.45, delante=0.9, codo=-30), escudo_frente,
                   {'torso': r(5, -14, 0), 'cabeza': r(4, 6)}, piernas(baja=3.0, izq=(0, -3), der=(0, 3)))
    grito = sumar(arma(-10, arriba=0.95, fuera=0.3, delante=0.05, codo=-8),
                  escudo(arriba=0.05, fuera=0.95, delante=0.3, codo=-30),
                  {'torso': r(-12, 6, 0), 'cuello': r(-12), 'cabeza': r(-26, 0, 0)},
                  piernas(baja=3.0, izq=(0, -5), der=(0, 5)))
    guardia = sumar(escalar(alzado, 0.4), piernas(baja=0.6, izq=(0, -1), der=(0, 1)))
    medio = sumar(arrodillado(0.45), {'torso': r(14, -4, 0), 'cabeza': r(-6)},
                  arma(-40, arriba=-0.2, fuera=0.4, delante=0.85, codo=-30), escudo(arriba=-0.6, fuera=0.3, delante=0.7, codo=-40))
    f_desp = linea(
        (0.0, DORMIDO, 'suave'),
        (ABRE, sumar(DORMIDO, {'cabeza': r(-8), 'cuello': r(-4)}), 'suave'),
        (SE_ALZA, sumar(DORMIDO, {'cabeza': r(-22), 'cuello': r(-10), 'torso': r(-6)}), 'suave'),
        (SE_ALZA + 0.7, medio, 'sale'),
        (ALZADO, alzado, 'suave'),
        (ALZADO + 0.35, arma_atras, 'sale'),
        (ALZADO + 0.55, choque, 'golpe'),
        (ALZADO + 0.8, arma_atras, 'sale'),
        (ALZADO + 1.0, choque, 'golpe'),
        (RUGE - 0.12, sumar(grito, {'cabeza': r(14), 'torso': r(8)}), 'suave'),
        (RUGE + 0.25, grito, 'golpe'),
        (RUGE + 1.3, sumar(grito, {'cabeza': r(4)}), 'suave'),
        (DUR_D - 0.6, guardia, 'suave'),
        (DUR_D, {}, 'suave'),
    )

    def despertar(s):
        return sumar(f_desp(s), {'cabeza': r(temblor(s, RUGE, RUGE + 1.2, 2.5, 16))},
                     {'torso': r(temblor(s, RUGE, RUGE + 1.2, 1.0, 12))})
    a['DESPERTAR'] = Anim('DESPERTAR', DUR_D, despertar, False, muelles)

    # --- Normal: Corte de Obsidiana. Barrido de derecha a izquierda (golpe 1), paso al frente y tajo de arriba abajo
    #     (golpe 2) ---
    N_CARGA, N_G1, N_G2, DUR_N = 0.34, 0.5, 1.02, 1.7
    carga1 = sumar({'torso': r(4, 36, 0), 'pelvis': r(0, 14, 0), 'cabeza': r(0, -26)},
                   arma(-35, arriba=0.55, fuera=0.75, delante=-0.35, codo=-85),
                   escudo(arriba=-0.1, fuera=0.1, delante=1.0, codo=-70),
                   piernas(baja=3.5, izq=(0, -5), der=(0, 6)))
    barrido = sumar({'torso': r(6, -40, 0), 'pelvis': r(0, -16, 0), 'cabeza': r(0, 22)},
                    arma(-80, arriba=0.05, fuera=-0.55, delante=0.85, codo=-8),
                    escudo(arriba=-0.5, fuera=0.85, delante=0.2, codo=-40),
                    piernas(baja=4.5, izq=(0, -6), der=(0, 6)))
    alza2 = sumar({'torso': r(-12, -4, 0), 'pelvis': r(0, -4, 0), 'cabeza': r(-8, 0)},
                  arma(-30, arriba=0.95, fuera=0.15, delante=-0.15, codo=-70),
                  escudo(arriba=-0.1, fuera=0.3, delante=0.95, codo=-60),
                  piernas(baja=2.0, avanza=4.0, izq=(0, -8), der=(-3, 9)))
    tajo = sumar({'torso': r(26, 0, 0), 'pelvis': r(6, 0, 0), 'cabeza': r(-14, 0)},
                 arma(-80, arriba=-0.45, fuera=0.1, delante=0.9, codo=-6),
                 escudo(arriba=-0.6, fuera=0.75, delante=0.2, codo=-30),
                 piernas(baja=7.0, avanza=8.0, izq=(0, -12), der=(0, 8)))
    f_norm = linea(
        (0.0, {}, 'suave'),
        (N_CARGA, carga1, 'sale'),
        (N_G1, barrido, 'seco'),
        (0.62, sumar(barrido, {'torso': r(0, -6, 0)}), 'sale'),
        (0.86, alza2, 'suave'),
        (N_G2, tajo, 'seco'),
        (1.25, sumar(tajo, {'torso': r(-3)}), 'sale'),
        (DUR_N, {}, 'suave'),
    )
    a['NORMAL'] = Anim('NORMAL', DUR_N, f_norm, False, muelles)

    # --- Area: Terremoto del Aguila. Se agacha, salta (3,5 bloques), cae con el escudo y el arma contra el suelo ---
    A_DESPEGA, A_CAE, DUR_A = 0.5, 1.2, 2.3
    agacha = sumar(piernas(baja=8.0, izq=(0, -3), der=(0, 3)), {'torso': r(20), 'cabeza': r(-12)},
                   arma(-50, arriba=-0.4, fuera=0.6, delante=0.4, codo=-50), escudo(arriba=-0.4, fuera=0.5, delante=0.6, codo=-50))
    vuelo = sumar({'raiz': p(0, -42, 0)}, piernas(baja=-1.0, izq=(-9, -2), der=(-7, 4)), {'torso': r(-14), 'cabeza': r(-8)},
                  arma(-40, arriba=0.95, fuera=0.25, delante=0.15, codo=-45),
                  escudo(arriba=0.45, fuera=0.3, delante=0.85, codo=-35))
    golpe = sumar(piernas(baja=11.0, izq=(0, -7), der=(0, 5)), {'torso': r(38), 'cabeza': r(-20)},
                  arma(-60, arriba=-0.55, fuera=0.25, delante=0.8, codo=-5),
                  escudo(arriba=-0.5, fuera=0.2, delante=0.85, codo=-10))
    f_area = linea(
        (0.0, {}, 'suave'),
        (A_DESPEGA - 0.05, agacha, 'sale'),
        (A_DESPEGA + 0.35, vuelo, 'sale'),
        (A_CAE - 0.12, sumar(vuelo, {'raiz': p(0, 6, 0)}), 'suave'),
        (A_CAE, golpe, 'cae'),
        (A_CAE + 0.45, sumar(golpe, {'torso': r(-4)}), 'sale'),
        (DUR_A, {}, 'suave'),
    )

    def area(s):
        return sumar(f_area(s), {'torso': r(temblor(s, A_CAE, A_CAE + 0.4, 2.0, 14))})
    a['AREA'] = Anim('AREA', DUR_A, area, False, muelles)

    # --- Especial: Tormenta de Obsidiana y Jade. Alza el macuahuitl al cielo y lo gira (las tres lluvias), y lo clava
    #     en el suelo (la erupcion de jade) ---
    E_ALZA, E_LLUVIAS, E_CLAVA, DUR_E = 0.8, (1.6, 2.2, 2.8), 3.7, 5.0
    alza = sumar(piernas(baja=3.0, izq=(0, -5), der=(0, 5), abre=6), {'torso': r(-12, 0, 0), 'cuello': r(-8), 'cabeza': r(-24, 0)},
                 arma(-5, arriba=1.0, fuera=0.1, delante=0.06, codo=-4),
                 escudo(arriba=0.15, fuera=1.0, delante=0.25, codo=-20))
    # Antes de clavarlo lo alza recto por encima de la cabeza, algo atras y por su lado (con el codo casi estirado):
    # antes lo doblaba tras la nuca y la hoja cruzaba el casco y el penacho (revision del 11-10-2026).
    alto_clava = sumar(piernas(baja=2.0, izq=(0, -4), der=(0, 4)), {'torso': r(-16, 6, 0), 'cabeza': r(-10)},
                       arma(8, arriba=1.0, fuera=0.3, delante=-0.3, codo=-12),
                       escudo(arriba=0.0, fuera=0.6, delante=0.8, codo=-40))
    clava = sumar(piernas(baja=12.0, izq=(0, -8), der=(0, 6)), {'torso': r(42), 'cabeza': r(-24)},
                  arma(-80, arriba=-0.72, fuera=0.12, delante=0.68, codo=-4),
                  escudo(arriba=-0.4, fuera=0.6, delante=0.7, codo=-20))
    f_esp = linea(
        (0.0, {}, 'suave'),
        (E_ALZA, alza, 'sale'),
        (E_CLAVA - 0.32, alto_clava, 'suave'),
        (E_CLAVA, clava, 'cae'),
        (E_CLAVA + 0.6, sumar(clava, {'torso': r(-4)}), 'sale'),
        (DUR_E, {}, 'suave'),
    )

    def especial(s):
        q = f_esp(s)
        # Llama a la tormenta removiendo el cielo: el brazo alzado traza circulos (dos vueltas que se aceleran) con la
        # hoja hacia arriba, el cuerpo se mece contra el brazo, y empuja con cada lluvia. (Antes el arma giraba sobre
        # su propia hoja, como un tornillo: Juan, "su mano o su espada es media rara lo que mueve".)
        u = min(1.0, max(0.0, (s - E_ALZA) / (E_CLAVA - 0.45 - E_ALZA)))
        k = ventana(s, E_ALZA, E_CLAVA - 0.45, 0.3, 0.25)
        if k > 0:
            th = 2 * math.pi * 2.0 * u ** 1.3
            circulo = sumar(arma(-5, arriba=0.92, fuera=0.1 + 0.32 * math.cos(th), delante=0.06 + 0.32 * math.sin(th), codo=-12),
                            {'torso': r(-12 + 3 * math.sin(th), -7 * math.cos(th), 4 * math.sin(th)), 'cabeza': r(-24, 4 * math.cos(th), 0)})
            q = {**q, **mezclar({n: q.get(n, {}) for n in circulo}, circulo, k)}
        for tl in E_LLUVIAS:
            k = ventana(s, tl, tl, 0.08, 0.25)
            q = sumar(q, {'torso': r(-3 * k), 'hombro_der': r(-6 * k)})
        return sumar(q, {'torso': r(temblor(s, E_CLAVA, E_CLAVA + 0.5, 2.0, 14))})
    a['ESPECIAL'] = Anim('ESPECIAL', DUR_E, especial, False, muelles)

    # --- Muerte: se tambalea, cae de rodillas soltando el arma y se desploma de frente ---
    DUR_M = 3.2
    tambalea = sumar(piernas(baja=2.0, izq=(0, 3), der=(-2, -6)), {'torso': r(-14, 10, 6), 'cabeza': r(-20, 10)},
                     arma(-20, arriba=-0.6, fuera=0.75, delante=0.0, codo=-10),
                     escudo(arriba=-0.5, fuera=0.85, delante=0.0, codo=-20))
    rodillas = sumar(piernas(baja=13.0, izq=(-1, 9), der=(-1, 9), punta_i=40, punta_d=40),
                     {'torso': r(14, 0, 0), 'cabeza': r(20, 0, 0)},
                     arma(30, arriba=-1.0, fuera=0.15, delante=0.0, codo=-5),
                     escudo(arriba=-1.0, fuera=0.2, delante=0.1, codo=-15))
    cae = sumar(rodillas, {'pelvis': rp((70, 0, 0), (0, 3, -6)), 'torso': r(14), 'cabeza': r(-20)},
                arma(30, arriba=0.3, fuera=0.4, delante=0.85, codo=-10), escudo(arriba=0.3, fuera=0.4, delante=0.85, codo=-20))
    f_muerte = linea(
        (0.0, {}, 'suave'),
        (0.45, tambalea, 'sale'),
        (1.3, rodillas, 'cae'),
        (1.6, sumar(rodillas, {'torso': r(-6)}), 'sale'),
        (2.4, cae, 'cae'),
        (DUR_M, cae, 'suave'),
    )
    a['MUERTE'] = Anim('MUERTE', DUR_M, f_muerte, False, muelles)

    tiempos = {
        'DESPERTAR_ABRE': tick(ABRE), 'DESPERTAR_SE_ALZA': tick(SE_ALZA), 'DESPERTAR_ALZADO': tick(ALZADO),
        'DESPERTAR_RUGE': tick(RUGE), 'DURACION_DESPERTAR': tick(DUR_D),
        'DESPERTAR_ARRANCA': tick(SE_ALZA + 0.7), 'DESPERTAR_CHOQUE_1': tick(ALZADO + 0.55),
        'DESPERTAR_CHOQUE_2': tick(ALZADO + 1.0),
        'DURACION_NORMAL': tick(DUR_N), 'NORMAL_CARGA': tick(N_CARGA), 'NORMAL_GOLPE_1': tick(N_G1),
        'NORMAL_GOLPE_2': tick(N_G2),
        'DURACION_AREA': tick(DUR_A), 'AREA_DESPEGA': tick(A_DESPEGA), 'AREA_CAE': tick(A_CAE),
        'DURACION_ESPECIAL': tick(DUR_E), 'ESPECIAL_ALZA': tick(E_ALZA), 'ESPECIAL_CLAVA': tick(E_CLAVA),
        'ESPECIAL_LLUVIA_1': tick(E_LLUVIAS[0]), 'ESPECIAL_LLUVIA_2': tick(E_LLUVIAS[1]),
        'ESPECIAL_LLUVIA_3': tick(E_LLUVIAS[2]),
        'DURACION_MUERTE': tick(DUR_M) + 50, 'MUERTE_RODILLAS': tick(1.3), 'MUERTE_CAE': tick(2.4),
        'DISOLVER_DESDE': tick(DUR_M) - 6,
        'PERIODO_ANDAR': tick(T_AND),
    }
    puntos = {
        'CABEZA': bloques('moctezuma', hs, {}, *CABEZA['moctezuma']),
        'PECHO': bloques('moctezuma', hs, {}, *PECHO['moctezuma']),
        'ARMA_BARRIDO': bloques('moctezuma', hs, a['NORMAL'].en(hs, N_G1), 'macuahuitl', (0, 18, 0)),
        'ARMA_TAJO': bloques('moctezuma', hs, a['NORMAL'].en(hs, N_G2), 'macuahuitl', (0, 28, 0)),
        'GOLPE_AREA': bloques('moctezuma', hs, a['AREA'].en(hs, A_CAE), 'mano_izq', (0, 4, -2)),
        'PUNTA_ALZADA': bloques('moctezuma', hs, a['ESPECIAL'].en(hs, 2.0), 'macuahuitl', (0, 31, 0)),
        'CLAVA': bloques('moctezuma', hs, a['ESPECIAL'].en(hs, E_CLAVA), 'macuahuitl', (0, 28, 0)),
    }
    anclas = {'HOJA_BASE': ('macuahuitl', (0, 4, 0)), 'HOJA_PUNTA': ('macuahuitl', (0, 31, 0)),
              'OJOS': ('cabeza', (0, -7, -5)), 'GEMA': ('pelvis', (0, -1.5, -6)), 'ESCUDO': ('escudo', (0, 1, 0))}
    return a, tiempos, puntos, anclas


@registrar('yiatzo')
def yiatzo(hs):
    """El mago no anda: flota. Version del 11-10-2026 (Juan: "las animaciones de boss de viento ... estan raras no
    parecen reales"): antes subia y bajaba como un ascensor, los brazos iban casi rectos y el Ciclon lo hacia girar
    entero tres vueltas. Ahora:
      - flota con deriva: sube y baja despacio y se mece en un ocho; el cuerpo se inclina hacia donde va y la capucha
        y los brazos llegan tarde (cada pieza con su retraso);
      - los brazos doblan el codo como brazos de verdad;
      - cada golpe tiene su anticipacion (coge aire), el golpe con el cuerpo detras y el seguimiento (el baston sigue
        de largo y el cuerpo se recoge);
      - el Ciclon lo dirige con el baston, trazando circulos por encima de la cabeza, sin girar sobre si mismo.
    La capa le sigue con retraso (fisica) y las losas de glifos le dan vueltas."""
    a = {}
    muelles = [Muelle('capa', 0.3, 38, 5, 60), Muelle('capa2', 0.25, 34, 4.5, 60),
               # Los jirones: ondean, pero poco respecto a la tunica, para que no se abra la junta.
               Muelle('falda', 0.75, 40, 6, 10), Muelle('falda2', 0.8, 36, 5.5, 6)]
    piedras = [h.nombre for h in hs if h.nombre.startswith('piedra')]
    origen = {n: hs[mjj._idx(hs, n)].pivote.copy() for n in piedras}

    def baston(arriba=-1.0, fuera=0.0, delante=0.0, codo=0.0, ang=None, muneca=None):
        """El brazo del baston. ang: el giro total del baston en la mano (180: el orbe sigue al brazo); sin ang, el
        baston queda a plomo con el orbe arriba."""
        if ang is None:
            d = np.array([-fuera, -arriba, -delante], float)
            d /= np.linalg.norm(d)
            ang = -(math.degrees(math.asin(max(-1.0, min(1.0, d[2])))) + codo)
        return brazo(hs, -1, arriba, fuera, delante, codo, muneca, ang, 'baston')

    def libro(arriba=-1.0, fuera=0.0, delante=0.0, codo=0.0, muneca=None):
        return brazo(hs, 1, arriba, fuera, delante, codo, muneca)

    def losas(ang, radio=1.0, alto=0.0, giro=0.0, bob=0.0, s=0.0):
        """Las losas giran 'ang' grados alrededor de el (en el plano), a 'radio' veces su distancia, subidas 'alto'
        pixeles, girando sobre si mismas 'giro' grados, y cada una sube y baja 'bob' pixeles."""
        q = {}
        c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for i, n in enumerate(piedras):
            o = origen[n]
            x, z = o[0] * radio, o[2] * radio
            nx, nz = x * c - z * sn, x * sn + z * c
            dy = -alto + bob * math.sin(2 * math.pi * s / 4.0 + i * 1.3)
            q[n] = {'pos': (nx - o[0], dy, nz - o[2]), 'rot': (0, giro, 0)}
        return q

    def suelo_losas(k=1.0):
        """Las losas tiradas por el suelo, alrededor de el."""
        q = {}
        for i, n in enumerate(piedras):
            o = origen[n]
            # El suelo, en el marco del cuerpo (la raiz flota 8 pixeles): y = 24 + 8 menos media losa.
            q[n] = {'pos': (o[0] * 0.15, (24 + 8 - 2.5 - o[1]) * k, -o[2] * 0.2), 'rot': (80 * k, i * 37, 10 * k)}
        return q

    def flota(s, alto=3.0, deriva=1.0, periodo=8.0):
        """La deriva del que flota: sube y baja (la mitad del periodo) y se mece en un ocho (x una vez por periodo, z
        dos), con el cuerpo inclinado hacia donde va y la capucha que llega tarde."""
        w = 2 * math.pi * s / periodo
        x = 1.6 * deriva * math.sin(w)
        z = 1.1 * deriva * math.sin(2 * w + 0.7)
        vx, vz = math.cos(w), math.cos(2 * w + 0.7)
        # El bajo de la tunica ondea: se queda atras de la deriva y hace una ola que baja (los jirones, mas).
        ola = math.sin(4 * w + 0.4)
        return sumar({'raiz': p(x, alto * math.sin(2 * w), z)},
                     {'cuerpo': r(1.5 * math.sin(2 * w + 0.6) + 2.2 * deriva * vz, 3 * math.sin(w), -2.6 * deriva * vx)},
                     {'capucha': r(-2.0 * math.sin(2 * w + 1.3) - 1.4 * deriva * vz, 5 * math.sin(w + 1.1), 1.8 * deriva * vx)},
                     {'capa': r(2.0 * deriva * vz, 0, 1.5 * deriva * vx)},
                     {'falda': r(1.5 + 2.0 * deriva * vz + 1.2 * ola, 1.2 * math.sin(w + 0.5), -1.8 * deriva * vx),
                      'falda2': r(0.8 + 1.4 * deriva * math.cos(2 * w + 1.5) + 1.2 * math.sin(4 * w + 1.4),
                                  1.0 * math.sin(w + 1.2), -1.4 * deriva * math.cos(w + 0.8))})

    def brazos_vivos(s, k=1.0, periodo=8.0):
        """Los brazos nunca quietos del todo: el hombro, el codo y la muneca respiran con un poco de retraso."""
        w = 2 * math.pi * s / periodo
        return escalar({'hombro_der': r(2.5 * math.sin(2 * w + 0.4), 0, 1.5 * math.sin(w)),
                        'hombro_izq': r(-2.5 * math.sin(2 * w + 0.9), 0, -1.5 * math.sin(w + 0.5)),
                        'antebrazo_der': r(-3.5 * math.sin(2 * w + 1.0)), 'antebrazo_izq': r(-4.5 * math.sin(2 * w + 1.5)),
                        'libro': r(3 * math.sin(4 * w), 0, 0)}, k)

    # --- Reposo: flota con su deriva; las losas dan una vuelta cada 8 s ---
    T_REP = 8.0

    def reposo(s):
        return sumar(flota(s), brazos_vivos(s), losas(360.0 * s / T_REP, 1.0, 0.0, 360.0 * s / T_REP, 2.0, s))
    a['REPOSO'] = Anim('REPOSO', T_REP, reposo, True, muelles)

    # --- Andar (se desliza): inclinado hacia delante y algo ladeado, sube y baja dos veces por vuelta, el baston
    #     cruzado y el libro pegado; las losas giran mas deprisa y se le pegan ---
    T_AND = 4.0

    def andar(s):
        w = 2 * math.pi * s / T_AND
        return sumar(
            {'raiz': p(0.8 * math.sin(w), -2 + 1.6 * math.sin(2 * w), 0)},
            {'cuerpo': r(10 + 1.5 * math.sin(2 * w + 0.6), 4 * math.sin(w), 3 * math.sin(w + 0.4))},
            {'capucha': r(-7 - 1.5 * math.sin(2 * w + 1.3), -3 * math.sin(w + 0.8), -2 * math.sin(w + 1.0))},
            baston(arriba=-0.72, fuera=0.25, delante=0.6, codo=-40 + 4 * math.sin(2 * w + 0.5)),
            libro(arriba=-0.6, fuera=0.35, delante=0.7, codo=-62 + 4 * math.sin(2 * w + 1.0)),
            # Al deslizarse hacia delante el bajo de la tunica se queda atras y ondea.
            {'falda': r(6 + 2 * math.sin(4 * w), 1.2 * math.sin(w), 0), 'falda2': r(3 + 2 * math.sin(4 * w + 1.3), 1 * math.sin(w + 1), 0)},
            losas(360.0 * s / T_AND, 0.82, 4.0, 720.0 * s / T_AND, 1.5, s),
        )
    a['ANDAR'] = Anim('ANDAR', T_AND, andar, True, muelles)

    # --- Dormido: en el suelo, meditando; el baston clavado a su lado, las losas tiradas alrededor; respira ---
    DORMIDO = sumar(
        {'raiz': p(0, 9, 0)},
        {'cuerpo': r(10, 0, 0), 'capucha': r(22, 0, 0)},
        baston(arriba=-0.85, fuera=0.35, delante=0.4, codo=-40),
        libro(arriba=-0.9, fuera=0.2, delante=0.4, codo=-70),
    )
    DORMIDO_LOSAS = sumar(DORMIDO, suelo_losas())

    def dormido(s):
        w = 2 * math.pi * s / 6.0
        return sumar(DORMIDO_LOSAS, {'cuerpo': r(1.2 * math.sin(w)), 'capucha': r(1.8 * math.sin(w + 0.6)),
                                     'raiz': p(0, -0.6 * math.sin(w), 0)})
    a['DORMIDO'] = Anim('DORMIDO', 6.0, dormido, True, muelles)

    # --- Despertar (6,5 s): las losas tiemblan, se alzan una a una, el sube del suelo, alza el baston, abre el libro
    #     y lo baja (la onda de viento); las losas se ponen a girar ---
    ABRE, SE_ALZA, ALZADO, RUGE, DUR_D = 1.0, 2.0, 3.4, 4.4, 6.5
    alzado = sumar({'raiz': p(0, -10, 0)}, {'cuerpo': r(-6, 0, 0), 'capucha': r(-14, 0, 0)},
                   baston(arriba=0.92, fuera=0.3, delante=0.15, codo=-22, ang=180),
                   libro(arriba=0.3, fuera=0.9, delante=0.3, codo=-34))
    golpe_d = sumar({'raiz': p(0, -4, 0)}, {'cuerpo': r(12, 0, 0), 'capucha': r(6, 0, 0)},
                    baston(arriba=-0.55, fuera=0.15, delante=0.8, codo=-24),
                    libro(arriba=-0.2, fuera=0.95, delante=0.2, codo=-42))
    sigue_d = sumar({'raiz': p(0, -3, 0)}, {'cuerpo': r(17, 0, 0), 'capucha': r(12, 0, 0)},
                    baston(arriba=-0.75, fuera=0.05, delante=0.62, codo=-30),
                    libro(arriba=-0.35, fuera=0.9, delante=0.25, codo=-46))
    f_desp = linea(
        (0.0, DORMIDO, 'suave'),
        (ABRE, sumar(DORMIDO, {'capucha': r(-10, 0, 0)}), 'suave'),
        (SE_ALZA, sumar(DORMIDO, {'capucha': r(-16, 0, 0), 'cuerpo': r(-4, 0, 0)}), 'suave'),
        (ALZADO, alzado, 'suave'),
        (RUGE - 0.25, sumar(alzado, {'raiz': p(0, -3, 0), 'cuerpo': r(-6), 'capucha': r(-4)}), 'suave'),
        (RUGE, golpe_d, 'golpe'),
        (RUGE + 0.3, sigue_d, 'sale'),
        (RUGE + 1.1, sumar(golpe_d, {'raiz': p(0, -2, 0)}), 'suave'),
        (DUR_D, {}, 'suave'),
    )

    def despertar(s):
        q = sumar(f_desp(s), brazos_vivos(s, ventana(s, ALZADO, DUR_D, 0.6, 0.01)))
        # Las losas: tiemblan en el suelo, se alzan de una en una (cada 0,25 s) y se ponen a girar alrededor de el;
        # con el golpe se apartan, y al final estan en su sitio (una vuelta entera).
        u = _suave(min(1.0, max(0.0, (s - SE_ALZA) / (DUR_D - SE_ALZA))))
        ang = 360.0 * u
        radio = 1.0 + 0.4 * ventana(s, ALZADO, RUGE + 0.6, 0.8, 1.2)
        alto = 10.0 * ventana(s, ALZADO - 0.6, RUGE + 0.4, 0.8, 1.4)
        aire = losas(ang, radio, alto, ang * 2)
        suelo = suelo_losas()
        for i, n in enumerate(piedras):
            t0 = SE_ALZA + i * 0.25
            k = _suave(min(1.0, max(0.0, (s - t0) / 0.9)))
            e = mezclar({n: suelo[n]}, {n: aire[n]}, k)[n]
            tiembla = temblor(s, ABRE, t0 + 0.2, 6.0, 9, i)
            e['rot'] = (e['rot'][0] + tiembla, e['rot'][1], e['rot'][2])
            q[n] = e
        # Al subir del suelo se balancea un poco hasta encontrar el aire.
        q = sumar(q, flota(s, 1.5 * ventana(s, SE_ALZA + 0.5, DUR_D, 0.8, 0.01), ventana(s, SE_ALZA + 0.5, DUR_D, 0.8, 0.01)))
        return q
    a['DESPERTAR'] = Anim('DESPERTAR', DUR_D, despertar, False, muelles)

    # --- Normal: Rafaga de Viento. Coge aire, lleva el baston atras por encima del hombro (el cuerpo girado, el codo
    #     doblado), lo descarga en diagonal con todo el cuerpo detras (salen las tres cuchillas en N_SUELTA) y el baston
    #     sigue de largo hasta abajo; luego se recoge ---
    N_CARGA, N_SUELTA, DUR_N = 0.42, 0.58, 1.4
    coge = sumar({'cuerpo': r(-5, 8, 0), 'capucha': r(-6, -4, 0), 'raiz': p(0, -1.5, 0)},
                 baston(arriba=-0.55, fuera=0.4, delante=0.45, codo=-48), libro(arriba=-0.5, fuera=0.3, delante=0.8, codo=-55))
    carga = sumar({'cuerpo': r(-6, 30, 2), 'capucha': r(-4, -18, 0), 'raiz': p(0, -2.5, 1)},
                  baston(arriba=0.7, fuera=0.6, delante=-0.3, codo=-62, ang=170),
                  libro(arriba=-0.05, fuera=0.2, delante=1.0, codo=-34), losas(0, 1.1, 2.0, 0))
    pasa = sumar({'cuerpo': r(4, 6, 0), 'capucha': r(0, 0, 0), 'raiz': p(0, -1, -1)},
                 baston(arriba=0.45, fuera=0.1, delante=0.8, codo=-34, ang=180),
                 libro(arriba=-0.3, fuera=0.6, delante=0.6, codo=-40), losas(12, 1.1, 2.0, 20))
    suelta = sumar({'cuerpo': r(12, -24, 0), 'capucha': r(4, 12, 0), 'raiz': p(0, 1, -2)},
                   baston(arriba=-0.12, fuera=-0.32, delante=0.95, codo=-22, ang=180),
                   libro(arriba=-0.5, fuera=0.85, delante=0.1, codo=-42), losas(25, 1.1, 2.0, 40))
    sigue = sumar({'cuerpo': r(16, -34, -3), 'capucha': r(8, 16, 0), 'raiz': p(0, 2, -2.5)},
                  baston(arriba=-0.5, fuera=-0.5, delante=0.7, codo=-30, ang=170),
                  libro(arriba=-0.55, fuera=0.8, delante=0.05, codo=-46), losas(35, 1.08, 1.5, 55))
    f_norm = linea(
        (0.0, {}, 'suave'),
        (0.18, coge, 'suave'),
        (N_CARGA, carga, 'sale'),
        (0.52, pasa, 'entra'),
        (N_SUELTA, suelta, 'lineal'),
        (0.74, sigue, 'sale'),
        (1.0, sumar(sigue, {'cuerpo': r(-4, 6, 2)}), 'suave'),
        (DUR_N, {}, 'suave'),
    )
    a['NORMAL'] = Anim('NORMAL', DUR_N, lambda s: sumar(f_norm(s), flota(s, 1.0, 0.4, 2.8)), False, muelles)

    # --- Area: Tormenta de Viento. Se encoge (coge el viento), sube con los brazos abiertos (las losas se apartan y
    #     giran deprisa), tiembla un instante cargado y los baja de golpe: el anillo de viento sale de el; el golpe le
    #     hunde un poco y vuelve a subir ---
    A_SUELTA, DUR_A = 1.1, 2.4
    encoge = sumar({'raiz': p(0, 3, 0)}, {'cuerpo': r(10, 0, 0), 'capucha': r(8, 0, 0)},
                   baston(arriba=-0.6, fuera=0.3, delante=0.5, codo=-50), libro(arriba=-0.6, fuera=0.3, delante=0.6, codo=-60))
    abre = sumar({'raiz': p(0, -12, 0)}, {'cuerpo': r(-10, 0, 0), 'capucha': r(-16, 0, 0)},
                 baston(arriba=0.6, fuera=0.85, delante=0.1, codo=-22, ang=180),
                 libro(arriba=0.6, fuera=0.85, delante=0.1, codo=-26))
    baja = sumar({'raiz': p(0, -3, 0)}, {'cuerpo': r(16, 0, 0), 'capucha': r(10, 0, 0)},
                 baston(arriba=-0.65, fuera=0.15, delante=0.7, codo=-24),
                 libro(arriba=-0.55, fuera=0.4, delante=0.7, codo=-30))
    hunde = sumar({'raiz': p(0, 1, 0)}, {'cuerpo': r(22, 0, 0), 'capucha': r(15, 0, 0)},
                  baston(arriba=-0.8, fuera=0.2, delante=0.5, codo=-30),
                  libro(arriba=-0.75, fuera=0.4, delante=0.5, codo=-36))
    f_area = linea(
        (0.0, {}, 'suave'),
        (0.3, encoge, 'suave'),
        (0.85, abre, 'sale'),
        (A_SUELTA - 0.05, sumar(abre, {'raiz': p(0, -1.5, 0), 'cuerpo': r(-3)}), 'suave'),
        (A_SUELTA, baja, 'golpe'),
        (1.3, hunde, 'sale'),
        (1.7, sumar(baja, {'cuerpo': r(-3)}), 'suave'),
        (DUR_A, {}, 'suave'),
    )

    def area(s):
        # Las losas se apartan mientras carga y dan vuelta y media deprisa; vuelven al acabar.
        k = ventana(s, 0.6, A_SUELTA + 0.4, 0.5, 0.7)
        ang = 720.0 * _suave(min(1.0, s / DUR_A))
        tiembla = temblor(s, 0.85, A_SUELTA, 1.6, 18)
        return sumar(f_area(s), {'cuerpo': r(tiembla, 0, tiembla * 0.6)}, losas(ang, 1.0 + 0.9 * k, 6.0 * k, ang * 2))
    a['AREA'] = Anim('AREA', DUR_A, area, False, muelles)

    # --- Especial: Ciclon Devastador. Alza el baston y DIRIGE el ciclon: el orbe traza circulos por encima de su
    #     cabeza, cada vez mas deprisa, con el cuerpo meciendose contra el baston y el libro abierto a un lado; sube
    #     poco a poco, se echa atras y lo empuja hacia fuera: estalla ---
    E_FORMA, E_ESTALLA, DUR_E = 1.0, 4.7, 6.0
    alza = sumar({'raiz': p(0, -14, 0)}, {'cuerpo': r(-8, 0, 0), 'capucha': r(-18, 0, 0)},
                 baston(arriba=0.95, fuera=0.2, delante=0.1, codo=-20, ang=180),
                 libro(arriba=0.45, fuera=0.85, delante=0.2, codo=-28))
    atras = sumar({'raiz': p(0, -20, 2)}, {'cuerpo': r(-16, 8, 0), 'capucha': r(-20, -4, 0)},
                  baston(arriba=0.75, fuera=0.25, delante=-0.45, codo=-50, ang=180),
                  libro(arriba=0.2, fuera=0.9, delante=0.1, codo=-36))
    empuja = sumar({'raiz': p(0, -12, -3)}, {'cuerpo': r(16, -6, 0), 'capucha': r(6, 4, 0)},
                   baston(arriba=0.1, fuera=0.1, delante=1.0, codo=-18, ang=180),
                   libro(arriba=0.1, fuera=0.9, delante=0.4, codo=-26))
    sigue_e = sumar({'raiz': p(0, -10, -4)}, {'cuerpo': r(22, -8, 0), 'capucha': r(12, 6, 0)},
                    baston(arriba=-0.1, fuera=0.05, delante=1.0, codo=-24, ang=180),
                    libro(arriba=0.0, fuera=0.9, delante=0.45, codo=-30))
    DIRIGE0, DIRIGE1 = E_FORMA + 0.4, E_ESTALLA - 0.55

    def dirige(s):
        """El brazo del baston trazando circulos por encima de la cabeza (tres vueltas que se aceleran)."""
        u = min(1.0, max(0.0, (s - DIRIGE0) / (DIRIGE1 - DIRIGE0)))
        th = 2 * math.pi * 3.0 * u ** 1.4
        k = ventana(s, DIRIGE0, DIRIGE1, 0.4, 0.3)
        fuera, delante = 0.2 + 0.45 * math.sin(th) * k, 0.1 + 0.45 * math.cos(th) * k
        cuerpo = r(-8 + 4 * math.cos(th) * k, -10 * math.sin(th) * k, 5 * math.sin(th) * k)
        return sumar(baston(arriba=0.95 - 0.15 * k, fuera=fuera, delante=delante, codo=-20 - 10 * k, ang=180),
                     {'cuerpo': cuerpo, 'capucha': r(-18 - 3 * math.cos(th + 0.6) * k, 6 * math.sin(th + 0.6) * k, 0)})

    f_esp = linea(
        (0.0, {}, 'suave'),
        (E_FORMA, alza, 'sale'),
        (DIRIGE1, sumar(alza, {'raiz': p(0, -6, 0)}), 'suave'),
        (E_ESTALLA - 0.2, atras, 'sale'),
        (E_ESTALLA, empuja, 'golpe'),
        (E_ESTALLA + 0.35, sigue_e, 'sale'),
        (E_ESTALLA + 0.8, empuja, 'suave'),
        (DUR_E, {}, 'suave'),
    )

    def especial(s):
        q = f_esp(s)
        k = ventana(s, DIRIGE0, DIRIGE1, 0.4, 0.3)
        if k > 0:
            # Mientras dirige, el circulo manda sobre el brazo del baston, el cuerpo y la capucha.
            d = dirige(s)
            q = {**q, **mezclar({n: q.get(n, {}) for n in d}, d, k)}
        kc = ventana(s, E_FORMA, E_ESTALLA, 0.6, 0.6)
        ang = 1080.0 * _suave(min(1.0, s / (E_ESTALLA + 0.2)))
        return sumar(q, losas(ang, 1.0 + 0.7 * kc, 14.0 * kc, ang * 2, 3.0, s), flota(s, 1.2, 0.5, 2.4))
    a['ESPECIAL'] = Anim('ESPECIAL', DUR_E, especial, False, muelles)

    # --- Muerte (Juan: "su animacion de muerte es rara"): la magia le falla. Se convulsiona en el aire con los brazos
    #     abiertos, la luz se le escapa, y se desploma: cae al suelo y la tunica se arruga y se extiende como si se
    #     quedara vacia, la capucha cae sobre ella, el baston se le escapa y las losas caen alrededor ---
    DUR_M, M_CAE = 3.0, 1.9
    tiembla = sumar({'raiz': p(0, -6, 0)}, {'cuerpo': r(-14, 0, 0), 'capucha': r(-24, 0, 0)},
                    {'falda': r(-6), 'falda2': r(-8)},
                    baston(arriba=0.4, fuera=0.9, delante=0.1, codo=-22, ang=180),
                    libro(arriba=0.3, fuera=0.9, delante=0.2, codo=-30))
    vacia = sumar({'cuerpo': rp((34, 0, 4), (0, 0, 0)), 'capucha': r(46, 0, 8)},
                  {'falda': {'rot': (-38, 0, 0), 'esc': (1.3, 0.5, 1.3)}, 'falda2': {'rot': (-30, 0, 0), 'esc': (1.25, 0.55, 1.25)},
                   'capa': r(-30), 'capa2': r(-20)},
                  baston(arriba=-0.55, fuera=0.85, delante=0.2, codo=-10, ang=100),
                  libro(arriba=-0.9, fuera=0.35, delante=0.4, codo=-12), suelo_losas())
    vacia = sumar(vacia, {'raiz': p(0, al_suelo(hs, vacia), 0)})
    f_m = linea(
        (0.0, {}, 'suave'),
        (0.5, tiembla, 'sale'),
        (1.45, sumar(tiembla, {'raiz': p(0, -3, 0), 'cuerpo': r(-6), 'capucha': r(-6)}), 'suave'),
        (M_CAE, vacia, 'cae'),
        (M_CAE + 0.2, sumar(vacia, {'cuerpo': r(-4), 'raiz': p(0, -1.0, 0)}), 'sale'),
        (M_CAE + 0.5, vacia, 'entra'),
        (DUR_M, vacia, 'suave'),
    )

    def muerte(s):
        return sumar(f_m(s), {'cuerpo': r(temblor(s, 0.2, 1.5, 2.0, 15)), 'capucha': r(temblor(s, 0.4, 1.6, 3.0, 11))})
    a['MUERTE'] = Anim('MUERTE', DUR_M, muerte, False, muelles)

    tiempos = {
        'DESPERTAR_ABRE': tick(ABRE), 'DESPERTAR_SE_ALZA': tick(SE_ALZA), 'DESPERTAR_ALZADO': tick(ALZADO),
        'DESPERTAR_RUGE': tick(RUGE), 'DURACION_DESPERTAR': tick(DUR_D),
        'DURACION_NORMAL': tick(DUR_N), 'NORMAL_CARGA': tick(N_CARGA), 'NORMAL_SUELTA': tick(N_SUELTA),
        'DURACION_AREA': tick(DUR_A), 'AREA_SUELTA': tick(A_SUELTA),
        'DURACION_ESPECIAL': tick(DUR_E), 'ESPECIAL_FORMA': tick(E_FORMA), 'ESPECIAL_ESTALLA': tick(E_ESTALLA),
        'DURACION_MUERTE': tick(DUR_M) + 50, 'MUERTE_CAE': tick(M_CAE), 'DISOLVER_DESDE': tick(DUR_M) - 10,
        'PERIODO_ANDAR': tick(T_AND), 'ZANCADA': 0.12,
    }
    puntos = {
        'CABEZA': bloques('yiatzo', hs, {}, *CABEZA['yiatzo']),
        'PECHO': bloques('yiatzo', hs, {}, *PECHO['yiatzo']),
        'ORBE_SUELTA': bloques('yiatzo', hs, a['NORMAL'].en(hs, N_SUELTA), 'baston', (0, -46, 0)),
        'ORBE_AREA': bloques('yiatzo', hs, a['AREA'].en(hs, A_SUELTA), 'baston', (0, -46, 0)),
        'ORBE_ALZADO': bloques('yiatzo', hs, a['ESPECIAL'].en(hs, 2.5), 'baston', (0, -46, 0)),
    }
    anclas = {'ORBE': ('baston', (0, -46, 0)), 'OJOS': ('capucha', (0, -6, -2)), 'LIBRO': ('libro', (0, -3, 0))}
    for i, n in enumerate(piedras):
        anclas[f'LOSA_{i}'] = (n, (0, 0, 0))
    return a, tiempos, puntos, anclas


@registrar('atlahua')
def atlahua(hs):
    """El rey del mar: pesado y lento, el tridente a plomo como un baston (Juan, con Nerea: "el tridente a plomo"),
    la capa de algas que le sigue con retraso. Estocada con paso al frente, golpe al suelo con el tridente y el
    tsunami con los dos brazos."""
    PI = Pierna(hs, 1)
    PD = Pierna(hs, -1)
    a = {}
    muelles = [Muelle('capa', 0.3, 34, 4.5, 60), Muelle('capa2', 0.25, 30, 4.0, 60)]

    def piernas(baja=0.0, avanza=0.0, izq=(0.0, 0.0), der=(0.0, 0.0), punta_i=0.0, punta_d=0.0, abre=0.0):
        bi = PI.reposo() + np.array([izq[0] - baja, izq[1] + avanza])
        bd = PD.reposo() + np.array([der[0] - baja, der[1] + avanza])
        return sumar(PI.pose(bi, punta_i, abre), PD.pose(bd, punta_d, abre), {'pelvis': p(0, baja, -avanza)})

    def tridente(arriba=-1.0, fuera=0.0, delante=0.0, codo=0.0, ang=None, muneca=None):
        """El brazo del tridente. ang: el giro total del tridente en la mano (180: las puntas siguen al brazo); sin
        ang, a plomo con las puntas arriba."""
        if ang is None:
            d = np.array([-fuera, -arriba, -delante], float)
            d /= np.linalg.norm(d)
            ang = -(math.degrees(math.asin(max(-1.0, min(1.0, d[2])))) + codo)
        return brazo(hs, -1, arriba, fuera, delante, codo, muneca, ang, 'tridente')

    def izquierdo(arriba=-1.0, fuera=0.0, delante=0.0, codo=0.0):
        return brazo(hs, 1, arriba, fuera, delante, codo)

    # --- Reposo: respira hondo, mira despacio, el tridente quieto ---
    T_REP = 4.5

    def reposo(s):
        w = 2 * math.pi * s / T_REP
        return sumar(
            piernas(baja=0.6 + 0.6 * math.sin(w)),
            {'torso': r(1.4 * math.sin(w + 0.6), 2.5 * math.sin(w / 2), 0)},
            {'cabeza': r(-1 + 2 * math.sin(w + 1.0), 12 * math.sin(w / 2 + 0.5), 0), 'mandibula': r(2 + 2 * math.sin(w))},
            {'hombro_izq': r(2 * math.sin(w + 0.8), 0, 1.5 * math.sin(w)), 'hombro_der': r(1.0 * math.sin(w + 1.0))},
        )
    a['REPOSO'] = Anim('REPOSO', T_REP, reposo, True, muelles)

    # --- Andar: paso lento y pesado; el tridente a plomo, que sube y baja con cada paso ---
    T_AND = 1.45
    ZANC = 8.0
    APOYO = 0.62

    def ciclo_pie(f):
        f %= 1.0
        if f < APOYO:
            u = f / APOYO
            return 0.0, -ZANC + 2 * ZANC * u
        u = (f - APOYO) / (1 - APOYO)
        return -4.5 * math.sin(math.pi * u) ** 1.2, ZANC - 2 * ZANC * _suave(u)

    def andar(s):
        f = s / T_AND
        w = 2 * math.pi * f
        iy, iz = ciclo_pie(f)
        dy, dz = ciclo_pie(f + 0.5)
        baja = 1.6 + 1.1 * math.cos(2 * w)
        return sumar(
            piernas(baja=baja, izq=(iy, iz), der=(dy, dz),
                    punta_i=-8 * max(0.0, math.sin(w + 0.4)), punta_d=-8 * max(0.0, math.sin(w + math.pi + 0.4))),
            {'pelvis': r(1.5, 5 * math.sin(w), 2.5 * math.sin(w))},
            {'torso': r(3.0, -6 * math.sin(w), -2.0 * math.sin(w))},
            {'cabeza': r(-2.0, 2 * math.sin(w), 0)},
            {'hombro_izq': r(10 * math.sin(w), 0, 0), 'antebrazo_izq': r(-5 + 5 * math.sin(w))},
            {'hombro_der': r(-4 * math.sin(w))},
        )
    a['ANDAR'] = Anim('ANDAR', T_AND, andar, True, muelles)

    # --- Dormido: de rodillas como una estatua, las dos manos en el tridente clavado delante, la cabeza gacha ---
    DORMIDO = sumar(
        piernas(baja=13.0, izq=(-1, 9), der=(-1, 9), punta_i=40, punta_d=40),
        {'torso': r(14, 0, 0), 'cuello': r(8), 'cabeza': r(22, 0, 0), 'mandibula': r(0)},
        tridente(arriba=-0.25, fuera=-0.15, delante=0.95, codo=-40),
        izquierdo(arriba=-0.2, fuera=-0.35, delante=0.9, codo=-50),
    )

    def dormido(s):
        w = 2 * math.pi * s / 5.5
        return sumar(DORMIDO, {'torso': r(1.0 * math.sin(w)), 'pelvis': p(0, 0.3 * math.sin(w), 0)})
    a['DORMIDO'] = Anim('DORMIDO', 5.5, dormido, True, muelles)

    # --- Despertar (7 s): los ojos se encienden, alza la cabeza, se levanta con el tridente, lo alza al cielo, ruge y
    #     lo clava en el suelo (el anillo de agua) ---
    ABRE, SE_ALZA, ALZADO, RUGE, DUR_D = 1.0, 2.2, 3.5, 4.8, 7.0
    medio = sumar(piernas(baja=6.0, izq=(0, -8), der=(-1, 6), punta_d=20), {'torso': r(10, 0, 0), 'cabeza': r(-4)},
                  tridente(arriba=-0.4, fuera=0.1, delante=0.9, codo=-30), izquierdo(arriba=-0.6, fuera=0.3, delante=0.7, codo=-30))
    alzado = sumar(piernas(baja=2.0, izq=(0, -4), der=(0, 4)), {'torso': r(-8, 0, 0), 'cabeza': r(-16)},
                   tridente(arriba=1.0, fuera=0.25, delante=0.05, codo=-5, ang=180),
                   izquierdo(arriba=0.1, fuera=0.95, delante=0.2, codo=-20))
    ruge = sumar(piernas(baja=5.0, izq=(0, -6), der=(0, 6)), {'torso': r(-14, 0, 0), 'cuello': r(-8), 'cabeza': r(-22),
                                                               'mandibula': r(30)},
                 tridente(arriba=1.0, fuera=0.25, delante=0.05, codo=-5, ang=180),
                 izquierdo(arriba=0.3, fuera=0.9, delante=0.2, codo=-30))
    clava = sumar(piernas(baja=6.0, izq=(0, -6), der=(0, 6)), {'torso': r(10, 0, 0), 'cabeza': r(-6), 'mandibula': r(12)},
                  tridente(arriba=-0.45, fuera=0.3, delante=0.85, codo=-15),
                  izquierdo(arriba=-0.3, fuera=0.9, delante=0.2, codo=-30))
    f_desp = linea(
        (0.0, DORMIDO, 'suave'),
        (ABRE, sumar(DORMIDO, {'cabeza': r(-8)}), 'suave'),
        (SE_ALZA, sumar(DORMIDO, {'cabeza': r(-24), 'torso': r(-6)}), 'suave'),
        (SE_ALZA + 0.8, medio, 'sale'),
        (ALZADO, alzado, 'suave'),
        (RUGE - 0.15, sumar(ruge, {'mandibula': r(-26), 'cabeza': r(10)}), 'suave'),
        (RUGE + 0.2, ruge, 'golpe'),
        (RUGE + 1.0, ruge, 'suave'),
        (RUGE + 1.25, clava, 'cae'),
        (DUR_D - 0.5, sumar(clava, {'torso': r(-6), 'mandibula': r(-12)}), 'suave'),
        (DUR_D, {}, 'suave'),
    )

    def despertar(s):
        return sumar(f_desp(s), {'cabeza': r(temblor(s, RUGE, RUGE + 1.0, 2.5, 15))})
    a['DESPERTAR'] = Anim('DESPERTAR', DUR_D, despertar, False, muelles)

    # --- Normal: Estocada del Tridente. Recoge el tridente a la cadera y lo clava hacia delante con un paso largo ---
    N_CARGA, N_GOLPE, DUR_N = 0.45, 0.58, 1.5
    carga = sumar(piernas(baja=4.0, izq=(0, -6), der=(0, 7)), {'torso': r(2, 30, 0), 'pelvis': r(0, 12, 0), 'cabeza': r(0, -24)},
                  tridente(arriba=-0.1, fuera=0.5, delante=-0.6, codo=-60, ang=170),
                  izquierdo(arriba=0.0, fuera=0.25, delante=0.95, codo=-10))
    estocada = sumar(piernas(baja=8.0, avanza=10.0, izq=(0, -14), der=(0, 9)),
                     {'torso': r(14, -22, 0), 'pelvis': r(0, -8, 0), 'cabeza': r(-8, 18)},
                     tridente(arriba=0.05, fuera=-0.1, delante=1.0, codo=-4, ang=182),
                     izquierdo(arriba=-0.3, fuera=0.9, delante=-0.2, codo=-20))
    f_norm = linea(
        (0.0, {}, 'suave'),
        (N_CARGA, carga, 'sale'),
        (N_GOLPE, estocada, 'seco'),
        (0.85, sumar(estocada, {'torso': r(-3)}), 'sale'),
        (DUR_N, {}, 'suave'),
    )
    a['NORMAL'] = Anim('NORMAL', DUR_N, f_norm, False, muelles)

    # --- Area: Olas del Abismo. Hace girar el tridente sobre la cabeza y lo clava en el suelo con las dos manos ---
    A_GIRA, A_GOLPE, DUR_A = 0.2, 1.0, 2.4
    gira = sumar(piernas(baja=3.0, izq=(0, -5), der=(0, 5)), {'torso': r(-8, 0, 0), 'cabeza': r(-12)},
                 tridente(arriba=1.0, fuera=0.15, delante=0.1, codo=-30, ang=95),
                 izquierdo(arriba=0.3, fuera=0.9, delante=0.2, codo=-20))
    golpe = sumar(piernas(baja=12.0, izq=(0, -7), der=(0, 6)), {'torso': r(34, 0, 0), 'cabeza': r(-18), 'mandibula': r(14)},
                  tridente(arriba=-0.75, fuera=0.05, delante=0.65, codo=-4, ang=180),
                  izquierdo(arriba=-0.6, fuera=-0.45, delante=0.7, codo=-10))
    f_area = linea(
        (0.0, {}, 'suave'),
        (A_GIRA + 0.25, gira, 'sale'),
        (A_GOLPE - 0.12, sumar(gira, {'torso': r(-6)}), 'suave'),
        (A_GOLPE, golpe, 'cae'),
        (A_GOLPE + 0.5, sumar(golpe, {'torso': r(-4)}), 'sale'),
        (DUR_A, {}, 'suave'),
    )

    def area(s):
        q = f_area(s)
        # El tridente da vuelta y media en la mano sobre la cabeza antes del golpe.
        g = _suave(min(1.0, max(0.0, (s - A_GIRA - 0.1) / (A_GOLPE - 0.25 - A_GIRA))))
        k = ventana(s, A_GIRA + 0.2, A_GOLPE - 0.15, 0.2, 0.1)
        return sumar(q, {'mano_der': r(0, 0, 720 * g * k)}, {'torso': r(temblor(s, A_GOLPE, A_GOLPE + 0.45, 2.0, 13))})
    a['AREA'] = Anim('AREA', DUR_A, area, False, muelles)

    # --- Especial: Tsunami del Abismo. Alza el tridente con las dos manos y ruge (la ola crece a su espalda), y lo
    #     baja apuntando al frente: la ola sale ---
    E_RUGE, E_LANZA, DUR_E = 1.4, 2.7, 5.5
    alza = sumar(piernas(baja=3.0, izq=(0, -6), der=(0, 6), abre=4), {'torso': r(-14, 0, 0), 'cuello': r(-6), 'cabeza': r(-20),
                                                                       'mandibula': r(8)},
                 tridente(arriba=1.0, fuera=0.05, delante=-0.05, codo=-10, ang=180),
                 izquierdo(arriba=1.0, fuera=-0.15, delante=-0.05, codo=-12))
    ruge = sumar(alza, {'mandibula': r(24), 'cabeza': r(-6)})
    lanza = sumar(piernas(baja=8.0, avanza=8.0, izq=(0, -12), der=(0, 8)),
                  {'torso': r(22, 0, 0), 'cabeza': r(-10), 'mandibula': r(16)},
                  tridente(arriba=-0.1, fuera=-0.05, delante=1.0, codo=-4, ang=182),
                  izquierdo(arriba=-0.1, fuera=-0.3, delante=0.95, codo=-6))
    f_esp = linea(
        (0.0, {}, 'suave'),
        (E_RUGE - 0.3, alza, 'sale'),
        (E_RUGE, ruge, 'golpe'),
        (E_LANZA - 0.3, sumar(alza, {'torso': r(-6)}), 'suave'),
        (E_LANZA, lanza, 'seco'),
        (E_LANZA + 1.6, sumar(lanza, {'torso': r(-4)}), 'suave'),
        (DUR_E, {}, 'suave'),
    )

    def especial(s):
        return sumar(f_esp(s), {'cabeza': r(temblor(s, E_RUGE, E_RUGE + 0.9, 2.0, 15))})
    a['ESPECIAL'] = Anim('ESPECIAL', DUR_E, especial, False, muelles)

    # --- Muerte (Juan: "se va para un lado y se queda como tronco"): ruge al cielo, hinca una rodilla apoyado en el
    #     tridente, intenta levantarse, el tridente se le escurre y se desploma de frente: cae de rodillas, el cuerpo
    #     se dobla por la cintura hasta el suelo, un brazo por delante, el tridente tirado a un lado y la cabeza de
    #     lado; el ultimo aliento le hunde un poco mas ---
    DUR_M, M_RODILLA, M_CAE = 3.4, 1.4, 2.5
    ruge = sumar({'torso': r(-12, 0, 0), 'cabeza': r(-20), 'mandibula': r(26)}, piernas(baja=2.0, izq=(0, 3), der=(0, -4)),
                 tridente(arriba=-0.6, fuera=0.5, delante=0.4, codo=-25), izquierdo(arriba=-0.3, fuera=0.8, delante=0.3, codo=-30))
    rodilla = sumar(piernas(baja=11.0, izq=(0.0, -12.0), der=(0.6, 10.9), punta_d=50),
                    {'torso': r(16, 0, 6), 'cabeza': r(18, 0, 0), 'mandibula': r(18)},
                    tridente(arriba=-0.3, fuera=0.35, delante=0.85, codo=-30),
                    izquierdo(arriba=-0.6, fuera=0.4, delante=0.6, codo=-40))
    intenta = sumar(piernas(baja=8.0, izq=(0.0, -10.0), der=(0.6, 9.0), punta_d=40),
                    {'torso': r(6, 0, 2), 'cabeza': r(4, 0, 0), 'mandibula': r(10)},
                    tridente(arriba=-0.25, fuera=0.4, delante=0.85, codo=-20),
                    izquierdo(arriba=-0.7, fuera=0.5, delante=0.4, codo=-30))
    postrado = sumar(piernas(baja=14.0, izq=(-1.0, 10.0), der=(-1.0, 10.0), punta_i=45, punta_d=45),
                     {'pelvis': r(30, 0, 0), 'torso': r(50, 0, 8), 'cabeza': r(4, 40, 12), 'mandibula': r(14)},
                     # Con el cuerpo doblado hacia el suelo, 'arriba' del torso es hacia delante: el brazo del tridente
                     # queda estirado por el suelo con el tridente delante, y el otro apoyado a su lado.
                     tridente(arriba=0.85, fuera=0.35, delante=0.25, codo=-10, ang=180),
                     izquierdo(arriba=0.45, fuera=0.7, delante=0.3, codo=-35))
    postrado = sumar(postrado, {'raiz': p(0, al_suelo(hs, postrado), 0)})
    f_m = linea(
        (0.0, {}, 'suave'),
        (0.5, ruge, 'sale'),
        (M_RODILLA, rodilla, 'cae'),
        (1.75, sumar(rodilla, {'torso': r(4, 0, 4)}), 'suave'),
        (2.1, intenta, 'suave'),
        (M_CAE, postrado, 'cae'),
        (M_CAE + 0.2, sumar(postrado, {'torso': r(-5), 'raiz': p(0, -1.0, 0)}), 'sale'),
        (M_CAE + 0.5, postrado, 'entra'),
        (DUR_M, sumar(postrado, {'torso': r(2), 'cabeza': r(3)}), 'suave'),
    )

    def muerte(s):
        return sumar(f_m(s), {'torso': r(temblor(s, 1.75, 2.15, 2.5, 13)), 'cabeza': r(temblor(s, 0.5, 1.3, 3.0, 9))})
    a['MUERTE'] = Anim('MUERTE', DUR_M, muerte, False, muelles)

    tiempos = {
        'DESPERTAR_ABRE': tick(ABRE), 'DESPERTAR_SE_ALZA': tick(SE_ALZA), 'DESPERTAR_ALZADO': tick(ALZADO),
        'DESPERTAR_RUGE': tick(RUGE), 'DURACION_DESPERTAR': tick(DUR_D), 'DESPERTAR_CLAVA': tick(RUGE + 1.25),
        'DURACION_NORMAL': tick(DUR_N), 'NORMAL_CARGA': tick(N_CARGA), 'NORMAL_GOLPE': tick(N_GOLPE),
        'DURACION_AREA': tick(DUR_A), 'AREA_GOLPE': tick(A_GOLPE),
        'DURACION_ESPECIAL': tick(DUR_E), 'ESPECIAL_RUGE': tick(E_RUGE), 'ESPECIAL_LANZA': tick(E_LANZA),
        'DURACION_MUERTE': tick(DUR_M) + 50, 'MUERTE_RODILLA': tick(M_RODILLA), 'MUERTE_CAE': tick(M_CAE),
        'DISOLVER_DESDE': tick(DUR_M) - 6,
        'PERIODO_ANDAR': tick(T_AND),
    }
    puntos = {
        'CABEZA': bloques('atlahua', hs, {}, *CABEZA['atlahua']),
        'PECHO': bloques('atlahua', hs, {}, *PECHO['atlahua']),
        'PUNTA_ESTOCADA': bloques('atlahua', hs, a['NORMAL'].en(hs, N_GOLPE), 'tridente', (0, -44, 0)),
        'PUNTA_GOLPE': bloques('atlahua', hs, a['AREA'].en(hs, A_GOLPE), 'tridente', (0, -44, 0)),
        'PUNTA_LANZA': bloques('atlahua', hs, a['ESPECIAL'].en(hs, E_LANZA), 'tridente', (0, -44, 0)),
        'PUNTA_CLAVA': bloques('atlahua', hs, a['DESPERTAR'].en(hs, RUGE + 1.25), 'tridente', (0, 20, 0)),
    }
    anclas = {'PUNTAS': ('tridente', (0, -44, 0)), 'OJOS': ('cabeza', (0, -6, -5)), 'SENUELO': ('torso', (0, -12, -8)),
              'BOCA': ('mandibula', (0, 1, -5))}
    return a, tiempos, puntos, anclas


@registrar('xiuhquetzal')
def xiuhquetzal(hs):
    """El fenix bate las alas como un ave grande. Version del 11-10-2026 (Juan: "las animaciones ... de la ave estan
    raras no parecen reales"): antes las dos partes del ala se movian a la vez, como una bisagra, y las batidas del
    ataque iban a saltos. Ahora:
      - la onda recorre el ala: la mano llega tarde al brazo, se abre en la bajada (el ala entera, barriendo hacia
        delante y con el borde de ataque hacia abajo) y se pliega hacia atras en la subida;
      - el cuerpo sube con cada bajada y cae un poco en la subida, cabecea con ella y la cola se abre y baja para
        frenar; la cabeza se queda quieta (el cuello compensa, como un ave de presa);
      - suspendido no es una maquina: deriva, se ladea y gira un poco el cuerpo (la cabeza sigue mirando al frente);
      - las batidas de la Tormenta de Plumas son batidas enteras (con la mano que llega tarde), no golpes de pose.
    La cola y la cresta de fuego ondean (fisica). El juego lo sube de verdad al volar: aqui solo va lo del cuerpo."""
    a = {}
    muelles = [Muelle('cola', 0.88, 42, 5.0, 25), Muelle('cola2', 0.82, 36, 4.0, 32), Muelle('cola3', 0.76, 30, 3.5, 38),
               Muelle('cresta', 1.0, 55, 5.0, 22), Muelle('barba', 0.6, 60, 6.0, 30)]

    def alas(alza=0.0, mano=0.0, barre=0.0, tuerce=0.0, mano_barre=0.0):
        """Las dos alas a la vez (en espejo): alza (grados que sube el ala, negativo baja), mano (lo que se pliega la
        mano del ala, hacia abajo), barre (adelante), tuerce (el borde de ataque) y mano_barre."""
        return {'ala_izq': r(tuerce, barre, -alza), 'ala_der': r(tuerce, -barre, alza),
                'mano_ala_izq': r(0, mano_barre, mano), 'mano_ala_der': r(0, -mano_barre, -mano)}

    B = 0.45      # la parte de la batida que es bajada
    RETRASO = 0.08  # lo que la mano llega tarde al brazo (fraccion de batida)

    def batida(f, amp=1.0):
        """Una batida en la fase f (0-1): bajada fuerte (0 a B) y subida con la mano plegada hacia atras, la mano con
        su retraso. Devuelve la pose (alas y cola) y lo que sube el cuerpo (pixeles, negativo arriba)."""
        f %= 1.0
        if f < B:
            u = f / B
            alza = 50 - 100 * _suave(u)
            barre, tuerce = 8 * math.sin(math.pi * u), -10 * math.sin(math.pi * u)
            sube, cola, cabeceo = -3.4 * math.sin(math.pi * u), 6 * math.sin(math.pi * u), -2.5 * math.sin(math.pi * u)
        else:
            u = (f - B) / (1 - B)
            alza = -50 + 100 * _suave(u)
            barre, tuerce = -12 * math.sin(math.pi * u), 14 * math.sin(math.pi * u)
            sube, cola, cabeceo = 2.2 * math.sin(math.pi * u), -3 * math.sin(math.pi * u), 2.0 * math.sin(math.pi * u)
        g = (f - RETRASO) % 1.0
        if g < B:
            u = g / B
            mano, mano_barre = -10 * math.sin(math.pi * u) + 6 * u, 4 * math.sin(math.pi * u)
        else:
            u = (g - B) / (1 - B)
            mano, mano_barre = 6 + 38 * math.sin(math.pi * u) - 6 * u, -28 * math.sin(math.pi * u)
        q = sumar(alas(alza, mano, barre, tuerce, mano_barre), {'cola': r(cola), 'cuerpo': r(cabeceo)})
        return escalar(q, amp), sube * amp

    def cuello_quieto(cuerpo_x, cuerpo_y=0.0):
        """El cuello compensa el cabeceo y el giro del cuerpo: la cabeza no se mueve (como la de un ave de presa)."""
        return {'cuello': r(-cuerpo_x * 0.55, -cuerpo_y * 0.4), 'cuello2': r(-cuerpo_x * 0.25, -cuerpo_y * 0.3),
                'cabeza': r(-cuerpo_x * 0.2, -cuerpo_y * 0.2)}

    # El boceto lleva el cuerpo inclinado mj.XIUHQUETZAL_INCLINA grados (vuela tendido, con el cuello alzado, la cola
    # y las patas hacia atras) y los hombros lo deshacen: las alas baten como siempre. VIEJA devuelve el cuerpo erguido
    # de antes, pieza a pieza (para dormir posado y envolverse en sus alas): lo que cambio cada reposo.
    I = mj.XIUHQUETZAL_INCLINA
    # (Tambien deshace las alas tendidas y las patas recogidas del reposo de ahora: el capullo sigue igual.)
    PM, PT, PG = mj.XIUHQUETZAL_PATAS
    VIEJA = {'cuerpo': r(-I), 'hombros': r(I), 'cuello': r(24 + 28), 'cuello2': r(-30 + 20), 'cabeza': r(-6 - 12),
             'cola': r(62 - 57), 'pata_izq': r(-28 - 52 - PM), 'pata_der': r(-28 - 52 - PM),
             'tarso_izq': r(-PT), 'tarso_der': r(-PT), 'garras_izq': r(-PG), 'garras_der': r(-PG),
             'ala_izq': r(-mj.XIUHQUETZAL_ALA_TENDIDA), 'ala_der': r(-mj.XIUHQUETZAL_ALA_TENDIDA)}

    def postura(extra):
        """Mas (o menos) inclinado: el cuerpo, sin mover las alas (los hombros lo deshacen) ni la cabeza."""
        return sumar({'cuerpo': r(extra), 'hombros': r(-extra)}, cuello_quieto(extra))

    def patas(x=0.0, tarso=0.0, garras=0.0):
        return {'pata_izq': r(x), 'pata_der': r(x), 'tarso_izq': r(tarso), 'tarso_der': r(tarso),
                'garras_izq': r(garras), 'garras_der': r(garras)}

    def deriva(s, periodo, k=1.0):
        """Lo que se ladea, gira y se desplaza el cuerpo suspendido (una vuelta por periodo, sin repetirse en cada
        batida)."""
        w = 2 * math.pi * s / periodo
        ladeo, giro = 4 * k * math.sin(w), 5 * k * math.sin(w + 1.3)
        return sumar({'raiz': p(2.0 * k * math.sin(w + 0.4), 0, 1.2 * k * math.sin(2 * w))}, {'cuerpo': r(0, giro, ladeo)},
                     cuello_quieto(0, giro)), giro

    # --- Reposo: suspendido, cuatro batidas lentas y fuertes por vuelta, derivando ---
    T_BATIDA = 1.5
    T_REP = 4 * T_BATIDA

    def reposo(s):
        f = s / T_BATIDA
        q, sube = batida(f)
        cx = 3.0 * math.sin(2 * math.pi * f + 0.6)
        dq, _ = deriva(s, T_REP)
        return sumar(q, dq, postura(60 - (I - 12)), {'raiz': p(0, sube, 0), 'cuerpo': r(cx)}, cuello_quieto(cx),
                     patas(6 * math.sin(2 * math.pi * f + 1.2), -5 * math.sin(2 * math.pi * f + 1.6),
                           4 * math.sin(2 * math.pi * f + 2.0)))
    a['REPOSO'] = Anim('REPOSO', T_REP, reposo, True, muelles)

    # --- Andar (vuela hacia delante): el cuerpo tendido, batidas mas cortas y seguidas, las patas recogidas; se ladea
    #     un poco a cada lado cada dos batidas ---
    T_AND = 0.9

    def andar(s):
        f = s / T_AND
        q, sube = batida(f, 0.85)
        cx = 24 + 2.5 * math.sin(2 * math.pi * f + 0.6)
        return sumar(q, {'raiz': p(0, sube, 0), 'cuerpo': r(cx, 0, 2.5 * math.sin(math.pi * f))}, cuello_quieto(cx),
                     patas(10, -10, 18), alas(barre=-6))
    a['ANDAR'] = Anim('ANDAR', 2 * T_AND, andar, True, muelles)

    # --- Dormido: en el suelo, envuelto en sus alas como en un capullo de brasa, la cabeza escondida; respira ---
    capullo = sumar({'raiz': p(0, 9, 0)}, {'cuerpo': r(16, 0, 0)}, patas(-38, 54, 20),
                    {'ala_izq': r(62, 64, 58), 'ala_der': r(62, -64, -58),
                     'mano_ala_izq': r(0, 62, 26), 'mano_ala_der': r(0, -62, -26)},
                    {'cuello': r(38), 'cuello2': r(24), 'cabeza': r(34)}, {'cola': r(18)})

    def dormido(s):
        w = 2 * math.pi * s / 4.0
        return sumar(capullo, VIEJA, {'cuerpo': {'esc': (1 + 0.025 * math.sin(w), 1 + 0.025 * math.sin(w), 1 + 0.025 * math.sin(w))}},
                     {'ala_izq': r(0, 0, 1.5 * math.sin(w)), 'ala_der': r(0, 0, -1.5 * math.sin(w))},
                     {'cabeza': r(1.5 * math.sin(w + 0.8))})
    a['DORMIDO'] = Anim('DORMIDO', 4.0, dormido, True, muelles)

    # --- Despertar (6,5 s): el capullo late, las alas se abren de golpe (el estallido de fuego) con la mano que llega
    #     tarde, despega con batidas fuertes, se cierne y chilla con la cabeza alta ---
    ABRE, SE_ALZA, ALZADO, RUGE, DUR_D = 1.4, 2.0, 3.4, 4.3, 6.5
    abierto = sumar(alas(48, -10, 10, -6), {'cuerpo': r(-10, 0, 0)}, cuello_quieto(-10), patas(14, -6, 0))
    abriendo = sumar(alas(36, 30, -4, 6, -20), {'cuerpo': r(-6, 0, 0)}, cuello_quieto(-6), patas(4, 10, 8))
    chillido = sumar(alas(56, -14, 14, -10), {'cuerpo': r(-14, 0, 0)},
                     {'cuello': r(-4), 'cuello2': r(-10), 'cabeza': r(-30), 'pico_inf': r(34)}, patas(20, -10, 0))
    f_desp = linea(
        (0.0, capullo, 'suave'),
        (ABRE, sumar(capullo, {'cabeza': r(-12), 'cuello': r(-8)}), 'suave'),
        (SE_ALZA - 0.15, sumar(capullo, {'cabeza': r(-16), 'cuello': r(-10), 'cuerpo': r(4)}), 'entra'),
        (SE_ALZA + 0.12, abriendo, 'golpe'),
        (SE_ALZA + 0.3, abierto, 'sale'),
        (ALZADO, abierto, 'suave'),
        (RUGE - 0.25, sumar(abierto, {'cabeza': r(14), 'pico_inf': r(-4), 'cuello': r(6)}), 'suave'),
        (RUGE + 0.15, chillido, 'golpe'),
        (RUGE + 1.1, sumar(chillido, {'cabeza': r(6), 'pico_inf': r(-14)}), 'suave'),
        (DUR_D, {}, 'suave'),
    )

    def despertar(s):
        q = f_desp(s)
        # Despega batiendo fuerte (de SE_ALZA + 0,35 a ALZADO) y luego se cierne con batidas lentas hasta el final.
        k = ventana(s, SE_ALZA + 0.45, DUR_D, 0.3, 0.01)
        if k > 0:
            f = (s - SE_ALZA - 0.25) / (0.75 if s < ALZADO else 1.3)
            b, sube = batida(f, 0.8)
            q = sumar(q, escalar(b, k), {'raiz': p(0, sube * k, 0)})
        tiembla = temblor(s, ABRE, SE_ALZA, 2.0, 12)
        # En el capullo va erguido como antes (el cuerpo de VIEJA); al despegar se tiende poco a poco.
        erguido = 1.0 - _suave(min(1.0, max(0.0, (s - SE_ALZA) / (ALZADO - SE_ALZA))))
        return sumar(q, escalar(VIEJA, erguido), {'cuerpo': r(tiembla, 0, tiembla * 0.5)},
                     {'cabeza': r(temblor(s, RUGE, RUGE + 0.9, 3.0, 16))})
    a['DESPERTAR'] = Anim('DESPERTAR', DUR_D, despertar, False, muelles)

    # --- Normal: Picotazo de Llamas. Una batida fuerte para subir, se encabrita, pliega las alas (primero el brazo,
    #     luego la mano) y se lanza en picado con el pico por delante; tras el golpe abre las alas de golpe para
    #     frenar y remonta batiendo ---
    N_CARGA, N_GOLPE, DUR_N = 0.42, 0.72, 1.6
    impulso = sumar(alas(-42, -4, 8, -10), {'cuerpo': r(-14, 0, 0), 'raiz': p(0, -3, 0)}, cuello_quieto(-14), patas(20, -12, 6))
    encabrita = sumar(alas(52, -10, -6, -8), {'cuerpo': r(-26, 0, 0)}, postura(-40),
                      {'cuello': r(18), 'cuello2': r(6), 'cabeza': r(-14), 'pico_inf': r(10)}, patas(-30, -20, 10))
    # En el picado el cuello se estira hacia delante y abajo (el pico por delante de todo, por debajo del cuerpo):
    # asi el pico llega a la presa sin que el cuerpo tenga que meterse en el suelo.
    pliega = sumar(alas(10, 30, -30, 14, -24), {'cuerpo': r(36, 0, 0), 'raiz': p(0, 2, 0)},
                   {'cuello': r(4), 'cuello2': r(4), 'cabeza': r(-4), 'pico_inf': r(20)}, patas(50, -30, 14))
    picado = sumar(alas(-30, 22, -46, 22, -32), {'cuerpo': r(72, 0, 0), 'raiz': p(0, 4, 0)}, postura(-15),
                   {'cuello': r(22), 'cuello2': r(12), 'cabeza': r(-14), 'pico_inf': r(32)}, patas(20, -20, 20))
    frena = sumar(alas(30, -16, 18, -18, 6), {'cuerpo': r(-20, 0, 0), 'raiz': p(0, -1, 0)}, postura(-30),
                  {'cuello': r(10), 'cabeza': r(-8), 'pico_inf': r(14)}, patas(-50, 20, -10))
    f_norm = linea(
        (0.0, {}, 'suave'),
        (0.2, impulso, 'golpe'),
        (N_CARGA, encabrita, 'sale'),
        (0.56, pliega, 'entra'),
        (N_GOLPE, picado, 'entra'),
        (N_GOLPE + 0.16, frena, 'golpe'),
        (N_GOLPE + 0.42, sumar(frena, alas(-60, 6, 6, -6)), 'sale'),
        (DUR_N, {}, 'suave'),
    )

    def normal(s):
        q = f_norm(s)
        # Remonta batiendo al final (las batidas entran poco a poco).
        k = ventana(s, N_GOLPE + 0.55, DUR_N, 0.2, 0.25)
        if k > 0:
            b, sube = batida((s - N_GOLPE - 0.5) / 0.6, 0.7)
            q = sumar(escalar(q, 1 - 0.5 * k), escalar(b, k), {'raiz': p(0, sube * k, 0)})
        return q
    a['NORMAL'] = Anim('NORMAL', DUR_N, normal, False, muelles)

    # --- Area: Tormenta de Plumas Igneas. Sube con las alas en alto y da tres batidas enormes (cada bajada acaba en
    #     el instante en que salen las plumas): batidas enteras, con la mano que llega tarde y el cuerpo que sube ---
    A_BATIDAS, DUR_A = (0.8, 1.3, 1.8), 2.6
    T_GRANDE = A_BATIDAS[1] - A_BATIDAS[0]
    alto = sumar(alas(60, -14, 6, -6), {'cuerpo': r(-6, 0, 0)}, {'cuello': r(6), 'cabeza': r(18)}, patas(16, -8, 0))
    f_area = linea((0.0, {}, 'suave'), (0.55, alto, 'sale'), (A_BATIDAS[-1] + 0.35, alto, 'suave'), (DUR_A, {}, 'suave'))

    def area(s):
        q = f_area(s)
        # Las batidas: la fase 0 es el ala arriba; la bajada acaba (fase B) en cada A_BATIDAS.
        inicio = A_BATIDAS[0] - B * T_GRANDE
        k = ventana(s, inicio, A_BATIDAS[-1] + (1 - B) * T_GRANDE * 0.6, 0.12, 0.35)
        if k > 0:
            b, sube = batida((s - inicio) / T_GRANDE, 1.25)
            q = sumar(mezclar(q, {n: v for n, v in q.items() if not n.startswith(('ala', 'mano_ala'))}, k), escalar(b, k),
                      {'raiz': p(0, 1.3 * sube * k, 0)}, {'cabeza': r(14 * k), 'pico_inf': r(16 * k)})
        return q
    a['AREA'] = Anim('AREA', DUR_A, area, False, muelles)

    # --- Especial: Llamarada del Renacimiento. Se envuelve en sus alas en el aire (un sol), tiembla, y se abre de
    #     golpe chillando (la mano llega tarde: el ala restalla): la nova de fuego; luego se cierne batiendo mientras
    #     llueve fuego ---
    E_ENVUELVE, E_ESTALLA, E_FIN, DUR_E = 1.2, 2.8, 4.2, 5.5
    envuelto = sumar({'cuerpo': r(6, 0, 0)}, patas(50, -40, 20),
                     {'ala_izq': r(62, 64, 58), 'ala_der': r(62, -64, -58),
                      'mano_ala_izq': r(0, 62, 26), 'mano_ala_der': r(0, -62, -26)},
                     {'cuello': r(30), 'cuello2': r(20), 'cabeza': r(26)}, {'cola': r(-10)})
    restalla = sumar(alas(50, 34, 4, 4, -18), {'cuerpo': r(-12, 0, 0)},
                     {'cuello': r(-4), 'cuello2': r(-8), 'cabeza': r(-22), 'pico_inf': r(30)}, patas(20, -10, 0))
    estalla = sumar(alas(62, -18, 18, -14), {'cuerpo': r(-18, 0, 0)},
                    {'cuello': r(-6), 'cuello2': r(-12), 'cabeza': r(-30), 'pico_inf': r(36)}, patas(24, -14, 0))
    f_esp = linea(
        (0.0, {}, 'suave'),
        (E_ENVUELVE, envuelto, 'suave'),
        (E_ESTALLA - 0.12, sumar(envuelto, {'cuerpo': {'esc': (0.94, 0.94, 0.94)}}), 'entra'),
        (E_ESTALLA + 0.06, restalla, 'golpe'),
        (E_ESTALLA + 0.22, estalla, 'sale'),
        (E_FIN, sumar(estalla, {'pico_inf': r(-20)}), 'suave'),
        (DUR_E, {}, 'suave'),
    )

    def especial(s):
        # Envuelto en sus alas va erguido (como el capullo); al estallar vuelve a tenderse.
        q = sumar(f_esp(s), escalar(VIEJA, ventana(s, E_ENVUELVE, E_ESTALLA, 0.9, 0.25)))
        k = ventana(s, E_ESTALLA + 0.45, E_FIN, 0.35, 0.8)
        if k > 0:
            b, sube = batida((s - E_ESTALLA) / 1.4, 0.5)
            q = sumar(q, escalar(b, k), {'raiz': p(0, sube * k, 0)})
        t = temblor(s, E_ENVUELVE, E_ESTALLA, 2.5, 14)
        return sumar(q, {'cuerpo': r(t, 0, t), 'raiz': p(t * 0.4, 0, 0)})
    a['ESPECIAL'] = Anim('ESPECIAL', DUR_E, especial, False, muelles)

    # --- Muerte (Juan: "deberia ser cayendo y su cuerpo tirado, no de lado"): chilla, aletea sin fuerza, se le doblan
    #     las alas y cae dando una vuelta; queda tendido boca abajo con las alas abiertas sobre el suelo, la cola
    #     estirada detras y la cabeza de lado. El juego lo deja caer; la pose apoya lo mas bajo en el suelo ---
    DUR_M, M_SUELO = 3.6, 1.9
    chilla = sumar(alas(50, -16, 20, -14), {'cuerpo': r(-24, 0, 10)}, postura(-20),
                   {'cuello': r(-6), 'cuello2': r(-14), 'cabeza': r(-34), 'pico_inf': r(38)})
    # Mientras cae: de vientre (no de cabeza), las alas flojas y caidas (alzadas se veian de canto, como un palo), la
    # cola tras el cuerpo y las patas recogidas.
    cae = sumar(alas(8, 36, -4, 18, -20), {'cuerpo': r(34, 0, 30)}, {'cuello': r(20), 'cuello2': r(8), 'cabeza': r(-10),
                                                                      'pico_inf': r(24)}, patas(-30, 30, 10),
                {'cola': r(-40), 'cola2': r(-12), 'cola3': r(-8)})
    # Tendido: el cuerpo horizontal (90 grados), las alas planas en el suelo (sin la inclinacion de los hombros ni la
    # de las alas tendidas), la cola estirada detras, el cuello caido y la cabeza de lado, y las patas dobladas bajo el
    # vientre (antes iban estiradas a lo largo del cuerpo y las garras asomaban por encima de la espalda).
    PM_T, PT_T, PG_T = -60, 54, 30   # el muslo hacia el suelo, el tarso hacia atras pegado a el, las garras cerradas
    tendido = sumar({'cuerpo': r(90 - (I - 12), 0, 0)}, alas(-6, 4, 8, 76 - (90 - I) - mj.XIUHQUETZAL_ALA_TENDIDA),
                    {'cola': r(-57), 'cola2': r(-6), 'cuello': r(12), 'cuello2': r(10), 'cabeza': r(0, 48, 18),
                     'pico_inf': r(12)},
                    patas(PM_T - (52 + PM), PT_T - (34 + PT), PG_T - (-12 + PG)))
    tendido = sumar(tendido, {'raiz': p(0, al_suelo(hs, tendido), 0)})
    rebota = sumar(tendido, {'raiz': p(0, -2.0, 0), 'cuerpo': r(-4, 0, 0)})
    f_m = linea(
        (0.0, {}, 'suave'),
        (0.45, chilla, 'golpe'),
        (1.4, cae, 'suave'),
        (M_SUELO, tendido, 'cae'),
        (M_SUELO + 0.22, rebota, 'sale'),
        (M_SUELO + 0.5, tendido, 'entra'),
        (DUR_M, tendido, 'suave'),
    )

    def muerte(s):
        q = f_m(s)
        # Entre el chillido y la caida aletea sin fuerza (batidas cada vez mas flojas).
        k = ventana(s, 0.55, 1.35, 0.2, 0.3)
        if k > 0:
            b, _ = batida((s - 0.55) / 0.5, 0.45 * k * (1.0 - (s - 0.55) / 1.3))
            q = sumar(q, b)
        # Al quedar tendido, las alas tiemblan un poco y se quedan quietas.
        t = temblor(s, M_SUELO, M_SUELO + 0.9, 4.0, 9)
        return sumar(q, {'ala_izq': r(0, 0, t), 'ala_der': r(0, 0, -t)})
    a['MUERTE'] = Anim('MUERTE', DUR_M, muerte, False, muelles)

    tiempos = {
        'DESPERTAR_ABRE': tick(ABRE), 'DESPERTAR_SE_ALZA': tick(SE_ALZA), 'DESPERTAR_ALZADO': tick(ALZADO),
        'DESPERTAR_RUGE': tick(RUGE), 'DURACION_DESPERTAR': tick(DUR_D),
        'DURACION_NORMAL': tick(DUR_N), 'NORMAL_CARGA': tick(N_CARGA), 'NORMAL_GOLPE': tick(N_GOLPE),
        'DURACION_AREA': tick(DUR_A), 'AREA_BATIDA_1': tick(A_BATIDAS[0]), 'AREA_BATIDA_2': tick(A_BATIDAS[1]),
        'AREA_BATIDA_3': tick(A_BATIDAS[2]),
        'DURACION_ESPECIAL': tick(DUR_E), 'ESPECIAL_ENVUELVE': tick(E_ENVUELVE), 'ESPECIAL_ESTALLA': tick(E_ESTALLA),
        'ESPECIAL_FIN': tick(E_FIN),
        'DURACION_MUERTE': tick(DUR_M) + 50, 'MUERTE_SUELO': tick(M_SUELO), 'DISOLVER_DESDE': tick(DUR_M) - 14,
        'PERIODO_ANDAR': tick(T_AND), 'PERIODO_BATIDA': tick(T_BATIDA), 'ZANCADA': 0.2,
    }
    puntos = {
        'CABEZA': bloques('xiuhquetzal', hs, {}, *CABEZA['xiuhquetzal']),
        'PECHO': bloques('xiuhquetzal', hs, {}, *PECHO['xiuhquetzal']),
        'PICO_GOLPE': bloques('xiuhquetzal', hs, a['NORMAL'].en(hs, N_GOLPE), 'pico', (0, 3, -6)),
        'PICO': bloques('xiuhquetzal', hs, {}, 'pico', (0, 3, -6)),
        'ALA_IZQ': bloques('xiuhquetzal', hs, {}, 'mano_ala_izq', (40, 0, 20)),
        'ALA_DER': bloques('xiuhquetzal', hs, {}, 'mano_ala_der', (-40, 0, 20)),
        'GARRAS': bloques('xiuhquetzal', hs, {}, 'garras_izq', (0, 1, -2)),
    }
    anclas = {'PECHO_BRASA': ('cuerpo', (0, -8, -6)), 'OJOS': ('cabeza', (0, -3.5, -2.5)), 'PUNTA_PICO': ('pico', (0, 3, -6)),
              'PUNTA_ALA_IZQ': ('mano_ala_izq', (44, 0, 24)), 'PUNTA_ALA_DER': ('mano_ala_der', (-44, 0, 24)),
              'COLA_PUNTA': ('cola3', (0, 22, 0)), 'CRESTA': ('cresta', (0, -14, 6))}
    return a, tiempos, puntos, anclas


# ----------------------------------------------------------------------
if __name__ == '__main__':
    pedidos = {}
    if len(sys.argv) > 3:
        for trozo in sys.argv[3].split(';'):
            nom, _, cuales = trozo.partition(':')
            pedidos[nom] = cuales.split(',') if cuales else None
    else:
        pedidos = {n: None for n in MINIJEFES}
    CLI = os.path.join(RAIZ, 'src/client/java/com/atalaya/client')
    ENT = os.path.join(RAIZ, 'src/main/java/com/atalaya/entity')
    for nombre, cuales in pedidos.items():
        if HOJAS:
            hs, *malla = mjj.malla(nombre)
        else:
            hs = mjj.esqueleto(nombre)
        anims, tiempos, puntos, anclas = MINIJEFES[nombre](hs)
        for n in ORDEN:
            assert n in anims, (nombre, n)
        if 'ANDAR' in anims:
            tiempos['ZANCADA'] = zancada(nombre, hs, anims['ANDAR'], 'pie_izq') if nombre in ('moctezuma', 'atlahua') \
                else tiempos.get('ZANCADA', 0.12)
        with open(os.path.join(CLI, clase(nombre) + 'Animaciones.java'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(java_anims(nombre, hs, anims))
        with open(os.path.join(ENT, clase(nombre) + 'Geometria.java'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(java_geometria(nombre, hs, anims, puntos, tiempos, anclas))
        nk = sum(len(ks) for n in ORDEN for _, _, ks in canales(hs, anims[n]))
        print(f'{nombre}: {nk} claves; zancada {tiempos.get("ZANCADA")}', flush=True)
        for k, v in puntos.items():
            print(f'   {k:16s} izq {v[0]:6.2f}  alto {v[1]:6.2f}  frente {v[2]:6.2f}')
        if HOJAS:
            os.makedirs(HOJAS, exist_ok=True)
            for n in (cuales or ORDEN):
                a_ = anims[n]
                ts = [a_.dur * k / 5 for k in range(6)] if not a_.bucle else [a_.dur * k / 6 for k in range(6)]
                hoja(nombre, hs, malla, a_, ts, HOJAS)
                print('   hoja', n, flush=True)

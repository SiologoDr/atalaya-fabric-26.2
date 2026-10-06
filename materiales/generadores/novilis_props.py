"""
Las piezas de Novilis, el Caballero Solar, para el juego:

  - las cuatro ESTATUAS de angel de las Trompetas del Apocalipsis (la misma
    malla para las cuatro: el renderer las gira hacia el centro), enteras y
    rotas;
  - las tres FUENTES SOLARES del ataque cooperativo, enteras y rotas.

Es la UNICA fuente de su geometria. De aqui salen:
  - src/client/.../EstatuaNovilisMalla.java   crear() y crearRota()
  - src/client/.../FuenteSolarMalla.java      crear() y crearRota()
  - textures/entity/novilis/estatua.png y estatua_brillo.png   (un atlas para
    la entera y la rota: la rota no usa nada que brille)
  - textures/entity/novilis/fuente.png y fuente_brillo.png      (igual)
y, si se le da carpeta, los renders de comprobacion y la presentacion.

Unidades: pixeles de modelo, 16 = 1 bloque, Y hacia abajo, el frente mira a
-Z y la base en y = 24 (como las entidades de vanilla). Se pinta a escala x1:
un texel por pixel de modelo, la misma densidad que un bloque.
  estatua: de y = 24 (suelo) a y = -96 -> 120 px = 7,5 bloques
  fuente:  de y = 24 a y = -56 -> 80 px = 5 bloques; el sol flota encima

Uso: python novilis_props.py <raiz del proyecto> [carpeta de renders]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr

D2R = math.pi / 180
T, Rx, Ry, Rz = vr.T, vr.Rx, vr.Ry, vr.Rz
ESCALA = 1.0


# ----------------------------------------------------------------------
#  Algebra
# ----------------------------------------------------------------------
def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def base_y(y, z_pista):
    """Base ortonormal (columnas X, Y, Z): la Y local hacia y, la Z lo mas
    cerca posible de z_pista."""
    y = unit(y)
    z = np.asarray(z_pista, float)
    z = unit(z - np.dot(z, y) * y)
    return np.column_stack([np.cross(y, z), y, z])


def rot3(rx, ry, rz):
    return (Rz(rz * D2R) @ Ry(ry * D2R) @ Rx(rx * D2R))[:3, :3]


def euler(R):
    """(rx, ry, rz) en grados con R = Rz Ry Rx (el orden de ModelPart)."""
    s = max(-1.0, min(1.0, -R[2, 0]))
    b = math.asin(s)
    if abs(s) < 0.99999:
        a = math.atan2(R[2, 1], R[2, 2])
        c = math.atan2(R[1, 0], R[0, 0])
    else:
        a = math.atan2(-R[1, 2], R[1, 1])
        c = 0.0
    return (math.degrees(a), math.degrees(b), math.degrees(c))


# ----------------------------------------------------------------------
#  El modelo: piezas con pivote, giro y cajas (x0, y0, z0, w, h, d, mat)
# ----------------------------------------------------------------------
class Parte:
    def __init__(self, nombre, padre, pivote, rot, cajas):
        self.nombre, self.padre = nombre, padre
        self.pivote = tuple(float(v) for v in pivote)
        self.rot = tuple(float(v) for v in rot)
        self.cajas = [tuple(c) for c in cajas]
        self.hijos = []


class Modelo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.partes = {}
        self.orden = []

    def parte(self, nombre, padre=None, pivote=(0, 0, 0), rot=(0, 0, 0), cajas=()):
        assert nombre not in self.partes, nombre
        self.partes[nombre] = Parte(nombre, padre, pivote, rot, cajas)
        self.orden.append(nombre)
        if padre:
            self.partes[padre].hijos.append(nombre)
        return nombre

    def local(self, nombre):
        p = self.partes[nombre]
        return T(*p.pivote) @ Rz(p.rot[2] * D2R) @ Ry(p.rot[1] * D2R) @ Rx(p.rot[0] * D2R)

    def mundo(self, nombre):
        p = self.partes[nombre]
        M = self.local(nombre)
        return self.mundo(p.padre) @ M if p.padre else M

    def parte_en(self, nombre, padre, pos, R, cajas=()):
        """Una pieza colocada en el espacio del modelo: posicion y giro (3x3)
        absolutos, que se pasan al espacio del padre."""
        Mp = self.mundo(padre) if padre else np.eye(4)
        piv = np.linalg.solve(Mp, np.array([*pos, 1.0]))[:3]
        return self.parte(nombre, padre, piv, euler(Mp[:3, :3].T @ R), cajas)

    def parte_r(self, nombre, padre, pivote, R, cajas=()):
        """Una pieza con su giro dado como matriz 3x3 (en el espacio del padre)."""
        return self.parte(nombre, padre, pivote, euler(R), cajas)

    def a_mundo(self, nombre, p=(0, 0, 0)):
        return (self.mundo(nombre) @ np.array([*p, 1.0]))[:3]

    def cajas(self, nombre, *cs):
        self.partes[nombre].cajas.extend(tuple(c) for c in cs)

    def matrices(self):
        out = {}
        for n in self.orden:
            p = self.partes[n]
            out[n] = (out[p.padre] if p.padre else np.eye(4)) @ self.local(n)
        return out


def apoyar(m, nombre, suelo):
    """Baja o sube una pieza suelta (hija de la raiz, sin giro) hasta que su
    punto mas bajo toque 'suelo' (y hacia abajo): los trozos caidos se posan."""
    Ms = m.matrices()
    pila, ys = [nombre], []
    while pila:
        n = pila.pop()
        pila.extend(m.partes[n].hijos)
        for c in m.partes[n].cajas:
            x0, y0, z0, w, h, d, _ = c
            for dx in (0, w):
                for dy in (0, h):
                    for dz in (0, d):
                        ys.append((Ms[n] @ np.array([x0 + dx, y0 + dy, z0 + dz, 1.0]))[1])
    p = m.partes[nombre]
    p.pivote = (p.pivote[0], p.pivote[1] + suelo - max(ys), p.pivote[2])


def espejo_caja(c):
    x0, y0, z0, w, h, d, mat = c
    return (-x0 - w, y0, z0, w, h, d, mat)


# ======================================================================
#  LA ESTATUA
# ======================================================================
# Alturas (y, hacia abajo). La figura mide 90 px de los pies a la coronilla
# (8 cabezas de 11,25): pies 6, rodilla -16,5, cadera -43, cintura -53,
# pecho -61,5, hombros -68, barbilla -72,7, coronilla -84. Las alas suben a -96.
PIE_Y = 6.0
CINTURA_Y = -53.0

# La trompeta: sube 33 grados y se abre 22 hacia la derecha de la figura (-X),
# para no taparle la cara a quien la mira de frente.
TROMPETA_ELEV = 30.0
TROMPETA_GIRO = 50.0
LARGO_TUBO = 29.0


def pedestal(m, padre, nombre='pedestal'):
    """Plinto de marmol con molduras de oro y un sol en cada cara."""
    m.parte(nombre, padre, (0, 0, 0), cajas=[
        (-15, 20.5, -15, 30, 3.5, 30, 'ped'),
        (-14.4, 19.4, -14.4, 28.8, 1.1, 28.8, 'oro'),
        (-13.7, 18.3, -13.7, 27.4, 1.1, 27.4, 'ped'),
        (-12.5, 9.4, -12.5, 25, 8.9, 25, 'ped_panel'),
        (-13.7, 8.3, -13.7, 27.4, 1.1, 27.4, 'ped'),
        (-14.3, 7.3, -14.3, 28.6, 1.0, 28.6, 'oro'),
        (-13.5, 6.0, -13.5, 27, 1.3, 27, 'ped'),
    ])
    # el sol de cada cara: un disco y una estrella girada 45 grados
    for k in range(4):
        a = k * 90.0
        R = rot3(0, a, 0)
        c = R @ np.array([0, 13.85, -12.5])
        m.parte_en(f'{nombre}_sol{k}', nombre, c, R, [(-2.2, -2.2, -0.55, 4.4, 4.4, 0.6, 'oro')])
        m.parte_en(f'{nombre}_rayos{k}', nombre, c, R @ rot3(0, 0, 45), [(-2.0, -2.0, -0.35, 4.0, 4.0, 0.4, 'oro'),
                                                                        (-0.5, -3.4, -0.3, 1.0, 6.8, 0.3, 'oro'),
                                                                        (-3.4, -0.5, -0.3, 6.8, 1.0, 0.3, 'oro')])


# ---------------------------- la ropa ---------------------------------
# El peplo: una falda larga hasta el plinto y, encima, la sobrefalda (el
# apoptygma) hasta medio muslo, mas baja por los lados. Las dos son duelas
# (tablas) alrededor del cuerpo que se abren hacia abajo; los huecos entre
# duelas, alternas mas fuera y mas dentro, hacen los pliegues.
N_DUELAS = 16
THETA_RODILLA = 32.0     # la rodilla de la pierna libre (izquierda, +X), por delante


def _elipse(th, y, rx, rzf, rzb, cx):
    s, c = math.sin(math.radians(th)), math.cos(math.radians(th))
    rz = rzf * (1 + c) / 2 + rzb * (1 - c) / 2
    return np.array([cx + rx * s, y, -rz * c]), unit([s / rx, 0.0, -c / rz])


def _cadera(th, extra=0.0):
    """La cadera en contrapposto: la derecha (la del peso, -X) mas alta y salida."""
    s = math.sin(math.radians(th))
    return _elipse(th, 9.5 + 1.7 * s, 9.0 + extra, 5.5 + extra, 6.4 + extra, -1.4)


def anillo_falda(nivel, th):
    if nivel == 0:      # bajo el cinto
        return _elipse(th, 0.3, 5.5, 3.9, 4.2, 0.0)
    if nivel == 1:
        return _cadera(th)
    if nivel == 2:
        p, n = _elipse(th, 35.5, 9.6, 6.3, 7.6, -0.6)
        return p + n * 3.8 * math.exp(-(_dif(th, THETA_RODILLA) / 25.0) ** 2), n     # la rodilla empuja la tela
    # el bajo, sobre el plinto: delante se levanta sobre los pies; detras arrastra
    y = PIE_Y - CINTURA_Y + 0.7 - 1.5 * max(0.0, math.cos(math.radians(th - 10))) ** 3
    return _elipse(th, y, 12.4, 9.0, 12.0, -0.3)


def anillo_sobre(nivel, th):
    """La sobrefalda (apoptygma): de la cintura a medio muslo, mas baja por los
    lados, donde se recoge la tela, y un poco mas por la izquierda (la cadera
    caida)."""
    if nivel == 0:
        return _elipse(th, 0.3, 5.7, 4.1, 4.3, 0.0)
    if nivel == 1:
        return _cadera(th, 0.9)
    s = math.sin(math.radians(th))
    p, n = _elipse(th, 20.5 + 6.0 * s * s + 1.6 * s, 10.6, 7.0, 8.0, -0.9)
    return p + n * 1.4 * math.exp(-(_dif(th, THETA_RODILLA) / 30.0) ** 2), n


def duelas(m, padre, prefijo, anillo, niveles, grosor, rota=None, semilla=5):
    """Duelas de un anillo al siguiente; la ultima lleva el ribete de oro.
    rota: None, o la altura relativa (0-1) a la que se quiebra cada duela."""
    r = random.Random(semilla)
    for k in range(N_DUELAS):
        th = k * 360.0 / N_DUELAS
        fuera = 0.55 if k % 2 == 0 else -0.45
        pts = [anillo(nv, th) for nv in range(niveles)]
        pts = [(p + n * fuera, n) for p, n in pts]
        for tramo in range(niveles - 1):
            (a, na), (b, nb) = pts[tramo], pts[tramo + 1]
            L = float(np.linalg.norm(b - a))
            # el ancho: el perimetro a esa altura entre las duelas, con solape
            pa = _perimetro(anillo, tramo, niveles)
            w = pa / N_DUELAS * 1.2
            R = base_y(b - a, -unit(na + nb))
            y0, h = -0.5, L + 1.0
            ultimo = tramo == niveles - 2
            if rota is not None:
                if not ultimo:
                    continue
                corte = r.uniform(*rota) * L
                y0, h = corte, L + 0.5 - corte
            cajas = [(-w / 2, y0, -grosor / 2, w, h, grosor, 'tela')]
            if k % 2 == 0 and tramo > 0 and rota is None:
                # la arista del pliegue, en relieve
                cajas.append((-0.6, y0 + 0.3, -grosor / 2 - 0.7, 1.2, h - 0.6, 1.0, 'tela'))
            if ultimo:
                cajas.append((-w / 2 - 0.05, L - 1.1, -grosor / 2 - 0.3, w + 0.1, 1.5, grosor + 0.35, 'oro'))
            m.parte_en(f'{prefijo}_{k}_{tramo}', padre, m.a_mundo(padre, a), R, cajas)


def _perimetro(anillo, tramo, niveles):
    tot = 0.0
    for nv in (tramo, tramo + 1):
        ps = [anillo(nv, th)[0] for th in range(0, 360, 10)]
        tot += sum(math.hypot(ps[i][0] - ps[i - 1][0], ps[i][2] - ps[i - 1][2]) for i in range(len(ps)))
    return tot / 2


def ropa(m, padre, rota=False):
    m.parte('falda', padre, (0, CINTURA_Y, 0))
    if rota:
        duelas(m, 'falda', 'falda', anillo_falda, 4, 1.8, rota=(0.15, 0.75))
        return
    duelas(m, 'falda', 'falda', anillo_falda, 4, 1.8)
    duelas(m, 'falda', 'sobre', anillo_sobre, 3, 1.5, semilla=6)


def pies(m, padre):
    """Los pies asoman bajo el borde: el derecho (el del peso) recto, el
    izquierdo adelantado y abierto, con el talon un poco alzado. Sandalias de oro."""
    for nombre, x, z, ry, rx in (('pie_der', -3.3, -5.3, 8, 0), ('pie_izq', 3.9, -6.6, -16, 6)):
        m.parte(nombre, padre, (x, PIE_Y, z), (rx, ry, 0), [
            (-1.55, -2.0, -4.6, 3.1, 2.0, 6.0, 'piel'),
            (-1.35, -1.45, -5.9, 2.7, 1.45, 1.5, 'piel'),        # dedos
            (-1.7, -2.25, -2.8, 3.4, 0.5, 0.8, 'oro'),           # tira de la sandalia
            (-1.65, -0.45, -6.0, 3.3, 0.45, 7.4, 'oro'),         # suela
        ])


def _dif(a, b):
    return (a - b + 180) % 360 - 180


def anillo_corpino(nivel, th):
    """El corpino del quiton, plisado: anillos del escote a la cintura (espacio
    del torso). El pecho lo empujan dos bultos suaves en el anillo del busto."""
    c = math.cos(math.radians(th))
    if nivel == 0:     # escote en barca: baja delante y detras, sube a los hombros
        return _elipse(th, -16.2 + 1.5 * c * c, 6.5, 3.6, 3.9, 0.0)
    if nivel == 1:     # el busto
        p, n = _elipse(th, -10.2, 6.7, 4.0, 4.1, 0.0)
        for tb in (25.0, -25.0):
            p = p + n * 1.9 * math.exp(-(_dif(th, tb) / 21.0) ** 2)
        return p, n
    if nivel == 2:     # bajo el pecho
        p, n = _elipse(th, -6.8, 6.0, 3.75, 4.0, 0.0)
        for tb in (25.0, -25.0):
            p = p + n * 0.45 * math.exp(-(_dif(th, tb) / 21.0) ** 2)
        return p, n
    return _elipse(th, 0.6, 5.3, 3.65, 3.9, 0.0)      # la cintura


def plisado(m, padre, prefijo, anillo, niveles, grosor, n_duelas, oro_arriba=False):
    """Como duelas(), pero de arriba abajo y con el ribete arriba (el escote)."""
    for k in range(n_duelas):
        th = k * 360.0 / n_duelas
        fuera = 0.22 if k % 2 == 0 else -0.18
        pts = [anillo(nv, th) for nv in range(niveles)]
        pts = [(p + n * fuera, n) for p, n in pts]
        for tramo in range(niveles - 1):
            (a, na), (b, nb) = pts[tramo], pts[tramo + 1]
            L = float(np.linalg.norm(b - a))
            per = 0.0
            for nv in (tramo, tramo + 1):
                ps = [anillo(nv, t)[0] for t in range(0, 360, 10)]
                per += sum(math.hypot(ps[i][0] - ps[i - 1][0], ps[i][2] - ps[i - 1][2]) for i in range(len(ps))) / 2
            w = per / n_duelas * 1.22
            R = base_y(b - a, -unit(na + nb))
            cajas = [(-w / 2, -0.4, -grosor / 2, w, L + 0.8, grosor, 'tela')]
            if oro_arriba and tramo == 0:
                cajas.append((-w / 2 - 0.05, -0.55, -grosor / 2 - 0.25, w + 0.1, 0.75, grosor + 0.3, 'oro'))
            m.parte_r(f'{prefijo}_{k}_{tramo}', padre, a, R, cajas)


def _cruz(x0, y0, z0, w, h, d, mat, k=0.72):
    """Una seccion redondeada: dos cajas en cruz (ancha y poco honda, y
    estrecha y honda), que juntas dejan las esquinas achaflanadas."""
    return [(x0, y0, z0 + d * (1 - k) / 2, w, h, d * k, mat),
            (x0 + w * (1 - k) / 2, y0, z0, w * k, h, d, mat)]


# ---------------------------- el cuerpo -------------------------------
def torso(m, padre):
    """Torso en contrapposto: un poco echado atras, girado hacia la trompeta y
    con los hombros al reves que la cadera. El corpino es plisado (duelas)."""
    m.parte('torso', padre, (0, CINTURA_Y, 0.3), (-3, 8, -3), [
        (-5.0, -15.0, -3.0, 10.0, 15.6, 6.4, 'tela'),         # el alma (tapa los huecos del plisado)
        *_cruz(-4.6, -17.0, -3.4, 9.2, 3.8, 6.8, 'piel', 0.8),  # escote y base del cuello
        (-5.95, -1.0, -4.2, 11.9, 1.7, 8.4, 'oro'),          # el cinto
        (-1.0, -1.5, -4.65, 2.0, 2.6, 0.6, 'oro'),           # su nudo
    ])
    plisado(m, 'torso', 'corpino', anillo_corpino, 4, 1.2, 14, oro_arriba=True)
    # hombros caidos (trapecio): de la base del cuello bajan hacia fuera
    for s, n in ((1, 'izq'), (-1, 'der')):
        caja = (0, 0, -3.0, 4.8, 2.4, 6.0, 'piel')
        m.parte('trapecio_' + n, 'torso', (2.0 * s, -17.0, 0.2), (0, 0, 24 * s), [espejo_caja(caja) if s < 0 else caja])
        m.parte('fibula_' + n, 'torso', (5.6 * s, -16.0, -0.4), (0, 0, 22 * s), [(-1.0, -1.0, -1.0, 2.0, 1.3, 2.0, 'oro')])


K_CABEZA = 0.88      # la cabeza, algo menor: la figura queda mas esbelta


def _k(c, k=None):
    k = K_CABEZA if k is None else k
    return tuple(v * k for v in c[:6]) + (c[6],)


def cabeza(m):
    """Cabeza ovalada y pequena, de perfil griego: frente, arco de las cejas,
    nariz recta que sale de la frente, labios y barbilla marcados. El pelo,
    con raya al medio, se recoge sobre las orejas y cae suelto por la espalda
    (melena())."""
    m.parte('cuello', 'torso', (0, -16.3, -0.2), (-5, 8, 2), _cruz(-1.7, -4.0, -1.8, 3.4, 4.6, 3.6, 'piel', 0.75))
    k = K_CABEZA
    m.parte('cabeza', 'cuello', (0, -3.5, -0.3), (-9, 14, 3), [_k(c) for c in [
        *_cruz(-3.9, -9.6, -3.4, 7.8, 6.8, 8.6, 'piel', 0.8),     # craneo, redondeado
        (-3.1, -8.6, -4.5, 6.2, 5.8, 4.8, 'rostro'),         # la cara: frente, ojos y pomulos
        (-2.2, -3.1, -4.4, 4.4, 2.4, 5.2, 'piel'),           # boca y mejillas
        (-1.05, -1.1, -4.85, 2.1, 1.45, 3.0, 'piel'),        # barbilla, adelantada
        (-2.7, -6.3, -4.95, 5.4, 0.55, 0.5, 'piel'),         # arco de las cejas
        (-0.45, -5.9, -5.35, 0.9, 2.2, 0.85, 'piel'),        # nariz: el puente
        (-0.55, -3.9, -5.75, 1.1, 1.0, 1.25, 'piel'),        # y la punta
        (-0.8, -2.15, -4.75, 1.6, 0.55, 0.35, 'piel'),       # labios
        (-0.7, -1.6, -4.7, 1.4, 0.45, 0.3, 'piel'),
        # el pelo: casquete, nuca y ondas recogidas hacia atras sobre las orejas
        *_cruz(-4.4, -10.6, -3.1, 8.8, 2.2, 8.9, 'pelo', 0.8),
        (-3.3, -11.2, -2.2, 6.6, 0.8, 7.0, 'pelo'),
        (-4.2, -9.6, 3.2, 8.4, 8.0, 2.4, 'pelo'),
        (-3.6, -8.8, 5.4, 7.2, 6.4, 1.4, 'pelo'),            # el nacimiento de la melena
        (-4.45, -9.2, -2.9, 1.15, 4.4, 6.1, 'pelo'),
        (3.3, -9.2, -2.9, 1.15, 4.4, 6.1, 'pelo'),
        (-4.3, -5.2, -1.3, 1.1, 4.8, 4.9, 'pelo'),
        (3.2, -5.2, -1.3, 1.1, 4.8, 4.9, 'pelo'),
        (-0.65, -9.75, -5.25, 1.3, 1.3, 0.45, 'oro'),        # la joya de la diadema
    ]])
    for s_, n in ((1, 'izq'), (-1, 'der')):
        def esp(c):
            return _k(c if s_ > 0 else espejo_caja(c))
        # la mandibula: dos planos que bajan en V hasta la barbilla
        m.parte('mandibula_' + n, 'cabeza', (2.95 * s_ * k, -3.6 * k, 0.0), (0, 0, 27 * s_),
                [esp((-1.0, 0, -3.0, 1.0, 3.7, 5.2, 'piel'))])
        # el arranque del pelo: de la raya hacia las sienes, en arco
        m.parte('flequillo_' + n, 'cabeza', (0.15 * s_ * k, -9.7 * k, -4.0 * k), (0, 0, 20 * s_),
                [esp((0, 0, -0.95, 4.3, 1.5, 2.2, 'pelo'))])
        m.parte('diadema_' + n, 'cabeza', (0.0, -9.05 * k, -4.95 * k), (0, 0, 14 * s_),
                [esp((0, -0.1, -0.25, 4.2, 0.55, 0.4, 'oro'))])
    # el halo: un disco de sol (nimbo) bien detras de la cabeza y por encima,
    # como un sol que sale tras ella (no la enmarca); oro mate con el canto de
    # oro claro. Va con el torso, de
    # cara al frente de la estatua, aunque ella gire la cabeza hacia la trompeta.
    Mt = m.mundo('torso')
    c = np.linalg.solve(Mt, np.array([*m.a_mundo('cabeza', (0, -5.6 * k, 1.0 * k)), 1.0]))[:3]
    m.parte('halo', 'torso', (c[0], c[1] - 4.2, c[2] + 8.2), (-10, 0, 0))
    for i in range(4):          # el disco: cuatro cuadrados girados (un poligono de 16 lados)
        m.parte(f'halo_disco{i}', 'halo', (0, 0, 0), (0, 0, i * 22.5), [(-4.9, -4.9, 0.1, 9.8, 9.8, 0.5, 'oro_mate')])
    n = 16
    for i in range(n):
        m.parte(f'halo_{i}', 'halo', (0, 0, 0), (0, 0, i * 360.0 / n),
                [(-1.1, -5.9, -0.45, 2.2, 0.95, 1.1, 'oro')])


def _hebra(m, nombre, padre, pts, ancho, grueso, normal):
    """Un mechon: tramos encadenados por los puntos (espacio del modelo), con la
    cara ancha hacia 'normal' (espacio del modelo)."""
    for i in range(len(pts) - 1):
        a, b = np.asarray(pts[i], float), np.asarray(pts[i + 1], float)
        L = float(np.linalg.norm(b - a))
        w = ancho * (1 - 0.12 * i / max(1, len(pts) - 2))
        m.parte_en(f'{nombre}_{i}', padre, a, base_y(b - a, normal),
                   [(-w / 2, -0.5, -grueso / 2, w, L + 1.0, grueso, 'pelo')])


def melena(m):
    """La melena suelta: dos capas de mechones escalonados que nacen en la nuca
    y caen por la espalda entre las alas, ondulando, hasta media espalda; y
    otros dos que caen por delante del hombro derecho hasta el pecho."""
    Mt = m.mundo('torso')

    def T_(p):
        return (Mt @ np.array([*p, 1.0]))[:3]
    atras = Mt[:3, :3] @ np.array([0, 0, 1.0])
    k = K_CABEZA
    capas = [  # (x en la nuca, largo, z sobre la espalda, ancho, grueso)
        [(-3.4, 16, 5.6, 2.4, 1.3), (-1.7, 20, 5.6, 2.4, 1.3), (0.0, 23, 5.6, 2.4, 1.3),
         (1.7, 19, 5.6, 2.4, 1.3), (3.4, 15, 5.6, 2.4, 1.3)],
        [(-2.5, 12, 6.7, 2.2, 1.2), (-0.8, 15, 6.7, 2.2, 1.2), (0.9, 14, 6.7, 2.2, 1.2), (2.6, 11, 6.7, 2.2, 1.2)],
    ]
    for c, capa in enumerate(capas):
        for i, (x, largo, z, w, g) in enumerate(capa):
            ini = m.a_mundo('cabeza', (x * 0.8 * k, -5.0 * k, 5.6 * k))
            onda = 0.6 if (i + c) % 2 else -0.6
            pts = [ini, T_((x, -16.5, z))]
            for j, f in enumerate((0.35, 0.7, 1.0)):
                y = -16.5 + largo * f
                zz = z - 0.9 * f                          # la espalda se mete hacia la cintura
                pts.append(T_((x * (1 + 0.15 * f) + (onda if j % 2 == 0 else -onda), y, zz)))
            _hebra(m, f'melena_{c}{i}', 'torso', pts, w, g, atras)
    # por delante del hombro derecho
    fuera = Mt[:3, :3] @ unit([-0.6, 0, -1.0])
    for i, (dx, largo) in enumerate(((0.0, 1.0), (1.3, 0.8))):
        ini = m.a_mundo('cabeza', ((-3.0 - dx * 0.3) * k, -4.0 * k, 1.2 * k))
        pts = [ini, T_((-4.0 + dx * 0.4, -17.4, 0.6)), T_((-5.0 + dx * 0.5, -15.2, -3.4)),
               T_((-4.6 + dx * 0.6, -11.4, -5.6)), T_((-4.2 + dx * 0.7, -11.4 + 5.0 * largo, -5.2))]
        _hebra(m, f'mechon_{i}', 'torso', pts, 2.2 - 0.3 * i, 1.2, fuera)


def trompeta(m):
    """La trompeta larga de heraldo, de la boca hacia arriba y adelante."""
    boca = m.a_mundo('cabeza', (0, -1.85 * K_CABEZA, -4.95 * K_CABEZA))
    e, g = math.radians(TROMPETA_ELEV), math.radians(TROMPETA_GIRO)
    d = np.array([-math.sin(g) * math.cos(e), -math.sin(e), -math.cos(g) * math.cos(e)])
    R = base_y(d, [0, -1, 0])
    m.parte_en('trompeta', 'torso', boca + d * 0.2, R, [
        (-0.95, -0.4, -0.95, 1.9, 1.5, 1.9, 'oro'),          # boquilla
        (-0.7, 0.8, -0.7, 1.4, LARGO_TUBO + 0.4, 1.4, 'oro'),  # el tubo
        (-1.1, 6.0, -1.1, 2.2, 1.2, 2.2, 'oro'),             # nudos
        (-1.1, 15.5, -1.1, 2.2, 1.2, 2.2, 'oro'),
        (-1.0, LARGO_TUBO - 0.4, -1.0, 2.0, 1.2, 2.0, 'oro'),
    ])
    campana(m, 'trompeta', LARGO_TUBO + 0.6)
    return boca, d


def campana(m, padre, y, oro='campana', luz=True, nombre='campana'):
    """La campana: dos coronas de duelas que se abren (la curva del pabellon)
    y el borde; dentro, la luz."""
    m.parte(nombre, padre, (0, y, 0))
    n = 8
    for k in range(n):
        Rk = rot3(0, k * 360.0 / n, 0)
        e = Rk @ np.array([0, 0, -1.0])
        for i, (r0, r1, y0, y1, w) in enumerate(((0.75, 2.0, 0.0, 3.2, 1.45), (2.0, 4.7, 3.2, 5.9, 3.4))):
            a = np.array([0, y0, 0]) + e * r0
            v = np.array([0, y1 - y0, 0]) + e * (r1 - r0)
            L = float(np.linalg.norm(v))
            R = base_y(v, -e)
            cajas = [(-w / 2, -0.3, -0.3, w, L + 0.6, 0.6, oro if i else ('oro' if oro == 'campana' else oro))]
            if i == 1:
                wr = 2 * math.pi * 4.9 / n * 1.12
                cajas.append((-wr / 2, L - 0.6, -0.75, wr, 1.1, 1.1, 'oro' if oro == 'campana' else oro))
            m.parte_r(f'{nombre}_{k}_{i}', nombre, a, R, cajas)
    if luz:
        m.cajas(nombre, (-2.6, 4.0, -2.6, 5.2, 0.6, 5.2, 'oro_luz'))
        m.parte(nombre + '_luz', nombre, (0, 0, 0), (0, 45, 0), [(-2.6, 4.05, -2.6, 5.2, 0.6, 5.2, 'oro_luz')])


def _ik(S, W, L1, L2, polo):
    """Codo de un brazo de dos tramos del hombro S a la muneca W."""
    v = W - S
    dist = min(float(np.linalg.norm(v)), L1 + L2 - 0.05)
    u = unit(v)
    a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    p = np.asarray(polo, float)
    p = unit(p - np.dot(p, u) * u)
    return S + u * a + p * h


L_BRAZO, L_ANTEBRAZO = 13.4, 12.2
AGARRES = {'izq': (10.5, (-0.2, 1.0, -0.6)), 'der': (19.0, (-1.0, 1.1, 0.4))}


def brazos(m, boca, d):
    """Los dos brazos, por cinematica inversa hasta la trompeta: la izquierda
    la sostiene junto a la boquilla, con el codo recogido delante del pecho (el
    antebrazo pasa bajo la barbilla, por el lado que no se ve); la derecha, del
    lado de la trompeta, se estira y la coge lejos. Ninguno tapa la cara."""
    for s, n in ((1, 'izq'), (-1, 'der')):
        agarre, polo = AGARRES[n]
        S = m.a_mundo('torso', (7.3 * s, -14.4, 0.2))
        G = boca + d * (0.2 + agarre) + np.array([0, 1.1, 0])   # la mano, bajo el tubo
        mano = unit(G - S)
        for _ in range(5):           # la muneca, un poco antes del agarre
            W = G - mano * 2.2
            E = _ik(S, W, L_BRAZO, L_ANTEBRAZO, polo)
            mano = unit(G - (E + unit(W - E) * L_ANTEBRAZO))
        W = G - mano * 2.2
        E = _ik(S, W, L_BRAZO, L_ANTEBRAZO, polo)
        R1 = base_y(E - S, [0, 0, 1])
        b = m.parte_en('brazo_' + n, 'torso', S, R1, [
            *_cruz(-1.9, -2.0, -1.9, 3.8, 5.0, 3.8, 'piel', 0.72),      # el hombro (deltoides)
            *_cruz(-1.6, 2.6, -1.6, 3.2, 5.6, 3.2, 'piel', 0.74),       # el brazo, lleno
            *_cruz(-1.35, 7.8, -1.4, 2.7, 6.4, 2.8, 'piel', 0.74),      # y mas fino hacia el codo
            (-1.72, 4.6, -1.72, 3.44, 0.8, 3.44, 'oro'),                # brazalete
        ])
        R2 = base_y(W - E, [0, 0, 1])
        a = m.parte_en('antebrazo_' + n, b, E, R2, [
            *_cruz(-1.35, -0.9, -1.4, 2.7, 5.4, 2.8, 'piel', 0.74),
            *_cruz(-1.1, 4.2, -1.15, 2.2, 4.8, 2.3, 'piel', 0.74),
            *_cruz(-0.9, 8.6, -0.95, 1.8, 4.2, 1.9, 'piel', 0.74),      # la muneca
            (-1.05, 10.3, -1.1, 2.1, 0.8, 2.2, 'oro'),                  # pulsera
        ])
        # la mano cerrada sobre el tubo: el dorso a un lado, los cuatro dedos
        # dando la vuelta por el otro (el tubo pasa por dentro del puno) y el
        # pulgar a lo largo del tubo
        R3 = base_y(G - W, d)
        cajas = [(-2.2, -0.4, -1.7, 1.6, 4.0, 3.4, 'piel'),           # palma y dorso
                 (-0.8, 0.1, -2.75, 1.2, 2.2, 1.1, 'piel')]            # pulgar
        for i in range(4):
            cajas.append((-0.7, 1.0 + 0.15 * (i % 2), -1.66 + i * 0.84, 2.0, 2.6, 0.78, 'piel'))
        m.parte_en('mano_' + n, a, W, R3, cajas)


# ---------------------------- las alas --------------------------------
# El ala, en su propio plano: Y hacia abajo, Z hacia atras, X el grosor
# (hacia fuera). El hueso sube del hombro a la muneca, por encima de la
# cabeza, y de ahi baja hacia atras; de el cuelgan las plumas en cuatro filas.
HUESO_ALA = [(0.0, 0.0), (1.0, -8.5), (3.2, -17.0), (6.8, -24.5), (11.5, -28.5), (16.5, -28.8), (21.0, -26.0)]


def _sobre_hueso(t):
    """Punto (z, y) a lo largo del hueso, t de 0 (hombro) a 1 (punta)."""
    seg = [math.dist(HUESO_ALA[i], HUESO_ALA[i + 1]) for i in range(len(HUESO_ALA) - 1)]
    s = t * sum(seg)
    for i, L in enumerate(seg):
        if s <= L or i == len(seg) - 1:
            f = min(1.0, s / L)
            a, b = HUESO_ALA[i], HUESO_ALA[i + 1]
            return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        s -= L


def _suave(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# Las filas: (cuantas, t0, t1, largo(t), caida(t) en grados hacia atras,
#             ancho, grueso, separacion del plano, material, por las dos caras)
FILAS_ALA = [
    ('remera', 12, 0.0, 1.0, lambda t: 13 + 4 * t + 22 * _suave((t - 0.35) / 0.65),
     lambda t: 2 + 10 * t + 22 * _suave((t - 0.5) / 0.5), 5.2, 0.9, 0.0, 'pluma', False),
    ('cobertera', 10, 0.03, 0.97, lambda t: 7.5 + 3 * t + 6 * _suave((t - 0.45) / 0.55),
     lambda t: 5 + 10 * t + 16 * _suave((t - 0.5) / 0.5), 4.8, 1.0, 0.65, 'pluma', True),
    ('menor', 9, 0.05, 0.95, lambda t: 5.0 + 2 * t,
     lambda t: 10 + 12 * t + 10 * _suave((t - 0.5) / 0.5), 4.2, 1.1, 1.05, 'pluma_cob', True),
    ('marginal', 8, 0.07, 0.92, lambda t: 3.4 + 1.0 * t, lambda t: 22 + 24 * t, 3.6, 1.2, 1.45, 'pluma_cob', True),
]


def plumas_ala(rota=False):
    """El trazado de las plumas en el plano del ala, de atras (remeras) a
    delante: [(fila, z, y, caida, largo, ancho)]."""
    out = []
    for (etiqueta, cuantas, t0, t1, largo, caida, ancho, grueso, xo, mat, dos) in FILAS_ALA:
        for k in range(cuantas):
            t = t0 + (t1 - t0) * k / (cuantas - 1)
            if rota and t > 0.32:
                continue
            z, y = _sobre_hueso(t)
            out.append((etiqueta, z + 0.5, y + 0.7, caida(t), largo(t), ancho))
    return out


def marco_ala(rota=False):
    """El rectangulo (z0, y0, ancho, alto) del plano del ala, en px enteros."""
    zs, ys = [], []
    for (_, z, y, a, L, w) in plumas_ala(rota):
        d = np.array([math.sin(math.radians(a)), math.cos(math.radians(a))])
        p = np.array([-d[1], d[0]])
        for s_ in (-0.6, L):
            for q in (-w / 2, w / 2):
                c = np.array([z, y]) + d * s_ + p * q
                zs.append(c[0])
                ys.append(c[1])
    for (z, y) in HUESO_ALA:
        zs.append(z)
        ys.append(y)
    z0, y0 = math.floor(min(zs)) - 1, math.floor(min(ys)) - 1
    return z0, y0, math.ceil(max(zs)) + 1 - z0, math.ceil(max(ys)) + 1 - y0


_SPRITES = {}


def sprite_ala(rota=False):
    """El ala pintada en su plano (y hacia abajo, z hacia atras), un texel por
    px: cada pluma con la raiz en sombra, la punta clara y el borde marcado, y
    la sombra que cada fila echa sobre la de debajo. Fuera del ala, transparente."""
    if rota in _SPRITES:
        return _SPRITES[rota]
    z0, y0, W, H = marco_ala(rota)
    zz, yy = np.meshgrid(np.arange(W) + z0 + 0.5, np.arange(H) + y0 + 0.5)
    v = np.zeros((H, W))
    lleno = np.zeros((H, W), bool)
    rnd = random.Random(41)
    for (fila, z, y, a, L, w) in plumas_ala(rota):
        d = np.array([math.sin(math.radians(a)), math.cos(math.radians(a))])
        p = np.array([-d[1], d[0]])
        s_ = (zz - z) * d[0] + (yy - y) * d[1]
        q = (zz - z) * p[0] + (yy - y) * p[1]
        punta = min(w * 1.1, L * 0.45)
        media = np.where(s_ > L - punta, (w / 2) * np.sqrt(np.clip((L - s_) / punta, 0, 1)), w / 2)
        dentro = (s_ >= -0.6) & (s_ <= L) & (np.abs(q) <= media)
        # la sombra de esta pluma sobre lo que ya habia debajo, junto a su borde
        if fila != 'remera':
            halo = (s_ >= -0.6) & (s_ <= L + 1.4) & (np.abs(q) <= media + 1.2) & ~dentro & lleno
            v[halo] -= 0.09
        f = np.clip(s_ / L, 0, 1)
        val = 0.67 - 0.11 * np.clip(1 - f * 1.5, 0, 1) + 0.07 * f + rnd.uniform(-0.02, 0.02)
        borde = (np.abs(q) > media - 0.9) | (s_ > L - 0.9)
        val = val - np.where(borde, 0.09, 0.0) + np.where((np.abs(q) < 0.5) & (f < 0.85), 0.035, 0.0)
        v[dentro] = val[dentro]
        lleno |= dentro
    grano = np.array([[rnd.random() for _ in range(W)] for _ in range(H)])
    v = np.maximum(v + 0.03 * (grano - 0.5), 0.5)      # sin agujeros oscuros junto al hueso
    img = np.zeros((H, W, 4))
    img[..., :3] = _de_rampa(RAMPAS['pluma'], v)
    img[..., 3] = np.where(lleno, 255, 0)
    _SPRITES[rota] = img
    return img


def ala(m, padre, s, nombre, pivote, rot, rota=False):
    """Un ala entera (s = 1 izquierda, +X; s = -1 derecha, en espejo): el plano
    con las plumas pintadas (recortado), y en relieve el hueso y las dos filas
    de coberteras de arriba, que le dan el canto redondo."""
    S = np.diag([-1.0, 1.0, 1.0])

    def esp(R):
        return R if s > 0 else S @ R @ S

    def caja(c):
        return espejo_caja(c) if s < 0 else c

    m.parte(nombre, padre, pivote, (rot[0], rot[1] * s, rot[2] * s))
    z0, y0, W, H = marco_ala(rota)
    m.cajas(nombre, (-0.5, y0, z0, 1.0, H, W, 'ala_rota_plano' if rota else 'ala_plano'))   # grueso entero: el sprite cae justo en los texeles
    r = random.Random(31)
    for i in range(len(HUESO_ALA) - 1):
        if rota and i > 1:
            break
        (za, ya), (zb, yb) = HUESO_ALA[i], HUESO_ALA[i + 1]
        L = math.hypot(zb - za, yb - ya)
        a = math.degrees(math.atan2(zb - za, yb - ya))
        g = 4.0 - 0.3 * i
        m.parte(f'{nombre}_hueso{i}', nombre, (0, ya, za), (a, 0, 0),
                [caja((-g / 2, -0.9, -1.7, g, L + 1.8, 3.4, 'pluma_cob')),
                 caja((-g / 2 - 0.15, -1.9, -2.0, g + 0.3, 3.8, 4.0, 'pluma_cob'))])   # la articulacion, sin rendijas
    for (etiqueta, cuantas, t0, t1, largo, caida, ancho, grueso, xo, mat, dos) in FILAS_ALA:
        if etiqueta not in ('menor', 'marginal'):
            continue
        for k in range(cuantas):
            t = t0 + (t1 - t0) * k / (cuantas - 1)
            if rota and t > 0.32:
                continue
            z, y = _sobre_hueso(t)
            Rl = rot3(caida(t), 0, 0) @ rot3(0, 8 + r.uniform(-3, 3), 0)
            # por fuera del hueso (que mide hasta 2 de medio grueso): asi no lo atraviesan
            x = (2.2 if etiqueta == 'menor' else 2.6) + (k % 2) * 0.2 - 0.1
            cajas = [caja((x - grueso / 2, -0.6, -ancho / 2, grueso, largo(t), ancho, mat)),
                     caja((-x - grueso / 2, -0.6, -ancho / 2, grueso, largo(t), ancho, mat))]
            m.parte_r(f'{nombre}_{etiqueta}{k}', nombre, (0.0, y + 0.7, z + 0.5), esp(Rl), cajas)


def estatua(rota=False):
    m = Modelo('estatua_rota' if rota else 'estatua')
    m.parte('estatua')
    pedestal(m, 'estatua')
    if rota:
        ruinas_estatua(m)
        return m
    pies(m, 'estatua')
    ropa(m, 'estatua')
    torso(m, 'estatua')
    cabeza(m)
    melena(m)
    boca, d = trompeta(m)
    brazos(m, boca, d)
    for s, n in ((1, 'izq'), (-1, 'der')):
        ala(m, 'torso', s, 'ala_' + n, (5.0 * s, -12.5, 4.4), (-4, 42, 12))
    return m


def ruinas_estatua(m):
    """La estatua rota: quedan los pies y el bajo de la falda, quebrado; un
    munon de ala caido apoyado en ella, la trompeta en el suelo y cascotes."""
    pies(m, 'estatua')
    ropa(m, 'estatua', rota=True)
    # el relleno de la rotura: marmol partido dentro de la falda
    m.parte('rotura', 'estatua', (0, 0, 0), cajas=[
        (-8.5, -7.0, -5.5, 17.0, 13.0, 12.0, 'cascote'),
        (-6.5, -10.5, -4.0, 8.0, 4.0, 9.0, 'cascote'),
        (1.5, -9.0, -3.0, 6.0, 2.5, 7.0, 'cascote'),
        (-7.5, -13.5, 1.5, 6.0, 7.0, 6.0, 'cascote'),
    ])
    # el munon del ala: su raiz partida, caida y apoyada contra la falda
    ala(m, 'estatua', 1, 'ala_rota', (9.5, 3.4, 4.0), (0, 18, 84), rota=True)
    # la trompeta, tirada sobre el plinto (la luz apagada)
    m.parte('trompeta_caida', 'estatua', (-8.0, 4.5, -10.5), (90, 0, -24), [
        (-0.7, 0.0, -0.7, 1.4, 21.0, 1.4, 'oro'),
        (-1.25, 6.0, -1.25, 2.5, 1.4, 2.5, 'oro')])
    campana(m, 'trompeta_caida', 21.0, oro='oro_mate', luz=False, nombre='campana_caida')
    # cascotes por el plinto
    r = random.Random(17)
    for i, (x, z, tam) in enumerate(((10.0, -9.0, 4.5), (-11.0, 4.0, 3.5), (6.0, -12.0, 2.5), (-4.0, 10.5, 3.0),
                                     (12.0, 9.0, 2.8), (-12.0, -11.5, 2.2), (0.5, -12.6, 2.0))):
        m.parte(f'cascote_{i}', 'estatua', (x, PIE_Y - tam * 0.45, z),
                (r.uniform(-25, 25), r.uniform(0, 90), r.uniform(-25, 25)),
                [(-tam / 2, -tam / 2, -tam * 0.4, tam, tam * 0.9, tam * 0.8, 'cascote')])
    m.parte('cabeza_caida', 'estatua', (-8.5, PIE_Y - 3.8, 9.0), (8, 40, 72), [_k(c) for c in [
        (-4.1, -4.2, -4.6, 8.2, 8.3, 9.0, 'cascote'),
        (-4.5, -5.1, -3.9, 9.0, 2.3, 9.1, 'pelo')]])
    for n in [n for n in m.orden if m.partes[n].padre == 'estatua' and
              (n.startswith('cascote') or n in ('trompeta_caida', 'cabeza_caida', 'ala_rota'))]:
        apoyar(m, n, PIE_Y + 0.3)


# ======================================================================
#  LA FUENTE SOLAR
# ======================================================================
# El centro del sol que flota encima de la cuna (lo pinta el renderer).
SOL_FUENTE_Y = -55.0


def fuente(rota=False):
    m = Modelo('fuente_rota' if rota else 'fuente')
    m.parte('fuente')
    m.parte('base', 'fuente', (0, 0, 0), cajas=[
        (-12, 20.5, -12, 24, 3.5, 24, 'ped'),
        (-11.4, 19.5, -11.4, 22.8, 1.0, 22.8, 'oro'),
        (-10.2, 16.8, -10.2, 20.4, 2.7, 20.4, 'ped'),
        (-9.0, 15.8, -9.0, 18.0, 1.0, 18.0, 'oro'),
    ])
    # el fuste: cuatro tramos que adelgazan, separados por bandas de sol
    tramos = [(15.8, -1.0, 6.0), (-3.4, -18.6, 5.4), (-21.0, -34.6, 4.8), (-37.0, -43.0, 4.2)]
    bandas = [(-1.0, -3.4, 6.3), (-18.6, -21.0, 5.7), (-34.6, -37.0, 5.1)]
    if rota:
        tramos, bandas = tramos[:1], []
    for i, (y1, y0, r) in enumerate(tramos):
        h = y1 - y0
        cajas = [(-r, y0, -r, 2 * r, h, 2 * r, 'marmol' if i else 'ped_panel')]
        for sx in (-1, 1):            # aristas de oro
            for sz in (-1, 1):
                cajas.append((sx * r - 0.45, y0, sz * r - 0.45, 0.9, h, 0.9, 'oro'))
        if rota:   # el tramo quebrado: arriba irregular
            cajas = [(-r, y0 + 9, -r, 2 * r, h - 9, 2 * r, 'ped_panel'),
                     (-r, y0 + 4, -r, r * 1.1, 5.2, 2 * r, 'cascote'),
                     (-r * 0.2, y0 + 6.5, -r, r * 1.2, 2.7, r * 1.3, 'cascote'),
                     (-r, y0 + 2.2, -r * 0.1, r, 2.2, r * 1.1, 'cascote')]
            for sx in (-1, 1):
                for sz in (-1, 1):
                    cajas.append((sx * r - 0.45, y0 + 9 - (sx + sz + 2) * 1.6, sz * r - 0.45, 0.9,
                                  h - 9 + (sx + sz + 2) * 1.6, 0.9, 'oro'))
        m.parte(f'tramo{i}', 'fuente', (0, 0, 0), cajas=cajas)
    for i, (y1, y0, r) in enumerate(bandas):
        m.parte(f'banda{i}', 'fuente', (0, 0, 0), cajas=[
            (-r, y0, -r, 2 * r, y1 - y0, 2 * r, 'banda_sol'),
            (-r - 0.35, y0 - 0.5, -r - 0.35, 2 * r + 0.7, 0.7, 2 * r + 0.7, 'oro'),
            (-r - 0.35, y1 - 0.2, -r - 0.35, 2 * r + 0.7, 0.7, 2 * r + 0.7, 'oro'),
        ])
    if not rota:
        # un disco de sol en cada cara del segundo tramo
        for k in range(4):
            R = rot3(0, k * 90.0, 0)
            c = R @ np.array([0, -11.0, -5.4])
            m.parte_en(f'disco{k}', 'fuente', c, R, [(-2.0, -2.0, -0.5, 4.0, 4.0, 0.6, 'disco_sol')])
            m.parte_en(f'disco_r{k}', 'fuente', c, R @ rot3(0, 0, 45), [(-1.7, -1.7, -0.35, 3.4, 3.4, 0.4, 'oro')])
        cuna(m, 'fuente', (0, -43.0, 0))
    else:
        # la cuna, caida y rajada, apoyada contra el munon
        m.parte('cuna_caida', 'fuente', (13.0, 19.0, -6.0), (24, 30, 78))
        cuna(m, 'cuna_caida', (0, 0, 0), rota=True)
        r = random.Random(23)
        # trozos del fuste por el suelo
        m.parte('trozo0', 'fuente', (-13.0, 21.0, 8.0), (4, 35, 88), [
            (-5.4, -8.0, -5.4, 10.8, 15.0, 10.8, 'marmol'),
            (-5.85, -6.6, -5.85, 11.7, 2.4, 11.7, 'banda_rota'),
            (-5.4, 7.0, -5.4, 10.8, 2.2, 10.8, 'cascote')])
        for i, (x, z, tam) in enumerate(((-8.0, -13.0, 4.0), (9.5, 12.0, 3.4), (15.0, 4.0, 2.6), (-15.0, -4.0, 2.4),
                                         (3.0, -14.5, 2.2), (-3.0, 14.0, 3.0))):
            m.parte(f'cascote_{i}', 'fuente', (x, 24 - tam * 0.4, z),
                    (r.uniform(-25, 25), r.uniform(0, 90), r.uniform(-25, 25)),
                    [(-tam / 2, -tam / 2, -tam * 0.4, tam, tam * 0.9, tam * 0.8, 'cascote')])
        for n in [n for n in m.orden if m.partes[n].padre == 'fuente' and
                  (n.startswith('cascote') or n in ('trozo0', 'cuna_caida'))]:
            apoyar(m, n, 24.3)
    return m


def cuna(m, padre, pos, rota=False):
    """La cuna de oro: un cuello abocinado, el cuenco (su fondo lo enciende el
    sol) y ocho brazos que se abren y luego suben, rematados en una bola; el
    sol flota dentro de la corona que hacen, sobre el cuenco."""
    oro = 'oro_mate' if rota else 'oro'
    m.parte('cuna', padre, pos, cajas=[
        (-4.6, -1.6, -4.6, 9.2, 1.6, 9.2, oro),
        (-6.2, -3.2, -6.2, 12.4, 1.6, 12.4, oro),
        (-5.2, -4.4, -5.2, 10.4, 1.3, 10.4, 'brasa' if rota else 'cuenco'),
    ])
    m.parte('cuna_b', 'cuna', (0, 0, 0), (0, 45, 0), [(-5.4, -3.0, -5.4, 10.8, 1.4, 10.8, oro)])
    for k in range(8):
        if rota and k in (2, 5):
            continue       # dos brazos rotos
        R = rot3(0, k * 45.0, 0)
        b = m.parte_en(f'cuna_brazo{k}', 'cuna', m.a_mundo('cuna', R @ np.array([0, -3.4, -5.4])),
                       m.mundo('cuna')[:3, :3] @ R @ rot3(38, 0, 0), [(-0.8, -6.6, -0.8, 1.6, 7.1, 1.6, oro)])
        largo = 2.5 if rota and k % 3 == 0 else 5.2
        c = m.parte(f'cuna_punta{k}', b, (0, -6.4, 0), (-30, 0, 0), [(-0.7, -largo, -0.7, 1.4, largo + 0.4, 1.4, oro)])
        if not (rota and k % 3 == 0):
            m.cajas(c, (-1.1, -largo - 2.0, -1.1, 2.2, 2.2, 2.2, oro))


# ======================================================================
#  Materiales: cada caja se pinta con el suyo, cara a cara
# ======================================================================
def _hex(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], float)


def _rampa(*hs):
    return np.array([_hex(h) for h in hs])


RAMPAS = {
    'tela': _rampa('8f8678', 'ada393', 'c8bfaf', 'dcd5c7', 'ebe6dc', 'f7f4ee'),
    'piel': _rampa('a79e90', 'c5bdaf', 'dcd5c8', 'ebe5da', 'f5f1e9', 'fdfbf6'),
    'rostro': _rampa('a79e90', 'c5bdaf', 'dcd5c8', 'ebe5da', 'f5f1e9', 'fdfbf6'),
    'pelo': _rampa('857b6d', 'a2988a', 'bcb3a4', 'd2cabc', 'e4ddd1', 'f0ebe2'),
    'pluma': _rampa('968c7e', 'b2a99a', 'cbc3b5', 'ddd7cb', 'ece8df', 'f8f5ef'),
    'pluma_cob': _rampa('968c7e', 'b2a99a', 'cbc3b5', 'ddd7cb', 'ece8df', 'f8f5ef'),
    'marmol': _rampa('8f8678', 'ada393', 'c8bfaf', 'dcd5c7', 'ebe6dc', 'f7f4ee'),
    'ped': _rampa('6f685e', '8a8275', 'a39b8d', 'bab2a4', 'cdc6b9', 'ddd7cc'),
    'ped_panel': _rampa('6f685e', '8a8275', 'a39b8d', 'bab2a4', 'cdc6b9', 'ddd7cc'),
    'cascote': _rampa('5e584f', '777065', '8f887c', 'a59e91', 'b9b2a5', 'c9c3b7'),
    'oro': _rampa('5c3a0e', '8a5a16', 'b67e22', 'd9a236', 'f0c860', 'fde7a0'),
    'oro_mate': _rampa('3e2a12', '5e4118', '7d5a20', '9a742e', 'b28d44', 'c7a660'),
    'campana': _rampa('5c3a0e', '8a5a16', 'b67e22', 'd9a236', 'f0c860', 'fde7a0'),
    'cuenco': _rampa('5c3a0e', '8a5a16', 'b67e22', 'd9a236', 'f0c860', 'fde7a0'),
}
# lo que brilla (capa emisiva): color del centro y del borde, y opacidad
LUZ = {
    'oro_luz': ('fffbe8', 'ffb43c', 255, 210),
    'banda_sol': ('fffbe0', 'ffb02a', 255, 235),
    'disco_sol': ('fffdf0', 'ffa020', 255, 220),
    'brasa': ('ffb060', 'a02808', 120, 40),
}
EMISIVOS = set(LUZ)


def _ruido_suave(fw, fh, rnd, paso=4.0):
    gw, gh = int(fw / paso) + 2, int(fh / paso) + 2
    g = np.array([[rnd.random() for _ in range(gw)] for _ in range(gh)])
    ys, xs = np.arange(fh) / paso, np.arange(fw) / paso
    y0, x0 = ys.astype(int), xs.astype(int)
    fy, fx = (ys - y0)[:, None], (xs - x0)[None, :]
    a = g[y0][:, x0]
    b = g[y0][:, x0 + 1]
    c = g[y0 + 1][:, x0]
    d = g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def _de_rampa(rampa, v):
    v = np.clip(v, 0, 1) * (len(rampa) - 1)
    i = np.clip(v.astype(int), 0, len(rampa) - 2)
    f = (v - i)[..., None]
    return rampa[i] * (1 - f) + rampa[i + 1] * f


def _vetas(img, rnd, n, color, k=0.35):
    """Vetas finas que serpentean (el marmol)."""
    fh, fw = img.shape[:2]
    for _ in range(n):
        x, y = rnd.uniform(0, fw), rnd.uniform(0, fh)
        a = rnd.uniform(0, math.tau)
        for _ in range(rnd.randint(4, 12)):
            xi, yi = int(x), int(y)
            if 0 <= xi < fw and 0 <= yi < fh:
                img[yi, xi, :3] = img[yi, xi, :3] * (1 - k) + color * k
            a += rnd.uniform(-0.6, 0.6)
            x += math.cos(a)
            y += math.sin(a)


def pintar_cara(mat, cara, fw, fh, rnd, caja):
    """Devuelve (color, brillo) de una cara: arrays (fh, fw, 4) uint8."""
    if mat in ('ala_plano', 'ala_rota_plano'):
        img = np.zeros((fh, fw, 4))
        if cara in ('este', 'oeste'):
            spr = sprite_ala(mat == 'ala_rota_plano')
            assert spr.shape[:2] == (fh, fw), (spr.shape, fh, fw)
            img = spr if cara == 'este' else spr[:, ::-1]
        return np.clip(img, 0, 255).astype(np.uint8), None
    rampa = RAMPAS.get(mat, RAMPAS['oro'])
    img = np.zeros((fh, fw, 4))
    img[..., 3] = 255
    brillo = None
    yy, xx = np.mgrid[0:fh, 0:fw]
    if mat in EMISIVOS:
        c1, c2, a1, a2 = LUZ[mat]
        cx, cy = (fw - 1) / 2, (fh - 1) / 2
        dd = np.maximum(np.abs(xx - cx) / max(1, fw / 2), np.abs(yy - cy) / max(1, fh / 2))
        dd = np.clip(dd, 0, 1)[..., None]
        col = _hex(c1) * (1 - dd) + _hex(c2) * dd
        if mat == 'banda_sol':
            # puntos de sol a lo largo de la banda
            punto = ((xx % 4) == 1)[..., None]
            col = np.where(punto, _hex('fffff4'), col * 0.92)
        if mat == 'disco_sol':
            r = np.hypot(xx - cx, yy - cy) / max(1, min(fw, fh) / 2)
            col = np.where((r > 0.55)[..., None] & (r < 0.85)[..., None], _hex('ffd060'), col)
        if mat == 'brasa':
            base = _de_rampa(RAMPAS['oro_mate'], 0.2 + 0.3 * _ruido_suave(fw, fh, rnd, 2.0))
            img[..., :3] = base
            br = np.zeros((fh, fw, 4))
            m = np.array([[rnd.random() < 0.25 for _ in range(fw)] for _ in range(fh)])
            br[..., :3] = col
            br[..., 3] = np.where(m, a1, 0)
            img[..., :3] = np.where(m[..., None], col * 0.7, img[..., :3])
            return img.astype(np.uint8), br.astype(np.uint8)
        img[..., :3] = col
        brillo = np.zeros((fh, fw, 4))
        brillo[..., :3] = col
        brillo[..., 3] = a1 * (1 - dd[..., 0]) + a2 * dd[..., 0]
        return img.astype(np.uint8), brillo.astype(np.uint8)

    oro = mat in ('oro', 'oro_mate', 'campana', 'cuenco')
    # valor base: ruido suave + grano
    grano = np.array([[rnd.random() for _ in range(fw)] for _ in range(fh)])
    if oro:
        v = 0.62 + 0.10 * (_ruido_suave(fw, fh, rnd, 2.0) - 0.5) + 0.10 * (grano - 0.5)
    elif mat == 'cascote':
        v = 0.55 + 0.22 * (_ruido_suave(fw, fh, rnd, 2.0) - 0.5) + 0.22 * (grano - 0.5)
    elif mat in ('piel', 'rostro'):
        v = 0.66 + 0.06 * (_ruido_suave(fw, fh, rnd, 5.0) - 0.5) + 0.03 * (grano - 0.5)
    else:
        v = 0.64 + 0.10 * (_ruido_suave(fw, fh, rnd, 4.0) - 0.5) + 0.05 * (grano - 0.5)

    lateral = cara in ('frente', 'espalda', 'oeste', 'este')
    # sombra horneada: arriba mas claro, abajo mas oscuro; la cara de abajo, oscura
    if lateral and fh > 2:
        v = v + 0.06 - 0.16 * (yy / max(1, fh - 1)) * min(1.0, fh / 10.0)
    elif cara == 'arriba':
        v = v + 0.07
    elif cara == 'abajo':
        v = v - (0.06 if mat in ('piel', 'rostro') else 0.16)

    if mat in ('tela', 'piel', 'pelo', 'marmol') and lateral and fw >= 3:
        # la caja se redondea: los bordes, en sombra (el fondo del pliegue, el
        # costado del brazo); asi un prisma se lee como un cilindro
        q = np.abs(2 * xx / max(1, fw - 1) - 1)
        k = 0.15 if mat == 'tela' else 0.10
        v = v - k * q ** 1.6 + k * 0.25
    if mat in ('pelo',) and fw >= 3:
        # surcos del pelo a lo largo de la caja
        fase = rnd.random() * 6
        if lateral:
            v = v + 0.05 * np.sin(xx * 1.6 + yy * 0.3 + fase)
        else:
            v = v + 0.05 * np.sin(xx * 1.6 + fase)
    if mat in ('pluma', 'pluma_cob') and lateral:
        cx = (fw - 1) / 2
        dx = np.abs(xx - cx)
        if fw >= 3:
            # la raiz en sombra (la tapa la fila de encima), la punta clara, el
            # raquis apenas marcado y el borde en sombra: asi las filas se escalonan
            f = yy / max(1, fh - 1)
            v = v + np.where(dx < 0.6, 0.035, 0.0)
            v = v - 0.20 * np.clip(1 - f * 1.5, 0, 1) + 0.07 * f
            v = v - np.where(dx >= cx - 0.1, 0.08, 0.0)
    if mat == 'ped_panel' and lateral and fw >= 12 and fh >= 8:
        # panel rehundido: un marco fino oscuro con luz debajo
        m1 = ((xx == 2) | (xx == fw - 3)) & (yy >= 2) & (yy <= fh - 3)
        m2 = ((yy == 2) | (yy == fh - 3)) & (xx >= 2) & (xx <= fw - 3)
        v = v - np.where(m1 | m2, 0.10, 0.0)
        m3 = ((xx == 3) & (yy >= 3) & (yy <= fh - 4)) | ((yy == 3) & (xx >= 3) & (xx <= fw - 4))
        v = v + np.where(m3, 0.05, 0.0)
    if oro:
        if lateral and fh >= 2:
            v = v + np.where(yy == 0, 0.12, 0.0)
        v = v + np.where(grano > 0.93, 0.14, 0.0)
    if mat == 'rostro' and cara == 'frente':
        v = _cara(v, fw, fh, caja)

    img[..., :3] = _de_rampa(rampa, v)
    if mat in ('tela', 'marmol', 'ped', 'ped_panel', 'pluma', 'pluma_cob'):
        n = int(fw * fh / 90 + rnd.random() * 1.2)
        _vetas(img, rnd, n, rampa[1], 0.24)
    if mat == 'cascote':
        _vetas(img, rnd, int(fw * fh / 30) + 1, rampa[0], 0.6)
    if mat == 'campana':
        # la luz de la campana: por dentro (la cara +Z de cada duela mira al
        # eje) sube hacia la boca; por fuera, apenas un reflejo en el borde
        brillo = np.zeros((fh, fw, 4))
        brillo[..., :3] = _hex('ffd070')
        f = np.clip(yy / max(1, fh - 1), 0, 1)
        if cara == 'espalda':
            brillo[..., 3] = 90 + 150 * f
            img[..., :3] = img[..., :3] * 0.5 + _hex('ffe6a0') * 0.5
        elif lateral:
            brillo[..., 3] = 55 * f ** 2
    if mat == 'cuenco' and cara == 'arriba':
        # el fondo de la cuna, encendido por el sol de encima
        brillo = np.zeros((fh, fw, 4))
        cx, cy = (fw - 1) / 2, (fh - 1) / 2
        r = np.clip(np.hypot(xx - cx, yy - cy) / max(1, fw / 2), 0, 1)
        brillo[..., :3] = _hex('ffe6a0')
        brillo[..., 3] = 200 * (1 - r)
    if mat in ('pluma', 'pluma_cob'):
        _punta_pluma(img, cara, fw, fh)
    return np.clip(img, 0, 255).astype(np.uint8), None if brillo is None else np.clip(brillo, 0, 255).astype(np.uint8)


OJO_Y = -5.6


def _cara(v, fw, fh, caja):
    """Rasgos tallados en la cara frontal de la cabeza: ojos cerrados (serena,
    tocando), cejas suaves y las mejillas redondeadas."""
    y0 = caja[1]
    fila_ojo = int(round(OJO_Y - y0))
    cx = (fw - 1) / 2
    for x in range(fw):
        dx = abs(x - cx)
        if dx > cx - 0.6:
            v[:, x] -= 0.07                 # los lados de la cara, en sombra
        if 1.0 <= dx <= 2.9:
            if 0 <= fila_ojo < fh:
                v[fila_ojo, x] -= 0.13      # el parpado cerrado
            if 0 <= fila_ojo - 1 < fh:
                v[fila_ojo - 1, x] -= 0.04  # la cuenca, en sombra suave
            if 0 <= fila_ojo - 2 < fh:
                v[fila_ojo - 2, x] -= 0.05  # la ceja
            if 0 <= fila_ojo + 1 < fh:
                v[fila_ojo + 1, x] += 0.04  # el pomulo
    return v


def _punta_pluma(img, cara, fw, fh):
    """Las plumas acaban en punta redondeada: se recorta la textura (cutout)."""
    if cara == 'abajo':
        img[..., 3] = 0
        return
    if cara == 'arriba':
        return
    cx = (fw - 1) / 2
    punta = min(max(2.0, fw * 1.1), fh * 0.4)
    for y in range(fh):
        r = fh - 1 - y                 # filas desde la punta
        if r >= punta:
            continue
        f = (r + 0.5) / punta
        media = (cx + 0.5) * math.sqrt(f)
        for x in range(fw):
            if abs(x - cx) > media:
                img[y, x, 3] = 0
        if fw <= 2 and r < punta * 0.5:
            img[y, :, 3] = 0


# ======================================================================
#  Atlas
# ======================================================================
ANCHO_ATLAS = 256


def clave(c):
    return (round(c[3], 3), round(c[4], 3), round(c[5], 3), c[6])


def tam_uv(k):
    w, h, d, _ = k
    return int(math.ceil(2 * (d + w))) + 1, int(math.ceil(d + h)) + 1


def empaquetar(modelos):
    claves = {}
    for mod in modelos:
        for n in mod.orden:
            for c in mod.partes[n].cajas:
                claves.setdefault(clave(c), c)
    orden = sorted(claves, key=lambda k: (-tam_uv(k)[1], -tam_uv(k)[0], k[3]))
    uv = {}
    # estanterias: cada caja en la primera fila donde quepa
    filas = []    # [y, alto, x]
    for k in orden:
        w, h = tam_uv(k)
        for f in filas:
            if f[2] + w <= ANCHO_ATLAS and h <= f[1]:
                uv[k] = (f[2], f[0])
                f[2] += w
                break
        else:
            y = filas[-1][0] + filas[-1][1] if filas else 0
            filas.append([y, h, w])
            uv[k] = (0, y)
    alto = filas[-1][0] + filas[-1][1]
    return uv, 1 << (alto - 1).bit_length()


def caras_uv(u, v, w, h, d):
    return {
        'arriba': (u + d, v, w, d),
        'abajo': (u + d + w, v, w, d),
        'oeste': (u, v + d, d, h),
        'frente': (u + d, v + d, w, h),
        'este': (u + d + w, v + d, d, h),
        'espalda': (u + 2 * d + w, v + d, w, h),
    }


def pintar_atlas(uv, alto, semilla=11):
    base = np.zeros((alto, ANCHO_ATLAS, 4), np.uint8)
    brillo = np.zeros_like(base)
    rnd = random.Random(semilla)
    for k, (u, v) in sorted(uv.items(), key=lambda kv: (kv[1][1], kv[1][0])):
        w, h, d, mat = k
        caja = _CAJA_DE.get(k, (0, 0, 0, w, h, d, mat))
        for cara, (fx, fy, fw, fh) in caras_uv(u, v, w, h, d).items():
            x0, y0 = int(math.floor(fx + 1e-6)), int(math.floor(fy + 1e-6))
            x1, y1 = int(math.ceil(fx + fw - 1e-6)), int(math.ceil(fy + fh - 1e-6))
            if x1 <= x0 or y1 <= y0:
                continue
            col, br = pintar_cara(mat, cara, x1 - x0, y1 - y0, rnd, caja)
            base[y0:y1, x0:x1] = col
            if br is not None:
                brillo[y0:y1, x0:x1] = br
    return base, brillo


_CAJA_DE = {}


def registrar_cajas(modelos):
    for mod in modelos:
        for n in mod.orden:
            for c in mod.partes[n].cajas:
                _CAJA_DE.setdefault(clave(c), c)


# ======================================================================
#  Java
# ======================================================================
def f(x):
    s = ('%.4f' % x).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s + 'F'


def _var(n):
    return 'p_' + n


def _cubos(p, uv):
    cub = 'CubeListBuilder.create()'
    for c in p.cajas:
        u, v = uv[clave(c)]
        cub += (f'\n                .texOffs({u}, {v}).addBox({f(c[0])}, {f(c[1])}, {f(c[2])}, '
                f'{f(c[3])}, {f(c[4])}, {f(c[5])}, infla)')
    return cub


def _java_parte(mod, n, uv, L, ramas, metodo):
    p = mod.partes[n]
    padre = _var(p.padre) if p.padre else 'p_root'
    rx, ry, rz = [r * D2R for r in p.rot]
    pose = (f'PartPose.offsetAndRotation({f(p.pivote[0])}, {f(p.pivote[1])}, {f(p.pivote[2])}, '
            f'{f(rx)}, {f(ry)}, {f(rz)})')
    decl = f'PartDefinition {_var(n)} = ' if p.hijos else ''
    L.append(f'        {decl}{padre}.addOrReplaceChild("{n}", {_cubos(p, uv)},\n                {pose});')
    for h in p.hijos:
        if h in ramas:
            L.append(f'        {metodo}_{h}({_var(n)}, infla);')
        else:
            _java_parte(mod, h, uv, L, ramas, metodo)


def java_malla(clase, comentario, variantes, uv, alto):
    """variantes: [(metodo publico, nombre privado, modelo, ramas)] -- cada rama
    va en su propio metodo (por el limite de 64 KB de bytecode por metodo)."""
    L = ['package com.atalaya.client;', '',
         'import net.minecraft.client.model.geom.PartPose;',
         'import net.minecraft.client.model.geom.builders.CubeDeformation;',
         'import net.minecraft.client.model.geom.builders.CubeListBuilder;',
         'import net.minecraft.client.model.geom.builders.LayerDefinition;',
         'import net.minecraft.client.model.geom.builders.MeshDefinition;',
         'import net.minecraft.client.model.geom.builders.PartDefinition;', '', '/**']
    L += [' * ' + x if x else ' *' for x in comentario]
    L += [' */', f'public final class {clase} {{', '', f'    private {clase}() {{', '    }']
    for publico, privado, mod, ramas in variantes:
        L += ['', f'    public static LayerDefinition {publico}() {{',
              f'        return {privado}(CubeDeformation.NONE);', '    }', '',
              f'    private static LayerDefinition {privado}(CubeDeformation infla) {{',
              '        MeshDefinition malla = new MeshDefinition();',
              '        PartDefinition p_root = malla.getRoot();']
        for n in mod.orden:
            if mod.partes[n].padre is None:
                _java_parte(mod, n, uv, L, ramas, privado)
        L += [f'        return LayerDefinition.create(malla, {ANCHO_ATLAS}, {alto});', '    }']
        for r in ramas:
            p = mod.partes[r]
            L += ['', f'    private static void {privado}_{r}(PartDefinition {_var(p.padre)}, CubeDeformation infla) {{']
            _java_parte(mod, r, uv, L, ramas, privado)
            L += ['    }']
    L.append('}')
    return '\n'.join(L) + '\n'


# ======================================================================
#  Render de comprobacion
# ======================================================================
def quads(mod, uv, alto, M, ocultar=()):
    Ms = mod.matrices()
    out = []
    for n in mod.orden:
        if any(n.startswith(o) for o in ocultar):
            continue
        Mn = M @ Ms[n]
        for c in mod.partes[n].cajas:
            u, v = uv[clave(c)]
            for pts, uvs in vr.caja_quads((u, v), c[:6], False, ANCHO_ATLAS, alto):
                w = [(Mn @ np.array([*q, 1.0]))[:3] for q in pts]
                out.append((w, uvs, n))
    return out


def dibujar(lz, cam, qs, tex, emis, luces, amb, niebla=None, brillo=1.0):
    for P, UV, _ in qs:
        n = vr.normal(P)
        luz = vr.iluminar(n, cam, np.mean(P, axis=0), luces, amb)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla, brillo=brillo)


def a_mundo(x, z, guinada, escala=ESCALA, y=0.0):
    """Como el renderer de una entidad: px/16, Y invertida, base (y=24) en el suelo."""
    return T(x, y, z) @ Ry(guinada * D2R) @ vr.S(escala) @ T(0, 1.5, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])


# ======================================================================
#  Principal
# ======================================================================
def generar(raiz):
    tex_dir = os.path.join(raiz, 'src/main/resources/assets/atalaya/textures/entity/novilis')
    java_dir = os.path.join(raiz, 'src/client/java/com/atalaya/client')
    os.makedirs(tex_dir, exist_ok=True)
    out = {}
    for nombre, hacer, clase, ramas, coment in (
            ('estatua', estatua, 'EstatuaNovilisMalla',
             (['pedestal', 'falda', 'ala_izq', 'ala_der', 'cabeza'], ['pedestal', 'falda', 'ala_rota']),
             ['Las estatuas de angel de Novilis (Trompetas del Apocalipsis). GENERADO por',
              'materiales/generadores/novilis_props.py: no se edita a mano.', '',
              'Escala x1 (un texel por pixel), la base en y = 24: mide 120 px = 7,5 bloques.',
              'Textura: textures/entity/novilis/estatua.png (y estatua_brillo.png, la luz de',
              'la campana de la trompeta). La entera y la rota comparten el atlas.']),
            ('fuente', fuente, 'FuenteSolarMalla',
             ([], []),
             ['Las fuentes solares de Novilis. GENERADO por materiales/generadores/novilis_props.py:',
              'no se edita a mano.', '',
              f'Escala x1, la base en y = 24: mide 80 px = 5 bloques. El sol flota con su centro en',
              f'y = {SOL_FUENTE_Y:g} (lo pinta el renderer aparte). Textura: textures/entity/novilis/',
              'fuente.png y fuente_brillo.png (las bandas de sol). La entera y la rota comparten el atlas.'])):
        entera, rota = hacer(False), hacer(True)
        registrar_cajas([entera, rota])
        uv, alto = empaquetar([entera, rota])
        base, brillo = pintar_atlas(uv, alto)
        Image.fromarray(base).save(os.path.join(tex_dir, nombre + '.png'))
        Image.fromarray(brillo).save(os.path.join(tex_dir, nombre + '_brillo.png'))
        java = java_malla(clase, coment, [('crear', 'entera', entera, ramas[0]), ('crearRota', 'rota', rota, ramas[1])],
                          uv, alto)
        with open(os.path.join(java_dir, clase + '.java'), 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(java)
        piezas = len(entera.orden), len(rota.orden)
        cajas = sum(len(entera.partes[n].cajas) for n in entera.orden), sum(len(rota.partes[n].cajas) for n in rota.orden)
        print(f'{nombre}: atlas {ANCHO_ATLAS}x{alto}, piezas {piezas}, cajas {cajas}')
        out[nombre] = (entera, rota, uv, alto, base, brillo)
    return out


# ======================================================================
#  Renders de comprobacion y presentacion (con carpeta)
# ======================================================================
LUZ_ESTUDIO = [((-0.5, 0.75, -0.75), (1.0, 0.98, 0.95), 0.80, 'llave'),
               ((0.7, 0.25, -0.3), (0.75, 0.8, 0.9), 0.22, 'llave'),
               ((0.4, 0.4, 0.9), (1.0, 0.85, 0.7), 0.45, 'contra')]
AMB_ESTUDIO = (0.36, 0.35, 0.34)
# la presentacion: luz calida de atardecer, pero que deje ver el marmol crema
LUZ_ESCENA = [((-0.35, 1.0, -0.55), (1.0, 0.86, 0.64), 1.0, 'llave'),
              ((0.6, 0.35, 0.9), (1.0, 0.45, 0.18), 0.85, 'contra'),
              ((-0.8, 0.15, 0.4), (0.95, 0.4, 0.15), 0.4, 'contra')]
AMB_ESCENA = (0.38, 0.27, 0.23)
# el Altar del Sol al atardecer (las luces de fuego_escenas.py)
LUZ_ALTAR = [((-0.35, 1.0, -0.55), (1.0, 0.78, 0.5), 1.15, 'llave'),
             ((0.6, 0.35, 0.9), (1.0, 0.38, 0.14), 0.85, 'contra'),
             ((-0.8, 0.1, 0.4), (0.9, 0.3, 0.1), 0.45, 'contra')]
AMB_ALTAR = (0.3, 0.17, 0.14)
FUENTES = 'C:/Windows/Fonts/'


class Lienzo(vr.Lienzo):
    """Como el de vigia_render, pero lo opaco que tapa algo le borra el brillo
    (si no, la luz de una campana se veria a traves de la estatua de delante)."""

    def triangulo(self, cam, P_, UV, tex, luz_fn, emis_tex=None, niebla=None, aditivo=False, brillo=1.0,
                  envolver=False, translucido=0.0):
        if aditivo or translucido > 0:
            return super().triangulo(cam, P_, UV, tex, luz_fn, emis_tex, niebla, aditivo, brillo, envolver, translucido)
        s = [cam.proyectar(p) for p in P_]
        if min(q[2] for q in s) < 0.05:
            return
        xs, ys = [q[0] for q in s], [q[1] for q in s]
        x0, x1 = max(int(math.floor(min(xs))), 0), min(int(math.ceil(max(xs))), self.W - 1)
        y0, y1 = max(int(math.floor(min(ys))), 0), min(int(math.ceil(max(ys))), self.H - 1)
        if x0 > x1 or y0 > y1:
            return
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = s
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            return
        l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l3 = 1 - l1 - l2
        dentro = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not dentro.any():
            return
        z = 1 / (l1 / az + l2 / bz + l3 / cz)
        u = (l1 * UV[0][0] / az + l2 * UV[1][0] / bz + l3 * UV[2][0] / cz) * z
        v = (l1 * UV[0][1] / az + l2 * UV[1][1] / bz + l3 * UV[2][1] / cz) * z
        th, tw = tex.shape[:2]
        if envolver:
            tu, tv = np.floor(u * tw).astype(int) % tw, np.floor(v * th).astype(int) % th
        else:
            tu, tv = np.clip((u * tw).astype(int), 0, tw - 1), np.clip((v * th).astype(int), 0, th - 1)
        texel = tex[tv, tu]
        zb = self.z[y0:y1 + 1, x0:x1 + 1]
        m = dentro & (texel[..., 3] > 25) & (z < zb)
        if not m.any():
            return
        rgb = texel[..., :3] / 255.0 * luz_fn
        if niebla is not None:
            f = niebla(z)[..., None]
            rgb = rgb * (1 - f) + np.array(niebla.color) * f
        col = self.color[y0:y1 + 1, x0:x1 + 1]
        col[m] = rgb[m]
        self.alfa[y0:y1 + 1, x0:x1 + 1][m] = 1.0
        zb[m] = z[m]
        em = self.emis[y0:y1 + 1, x0:x1 + 1]
        em[m] = 0.0
        if emis_tex is not None:
            et = emis_tex[tv, tu]
            ea = et[..., 3] / 255.0
            me = m & (ea > 0.01)
            k = 1.0 if niebla is None else (1 - niebla(z))[..., None]
            em[me] = (et[..., :3] / 255.0 * ea[..., None] * brillo * k)[me]
            col[me] = np.maximum(col, et[..., :3] / 255.0 * k)[me]


class Niebla:
    color = (0.42, 0.16, 0.08)

    def __init__(self, ini=18.0, largo=60.0, tope=0.85):
        self.ini, self.largo, self.tope = ini, largo, tope

    def __call__(self, z):
        return np.clip((z - self.ini) / self.largo, 0, self.tope)


def estudio(lz, fondo=(0.86, 0.86, 0.87), emis=0.6):
    col = np.clip(lz.color + lz.emis * emis, 0, 1)
    a = lz.alfa[..., None]
    g = np.linspace(1.0, 0.82, lz.H)[:, None, None]
    return col * a + np.array(fondo) * g * (1 - a)


def a_img(arr, W, H):
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)


def rotulo(img, texto, x, y, tam=26, color=(40, 30, 24), fuente='Oswald-Bold.ttf', centro=False):
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype(FUENTES + fuente, tam)
    except OSError:
        f = ImageFont.load_default()
    if centro:
        x -= d.textlength(texto, font=f) / 2
    d.text((x, y), texto, font=f, fill=color)


def dibujar_prop(lz, cam, hecho, cual, rota, x, z, guinada, luces, amb, niebla=None, brillo=1.0, ocultar=()):
    entera, rotam, uv, alto, base, br = hecho[cual]
    M = a_mundo(x, z, guinada)
    dibujar(lz, cam, quads(rotam if rota else entera, uv, alto, M, ocultar), base, br, luces, amb, niebla, brillo)
    return M


# --- el jugador de escala (1,8 bloques), con losetas de color liso ---
def _liso(c1, c2, semilla):
    r = random.Random(semilla)
    a, b = _hex(c1), _hex(c2)
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            t[y, x] = (*(a if r.random() < 0.7 else b).astype(int), 255)
    return t


MAT_JUGADOR = {'j_piel': _liso('c9956c', 'b8845e', 40), 'j_pelo': _liso('3b2a1e', '2c1f16', 41),
               'j_camisa': _liso('2f8f8a', '27807b', 42), 'j_pantalon': _liso('3a3f7a', '30356a', 43),
               'j_bota': _liso('4a4a4a', '3a3a3a', 44)}


def jugador(lz, cam, x, z, guinada, luces, amb, niebla=None, brazo=0.0):
    """Un jugador de vanilla (32 px = 2 bloques con la cabeza; 1,8 de alto)."""
    cajas = [((-4, 0, -2, 8, 12, 4), 'j_camisa', (0, 0, 0), 0),
             ((-4, -8, -4, 8, 8, 8), 'j_piel', (0, 0, 0), 0), ((-4.2, -8.2, -4.2, 8.4, 3, 8.4), 'j_pelo', (0, 0, 0), 0),
             ((-2, -2, -2, 4, 12, 4), 'j_piel', (6, 2, 0), brazo), ((-2, -2, -2, 4, 12, 4), 'j_piel', (-6, 2, 0), -brazo),
             ((-2.1, -2.1, -2.1, 4.2, 5, 4.2), 'j_camisa', (6, 2, 0), brazo),
             ((-2.1, -2.1, -2.1, 4.2, 5, 4.2), 'j_camisa', (-6, 2, 0), -brazo),
             ((-2, 0, -2, 4, 12, 4), 'j_pantalon', (2, 12, 0), 0), ((-2, 0, -2, 4, 12, 4), 'j_pantalon', (-2, 12, 0), 0),
             ((-2.1, 9, -2.1, 4.2, 3, 4.2), 'j_bota', (2, 12, 0), 0), ((-2.1, 9, -2.1, 4.2, 3, 4.2), 'j_bota', (-2, 12, 0), 0)]
    M = T(x, 0, z) @ Ry(guinada * D2R) @ T(0, 1.5, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1]) @ T(0, -0.0, 0)
    for box, mat, piv, rx in cajas:
        L = M @ T(*piv) @ Rx(rx * D2R)
        x0, y0, z0, w, h, d = box
        # 1,8 bloques: la cabeza de 8 px y el cuerpo de 24, a escala 0,9
        for pts, uv in _caja_mosaico(box):
            P = [(L @ np.array([*p, 1.0]))[:3] for p in pts]
            P = [np.array([p[0], p[1] * 0.9, p[2]]) for p in P]
            n = vr.normal(P)
            luz = vr.iluminar(n, cam, np.mean(P, axis=0), luces, amb)
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [P[i] for i in tri], [uv[i] for i in tri], MAT_JUGADOR[mat], luz, None, niebla,
                             envolver=True)


def _caja_mosaico(box):
    x0, y0, z0, w, h, d = box
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    V = {0: (x0, y0, z0), 1: (x1, y0, z0), 2: (x1, y1, z0), 3: (x0, y1, z0),
         4: (x0, y0, z1), 5: (x1, y0, z1), 6: (x1, y1, z1), 7: (x0, y1, z1)}
    caras = [((5, 4, 0, 1), w, d), ((2, 3, 7, 6), w, d), ((0, 4, 7, 3), d, h),
             ((1, 0, 3, 2), w, h), ((5, 1, 2, 6), d, h), ((4, 5, 6, 7), w, h)]
    out = []
    for idx, a, b in caras:
        out.append(([V[i] for i in idx], [(a / 16, 0), (0, 0), (0, b / 16), (a / 16, b / 16)]))
    return out


# --- vistas ---
def vistas(hecho, cual, rota, guinadas, W=360, H=720, dist=15.0, ojo_y=4.6, obj_y=4.0, fov=34, titulos=None):
    paneles = []
    for g in guinadas:
        cam = vr.Camara(ojo=(0.0, ojo_y, -dist), objetivo=(0.0, obj_y, 0.0), fov=fov, ancho=W * 2, alto=H * 2)
        lz = Lienzo(W * 2, H * 2)
        dibujar_prop(lz, cam, hecho, cual, rota, 0, 0, g, LUZ_ESTUDIO, AMB_ESTUDIO)
        paneles.append(a_img(estudio(lz), W, H))
    img = Image.new('RGB', (W * len(paneles), H))
    for i, p in enumerate(paneles):
        img.paste(p, (i * W, 0))
        if titulos:
            rotulo(img, titulos[i], i * W + W // 2, H - 44, 24, centro=True)
    return img


def cerca(hecho, W=1600, H=1000):
    """El primer plano: busto, cabeza y manos, de frente y a tres cuartos."""
    paneles = []
    for g, ojo, obj, fov in ((12, (0, 6.1, -8.0), (0, 5.55, 0), 22), (-28, (0, 6.1, -8.0), (0, 5.5, 0), 22)):
        cam = vr.Camara(ojo=ojo, objetivo=obj, fov=fov, ancho=W, alto=H * 2)
        lz = Lienzo(W, H * 2)
        dibujar_prop(lz, cam, hecho, 'estatua', False, 0, 0, g, LUZ_ESTUDIO, AMB_ESTUDIO)
        paneles.append(a_img(estudio(lz), W // 2, H))
    img = Image.new('RGB', (W, H))
    for i, p in enumerate(paneles):
        img.paste(p, (i * W // 2, 0))
    return img


def escala(hecho, W=1800, H=820):
    """En fila, con un jugador de 1,8 bloques: la estatua entera y rota y la
    fuente entera y rota."""
    cam = vr.Camara(ojo=(0.0, 3.3, -25.0), objetivo=(0.0, 3.5, 0.0), fov=30, ancho=W * 2, alto=H * 2)
    lz = Lienzo(W * 2, H * 2)
    # (la camara mira a +Z: la X del mundo crece hacia la izquierda de la imagen)
    jugador(lz, cam, 10.0, -0.5, 200, LUZ_ESTUDIO, AMB_ESTUDIO)
    dibujar_prop(lz, cam, hecho, 'estatua', False, 5.6, 0, 12, LUZ_ESTUDIO, AMB_ESTUDIO)
    dibujar_prop(lz, cam, hecho, 'estatua', True, -0.6, 0, 20, LUZ_ESTUDIO, AMB_ESTUDIO)
    dibujar_prop(lz, cam, hecho, 'fuente', False, -5.6, 0, 20, LUZ_ESTUDIO, AMB_ESTUDIO)
    dibujar_prop(lz, cam, hecho, 'fuente', True, -10.2, 0, 30, LUZ_ESTUDIO, AMB_ESTUDIO)
    sol_flotante(lz, cam, (-5.6, (24 - SOL_FUENTE_Y) / 16 * ESCALA, 0.0), 0.42)
    img = a_img(estudio(lz, emis=0.8), W, H)
    # las reglas: un bloque cada marca
    d = ImageDraw.Draw(img)
    for x, txt in ((10.0, 'jugador 1,8'), (5.6, 'estatua 7,5'), (-0.6, 'rota'), (-5.6, 'fuente 5'), (-10.2, 'rota')):
        sx, sy, _ = cam.proyectar((x, 0.0, -1.6))
        rotulo(img, txt, sx / 2, sy / 2 + 14, 24, centro=True)
    for yb in range(0, 9):
        a = cam.proyectar((12.6, yb, 0.0))
        b = cam.proyectar((12.0, yb, 0.0))
        d.line((a[0] / 2, a[1] / 2, b[0] / 2, b[1] / 2), fill=(90, 80, 70), width=2)
        rotulo(img, str(yb), a[0] / 2 - 26, a[1] / 2 - 12, 20)
    return img


# --- el sol de la fuente y los brillos (lo que en el juego pinta el renderer) ---
def _disco(n, nuc, pri, duro=0.35, cola=2.2):
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2) / (n / 2)
    a = np.clip(1 - r, 0, 1) ** cola
    k = np.clip((duro - r) / duro, 0, 1)[..., None]
    col = np.array(pri, float) * (1 - k) + np.array(nuc, float) * k
    t = np.zeros((n, n, 4))
    t[..., :3] = col
    t[..., 3] = np.clip(a * 255 * 1.4, 0, 255)
    return t.astype(np.uint8)


def billboard(cam, p, tam):
    r, u = cam.r * tam, cam.u * tam
    p = np.asarray(p, float)
    return [p - r + u, p + r + u, p + r - u, p - r - u], [(0, 0), (1, 0), (1, 1), (0, 1)]


def aditivo(lz, cam, P, UV, tex, k):
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, aditivo=True, brillo=k)


_TEX = {}


def sol_flotante(lz, cam, p, radio):
    """El solecito de la fuente: un nucleo blanco, el disco de oro y su halo."""
    if 'sol' not in _TEX:
        _TEX['sol'] = _disco(128, (255, 252, 235), (255, 176, 60), 0.5, 1.2)
        _TEX['halo'] = _disco(128, (255, 214, 120), (255, 120, 30), 0.2, 2.6)
    P, UV = billboard(cam, p, radio * 3.2)
    aditivo(lz, cam, P, UV, _TEX['halo'], 0.9)
    P, UV = billboard(cam, p, radio * 1.25)
    aditivo(lz, cam, P, UV, _TEX['sol'], 1.6)


def brillo_en(lz, cam, p, tam, k=0.8):
    if 'brillo' not in _TEX:
        _TEX['brillo'] = _disco(64, (255, 236, 180), (255, 150, 50), 0.25, 2.4)
    P, UV = billboard(cam, p, tam)
    aditivo(lz, cam, P, UV, _TEX['brillo'], k)


# --- el altar al atardecer ---
def _loseta_suelo(semilla, rampa, pesos, juntas=False):
    r = random.Random(semilla)
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            b = r.choice(pesos)
            if juntas and (x == 0 or y == 0):
                b = max(0, b - 2)
            t[y, x] = (*rampa[b].astype(int), 255)
    return t


BASALTO = _rampa('1e1a1c', '2a2427', '363033', '443d40', '554c4e')
ORO_SUELO = _rampa('8a5a14', 'b0761c', 'd09424', 'e8b23a', 'ffd86a')
TERRA = _rampa('6a2c16', '7e361c', '904224', 'a24e2c', 'b45c36')
SUELO = {'basalto': _loseta_suelo(31, BASALTO, (1, 2, 2, 2, 3)), 'basalto_j': _loseta_suelo(32, BASALTO, (0, 1, 1, 2, 2), True),
         'oro': _loseta_suelo(38, ORO_SUELO, (2, 3, 3, 4), True), 'terra': _loseta_suelo(34, TERRA, (1, 2, 2, 3, 3, 4))}


def suelo(lz, cam, niebla, R_altar=17):
    r = random.Random(7)
    for gx in range(-40, 40):
        for gz in range(-30, 70):
            d = math.hypot(gx + 0.5, gz + 0.5)
            lejos = abs(gx) > 24 or gz > 30
            if lejos and (gx % 4 or gz % 4):
                continue
            b = 4 if lejos else 1
            # solo anillos concentricos de oro: el sol del altar
            if d < R_altar:
                mat = 'basalto' if r.random() < 0.8 else 'basalto_j'
                if d > R_altar - 1.1 or 3.0 < d < 4.0 or d < 1.2:
                    mat = 'oro'
            else:
                mat = 'terra' if r.random() < 0.9 else 'basalto'
            P = [(gx, 0, gz), (gx + b, 0, gz), (gx + b, 0, gz + b), (gx, 0, gz + b)]
            n = np.array([0, 1.0, 0])
            luz = vr.iluminar(n, cam, np.mean(P, axis=0), LUZ_ALTAR[:1], (0.3, 0.17, 0.13)) * 0.8
            UV = [(0, 0), (b, 0), (b, b), (0, b)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], SUELO[mat], luz, None, niebla, envolver=True)


def cielo(W, H, horizonte):
    y = np.linspace(0, 1, H)[:, None]
    arriba, medio, abajo = np.array([0.09, 0.03, 0.06]), np.array([0.40, 0.10, 0.07]), np.array([0.98, 0.50, 0.19])
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.6, arriba + (medio - arriba) * (k / 0.6), medio + (abajo - medio) * ((k - 0.6) / 0.4))
    return np.broadcast_to(col[:, None, :], (H, W, 3)).copy()


def tono(x, blanco=0.35):
    m = x.max(axis=-1, keepdims=True)
    y = x / np.maximum(1, m)
    return np.clip(y + (1 - y) * np.clip(np.clip(m - 1, 0, None) * blanco, 0, 1), 0, 1)


def bloom(arr, emis, radios=((3, 0.8), (14, 0.6), (44, 0.45))):
    e = Image.fromarray((np.clip(emis, 0, 1) * 255).astype(np.uint8))
    out = arr.copy()
    for r_, k in radios:
        out += np.array(e.filter(ImageFilter.GaussianBlur(r_))).astype(float) / 255.0 * k
    return out + emis * 0.55


def vineta(arr, fuerza=0.5):
    H, W = arr.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - fuerza * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.3, 0, 1) ** 1.3
    return arr * v[..., None]


def brasas(img, n, semilla, color=(255, 170, 60)):
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H)
        rad = r.choice([1, 1, 1.5, 2, 2, 3]) * W / 1600
        d.line((x, y, x + r.uniform(-1, 1), y + r.uniform(2, 7) * W / 1600), fill=(*color, r.randint(120, 230)),
               width=max(1, int(rad)))
    out = Image.alpha_composite(img.convert('RGBA'), capa.filter(ImageFilter.GaussianBlur(2)))
    return Image.alpha_composite(out, capa)


def presentacion(hecho, W=1600, H=900, ss=2):
    """Las cuatro estatuas en corro, de cara al centro, y una fuente con su sol
    en medio, en el Altar del Sol al atardecer."""
    cam = vr.Camara(ojo=(-3.0, 8.2, -20.5), objetivo=(0.4, 3.7, 1.5), fov=50, ancho=W * ss, alto=H * ss)
    lz = Lienzo(W * ss, H * ss)
    niebla = Niebla(26, 70)
    suelo(lz, cam, niebla)
    R = 11.5
    campanas = []
    angulos = (55, 145, 235, 325)
    # de atras adelante, para que los brillos queden bien tapados
    orden = sorted(angulos, key=lambda a: -np.linalg.norm(np.array([math.cos(math.radians(a)) * R, 0,
                                                                         math.sin(math.radians(a)) * R]) - cam.ojo))
    for a in orden:
        x, z = math.cos(math.radians(a)) * R, math.sin(math.radians(a)) * R
        # de cara al centro: el frente del modelo (-Z) mira a (0, 0)
        g = math.degrees(math.atan2(x, z))
        M = dibujar_prop(lz, cam, hecho, 'estatua', False, x, z, g, LUZ_ESCENA, AMB_ESCENA, niebla, 1.2)
        m = hecho['estatua'][0]
        campanas.append((M @ np.array([*m.a_mundo('campana', (0, 5.6, 0)), 1.0]))[:3])
    Mf = dibujar_prop(lz, cam, hecho, 'fuente', False, 0.0, 0.0, 30, LUZ_ESCENA, AMB_ESCENA, niebla, 1.3)
    # dos jugadores: uno golpea la estatua de delante a la izquierda; el otro corre
    xe, ze = math.cos(math.radians(235)) * R, math.sin(math.radians(235)) * R
    jugador(lz, cam, xe + 2.2, ze + 1.4, math.degrees(math.atan2(-2.2, -1.4)) + 180, LUZ_ESCENA, AMB_ESCENA, niebla, brazo=-70)
    jugador(lz, cam, 3.4, -3.6, 140, LUZ_ESCENA, AMB_ESCENA, niebla, brazo=25)
    for p in campanas:
        brillo_en(lz, cam, p, 0.9, 0.55)
    sol_flotante(lz, cam, (0.0, (24 - SOL_FUENTE_Y) / 16, 0.0), 0.5)
    # componer
    alfa = np.array(Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float)[..., None] / 255
    col = np.array(Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)) / 255.0
    emis = np.array(Image.fromarray((np.clip(tono(lz.emis), 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)) / 255.0
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / ss
    fondo = cielo(W, H, horiz)
    # el sol del caballero, bajo, detras del altar
    sx, sy, sz = cam.proyectar((6.0, 26.0, 90.0))
    sx, sy = sx / ss, sy / ss
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot(xx - sx, yy - sy) / 55.0
    fondo = fondo + (np.clip(1 - (d - 1) / 7, 0, 1) ** 2.5)[..., None] * np.array([1.0, 0.55, 0.2]) * 0.5
    disco = np.clip(1.4 - d, 0, 1)[..., None] ** 0.5
    fondo = fondo * (1 - disco) + disco * np.array([1.0, 0.86, 0.55])
    arr = col * alfa + np.clip(fondo, 0, 1) * (1 - alfa)
    arr = tono(bloom(arr, emis))
    arr = vineta(arr, 0.5)
    arr = np.clip(arr * np.array([1.04, 0.98, 0.94]), 0, 1)
    img = brasas(Image.fromarray((arr * 255).astype(np.uint8)), 170, 3)
    img = img.convert('RGB')
    rotulo(img, 'LAS TROMPETAS DEL APOCALIPSIS', 40, 30, 40, (255, 226, 170))
    # (el rotulo lleva tildes: van escapadas para que el fuente siga en ASCII)
    rotulo(img, 'Cuatro \u00e1ngeles de m\u00e1rmol y oro, y una fuente solar  \u00b7  Novilis, el Caballero Solar', 42, 80, 22,
           (240, 200, 160), 'georgiai.ttf')
    return img


def renders(hecho, out, cuales=None):
    def quiero(n):
        return cuales is None or n in cuales

    def guardar(img, nombre):
        img.convert('RGB').save(os.path.join(out, nombre + '.jpg'), quality=91)
        print('ok', nombre, flush=True)

    if quiero('vistas'):
        guardar(vistas(hecho, 'estatua', False, [0, -35, 35, 90, 180],
                       titulos=['frente', '3/4 por su izquierda', '3/4 por su derecha', 'perfil', 'espalda']),
                'estatua_vistas')
    if quiero('cerca'):
        guardar(cerca(hecho), 'estatua_cerca')
    if quiero('rota'):
        guardar(vistas(hecho, 'estatua', True, [0, -40, 40, 180], W=420, H=520, dist=11.0, ojo_y=3.0, obj_y=1.3, fov=30,
                       titulos=['rota: frente', 'tres cuartos', 'tres cuartos', 'espalda']), 'estatua_rota')
    if quiero('fuente'):
        a = vistas(hecho, 'fuente', False, [20, 65], W=360, H=640, dist=11.0, ojo_y=3.4, obj_y=2.8, fov=34,
                   titulos=['fuente', 'fuente'])
        b = vistas(hecho, 'fuente', True, [20, 200], W=360, H=640, dist=11.0, ojo_y=3.4, obj_y=1.4, fov=34,
                   titulos=['rota', 'rota'])
        img = Image.new('RGB', (1440, 640))
        img.paste(a, (0, 0))
        img.paste(b, (720, 0))
        guardar(img, 'fuente_vistas')
    if quiero('escala'):
        guardar(escala(hecho), 'escala')
    if quiero('presentacion'):
        guardar(presentacion(hecho), 'props_presentacion')


if __name__ == '__main__':
    RAIZ = sys.argv[1]
    hecho = generar(RAIZ)
    if len(sys.argv) > 2:
        OUT = sys.argv[2]
        os.makedirs(OUT, exist_ok=True)
        renders(hecho, OUT, sys.argv[3].split(',') if len(sys.argv) > 3 else None)

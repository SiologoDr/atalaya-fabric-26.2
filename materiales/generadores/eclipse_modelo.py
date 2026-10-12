"""
Boceto 3D de la Serpiente del Eclipse (quinto jefe; nombre propuesto: Umbra),
para la ficha de diseno. Segunda version (12-10-2026, Juan): texturas propias
—nada que huela a bloque de vanilla— y mucho mas detalle en la entidad.

A diferencia de los otros bocetos (arboles de nodos en px de modelo), la
serpiente se construye directamente en bloques de mundo: una curva de control
(Catmull-Rom) recorrida por segmentos de seccion octogonal (dos cajas cruzadas
a 45 grados) con escamas a medias lunas, escudos dorsales solapados, placas de
vientre, aletas de costado, cresta de obsidiana, anillos votivos remachados y
costuras de luz de corona. La cabeza lleva corona craneal, pomulos y ceja de
placa remachada, gorguera de tres placas en el cuello, barbas, encias de
cromosfera, dos filas de dientes y el tocado de cada variante.

Materiales en mosaico de 32 px = 1 bloque, dibujados aqui (escamas solapadas,
placa remachada, obsidiana facetada, oro batido): sirven para decidir forma,
tamano y color, no son la textura final.

Tres variantes:
  A  Corona del Eclipse   el anillo del sol devorado flota tras su cabeza, de
                          obsidiana con el borde de fuego blanco y un mordisco
  B  Fauces del Ocaso     sin anillo: capucha de cobra con el eclipse pintado
                          por dentro (disco negro y corona de luz)
  C  Devorasoles          el anillo roto en ocho fragmentos que la orbitan;
                          mas oro votivo y las costuras al rojo

Medidas: unos 55 bloques de largo, cuerpo de 3,2 de grueso; alzada llega a los
13 bloques y el anillo del eclipse mide 7 de diametro.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm

TAU = math.tau

# ----------------------------------------------------------------------
#  Rampas (DISENO.md: cinco tonos, el borde tenido, el nucleo sin blanco puro)
# ----------------------------------------------------------------------
ESCAMA = nm._rampa('07050e', '110c1c', '1c1530', '2b2148', '3f3264')     # obsidiana ciruela fria
ESCAMA_O = nm._rampa('040308', '0b0714', '140e22', '1d1534', '2a1f4a')
VIENTRE = nm._rampa('262030', '3c3348', '564a60', '71627a', '8d7e92')    # ceniza palida
OBSIDIANA = nm._rampa('05040a', '0d0a18', '16122a', '211b40', '31295e')  # vitrea, facetada
PLACA = nm._rampa('0a0812', '16121f', '221c30', '2f2742', '453a5c')      # placa remachada
ORO_Q = nm._rampa('3a2408', '6a4410', '9a6a1a', 'c89428', 'eec45a')      # oro quemado
MARFIL = nm._rampa('6a5f4e', '948870', 'bcb096', 'd8cfb4', 'f2ecd8')     # colmillos
# Luces (emisivas)
CORONA = ('fff6d8', 'ffc23a')     # la corona del eclipse: blanco dorado
CROMO = ('ffd8c8', 'ff3a4a')      # cromosfera: el rojo rosado del borde


def _vacia(n=32):
    return np.zeros((n, n, 4), np.uint8)


def _pon(t, x, y, c, a=255):
    t[y % t.shape[0], x % t.shape[1]] = (*c, a)


def _escamas(semilla, rampa):
    """Escamas de serpiente: medias lunas solapadas a tresbolillo (32 px = 1 bloque).
    Se dibujan de arriba abajo para que cada fila pise a la anterior, sin juntas rectas."""
    r = random.Random(semilla)
    t = _vacia(32)
    paso_y, ancho = 5, 8
    for fila in range(-1, 8):
        y0 = fila * paso_y
        off = (ancho // 2) if fila % 2 else 0
        for cx in range(off - ancho, 33 + ancho, ancho):
            base = r.choice((1, 2, 2, 2))
            con_brillo = r.random() < 0.18
            for dy in range(0, paso_y + 3):
                k = dy / (paso_y + 2)
                w = math.sqrt(max(0.0, 1 - k * k)) * (ancho / 2)
                for dx in range(-int(w), int(w) + 1):
                    x, y = cx + dx, y0 + dy
                    borde = abs(dx) > w - 1.2 or dy >= paso_y + 1
                    if borde:
                        c = rampa[0]
                    elif dy <= 1 and abs(dx) < w - 2:
                        c = rampa[min(4, base + (2 if con_brillo else 1))]   # el lomo de la escama, a la luz
                    else:
                        c = rampa[base]
                    _pon(t, x, y, c)
    for _ in range(5):
        _pon(t, r.randrange(32), r.randrange(32), rampa[4])                  # motas de brillo frio
    return t


def _vientre_tex(semilla):
    """Placas del vientre: escudos anchos que se solapan, con el canto a la luz y muescas."""
    r = random.Random(semilla)
    t = _vacia(32)
    for y in range(32):
        fy = y % 8
        for x in range(32):
            if fy == 0:
                c = VIENTRE[4] if (x + y // 8) % 9 else VIENTRE[2]
            elif fy == 1:
                c = VIENTRE[3]
            elif fy >= 6:
                c = VIENTRE[0] if fy == 7 else VIENTRE[1]
            else:
                c = VIENTRE[2] if r.random() > 0.12 else VIENTRE[1]
            if fy in (2, 3, 4) and x % 8 == (y // 8 * 3) % 8:
                c = VIENTRE[1]                                               # la muesca del uso
            _pon(t, x, y, c)
    return t


def _obsidiana_tex(semilla):
    """Obsidiana facetada: celdas angulosas con el filo de la fractura a la luz."""
    r = random.Random(semilla)
    t = _vacia(32)
    puntos = [(r.uniform(0, 32), r.uniform(0, 32), r.choice((0, 1, 1, 2, 2, 3))) for _ in range(9)]

    def cerca(x, y):
        mejor = None
        d1 = d2 = 1e9
        for (px, py, tono) in puntos:
            dx = min(abs(x - px), 32 - abs(x - px))
            dy = min(abs(y - py), 32 - abs(y - py))
            d = dx * dx + dy * dy
            if d < d1:
                d2, d1, mejor = d1, d, tono
            elif d < d2:
                d2 = d
        return mejor, d2 - d1

    for y in range(32):
        for x in range(32):
            tono, margen = cerca(x, y)
            c = OBSIDIANA[tono]
            if margen < 2.2:
                c = OBSIDIANA[4] if (x * 3 + y) % 7 < 2 else OBSIDIANA[0]    # el filo de la faceta
            _pon(t, x, y, c)
    for _ in range(4):
        _pon(t, r.randrange(32), r.randrange(32), nm._hex('8a9ac8'))
    return t


def _placa_tex(semilla):
    """Placa forjada: bisel por todo el canto, remaches en las esquinas y algun grabado."""
    r = random.Random(semilla)
    t = _vacia(32)
    for y in range(32):
        for x in range(32):
            fx, fy = x % 16, y % 16
            m = min(fx, fy, 15 - fx, 15 - fy)
            if m == 0:
                c = PLACA[0]
            elif m == 1:
                c = PLACA[3] if fx + fy < 16 else PLACA[1]                   # el bisel
            else:
                c = PLACA[2] if r.random() > 0.12 else PLACA[1]
            _pon(t, x, y, c)
    for oy in (0, 16):
        for ox in (0, 16):
            for (rx, ry) in ((3, 3), (12, 3), (3, 12), (12, 12)):
                _pon(t, ox + rx, oy + ry, PLACA[4])
                _pon(t, ox + rx + 1, oy + ry, PLACA[1])
                _pon(t, ox + rx, oy + ry + 1, PLACA[0])
            for k in range(4):
                _pon(t, ox + 6 + k, oy + 7 + (k % 2), PLACA[0])              # el grabado
    return t


def _oro_tex(semilla):
    """Oro quemado batido: vetas horizontales de martillo, canto oscuro y remaches."""
    r = random.Random(semilla)
    t = _vacia(32)
    for y in range(32):
        for x in range(32):
            fy = y % 8
            b = (1, 2, 3, 3, 2, 2, 1, 0)[fy]
            if r.random() < 0.08:
                b = max(0, b - 1)
            if (x * 5 + y * 3) % 29 == 0:
                b = 4                                                        # el destello del batido
            _pon(t, x, y, ORO_Q[b])
    for x in range(2, 32, 8):
        _pon(t, x, 3, ORO_Q[4])
        _pon(t, x + 1, 4, ORO_Q[0])                                          # remaches
    return t


def _marfil_tex(semilla):
    r = random.Random(semilla)
    t = _vacia(32)
    for y in range(32):
        for x in range(32):
            b = r.choice((2, 3, 3, 3, 4))
            if (x + 2 * y) % 17 == 0:
                b = 1                                                        # la estria del colmillo
            _pon(t, x, y, MARFIL[b])
    return t


def _emisivo(c1, c2, semilla=0):
    a, b = nm._hex(c1), nm._hex(c2)
    t = _vacia(32)
    for y in range(32):
        for x in range(32):
            d = max(abs(x - 15.5), abs(y - 15.5)) / 15.5
            c = tuple(int(a[i] + (b[i] - a[i]) * d) for i in range(3))
            _pon(t, x, y, c)
    return t


def _ojo():
    """El ojo: brasa de oro con la pupila en rendija vertical."""
    a, b = nm._hex('ffe9a8'), nm._hex('ff8a1e')
    t = _vacia(32)
    for y in range(32):
        for x in range(32):
            d = max(abs(x - 15.5), abs(y - 15.5)) / 15.5
            c = tuple(int(a[i] + (b[i] - a[i]) * d) for i in range(3))
            rendija = 3.0 * math.sqrt(max(0.0, 1 - ((y - 15.5) / 16.0) ** 2))
            if abs(x - 15.5) < rendija:
                c = nm._hex('140a08')
            _pon(t, x, y, c)
    return t


MAT = {
    'escama': _escamas(1, ESCAMA),
    'escama_osc': _escamas(2, ESCAMA_O),
    'vientre': _vientre_tex(3),
    'obsidiana': _obsidiana_tex(4),
    'placa': _placa_tex(5),
    'oro': _oro_tex(6),
    'marfil': _marfil_tex(7),
    'fauce': nm._loseta(8, lambda x, y, r: ESCAMA_O[r.choice((0, 0, 1))]),   # el interior oscuro de la boca
    # emisivos
    'corona': _emisivo(*CORONA, 10),
    'cromo': _emisivo(*CROMO, 11),
    'ojo': _ojo(),
}
EMISIVOS = {'corona', 'cromo', 'ojo'}


# ----------------------------------------------------------------------
#  Cajas en bloques de mundo (Y hacia arriba): el mosaico repite cada bloque
# ----------------------------------------------------------------------
def _caja_quads(box):
    x0, y0, z0, w, h, d = box
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    V = {0: (x0, y0, z0), 1: (x1, y0, z0), 2: (x1, y1, z0), 3: (x0, y1, z0),
         4: (x0, y0, z1), 5: (x1, y0, z1), 6: (x1, y1, z1), 7: (x0, y1, z1)}
    caras = [((5, 4, 0, 1), w, d), ((2, 3, 7, 6), w, d), ((0, 4, 7, 3), d, h),
             ((1, 0, 3, 2), w, h), ((5, 1, 2, 6), d, h), ((4, 5, 6, 7), w, h)]
    out = []
    for idx, a, b in caras:
        if a <= 0 or b <= 0:
            continue
        uv = [(a, 0), (0, 0), (0, b), (a, b)]
        out.append(([V[i] for i in idx], uv))
    return out


def caja(out, M, x0, y0, z0, w, h, d, mat):
    for pts, uv in _caja_quads((x0, y0, z0, w, h, d)):
        p = [(M @ np.array([*q, 1.0]))[:3] for q in pts]
        out.append((p, uv, mat))


def marco(p, f, up=(0, 1, 0)):
    """Matriz del marco en p con +Z hacia f (y +Y lo mas arriba posible)."""
    f = np.array(f, float)
    f /= max(np.linalg.norm(f), 1e-9)
    u = np.array(up, float)
    u = u - f * (u @ f)
    if np.linalg.norm(u) < 1e-6:
        u = np.array([0.0, 0.0, 1.0]) - f * f[2]
    u /= np.linalg.norm(u)
    r = np.cross(u, f)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = r, u, f, p
    return M


def catmull(pts, n):
    """La curva por los puntos de control, con n muestras (posicion y tangente)."""
    P = [np.array(p, float) for p in pts]
    P = [P[0] + (P[0] - P[1])] + P + [P[-1] + (P[-1] - P[-2])]
    puntos, tangentes = [], []
    tramos = len(P) - 3
    for i in range(n):
        t = i / (n - 1) * tramos
        k = min(int(t), tramos - 1)
        u = t - k
        p0, p1, p2, p3 = P[k], P[k + 1], P[k + 2], P[k + 3]
        a = 2 * p1
        b = p2 - p0
        c = 2 * p0 - 5 * p1 + 4 * p2 - p3
        d = -p0 + 3 * p1 - 3 * p2 + p3
        puntos.append(0.5 * (a + b * u + c * u * u + d * u ** 3))
        tangentes.append(0.5 * (b + 2 * c * u + 3 * d * u * u))
    return puntos, tangentes


# ----------------------------------------------------------------------
#  El cuerpo: segmentos octogonales sobre la curva
# ----------------------------------------------------------------------
def _radio(along, R):
    """El grosor a lo largo del cuerpo (along: 0 en la cola, 1 en la cabeza)."""
    if along < 0.24:
        t = along / 0.24
        return R * (0.3 + 0.7 * t ** 0.8)              # la cola se afila
    if along > 0.84:
        t = (along - 0.84) / 0.16
        return R * (1.0 - 0.24 * t)                    # el cuello, algo mas fino
    return R


def cuerpo(out, camino, variante='A', R=1.55, n=None, costura='corona'):
    """Los segmentos del cuerpo de cola (along 0) a cabeza (along 1)."""
    n = n or max(30, int(sum(np.linalg.norm(np.array(camino[i + 1]) - np.array(camino[i]))
                             for i in range(len(camino) - 1)) / 1.15))
    pts, tg = catmull(camino, n)
    cada_oro = {'A': 7, 'B': 8, 'C': 5}[variante]
    r2 = math.sqrt(0.5)
    for i in range(1, n - 1):
        along = i / (n - 1)
        r = _radio(along, R)
        M = marco(pts[i], tg[i])
        L = np.linalg.norm(pts[min(i + 1, n - 1)] - pts[i - 1]) * 0.78
        esc = 'escama_osc' if (i // 3) % 4 == 3 else 'escama'
        caja(out, M, -r, -r, -L / 2, 2 * r, 2 * r, L, esc)
        caja(out, M @ vr.Rz(45 * vr.D2R), -r * r2 * 1.12, -r * r2 * 1.12, -L / 2 * 0.96,
             2 * r * r2 * 1.12, 2 * r * r2 * 1.12, L * 0.96, esc)
        # la placa del vientre, solapada como tejas (un escudo por segmento)
        caja(out, M @ vr.Rx(4 * vr.D2R), -r * 0.6, -r * 1.14, -L / 2 - 0.12, r * 1.2, r * 0.3, L * 0.7, 'vientre')
        caja(out, M, -r * 0.48, -r * 1.2, -L / 2 * 0.3, r * 0.96, r * 0.22, L * 0.62, 'vientre')
        # el escudo dorsal, solapado hacia atras (el lomo acorazado)
        if 0.06 < along < 0.97:
            caja(out, M @ vr.Rx(-5 * vr.D2R), -r * 0.56, r * 0.62, -L / 2 - 0.14, r * 1.12, r * 0.42, L * 0.78, 'placa')
        # cuanto tuerce aqui la curva (los adornos solo van en lo derecho)
        t0 = tg[i - 1] / np.linalg.norm(tg[i - 1])
        t1 = tg[min(i + 1, n - 1)] / np.linalg.norm(tg[min(i + 1, n - 1)])
        recto = float(t0 @ t1) > 0.962
        # la cresta de obsidiana, una pua si y otra no
        if i % 2 == 0 and 0.08 < along < 0.9:
            alto = r * (0.52 if i % 4 else 0.8)
            caja(out, M @ vr.T(0, r * 1.0, 0) @ vr.Rx(-30 * vr.D2R), -0.11, 0, -alto * 0.25,
                 0.22, alto, alto * 0.55, 'obsidiana')
        # las aletas del costado: espinas cortas que salen de entre las escamas
        if i % 3 == 2 and 0.3 < along < 0.88:
            for s in (1, -1):
                caja(out, M @ vr.T(r * 0.92 * s, r * 0.25, 0) @ vr.Rz(-58 * s * vr.D2R) @ vr.Rx(-14 * vr.D2R),
                     -0.09, 0, -0.26, 0.18, r * 0.62, 0.42, 'obsidiana')
        # el anillo votivo de oro quemado, con sus remaches (solo donde va derecho)
        if i % cada_oro == cada_oro // 2 and 0.14 < along < 0.9 and recto:
            g = r * 1.07
            caja(out, M, -g, -g, -0.17, 2 * g, 2 * g, 0.34, 'oro')
            caja(out, M @ vr.Rz(45 * vr.D2R), -g * r2 * 1.07, -g * r2 * 1.07, -0.15,
                 2 * g * r2 * 1.07, 2 * g * r2 * 1.07, 0.3, 'oro')
            for a in (45, 135, 225, 315):
                caja(out, M @ vr.Rz(a * vr.D2R) @ vr.T(0, g * 1.02, 0), -0.1, -0.06, -0.26, 0.2, 0.16, 0.52, 'oro')
        # la costura de luz entre segmentos
        elif i % 3 == 1 and 0.06 < along < 0.92 and costura and recto:
            g = r * 1.04
            caja(out, M @ vr.Rz(45 * vr.D2R), -g * r2, -g * r2, -0.08, 2 * g * r2, 2 * g * r2, 0.16, costura)
    M_cab = marco(pts[n - 1], tg[n - 1])
    M_cola = marco(pts[2], -tg[2])
    return M_cab, M_cola, _radio(0.0, R)


def cola(out, M, R=1.55):
    """El cascabel del eclipse: discos de obsidiana con el canto de oro, y la punta."""
    r2 = math.sqrt(0.5)
    z = 0.9
    for j, k in enumerate((1.5, 1.15, 0.85)):
        r = R * 0.62 * k
        for rot in (0, 45):
            caja(out, M @ vr.T(0, 0, z) @ vr.Rz(rot * vr.D2R), -r * (r2 if rot else 1), -r * (r2 if rot else 1), 0,
                 2 * r * (r2 if rot else 1), 2 * r * (r2 if rot else 1), 0.34, 'obsidiana')
        g = r * 0.5
        caja(out, M @ vr.T(0, 0, z + 0.36), -g, -g, 0, 2 * g, 2 * g, 0.1, 'oro')
        z += 0.78
    caja(out, M @ vr.T(0, 0, z) @ vr.Rz(45 * vr.D2R), -0.22, -0.22, 0, 0.44, 0.44, 1.3, 'obsidiana')


# ----------------------------------------------------------------------
#  La cabeza (en su marco: x derecha, y arriba, z hacia delante)
# ----------------------------------------------------------------------
def _colmillo(out, M, largo=0.95, g=0.3):
    caja(out, M, -g / 2, -largo * 0.55, -g / 2, g, largo * 0.6, g, 'marfil')
    caja(out, M @ vr.T(0, -largo * 0.5, 0) @ vr.Rx(10 * vr.D2R), -g * 0.3, -largo * 0.55, -g * 0.3,
         g * 0.6, largo * 0.6, g * 0.6, 'marfil')


def _cuerno(out, M, largos=(1.6, 1.2, 0.85), g0=0.52):
    g = g0
    Mi = M
    for L in largos:
        caja(out, Mi, -g / 2, 0, -g / 2, g, L, g, 'obsidiana')
        # el anillo de oro de la articulacion
        caja(out, Mi @ vr.T(0, L * 0.88, 0), -g * 0.62, 0, -g * 0.62, g * 1.24, 0.14, g * 1.24, 'oro')
        Mi = Mi @ vr.T(0, L * 0.92, 0) @ vr.Rx(-17 * vr.D2R)
        g *= 0.68
    caja(out, Mi, -g / 2, 0, -g / 2, g, 0.5, g, 'corona')     # la punta, encendida


def _halo(out, M, variante):
    """El anillo del eclipse tras la cabeza (en el plano de la cabeza: cuando ella
    te mira, el anillo es un circulo perfecto). A: entero con un mordisco; C: roto."""
    rin = 2.9
    n = 16
    r = random.Random(9)
    gajo = TAU * rin / n                                    # los gajos se tocan: el aro es macizo
    for k in range(n):
        if variante == 'A' and k in (1, 2):
            continue                                        # el mordisco, arriba a la derecha
        if variante == 'C' and k % 4 == 3:
            continue
        a = TAU * (k + 0.5) / n
        x, y = math.sin(a) * rin, math.cos(a) * rin
        Mk = M @ vr.T(x, y, 0) @ vr.Rz(-math.degrees(a) * vr.D2R)
        if variante == 'C':
            Mk = Mk @ vr.T(r.uniform(-0.08, 0.3), 0, r.uniform(-0.35, 0.35)) @ vr.Rx(r.uniform(-12, 12) * vr.D2R)
        caja(out, Mk, -gajo * 0.56, -0.7, -0.14, gajo * 1.12, 1.4, 0.28, 'obsidiana')
        caja(out, Mk, -gajo * 0.56, 0.62, -0.09, gajo * 1.12, 0.42, 0.18, 'corona')   # el borde que arde, continuo
        # el grabado votivo de oro por la cara de dentro del aro
        caja(out, Mk, -gajo * 0.3, -0.52, -0.17, gajo * 0.6, 0.3, 0.1, 'oro')
        if k % 3 == 0:
            caja(out, Mk @ vr.T(0.1, 0.95, 0) @ vr.Rz(14 * vr.D2R), -0.09, 0, -0.06, 0.18, 0.7, 0.12, 'corona')
    if variante == 'A':
        # los dos cabos del mordisco gotean luz
        for k in (0, 3):
            a = TAU * (k + 0.5) / n
            x, y = math.sin(a) * rin, math.cos(a) * rin
            caja(out, M @ vr.T(x, y, 0), -0.15, -0.15, -0.2, 0.3, 0.3, 0.4, 'cromo')


def _capucha(out, M):
    """La capucha de cobra (variante B): dos alas que se abren tras la cabeza,
    cada una con el eclipse pintado de cara (el disco negro y su corona)."""
    for s in (1, -1):
        Mb = M @ vr.T(0.55 * s, 0.5, -1.35) @ vr.Ry(-30 * s * vr.D2R) @ vr.Rz(-10 * s * vr.D2R)
        x0 = 0.0 if s > 0 else -2.3
        caja(out, Mb, x0, -0.95, -0.11, 2.3, 3.5, 0.22, 'escama_osc')
        # el canto de la capucha, de obsidiana, y tres puas en lo alto
        caja(out, Mb, x0 + (2.3 if s > 0 else -0.24), -0.95, -0.14, 0.24, 3.6, 0.28, 'obsidiana')
        for j in range(3):
            caja(out, Mb @ vr.T((0.5 + j * 0.75) * s, 2.5, 0) @ vr.Rz(-14 * s * vr.D2R), -0.11, 0, -0.1,
                 0.22, 0.75 - j * 0.14, 0.2, 'obsidiana')
        # el eclipse de dentro: el disco negro con su anillo de luz
        Mc = Mb @ vr.T(1.15 * s, 1.0, 0.13)
        caja(out, Mc, -0.55, -0.55, 0, 1.1, 1.1, 0.06, 'obsidiana')
        for k in range(10):
            a = TAU * k / 10
            caja(out, Mc @ vr.T(math.cos(a) * 0.78, math.sin(a) * 0.78, 0.01), -0.1, -0.1, 0,
                 0.2, 0.2, 0.07, 'corona')
        caja(out, Mc @ vr.T(0.62, 0.62, 0.02), -0.07, -0.07, 0, 0.14, 0.14, 0.08, 'cromo')
    # la cresta que une las dos alas por arriba
    caja(out, M @ vr.T(0, 1.55, -1.1) @ vr.Rx(-32 * vr.D2R), -0.22, 0, -0.22, 0.44, 1.2, 0.44, 'obsidiana')


def cabeza(out, M, variante='A', boca=18.0):
    """La cabeza, con la boca abierta 'boca' grados."""
    # mas grande que el cuello y un poco adelantada, como la de una vibora
    M = M @ vr.T(0, 0.1, 0.7) @ vr.S(1.34)
    # la gorguera: tres placas solapadas donde el cuello se vuelve cabeza
    for (dz, g) in ((-2.2, 1.5), (-1.75, 1.38), (-1.3, 1.26)):
        caja(out, M @ vr.T(0, 0.05, dz) @ vr.Rx(-6 * vr.D2R), -g, -g * 0.62, -0.22, 2 * g, g * 1.5, 0.44, 'placa')
    # el craneo y el hocico
    caja(out, M, -1.6, -0.75, -1.1, 3.2, 1.95, 2.6, 'escama')
    caja(out, M @ vr.Rx(7 * vr.D2R), -1.15, -0.5, 1.4, 2.3, 1.25, 2.3, 'escama')
    caja(out, M @ vr.Rx(10 * vr.D2R), -0.85, -0.25, 3.4, 1.7, 0.8, 0.9, 'escama_osc')     # la punta del hocico
    # la corona craneal: placa remachada con la quilla y el ojo ciego del craneo
    caja(out, M, -1.38, 1.02, -0.75, 2.76, 0.42, 2.5, 'placa')
    caja(out, M @ vr.Rx(16 * vr.D2R), -0.2, 1.1, 1.2, 0.4, 0.52, 1.7, 'obsidiana')         # la quilla
    caja(out, M @ vr.T(0, 1.2, 0.2), -0.24, 0, -0.24, 0.48, 0.3, 0.48, 'oro')
    caja(out, M @ vr.T(0, 1.28, 0.2), -0.12, 0, -0.12, 0.24, 0.26, 0.24, 'cromo')
    # la fila de puas de la ceja, de mas a menos
    for s in (1, -1):
        for (dz, h) in ((0.3, 0.55), (0.85, 0.45), (1.35, 0.32)):
            caja(out, M @ vr.T(1.15 * s, 1.1, dz) @ vr.Rz(-26 * s * vr.D2R) @ vr.Rx(-18 * vr.D2R),
                 -0.1, 0, -0.1, 0.2, h, 0.2, 'obsidiana')
    for s in (1, -1):
        # la ceja de placa, el ojo y su lagrima de cromosfera
        caja(out, M @ vr.T(1.18 * s, 0.78, 0.9) @ vr.Rz(-24 * s * vr.D2R) @ vr.Rx(-6 * vr.D2R),
             -0.5, 0, -0.5, 1.0, 0.42, 1.5, 'placa')
        caja(out, M @ vr.T(1.56 * s, 0.32, 1.15) @ vr.Ry(8 * s * vr.D2R), -0.07, -0.3, -0.5, 0.14, 0.6, 1.0, 'ojo')
        caja(out, M @ vr.T(1.62 * s, -0.18, 1.2) @ vr.Ry(8 * s * vr.D2R), -0.045, -0.3, -0.08, 0.09, 0.34, 0.16, 'cromo')
        # el pomulo: placa remachada sobre la mejilla, con su pua
        caja(out, M @ vr.T(1.3 * s, -0.2, 0.2) @ vr.Rz(12 * s * vr.D2R), -0.45, -0.5, -0.9, 0.9, 1.0, 1.9, 'placa')
        caja(out, M @ vr.T(1.62 * s, -0.1, -0.4) @ vr.Rz(-78 * s * vr.D2R), -0.09, 0, -0.09, 0.18, 0.6, 0.18, 'obsidiana')
        # la encia de cromosfera que se asoma entre los dientes
        caja(out, M @ vr.T(0.5 * s, -0.52, 2.2), -0.26, -0.1, -1.2, 0.52, 0.12, 2.2, 'cromo')
        # colmillos y dos filas de dientes arriba
        _colmillo(out, M @ vr.T(0.88 * s, -0.68, 3.1) @ vr.Rx(12 * vr.D2R) @ vr.Rz(-7 * s * vr.D2R), 1.05, 0.3)
        _colmillo(out, M @ vr.T(1.08 * s, -0.68, 1.6) @ vr.Rx(8 * vr.D2R) @ vr.Rz(-5 * s * vr.D2R), 0.7, 0.24)
        for j in range(4):
            caja(out, M @ vr.T(0.98 * s, -0.66, 0.1 + j * 0.52), -0.08, -0.3, -0.08, 0.16, 0.34, 0.16, 'marfil')
        for j in range(3):
            caja(out, M @ vr.T(0.6 * s, -0.6, 0.5 + j * 0.8), -0.06, -0.22, -0.06, 0.12, 0.26, 0.12, 'marfil')
        # la barba: dos bigotes de obsidiana que cuelgan de la quijada alta
        caja(out, M @ vr.T(0.95 * s, -0.62, 2.9) @ vr.Rx(38 * vr.D2R) @ vr.Rz(14 * s * vr.D2R),
             -0.07, -0.85, -0.07, 0.14, 0.85, 0.14, 'obsidiana')
    # la nariz: dos muescas oscuras con un punto de brasa dentro
    for s in (1, -1):
        caja(out, M @ vr.T(0.46 * s, 0.34, 4.2) @ vr.Rx(10 * vr.D2R), -0.11, -0.07, -0.05, 0.22, 0.14, 0.1, 'fauce')
        caja(out, M @ vr.T(0.46 * s, 0.32, 4.26) @ vr.Rx(10 * vr.D2R), -0.035, -0.03, -0.02, 0.07, 0.06, 0.05, 'cromo')
    # la mandibula, colgada atras, que se abre
    Mj = M @ vr.T(0, -0.62, -0.5) @ vr.Rx(math.radians(boca))
    caja(out, Mj, -1.3, -0.62, 0.1, 2.6, 0.66, 3.6, 'escama_osc')
    caja(out, Mj @ vr.Rx(6 * vr.D2R), -0.75, -0.5, 3.55, 1.5, 0.5, 0.75, 'escama_osc')     # el menton
    caja(out, Mj, -1.05, -0.74, 0.6, 2.1, 0.2, 2.6, 'placa')                               # la placa de la quijada
    caja(out, Mj @ vr.T(0, -0.7, 3.3) @ vr.Rx(28 * vr.D2R), -0.12, -0.6, -0.12, 0.24, 0.6, 0.24, 'obsidiana')  # la perilla
    caja(out, Mj, -1.0, 0.02, 0.4, 2.0, 0.14, 2.9, 'cromo')                                # la lengua de brasa
    caja(out, Mj @ vr.T(0, 0.1, 3.0) @ vr.Rx(-14 * vr.D2R), -0.3, 0, 0, 0.26, 0.1, 1.1, 'cromo')
    caja(out, Mj @ vr.T(0.08, 0.1, 3.0) @ vr.Rx(-14 * vr.D2R) @ vr.Ry(16 * vr.D2R), 0, 0, 0, 0.26, 0.1, 1.0, 'cromo')
    for s in (1, -1):
        _colmillo(out, Mj @ vr.T(0.95 * s, 0.4, 3.0) @ vr.Rx(math.radians(188)) @ vr.Rz(6 * s * vr.D2R), 0.72, 0.24)
        for j in range(3):
            caja(out, Mj @ vr.T(0.82 * s, 0.32, 0.8 + j * 0.7), -0.07, 0, -0.07, 0.14, 0.3, 0.14, 'marfil')
        caja(out, Mj @ vr.T(0.7 * s, 0.26, 0.3), -0.3, 0, -0.14, 0.6, 0.1, 2.9, 'cromo')   # la encia de abajo
    # la garganta, encendida: solo se ve con la boca abierta
    if boca >= 20:
        caja(out, M @ vr.T(0, -0.3, 0.1), -0.5, -0.32, -0.4, 1.0, 0.6, 0.8, 'cromo')
    # el tocado de cada variante
    if variante in ('A', 'C'):
        for s in (1, -1):
            _cuerno(out, M @ vr.T(0.95 * s, 0.9, -0.3) @ vr.Rx(-132 * vr.D2R) @ vr.Rz(16 * s * vr.D2R),
                    (2.0, 1.5, 1.0) if variante == 'A' else (1.2, 0.9), 0.56)
            _cuerno(out, M @ vr.T(1.3 * s, 0.55, -0.8) @ vr.Rx(-120 * vr.D2R) @ vr.Rz(34 * s * vr.D2R), (0.9, 0.6), 0.34)
        _halo(out, M @ vr.T(0, 1.05, -3.3), variante)
    else:
        _capucha(out, M)
        for s in (1, -1):
            _cuerno(out, M @ vr.T(0.95 * s, 0.9, -0.3) @ vr.Rx(-140 * vr.D2R) @ vr.Rz(24 * s * vr.D2R), (1.0, 0.7), 0.4)


def serpiente(camino, variante='A', boca=16.0, R=1.55):
    """Todos los quads de la serpiente sobre el camino (de la cola a la cabeza)."""
    out = []
    costura = {'A': 'corona', 'B': 'corona', 'C': 'cromo'}[variante]
    M_cab, M_cola, _ = cuerpo(out, camino, variante, R, costura=costura)
    cabeza(out, M_cab, variante, boca)
    cola(out, M_cola, R)
    return out


# ----------------------------------------------------------------------
#  Dibujo (como nm.dibujar pero con estos materiales)
# ----------------------------------------------------------------------
def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.5):
    for P, UV, mat in qs:
        tex = MAT[mat]
        if mat in EMISIVOS:
            luz, emis = np.ones(3), tex
        else:
            n = vr.normal(P)
            luz, emis = vr.iluminar(n, cam, np.mean(P, axis=0), luces, ambiente), None
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla,
                         brillo=brillo, envolver=True)


# ----------------------------------------------------------------------
#  Caminos (bloques, Y arriba): de la cola a la cabeza
# ----------------------------------------------------------------------
def camino_alzada(R=1.55):
    y = R * 1.05
    return [
        (11.0, y, 9.0), (3.5, y, 12.5), (-4.5, y, 11.0), (-9.5, y, 5.0), (-8.0, y, -2.0),
        (-1.5, y, -5.0), (5.0, y, -2.0), (7.0, y, 4.0), (2.5, y, 7.5), (-2.5, y + 0.4, 6.0),
        (-5.0, 3.4, 2.5), (-4.6, 6.4, -0.5), (-2.4, 9.6, -2.4), (0.0, 11.9, -4.0), (1.0, 12.6, -6.6),
    ]


def camino_fauces():
    return [(10.0, 1.5, 14.0), (6.0, 1.7, 9.0), (2.5, 2.6, 4.0), (0.0, 3.8, 0.0), (-0.2, 4.9, -3.0), (0.5, 5.5, -6.0)]


def camino_escala(R=1.55):
    y = R * 1.05
    return [
        (20.0, y, 2.0), (13.0, y, 6.0), (6.0, y, 2.5), (0.0, y, 6.0), (-6.0, y, 2.0),
        (-9.0, y, -3.0), (-6.5, 3.0, -7.0), (-3.5, 6.2, -8.5), (-1.5, 9.4, -8.0), (-0.5, 12.0, -6.5),
    ]

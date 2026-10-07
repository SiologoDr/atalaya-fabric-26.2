"""
Renders de la ficha de las mecanicas nuevas de Rajang (octubre de 2026: "que
cada jefe haga que los jugadores cooperen con mecanicas suyas"). Cada propuesta
en la plaza del Templo del Jaguar, con la malla y las texturas del juego y
jugadores; usa las ayudas de rajang_mejoras_escenas (lienzo, Rajang del juego,
la flecha de la Embestida) y de tierra_escenas / tierra_ataques (la plaza, la
piramide, los arboles, calcos, carteles y polvo).

  muro     Muro de Escudos: la Embestida se estampa contra tres jugadores
           hombro con hombro, con el escudo, encima de la flecha
  idolo    Idolo de Oro: el portador corre con el idolo en alto, Rajang le
           persigue al galope; un companero se lo pide y al fondo, el altar
  losas    Losas del Templo: ruge en medio; tres losas con glifos encendidas
           y un jugador en cada una, a la vez
  acecho   Acecho del Jaguar: camuflado (solo los ojos y las huellas de jade);
           el grupo junto lo frena, el que va solo tiene el aro rojo

Uso: python rajang_mecanicas_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rajang_mejoras_escenas as rm  # lee la raiz y la carpeta de salida de sys.argv
import tierra_escenas as ts
import tierra_ataques as ta
import rajang_juego as rj
import rajang_juego_anim as ra
import nerea_modelo as nm
import nerea_escenas as ne
import vigia_render as vr

OUT = rm.OUT
SS = rm.SS
TAU = math.tau
FUENTE = ts.FUENTE

JADE = (150, 255, 120)
JADE_CLARO = (226, 255, 200)
ORO = (255, 196, 70)
ORO_CLARO = (255, 240, 190)
ROJO = (255, 80, 70)
BLANCO = (240, 255, 236)


# ----------------------------------------------------------------------
#  El escudo y las poses de los jugadores
# ----------------------------------------------------------------------
def _tex_escudo(n=32):
    """El escudo de vanilla visto de frente: tablas de madera en vertical, el
    marco de hierro y la franja de en medio."""
    r = random.Random(7)
    t = np.zeros((n, n, 4), np.uint8)
    madera = [nm._hex(h) for h in ('7a4e26', '8a5a2e', '9c6a38', 'ab7842')]
    hierro = [nm._hex(h) for h in ('5a5e66', '8a8f98', 'b4b9c2')]
    for y in range(n):
        for x in range(n):
            if x < 3 or x >= n - 3 or y < 3 or y >= n - 3:
                c = hierro[0] if (x in (0, n - 1) or y in (0, n - 1)) else hierro[r.choice([1, 1, 2])]
            elif 13 <= x <= 18:
                c = hierro[r.choice([1, 2])] if not (15 <= x <= 16 and 14 <= y <= 17) else nm._hex('e2b443')
            elif (x - 3) % 5 == 0:
                c = nm._hex('5c3a1c')
            else:
                c = madera[r.choice([0, 1, 1, 2, 2, 3])]
            t[y, x] = (*c, 255)
    return t


nm.MAT.update({'escudo': _tex_escudo()})
nm.ESTIRADOS.add('escudo')


def _buscar(n, nombre):
    if n[0] == nombre:
        return n
    for h in n[4]:
        q = _buscar(h, nombre)
        if q is not None:
            return q
    return None


def jugador(lz, cam, x, z, guinada, y=0.0, pose=None, escudo=False, niebla=None, luces=None, amb=None):
    """El jugador de las fichas, con pose (brazos y piernas) y, si se pide, el
    escudo delante del pecho (como al cubrirse)."""
    raiz = ne.jugador()
    if escudo:
        # en el brazo izquierdo, por delante y algo hacia su lado (como al cubrirse en vanilla)
        _buscar(raiz, 'cuerpo')[3].append(((-5.0, -3.0, -6.0, 15, 19, 1.6), 'escudo'))
    M = vr.T(0, y, 0) @ ne.jugador_a_mundo(x, z, guinada)
    nm.dibujar(lz, cam, nm.quads(raiz, pose or {}, M), luces or ts.LUCES_SELVA, amb or ts.AMB_SELVA, niebla)


CUBRIRSE = {'bi': {'rot': (-62, 0, -6)}, 'bd': {'rot': (-24, 0, 10)}, 'pi': {'rot': (-22, 0, 0)},
            'pd': {'rot': (24, 0, 0)}}
ALZAR = {'bi': {'rot': (-172, 0, -10)}, 'bd': {'rot': (-172, 0, 10)}, 'pi': {'rot': (-38, 0, 0)},
         'pd': {'rot': (34, 0, 0)}}
CORRER = {'bi': {'rot': (40, 0, 0)}, 'bd': {'rot': (-44, 0, 0)}, 'pi': {'rot': (-40, 0, 0)}, 'pd': {'rot': (38, 0, 0)}}
PEDIR = {'bi': {'rot': (-150, 0, -24)}, 'bd': {'rot': (-20, 0, 6)}}
QUIETO = {'bi': {'rot': (-12, 0, 0)}, 'bd': {'rot': (14, 0, 0)}}
JUNTOS = {'bi': {'rot': (-50, 0, -6)}, 'bd': {'rot': (-56, 0, 6)}}
MIRAR_ATRAS = {'cabeza': {'rot': (0, 40, 0)}, 'bi': {'rot': (10, 0, -20)}, 'bd': {'rot': (-12, 0, 20)}}


# ----------------------------------------------------------------------
#  Texturas de los efectos (RGBA uint8)
# ----------------------------------------------------------------------
def _rgba(col, a):
    t = np.zeros(col.shape[:2] + (4,))
    t[..., :3] = col
    t[..., 3] = np.clip(a, 0, 1) * 255
    return np.clip(t, 0, 255).astype(np.uint8)


def tex_chispa(n=96, color=(255, 252, 226)):
    """La estrella del golpe: cuatro puntas largas y el centro encendido."""
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = np.abs(xx + 0.5 - n / 2) / (n / 2), np.abs(yy + 0.5 - n / 2) / (n / 2)
    d = np.hypot(dx, dy)
    a = np.maximum(np.clip(1 - (dx * 7 + dy), 0, 1), np.clip(1 - (dy * 7 + dx), 0, 1))
    # las cuatro diagonales, mas cortas
    u, v = (dx + dy) / math.sqrt(2), np.abs(dx - dy) / math.sqrt(2)
    a = np.maximum(a, np.clip(1 - (v * 9 + u * 1.6), 0, 1) * 0.7)
    a = np.maximum(a, np.clip(1 - d * 2.6, 0, 1) ** 0.8)
    return _rgba(np.ones((n, n, 3)) * np.array(color), a * 1.2)


def tex_halo(color, nucleo, n=64, duro=2.0):
    return ta._tex_halo(n, color, nucleo, duro)


def tex_haz(color, w=32, h=64):
    """Un haz vertical (v=0 abajo): el alma clara y el color por fuera, que se
    apaga hacia arriba."""
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    u = np.ones((h, 1)) * np.linspace(-1, 1, w)[None]
    a = np.clip(1 - np.abs(u), 0, 1) ** 1.6 * np.clip(1 - v, 0, 1) ** 0.7
    k = np.clip(1 - np.abs(u) * 3, 0, 1)[..., None]
    col = np.array(color) * (1 - k) + np.array(ORO_CLARO) * k
    return _rgba(col, a * 0.95)


def tex_aro(color, n=512, grueso=0.03, marcas=24, relleno=0.0, glifos=False):
    """Un aro en el suelo: dos filetes, muescas que giran y, si se pide, la
    greca escalonada por dentro."""
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = (xx + 0.5) / n * 2 - 1, (yy + 0.5) / n * 2 - 1
    d = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)
    a = np.exp(-((d - (1 - grueso)) / (grueso * 0.5)) ** 2)
    a += 0.7 * np.exp(-((d - (1 - grueso * 3.2)) / (grueso * 0.25)) ** 2)
    muescas = (np.abs(((ang / TAU * marcas) % 1.0) - 0.5) < 0.18) & (d > 1 - grueso * 2.8) & (d < 1 - grueso * 1.6)
    a = np.where(muescas, np.maximum(a, 0.85), a)
    if glifos:
        # una greca escalonada en un anillo por dentro
        s = (ang / TAU * 40) % 1.0
        r_ = (d - 0.62) / 0.12
        greca = (np.abs(r_) < 1) & ((np.abs(s - 0.5) < 0.12) | (np.abs(r_ - np.where(s < 0.5, 0.6, -0.6)) < 0.2))
        a = np.where(greca, np.maximum(a, 0.6), a)
        a += 0.5 * np.exp(-((d - 0.5) / 0.006) ** 2) + 0.5 * np.exp(-((d - 0.74) / 0.006) ** 2)
    a += np.where(d < 1 - grueso * 3.2, relleno * (0.6 + 0.4 * d), 0.0)
    a *= d < 1
    return _rgba(np.ones((n, n, 3)) * np.array(color), a)


def tex_muro(w=192, h=64, color=ORO):
    """El muro de escudos: un panel de hiladas de piedra en luz, mas fuerte en
    los bordes y abajo."""
    yy, xx = np.mgrid[0:h, 0:w]
    u, v = (xx + 0.5) / w, (yy + 0.5) / h
    fila = (yy // 16)
    junta_h = (yy % 16) < 2
    junta_v = ((xx + (fila % 2) * 16) % 32) < 2
    a = np.where(junta_h | junta_v, 0.75, 0.12)
    a += 0.8 * np.exp(-(np.minimum(u, 1 - u) / 0.03) ** 2) + 0.6 * np.exp(-((1 - v) / 0.06) ** 2)
    a += 0.5 * np.exp(-(v / 0.04) ** 2)
    a *= np.clip(1.2 - v * 0.4, 0, 1)
    return _rgba(np.ones((h, w, 3)) * np.array(color), a)


def tex_huella(n=128, color=JADE):
    """Una huella de jaguar vista desde arriba (los dedos hacia v=0): la
    almohadilla de tres lobulos y cuatro dedos ovalados, sin unas."""
    img = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(img)
    k = n / 128
    # la almohadilla: tres lobulos abajo y la frente recta
    d.ellipse((30 * k, 66 * k, 98 * k, 118 * k), fill=255)
    d.ellipse((22 * k, 80 * k, 58 * k, 116 * k), fill=255)
    d.ellipse((70 * k, 80 * k, 106 * k, 116 * k), fill=255)
    # los cuatro dedos, en arco
    for cx, cy, rx, ry in ((22, 50, 12, 15), (46, 28, 12, 16), (82, 28, 12, 16), (106, 50, 12, 15)):
        d.ellipse(((cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k), fill=255)
    m = np.array(img.filter(ImageFilter.GaussianBlur(1.2 * k))).astype(float) / 255
    halo = np.array(img.filter(ImageFilter.GaussianBlur(7 * k))).astype(float) / 255
    a = np.clip(m * 0.95 + halo * 0.45, 0, 1)
    k_ = np.clip(m * 1.2 - 0.2, 0, 1)[..., None] * 0.35
    col = np.array(color) * (1 - k_) + np.array(JADE_CLARO) * k_
    return _rgba(col, a)


def _mascara_glifo(n):
    """El glifo tallado en las losas: el marco doble, la cara del jaguar en
    medio y la greca en las cuatro esquinas."""
    m = np.zeros((n, n), bool)
    b = max(2, n // 24)
    m[b:2 * b, b:n - b] = m[n - 2 * b:n - b, b:n - b] = True
    m[b:n - b, b:2 * b] = m[b:n - b, n - 2 * b:n - b] = True
    c = 4 * b
    m[c:c + b // 2 + 1, c:n - c] = m[n - c - b // 2 - 1:n - c, c:n - c] = True
    m[c:n - c, c:c + b // 2 + 1] = m[c:n - c, n - c - b // 2 - 1:n - c] = True
    g = int(n * 0.5)
    o = (n - g) // 2
    m[o:o + g, o:o + g] |= ta._jaguar_glifo(g, g)
    e = int(n * 0.14)
    for (y0, x0) in ((c + b, c + b), (c + b, n - c - b - e), (n - c - b - e, c + b), (n - c - b - e, n - c - b - e)):
        m[y0:y0 + e, x0:x0 + e] |= ta._glifo(2, e, e)
    return m


def tex_losa(n=96, semilla=3):
    """La losa del templo (lo opaco): piedra verde oscura con lo tallado hundido."""
    n1 = ta._fbm2(n, n, (4, 4), semilla)
    n2 = ta._fbm2(n, n, (16, 16), semilla + 1)
    col = ta._mezcla(('16261a', '1e3424', '28442e', '345838', '3e6a44'), 0.5 + 0.5 * (n1 - 0.5) + 0.25 * (n2 - 0.5))
    m = _mascara_glifo(n)
    col[m] = col[m] * 0.5
    bajo = np.roll(m, 1, axis=0) & ~m
    col[bajo] = col[bajo] * 1.3 + 12
    return _rgba(col, np.ones((n, n)))


def tex_losa_brillo(n=96, color=JADE):
    """Lo que se enciende de la losa: lo tallado y un halo suave por encima."""
    m = _mascara_glifo(n).astype(float)
    halo = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(n / 40))).astype(float) / 255
    a = np.clip(m * 0.95 + halo * 0.5 + 0.08, 0, 1)
    return _rgba(np.ones((n, n, 3)) * np.array(color), a)


CHISPA = tex_chispa()
HALO_ORO = tex_halo(ORO, ORO_CLARO)
HAZ_ORO = tex_haz(ORO)
HAZ_JADE = tex_haz(JADE)
FLECHA_LLENA = rm._tex_flecha(lleno=0.985)
HUELLA = tex_huella()
LOSA = tex_losa()
LOSA_BRILLO = tex_losa_brillo()


# ----------------------------------------------------------------------
#  Geometria de los efectos
# ----------------------------------------------------------------------
def panel(lz, cam, a, b, alto, textura, brillo=1.0, y=0.0):
    """Un panel vertical sumado de a a b (x, z), de y a y + alto."""
    P = [(a[0], y + alto, a[1]), (b[0], y + alto, b[1]), (b[0], y, b[1]), (a[0], y, a[1])]
    UV = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], textura, np.ones(3), None, None, aditivo=True,
                     brillo=brillo)


def punto_rajang(pose, pieza, x, z, guinada, local=(0, 0, 0), fase=1):
    """Donde cae en el mundo un punto de una pieza de Rajang dibujado en (x, z)."""
    M = vr.entidad_a_mundo(x, 0, z, guinada)
    return (M @ rj.matrices(rm.con_fase(pose, fase))[pieza] @ np.array([*local, 1.0]))[:3]


def idolo(x, y, z, giro=0.0, k=1.0):
    """El idolo de oro: un jaguar sentado, de bloques de oro, con la gema de
    jade en el pecho (cajas de mundo, y hacia arriba)."""
    qs = []

    def c(dx, dy, dz, w, h, d, mat):
        qs.extend(_girar(ts.caja(dx * k, dy * k, dz * k, w * k, h * k, d * k, mat), giro, x, y, z))
    c(-0.32, 0.0, -0.26, 0.64, 0.12, 0.52, 'oro')         # la peana
    c(-0.22, 0.12, -0.16, 0.44, 0.42, 0.34, 'oro')        # el cuerpo
    c(-0.26, 0.12, -0.24, 0.16, 0.18, 0.16, 'oro')        # las patas de delante
    c(0.10, 0.12, -0.24, 0.16, 0.18, 0.16, 'oro')
    c(-0.25, 0.52, -0.25, 0.50, 0.36, 0.40, 'oro')        # la cabeza
    c(-0.25, 0.86, -0.10, 0.12, 0.12, 0.10, 'oro')        # las orejas
    c(0.13, 0.86, -0.10, 0.12, 0.12, 0.10, 'oro')
    c(-0.20, 0.64, -0.27, 0.12, 0.07, 0.03, 'cristal')     # los ojos de jade
    c(0.08, 0.64, -0.27, 0.12, 0.07, 0.03, 'cristal')
    c(-0.09, 0.26, -0.20, 0.18, 0.18, 0.06, 'cristal')     # la gema del pecho
    return qs


def _girar(qs, giro, x, y, z):
    M = vr.T(x, y, z) @ vr.Ry(math.radians(giro))
    return [([tuple((M @ np.array([*p, 1.0]))[:3]) for p in P], UV, mat) for P, UV, mat in qs]


# ----------------------------------------------------------------------
#  Rotulos (sobre la imagen compuesta, en pixeles de 1600 de ancho)
# ----------------------------------------------------------------------
def rotulo(img, cam, p, texto, dx, dy, tam=30, color=BLANCO, linea=True, centro=False):
    """Un rotulo en mayusculas junto al punto p del mundo, desplazado (dx, dy),
    con su sombra y, si se pide, una linea fina hasta el punto."""
    sx, sy, z = cam.proyectar(p)
    if z < 0.5:
        return
    sx, sy = sx / SS, sy / SS
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', tam)
    d = ImageDraw.Draw(img)
    w = d.textlength(texto, font=f)
    tx, ty = sx + dx, sy + dy
    if centro:
        tx -= w / 2
    elif dx < 0:
        tx -= w
    tx = min(max(tx, 14), img.size[0] - w - 14)          # que no se salga de la foto
    if linea:
        # la linea sale del borde del texto mas cercano al punto (Oswald deja
        # aire arriba: la letra va de 0,3 a 1,25 veces el tamano)
        ax = min(max(sx, tx), tx + w)
        arriba, abajo = ty + tam * 0.3, ty + tam * 1.3
        ay = abajo if sy > abajo else (arriba if sy < arriba else sy)
        if arriba <= sy <= abajo:
            ax = tx - 6 if sx < tx else tx + w + 6
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        dc.line([(sx, sy), (ax, ay)], fill=(6, 18, 10, 160), width=5)
        dc.line([(sx, sy), (ax, ay)], fill=(*color, 230), width=2)
        dc.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=(*color, 255))
        img.alpha_composite(capa)
    for o in ((3, 3), (2, 2), (-1, 1)):
        d.text((tx + o[0], ty + o[1]), texto, font=f, fill=(6, 18, 10, 255))
    d.text((tx, ty), texto, font=f, fill=(*color, 255))


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)


# ----------------------------------------------------------------------
#  1. Muro de Escudos
#
#  Corre hacia -z por la flecha; tres jugadores hombro con hombro encima de
#  ella, de cara a el y con el escudo: la cabeza baja se estampa contra los
#  escudos (la chispa) y el muro brilla en oro.
# ----------------------------------------------------------------------
def muro(W=1600, H=900, fase=1):
    cam = vr.Camara(ojo=(7.6, 4.0, -8.2), objetivo=(-1.2, 3.4, 4.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(26, 70)
    escena = rm.plaza_templo() + ts.piramide(6, 46) + ts._arboles((-30, 30, 16, 10), (26, 34, 18, 11), (-30, 4, 15, 9))
    ts.dibujar_mundo(lz, cam, escena, niebla, fase)
    zm = -1.0                                  # la fila del muro
    rz = zm + 10.0                             # su pecho: el hocico, a un bloque de los escudos
    ta.grieta(lz, cam, 0.0, rz + 16, 0.0, rz + 2, 1.4, semilla=31, parte='oscura')
    for x, g in ((-1.45, 184), (0.0, 180), (1.45, 176)):
        jugador(lz, cam, x, zm, g, pose=CUBRIRSE, escudo=True, niebla=niebla)
    # a la carrera, pero la cabeza le rebota hacia arriba al chocar
    pose = ra.sumar(ra.pose_en('EMBESTIDA', 0.22), ra.cabeza(x=-12, boca=10, orejas=10), ra.cuerpo(x=-4, baja=-10))
    rm.rajang(lz, cam, 0.0, rz, rm.guinada_hacia(0, -1), pose, fase, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    # lo que brilla: la flecha, el muro y el golpe
    rm.calco_tramo(lz, cam, 0.0, rz + 4.0, 0.0, -9.5, 3.0, FLECHA_LLENA, 1.1)
    ta.grieta(lz, cam, 0.0, rz + 16, 0.0, rz + 2, 1.4, semilla=31, brillo=1.0, parte='brillo')
    panel(lz, cam, (-2.3, zm + 0.66), (2.3, zm + 0.66), 2.5, tex_muro(), 1.0, y=0.05)
    golpe = np.array([0.3, 2.0, zm + 1.1])
    ta.cartel(lz, cam, golpe, 2.6, HALO_ORO, 0.8)
    ta.cartel(lz, cam, golpe, 1.7, CHISPA, 1.4)
    ta.calco(lz, cam, 0.0, zm + 0.8, 3.8, ta.ONDA, 0.8)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 41)
    ta.polvo_en(img, cam, [(-2.0, 0.3, zm + 1.5, 1.6), (2.0, 0.3, zm + 1.5, 1.6), (0, 0.3, rz + 5, 3.0)], SS,
                (128, 110, 80), 42)
    rm.lineas_movimiento(img, cam, (0.0, 5.0, rz + 4), (0, 0, -1), 22, 8.0, 43)
    rotulo(img, cam, (1.45, 2.3, zm), '¡MURO DE ESCUDOS!', 40, -150, 50, ORO_CLARO, linea=False)
    rotulo(img, cam, (-1.2, 6.5, rz - 6), 'SE ESTAMPA: 4 S ATURDIDO', -150, -80, 30, BLANCO)
    rotulo(img, cam, (-1.6, 0.05, -6.0), 'LA FLECHA DE LA EMBESTIDA', -140, 20, 26, JADE_CLARO)
    guardar(img, 'muro')


# ----------------------------------------------------------------------
#  2. Idolo de Oro
#
#  Todos corren hacia +x: Rajang al galope detras del portador, que lleva el
#  idolo en alto; delante, un companero que se lo pide; al fondo, el altar
#  (el aro de oro y jade con su haz de luz).
# ----------------------------------------------------------------------
def altar(lz, cam, x, z, niebla, fase):
    """El altar: una peana de piedra del templo con el borde de oro (lo opaco)."""
    qs = ts.caja(x - 1.2, 0, z - 1.2, 2.4, 0.9, 2.4, 'templo') + ts.caja(x - 1.35, 0.9, z - 1.35, 2.7, 0.25, 2.7, 'oro')
    ts.dibujar_mundo(lz, cam, qs, niebla, fase)


def altar_brillo(lz, cam, x, z):
    ta.calco(lz, cam, x, z, 4.2, tex_aro(ORO, glifos=True, relleno=0.12), 1.2)
    ta.calco(lz, cam, x, z, 3.0, tex_aro(JADE, grueso=0.05, marcas=12), 0.9)
    ta.cinta(lz, cam, (x, 1.1, z), (x, 30.0, z), 1.4, HAZ_ORO, 1.2)
    ta.cinta(lz, cam, (x, 1.1, z), (x, 22.0, z), 0.5, HAZ_ORO, 1.0)
    ta.cartel(lz, cam, (x, 1.6, z), 2.6, HALO_ORO, 0.8)


def idolo_escena(W=1600, H=900, fase=2):
    # la camara mira hacia +z: en la foto, -x queda a la derecha
    cam = vr.Camara(ojo=(-1.5, 4.2, -12.0), objetivo=(-2.5, 3.8, 5.0), fov=64, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(30, 80)
    escena = rm.plaza_templo(26, 60, 44) + ts.piramide(14, 44) + ts._arboles((30, 22, 16, 10), (-30, 34, 18, 11),
                                                                              (-12, 46, 17, 10))
    ts.dibujar_mundo(lz, cam, escena, niebla, fase)
    portador = np.array([-2.6, -1.0])
    companero = np.array([-7.4, -3.4])
    meta = np.array([-14.0, 20.0])
    rx, rz = 8.6, 4.0                            # su pecho
    altar(lz, cam, meta[0], meta[1], niebla, fase)
    # el portador, corriendo hacia el altar con el idolo en alto
    g_port = rm.guinada_hacia(meta[0] - portador[0], meta[1] - portador[1])
    jugador(lz, cam, portador[0], portador[1], g_port, pose=ALZAR, niebla=niebla)
    ts.dibujar_mundo(lz, cam, idolo(portador[0], 2.2, portador[1], giro=-15, k=1.25), niebla, fase)
    # el companero, de cara a el, con la mano en alto
    jugador(lz, cam, companero[0], companero[1], rm.guinada_hacia(*(portador - companero)), pose=PEDIR, niebla=niebla)
    # Rajang al galope detras del portador, la cabeza baja y fija en el
    pose = ra.sumar(ra.pose_en('CORRER', 0.5), ra.cuerpo(baja=-9), ra.cabeza(x=-4, boca=12))
    rm.rajang(lz, cam, rx, rz, rm.guinada_hacia(portador[0] - rx, portador[1] - rz), pose, fase, ts.LUCES_SELVA,
              ts.AMB_SELVA, niebla)
    # lo que brilla: el idolo, el aro del portador, el altar y las chispas de oro
    ta.calco(lz, cam, portador[0], portador[1], 1.5, tex_aro(ORO, grueso=0.08, marcas=10, relleno=0.15), 1.0)
    altar_brillo(lz, cam, meta[0], meta[1])
    centro = np.array([portador[0], 2.8, portador[1]])
    ta.cartel(lz, cam, centro, 2.0, HALO_ORO, 0.9)
    ta.cartel(lz, cam, centro + np.array([0, 0.1, 0]), 0.8, CHISPA, 0.6)
    r = random.Random(5)
    for _ in range(16):
        q = centro + np.array([r.uniform(-1.3, 1.3), r.uniform(-1.0, 1.4), r.uniform(-1.3, 1.3)])
        ta.cartel(lz, cam, q, r.uniform(0.1, 0.22), HALO_ORO, 1.2)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 51)
    ta.polvo_en(img, cam, [(rx + 3, 0.3, rz, 3.2), (rx - 2, 0.3, rz - 1, 2.4)], SS, (128, 110, 80), 52)
    rm.lineas_movimiento(img, cam, (rx, 4.0, rz), (portador[0] - rx, 0, portador[1] - rz), 24, 8.0, 53)
    rm.lineas_movimiento(img, cam, (portador[0] + 0.8, 1.0, portador[1] - 0.2), (-1, 0, 0.4), 8, 2.5, 54, ORO_CLARO, 2)
    rotulo(img, cam, (portador[0], 3.4, portador[1]), 'PORTADOR', 0, -120, 40, ORO_CLARO, centro=True)
    rotulo(img, cam, (companero[0], 2.5, companero[1]), '¡PÁSAMELO!', 50, -50, 40, BLANCO)
    rotulo(img, cam, (meta[0], 8.0, meta[1]), 'ALTAR', -50, -30, 40, ORO_CLARO)
    rotulo(img, cam, (rx - 5.5, 6.0, rz), 'SOLO VA A POR EL PORTADOR', -40, -170, 28, JADE_CLARO)
    guardar(img, 'idolo')


# ----------------------------------------------------------------------
#  3. Losas del Templo
#
#  Ruge en medio de la plaza; alrededor, a 12-18 bloques, tres losas con el
#  glifo encendido y un jugador encima de cada una. El aro de cada losa es la
#  cuenta de los 3 s (las tres a la vez); mientras, las ondas de sus golpes.
# ----------------------------------------------------------------------
def tex_cuenta(cuenta, n=256, color=JADE):
    """El aro de la cuenta: lo que llevan pisado (de las 12 en sentido horario),
    encendido; lo que falta, tenue; y doce marcas."""
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = (xx + 0.5) / n * 2 - 1, (yy + 0.5) / n * 2 - 1
    d = np.hypot(dx, dy)
    ang = (np.arctan2(dx, -dy) / TAU) % 1.0
    banda = (d > 0.84) & (d < 0.97)
    a = np.where(banda, np.where(ang < cuenta, 0.95, 0.22), 0.0)
    marcas = (np.abs(((ang * 12) % 1.0) - 0.5) > 0.46) & (d > 0.8) & (d < 1.0)
    a = np.where(marcas, 1.0, a)
    a += 0.6 * np.exp(-((d - 0.78) / 0.008) ** 2)
    return _rgba(np.ones((n, n, 3)) * np.array(color), a * (d < 1))


def losa(lz, cam, x, z, niebla, fase):
    """La losa (lo opaco): la piedra un poco alzada y la cara tallada encima."""
    ts.dibujar_mundo(lz, cam, ts.caja(x - 1.5, 0, z - 1.5, 3, 0.16, 3, 'templo'), niebla, fase)
    ta.calco(lz, cam, x, z, 1.5, LOSA, y=0.17, opaco=True, luz=np.array([0.9, 0.95, 0.9]))


def losas(W=1600, H=900, fase=3):
    cam = vr.Camara(ojo=(-1.5, 10.5, -19.5), objetivo=(0.0, 2.2, 4.5), fov=64, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 80)
    escena = rm.plaza_templo(26, 64, 44) + ts.piramide(2, 46) + ts._arboles((-32, 24, 17, 10), (32, 28, 18, 11),
                                                                             (-36, -6, 15, 9), (36, -2, 15, 9))
    ts.dibujar_mundo(lz, cam, escena, niebla, fase)
    cx, cz = 0.0, 5.0
    sitios = [(-11.0, -3.0), (10.0, -4.5), (14.0, 14.0)]
    r = random.Random(8)
    grietas = []
    for k in range(8):
        a = TAU * k / 8 + r.uniform(-0.2, 0.2)
        grietas.append((cx + math.cos(a) * 3.5, cz + math.sin(a) * 3.5, cx + math.cos(a) * r.uniform(7, 10),
                        cz + math.sin(a) * r.uniform(7, 10), r.uniform(0.4, 0.7), 60 + k))
    for g in grietas:
        ta.grieta(lz, cam, *g[:5], semilla=g[5], parte='oscura')
    for (x, z) in sitios:
        losa(lz, cam, x, z, niebla, fase)
        jugador(lz, cam, x, z, rm.guinada_hacia(cx - x, cz - z), y=0.16, pose=QUIETO, niebla=niebla)
    # un cuarto jugador, fuera, saltando la onda
    jugador(lz, cam, -4.0, -6.5, rm.guinada_hacia(cx + 4, cz + 6.5), y=0.9, pose=CORRER, niebla=niebla)
    pose = ra.sumar(ra.pose_en('RUGIDO', 0.6), ra.cabeza(y=-8))
    rm.rajang(lz, cam, cx, cz, rm.guinada_hacia(0.7, -1), pose, fase, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    # lo que brilla: las grietas, las ondas, las losas encendidas y su cuenta
    for g in grietas:
        ta.grieta(lz, cam, *g[:5], semilla=g[5], brillo=1.0, parte='brillo')
    ta.calco(lz, cam, cx, cz, 8.5, ta.ONDA, 0.8)
    ta.calco(lz, cam, cx, cz, 10.0, ta.ONDA, 0.5)
    cuenta = tex_cuenta(0.66)
    for (x, z) in sitios:
        ta.calco(lz, cam, x, z, 1.5, LOSA_BRILLO, 1.2, y=0.18)
        ta.calco(lz, cam, x, z, 2.5, cuenta, 1.1, y=0.06)
        ta.cinta(lz, cam, (x, 0.2, z), (x, 5.5, z), 1.5, HAZ_JADE, 0.55)
        ta.cinta(lz, cam, (x, 2.6, z), (cx, 7.0, cz), 0.25, ts.LINEA, 0.6)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 61, oscuro=0.2, rayos=False)
    ta.polvo_en(img, cam, [(cx, 0.4, cz - 4, 4.0)], SS, (110, 120, 80), 62)
    for (x, z) in sitios:
        rotulo(img, cam, (x, 2.6, z), '3 S', 0, -62, 40 if z < 10 else 30, JADE_CLARO, linea=False, centro=True)
    rotulo(img, cam, (cx, 11.5, cz), '¡TODAS A LA VEZ!', 0, -70, 54, JADE_CLARO, linea=False, centro=True)
    rotulo(img, cam, (-4.0, 1.0, -6.5), 'Y SALTAR SUS ONDAS', -40, 60, 26, BLANCO)
    rotulo(img, cam, (-11.0 - 1.5, 0.2, -3.0 - 1.5), 'LOSA CON GLIFO', -60, 40, 26, BLANCO)
    guardar(img, 'losas')


# ----------------------------------------------------------------------
#  4. Acecho del Jaguar
#
#  De noche en la plaza. Camuflado, de Rajang solo se ve un temblor oscuro y
#  los ojos de oro encendidos (el aviso); las huellas de jade rodean al grupo
#  y acaban en el. El grupo, junto (el aro de 4 bloques), lo frena; el que se
#  ha quedado solo tiene el aro rojo y el arco del salto encima.
# ----------------------------------------------------------------------
LUCES_NOCHE = [((-0.5, 1.0, -0.35), (0.55, 0.7, 0.6), 0.75, 'llave'), ((0.7, 0.35, 0.7), (0.35, 0.9, 0.45), 0.6, 'contra')]
AMB_NOCHE = (0.13, 0.17, 0.14)


def rajang_camuflado(lz, cam, x, z, guinada, pose, fase, k=0.4, tinte=(0.5, 0.68, 0.55)):
    """Rajang casi invisible: la malla del juego, oscura y translucida, sin
    brillos (se pinta despues de lo opaco)."""
    M = vr.entidad_a_mundo(x, 0, z, guinada)
    tex, _ = rm.piel(fase)
    qs = rj.quads(rm.con_fase(pose, fase), rm.UV_ATLAS, rm.ALTO_ATLAS, M)
    qs.sort(key=lambda q: -cam.proyectar(np.mean(q[0], axis=0))[2])
    for Pq, UVq, _, _ in qs:
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), LUCES_NOCHE, AMB_NOCHE) * np.array(tinte)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[i] for i in tri], [UVq[i] for i in tri], tex, luz, None, None, translucido=k)
    return qs


def camino_huellas(puntos, paso=2.3, lado=0.75):
    """Las huellas a lo largo de una curva (lista de (x, z)): (x, z, giro) de
    cada una, alternando a un lado y a otro, con los dedos hacia delante."""
    pts = [np.array(p, float) for p in puntos]
    largo = [0.0]
    for i in range(1, len(pts)):
        largo.append(largo[-1] + np.linalg.norm(pts[i] - pts[i - 1]))
    out = []
    t, k = 0.0, 0
    while t < largo[-1]:
        i = max(j for j in range(len(pts) - 1) if largo[j] <= t)
        u = (t - largo[i]) / max(largo[i + 1] - largo[i], 1e-6)
        p = pts[i] + (pts[i + 1] - pts[i]) * u
        d = (pts[i + 1] - pts[i]) / max(np.linalg.norm(pts[i + 1] - pts[i]), 1e-6)
        n = np.array([-d[1], d[0]]) * lado * (1 if k % 2 else -1)
        out.append((p[0] + n[0], p[1] + n[1], math.degrees(math.atan2(d[0], -d[1]))))
        t += paso
        k += 1
    return out


def suave(puntos, n=8):
    """Catmull-Rom por los puntos de control (para que el rodeo sea curvo)."""
    P = [np.array(p, float) for p in puntos]
    P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        for k in range(n):
            u = k / n
            out.append(tuple(ra.catmull(u, P[i - 1], P[i], P[i + 1], P[i + 2])))
    out.append(tuple(P[-2]))
    return out


def acecho(W=1600, H=900, fase=2):
    # la camara mira hacia +z: en la foto, -x queda a la derecha
    cam = vr.Camara(ojo=(-1.0, 8.5, -20.0), objetivo=(-1.5, 1.5, 3.5), fov=62, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(22, 60)
    niebla.color = (0.07, 0.12, 0.09)
    escena = rm.plaza_templo(26, 60, 44) + ts.piramide(0, 42) + ts._arboles((-28, 18, 16, 10), (28, 22, 18, 11),
                                                                             (-20, 34, 17, 10), (18, 38, 16, 9))
    ts.dibujar_mundo(lz, cam, escena, niebla, fase, LUCES_NOCHE, AMB_NOCHE)
    grupo = np.array([6.5, -3.0])
    solo = np.array([-4.5, -8.0])
    rx, rz = -19.0, 8.5                      # su pecho, agazapado
    for dx, dz, g in ((-0.9, -0.5, 20), (0.9, -0.4, -30), (0.0, 0.9, 170)):
        jugador(lz, cam, grupo[0] + dx, grupo[1] + dz, rm.guinada_hacia(rx - grupo[0], rz - grupo[1]) + g * 0.3,
                pose=JUNTOS, niebla=niebla, luces=LUCES_NOCHE, amb=AMB_NOCHE)
    jugador(lz, cam, solo[0], solo[1], rm.guinada_hacia(0.4, -1), pose=MIRAR_ATRAS, niebla=niebla, luces=LUCES_NOCHE,
            amb=AMB_NOCHE)
    pose = ra.sumar(ra.pose_en('EMBESTIDA_AVISO', 1.0), ra.cabeza(x=-6, boca=20, orejas=-10))
    g_r = rm.guinada_hacia(solo[0] - rx, solo[1] - rz)
    # lo que brilla primero (las huellas, los aros), y encima el camuflaje translucido
    rodeo = suave([(14.5, -9.5), (15.5, 2.0), (10.0, 9.5), (1.0, 12.5), (-8.0, 13.0), (rx + 5.0, rz + 2.5)], 10)
    huellas = camino_huellas(rodeo)
    for i, (x, z, giro) in enumerate(huellas):
        k = 0.35 + 0.85 * (i + 1) / len(huellas)
        ta.calco(lz, cam, x, z, 0.95, HUELLA, k, giro=giro)
    ta.calco(lz, cam, grupo[0], grupo[1], 4.0, tex_aro(JADE, grueso=0.025, marcas=32, relleno=0.06), 0.9)
    ta.calco(lz, cam, solo[0], solo[1], 1.7, tex_aro(ROJO, grueso=0.09, marcas=8, relleno=0.18), 1.3)
    rajang_camuflado(lz, cam, rx, rz, g_r, pose, fase)
    # los ojos: el aviso de 1 s antes del salto
    for pieza in ('ojo_izq', 'ojo_der'):
        o = punto_rajang(pose, pieza, rx, rz, g_r, local=(0, 0, -1.0), fase=fase)
        ta.cartel(lz, cam, o, 1.5, HALO_ORO, 1.1)
        ta.cartel(lz, cam, o, 0.55, CHISPA, 1.5)
    # el arco del salto, de el al solitario
    cabeza = punto_rajang(pose, 'cabeza', rx, rz, g_r, fase=fase)
    meta = np.array([solo[0], 1.2, solo[1]])
    halo_rojo = tex_halo(ROJO, (255, 200, 190))
    for i in range(2, 24):
        u = i / 24
        q = cabeza + (meta - cabeza) * u + np.array([0, 5.0 * math.sin(math.pi * u), 0])
        ta.cartel(lz, cam, q, 0.3 + 0.25 * u, halo_rojo, 1.3)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 71, oscuro=0.6, rayos=False)
    rotulo(img, cam, (grupo[0], 2.3, grupo[1]), 'JUNTOS: LO FRENAN', 0, -120, 40, JADE_CLARO, linea=False, centro=True)
    rotulo(img, cam, (solo[0], 0.0, solo[1]), 'SOLO: SALTA SOBRE TI', 0, 40, 40, (255, 150, 140), linea=False,
           centro=True)
    h = huellas[5]
    rotulo(img, cam, (h[0], 0.05, h[1]), 'SUS HUELLAS DE JADE', -40, 90, 28, JADE_CLARO)
    o = punto_rajang(pose, 'ojo_der', rx, rz, g_r, fase=fase)
    rotulo(img, cam, o, 'SOLO SE LE VEN LOS OJOS', 10, -190, 28, ORO_CLARO)
    guardar(img, 'acecho')


ESCENAS = {'muro': muro, 'idolo': idolo_escena, 'losas': losas, 'acecho': acecho}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
        print('ok', nombre, flush=True)

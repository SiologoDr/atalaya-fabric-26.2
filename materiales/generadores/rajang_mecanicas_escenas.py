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

Segunda ficha (los minijuegos): camaras mas cerca de los jugadores.

  monta    Monta al Jaguar: se encabrita para tirar al jinete, que va agarrado
           a la espada clavada en su lomo (con el contorno de oro); al lado, la
           pantalla del jinete (la flecha, la tecla A, la cuenta y los aciertos
           seguidos) y abajo dos companeros que le pegan en las patas
  suelo    Suelo que se Hunde: la plaza hecha losas de jade de 2x2 sobre un
           foso de pinchos; el que corre deja un rastro (agrietada, rota,
           cayendo, hueco), otro salta un hueco y Rajang ruge inmune en su peana
  lazos    Lazos de Liana: agazapado para la Embestida (la flecha), las patas
           encendidas; tres jugadores tiran de lianas tensas atadas a tres patas
           (el nudo de oro) y un cuarto corre con otra junto a las que brotan
  glifos   Glifos del Templo: corro de columnas con seis glifos de jade iguales
           de luz; el Vidente (contorno de oro) los dice, otro golpea la espiral,
           el jaguar ya esta roto; arriba, la pantalla del Vidente con los 3
           verdaderos

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


# ======================================================================
#  Segunda ficha: los minijuegos (octubre de 2026)
# ======================================================================
def _plano(c1, c2, semilla, p=0.7):
    a, b = nm._hex(c1), nm._hex(c2)
    return nm._loseta(semilla, lambda x, y, r: a if r.random() < p else b)


nm.MAT.update({
    'hoja_espada': _plano('6eeee2', '4fd8cf', 331),       # la espada de diamante
    'filo_espada': _plano('c8fff8', 'a8f8ee', 332),
    'mango_espada': _plano('5a3a1e', '4a2e16', 333),
    'guarda_espada': _plano('2fb8c8', '24a0ae', 334),
})


def nodo_espada(nombre='espada', off=(0, 10, -1), rot=(0, 0, 0), k=1.0):
    """Una espada de diamante en pixeles de modelo: la hoja hacia -Z, el mango
    hacia +Z y el centro del puno en el origen del nodo."""
    def c(x, y, z, w, h, d):
        return (x * k, y * k, z * k, w * k, h * k, d * k)
    return nm.nodo(nombre, off, rot, [
        (c(-0.8, -0.8, -1.0, 1.6, 1.6, 5.0), 'mango_espada'),
        (c(-0.9, -0.9, 3.6, 1.8, 1.8, 1.4), 'guarda_espada'),
        (c(-3.0, -1.2, -2.4, 6.0, 2.4, 1.4), 'guarda_espada'),
        (c(-0.6, -1.4, -16.0, 1.2, 2.8, 13.6), 'hoja_espada'),
        (c(-0.5, -0.9, -18.0, 1.0, 1.8, 2.0), 'filo_espada'),
    ])


def matriz_jugador(x, z, guinada, y=0.0, inclina=0.0):
    """La del jugador de las fichas; 'inclina' lo echa hacia atras (grados)
    girando por los pies."""
    return vr.T(x, y, z) @ vr.Ry(guinada * vr.D2R) @ vr.Rx(-inclina * vr.D2R) @ vr.T(0, 1.5, 0) \
        @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])


def jugador2(lz, cam, M, pose=None, espada=False, rot_espada=(0, 0, 0), niebla=None, luces=None, amb=None):
    """El jugador con la matriz M (de matriz_jugador o pegado a Rajang) y, si se
    pide, la espada en la mano derecha."""
    raiz = ne.jugador()
    if espada:
        _buscar(raiz, 'bd')[4].append(nodo_espada(rot=rot_espada))
    qs = nm.quads(raiz, pose or {}, M)
    nm.dibujar(lz, cam, qs, luces or ts.LUCES_SELVA, amb or ts.AMB_SELVA, niebla)
    return qs


def contorno(img, cam, qs, color, grosor=3, halo=0.5, lz=None):
    """El contorno de algo (como el efecto Brillante de Minecraft): la silueta
    de los quads, engordada, menos ella misma; con un halo suave. Con lz, solo
    lo que se ve en ese lienzo (lo tapado no lleva contorno)."""
    W, H = img.size
    solo = vr.Lienzo(W * SS, H * SS)
    blanco = np.full((4, 4, 4), 255, np.uint8)
    for P, _, _ in qs:
        for tri in ((0, 1, 2), (0, 2, 3)):
            solo.triangulo(cam, [P[i] for i in tri], [(0, 0), (1, 0), (1, 1)], blanco, np.ones(3))
    alfa_s = solo.alfa
    if lz is not None:
        alfa_s = alfa_s * (solo.z <= lz.z * 1.002 + 1e-3)
    a = Image.fromarray((alfa_s * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    gordo = a.filter(ImageFilter.MaxFilter(2 * grosor + 1))
    borde = np.clip(np.array(gordo).astype(float) - np.array(a).astype(float), 0, 255) / 255
    suave = np.array(gordo.filter(ImageFilter.GaussianBlur(grosor * 3))).astype(float) / 255 * halo
    alfa = np.clip(np.maximum(borde, suave * (1 - np.array(a) / 255)), 0, 1)
    capa = np.zeros((H, W, 4), np.uint8)
    capa[..., :3] = color
    capa[..., 3] = (alfa * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(capa))


def mano_jugador(M, pose, lado='bd', largo=10.0):
    """Donde cae en el mundo la mano de un brazo del jugador (bi o bd)."""
    piv = {'bi': (6, 2, 0), 'bd': (-6, 2, 0)}[lado]
    r = (pose or {}).get(lado, {}).get('rot', (0, 0, 0))
    L = vr.T(*piv) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R)
    return (M @ L @ np.array([0, largo, 0, 1.0]))[:3]


def matriz_hacia(p, q, k=1.0):
    """La matriz de un nodo de pixeles (la hoja hacia -Z) con el origen en p y la
    hoja apuntando hacia q, a k/16 bloques por pixel."""
    d = np.array(q, float) - np.array(p, float)
    zax = -d / np.linalg.norm(d)
    xax = np.cross([0.0, 1.0, 0.0], zax)
    if np.linalg.norm(xax) < 1e-6:
        xax = np.array([1.0, 0, 0])
    xax /= np.linalg.norm(xax)
    yax = np.cross(zax, xax)
    R = np.eye(4)
    R[:3, 0], R[:3, 1], R[:3, 2] = xax, yax, zax
    return vr.T(*p) @ R @ np.diag([k / 16, k / 16, k / 16, 1])


def rajang_en(lz, cam, x, y, z, guinada, pose, fase, luces=None, amb=None, niebla=None, k_cristal=0.45):
    """Como rm.rajang, pero a la altura y (encima de una peana)."""
    M = vr.entidad_a_mundo(x, y, z, guinada)
    tex, brillo = rm.piel(fase)
    qs = rj.quads(rm.con_fase(pose, fase), rm.UV_ATLAS, rm.ALTO_ATLAS, M)
    for Pq, UVq, _, mat in qs:
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), luces or ts.LUCES_SELVA, amb or ts.AMB_SELVA)
        k = k_cristal if mat == 'cristal' else 1.0
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[i] for i in tri], [UVq[i] for i in tri], tex, luz, brillo, niebla, brillo=k)
    return qs


def matriz_pieza(pose, pieza, x, z, guinada, fase, y=0.0):
    """La matriz de una pieza de Rajang en el mundo (pixeles de su modelo)."""
    return vr.entidad_a_mundo(x, y, z, guinada) @ rj.matrices(rm.con_fase(pose, fase))[pieza]


def _fuente(tam):
    return ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', tam)


def texto_sombra(img, xy, texto, tam, color=BLANCO, sombra=(6, 18, 10)):
    d = ImageDraw.Draw(img)
    f = _fuente(tam)
    for o in ((3, 3), (2, 2), (-1, 1)):
        d.text((xy[0] + o[0], xy[1] + o[1]), texto, font=f, fill=(*sombra, 255))
    d.text(xy, texto, font=f, fill=(*color, 255))


def pildora(img, cx, cy, texto, tam, color=BLANCO, fondo=(8, 22, 14, 205), borde=(150, 255, 120, 220)):
    """Un texto dentro de una pastilla redondeada, centrado en (cx, cy)."""
    f = _fuente(tam)
    d = ImageDraw.Draw(img)
    w = d.textlength(texto, font=f)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).rounded_rectangle((cx - w / 2 - 18, cy - tam * 0.62, cx + w / 2 + 18, cy + tam * 0.72),
                                           int(tam * 0.6), fill=fondo, outline=borde, width=3)
    img.alpha_composite(capa)
    texto_sombra(img, (cx - w / 2, cy - tam * 0.68), texto, tam, color)


def capa_fina(img, dibujo, k=2):
    """Dibuja con PIL a k veces el tamano y lo baja (bordes suaves): dibujo(d, k)."""
    W, H = img.size
    capa = Image.new('RGBA', (W * k, H * k), (0, 0, 0, 0))
    dibujo(ImageDraw.Draw(capa), k)
    img.alpha_composite(capa.resize((W, H), Image.LANCZOS))


# ----------------------------------------------------------------------
#  5. Monta al Jaguar
#
#  Se encabrita con las patas de delante en alto para tirar al jinete, que
#  va agarrado a la espada clavada en su lomo; junto a el, lo que sale en la
#  pantalla del jinete: la flecha que toca (A), la cuenta del tiempo y los
#  aciertos seguidos (2 de 5). Abajo, dos companeros le pegan en las patas.
# ----------------------------------------------------------------------
AGARRADO = {'bi': {'rot': (-104, 0, -12)}, 'bd': {'rot': (-104, 0, 12)}, 'pi': {'rot': (-62, 0, 34)},
            'pd': {'rot': (-62, 0, -34)}, 'cabeza': {'rot': (-16, 0, 0)}}
GOLPE = {'cabeza': {'rot': (-22, 0, 0)}, 'bi': {'rot': (-30, 0, -10)}, 'bd': {'rot': (-150, 0, 10)},
         'pi': {'rot': (-24, 0, 0)}, 'pd': {'rot': (20, 0, 0)}}
TAJO = {'cabeza': {'rot': (-14, 0, 0)}, 'bi': {'rot': (-20, 0, -8)}, 'bd': {'rot': (-96, -30, 20)},
        'pi': {'rot': (-20, 0, 0)}, 'pd': {'rot': (18, 0, 0)}}
# el jinete, con algo mas de luz para que se lea sobre el jade
LUCES_JINETE = [((-0.5, 1.0, -0.6), (1.0, 0.95, 0.8), 1.2, 'llave'), ((0.7, 0.35, 0.7), (1.0, 0.9, 0.5), 0.9, 'contra')]


def flecha_hud(d, cx, cy, tam, k, color, sombra=(6, 18, 10, 200)):
    """Una flecha gruesa hacia la izquierda, centrada en (cx, cy) (en la capa x k)."""
    s = tam * k
    pts = [(-0.95, 0.0), (-0.1, -0.78), (-0.1, -0.34), (0.9, -0.34), (0.9, 0.34), (-0.1, 0.34), (-0.1, 0.78)]
    q = [(cx * k + x * s * 0.5, cy * k + y * s * 0.5) for x, y in pts]
    d.polygon([(x + 5 * k, y + 5 * k) for x, y in q], fill=sombra)
    d.polygon(q, fill=color)


def pantalla_jinete(img, cx, cy, cuenta=0.62, aciertos=2, total=5):
    """Lo que ve el jinete: la flecha que toca dentro de un aro que se va
    cerrando (la cuenta), la tecla (A) y los aciertos seguidos."""
    R = 92

    def dib(d, k):
        # el marco de la pantalla (para que se lea como un recuadro aparte)
        x0, y0, x1, y1 = cx - R - 190, cy - R - 82, cx + R + 70, cy + R + 84
        d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), 18 * k, fill=(6, 16, 10, 150),
                            outline=(*ORO_CLARO, 200), width=3 * k)
        # el fondo y el aro de la cuenta
        d.ellipse(((cx - R) * k, (cy - R) * k, (cx + R) * k, (cy + R) * k), fill=(8, 24, 14, 215))
        d.ellipse(((cx - R) * k, (cy - R) * k, (cx + R) * k, (cy + R) * k), outline=(150, 255, 120, 120), width=4 * k)
        a0 = -90
        d.arc(((cx - R - 8) * k, (cy - R - 8) * k, (cx + R + 8) * k, (cy + R + 8) * k), a0, a0 + 360 * cuenta,
              fill=(*ORO, 255), width=12 * k)
        flecha_hud(d, cx, cy, 128, k, (*JADE_CLARO, 255))
        # la tecla
        tx, ty, L = cx + R * 0.72, cy + R * 0.62, 66
        d.rounded_rectangle(((tx - L / 2 + 4) * k, (ty - L / 2 + 6) * k, (tx + L / 2 + 4) * k, (ty + L / 2 + 6) * k),
                            12 * k, fill=(4, 10, 6, 220))
        d.rounded_rectangle(((tx - L / 2) * k, (ty - L / 2) * k, (tx + L / 2) * k, (ty + L / 2) * k), 12 * k,
                            fill=(236, 244, 232, 255), outline=(*ORO, 255), width=4 * k)
        f = _fuente(46 * k)
        w = d.textlength('A', font=f)
        d.text((tx * k - w / 2, (ty - 36) * k), 'A', font=f, fill=(20, 40, 26, 255))
        # los aciertos seguidos
        paso = 40
        x0 = cx - paso * (total - 1) / 2
        for i in range(total):
            px, py, r_ = x0 + i * paso, cy + R + 48, 13
            rombo = [(px * k, (py - r_) * k), ((px + r_) * k, py * k), (px * k, (py + r_) * k), ((px - r_) * k, py * k)]
            if i < aciertos:
                d.polygon(rombo, fill=(*ORO, 255), outline=(255, 250, 220, 255))
            else:
                d.polygon(rombo, fill=(8, 24, 14, 200), outline=(*JADE_CLARO, 200))
    capa_fina(img, dib)
    texto_sombra(img, (cx - R - 170, cy - R - 70), 'PANTALLA DEL JINETE', 28, JADE_CLARO)
    texto_sombra(img, (cx - R - 160, cy - 52), '¡A!', 76, ORO_CLARO)
    texto_sombra(img, (cx - R - 172, cy + R + 30), 'SEGUIDOS', 26, ORO_CLARO)


def arcos(img, cam, p, radio, a0, n=3, color=BLANCO):
    """Arcos de sacudida (como en un tebeo) alrededor del punto p del mundo."""
    sx, sy, z = cam.proyectar(p)
    if z < 0.5:
        return
    sx, sy = sx / SS, sy / SS

    def dib(d, k):
        for i in range(n):
            r_ = radio + i * radio * 0.28
            caja = ((sx - r_) * k, (sy - r_) * k, (sx + r_) * k, (sy + r_) * k)
            d.arc(caja, a0 - 22 + i * 4, a0 + 22 - i * 4, fill=(6, 18, 10, 150), width=7 * k)
            d.arc(caja, a0 - 22 + i * 4, a0 + 22 - i * 4, fill=(*color, 230), width=4 * k)
    capa_fina(img, dib)


def monta(W=1600, H=900, fase=2, rajang_xz=(2.0, 7.0), mira=(1.0, -0.2), ojo=(-1.0, 8.0, -7.6),
          objetivo=(-0.8, 5.7, 5.0), fov=64, nombre='monta', jugadores=((-2.6, 3.6), (1.6, 3.4)), hud=(1370, 300),
          silla=(17.0, -31.0, -66.0), cabeza=(-30, 8, -14), halo=0.15, alza=16.0):
    rx, rz = rajang_xz                                 # su pecho
    g = rm.guinada_hacia(*mira)
    # corcovea: alzado sobre las de atras, las de delante en alto y la cabeza
    # vuelta por encima del hombro hacia el jinete
    pose = ra.sumar(ra.pose_en('TERREMOTO', 0.6), ra.cuerpo(x=alza, z=8, baja=alza * 0.45),
                    ra.cabeza(y=cabeza[0], z=cabeza[1], boca=8, cuello_y=cabeza[2]),
                    ra.cola(sube=-6, lado=-40, fase=0.0, onda=0))
    # el jinete, agarrado al borde del lomo del lado de la camara (en el marco
    # del cuerpo de Rajang, en pixeles: Y abajo, el frente a -Z)
    Mc = matriz_pieza(pose, 'cuerpo', rx, rz, g, fase)
    cerca = [np.linalg.norm((Mc @ np.array([20.0 * s_, -30, silla[2], 1]))[:3] - np.array(ojo)) for s_ in (1, -1)]
    lado = 1 if cerca[0] < cerca[1] else -1
    silla = (silla[0] * lado, silla[1], silla[2])
    Mj = Mc @ vr.T(*silla) @ vr.Rz(math.radians(-12 * lado)) @ vr.Rx(math.radians(22)) @ vr.T(0, -12, 0)
    jinete = (Mj @ np.array([0, -2, 0, 1.0]))[:3]
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(26, 70)
    escena = rm.plaza_templo(26, 70, 44) + ts.piramide(-16, 46) + ts._arboles((22, 34, 16, 10), (-30, 30, 18, 11),
                                                                             (30, 10, 15, 9))
    ts.dibujar_mundo(lz, cam, escena, niebla, fase)
    rm.rajang(lz, cam, rx, rz, g, pose, fase, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    qs_jinete = jugador2(lz, cam, Mj, pose=AGARRADO, niebla=niebla, luces=LUCES_JINETE, amb=(0.42, 0.44, 0.36))
    # la espada clavada delante de el: el puno en sus manos y la hoja hundida en el lomo
    manos = (mano_jugador(Mj, AGARRADO, 'bi') + mano_jugador(Mj, AGARRADO, 'bd')) / 2
    m_l = np.linalg.inv(Mc) @ np.array([*manos, 1.0])
    entra = (Mc @ np.array([31.0 * lado, -27.0, m_l[2] - 3.0, 1.0]))[:3]      # donde entra la hoja
    Me = matriz_hacia(manos, (Mc @ np.array([20.0 * lado, -10.0, m_l[2] - 6.0, 1.0]))[:3], 1.8)
    herida = entra
    qs_espada = nm.quads(nodo_espada(off=(0, 0, 0)), {}, Me)
    nm.dibujar(lz, cam, qs_espada, LUCES_JINETE, (0.42, 0.44, 0.36), niebla, brillo=1.6)
    # los dos de abajo, mirando arriba y pegandole en las patas de atras
    golpes = [punto_rajang(pose, 'tibia_izq' if lado > 0 else 'tibia_der', rx, rz, g, (0, 6, -12), fase),
              (Mc @ np.array([20.0 * lado, 40.0, -70.0, 1.0]))[:3]]
    for i, (x, z) in enumerate(jugadores):
        b = golpes[i % 2]
        jugador2(lz, cam, matriz_jugador(x, z, rm.guinada_hacia(b[0] - x, b[2] - z)), pose=GOLPE, espada=True,
                 rot_espada=(-30, 0, 0), niebla=niebla)
    # lo que brilla: el jinete, la herida de la espada, los golpes de abajo
    ta.cartel(lz, cam, jinete, 2.0, HALO_ORO, halo)
    ta.cartel(lz, cam, herida, 1.8, HALO_ORO, 0.9)
    ta.cartel(lz, cam, herida, 1.2, CHISPA, 1.1)
    blanco = tex_halo((255, 250, 220), (255, 255, 255))
    for p in golpes:
        ta.cartel(lz, cam, p, 0.8, CHISPA, 1.0)
        ta.cartel(lz, cam, p, 1.1, blanco, 0.45)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 81)
    ta.polvo_en(img, cam, [(p[0], 0.3, p[2], 2.2) for p in (punto_rajang(pose, n, rx, rz, g, fase=fase)
                                                             for n in ('pie_izq', 'pie_der'))], SS, (128, 110, 80), 82)
    # el corcoveo: arcos de sacudida junto a las patas en alto, la grupa y el jinete
    for pieza, r_, a0 in (('mano_izq', 60, 150), ('mano_der', 80, 160), ('cola0', 70, -40)):
        p = punto_rajang(pose, pieza, rx, rz, g, fase=fase)
        arcos(img, cam, p, r_ * W / 1600, a0, 3)
    arcos(img, cam, jinete + np.array([0, 0.6, 0]), 70 * W / 1600, 200, 2, color=ORO_CLARO)
    contorno(img, cam, qs_jinete + qs_espada, ORO_CLARO, grosor=max(1, round(5 * W / 1600)), halo=1.0, lz=lz)
    k = W / 1600
    pantalla_jinete(img, hud[0] * k, hud[1] * k)
    rotulo(img, cam, jinete + np.array([0, 0.9, 0]), 'EL JINETE', 110, -40, 46, ORO_CLARO)
    pata_d = punto_rajang(pose, 'mano_izq', rx, rz, g, fase=fase)
    rotulo(img, cam, pata_d, 'CORCOVEA PARA TIRARLO', -30, 90, 30, BLANCO)
    x, z = (np.array(jugadores[0]) + np.array(jugadores[1])) / 2
    rotulo(img, cam, (x, 0.0, z), 'LOS DEMÁS LE PEGAN', 0, 18, 30, JADE_CLARO, linea=False, centro=True)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  6. Suelo que se Hunde
#
#  La plaza se ha vuelto losas de jade de 2x2 sobre un foso de pinchos. El
#  que corre deja detras un rastro: la que acaba de pisar, agrietada; la de
#  antes, rota y encendida; la de antes, cayendo; y las demas, ya huecos.
#  Otro salta un hueco. Al fondo, Rajang ruge en su peana, inmune (los aros
#  de runas), y lanza zarpazos de roca.
# ----------------------------------------------------------------------
LOSA_PASO = 2.0
LOSA_LADO = 1.86
Y_FOSO = -7.0
LUCES_FOSO = [((-0.3, 1.0, -0.2), (0.55, 0.7, 0.55), 0.55, 'llave')]
AMB_FOSO = (0.07, 0.09, 0.07)
AMBAR = (255, 178, 70)


def _grietas_mascara(n, cuantas, grueso, semilla):
    """Grietas que salen de un punto (algo descentrado) hacia los bordes."""
    r = random.Random(semilla)
    img = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(img)
    cx, cy = n * r.uniform(0.38, 0.62), n * r.uniform(0.38, 0.62)
    for k in range(cuantas):
        a = TAU * k / cuantas + r.uniform(-0.3, 0.3)
        x, y, w = cx, cy, grueso
        while 0 < x < n and 0 < y < n:
            a += r.uniform(-0.5, 0.5)
            x1, y1 = x + math.cos(a) * n * 0.07, y + math.sin(a) * n * 0.07
            d.line((x, y, x1, y1), fill=255, width=max(1, int(w)))
            if r.random() < 0.25:
                a2 = a + r.choice([-1, 1]) * r.uniform(0.6, 1.1)
                d.line((x1, y1, x1 + math.cos(a2) * n * 0.1, y1 + math.sin(a2) * n * 0.1), fill=255,
                       width=max(1, int(w * 0.6)))
            x, y, w = x1, y1, max(1.0, w * 0.9)
    return np.array(img).astype(float) / 255


def tex_losa_jade(grietas=0, n=64, semilla=11):
    """La losa de jade de la plaza nueva: piedra de jade con bisel, un marco
    tallado y el ojo en medio; con grietas (1 o 2), rajada y encendida en ambar."""
    n1 = ta._fbm2(n, n, (4, 4), semilla)
    n2 = ta._fbm2(n, n, (16, 16), semilla + 1)
    col = ta._mezcla(ta.JADE, 0.58 + 0.3 * (n1 - 0.5) + 0.2 * (n2 - 0.5))
    yy, xx = np.mgrid[0:n, 0:n]
    b = n // 14
    col[(yy < b) | (xx < b)] = col[(yy < b) | (xx < b)] * 1.3 + 14
    col[(yy >= n - b) | (xx >= n - b)] *= 0.55
    m = np.zeros((n, n), bool)
    c = n // 5
    m[c:c + 2, c:n - c] = m[n - c - 2:n - c, c:n - c] = True
    m[c:n - c, c:c + 2] = m[c:n - c, n - c - 2:n - c] = True
    g = n // 3
    o = (n - g) // 2
    m[o:o + g, o:o + g] |= ta._glifo(1, g, g)
    col[m] *= 0.55
    em = None
    if grietas:
        gm = _grietas_mascara(n, 4 if grietas == 1 else 8, 2.0 if grietas == 1 else 3.5, semilla + grietas * 7)
        col = col * (1 - gm[..., None] * 0.85)
        halo = np.array(Image.fromarray((gm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(float) / 255
        k = 0.55 if grietas == 1 else 1.0
        em = _rgba(np.ones((n, n, 3)) * np.array(AMBAR), np.clip(gm * k + halo * 0.6 * k, 0, 1))
        col = np.maximum(col, gm[..., None] * np.array(AMBAR) * (0.5 if grietas == 1 else 0.85))
    return _rgba(col, np.ones((n, n))), em


ts.SELVA.update({'losa_jade': tex_losa_jade(0)[0], 'losa_jade_g1': tex_losa_jade(1), 'losa_jade_g2': tex_losa_jade(2)})


def losa_jade(cx, cz, estado, M=None):
    """Una losa de 2x2 (quads de mundo): la cara de arriba con su textura y los
    lados de jade oscuro; M (opcional) la mueve (cayendo)."""
    h = LOSA_LADO / 2
    mat = {'sana': 'losa_jade', 'grieta': 'losa_jade_g1', 'rota': 'losa_jade_g2', 'cae': 'losa_jade_g2'}[estado]
    arriba = [([(cx - h, 0.0, cz - h), (cx + h, 0.0, cz - h), (cx + h, 0.0, cz + h), (cx - h, 0.0, cz + h)],
               [(0, 0), (1, 0), (1, 1), (0, 1)], mat)]
    qs = arriba + ts.caja(cx - h, -0.55, cz - h, LOSA_LADO, 0.54, LOSA_LADO, 'jade_osc')
    if M is not None:
        qs = [([tuple((M @ np.array([*p, 1.0]))[:3]) for p in P], UV, m) for P, UV, m in qs]
    return qs


def peana(x, z, w, d, alto):
    """La peana de piedra del templo, con la cenefa de oro arriba y un escalon."""
    return (ts.caja(x - w / 2 - 1, -0.6, z - d / 2 - 1, w + 2, 1.2, d + 2, 'templo') +
            ts.caja(x - w / 2, 0.6, z - d / 2, w, alto - 0.9, d, 'templo') +
            ts.caja(x - w / 2 - 0.2, alto - 0.35, z - d / 2 - 0.2, w + 0.4, 0.35, d + 0.4, 'oro'))


SALTO = {'cabeza': {'rot': (-10, 0, 0)}, 'bi': {'rot': (-150, 0, -30)}, 'bd': {'rot': (-140, 0, 30)},
         'pi': {'rot': (-70, 0, 0)}, 'pd': {'rot': (10, 0, 0)}}


def _caja_arco(cam, p, alto=1.8, ancho=2.4):
    """La caja (en la foto) del arco de un salto sobre p (x, z)."""
    a = cam.proyectar((p[0] + ancho / 2, 0.6, p[1]))
    b = cam.proyectar((p[0] - ancho / 2, 0.6 + alto * 2, p[1]))
    xs, ys = sorted((a[0] / SS, b[0] / SS)), sorted((a[1] / SS, b[1] / SS))
    return (xs[0], ys[0], xs[1], ys[1] + (ys[1] - ys[0]))


def suelo(W=1600, H=900, fase=3, ojo=(0.5, 6.6, -8.6), objetivo=(-1.0, 1.0, 10.0), fov=58, nombre='suelo'):
    # la camara mira hacia +z: en la foto, +x queda a la izquierda
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(30, 80)
    R = 25.0
    fuera = [q for q in rm.plaza_templo(26, 70, 44) if q[2] != 'plaza']
    escena = fuera + ts._arboles((-32, 26, 17, 10), (32, 30, 18, 11), (-36, -4, 15, 9), (36, 0, 15, 9))
    ts.dibujar_mundo(lz, cam, escena, niebla, fase)
    # el foso: el fondo oscuro
    foso = []
    for gx in range(-26, 26, 4):
        for gz in range(-26, 40, 4):
            foso.append(([(gx, Y_FOSO, gz), (gx + 4, Y_FOSO, gz), (gx + 4, Y_FOSO, gz + 4), (gx, Y_FOSO, gz + 4)],
                         [(0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5)], 'roca_tierra'))
    ts.dibujar_mundo(lz, cam, foso, niebla, fase, LUCES_FOSO, AMB_FOSO)
    # el rastro del que corre (de lo mas viejo a lo mas nuevo) y los huecos de antes
    corre = np.array([1.4, 1.0])
    rastro = [(-9, 11), (-9, 9), (-7, 9), (-7, 7), (-7, 5), (-7, 3), (-7, 1), (-5, 1), (-3, 1), (-1, 1), (1, 1)]
    estados = {}
    for (x, z) in rastro[:-3]:
        estados[(x, z)] = 'hueco'
    estados[rastro[-3]] = 'cae'
    estados[rastro[-2]] = 'rota'
    estados[rastro[-1]] = 'grieta'
    r = random.Random(23)
    huecos_viejos = [(7, 5), (9, 7), (3, 9), (1, 13), (9, 11), (11, 3), (-3, 15), (13, 11), (-15, 9), (7, 15),
                     (-13, 15), (15, 5), (-17, 3), (11, -3), (-15, -5), (5, 13), (-11, -3), (3, -5), (-3, 7)]
    for h_ in huecos_viejos:
        estados[h_] = 'hueco'
    ped = (-1.0, 27.0, 12.0, 18.0, 2.6)                 # la peana: x, z, ancho, fondo, alto
    tiles, pinchos = [], []
    for i in range(-13, 13):
        for j in range(-13, 20):
            x, z = i * LOSA_PASO + 1, j * LOSA_PASO + 1
            if math.hypot(x, z - 4) > R:
                continue
            if abs(x - ped[0]) < ped[2] / 2 + 1.2 and abs(z - ped[1]) < ped[3] / 2 + 1.2:
                continue
            e = estados.get((x, z), 'sana')
            if e == 'hueco':
                for k in range(3):
                    pinchos += ta.pico(x + r.uniform(-0.6, 0.6), z + r.uniform(-0.6, 0.6), r.uniform(5.0, 6.2),
                                       r.uniform(0.35, 0.55), (r.uniform(-0.1, 0.1), r.uniform(-0.1, 0.1)),
                                       semilla=100 + i * 37 + j * 11 + k, extras=False)
                continue
            if e == 'cae':
                M = vr.T(x, -1.2, z) @ vr.Rz(-0.75) @ vr.Rx(0.35) @ vr.T(-x, 0, -z)
                tiles += losa_jade(x, z, e, M)
                continue
            M = vr.T(0, -0.12, 0) if e == 'rota' else None
            tiles += losa_jade(x, z, e, M)
    pinchos = [(P + np.array([0.0, Y_FOSO, 0.0]), UV, m) for P, UV, m in pinchos]
    ta.dibujar(lz, cam, pinchos, [((-0.4, 1.0, -0.5), (1.0, 0.85, 0.65), 0.75, 'llave')], (0.16, 0.16, 0.13), niebla)
    ts.dibujar_mundo(lz, cam, tiles + peana(*ped), niebla, fase)
    # los jugadores: el que corre (sin parar) y el que salta un hueco
    jugador2(lz, cam, matriz_jugador(corre[0], corre[1], rm.guinada_hacia(1, -0.12)), pose=CORRER, niebla=niebla)
    salta = np.array([7.0, 5.0])
    jugador2(lz, cam, matriz_jugador(salta[0], salta[1], rm.guinada_hacia(0.2, 1), y=1.4), pose=SALTO,
             niebla=niebla)
    # Rajang en la peana, rugiendo, algo de lado
    pose = ra.sumar(ra.pose_en('RUGIDO', 0.6), ra.cabeza(y=-10))
    g_r = rm.guinada_hacia(0.7, -1)
    rajang_en(lz, cam, ped[0] + 2.0, ped[4], ped[1] - 3.0, g_r, pose, fase, niebla=niebla)
    # los zarpazos de roca, de camino
    rocas = []
    vuelo = [(np.array([6.0, 3.0, 11.0]), 0.5), (np.array([-6.0, 3.6, 10.0]), 0.42)]
    for k, (p, t) in enumerate(vuelo):
        for j in range(4):
            rocas += ta.roca_cubica(*(p + np.array([r.uniform(-0.5, 0.5), r.uniform(-0.3, 0.3), r.uniform(-0.5, 0.5)])),
                                    t * r.uniform(0.6, 1.1), semilla=600 + k * 10 + j)
    ta.dibujar(lz, cam, rocas, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    # lo que brilla: la inmunidad (los aros de runas), el foso y las grietas
    ts.aro_runas(lz, cam, ped[0] - 1.0, ped[4] + 2.2, ped[1] - 1.0, 7.0, 0.7, 1.0)
    ts.aro_runas(lz, cam, ped[0] - 1.0, ped[4] + 5.6, ped[1] - 1.0, 6.0, 0.5, 0.8, giro=0.3)
    halo_ambar = tex_halo(AMBAR, (255, 236, 190))
    for (x, z), e in estados.items():
        if e == 'hueco' and math.hypot(x - corre[0], z - corre[1]) < 16:
            ta.calco(lz, cam, x, z, 1.3, halo_ambar, 0.35, y=Y_FOSO + 0.05)
    for (x, z) in rastro[-3:-1]:
        ta.cartel(lz, cam, (x, 0.4, z), 1.4, halo_ambar, 0.35)
    # el camino que ha hecho: una linea de puntos por el rastro
    for (x0, z0), (x1, z1) in zip(rastro[:-1], rastro[1:]):
        for u in (0.25, 0.75):
            ta.calco(lz, cam, x0 + (x1 - x0) * u, z0 + (z1 - z0) * u, 0.18, halo_ambar, 0.9, y=0.06)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 91, oscuro=0.25, rayos=False)
    ta.polvo_en(img, cam, [(rastro[-3][0], -0.5, rastro[-3][1], 1.5), (ped[0], ped[4], ped[1] - 3, 4.0)], SS,
                (128, 110, 80), 92)
    for k, (p, t) in enumerate(vuelo):
        rm.lineas_movimiento(img, cam, p, p - np.array([ped[0], ped[4] + 4, ped[1] - 4]), 10, 4.0, 93 + k,
                             (230, 220, 190), 3)
    rm.lineas_movimiento(img, cam, (corre[0] - 0.9, 1.1, corre[1]), (1, 0, -0.12), 10, 2.6, 96)
    rm.lineas_movimiento(img, cam, (salta[0], 1.9, salta[1] - 0.8), (0.1, 0.5, 1), 6, 1.6, 97)
    rotulo(img, cam, (corre[0], 2.2, corre[1]), '¡NO PARES!', 0, -120, 56, ORO_CLARO, linea=False, centro=True)
    rotulo(img, cam, (rastro[-2][0], 0.0, rastro[-2][1] - 0.7), 'LA LOSA QUE PISAS CAE 1 S DESPUÉS', -20, 80, 30,
           (255, 214, 150))
    hx, hz = rastro[-7]
    rotulo(img, cam, (hx, -0.8, hz + 0.7), 'FOSO DE PINCHOS', 120, 60, 30, BLANCO)
    p, _ = vuelo[0]
    rotulo(img, cam, p + np.array([0, 0.6, 0]), 'LANZA ROCAS', -40, -70, 26, BLANCO)
    rotulo(img, cam, (ped[0] - 2.0, ped[4] + 7.0, ped[1] - 3.0), 'INMUNE EN SU PEANA', -80, -40, 32, JADE_CLARO)
    rotulo(img, cam, (salta[0], 2.6, salta[1]), 'SALTA LOS HUECOS', 60, -100, 28, BLANCO)
    pildora(img, W - 110, 52, '15 S', 34, ORO_CLARO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  7. Lazos de Liana
#
#  Agazapado para la Embestida (la flecha en el suelo) y con las cuatro patas
#  encendidas. Tres jugadores tiran cada uno de una liana tensa atada a una
#  pata (el nudo de oro); un cuarto corre con otra liana en la mano, junto a
#  las que brotan del suelo.
# ----------------------------------------------------------------------
VERDE_LIANA = (120, 230, 90)


def tex_liana(w=48, h=96, semilla=5):
    """La liana a lo largo (v): dos hebras retorcidas y hojas a los lados,
    recortadas (alfa 0 fuera)."""
    r = random.Random(semilla)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hojas = [(0.18, -1), (0.45, 1), (0.72, -1), (0.95, 1)]
    for v, lado in hojas:
        cy = v * h
        cx = w / 2 + lado * w * 0.26
        col = r.choice([(96, 200, 66), (118, 220, 78), (84, 184, 58)])
        d.ellipse((cx - w * 0.2, cy - h * 0.09, cx + w * 0.2, cy + h * 0.09), fill=(*col, 255))
        d.line((w / 2, cy - h * 0.06, cx + lado * w * 0.12, cy + h * 0.02), fill=(40, 96, 32, 255), width=2)
    for k in range(2):
        pts = []
        for i in range(h + 1):
            u = 0.5 + 0.13 * math.sin(i / h * TAU * 3 + k * math.pi)
            pts.append((u * w, i))
        d.line(pts, fill=((70, 120, 44, 255) if k else (96, 150, 56, 255)), width=max(3, w // 6))
    d.line([(w / 2, 0), (w / 2, h)], fill=(130, 200, 80, 255), width=2)
    return np.array(img)


LIANA = tex_liana()


def liana(lz, cam, puntos, ancho=0.32, luz=(1.05, 1.1, 1.0), paso=0.9):
    """Una liana (cinta de cara a la camara, opaca y recortada) por una lista
    de puntos del mundo; las hojas se repiten cada 'paso' bloques."""
    v = 0.0
    luz = np.array(luz)
    for p0, p1 in zip(puntos[:-1], puntos[1:]):
        p0, p1 = np.array(p0, float), np.array(p1, float)
        d = p1 - p0
        L = np.linalg.norm(d)
        lado = np.cross(d, cam.ojo - (p0 + p1) / 2)
        lado = lado / max(np.linalg.norm(lado), 1e-9) * ancho
        P = [p0 - lado, p0 + lado, p1 + lado, p1 - lado]
        UV = [(0, v), (1, v), (1, v + L / paso), (0, v + L / paso)]
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], LIANA, luz, None, None, envolver=True)
        v += L / paso


def curva(p0, p1, combo, n=12):
    """Una curva de p0 a p1 que se comba 'combo' bloques hacia abajo en medio."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    return [p0 + (p1 - p0) * (i / n) - np.array([0, combo * math.sin(math.pi * i / n), 0]) for i in range(n + 1)]


TIRAR = {'cabeza': {'rot': (-6, 0, 0)}, 'bi': {'rot': (-78, 0, -4)}, 'bd': {'rot': (-84, 0, 4)},
         'pi': {'rot': (26, 0, 0)}, 'pd': {'rot': (-30, 0, 0)}}
CORRER_LIANA = {'bi': {'rot': (44, 0, 0)}, 'bd': {'rot': (-70, 0, 10)}, 'pi': {'rot': (-40, 0, 0)},
                'pd': {'rot': (38, 0, 0)}}


def lazos(W=1600, H=900, fase=2, ojo=(-2.5, 6.5, -10.0), objetivo=(-0.8, 1.8, 6.0), fov=62, nombre='lazos'):
    # la camara mira hacia +z: en la foto, +x queda a la izquierda
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(30, 80)
    escena = rm.plaza_templo(26, 70, 44) + ts.piramide(-14, 44) + ts._arboles((26, 30, 16, 10), (-30, 28, 18, 11),
                                                                             (32, 4, 15, 9))
    ts.dibujar_mundo(lz, cam, escena, niebla, fase)
    rx, rz = 0.0, 8.0
    mira = np.array([1.0, -0.3])
    g = rm.guinada_hacia(*mira)                        # mira hacia la izquierda de la foto y algo hacia aqui
    fwd = mira / np.linalg.norm(mira)
    pose = ra.sumar(ra.pose_en('EMBESTIDA_AVISO', 0.95), ra.cabeza(y=-10))
    rm.rajang(lz, cam, rx, rz, g, pose, fase, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)

    def nudo(a, b):
        return (punto_rajang(pose, a, rx, rz, g, fase=fase) + punto_rajang(pose, b, rx, rz, g, fase=fase)) / 2
    patas = {'del_cerca': nudo('antebrazo_izq', 'mano_izq'), 'del_lejos': nudo('antebrazo_der', 'mano_der'),
             'tras_cerca': nudo('tarso_izq', 'pie_izq'), 'tras_lejos': nudo('tarso_der', 'pie_der')}
    # los tres que tiran, cada uno de una pata, y el que corre a por la cuarta
    sitios = {'del_cerca': (5.6, -0.2), 'del_lejos': (11.5, 4.0), 'tras_lejos': (-13.0, 15.5)}
    tiran = []
    for n, (qx, qz) in sitios.items():
        p = patas[n]
        Mj = matriz_jugador(qx, qz, rm.guinada_hacia(p[0] - qx, p[2] - qz), inclina=16)
        jugador2(lz, cam, Mj, pose=TIRAR, niebla=niebla)
        manos = (mano_jugador(Mj, TIRAR, 'bi') + mano_jugador(Mj, TIRAR, 'bd')) / 2
        tiran.append((n, np.array([qx, qz]), manos))
    libre = 'tras_cerca'
    pl = patas[libre]
    corre = np.array([-9.6, 0.4])
    g_c = rm.guinada_hacia(pl[0] - corre[0], pl[2] - corre[1])
    Mc_ = matriz_jugador(corre[0], corre[1], g_c)
    jugador2(lz, cam, Mc_, pose=CORRER_LIANA, niebla=niebla)
    mano_c = mano_jugador(Mc_, CORRER_LIANA, 'bd')
    # las lianas: tensas (rectas) de las manos a la pata, con un cabo suelto detras
    for n, q, manos in tiran:
        p = patas[n]
        atras = manos + (manos - p) / np.linalg.norm(manos - p) * 1.8
        atras[1] = 0.05
        liana(lz, cam, [p, manos], ancho=0.46)
        liana(lz, cam, curva(manos, atras, 0.2, 5), ancho=0.4)
    detras = np.array([corre[0] - 0.7, 0.05, corre[1] - 1.5])
    liana(lz, cam, curva(mano_c, detras, 0.35, 8), ancho=0.42)
    brotes = []
    for k, (bx, bz, alto, fase_b) in enumerate(((-11.6, 3.6, 2.2, 0.0), (-13.2, 2.4, 1.7, 1.7), (-10.2, 5.0, 1.5, 3.1))):
        b = np.array([bx, 0.0, bz])
        pts = [b + np.array([0.45 * math.sin(i * 0.8 + fase_b), alto * i / 8, 0.3 * math.cos(i * 0.6 + fase_b)])
               for i in range(9)]
        liana(lz, cam, pts, ancho=0.38)
        brotes.append(b)
    # lo que brilla: la flecha, las patas (las atadas, con el nudo de oro) y las lianas tensas
    ini = np.array([rx, rz]) + fwd * 6.0
    fin = np.array([rx, rz]) + fwd * 26.0
    rm.calco_tramo(lz, cam, ini[0], ini[1], fin[0], fin[1], 3.0, rm.FLECHA, 1.0)
    halo_verde = tex_halo(JADE, JADE_CLARO)
    for n, p in patas.items():
        ta.calco(lz, cam, p[0], p[2], 1.9, ts.ARO_AVISO, 1.3)
        ta.cartel(lz, cam, p + np.array([0, 0.3, 0]), 2.2 if n == libre else 1.6, halo_verde, 1.0 if n == libre else 0.45)
    for n, q, manos in tiran:
        p = patas[n]
        ts.aro_runas(lz, cam, p[0], p[1], p[2], 1.05, 0.5, 1.4, n=24)
        ta.cinta(lz, cam, p, manos, 0.55, ts.LINEA, 0.5)
    for b in brotes:
        ta.calco(lz, cam, b[0], b[2], 1.0, halo_verde, 0.6)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 101)
    ta.polvo_en(img, cam, [(p[0], 0.2, p[2], 1.4) for p in patas.values()], SS, (128, 110, 80), 102)
    rm.lineas_movimiento(img, cam, (corre[0] - 0.5, 1.0, corre[1] - 0.5), (pl[0] - corre[0], 0, pl[2] - corre[1]), 8,
                         2.2, 103)
    pildora(img, W / 2, 50, '3 PATAS ATADAS: TROPIEZA Y CAE', 36, ORO_CLARO)
    n0, q0, m0 = tiran[0]
    medio = patas[n0] + (m0 - patas[n0]) * 0.55
    rotulo(img, cam, medio, 'LIANA TENSA (A 12 BLOQUES COMO MUCHO)', -10, 130, 28, JADE_CLARO)
    rotulo(img, cam, patas[libre] + np.array([0, 0.6, 0]), 'PATA QUE BRILLA', 30, -120, 30, JADE_CLARO)
    rotulo(img, cam, patas['del_cerca'] + np.array([0, 0.4, 0]), 'ATADA', -40, -150, 32, ORO_CLARO)
    rotulo(img, cam, brotes[2] + np.array([0, 1.4, 0]), 'COGE UNA LIANA DEL SUELO', 40, -110, 28, BLANCO)
    fl = np.array([rx, 0.05, rz]) + np.array([fwd[0], 0, fwd[1]]) * 15
    rotulo(img, cam, fl, 'LA EMBESTIDA NO SALE', 30, 60, 28, BLANCO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  8. Glifos del Templo
#
#  Columnas del templo en corro, cada una con su glifo de jade encendido (seis
#  distintos, todos con la misma luz). El Vidente (con el contorno de oro)
#  senala uno y lo dice; otro golpea el glifo de la espiral; el del jaguar ya
#  esta roto. Arriba, lo que ve el Vidente en su pantalla: los 3 verdaderos.
# ----------------------------------------------------------------------
GLIFOS = ('jaguar', 'ojo', 'espiral', 'sol', 'piramide', 'luna')
VERDADEROS = ('jaguar', 'espiral', 'sol')


def mascara_glifo(nombre, n=128):
    """Los seis glifos de las columnas (mascara booleana n x n, trazo grueso)."""
    img = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(img)
    k = n / 128
    w = int(11 * k)
    if nombre == 'jaguar':
        m = ta._jaguar_glifo(n, n)
        img = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(max(3, int(5 * k) | 1)))
        return np.array(img) > 127
    if nombre == 'ojo':
        d.ellipse((10 * k, 34 * k, 118 * k, 94 * k), outline=255, width=w)
        d.ellipse((46 * k, 46 * k, 82 * k, 82 * k), fill=255)
    elif nombre == 'espiral':
        pts, x, y, L, dirs = [], 64 * k, 64 * k, 12 * k, [(1, 0), (0, 1), (-1, 0), (0, -1)]
        pts.append((x, y))
        for i in range(9):
            dx, dy = dirs[i % 4]
            x, y = x + dx * L, y + dy * L
            pts.append((x, y))
            L += 12 * k
        d.line(pts, fill=255, width=w, joint='curve')
    elif nombre == 'sol':
        d.ellipse((40 * k, 40 * k, 88 * k, 88 * k), fill=255)
        for i in range(8):
            a = TAU * i / 8
            d.line((64 * k + math.cos(a) * 34 * k, 64 * k + math.sin(a) * 34 * k, 64 * k + math.cos(a) * 58 * k,
                    64 * k + math.sin(a) * 58 * k), fill=255, width=w)
    elif nombre == 'piramide':
        for i in range(4):
            y0 = (100 - i * 22) * k
            x0, x1 = (14 + i * 15) * k, (114 - i * 15) * k
            d.rectangle((x0, y0, x1, y0 + 18 * k), fill=255)
        d.rectangle((56 * k, 104 * k, 72 * k, 122 * k), fill=0)
    elif nombre == 'luna':
        d.ellipse((14 * k, 14 * k, 114 * k, 114 * k), fill=255)
        d.ellipse((40 * k, 4 * k, 128 * k, 104 * k), fill=0)
    return np.array(img) > 127


def tex_placa(nombre, roto=False, n=96):
    """La placa de la columna: piedra verde oscura con el glifo tallado (lo
    opaco) y, aparte, su brillo de jade (None si esta roto)."""
    n1 = ta._fbm2(n, n, (4, 4), 21)
    n2 = ta._fbm2(n, n, (16, 16), 22)
    col = ta._mezcla(('16261a', '1e3424', '28442e', '345838', '3e6a44'), 0.5 + 0.5 * (n1 - 0.5) + 0.25 * (n2 - 0.5))
    m = np.zeros((n, n), bool)
    g = int(n * 0.74)
    o = (n - g) // 2
    m[o:o + g, o:o + g] = mascara_glifo(nombre, g)
    b = max(2, n // 24)
    marco = np.zeros((n, n), bool)
    marco[b:2 * b, b:n - b] = marco[n - 2 * b:n - b, b:n - b] = True
    marco[b:n - b, b:2 * b] = marco[b:n - b, n - 2 * b:n - b] = True
    col[m | marco] *= 0.5
    if roto:
        gm = _grietas_mascara(n, 7, 3.0, 5)
        col = col * (1 - gm[..., None] * 0.8) * 0.75
        return _rgba(col, np.ones((n, n))), None
    halo = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(n / 28))).astype(float) / 255
    brillo = _rgba(np.ones((n, n, 3)) * np.array(JADE), np.clip(m * 0.95 + halo * 0.7 + marco * 0.4, 0, 1))
    col[m] = col[m] * 0.4 + np.array(JADE) * 0.5
    return _rgba(col, np.ones((n, n))), brillo


def columna_templo(cx, cz, giro, alto=7.6, ancho=2.8):
    """Columna cuadrada del templo (quads de mundo) girada 'giro' grados: basa,
    fuste, dos cenefas de oro y el capitel."""
    qs = (ts.caja(-ancho / 2 - 0.35, 0, -ancho / 2 - 0.35, ancho + 0.7, 0.6, ancho + 0.7, 'templo') +
          ts.caja(-ancho / 2, 0.6, -ancho / 2, ancho, alto - 1.2, ancho, 'templo') +
          ts.caja(-ancho / 2 - 0.08, 4.2, -ancho / 2 - 0.08, ancho + 0.16, 0.3, ancho + 0.16, 'oro') +
          ts.caja(-ancho / 2 - 0.08, 0.6, -ancho / 2 - 0.08, ancho + 0.16, 0.25, ancho + 0.16, 'oro') +
          ts.caja(-ancho / 2 - 0.45, alto - 0.6, -ancho / 2 - 0.45, ancho + 0.9, 0.6, ancho + 0.9, 'templo'))
    return _girar(qs, giro, cx, 0.0, cz)


def placa(lz, cam, cx, cz, giro, tex, ancho=2.8, y0=1.25, y1=3.95, brillo=None, k=1.0, niebla=None):
    """La placa del glifo en la cara de la columna que mira al centro (-Z
    local): lo opaco o, con brillo, su luz sumada."""
    h = ancho / 2 - 0.15
    M = vr.T(cx, 0, cz) @ vr.Ry(math.radians(giro))
    P = [(M @ np.array([x, y, -ancho / 2 - 0.03, 1.0]))[:3] for x, y in ((h, y1), (-h, y1), (-h, y0), (h, y0))]
    UV = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for tri in ((0, 1, 2), (0, 2, 3)):
        if brillo is None:
            luz = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), ts.LUCES_SELVA, ts.AMB_SELVA)
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, None, niebla)
        else:
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], brillo, np.ones(3), None, None, aditivo=True,
                         brillo=k)
    return (M @ np.array([0, (y0 + y1) / 2, -ancho / 2 - 0.1, 1.0]))[:3]


def icono_glifo(nombre, tam, color, fondo=None):
    """El glifo como imagen RGBA de tam x tam, del color pedido y con halo."""
    m = mascara_glifo(nombre, tam * 2)
    a = Image.fromarray((m * 255).astype(np.uint8)).resize((tam, tam), Image.LANCZOS)
    halo = a.filter(ImageFilter.GaussianBlur(tam / 14))
    alfa = np.maximum(np.array(a), (np.array(halo) * 0.6).astype(np.uint8)) if fondo is None else np.array(a)
    out = np.zeros((tam, tam, 4), np.uint8)
    out[..., :3] = color
    out[..., 3] = alfa
    return Image.fromarray(out)


def pantalla_vidente(img, x0, y0):
    """Lo que ve el Vidente: los seis glifos; los 3 verdaderos en oro y con su
    marca, los falsos apagados."""
    tam, paso = 74, 104
    w, h = paso * 6 + 40, 236

    def dib(d, k):
        d.rounded_rectangle((x0 * k, y0 * k, (x0 + w) * k, (y0 + h) * k), 18 * k, fill=(6, 16, 10, 200),
                            outline=(*ORO_CLARO, 220), width=3 * k)
        for i, n in enumerate(GLIFOS):
            cx, cy = x0 + 20 + paso * i + paso / 2, y0 + 112
            r_ = 46
            if n in VERDADEROS:
                d.ellipse(((cx - r_) * k, (cy - r_) * k, (cx + r_) * k, (cy + r_) * k), fill=(60, 44, 8, 230),
                          outline=(*ORO, 255), width=5 * k)
            else:
                d.ellipse(((cx - r_) * k, (cy - r_) * k, (cx + r_) * k, (cy + r_) * k), fill=(14, 22, 16, 220),
                          outline=(90, 110, 96, 200), width=3 * k)
    capa_fina(img, dib)
    for i, n in enumerate(GLIFOS):
        cx, cy = x0 + 20 + paso * i + paso / 2, y0 + 112
        ic = icono_glifo(n, tam, ORO_CLARO if n in VERDADEROS else (110, 130, 116), None if n in VERDADEROS else 1)
        img.alpha_composite(ic, (int(cx - tam / 2), int(cy - tam / 2)))
    texto_sombra(img, (x0 + 22, y0 + 10), 'PANTALLA DEL VIDENTE: LOS 3 VERDADEROS', 28, ORO_CLARO)
    f = _fuente(26)
    for i, n in enumerate(GLIFOS):
        cx = x0 + 20 + paso * i + paso / 2
        t = 'SÍ' if n in VERDADEROS else 'NO'
        w_ = ImageDraw.Draw(img).textlength(t, font=f)
        texto_sombra(img, (cx - w_ / 2, y0 + 168), t, 26, ORO if n in VERDADEROS else (150, 170, 156))


def bocadillo(img, cam, p, texto, dx, dy, tam=32):
    """Un bocadillo de dialogo con la punta hacia el punto p del mundo."""
    sx, sy, _ = cam.proyectar(p)
    sx, sy = sx / SS, sy / SS
    f = _fuente(tam)
    w = ImageDraw.Draw(img).textlength(texto, font=f)
    x0, y0 = sx + dx, sy + dy
    x1, y1 = x0 + w + 40, y0 + tam * 1.6

    def dib(d, k):
        punta = [((x0 + 30) * k, y1 * k), ((x0 + 70) * k, y1 * k), (sx * k, (sy - 6) * k)]
        d.polygon(punta, fill=(250, 252, 244, 245), outline=(30, 40, 30, 255))
        d.rounded_rectangle((x0 * k, y0 * k, x1 * k, y1 * k), int(tam * 0.5 * k), fill=(250, 252, 244, 245),
                            outline=(30, 40, 30, 255), width=3 * k)
        d.polygon([((x0 + 32) * k, (y1 - 4) * k), ((x0 + 68) * k, (y1 - 4) * k), ((sx + 2) * k, (sy - 10) * k)],
                  fill=(250, 252, 244, 255))
    capa_fina(img, dib)
    ImageDraw.Draw(img).text((x0 + 20, y0 + tam * 0.1), texto, font=f, fill=(28, 40, 30, 255))


SENALAR = {'cabeza': {'rot': (-10, 0, 0)}, 'bd': {'rot': (-112, 0, 6)}, 'bi': {'rot': (-30, 0, -10)}}
MIRAR = {'cabeza': {'rot': (-8, 30, 0)}, 'bi': {'rot': (-12, 0, -6)}, 'bd': {'rot': (-40, 0, 6)}}


def glifos(W=1600, H=900, fase=3, ojo=(0.5, 7.5, -11.0), objetivo=(0.0, 2.8, 11.0), fov=60, nombre='glifos',
           rajang_xz=(0.5, 14.0), mira_r=(0.55, -1.0), vid=(0.6, 0.6), asigna=None, R=11.0, otro=(-1.4, 6.4)):
    # la camara mira hacia +z: en la foto, +x queda a la izquierda
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 90)
    escena = rm.plaza_templo(26, 70, 44) + ts.piramide(-4, 50) + ts._arboles((-30, 32, 17, 10), (30, 36, 18, 11),
                                                                             (-36, 6, 15, 9), (36, 10, 15, 9))
    ts.dibujar_mundo(lz, cam, escena, niebla, fase)
    cx, cz = 0.0, 11.0
    # el corro: hueco hacia la camara; cada glifo en las cuatro caras de su columna
    asigna = {int(k): v for k, v in (asigna or {300: 'sol', 240: 'espiral', 60: 'ojo', 120: 'jaguar', 0: 'piramide',
                                               180: 'luna'}).items()}
    roto = 'jaguar'
    cols, mundo = {}, []
    for a, n in asigna.items():
        x, z = cx + R * math.cos(math.radians(a)), cz + R * math.sin(math.radians(a))
        giro = rm.guinada_hacia(cx - x, cz - z)
        mundo += columna_templo(x, z, giro)
        cols[n] = (x, z, giro)
    r = random.Random(77)
    x, z, _ = cols[roto]
    for j in range(9):
        a = r.uniform(0, TAU)
        ta.dibujar(lz, cam, ta.roca_cubica(x + math.cos(a) * r.uniform(1.8, 3.2), 0.15, z + math.sin(a) * r.uniform(1.8, 3.2),
                                           r.uniform(0.15, 0.3), semilla=800 + j), ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    ts.dibujar_mundo(lz, cam, mundo, niebla, fase)
    texs = {n: tex_placa(n, roto=(n == roto)) for n in GLIFOS}
    caras = {}
    for n, (x, z, giro) in cols.items():
        mejor = None
        for k in range(4):
            c = placa(lz, cam, x, z, giro + 90 * k, texs[n][0], niebla=niebla)
            normal = c - np.array([x, c[1], z])
            vista = normal @ (cam.ojo - c)
            if mejor is None or vista > mejor[0]:
                mejor = (vista, c, giro + 90 * k)
        caras[n] = mejor
    # Rajang en medio, rugiendo al cielo
    pose = ra.sumar(ra.pose_en('RUGIDO', 0.6), ra.cabeza(y=12))
    rm.rajang(lz, cam, rajang_xz[0], rajang_xz[1], rm.guinada_hacia(*mira_r), pose, fase, ts.LUCES_SELVA, ts.AMB_SELVA,
              niebla)
    # el Vidente, senalando el glifo del sol; el que golpea la espiral; uno que espera junto al ojo
    vid = np.array(vid, float)
    sol = caras['sol'][1]
    Mv = matriz_jugador(vid[0], vid[1], rm.guinada_hacia(sol[0] - vid[0], sol[2] - vid[1]))
    qs_vid = jugador2(lz, cam, Mv, pose=SENALAR, niebla=niebla)
    esp, g_esp = caras['espiral'][1], caras['espiral'][2]
    hacia = np.array([-math.sin(math.radians(g_esp)), -math.cos(math.radians(g_esp))])     # la normal de esa cara
    lado_ = np.array([hacia[1], -hacia[0]])
    gol = np.array([esp[0], esp[2]]) + hacia * 1.7 + lado_ * 1.1
    jugador2(lz, cam, matriz_jugador(gol[0], gol[1], rm.guinada_hacia(esp[0] - gol[0], esp[2] - gol[1])), pose=GOLPE,
             espada=True, rot_espada=(-30, 0, 0), niebla=niebla)
    ojo_c = caras['ojo'][1]
    esp2 = np.array(otro, float)
    jugador2(lz, cam, matriz_jugador(esp2[0], esp2[1], rm.guinada_hacia(vid[0] - esp2[0], vid[1] - esp2[1])),
             pose=MIRAR, espada=True, rot_espada=(-60, 0, 0), niebla=niebla)
    # lo que brilla: los glifos (todos con la misma luz), el golpe, el aro del Vidente
    halo_j = tex_halo(JADE, JADE_CLARO)
    for n, (x, z, giro) in cols.items():
        if texs[n][1] is None:
            continue
        for k in range(4):
            placa(lz, cam, x, z, giro + 90 * k, None, brillo=texs[n][1], k=1.25)
        ta.cartel(lz, cam, caras[n][1], 2.6, halo_j, 0.3)
    golpe = esp + np.array([hacia[0], 0.2, hacia[1]]) * 0.5
    ta.cartel(lz, cam, golpe, 1.4, CHISPA, 1.2)
    ta.cartel(lz, cam, golpe, 2.0, tex_halo((255, 250, 220), (255, 255, 255)), 0.5)
    ta.calco(lz, cam, vid[0], vid[1], 1.6, tex_aro(ORO, grueso=0.08, marcas=10, relleno=0.2), 1.2)
    ta.cartel(lz, cam, (vid[0], 1.0, vid[1]), 1.8, HALO_ORO, 0.35)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 111, oscuro=0.2, rayos=False)
    contorno(img, cam, qs_vid, ORO_CLARO, grosor=4, halo=1.0, lz=lz)
    pantalla_vidente(img, W - 700, 22)
    cabeza_v = (Mv @ np.array([0, -8, 0, 1.0]))[:3]
    bocadillo(img, cam, cabeza_v + np.array([0, 0.3, 0]), '¡EL SOL, LA ESPIRAL Y EL JAGUAR!', -60, -170, 34)
    rotulo(img, cam, (vid[0], 0.1, vid[1]), 'EL VIDENTE', -90, 40, 44, ORO_CLARO)
    rotulo(img, cam, golpe, 'GOLPEA LOS QUE ÉL DICE', 120, 190, 30, BLANCO)
    rotulo(img, cam, ojo_c, 'LOS DEMÁS LOS VEN TODOS IGUALES', -20, -200, 28, JADE_CLARO)
    rotulo(img, cam, caras[roto][1], 'UNO YA ROTO', 60, -90, 28, BLANCO)
    pildora(img, 80, 50, '25 S', 34, ORO_CLARO)
    guardar(img, nombre)


ESCENAS = {'muro': muro, 'idolo': idolo_escena, 'losas': losas, 'acecho': acecho, 'monta': monta, 'suelo': suelo,
           'lazos': lazos, 'glifos': glifos}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
        print('ok', nombre, flush=True)

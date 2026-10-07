"""
Renders de la ficha de las mecanicas nuevas de Aeralis (octubre de 2026: "que
cada jefe haga que los jugadores cooperen con mecanicas suyas"). Cada propuesta
en la Cima del Vendaval, con la Aeralis del juego (vendaval_juego) y jugadores;
usa las ayudas de viento_remake_escenas (la Aeralis del juego, la cima, el
cielo, las texturas de viento) y de viento_escenas (tornados, cuchillas, el
jugador y la composicion con el cielo de tormenta).

  ascenso   Corrientes de Ascenso: sube a 16 bloques; tres corrientes de aire
            suben a los jugadores hasta ella; uno sube, otro ya le pega con la
            espada y los demas esperan abajo
  campanas  Campanas del Viento: cuatro campanas en postes alrededor de la
            arena, cada una de su color y con su numero; suena una y hay que
            repetir el orden; un jugador bajo cada campana
  ojo       Ojo del Huracan: un muro de tormenta rodea la arena y solo el ojo,
            un circulo en calma que se mueve, protege; todos dentro y uno fuera,
            arrastrado por el viento
  desarme   Rafaga Ladrona: una rafaga arranca las espadas de dos jugadores; las
            espadas giran en remolinos en el aire, un companero golpea uno y
            otra espada ya cae junto a su dueno

Uso: python aeralis_mecanicas_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import viento_remake_escenas as R  # lee la raiz y la carpeta de salida de sys.argv
from viento_remake_escenas import (vr, nm, ne, ve, rm, aeralis, cinta3d, billboard, cuadrado_suelo, rayo,
                                   tex_viento2, tex_aro, tex_plano, tex_cuchilla, tex_chevrones, luz_fase,
                                   LUCES, AMB, SS, OUT, FUENTE, Y_VUELO_NUEVA)

TAU = math.tau

# Los colores de fase de la barra del jefe (AeralisBarraHud.COLOR_FASE)
CIAN = (95, 210, 255)
INDIGO = (127, 140, 255)
VIOLETA = (176, 124, 255)
MAGENTA = (255, 79, 216)
COLOR_FASE = {1: CIAN, 2: INDIGO, 3: VIOLETA, 4: MAGENTA}
BLANCO = (238, 242, 255)
PLATA = (214, 222, 240)
ROJO = (255, 110, 120)
SOMBRA = (6, 8, 22)


def claro(c, k=0.5):
    return tuple(int(c[i] + (255 - c[i]) * k) for i in range(3))


def oscuro(c, k=0.5):
    return tuple(int(c[i] * (1 - k)) for i in range(3))


# ----------------------------------------------------------------------
#  Materiales: la espada y las campanas
# ----------------------------------------------------------------------
def _plano(c1, c2, semilla, p=0.7):
    a, b = nm._hex(c1), nm._hex(c2)
    return nm._loseta(semilla, lambda x, y, r: a if r.random() < p else b)


def _bronce(color, semilla):
    """El cuerpo de la campana: metal del color, mas claro arriba."""
    c = np.array(color, float)

    def f(x, y, r):
        k = 0.55 + 0.35 * (1 - y / 15) + r.uniform(-0.06, 0.06)
        return tuple(int(v) for v in np.clip(c * k + 30 * (1 - y / 15), 0, 255))
    return nm._loseta(semilla, f)


nm.MAT.update({
    'hoja': _plano('6eeee2', '4fd8cf', 301),          # la hoja de diamante
    'hoja_filo': _plano('c8fff8', 'a8f8ee', 302),
    'mango': _plano('5a3a1e', '4a2e16', 303),
    'guarda': _plano('2fb8c8', '24a0ae', 304),
    'madera_osc': _plano('3a2a1e', '2e2016', 305),
    'hierro': _plano('8a8f98', '6e737c', 306),
})
for i, c in enumerate((CIAN, INDIGO, VIOLETA, MAGENTA)):
    nm.MAT['campana_%d' % (i + 1)] = _bronce(c, 310 + i)
    nm.MAT['badajo_%d' % (i + 1)] = _plano('%02x%02x%02x' % claro(c, 0.7), '%02x%02x%02x' % claro(c, 0.5), 320 + i)
    nm.EMISIVOS.add('badajo_%d' % (i + 1))


# ----------------------------------------------------------------------
#  Jugadores (con espada) y sus poses
# ----------------------------------------------------------------------
def _buscar(n, nombre):
    if n[0] == nombre:
        return n
    for h in n[4]:
        q = _buscar(h, nombre)
        if q is not None:
            return q
    return None


def nodo_espada(nombre='espada', off=(0, 10, -1), rot=(0, 0, 0)):
    """Una espada de diamante en pixeles de modelo: la hoja hacia -Z (delante),
    el mango hacia +Z; el centro del puno en el origen del nodo."""
    return nm.nodo(nombre, off, rot, [
        ((-0.8, -0.8, -1.0, 1.6, 1.6, 5.0), 'mango'),          # el puno
        ((-0.9, -0.9, 3.6, 1.8, 1.8, 1.4), 'guarda'),         # el pomo
        ((-3.0, -1.2, -2.4, 6.0, 2.4, 1.4), 'guarda'),        # la cruz
        ((-0.6, -1.4, -16.0, 1.2, 2.8, 13.6), 'hoja'),        # la hoja
        ((-0.5, -0.9, -18.0, 1.0, 1.8, 2.0), 'hoja_filo'),    # la punta
    ])


def jugador(lz, cam, x, z, guinada, y=0.0, pose=None, espada=False, rot_espada=(0, 0, 0), niebla=None,
            luces=None, amb=None, inclina=0.0):
    """El jugador de las fichas, con pose y, si se pide, la espada en la mano
    derecha. 'inclina' lo tumba hacia atras (grados), como al salir volando."""
    raiz = ne.jugador()
    if espada:
        _buscar(raiz, 'bd')[4].append(nodo_espada(rot=rot_espada))
    M = vr.T(x, y, z) @ vr.Ry(guinada * vr.D2R) @ vr.T(0, 1.0, 0) @ vr.Rx(inclina * vr.D2R) @ vr.T(0, -1.0, 0) \
        @ vr.T(0, 1.5, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])
    nm.dibujar(lz, cam, nm.quads(raiz, pose or {}, M), luces or LUCES, amb or AMB, niebla)


def espada_suelta(lz, cam, p, rot, escala=1.6, niebla=None):
    """Una espada sola en el mundo (girando en el remolino o cayendo), con el
    centro del puno en p; rot en grados (x, y, z) del mundo."""
    M = vr.T(*p) @ vr.Ry(rot[1] * vr.D2R) @ vr.Rz(rot[2] * vr.D2R) @ vr.Rx(rot[0] * vr.D2R) \
        @ np.diag([escala / 16, -escala / 16, escala / 16, 1])
    nm.dibujar(lz, cam, nm.quads(nodo_espada(off=(0, 0, 6)), {}, M), LUCES, AMB, niebla, brillo=1.6)


def guinada_hacia(dx, dz):
    """La guinada (grados) para que algo con el frente en -Z mire hacia (dx, dz)."""
    return math.degrees(math.atan2(-dx, -dz))


MIRAR_ARRIBA = {'cabeza': {'rot': (-30, 0, 0)}, 'bi': {'rot': (-20, 0, -8)}, 'bd': {'rot': (-30, 0, 8)}}
SUBIR = {'cabeza': {'rot': (-24, 0, 0)}, 'bi': {'rot': (-160, 0, -20)}, 'bd': {'rot': (-150, 0, 22)},
         'pi': {'rot': (14, 0, 4)}, 'pd': {'rot': (-12, 0, -4)}}
GOLPE_ALTO = {'cabeza': {'rot': (-20, 0, 0)}, 'bi': {'rot': (-20, 0, -10)}, 'bd': {'rot': (-128, 0, 6)},
              'pi': {'rot': (-16, 0, 0)}, 'pd': {'rot': (14, 0, 0)}}
PEDIR = {'cabeza': {'rot': (-26, 0, 0)}, 'bi': {'rot': (-158, 0, -22)}, 'bd': {'rot': (-140, 0, 26)}}
ARRASTRADO = {'cabeza': {'rot': (10, 0, 0)}, 'bi': {'rot': (-110, 0, -60)}, 'bd': {'rot': (-100, 0, 64)},
              'pi': {'rot': (-30, 0, 0)}, 'pd': {'rot': (36, 0, 0)}}
JUNTOS = {'bi': {'rot': (-24, 0, -6)}, 'bd': {'rot': (-30, 0, 6)}}


# ----------------------------------------------------------------------
#  Texturas de los efectos (RGBA uint8)
# ----------------------------------------------------------------------
def _rgba(col, a):
    t = np.zeros(col.shape[:2] + (4,))
    t[..., :3] = col
    t[..., 3] = np.clip(a, 0, 1) * 255
    return np.clip(t, 0, 255).astype(np.uint8)


def tex_halo(color, n=64, duro=2.0):
    """Un halo redondo: el centro casi blanco y el color que se apaga hacia fuera."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    a = np.clip(1 - d, 0, 1) ** duro
    k = np.clip(1 - d * 2.2, 0, 1)[..., None]
    col = np.array(color) * (1 - k) + 255 * k
    return _rgba(col, a)


def tex_chispa(n=96, color=(255, 252, 236)):
    """La estrella del golpe: cuatro puntas largas y el centro encendido."""
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = np.abs(xx + 0.5 - n / 2) / (n / 2), np.abs(yy + 0.5 - n / 2) / (n / 2)
    d = np.hypot(dx, dy)
    a = np.maximum(np.clip(1 - (dx * 7 + dy), 0, 1), np.clip(1 - (dy * 7 + dx), 0, 1))
    u, v = (dx + dy) / math.sqrt(2), np.abs(dx - dy) / math.sqrt(2)
    a = np.maximum(a, np.clip(1 - (v * 9 + u * 1.6), 0, 1) * 0.7)
    a = np.maximum(a, np.clip(1 - d * 2.6, 0, 1) ** 0.8)
    return _rgba(np.ones((n, n, 3)) * np.array(color), a * 1.2)


def tex_corriente(color, w=48, h=96, semilla=1):
    """La pared de una corriente de ascenso: hebras de viento inclinadas que
    suben (claras), sobre un velo tenue del color."""
    r = random.Random(semilla)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    a = np.full((h, w), 0.10)
    col = np.ones((h, w, 3)) * np.array(color, float)
    for _ in range(26):
        x0, y0 = r.uniform(0, w), r.uniform(0, h)
        L, g = r.uniform(14, 40), r.uniform(0.8, 1.8)
        # la hebra sube en diagonal (u avanza con v): el giro de la corriente
        t = np.clip(((yy - y0) % h) / L, 0, 1)
        dx = ((xx - x0 - (yy - y0) * 0.45) + w / 2) % w - w / 2
        m = np.exp(-(dx / g) ** 2) * (((yy - y0) % h) < L) * np.sin(math.pi * t) ** 0.6
        a = np.maximum(a, m * r.uniform(0.6, 1.0))
        col += m[..., None] * (255 - np.array(color, float)) * 0.7
    return _rgba(np.clip(col, 0, 255), a)


def tex_nota(color, n=48):
    """Una nota musical de pixel: cabeza redonda, palo y bandera."""
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            cab = math.hypot((x - 16) / 9.0, (y - 36) / 7.0) <= 1.0
            palo = 23 <= x <= 26 and 8 <= y <= 36
            bandera = 26 <= x <= 36 and 8 <= y <= 16 + (x - 26) * 0.6
            if cab or palo or bandera:
                t[y, x] = (*color, 255)
    return t


def tex_onda(color, n=128, grueso=0.08):
    """Un aro de sonido (la onda de una campana): un anillo suave."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    a = np.exp(-((d - (1 - grueso * 1.5)) / grueso) ** 2) * (d < 1)
    k = np.exp(-((d - (1 - grueso * 1.5)) / (grueso * 0.35)) ** 2)[..., None] * 0.6
    col = np.array(color) * (1 - k) + 255 * k
    return _rgba(col, a)


CHISPA = tex_chispa()


# ----------------------------------------------------------------------
#  Geometria de los efectos
# ----------------------------------------------------------------------
def trans(lz, cam, qs, tex, k=0.85, niebla=None, glow=0.0):
    ve.dibujar_translucido(lz, cam, qs, tex, k, niebla, glow)


def brillo(lz, cam, qs, tex, k=1.0):
    """Solo luz (aditivo): halos, chispas, ondas."""
    for P, UV in qs:
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, aditivo=True,
                         brillo=k)


def columna_aire(x, z, alto, r=1.8, giro=0.0, anillos=18, segs=14, huecos=True, base=0.0, vueltas=2.5, rep=None):
    """Una corriente de ascenso: un cilindro recto de viento, en franjas que
    suben girando (con huecos para ver a traves). Con 'rep' la textura se
    repite cada 'rep' segmentos (para los cilindros grandes)."""
    out = []
    for k in range(anillos):
        t0, t1 = k / anillos, (k + 1) / anillos
        ya, yb = base + alto * t0, base + alto * t1
        for s in range(segs):
            if huecos and (s + k) % 4 == 0:
                continue
            if rep:
                u0, u1 = (s % rep) / rep, (s % rep + 1) / rep
            else:
                u0, u1 = s / segs, (s + 1) / segs
            a0 = giro + TAU * s / segs + t0 * vueltas
            a1 = giro + TAU * (s + 1) / segs + t0 * vueltas
            b0, b1 = giro + TAU * s / segs + t1 * vueltas, giro + TAU * (s + 1) / segs + t1 * vueltas
            P = [(x + r * math.cos(a0), ya, z + r * math.sin(a0)), (x + r * math.cos(a1), ya, z + r * math.sin(a1)),
                 (x + r * math.cos(b1), yb, z + r * math.sin(b1)), (x + r * math.cos(b0), yb, z + r * math.sin(b0))]
            out.append((P, [(u0, 1 - t0), (u1, 1 - t0), (u1, 1 - t1), (u0, 1 - t1)]))
    return out


def helice(x, z, r, y0, y1, vueltas, giro=0.0, n=40):
    """Puntos de una helice que sube (para las estelas de la corriente)."""
    return [(x + r * math.cos(giro + TAU * vueltas * t), y0 + (y1 - y0) * t, z + r * math.sin(giro + TAU * vueltas * t))
            for t in np.linspace(0, 1, n)]


# ----------------------------------------------------------------------
#  Composicion y rotulos (sobre la imagen compuesta, en pixeles de 1600)
# ----------------------------------------------------------------------
def componer(lz, cam, W, H, semilla, fase, rayos=0.4, estelas=50):
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 300, 0.0, cam.ojo[2] + cam.f[2] * 300]))[1] / SS
    return ve.componer(lz, W, H, horiz, semilla, fase, rayos=rayos, n_estelas=estelas)


def pantalla(cam, p):
    sx, sy, z = cam.proyectar(p)
    return sx / SS, sy / SS, z


def rotulo(img, cam, p, texto, dx, dy, tam=30, color=BLANCO, linea=True, centro=False):
    """Un rotulo en mayusculas junto al punto p del mundo, desplazado (dx, dy),
    con su sombra y, si se pide, una linea fina hasta el punto."""
    sx, sy, z = pantalla(cam, p)
    if z < 0.5:
        return
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', tam)
    d = ImageDraw.Draw(img)
    w = d.textlength(texto, font=f)
    tx, ty = sx + dx, sy + dy
    if centro:
        tx -= w / 2
    elif dx < 0:
        tx -= w
    tx = min(max(tx, 14), img.size[0] - w - 14)
    if linea:
        ax = min(max(sx, tx), tx + w)
        arriba, abajo = ty + tam * 0.3, ty + tam * 1.3
        ay = abajo if sy > abajo else (arriba if sy < arriba else sy)
        if arriba <= sy <= abajo:
            ax = tx - 6 if sx < tx else tx + w + 6
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        dc.line([(sx, sy), (ax, ay)], fill=(*SOMBRA, 170), width=5)
        dc.line([(sx, sy), (ax, ay)], fill=(*color, 235), width=2)
        dc.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=(*color, 255))
        img.alpha_composite(capa)
    texto_sombra(img, (tx, ty), texto, f, color)
    return tx, ty, w


def texto_sombra(img, xy, texto, f, color):
    d = ImageDraw.Draw(img)
    tx, ty = xy
    for o in ((3, 3), (2, 2), (-1, 1), (1, -1)):
        d.text((tx + o[0], ty + o[1]), texto, font=f, fill=(*SOMBRA, 255))
    d.text((tx, ty), texto, font=f, fill=(*color, 255))


def lineas_viento(img, pts2d, color=(230, 240, 255), alfa=200, ancho=3):
    """Trazos de viento sobre la foto (listas de puntos de pantalla)."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for pts in pts2d:
        d.line(pts, fill=(*color, alfa), width=ancho, joint='curve')
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(0.8)))


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)


# ----------------------------------------------------------------------
#  1. Corrientes de Ascenso
#
#  Aeralis sube a 16 bloques (fuera del alcance de la espada) y lanza rafagas
#  desde arriba. Del suelo salen tres corrientes de aire: uno sube por la de
#  la izquierda, otro ya esta a su altura en la del centro y le pega con la
#  espada; los demas esperan al pie de la de la derecha.
# ----------------------------------------------------------------------
def ascenso(W=1600, H=900, fase=3):
    P = rm.paleta(fase)
    col = COLOR_FASE[fase]
    # la camara mira hacia +z: en la foto, -x queda a la derecha
    cam = vr.Camara(ojo=(-2.0, 3.6, -21.0), objetivo=(0.5, 11.6, 6.0), fov=66, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(26, 60)
    ve.suelo(lz, cam, niebla=niebla)
    for i, (x, z, alto, rota) in enumerate(((-17, 12, 5, True), (16, 14, 7, True), (-21, -2, 3, True), (22, 2, 4, False))):
        nm.dibujar(lz, cam, ve.columna(x, z, alto, rota, i), LUCES, AMB, niebla)
    yv = 16.0                                   # el origen de la entidad: 16 bloques sobre el suelo
    ax_, az_ = 0.5, 10.0
    corrientes = [(-9.5, -5.0), (4.2, 5.4), (11.5, 0.5)]
    alto_c = yv + 5.0
    # los que esperan abajo, al pie de la corriente de la izquierda (mirando arriba)
    for dx, dz, g in ((-2.8, -1.0, 25), (2.4, -1.6, -30), (0.0, -3.1, 0)):
        x, z = corrientes[2][0] + dx, corrientes[2][1] + dz
        jugador(lz, cam, x, z, guinada_hacia(ax_ - x, az_ - z) + g, pose=MIRAR_ARRIBA, espada=True, niebla=niebla)
    # el que sube por la de la derecha, con los brazos en alto
    sube = (corrientes[0][0], 9.0, corrientes[0][1])
    jugador(lz, cam, sube[0], sube[2], guinada_hacia(cam.ojo[0] - sube[0], cam.ojo[2] - sube[2]) + 35, y=sube[1],
            pose=SUBIR, espada=True, niebla=niebla)
    # el que ya esta a su altura, en la del centro, de cara a su abdomen y con la espada en alto
    alto_golpe = yv + 3.2
    pg = (corrientes[1][0], corrientes[1][1])
    jugador(lz, cam, pg[0], pg[1], guinada_hacia(ax_ - pg[0], az_ - 0.5 - pg[1]), y=alto_golpe, pose=GOLPE_ALTO,
            espada=True, rot_espada=(-60, 0, 0), niebla=niebla)
    aeralis(lz, cam, 'despues', ax_, yv, az_, guinada_hacia(cam.ojo[0] - ax_, cam.ojo[2] - az_), pose=rm.HEROICA,
            fase=fase, niebla=niebla)
    # lo translucido: las corrientes (dos capas que giran), su aro y sus estelas
    for i, (x, z) in enumerate(corrientes):
        trans(lz, cam, cuadrado_suelo(x, z, 2.9), tex_aro(P['borde'], 128, 0.07, 20, 50), 0.9, None, 0.8)
        trans(lz, cam, columna_aire(x, z, alto_c, 1.9, 0.4 * i, vueltas=2.0), tex_corriente(P['halo'], semilla=3 + i),
              0.5, niebla, 0.10)
        trans(lz, cam, columna_aire(x, z, alto_c, 2.35, 1.3 + i, vueltas=-1.6, huecos=True),
              tex_corriente(col, semilla=9 + i), 0.3, niebla, 0.06)
        r = random.Random(40 + i)
        for k in range(3):
            pts = helice(x, z, r.uniform(1.2, 1.8), r.uniform(0.3, 3.0), alto_c - r.uniform(0, 4), r.uniform(1.6, 2.6),
                         r.uniform(0, TAU), 36)
            trans(lz, cam, cinta3d(pts, 0.05, cam), tex_plano(claro(col, 0.6)), 0.8, niebla, 0.35)
        # flechas que suben por dentro
        for k in range(6):
            fx, fz = x + r.uniform(-1.0, 1.0), z + r.uniform(-1.0, 1.0)
            fy = 1.0 + k * (alto_c - 3) / 6 + r.uniform(-0.5, 0.5)
            trans(lz, cam, cinta3d([(fx, fy, fz), (fx, fy + 1.6, fz)], 0.05, cam), tex_plano(claro(col, 0.7)), 1.0,
                  niebla, 0.6)
        motas = [billboard((x + r.uniform(-1.6, 1.6), r.uniform(0.4, alto_c), z + r.uniform(-1.6, 1.6)), 0.08, cam,
                           r.uniform(0, 3)) for _ in range(22)]
        trans(lz, cam, motas, tex_plano(luz_fase(P)), 1.0, niebla, 0.6)
    # el que pega: un aro de luz alrededor y la chispa del golpe en su abdomen
    centro_g = np.array([pg[0], alto_golpe + 1.0, pg[1]])
    brillo(lz, cam, [billboard(centro_g, 1.9, cam)], tex_onda(claro(col, 0.3), grueso=0.06), 1.0)
    golpe = centro_g + (np.array([ax_, alto_golpe + 2.0, az_]) - centro_g) * 0.55
    brillo(lz, cam, [billboard(golpe, 1.4, cam)], tex_halo(col), 0.9)
    brillo(lz, cam, [billboard(golpe, 1.0, cam, 0.3)], CHISPA, 1.5)
    img = componer(lz, cam, W, H, 31, fase, rayos=0.7, estelas=40)
    rotulo(img, cam, (corrientes[0][0] - 2.0, 3.0, corrientes[0][1]), 'CORRIENTE', -60, 40, 42, claro(col, 0.6))
    rotulo(img, cam, (pg[0] + 1.2, alto_golpe + 1.6, pg[1]), '¡A SU ALTURA!', -170, -70, 46, BLANCO)
    rotulo(img, cam, (corrientes[2][0], 0.0, corrientes[2][1] - 3.4), 'LOS DEMÁS ESPERAN SU TURNO', 0, 6, 28, PLATA,
           linea=False, centro=True)
    rotulo(img, cam, (sube[0], sube[1] + 1.0, sube[2]), 'SUBE', -60, -20, 30, claro(col, 0.6))
    guardar(img, 'ascenso')


# ----------------------------------------------------------------------
#  2. Campanas del Viento
#
#  Cuatro postes de piedra alrededor de la arena, cada uno con una campana de
#  su color (los de las fases: cian, indigo, violeta, magenta) y su numero.
#  Ella ha tocado la melodia (1, 3, 2, 4) y ahora hay que repetirla: la 1 ya
#  ha sonado, la 3 es la que toca (se enciende y suena) y su jugador la golpea.
# ----------------------------------------------------------------------
ALTO_POSTE = 5.6
BRAZO = 2.2


def poste_campana(x, z, giro, n, escala_campana=1.5):
    """Un poste de piedra con un brazo hacia el centro de la arena y la campana
    colgando de su punta. Devuelve (quads, centro de la campana, su boca)."""
    h = ALTO_POSTE * 16
    L = BRAZO * 16
    cajas = [((-14, -16, -14, 28, 16, 28), 'roca_osc'), ((-10, -h, -10, 20, h - 16, 20), 'roca')]
    for k in range(1, int(ALTO_POSTE)):
        cajas.append(((-10.6, -k * 16 - 2, -10.6, 21.2, 2, 21.2), 'roca_osc'))
    cajas += [((-12, -h - 6, -12, 24, 6, 24), 'roca_osc'),            # el capitel
              ((-4, -h - 4, -L - 4, 8, 8, L), 'roca_osc'),             # el brazo
              ((-1, -h + 4, -L - 1, 2, 10, 2), 'hierro')]              # la varilla
    k = escala_campana
    y0 = -h + 13
    campana = [((-5 * k, y0, -L - 5 * k, 10 * k, 4 * k, 10 * k), 'campana_%d' % n),
               ((-8.5 * k, y0 + 4 * k, -L - 8.5 * k, 17 * k, 13 * k, 17 * k), 'campana_%d' % n),
               ((-11 * k, y0 + 17 * k, -L - 11 * k, 22 * k, 4 * k, 22 * k), 'campana_%d' % n),
               ((-2.5 * k, y0 + 21 * k, -L - 2.5 * k, 5 * k, 5 * k, 5 * k), 'badajo_%d' % n)]
    raiz = nm.nodo('poste', (0, 0, 0), (0, giro, 0), cajas + campana)
    M = vr.T(x, 0, z) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1])
    qs = nm.quads(raiz, {}, M)
    d = np.array([-math.sin(math.radians(giro)), 0.0, -math.cos(math.radians(giro))])
    punta = np.array([x, 0.0, z]) + d * BRAZO
    centro = punta + np.array([0, (h - 13 - 12 * k) / 16, 0])
    boca = punta + np.array([0, (h - 13 - 21 * k) / 16, 0])
    return qs, centro, boca


def campanas(W=1600, H=900, fase=2):
    colores = {1: CIAN, 2: INDIGO, 3: VIOLETA, 4: MAGENTA}
    # la camara mira hacia +z: en la foto, -x queda a la derecha
    cam = vr.Camara(ojo=(0.0, 11.0, -28.0), objetivo=(0.0, 6.5, 6.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(30, 70)
    ve.suelo(lz, cam, niebla=niebla)
    ax_, az_ = 0.0, 14.0
    # los postes, alrededor de la arena y numerados de izquierda a derecha en la foto
    sitios = {1: (20.5, 8.0), 2: (8.5, -5.0), 3: (-8.5, -5.0), 4: (-20.5, 8.0)}
    campana = {}
    for n, (x, z) in sitios.items():
        # el brazo, hacia el medio de la foto y algo hacia la camara: la campana se ve entera
        giro = guinada_hacia(-math.copysign(1.0, x), -0.45)
        qs, centro, boca = poste_campana(x, z, giro, n)
        nm.dibujar(lz, cam, qs, LUCES, AMB, niebla, brillo=1.6)
        campana[n] = (centro, boca, giro)
    # un jugador bajo cada campana; el de la 3 la golpea
    ahora, sonadas = 3, (1,)
    for n, (centro, boca, giro) in campana.items():
        # a su lado, hacia el medio, de perfil para la camara
        px, pz = centro[0] - math.copysign(1.35, centro[0]), centro[2] - 0.6
        if n == ahora:
            jugador(lz, cam, px, pz, guinada_hacia(centro[0] - px, centro[2] - pz), pose=GOLPE_ALTO, espada=True,
                    rot_espada=(-60, 0, 0), niebla=niebla)
        else:
            jugador(lz, cam, px, pz, guinada_hacia(centro[0] - px, centro[2] - pz) + 20, pose=MIRAR_ARRIBA,
                    espada=True, niebla=niebla)
    aeralis(lz, cam, 'despues', ax_, Y_VUELO_NUEVA, az_, guinada_hacia(cam.ojo[0] - ax_, cam.ojo[2] - az_),
            pose=rm.ESCAMAS, fase=fase, niebla=niebla)
    # las cintas musicales: salen de ella y se enroscan, una de cada color, con notas
    pecho = np.array([ax_, Y_VUELO_NUEVA + 7.5, az_ - 1.0])
    for n, (centro, boca, giro) in campana.items():
        c = colores[n]
        a = pecho
        b = np.array(centro) + np.array([0, 2.4, 0])
        lado = np.cross(b - a, [0, 1, 0])
        lado /= np.linalg.norm(lado)
        pts = [tuple(a + (b - a) * t + np.array([0, 3.0 * math.sin(math.pi * t), 0]) +
                     lado * 1.4 * math.sin(TAU * 1.5 * t) * math.sin(math.pi * t)) for t in np.linspace(0.18, 0.86, 22)]
        k = 1.0 if n == ahora else (0.55 if n in sonadas else 0.35)
        trans(lz, cam, cinta3d(pts, 0.16, cam), tex_cuchilla(c, 64, 16, n), 0.55 * k + 0.2, niebla, 0.5 * k)
        tn = tex_nota(claro(c, 0.45))
        for j, q in enumerate(pts[3::5]):
            trans(lz, cam, [billboard(np.array(q) + np.array([0, 0.9, 0]), 0.55, cam, 0.25 * (j % 2 * 2 - 1))], tn,
                  1.0, niebla, 0.9 * k)
    # las campanas encendidas: la que toca, a tope y con sus ondas; la que ya ha
    # sonado, tenue; las que faltan, apenas
    for n, (centro, boca, giro) in campana.items():
        c = colores[n]
        if n == ahora:
            brillo(lz, cam, [billboard(centro, 3.4, cam)], tex_halo(c), 1.3)
            for rr in (2.2, 3.1, 4.0):
                brillo(lz, cam, [billboard(centro, rr, cam)], tex_onda(claro(c, 0.2), grueso=0.05), 1.0)
            brillo(lz, cam, [billboard(boca + np.array([0.0, -0.3, 0.0]), 0.9, cam, 0.3)], CHISPA, 1.3)
        else:
            brillo(lz, cam, [billboard(centro, 2.2, cam)], tex_halo(c), 0.55 if n in sonadas else 0.35)
        trans(lz, cam, cuadrado_suelo(centro[0], centro[2], 1.8), tex_aro(c, 128, 0.08, 12, 40 if n == ahora else 20),
              0.9, None, 0.9 if n == ahora else 0.4)
    img = componer(lz, cam, W, H, 41, fase, rayos=0.4, estelas=40)
    # el numero de cada campana, encima
    for n, (centro, boca, giro) in campana.items():
        c = colores[n]
        sx, sy, _ = pantalla(cam, np.array(centro) + np.array([0, 2.3, 0]))
        f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 76 if n == ahora else 60)
        w = ImageDraw.Draw(img).textlength(str(n), font=f)
        texto_sombra(img, (sx - w / 2, sy - 90), str(n), f, claro(c, 0.35) if n == ahora else c)
    # la melodia, arriba: la 1 ya ha sonado, la 3 es la de ahora
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 30)
    fg = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 64)
    d = ImageDraw.Draw(img)
    orden = (1, 3, 2, 4)
    titulo = 'SU MELODÍA'
    wt = d.textlength(titulo, font=f)
    paso = 96
    ancho = wt + 28 + paso * len(orden)
    x0 = (W - ancho) / 2
    y0 = H - 128
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).rounded_rectangle((x0 - 26, y0, x0 + ancho + 6, y0 + 96), 18, fill=(8, 10, 30, 185),
                                           outline=(150, 160, 230, 160), width=2)
    img.alpha_composite(capa)
    d = ImageDraw.Draw(img)
    texto_sombra(img, (x0, y0 + 24), titulo, f, PLATA)
    for j, n in enumerate(orden):
        cx = x0 + wt + 28 + paso * j + paso / 2
        c = colores[n]
        col = claro(c, 0.35) if n == ahora else (c if n not in sonadas else oscuro(c, 0.35))
        w = d.textlength(str(n), font=fg)
        texto_sombra(img, (cx - w / 2, y0 - 4), str(n), fg, col)
        if n == ahora:
            d.rounded_rectangle((cx - 30, y0 + 82, cx + 30, y0 + 88), 3, fill=(*claro(c, 0.3), 255))
        if n in sonadas:
            d.line((cx - 18, y0 + 48, cx + 18, y0 + 48), fill=(*PLATA, 200), width=3)
        if j < len(orden) - 1:
            d.text((cx + paso / 2 - 6, y0 + 22), '·', font=f, fill=(*PLATA, 255))
    centro3, boca3, _ = campana[ahora]
    rotulo(img, cam, boca3 + np.array([0.6, -1.4, 0.0]), '¡EN ORDEN!', 70, 50, 48, BLANCO)
    guardar(img, 'campanas')


# ----------------------------------------------------------------------
#  3. Ojo del Huracan
#
#  Un muro de tormenta rodea la arena (oscuro, girando, con rayos) y por el
#  suelo el viento barre en espiral. Solo el ojo, un circulo de 8 bloques en
#  calma, protege: va derivando (la flecha y su sitio siguiente, en punteado).
#  Todos se apinan dentro; el que se ha quedado fuera sale arrastrado.
# ----------------------------------------------------------------------
def tex_nube(color, n=64, semilla=1):
    """Una bocanada de nube de tormenta: un disco blando, mas oscuro abajo."""
    r = random.Random(semilla)
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    a = np.zeros((n, n))
    for _ in range(6):
        cx, cy, rr = r.uniform(0.3, 0.7) * n, r.uniform(0.35, 0.65) * n, r.uniform(0.18, 0.32) * n
        a = np.maximum(a, np.clip(1 - np.hypot(xx - cx, yy - cy) / rr, 0, 1) ** 0.8)
    k = (yy / n)[..., None]
    col = np.array(color, float) * (1.25 - 0.5 * k)
    return _rgba(np.clip(col, 0, 255), a * 0.95)


def tex_muro_tormenta(w=64, h=128, semilla=1, color=(46, 22, 78), veta=(170, 120, 235), n_vetas=14):
    """La pared del huracan: nube oscura casi opaca con vetas claras en
    diagonal (el giro) y algun jiron mas claro."""
    r = random.Random(semilla)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    ruido = np.zeros((h, w))
    for k in range(5):
        fx, fy, f0 = r.uniform(0.05, 0.2), r.uniform(0.02, 0.1), r.uniform(0, TAU)
        ruido += np.sin(xx * fx + yy * fy + f0) / (k + 1)
    ruido = (ruido - ruido.min()) / (ruido.max() - ruido.min())
    a = 0.55 + 0.35 * ruido
    col = np.ones((h, w, 3)) * np.array(color, float) * (0.7 + 0.6 * ruido[..., None])
    for _ in range(n_vetas):
        x0, g = r.uniform(0, w), r.uniform(0.8, 2.2)
        dx = ((xx - x0 - yy * 0.6) + w / 2) % w - w / 2
        m = np.exp(-(dx / g) ** 2) * r.uniform(0.5, 1.0)
        col = col * (1 - m[..., None]) + np.array(veta, float) * m[..., None]
        a = np.maximum(a, m * 0.95)
    return _rgba(np.clip(col, 0, 255), a)


def tex_suelo_tormenta(X0, X1, Z0, Z1, ojo, R_ojo, R_muro, centro, n=640, color=(40, 16, 70), veta=(205, 150, 255)):
    """El suelo de la arena visto desde arriba (fila = z, columna = x): fuera del
    ojo, un velo oscuro con vetas de viento en espiral alrededor del centro;
    dentro del ojo, nada (la calma); el borde del ojo se aclara."""
    zz, xx = np.mgrid[0:n, 0:n].astype(float)
    x = X0 + (xx + 0.5) / n * (X1 - X0)
    z = Z0 + (zz + 0.5) / n * (Z1 - Z0)
    d_ojo = np.hypot(x - ojo[0], z - ojo[1])
    rx, rz = x - centro[0], z - centro[1]
    rr = np.hypot(rx, rz) + 1e-6
    ang = np.arctan2(rz, rx)
    s = (ang * 5 / TAU + np.log(rr) * 1.8) % 1.0
    vetas = np.exp(-((s - 0.5) / 0.05) ** 2)
    fuera = np.clip((d_ojo - R_ojo - 0.3) / 1.8, 0, 1) * (rr < R_muro + 1)
    a = fuera * (0.45 + 0.4 * vetas)
    k = vetas[..., None] * 0.8
    col = np.array(color, float) * (1 - k) + np.array(veta, float) * k
    return _rgba(col, a)


def suelo_teselas(X0, X1, Z0, Z1, paso=6.0, y=0.08):
    """Un plano del suelo en baldosas (para que ninguna quede detras de la
    camara), con las UV de su trozo de la textura."""
    out = []
    xs = np.arange(X0, X1 + 1e-6, paso)
    zs = np.arange(Z0, Z1 + 1e-6, paso)
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            xa, xb, za, zb = xs[i], xs[i + 1], zs[j], zs[j + 1]
            ua, ub = (xa - X0) / (X1 - X0), (xb - X0) / (X1 - X0)
            va, vb = (za - Z0) / (Z1 - Z0), (zb - Z0) / (Z1 - Z0)
            out.append(([(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)], [(ua, va), (ub, va), (ub, vb), (ua, vb)]))
    return out


def circulo_suelo(cx, cz, R, n=64, y=0.1):
    return [(cx + R * math.cos(TAU * k / n), y, cz + R * math.sin(TAU * k / n)) for k in range(n + 1)]


def ojo(W=1600, H=900, fase=4):
    P = rm.paleta(fase)
    col = COLOR_FASE[fase]
    calma = (210, 245, 255)
    # la camara mira hacia +z desde lo alto: en la foto, -x queda a la derecha
    cam = vr.Camara(ojo=(-2.0, 28.0, -21.0), objetivo=(1.0, 0.0, 10.0), fov=62, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(40, 80)
    ve.suelo(lz, cam, niebla=niebla)
    centro = (0.0, 6.0)
    R_muro = 27.0
    ojo_c = np.array([3.0, 5.0])
    R_ojo = 8.0
    deriva = np.array([-1.0, 0.45])
    deriva /= np.linalg.norm(deriva)
    # todos apinados dentro del ojo
    dentro = [(1.2, 3.2, 200), (4.6, 2.6, 160), (2.8, 6.4, 20), (5.6, 5.8, -40), (0.2, 6.0, 60), (3.6, 4.2, 120)]
    for x, z, g in dentro:
        jugador(lz, cam, x, z, g, pose=JUNTOS, espada=True, niebla=niebla)
    # el que se ha quedado fuera, arrastrado por el viento (girando con la tormenta)
    fuera = np.array([-6.0, -9.0])
    jugador(lz, cam, fuera[0], fuera[1], 130, y=1.6, pose=ARRASTRADO, inclina=-35, niebla=niebla)
    trans(lz, cam, cuadrado_suelo(fuera[0] + 0.6, fuera[1] - 0.3, 1.4), tex_aro(ROJO, 64, 0.12, 8, 60), 0.9, None, 0.8)
    aeralis(lz, cam, 'despues', -2.0, Y_VUELO_NUEVA, 18.0, guinada_hacia(cam.ojo[0] + 2, cam.ojo[2] - 18),
            pose=rm.HEROICA, fase=fase, niebla=niebla)
    # el suelo de la tormenta, con el hueco del ojo
    X0, X1, Z0, Z1 = -30.0, 30.0, -24.0, 36.0
    trans(lz, cam, suelo_teselas(X0, X1, Z0, Z1), tex_suelo_tormenta(X0, X1, Z0, Z1, ojo_c, R_ojo, R_muro, centro),
          0.95, niebla, 0.25)
    # el ojo: el aro claro y su sitio siguiente, en punteado
    trans(lz, cam, cuadrado_suelo(ojo_c[0], ojo_c[1], R_ojo), tex_aro(calma, 256, 0.035, 48, 26), 1.0, None, 1.2)
    sig = ojo_c + deriva * 6.0
    aro_sig = circulo_suelo(sig[0], sig[1], R_ojo, 48)
    for k in range(0, 48, 2):
        trans(lz, cam, cinta3d(aro_sig[k:k + 2], 0.09, cam), tex_plano(calma), 0.8, None, 0.6)
    # la flecha de la deriva, en galones
    a = ojo_c + deriva * (R_ojo - 3.5)
    b = ojo_c + deriva * (R_ojo + 6.5)
    dd = (b - a) / np.linalg.norm(b - a)
    lado = np.array([-dd[1], dd[0]]) * 1.7
    gal = []
    paso = 1.7
    for k in range(int(np.linalg.norm(b - a) // paso)):
        p0, p1 = a + dd * k * paso, a + dd * (k + 1) * paso
        Pq = [p1 - lado, p1 + lado, p0 + lado, p0 - lado]
        gal.append(([(q[0], 0.12, q[1]) for q in Pq], [(0, 0), (1, 0), (1, 1), (0, 1)]))
    trans(lz, cam, gal, tex_chevrones(calma), 1.0, None, 1.0)
    # el muro del huracan: dos capas que giran, con rayos dentro
    alto_muro = 12.0
    trans(lz, cam, columna_aire(centro[0], centro[1], alto_muro, R_muro, 0.0, anillos=6, segs=96, huecos=False,
                                vueltas=0.5, rep=4),
          tex_muro_tormenta(semilla=2, color=(20, 9, 36), veta=(92, 62, 150), n_vetas=6), 0.94, niebla, 0.0)
    trans(lz, cam, columna_aire(centro[0], centro[1], alto_muro + 1.0, R_muro - 1.5, 1.0, anillos=6, segs=96,
                                huecos=True, vueltas=-0.4, rep=3),
          tex_muro_tormenta(semilla=5, color=(40, 18, 70), veta=(200, 140, 250), n_vetas=4), 0.22, niebla, 0.03)
    # el borde de arriba del muro: un anillo de nubes oscuras
    r = random.Random(3)
    nubes = []
    for k in range(110):
        a = TAU * k / 110 + r.uniform(-0.02, 0.02)
        rr = R_muro + r.uniform(-1.5, 1.0)
        nubes.append(billboard((centro[0] + rr * math.cos(a), alto_muro + r.uniform(-1.5, 1.5),
                                centro[1] + rr * math.sin(a)), r.uniform(2.6, 4.2), cam, r.uniform(-0.4, 0.4)))
    trans(lz, cam, nubes, tex_nube((44, 26, 72), semilla=4), 0.9, niebla, 0.0)
    r = random.Random(12)
    for k in range(9):
        ang = math.pi / 2 + r.uniform(-1.4, 1.4)
        x, z = centro[0] + (R_muro - 1) * math.cos(ang), centro[1] + (R_muro - 1) * math.sin(ang)
        pts = rayo((x, alto_muro - 1.0, z), (x + r.uniform(-3, 3), 0.5, z + r.uniform(-2, 2)), 90 + k, 10, 1.1)
        trans(lz, cam, cinta3d(pts, 0.14, cam), tex_plano(claro(col, 0.5)), 1.0, None, 1.6)
    # el viento que barre el suelo: estelas en arco alrededor del centro
    for k in range(26):
        rr = r.uniform(10, R_muro - 2)
        a0 = r.uniform(0, TAU)
        arco = [(centro[0] + rr * math.cos(a0 + t), 0.6 + 0.3 * math.sin(k), centro[1] + rr * math.sin(a0 + t))
                for t in np.linspace(0, 0.5, 8)]
        p_med = np.array(arco[4])
        if np.hypot(p_med[0] - ojo_c[0], p_med[2] - ojo_c[1]) < R_ojo + 1.5:
            continue
        trans(lz, cam, cinta3d(arco, 0.07, cam), tex_cuchilla(claro(col, 0.55), 64, 12, k), 0.8, niebla, 0.5)
    # un brillo de calma dentro del ojo
    brillo(lz, cam, cuadrado_suelo(ojo_c[0], ojo_c[1], R_ojo * 0.95, y=0.11), tex_halo(calma, 128, 1.2), 0.25)
    img = componer(lz, cam, W, H, 51, fase, rayos=1.0, estelas=70)
    # el viento que se lleva al de fuera
    trazos = []
    for k in range(7):
        p0 = np.array([fuera[0] + 4.5, 0.6 + k * 0.35, fuera[1] - 3.0 + k * 0.5])
        pts = []
        for t in np.linspace(0, 1, 10):
            q = p0 + np.array([-8.0 * t, 0.6 * math.sin(t * math.pi), 3.5 * t])
            sx, sy, _ = pantalla(cam, q)
            pts.append((sx, sy))
        trazos.append(pts)
    lineas_viento(img, trazos, (236, 228, 255), 190, 3)
    rotulo(img, cam, (ojo_c[0] + R_ojo * 0.8, 0.1, ojo_c[1] - R_ojo * 0.55), 'OJO DEL HURACÁN', -40, 90, 46,
           claro(calma, 0.3))
    rotulo(img, cam, (b[0], 0.12, b[1]), 'SE MUEVE', -40, -70, 44, claro(calma, 0.3))
    rotulo(img, cam, (fuera[0], 2.4, fuera[1]), 'FUERA, TE ARRASTRA', 60, 30, 30, claro(ROJO, 0.4))
    guardar(img, 'ojo')


# ----------------------------------------------------------------------
#  4. Rafaga Ladrona
#
#  Su rafaga (cintas de viento que salen de ella) ha arrancado la espada a dos
#  jugadores. La de la izquierda gira dentro de un remolino pequeno en el aire
#  y un companero lo golpea (lleva 2 de 3 golpes); la de la derecha ya cae,
#  con el remolino deshecho, junto a su dueno.
# ----------------------------------------------------------------------
def remolino(lz, cam, c, P, col, niebla, giro=0.0, alto=4.0, k=1.0):
    """Un remolino pequeno en el aire, centrado en c: dos embudos que giran y
    tres anillos de viento que lo cinen."""
    base = c[1] - alto / 2
    trans(lz, cam, ve.tornado(c[0], c[2], alto, 0.5, 1.6, giro, anillos=12, segs=12, base=base),
          tex_viento2(P['tormenta'], 61, densidad=1.0), 0.75 * k, niebla, 0.04 * k)
    trans(lz, cam, ve.tornado(c[0], c[2], alto * 1.05, 0.7, 2.1, giro + 1.2, anillos=12, segs=14, base=base - 0.05),
          tex_viento2(P['halo'], 62), 0.6 * k, niebla, 0.08 * k)
    for hh in (0.2, 0.5, 0.85):
        rr = 0.7 + (2.1 - 0.7) * hh ** 1.5 + 0.15
        aro = [(c[0] + rr * math.cos(a), base + alto * hh, c[2] + rr * math.sin(a)) for a in np.linspace(0, TAU, 25)]
        trans(lz, cam, cinta3d(aro, 0.05, cam), tex_plano(claro(col, 0.6)), 1.0 * k, niebla, 0.35 * k)
    for j in range(2):
        pts = [(c[0] + (0.6 + 1.3 * t ** 1.4) * math.cos(giro + j * math.pi + TAU * 1.6 * t), base + alto * t,
                c[2] + (0.6 + 1.3 * t ** 1.4) * math.sin(giro + j * math.pi + TAU * 1.6 * t)) for t in np.linspace(0, 1, 30)]
        trans(lz, cam, cinta3d(pts, 0.04, cam), tex_plano(claro(col, 0.5)), 0.9 * k, niebla, 0.25 * k)


def desarme(W=1600, H=900, fase=2):
    P = rm.paleta(fase)
    col = COLOR_FASE[fase]
    # la camara mira hacia +z: en la foto, -x queda a la derecha
    cam = vr.Camara(ojo=(1.5, 5.6, -12.5), objetivo=(-0.5, 4.2, 6.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(26, 60)
    ve.suelo(lz, cam, niebla=niebla)
    for i, (x, z, alto, rota) in enumerate(((16, 12, 5, True), (-20, 10, 3, True), (19, 2, 4, False))):
        nm.dibujar(lz, cam, ve.columna(x, z, alto, rota, i), LUCES, AMB, niebla)
    ax_, az_ = -15.0, 26.0                      # ella, al fondo a la derecha
    w1 = np.array([4.0, 4.9, 0.0])              # el remolino que golpean
    w2 = np.array([-3.6, 5.4, -0.6])            # el que ya se ha deshecho
    duenno1 = (3.2, -2.6)
    aliado = (6.9, -0.6)
    duenno2 = (-4.6, -2.6)
    cae = np.array([-3.9, 2.7, -1.4])           # la espada que cae (a media hoja)
    # los duenos, sin espada; el aliado, golpeando el remolino
    jugador(lz, cam, duenno1[0], duenno1[1], guinada_hacia(w1[0] - duenno1[0], w1[2] - duenno1[1]) + 25, pose=PEDIR,
            niebla=niebla)
    jugador(lz, cam, aliado[0], aliado[1], guinada_hacia(w1[0] - aliado[0], w1[2] - aliado[1]), pose=GOLPE_ALTO,
            espada=True, rot_espada=(-60, 0, 0), niebla=niebla)
    jugador(lz, cam, duenno2[0], duenno2[1], guinada_hacia(cae[0] - duenno2[0], cae[2] - duenno2[1]),
            pose={'cabeza': {'rot': (-16, 0, 0)}, 'bi': {'rot': (-80, 0, -14)}, 'bd': {'rot': (-86, 0, 14)}},
            niebla=niebla)
    aeralis(lz, cam, 'despues', ax_, Y_VUELO_NUEVA, az_, guinada_hacia(cam.ojo[0] - ax_, cam.ojo[2] - az_) - 25,
            pose=rm.HEROICA, fase=fase, niebla=niebla)
    # las espadas: la que gira en el remolino (en diagonal) y la que cae, de punta
    espada_suelta(lz, cam, cae, (-90, 20, 0), escala=1.9, niebla=niebla)
    # la rafaga: cintas de viento que salen de ella y barren hacia los remolinos
    pecho = np.array([ax_ + 2.0, Y_VUELO_NUEVA + 8.0, az_ - 3.0])
    for k, (meta, curva, alto) in enumerate(((w1 + np.array([1.0, 1.2, 0]), 3.0, 3.5), (w2, -1.5, 2.0),
                                             (w1 + np.array([3.0, 3.0, 2.0]), 5.0, 5.0))):
        lado = np.cross(meta - pecho, [0, 1, 0])
        lado /= np.linalg.norm(lado)
        pts = [tuple(pecho + (meta - pecho) * t + lado * curva * math.sin(math.pi * t) +
                     np.array([0, alto * math.sin(math.pi * t), 0])) for t in np.linspace(0.15, 0.85, 16)]
        trans(lz, cam, cinta3d(pts, 0.28, cam), tex_cuchilla(P['borde'], 64, 16, k + 3), 0.6, niebla, 0.3)
    # el remolino que golpean, con la espada dentro (se pinta despues, para que se lea)
    remolino(lz, cam, w1, P, col, niebla, giro=0.4, k=1.0)
    espada_suelta(lz, cam, w1 + np.array([0.0, 0.1, 0.0]), (40, 100, 0), escala=2.0, niebla=niebla)
    for j in range(2):
        rr = 1.05 + 0.2 * j
        arco = [(w1[0] + rr * math.cos(a), w1[1] - 0.2 + 0.4 * j, w1[2] + rr * math.sin(a))
                for a in np.linspace(3.6 + j * 2.5, 3.6 + j * 2.5 + 2.2, 12)]
        trans(lz, cam, cinta3d(arco, 0.06, cam), tex_plano(claro(col, 0.7)), 0.9, None, 0.4)
    # el golpe del aliado en el remolino
    golpe = w1 + (np.array([aliado[0], 3.4, aliado[1]]) - w1) * 0.5
    brillo(lz, cam, [billboard(golpe, 1.2, cam)], tex_halo(claro(col, 0.3)), 0.9)
    brillo(lz, cam, [billboard(golpe, 0.9, cam, 0.3)], CHISPA, 1.5)
    # el remolino deshecho: jirones sueltos que se abren hacia fuera
    for j in range(5):
        a0 = TAU * j / 5 + 0.3
        arco = [(w2[0] + (0.9 + 1.2 * t) * math.cos(a0 + 1.4 * t), w2[1] + 0.4 * math.sin(j) + 0.5 * t,
                 w2[2] + (0.9 + 1.2 * t) * math.sin(a0 + 1.4 * t)) for t in np.linspace(0, 1, 9)]
        trans(lz, cam, cinta3d(arco, 0.12, cam), tex_cuchilla(P['halo'], 48, 12, j), 0.45, niebla, 0.2)
    # el aro de la espada que cae, en el suelo junto a su dueno
    trans(lz, cam, cuadrado_suelo(cae[0], cae[2], 1.1), tex_aro(claro(col, 0.5), 64, 0.12, 8, 60), 0.9, None, 0.9)
    img = componer(lz, cam, W, H, 61, fase, rayos=0.3, estelas=50)
    # la caida: trazos verticales encima de la espada que cae
    trazos = []
    for dx in (-0.22, 0.0, 0.22):
        a = pantalla(cam, cae + np.array([dx, 1.25, 0]))
        b = pantalla(cam, cae + np.array([dx, 2.7, 0]))
        trazos.append([(a[0], a[1]), (b[0], b[1])])
    lineas_viento(img, trazos, (230, 236, 255), 210, 3)
    rotulo(img, cam, w1 + np.array([-0.4, 0.5, 0]), '¡SU ESPADA!', 90, -190, 50, BLANCO)
    tx, ty, w = rotulo(img, cam, golpe, 'GOLPEA EL REMOLINO', -60, -150, 40, claro(col, 0.55))
    # los golpes que lleva: 2 de 3, debajo del rotulo
    d = ImageDraw.Draw(img)
    for j in range(3):
        cx, cy = tx + w - 14 - (2 - j) * 34, ty + 74
        lleno = j < 2
        d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill=(*claro(col, 0.5), 255) if lleno else (*SOMBRA, 170),
                  outline=(*claro(col, 0.5), 255) if not lleno else (*SOMBRA, 255), width=3)
    texto_sombra(img, (tx + w - 14 - 2 * 34 - 118, ty + 56), '2 DE 3', ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 26),
                 PLATA)
    rotulo(img, cam, cae + np.array([0.0, -1.0, 0]), 'LA OTRA YA CAE', -70, 80, 30, PLATA)
    guardar(img, 'desarme')


ESCENAS = {'ascenso': ascenso, 'campanas': campanas, 'ojo': ojo, 'desarme': desarme}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
        print('ok', nombre, flush=True)

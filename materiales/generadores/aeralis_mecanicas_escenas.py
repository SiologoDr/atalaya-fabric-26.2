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

Segunda ficha (de la primera Juan se queda solo la Rafaga Ladrona y pide mas
propuestas). Camaras mas cerca de los jugadores, para que se lean bien:

  rompevientos  Rompevientos: un vendaval cruza la cima; uno agachado de cara al
                viento levanta un arco cian y tres companeros en fila detras no
                se mueven (el viento pasa por encima); uno solo sale volando
  gemelos       Tornados Gemelos: dos tornados cian unidos por un hilo de viento
                y otra pareja magenta al fondo; un jugador en cada tornado cian
                da el ultimo golpe a la vez, con la regla de 1 s entre los dos
  cegador       Polvo Cegador: polvo de escamas violeta; dos ciegos (una esfera
                oscura en la cabeza) y su guia al lado, con el contorno blanco
                del efecto Brillante, que los saca por un camino en punteado de
                la zona roja que va a estallar
  hilos         Hilos del Viento: dos jugadores cuelgan de hilos de viento de sus
                patas a 8 bloques del suelo; abajo, tres arqueros tiran a los
                hilos: uno se rompe y otras dos flechas van de camino

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


# ======================================================================
#  Segunda ficha (octubre de 2026): Juan se queda la Rafaga Ladrona y pide
#  mas propuestas. Camaras mas cerca de los jugadores, que se lean bien.
# ======================================================================
nm.MAT.update({
    'arco': _plano('7a5230', '6a4626', 330),           # la madera del arco
    'cuerda': _plano('e8e4dc', 'd6d2ca', 331),
    'flecha': _plano('8a6a44', '7a5c3a', 332),
    'punta_flecha': _plano('b8bcc4', 'a0a4ac', 333),
})


def nodo_arco(nombre='arco_mano'):
    """Un arco en la mano izquierda: el puno en la mano, las palas en arco hacia
    delante (+y del brazo) y la cuerda tensa hacia el cuerpo."""
    cajas = [((-0.8, 9.0, -1.2, 1.6, 3.0, 2.4), 'arco')]
    for k in range(-4, 5):
        z = k * 2.2
        y = 11.5 + 3.2 * (1 - (k / 4.0) ** 2)
        cajas.append(((-0.6, y - 0.8, z - 1.2, 1.2, 1.6, 2.4), 'arco'))
    # la cuerda: de punta a punta, tirada hacia atras en el medio
    for k in range(-8, 9):
        z = k * 1.1
        y = 11.4 - 4.5 * (1 - abs(k) / 8.0)
        cajas.append(((-0.25, y - 0.3, z - 0.55, 0.5, 0.6, 1.1), 'cuerda'))
    return nm.nodo(nombre, (0, 0, 0), (0, 0, 0), cajas)


def jugador2(lz, cam, x, z, guinada, y=0.0, pose=None, espada=False, arco=False, rot_espada=(0, 0, 0), niebla=None,
             inclina=0.0, alabeo=0.0, lienzo_extra=None):
    """Como jugador(), con arco en la mano izquierda si se pide, alabeo (giro de
    lado, grados) y, si se pasa otro lienzo, se pinta tambien en el (para sacar
    su silueta)."""
    raiz = ne.jugador()
    if espada:
        _buscar(raiz, 'bd')[4].append(nodo_espada(rot=rot_espada))
    if arco:
        _buscar(raiz, 'bi')[4].append(nodo_arco())
    M = vr.T(x, y, z) @ vr.Ry(guinada * vr.D2R) @ vr.T(0, 1.0, 0) @ vr.Rz(alabeo * vr.D2R) @ vr.Rx(inclina * vr.D2R) \
        @ vr.T(0, -1.0, 0) @ vr.T(0, 1.5, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])
    qs = nm.quads(raiz, pose or {}, M)
    nm.dibujar(lz, cam, qs, LUCES, AMB, niebla)
    if lienzo_extra is not None:
        nm.dibujar(lienzo_extra, cam, qs, LUCES, AMB, None)


# Agachado: el torso hacia delante y mas bajo, las caderas atras y las piernas
# en diagonal hasta los pies (bajo el cuello), como un Shift exagerado.
AGACHADO = {'cuerpo': {'rot': (42, 0, 0), 'pos': (0, 5.5, 0)}, 'cabeza': {'rot': (-40, 0, 0)},
            'bi': {'rot': (-78, 0, -10)}, 'bd': {'rot': (-84, 0, 10)},
            'pi': {'rot': (-37, 0, 0), 'pos': (0, 2.4, 8.0)}, 'pd': {'rot': (-31, 0, 0), 'pos': (0, 2.4, 8.0)}}
# De pie aguantando: algo inclinado hacia el viento
AGUANTA = {'cuerpo': {'rot': (10, 0, 0)}, 'cabeza': {'rot': (-10, 0, 0)}, 'bi': {'rot': (-20, 0, -8)},
           'bd': {'rot': (-40, 0, 8)}, 'pi': {'rot': (-8, 0, 0)}, 'pd': {'rot': (8, 0, 0)}}
VOLANDO = {'cabeza': {'rot': (16, 0, 0)}, 'bi': {'rot': (-150, 0, -50)}, 'bd': {'rot': (-140, 0, 56)},
           'pi': {'rot': (-36, 0, 10)}, 'pd': {'rot': (30, 0, -8)}}
CIEGO = {'cabeza': {'rot': (16, 0, 0)}, 'bi': {'rot': (-82, 0, -14)}, 'bd': {'rot': (-88, 0, 12)},
         'pi': {'rot': (-16, 0, 0)}, 'pd': {'rot': (14, 0, 0)}}
GUIA = {'cabeza': {'rot': (0, 0, 0)}, 'bi': {'rot': (36, 0, -14)}, 'bd': {'rot': (-28, 0, 6)},
        'pi': {'rot': (-28, 0, 0)}, 'pd': {'rot': (26, 0, 0)}}
COLGADO = {'cabeza': {'rot': (24, 0, 0)}, 'bi': {'rot': (-168, 0, -16)}, 'bd': {'rot': (-160, 0, 18)},
           'pi': {'rot': (14, 0, 6)}, 'pd': {'rot': (-10, 0, -6)}}
ARQUERO = {'cabeza': {'rot': (-30, 0, 0)}, 'bi': {'rot': (-128, 0, 0)}, 'bd': {'rot': (-112, 0, 30)},
           'pi': {'rot': (-12, 0, 0)}, 'pd': {'rot': (12, 0, 0)}}


def tex_parapeto(color, w=64, h=64):
    """El rompevientos: una pared curva de viento, tenue por dentro, con el
    borde de arriba y los lados encendidos y hebras que se doblan."""
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    u, v = (xx + 0.5) / w, (yy + 0.5) / h
    a = 0.16 + 0.10 * (1 - v)
    a = np.maximum(a, np.exp(-(v / 0.06) ** 2))
    a = np.maximum(a, np.exp(-(u / 0.05) ** 2) * 0.8)
    a = np.maximum(a, np.exp(-((1 - u) / 0.05) ** 2) * 0.8)
    for k in range(6):
        y0 = 0.18 + k * 0.13
        a = np.maximum(a, np.exp(-((v - y0 - 0.06 * np.sin(u * math.pi * 2 + k)) / 0.012) ** 2) * 0.55)
    k = np.clip(a - 0.3, 0, 1)[..., None]
    col = np.array(color, float) * (1 - k) + 255 * k
    return _rgba(col, a)


def tex_sombra(n=64, color=(14, 8, 26), centro=0.82):
    """La ceguera: una esfera oscura alrededor de la cabeza (oscura hasta la
    mitad y luego se apaga)."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    a = np.clip((1 - d) / 0.45, 0, 1) ** 0.8 * centro
    return _rgba(np.ones((n, n, 3)) * np.array(color), a)


def tex_punto(color, n=32):
    """Un punto del camino, redondo y nitido."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    a = np.clip((1 - d) * 4, 0, 1)
    k = np.clip(1 - d * 1.6, 0, 1)[..., None] * 0.6
    return _rgba(np.array(color) * (1 - k) + 255 * k, a)


def contorno(img, lz_sil, color=(255, 255, 255), grueso=7, difuso=9, fuerza=1.0):
    """El contorno del efecto Brillante: una raya clara alrededor de la silueta
    (lz_sil solo tiene a quien brilla) y un halo suave por fuera."""
    W, H = img.size
    m = Image.fromarray((np.clip(lz_sil.alfa, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    mi = np.array(m, float) / 255
    gordo = np.array(m.filter(ImageFilter.MaxFilter(grueso)), float) / 255
    halo = np.array(m.filter(ImageFilter.MaxFilter(grueso + 6)).filter(ImageFilter.GaussianBlur(difuso)), float) / 255
    a = np.clip(np.maximum((gordo - mi) * 1.0, halo * 0.55) * (1 - mi) * fuerza, 0, 1)
    capa = np.zeros((H, W, 4), np.uint8)
    capa[..., :3] = color
    capa[..., 3] = (a * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(capa, 'RGBA'))


def chispazo(lz, cam, p, col, tam=1.0):
    brillo(lz, cam, [billboard(p, 1.3 * tam, cam)], tex_halo(col), 1.0)
    brillo(lz, cam, [billboard(p, 1.0 * tam, cam, 0.3)], CHISPA, 1.6)
    brillo(lz, cam, [billboard(p, 1.5 * tam, cam)], tex_onda(claro(col, 0.3), grueso=0.06), 0.9)


def tornado_color(lz, cam, x, z, alto, col, niebla, giro=0.0, r1=2.5, anillos=True, semilla=0):
    """Un tornado como los del juego (dos embudos y tres anillos), en un color."""
    trans(lz, cam, ve.tornado(x, z, alto, 0.25, r1 * 0.62, giro, anillos=16, segs=12),
          tex_viento2(oscuro(col, 0.35), 5 + semilla, densidad=0.9), 0.75, niebla, 0.05)
    trans(lz, cam, ve.tornado(x, z, alto * 1.04, 0.45, r1, giro + 1.0, anillos=18, segs=16),
          tex_viento2(col, 9 + semilla), 0.8, niebla, 0.14)
    if anillos:
        for hh in (0.3, 0.55, 0.8):
            rr = 0.45 + (r1 - 0.45) * hh ** 1.5 + 0.2
            aro = [(x + rr * math.cos(a), alto * hh, z + rr * math.sin(a)) for a in np.linspace(0, TAU, 25)]
            trans(lz, cam, cinta3d(aro, 0.05, cam), tex_plano(claro(col, 0.55)), 1.0, niebla, 0.5)
    r = random.Random(100 + semilla)
    esc = []
    for _ in range(14):
        a, hh = r.uniform(0, TAU), r.uniform(0.1, 0.9)
        rr = 0.45 + (r1 - 0.45) * hh ** 1.5
        esc.append(billboard((x + rr * math.cos(a), alto * hh, z + rr * math.sin(a)), r.uniform(0.07, 0.14), cam,
                             r.uniform(0, 3)))
    trans(lz, cam, esc, tex_plano((70, 66, 74)), 1.0, niebla, 0.0)


def hilo_viento(lz, cam, a, b, col, niebla, ancho=0.05, vueltas=3.0, radio=0.16, comba=0.0, glow=1.0, n=40):
    """Un hilo de viento de a a b: dos hebras que se enroscan y un nucleo
    claro; 'comba' lo hace caer en el medio."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    e1 = np.cross(d, [0, 1, 0])
    if np.linalg.norm(e1) < 1e-6:
        e1 = np.cross(d, [1, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d / L, e1)
    ts = np.linspace(0, 1, n)
    eje = [a + d * t - np.array([0, comba * math.sin(math.pi * t), 0]) for t in ts]
    trans(lz, cam, cinta3d(eje, ancho * 2.6, cam), tex_plano(col, 90), 0.6, niebla, 0.4 * glow)
    trans(lz, cam, cinta3d(eje, ancho * 0.7, cam), tex_plano(claro(col, 0.8)), 1.0, niebla, 1.2 * glow)
    for j in range(2):
        pts = [eje[i] + (e1 * math.cos(TAU * vueltas * t + j * math.pi) + e2 * math.sin(TAU * vueltas * t + j * math.pi))
               * radio for i, t in enumerate(ts)]
        trans(lz, cam, cinta3d(pts, ancho * 0.6, cam), tex_plano(claro(col, 0.5)), 1.0, niebla, 0.7 * glow)


def rafagas(lz, cam, r, n, x0, x1, ys, zs, colores, niebla, ancho=(0.05, 0.12), largo=(5, 13), desvio=None, glow=0.45):
    """Cintas de viento horizontales que van de +x a -x; 'desvio(p)' puede
    doblarlas (devuelve el punto movido) o cortarlas (None)."""
    for k in range(n):
        y, z = r.uniform(*ys), r.uniform(*zs)
        L = r.uniform(*largo)
        xa = r.uniform(x0, x1)
        fase_ = r.uniform(0, TAU)
        pts = []
        for t in np.linspace(0, 1, 14):
            p = np.array([xa - L * t, y + 0.18 * math.sin(fase_ + t * 5), z + 0.12 * math.sin(fase_ * 2 + t * 4)])
            if desvio is not None:
                p = desvio(p)
                if p is None:
                    break
            pts.append(p)
        if len(pts) < 4:
            continue
        c = colores[k % len(colores)]
        trans(lz, cam, cinta3d(pts, r.uniform(*ancho), cam), tex_cuchilla(c, 96, 16, k), r.uniform(0.55, 0.9), niebla,
              glow)


# ----------------------------------------------------------------------
#  5. Rompevientos
#
#  Un vendaval barre la cima de izquierda a derecha (en la foto). Un jugador
#  agachado de cara al viento levanta un rompevientos (un arco cian de luz) y
#  tres companeros en fila detras de el no se mueven: el viento pasa por
#  encima. Uno que se ha quedado solo sale volando, tumbado y con estelas.
# ----------------------------------------------------------------------
def rompevientos(W=1600, H=900, fase=2):
    col = COLOR_FASE[fase]
    escudo = (120, 236, 255)
    zf = 2.0                                    # la fila
    xa = 4.4                                    # el agachado, de cara al viento (+x)
    fila = [xa - 1.5, xa - 2.7, xa - 3.9]
    # la camara mira hacia +z, de lado a la fila: en la foto, +x queda a la
    # izquierda (de alli viene el viento)
    cam = vr.Camara(ojo=(1.6, 4.0, -6.6), objetivo=(1.2, 2.5, 6.0), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(24, 60)
    ve.suelo(lz, cam, niebla=niebla)
    for i, (x, z, alto, rota) in enumerate(((-15, 16, 5, True), (-20, 6, 3, True), (19, 12, 4, False))):
        nm.dibujar(lz, cam, ve.columna(x, z, alto, rota, i), LUCES, AMB, niebla)
    jugador2(lz, cam, xa, zf, guinada_hacia(1, -0.25), y=-0.02, pose=AGACHADO, niebla=niebla)
    for k, x in enumerate(fila):
        jugador2(lz, cam, x, zf + (0.12 if k % 2 else -0.1), guinada_hacia(1, -0.5), pose=AGUANTA, espada=True,
                 rot_espada=(55, 0, 0), niebla=niebla)
    # el que esta solo, mas atras y fuera de la fila: sale volando a la derecha
    solo = np.array([-4.6, 2.4, 5.0])
    jugador2(lz, cam, solo[0], solo[2], guinada_hacia(1, -0.6), y=solo[1], pose=VOLANDO, inclina=-50, alabeo=-28,
             niebla=niebla)
    # ella, al fondo a la izquierda: bate las alas y sopla
    ax_, az_ = 15.0, 40.0
    aeralis(lz, cam, 'despues', ax_, Y_VUELO_NUEVA + 1.0, az_, guinada_hacia(-0.8, -1.0), pose=rm.ALETEO, fase=fase,
            niebla=ve.NieblaCielo(40, 120))
    # la zona en calma detras del rompevientos, en el suelo
    for k in range(10):
        x0, x1 = xa + 0.5 - k * 0.6, xa + 0.5 - (k + 1) * 0.6
        an = 1.2 + 0.04 * k
        q = [([(x0, 0.07, zf - an), (x1, 0.07, zf - an), (x1, 0.07, zf + an), (x0, 0.07, zf + an)],
              [(0, 0), (1, 0), (1, 1), (0, 1)])]
        trans(lz, cam, q, tex_plano(escudo, int(90 * (1 - k / 10))), 0.9, None, 0.2 * (1 - k / 10))
    # el rompevientos: un arco de luz delante del agachado (del lado del viento)
    arco = []
    R_, alto_ = 1.25, 2.1
    segs = 16
    for s_ in range(segs):
        a0 = -1.3 + 2.6 * s_ / segs
        a1 = -1.3 + 2.6 * (s_ + 1) / segs
        p0 = (xa + R_ * math.cos(a0), zf + R_ * math.sin(a0))
        p1 = (xa + R_ * math.cos(a1), zf + R_ * math.sin(a1))
        arco.append(([(p0[0], 0.02, p0[1]), (p1[0], 0.02, p1[1]), (p1[0], alto_, p1[1]), (p0[0], alto_, p0[1])],
                     [(s_ / segs, 1), ((s_ + 1) / segs, 1), ((s_ + 1) / segs, 0), (s_ / segs, 0)]))
    trans(lz, cam, arco, tex_parapeto(escudo), 0.6, None, 0.22)
    borde = [(xa + R_ * math.cos(a), alto_, zf + R_ * math.sin(a)) for a in np.linspace(-1.3, 1.3, 24)]
    trans(lz, cam, cinta3d(borde, 0.04, cam), tex_plano(claro(escudo, 0.6)), 1.0, None, 1.0)
    # el vendaval: cintas que cruzan la cima; las que no pasan por la fila
    # se cortan antes de llegar a ella (el aire alli esta en calma)
    def desvio(p):
        if abs(p[2] - zf) < 1.9 and p[1] < 2.9 and xa - 7.0 < p[0] < xa + 1.3:
            return None
        return p
    r = random.Random(7)
    blancos = [BLANCO, (200, 240, 255), claro(escudo, 0.3)]
    # detras de la fila (lo mas) y en lo alto
    rafagas(lz, cam, r, 66, -10, 26, (0.3, 6.5), (zf + 1.9, 18), blancos, niebla, desvio=desvio, glow=0.35)
    # por delante de la fila, finas: a ras de suelo o por encima de las cabezas
    rafagas(lz, cam, r, 12, -8, 20, (3.6, 5.5), (-2.0, zf - 1.9), blancos, niebla, ancho=(0.03, 0.05), glow=0.25)
    rafagas(lz, cam, r, 10, -8, 20, (0.1, 0.4), (-2.5, zf - 1.9), blancos, niebla, ancho=(0.03, 0.05), glow=0.25)
    # las que llegan al rompevientos: chocan, suben por el arco y pasan por
    # encima de la fila, cada una a su altura
    for k in range(7):
        z = zf + r.uniform(-0.9, 0.9)
        y = r.uniform(0.4, 1.9)
        h = r.uniform(3.0, 3.9)
        pts = []
        for t in np.linspace(0, 1, 30):
            x = xa + 9.0 - 17.0 * t
            u = (xa + 1.4 - x) / 1.6                 # 0 en el arco, 1 encima de el
            sube = 0.5 - 0.5 * math.cos(math.pi * min(1.0, max(0.0, u)))
            baja = 0.5 - 0.5 * math.cos(math.pi * min(1.0, max(0.0, (xa - 5.0 - x) / 3.0)))
            yy = y + (h - y) * sube - (h - y) * 0.45 * baja
            pts.append(np.array([x, yy, z + 0.4 * (z - zf) * sube]))
        trans(lz, cam, cinta3d(pts, 0.07, cam), tex_cuchilla(BLANCO, 96, 16, 40 + k), 0.85, niebla, 0.5)
    # alrededor del que vuela: estelas que lo empujan
    for k in range(8):
        y = solo[1] + r.uniform(-1.0, 1.4)
        z = solo[2] + r.uniform(-0.8, 0.8)
        x0 = solo[0] + r.uniform(1.5, 4.5)
        pts = [np.array([x0 - 7 * t, y + 0.6 * t, z]) for t in np.linspace(0, 1, 10)]
        trans(lz, cam, cinta3d(pts, 0.06, cam), tex_cuchilla(BLANCO, 96, 16, 60 + k), 0.9, niebla, 0.6)
    img = componer(lz, cam, W, H, 71, fase, rayos=0.4, estelas=80)
    rotulo(img, cam, (xa - 0.1, 1.0, zf - 0.3), 'SE AGACHA: PARA EL VIENTO', -30, 190, 40, claro(escudo, 0.35))
    rotulo(img, cam, (fila[1], 2.1, zf), '¡DETRÁS DE ÉL!', 20, -190, 50, BLANCO)
    rotulo(img, cam, (solo[0], solo[1] + 0.6, solo[2]), 'SOLO: TE LLEVA', -10, -160, 40, claro(ROJO, 0.4))
    guardar(img, 'rompevientos')


# ----------------------------------------------------------------------
#  6. Tornados Gemelos
#
#  Dos tornados cian unidos por un hilo de viento (una pareja) y, mas lejos,
#  otra pareja magenta. Un jugador en cada tornado cian: los dos dan el
#  ultimo golpe a la vez (chispas en los dos) y, entre ellos, el margen: 1 s.
# ----------------------------------------------------------------------
def pildora(img, cx, cy, texto, tam, color, fondo=(8, 10, 30, 200), borde=(150, 160, 230, 200)):
    """Un texto dentro de una pastilla redondeada, centrado en (cx, cy)."""
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', tam)
    d = ImageDraw.Draw(img)
    w = d.textlength(texto, font=f)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).rounded_rectangle((cx - w / 2 - 18, cy - tam * 0.62, cx + w / 2 + 18, cy + tam * 0.72),
                                           int(tam * 0.6), fill=fondo, outline=borde, width=3)
    img.alpha_composite(capa)
    texto_sombra(img, (cx - w / 2, cy - tam * 0.68), texto, f, color)


def gemelos(W=1600, H=900, fase=3):
    par_a, par_b = (110, 225, 255), MAGENTA
    # la camara mira hacia +z: en la foto, +x queda a la izquierda
    cam = vr.Camara(ojo=(0.0, 3.0, -7.0), objetivo=(0.0, 3.7, 8.0), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(24, 60)
    ve.suelo(lz, cam, niebla=niebla)
    for i, (x, z, alto, rota) in enumerate(((-16, 18, 5, True), (17, 16, 3, True), (21, 4, 4, False))):
        nm.dibujar(lz, cam, ve.columna(x, z, alto, rota, i), LUCES, AMB, niebla)
    za, xa = 4.0, 4.5                          # la pareja de cerca
    zb, xb = 26.0, 3.6                         # la de lejos, entre las dos de cerca
    alto_a, alto_b = 6.5, 7.0
    # un jugador en cada tornado de cerca, por fuera, dando el golpe
    golpes = []
    for sgn in (1, -1):
        tx = sgn * xa
        px, pz = sgn * (xa + 2.2), za - 1.0
        jugador2(lz, cam, px, pz, guinada_hacia(tx - px, za - pz), pose=GOLPE_ALTO, espada=True,
                 rot_espada=(-60, 0, 0), niebla=niebla)
        d = np.array([px - tx, 0.0, pz - za])
        d /= np.linalg.norm(d)
        golpes.append(np.array([tx, 1.8, za]) + d * 0.9)
    # dos jugadores lejos, junto a la otra pareja
    for sgn in (1, -1):
        px, pz = sgn * (xb + 2.2), zb - 1.5
        jugador2(lz, cam, px, pz, guinada_hacia(sgn * xb - px, zb - pz), pose=JUNTOS, espada=True, niebla=niebla)
    aeralis(lz, cam, 'despues', 0.0, 12.0, 44.0, guinada_hacia(cam.ojo[0], cam.ojo[2] - 44.0), pose=rm.HEROICA,
            fase=fase, niebla=ve.NieblaCielo(40, 120))
    # las parejas: de lejos a cerca (lo translucido, de atras a delante)
    for (xt, zt, alto, c, sem) in ((xb, zb, alto_b, par_b, 20), (xa, za, alto_a, par_a, 0)):
        for sgn in (1, -1):
            trans(lz, cam, cuadrado_suelo(sgn * xt, zt, 2.1), tex_aro(c, 128, 0.07, 20, 30), 0.8, niebla, 0.3)
            tornado_color(lz, cam, sgn * xt, zt, alto, c, niebla, giro=0.7 * sgn + sem * 0.1, r1=1.8,
                          semilla=sem + (sgn > 0))
        hy = alto * (0.75 if zt < 10 else 0.64)
        hilo_viento(lz, cam, (xt - 1.0, hy, zt), (-xt + 1.0, hy, zt), c, niebla, ancho=0.06 if zt < 10 else 0.11,
                    vueltas=4.0, radio=0.17 if zt < 10 else 0.25, comba=0.4, glow=1.3)
        r = random.Random(sem + 3)
        motas = [billboard((r.uniform(-xt + 1, xt - 1), hy - 0.3 + r.uniform(-0.4, 0.4), zt + r.uniform(-0.3, 0.3)),
                           0.06, cam, r.uniform(0, 3)) for _ in range(30)]
        trans(lz, cam, motas, tex_plano(claro(c, 0.6)), 1.0, niebla, 1.0)
    for g in golpes:
        chispazo(lz, cam, g, par_a, 0.75)
    img = componer(lz, cam, W, H, 81, fase, rayos=0.6, estelas=50)
    # entre los dos golpes: la regla de 1 s
    g1, g2 = pantalla(cam, golpes[0]), pantalla(cam, golpes[1])
    y_reg = max(g1[1], g2[1]) + 70
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    for (x0, y0, x1, y1) in ((g1[0], y_reg, g2[0], y_reg), (g1[0], g1[1] + 30, g1[0], y_reg + 16),
                             (g2[0], g2[1] + 30, g2[0], y_reg + 16)):
        dc.line([(x0, y0), (x1, y1)], fill=(*SOMBRA, 180), width=8)
        dc.line([(x0, y0), (x1, y1)], fill=(*claro(par_a, 0.5), 255), width=4)
    img.alpha_composite(capa)
    cx = (g1[0] + g2[0]) / 2
    pildora(img, cx, y_reg, '1 S', 50, BLANCO, borde=(*claro(par_a, 0.3), 230))
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 64)
    w = ImageDraw.Draw(img).textlength('¡A LA VEZ!', font=f)
    texto_sombra(img, (cx - w / 2, y_reg + 50), '¡A LA VEZ!', f, BLANCO)
    hy = alto_a * 0.75
    rotulo(img, cam, (0.0, hy - 0.4, za), 'GEMELOS', 0, -120, 50, claro(par_a, 0.45), centro=True)
    guardar(img, 'gemelos')


# ----------------------------------------------------------------------
#  7. Polvo Cegador
#
#  Ella sacude las alas y cae un polvo de escamas violeta que brilla. Dos
#  jugadores quedan ciegos (una esfera oscura alrededor de la cabeza, con los
#  brazos por delante, a tientas); cada uno tiene a su guia al lado, con el
#  contorno blanco del efecto Brillante, que va delante y lo saca de la zona
#  roja que va a estallar (el camino en punteado).
# ----------------------------------------------------------------------
def camino_puntos(lz, cam, pts, color, paso=0.55, tam=0.13, flecha=True):
    """Un camino en punteado por el suelo, con una punta de flecha al final."""
    pts = [np.array(p, float) for p in pts]
    seg = []
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.linalg.norm(b - a) / 0.05))
        seg += [a + (b - a) * t for t in np.linspace(0, 1, n, endpoint=False)]
    seg.append(pts[-1])
    acum, sig, puntos = 0.0, 0.0, []
    for a, b in zip(seg[:-1], seg[1:]):
        if acum >= sig:
            puntos.append(a)
            sig += paso
        acum += np.linalg.norm(b - a)
    tp = tex_punto(color)
    for q in puntos[:-1]:
        trans(lz, cam, cuadrado_suelo(q[0], q[1], tam, y=0.09), tp, 1.0, None, 0.9)
    if flecha:
        fin, ant = seg[-1], seg[-8]
        d = (fin - ant) / np.linalg.norm(fin - ant)
        lado = np.array([-d[1], d[0]])
        P = [fin + d * 0.45, fin - d * 0.2 + lado * 0.45, fin - d * 0.02, fin - d * 0.2 - lado * 0.45]
        trans(lz, cam, [([(q[0], 0.09, q[1]) for q in P], [(0.5, 0.5), (0.5, 0.5), (0.5, 0.5), (0.5, 0.5)])],
              tex_plano(color), 1.0, None, 0.9)


def cegador(W=1600, H=900, fase=2):
    polvo = (196, 150, 255)
    guia_c = (255, 255, 255)
    # la camara mira hacia +z algo desde arriba: en la foto, +x queda a la izquierda
    cam = vr.Camara(ojo=(0.4, 4.4, -7.6), objetivo=(0.0, 2.0, 6.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    lz_guia = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(24, 60)
    ve.suelo(lz, cam, niebla=niebla)
    for i, (x, z, alto, rota) in enumerate(((-15, 16, 5, True), (16, 14, 3, True), (-20, 4, 4, False))):
        nm.dibujar(lz, cam, ve.columna(x, z, alto, rota, i), LUCES, AMB, niebla)
    # las dos parejas: (ciego, su guia, el centro de la zona roja, hacia donde salen)
    parejas = [((3.7, 3.6), (2.0, 1.6), (4.6, 4.8), (0.6, -0.1)),
               ((-4.4, 3.4), (-2.4, 2.5), (-5.4, 4.6), (-0.9, 0.7))]
    zonas = []
    for ciego, guia, zona, sale in parejas:
        zonas.append(zona)
        g_ciego = guinada_hacia(guia[0] - ciego[0], guia[1] - ciego[1])
        jugador2(lz, cam, ciego[0], ciego[1], g_ciego, pose=CIEGO, niebla=niebla)
        g_guia = guinada_hacia(sale[0] - guia[0], sale[1] - guia[1])
        pose = dict(GUIA)
        pose['cabeza'] = {'rot': (0, 38 if ciego[0] > 0 else -38, 0)}
        pose['bi' if ciego[0] > 0 else 'bd'] = {'rot': (34, 0, -14 if ciego[0] > 0 else 14)}
        pose['bd' if ciego[0] > 0 else 'bi'] = {'rot': (-30, 0, 6 if ciego[0] > 0 else -6)}
        jugador2(lz, cam, guia[0], guia[1], g_guia, pose=pose, espada=True, niebla=niebla, lienzo_extra=lz_guia)
    # dos mas lejos, peleando
    for x, z in ((8.0, 12.0), (-9.0, 13.0)):
        jugador2(lz, cam, x, z, guinada_hacia(-x * 0.2, 30 - z), pose=GOLPE_ALTO, espada=True, rot_espada=(-60, 0, 0),
                 niebla=niebla)
    aeralis(lz, cam, 'despues', 1.0, 3.0, 36.0, guinada_hacia(cam.ojo[0] - 1.0, cam.ojo[2] - 36.0), pose=rm.ESCAMAS,
            fase=fase, niebla=ve.NieblaCielo(40, 120))
    # las zonas rojas que van a estallar
    r = random.Random(9)
    for k, (zx, zz) in enumerate(zonas):
        trans(lz, cam, cuadrado_suelo(zx, zz, 2.7), tex_aro(ROJO, 128, 0.07, 16, 70), 0.95, None, 0.9)
        brillo(lz, cam, cuadrado_suelo(zx, zz, 2.5, y=0.1), tex_halo(ROJO, 128, 1.4), 0.35)
        for j in range(5):
            a = r.uniform(0, TAU)
            pts = rayo((zx, 0.1, zz), (zx + 2.2 * math.cos(a), 0.1, zz + 2.2 * math.sin(a)), 200 + k * 10 + j, 6, 0.25)
            pts = [(q[0], 0.1, q[2]) for q in pts]
            trans(lz, cam, cinta3d(pts, 0.035, cam), tex_plano(claro(ROJO, 0.4)), 1.0, None, 1.0)
        ascuas = [billboard((zx + r.uniform(-2.2, 2.2), r.uniform(0.2, 1.8), zz + r.uniform(-2.2, 2.2)), 0.05, cam,
                            r.uniform(0, 3)) for _ in range(26)]
        brillo(lz, cam, ascuas, tex_halo(claro(ROJO, 0.3), 16, 1.0), 1.4)
    # el camino de cada guia, en punteado, desde el ciego hasta fuera de la zona
    for ciego, guia, zona, sale in parejas:
        medio = (np.array(ciego) + np.array(guia)) / 2 + np.array([0.25, -0.15])
        camino_puntos(lz, cam, [ciego, medio, guia, sale], (255, 236, 170), tam=0.16)
    # el polvo: un velo violeta y escamas que brillan, sobre todo alrededor de los ciegos
    cielo_polvo = []
    for ciego, guia, zona, sale in parejas:
        for _ in range(9):
            q = (ciego[0] + r.uniform(-1.8, 1.8), r.uniform(0.6, 3.2), ciego[1] + r.uniform(-1.5, 1.8))
            cielo_polvo.append(billboard(q, r.uniform(0.9, 1.6), cam, r.uniform(0, 3)))
    trans(lz, cam, cielo_polvo, tex_halo(polvo, 64, 1.6), 0.22, niebla, 0.12)
    escamas = []
    for ciego, guia, zona, sale in parejas:
        for _ in range(120):
            q = (ciego[0] + r.gauss(0, 1.3), r.uniform(0.2, 3.6), ciego[1] + r.gauss(0, 1.3))
            escamas.append(billboard(q, r.uniform(0.05, 0.11), cam, r.uniform(0, 3)))
    for _ in range(160):
        q = (r.uniform(-12, 12), r.uniform(0.5, 9), r.uniform(-1, 26))
        escamas.append(billboard(q, r.uniform(0.04, 0.09), cam, r.uniform(0, 3)))
    cabezas = [np.array([c[0], 1.78, c[1]]) for c, _, _, _ in parejas]
    escamas = [q for q in escamas if min(np.linalg.norm(np.mean(q[0], axis=0) - c) for c in cabezas) > 0.75]
    brillo(lz, cam, escamas, tex_chispa(32, claro(polvo, 0.4)), 1.3)
    # la ceguera: una esfera oscura alrededor de la cabeza de cada ciego
    for ciego, guia, zona, sale in parejas:
        cab = np.array([ciego[0], 1.78, ciego[1]])
        # delante de la cabeza, para que la tape (lo translucido no tapa lo que tiene delante)
        cab = cab + (cam.ojo - cab) / np.linalg.norm(cam.ojo - cab) * 0.7
        trans(lz, cam, [billboard(cab, 0.8, cam)], tex_sombra(centro=0.9), 1.0, None, 0.0)
        brillo(lz, cam, [billboard(cab, 0.8, cam)], tex_onda(polvo, grueso=0.07), 0.4)
    img = componer(lz, cam, W, H, 91, fase, rayos=0.4, estelas=40)
    contorno(img, lz_guia, guia_c, grueso=9, difuso=10)
    c1, g1, z1, s1 = parejas[0]
    c2, g2, z2, s2 = parejas[1]
    rotulo(img, cam, (c1[0], 2.3, c1[1]), 'CIEGO', 40, -150, 46, claro(polvo, 0.45))
    rotulo(img, cam, (g1[0] + 0.15, 1.1, g1[1]), 'SU GUÍA', -120, 120, 46, BLANCO)
    rotulo(img, cam, (s2[0], 0.1, s2[1]), '¡SÍGUELO!', 90, 50, 46, (255, 236, 170))
    guardar(img, 'cegador')


# ----------------------------------------------------------------------
#  8. Hilos del Viento
#
#  Aeralis vuela con dos jugadores colgando bajo ella de hilos de viento
#  (dos por jugador, de sus patas a los hombros), a unos 8 bloques del suelo.
#  Abajo, tres companeros les tiran flechas a los hilos: uno ya se rompe
#  (chispas y los dos cabos sueltos) y otras dos flechas van de camino.
# ----------------------------------------------------------------------
def flecha(lz, cam, a, b, k=0.82, niebla=None, color=BLANCO):
    """Una flecha que va de a hacia b: la estela hasta donde va (k del camino)
    y la flecha, con su punta y sus plumas."""
    a, b = np.array(a, float), np.array(b, float)
    d = (b - a) / np.linalg.norm(b - a)
    pos = a + (b - a) * k
    estela = [a + (pos - a) * t for t in np.linspace(0.2, 0.97, 12)]
    trans(lz, cam, cinta3d(estela, 0.12, cam), tex_cuchilla(color, 96, 16, 5), 0.8, niebla, 0.8)
    trans(lz, cam, cinta3d([pos - d * 1.3, pos], 0.05, cam), tex_plano((122, 92, 58)), 1.0, niebla, 0.0)
    trans(lz, cam, cinta3d([pos - d * 1.3, pos - d * 0.95], 0.13, cam), tex_plano((240, 240, 240)), 1.0, niebla, 0.3)
    trans(lz, cam, cinta3d([pos - d * 0.02, pos + d * 0.25], 0.1, cam), tex_plano((210, 216, 226)), 1.0, niebla, 0.4)
    brillo(lz, cam, [billboard(pos, 0.4, cam)], tex_halo(color, 32, 1.4), 0.8)
    return pos


def hilos(W=1600, H=900, fase=3):
    hc = (150, 235, 255)
    # la camara, abajo detras de los arqueros, mira hacia arriba (+z)
    cam = vr.Camara(ojo=(-0.8, 2.4, -1.0), objetivo=(0.2, 8.8, 14.0), fov=64, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    lz_atrapados = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(28, 70)
    ve.suelo(lz, cam, niebla=niebla)
    for i, (x, z, alto, rota) in enumerate(((-16, 18, 5, True), (17, 16, 3, True), (21, 4, 4, False))):
        nm.dibujar(lz, cam, ve.columna(x, z, alto, rota, i), LUCES, AMB, niebla)
    ax_, ay_, az_ = 0.3, 6.9, 13.5
    g_ae = guinada_hacia(cam.ojo[0] - ax_, cam.ojo[2] - az_) + 14
    # las patas de delante, abiertas y hacia abajo: de ellas cuelgan los hilos
    pose = dict(rm.HEROICA)
    pose.update({'pata0_izq': {'rot': (20, 0, -45)}, 'pata0_izq_tibia': {'rot': (40, 0, 0)},
                 'pata0_der': {'rot': (20, 0, 45)}, 'pata0_der_tibia': {'rot': (40, 0, 0)}})
    aeralis(lz, cam, 'despues', ax_, ay_, az_, g_ae, pose=pose, fase=fase, niebla=niebla)
    M = vr.T(0, ay_, 0) @ vr.entidad_a_mundo(ax_, 0, az_, g_ae)
    Ms = rm.matrices(pose)

    def punta(nombre, local):
        return (M @ Ms[nombre] @ np.array([*local, 1.0]))[:3]

    def ent(izq, alto, frente):
        """Del espacio de la entidad en bloques (izquierda, alto, frente) al mundo."""
        return (M @ np.array([izq * 16, 24.016 - alto * 16, -frente * 16, 1.0]))[:3]
    # los dos colgados, delante de ella y a 8 bloques del suelo; cada uno de
    # dos hilos: la pata de delante y la del medio de su lado
    colgados = []
    for s_ in (1, -1):
        pie = ent(2.5 * s_, 0.0, 4.2)
        pie[1] = 7.0
        anclas = [punta('pata0_izq_garra' if s_ > 0 else 'pata0_der_garra', (0, 11, 0)),
                  punta('pata1_der_garra' if s_ > 0 else 'pata1_izq_garra', (0, 9, 0))]
        colgados.append((pie, anclas))
    colgados.sort(key=lambda q: -q[0][0])           # el de la izquierda de la foto, primero
    hombros = []
    for k, (pie, anclas) in enumerate(colgados):
        g = guinada_hacia(cam.ojo[0] - pie[0], cam.ojo[2] - pie[2]) + (20 if k else -20)
        jugador2(lz, cam, pie[0], pie[2], g, y=pie[1], pose=COLGADO, espada=True, rot_espada=(40, 0, 0),
                 alabeo=6 if k else -6, niebla=niebla, lienzo_extra=lz_atrapados)
        lado = np.array([-math.cos(math.radians(g)), 0, math.sin(math.radians(g))]) * 0.32
        hombros.append([pie + np.array([0, 1.55, 0]) + lado, pie + np.array([0, 1.55, 0]) - lado])
    # que hombro va con que ancla: el mas cercano
    for k, (pie, anclas) in enumerate(colgados):
        if np.linalg.norm(anclas[0] - hombros[k][0]) > np.linalg.norm(anclas[0] - hombros[k][1]):
            hombros[k] = hombros[k][::-1]
    # los arqueros, abajo, apuntando a los hilos
    arqueros = [(3.4, 7.6), (-0.2, 6.8), (-3.8, 7.8)]
    # a que apunta cada uno: (colgado, hilo, la flecha ya ha llegado)
    blancos_ = [(0, 0, True), (0, 1, False), (1, 0, False)]
    puntos_blanco = []
    for (x, z), (ic, ih, llego) in zip(arqueros, blancos_):
        a, b = colgados[ic][1][ih], hombros[ic][ih]
        blanco = a + (b - a) * ((0.78 if llego else 0.6) if ih == 0 else 0.5)
        puntos_blanco.append(blanco)
        jugador2(lz, cam, x, z, guinada_hacia(blanco[0] - x, blanco[2] - z), pose=ARQUERO, arco=True, niebla=niebla)
    # los hilos: dos por colgado, de la punta de la pata al hombro; uno roto
    for ic, (pie, anclas) in enumerate(colgados):
        for ih in range(2):
            a, b = anclas[ih], hombros[ic][ih]
            if (ic, ih) == (0, 0):
                corte = puntos_blanco[0]
                d = (b - a) / np.linalg.norm(b - a)
                fuera = np.array([1.0, 0, 0])
                arriba = [a + (corte - d * 0.55 - a) * t + fuera * 0.7 * t ** 2 for t in np.linspace(0, 1, 14)]
                abajo = [corte + d * 0.55 + (b - corte - d * 0.55) * t + fuera * 0.8 * (1 - t) ** 2
                         for t in np.linspace(0, 1, 14)]
                for tramo in (arriba, abajo):
                    trans(lz, cam, cinta3d(tramo, 0.08, cam), tex_plano(hc, 90), 0.6, niebla, 0.5)
                    trans(lz, cam, cinta3d(tramo, 0.03, cam), tex_plano(claro(hc, 0.7)), 1.0, niebla, 1.1)
                chispazo(lz, cam, corte, hc, 0.9)
                r = random.Random(3)
                trozos = [billboard(corte + np.array([r.uniform(-0.8, 0.8), r.uniform(-0.6, 0.6), r.uniform(-0.4, 0.4)]),
                                    0.05, cam, r.uniform(0, 3)) for _ in range(22)]
                brillo(lz, cam, trozos, tex_halo(claro(hc, 0.4), 16, 1.0), 1.5)
            else:
                hilo_viento(lz, cam, a, b, hc, niebla, ancho=0.065, vueltas=5, radio=0.09, glow=1.3)
        # el lazo de viento alrededor del pecho
        c = pie + np.array([0, 1.25, 0])
        aro = [c + np.array([0.45 * math.cos(t), 0.08 * math.sin(t * 2), 0.35 * math.sin(t)]) for t in np.linspace(0, TAU, 25)]
        trans(lz, cam, cinta3d(aro, 0.035, cam), tex_plano(claro(hc, 0.6)), 1.0, niebla, 1.0)
    # las flechas
    en_vuelo = []
    for (x, z), (ic, ih, llego), blanco in zip(arqueros, blancos_, puntos_blanco):
        g = guinada_hacia(blanco[0] - x, blanco[2] - z)
        fr = np.array([-math.sin(math.radians(g)), 0, -math.cos(math.radians(g))])
        salida = np.array([x, 1.9, z]) + fr * 0.6
        if llego:
            estela = [salida + (blanco - salida) * t for t in np.linspace(0.3, 0.95, 10)]
            trans(lz, cam, cinta3d(estela, 0.1, cam), tex_cuchilla(BLANCO, 96, 16, 9), 0.7, niebla, 0.7)
        else:
            en_vuelo.append(flecha(lz, cam, salida, blanco, k=0.7 if ih else 0.58, niebla=niebla))
    img = componer(lz, cam, W, H, 101, fase, rayos=0.6, estelas=40)
    # los atrapados brillan con el viento que los envuelve: se leen sobre las alas
    contorno(img, lz_atrapados, claro(hc, 0.3), grueso=7, difuso=8)
    pie2, anclas2 = colgados[1]
    rotulo(img, cam, anclas2[0] + (hombros[1][0] - anclas2[0]) * 0.4, 'HILOS', 130, -30, 50, claro(hc, 0.4))
    rotulo(img, cam, en_vuelo[0], '¡CORTADLOS!', -110, 20, 52, BLANCO)
    rotulo(img, cam, pie2 + np.array([0, 0.3, 0]), 'SI NO, LOS SUELTA ARRIBA', 50, 120, 38, claro(ROJO, 0.4))
    guardar(img, 'hilos')


ESCENAS = {'ascenso': ascenso, 'campanas': campanas, 'ojo': ojo, 'desarme': desarme,
           'rompevientos': rompevientos, 'gemelos': gemelos, 'cegador': cegador, 'hilos': hilos}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
        print('ok', nombre, flush=True)

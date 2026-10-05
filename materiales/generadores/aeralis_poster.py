"""
Poster promocional de Aeralis, la Mariposa del Vendaval, en la Cima del
Vendaval con la tormenta encima. Presenta al jefe: ella grande a la derecha,
su nombre a la izquierda y nada mas (ni jugadores ni lista de ataques).

Aeralis en la fase III (Tempestad), con la camara baja mirandola desde
abajo: las alas abiertas de par en par, los rayos saltando entre ellas, el
ojo de la tormenta encendido en el pecho y los colmillos abiertos hacia quien
mira. A su alrededor sube en espiral el viento de su vendaval (por detras de
ella; por delante solo le pasa por el abdomen y las cintas), dos tornados la
flanquean en la meseta y una cuchilla del Aleteo viene de frente hacia quien
mira. Detras, las nubes giran alrededor del ojo de la tormenta. Arriba, su
barra de jefe tal cual sale en el juego.

Todo lo que sale esta hecho para el mod: la malla del juego con su atlas y su
capa de brillo (vendaval_juego.py), los tornados y la cuchilla con la forma y
las texturas que usa el juego (TornadoAeralisRenderer, CuchillaVientoRenderer),
el viento del vendaval (una textura en pixeles pintada aqui), el cielo, la
meseta, las particulas propias y la barra. Las fuentes son las del sistema.

Uso: python aeralis_poster.py <raiz del proyecto> <salida.png> [escala]
"""
import math, os, sys, random, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ, SALIDA = sys.argv[1], sys.argv[2]
ESCALA = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['VENDAVAL_SIN_FISICA'] = '1'
_argv = sys.argv
sys.argv = [_argv[0], RAIZ, tempfile.mkdtemp()]
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne
import vendaval_juego as vj
import vendaval_juego_anim as va
import viento_escenas as vs
sys.argv = _argv

A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
P = os.path.join(A, 'particle')
GUI = os.path.join(A, 'gui')
FUENTES = 'C:/Windows/Fonts/'
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
SS = 2
FASE = 3

CIELO = (120, 214, 255, 255)
VIOLETA = (190, 140, 255, 255)
BLANCO = (240, 244, 252, 255)
GRIS = (184, 194, 214, 255)


def fuente(nombre, tam):
    return ImageFont.truetype(FUENTES + nombre, int(tam * ESCALA))


def px(n):
    return int(round(n * ESCALA))


# ----------------------------------------------------------------------
#  La pose: las alas abiertas de par en par hacia quien mira, la cabeza
#  baja clavando los ojos, los colmillos abiertos, las patas delanteras
#  alzadas y el abdomen curvado hacia delante como un insecto de presa, con
#  las cintas de viento ondeando a los lados.
# ----------------------------------------------------------------------
def pose_poster():
    return va.sumar(va.alas(16, 46, (12, 26), giro=-10), va.antenas(-8, 22), va.colmillos(32), va.abdomen(-14, -22),
                    va.patas(-34, -14, -10), {'cabeza': va.r(20, -4, 0), 'torax': va.r(-4, 4, 0),
                                              'cinta_izq': va.r(-30, 0, -70), 'cinta_der': va.r(-20, 0, 55)})


# ----------------------------------------------------------------------
#  Escena: camara baja en la meseta, mirando hacia arriba
# ----------------------------------------------------------------------
AERALIS_EN = (4.5, 3.0, 5.0)
GUINADA = float(os.environ.get('GUINADA', '34'))         # de frente a la camara
CAM = vr.Camara(ojo=(-7.0, 0.7, -12.8), objetivo=(float(os.environ.get('OBJ_X', '8.4')), 10.6, 2.0), fov=56,
                ancho=W * SS, alto=H * SS)
LUCES = [
    ((-0.4, 1.0, -0.7), (0.82, 0.88, 1.0), 1.1, 'llave'),      # la luz plana de la tormenta
    ((0.8, 0.4, 0.7), (0.66, 0.42, 1.0), 1.35, 'contra'),      # los rayos la recortan en violeta
    ((-0.9, 0.2, 0.5), (0.35, 0.82, 1.0), 1.1, 'contra'),      # el cielo, en cian
]
AMBIENTE = (0.19, 0.2, 0.31)


def sumar(base, capa, k=1.0):
    f = np.array(base).astype(float)
    f[..., :3] = np.clip(f[..., :3] + np.array(capa).astype(float)[..., :3] * k, 0, 255)
    return Image.fromarray(f.astype(np.uint8))


def sprite(nombre, ancho, alto=None):
    return Image.open(os.path.join(P, nombre)).convert('RGBA').resize((max(1, ancho), max(1, alto or ancho)), Image.NEAREST)


def pantalla(p):
    """Del mundo al poster: (x, y) en pixeles de la imagen final y la profundidad."""
    sx, sy, z = CAM.proyectar(np.asarray(p, float))
    return sx / SS, sy / SS, z


def desproyectar(sx, sy, prof):
    """El punto del mundo que cae en (sx, sy) del poster (medido en 1920x1080) a "prof" bloques de la camara."""
    x = (sx * ESCALA * SS - CAM.W / 2) * prof / CAM.foco
    y = (CAM.H / 2 - sy * ESCALA * SS) * prof / CAM.foco
    return CAM.ojo + CAM.f * prof + CAM.r * x + CAM.u * y


def delante_del_eje(p):
    """Si un punto queda entre la camara y el eje de Aeralis (a su misma altura)."""
    eje = np.array([AERALIS_EN[0], p[1], AERALIS_EN[2]])
    return (np.asarray(p) - eje) @ CAM.f < 0


def a_imagen(arr):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    return im.resize((W, H), Image.LANCZOS)


def flotante(im):
    return np.array(im).astype(float) / 255.0


# ----------------------------------------------------------------------
#  El viento hecho malla. Todo lo traslucido (alas, cintas, tornados, el
#  vendaval y la cuchilla) va a una lista de velos que se pintan juntos de
#  atras a delante, para que se tapen bien entre ellos.
#  Un velo: (cuatro puntos, sus UV, textura, tinte, opacidad, brillo, mosaico)
# ----------------------------------------------------------------------
TEX_TORNADO = vr.cargar(os.path.join(A, 'entity/aeralis/tornado.png'))
TEX_CUCHILLA = vr.cargar(os.path.join(A, 'entity/aeralis/cuchilla.png'))


def tornado(x, z, alto, ancho, edad):
    """Un tornado como lo pinta TornadoAeralisRenderer: un embudo que se
    ensancha hacia arriba, con dos capas que giran a distinta velocidad y el
    eje que se tuerce; se deshace por abajo y por arriba."""
    velos = []
    for (e, al, an, giro, sube, k, tinte) in ((edad, alto, ancho, 1.0, 1.0, 0.6, (200, 210, 226)),
                                              (edad + 13, alto * 0.96, ancho * 0.66, 1.9, -1.4, 0.45, (236, 242, 250))):
        def punto(a, h):
            ang = a * math.tau
            r = an * (0.42 + 2.2 * h ** 1.5)
            ox = math.sin(h * 3.0 + e * 0.11) * 0.45 * h * an
            oz = math.cos(h * 2.6 + e * 0.09) * 0.45 * h * an
            uv = (a * 2.0 + e * 0.045 * giro, h * 3.0 - e * 0.03 * sube)
            return np.array([x + ox + math.cos(ang) * r, h * al, z + oz + math.sin(ang) * r]), uv
        for j in range(14):
            for i in range(18):
                a0, a1, h0, h1 = i / 18, (i + 1) / 18, j / 14, (j + 1) / 14
                pts, uvs = zip(*[punto(a, h) for a, h in ((a0, h0), (a1, h0), (a1, h1), (a0, h1))])
                hm = (h0 + h1) / 2
                borde = min(1.0, hm / 0.12) * min(1.0, (1.0 - hm) / 0.2)
                velos.append((list(pts), list(uvs), TEX_TORNADO, np.array(tinte) / 255.0, k * borde, 0.12 * borde, True))
    return velos


def cuchilla(centro, frente, lado, escala):
    """Una cuchilla del Aleteo como la pinta CuchillaVientoRenderer: una
    media luna de aire curvada hacia delante, de dos tiras cruzadas (tumbada
    y de pie), con dos ecos detras que hacen de estela. Brilla."""
    frente = frente / np.linalg.norm(frente)
    lado = lado / np.linalg.norm(lado)
    arriba = np.cross(lado, frente)
    velos = []
    for k, (alfa, e) in enumerate(((1.0, 1.0), (0.35, 0.9))):
        base = centro - frente * 0.95 * k * escala
        # mas fina y mas curva que en el juego, para que la media luna se lea de lejos
        for grosor, ka in ((frente * 0.24, 1.0), (arriba * 0.24, 0.85)):
            def c(u):
                x = u * 2 - 1
                return base + lado * x * 2.0 * escala * e + frente * 1.1 * (1 - x * x) * escala + arriba * 0.4 * escala
            for i in range(12):
                u0, u1 = i / 12, (i + 1) / 12
                g = grosor * escala
                pts = [c(u0) - g, c(u1) - g, c(u1) + g, c(u0) + g]
                velos.append((pts, [(u0, 1.0 - 1e-3), (u1, 1.0 - 1e-3), (u1, 0.0), (u0, 0.0)], TEX_CUCHILLA,
                              np.ones(3) * 1.1, alfa * ka, 0.45 * alfa * ka, False))
    return velos


def _tex_racha(semilla, w=64, h=12):
    """El viento del vendaval: la fila 0 es el filo de la racha, blanco
    helado; debajo, vetas de aire cian a lo largo, cada vez mas raras (el
    cian la separa del violeta de las alas)."""
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        k = 1 - y / (h - 1)
        x = 0
        while x < w:
            largo = r.randint(4, 14)
            if y <= 1:
                col, a = (232, 250, 255), r.randint(210, 250) if r.random() < 0.85 else 0
            elif y == 2:
                col, a = (188, 236, 255), r.randint(140, 200) if r.random() < 0.6 else 0
            elif r.random() < 0.3 + 0.5 * k:
                col, a = (140, 214, 250), int(r.randint(90, 170) * (0.3 + 0.7 * k))
            else:
                col, a = (80, 140, 210), int(r.randint(24, 70) * (0.25 + 0.75 * k))
            for xx in range(x, min(w, x + largo)):
                t[y, xx] = (*col, a)
            x += largo + (0 if y <= 1 else r.randint(0, 5))
    return t


TEX_RACHA = _tex_racha(5)
TEX_FILO = TEX_RACHA.copy()                # solo el filo brilla
TEX_FILO[3:, :, 3] = 0

# Altura (bloques) hasta la que el viento puede pasar por delante de ella: por
# encima se esconde, para no taparle la cara ni el ojo de la tormenta.
FRENTE_MAX = 7.6
# Las rachas que suben: (angulo de salida, vueltas, altura de salida y de
# llegada, radio abajo y arriba, ancho de la banda abajo y arriba).
RACHAS = [
    (0.2, 0.7, 0.4, 13.0, 2.6, 8.4, 0.6, 1.9),
    (1.5, 0.62, 1.4, 14.5, 3.0, 9.4, 0.5, 1.7),
    (2.8, 0.74, 0.6, 12.0, 2.4, 7.6, 0.6, 2.0),
    (4.2, 0.6, 2.4, 15.0, 3.2, 9.8, 0.45, 1.5),
    (5.3, 0.68, 0.8, 11.5, 2.8, 7.4, 0.55, 1.8),
]


def rachas():
    """El vendaval subiendo en espiral alrededor de ella desde la meseta,
    abriendose como un embudo. Devuelve los velos de delante (los que hay que
    apartar de su cara) por separado."""
    cx, cz = AERALIS_EN[0], AERALIS_EN[2]
    detras, delante, filos = [], [], []
    for th0, vueltas, y0, y1, r0, r1, b0, b1 in RACHAS:
        filas = []
        for i in range(130):
            t = i / 129
            th = th0 + t * vueltas * math.tau
            rad = r0 + (r1 - r0) * t ** 1.3
            p = np.array([cx + math.cos(th) * rad, y0 + (y1 - y0) * t, cz + math.sin(th) * rad])
            filas.append((p, p + np.array([0, b0 + (b1 - b0) * t, 0]), 0.9 * math.sin(math.pi * t) ** 0.6))
        s = 0.0
        for (a0, a1, ka), (b0_, b1_, kb) in zip(filas, filas[1:]):
            ds = float(np.linalg.norm(b0_ - a0))
            ua, ub = s / 3.2, (s + ds) / 3.2
            s += ds
            velo = ([a0, b0_, b1_, a1], [(ua, 0.999), (ub, 0.999), (ub, 0.0), (ua, 0.0)], TEX_RACHA, np.ones(3),
                    (ka + kb) / 2, 0.3 * (ka + kb) / 2, True)
            if delante_del_eje(a0) and a0[1] > FRENTE_MAX - 0.5:
                delante.append(velo)
            else:
                detras.append(velo)
        filos += [f[1] for f in filas[4::8]]
    return detras, delante, filos


def pintar_velos(lz, velos, niebla):
    """De atras a delante: cada velo se mezcla con lo que ya hay y no tapa en
    profundidad; lo que brilla suma a la capa de luz."""
    velos = [v for v in velos if min(CAM.proyectar(p)[2] for p in v[0]) > 2.0]
    velos.sort(key=lambda v: -CAM.proyectar(np.mean(v[0], axis=0))[2])
    for pts, uvs, tex, tinte, k, glow, mosaico in velos:
        # arriba del todo se disuelve: la franja de la barra queda limpia
        alto = min(CAM.proyectar(p)[1] for p in pts) / SS / ESCALA
        apaga = min(1.0, max(0.0, (alto - 110) / 90))
        k_, g_ = k * apaga, glow * apaga
        if k_ < 0.02 and g_ < 0.01:
            continue
        for tri in ((0, 1, 2), (0, 2, 3)):
            if k_ >= 0.02:
                lz.triangulo(CAM, [pts[i] for i in tri], [uvs[i] for i in tri], tex, tinte, None, niebla,
                             envolver=mosaico, translucido=min(1.0, k_))
            if g_ >= 0.01:
                lz.triangulo(CAM, [pts[i] for i in tri], [uvs[i] for i in tri], TEX_FILO if tex is TEX_RACHA else tex,
                             np.ones(3), None, None, aditivo=True, brillo=g_, envolver=mosaico)


# ----------------------------------------------------------------------
#  Aeralis: la malla del juego
# ----------------------------------------------------------------------
def velos_aeralis(qs, tex, brillo):
    """Las alas y las cintas: planos traslucidos, con las vetas y los ocelos
    que brillan."""
    planos = set(vj.PLANOS)
    out = []
    for Pq, UVq, _, mat in qs:
        if mat not in planos:
            continue
        luz = 0.55 + 0.6 * vr.iluminar(vr.normal(Pq), CAM, np.mean(Pq, axis=0), LUCES, AMBIENTE)
        out.append((list(Pq), list(UVq), tex, luz, 1.0, 0.0, False))
        out.append((list(Pq), list(UVq), brillo, np.ones(3), 0.0, 0.42, False))
    return out


def pintar_opaco(lz, qs, tex, brillo, niebla, silueta=False):
    planos = set(vj.PLANOS)
    for Pq, UVq, _, mat in qs:
        if mat in planos:
            continue
        luz = np.ones(3) if silueta else vr.iluminar(vr.normal(Pq), CAM, np.mean(Pq, axis=0), LUCES, AMBIENTE)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, luz,
                         None if silueta else brillo, None if silueta else niebla, brillo=1.6)


# ----------------------------------------------------------------------
#  Rayos y nubes, en 2D
# ----------------------------------------------------------------------
def rayo(capa, pts_guia, semilla, grosor, color, ramas=True, temblor=36):
    """Un relampago que sigue una guia (lista de puntos): una linea quebrada
    con ramas."""
    r = random.Random(semilla)
    d = ImageDraw.Draw(capa)
    guia = np.array(pts_guia, float)
    largo = np.sum(np.linalg.norm(np.diff(guia, axis=0), axis=1))
    n = max(6, int(largo / px(28)))
    t_guia = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(guia, axis=0), axis=1))]) / largo
    pts = []
    for k in range(n + 1):
        t = k / n
        x = np.interp(t, t_guia, guia[:, 0])
        y = np.interp(t, t_guia, guia[:, 1])
        sacude = 0 if k in (0, n) else px(temblor) * math.sin(math.pi * t) ** 0.5
        pts.append((x + r.uniform(-1, 1) * sacude, y + r.uniform(-1, 1) * sacude))
    d.line(pts, fill=color, width=grosor)
    if ramas:
        for k in range(2, n - 2, 3):
            bx, by = pts[k]
            rama = [(bx, by)]
            ang = r.uniform(0, math.tau)
            for j in range(3):
                bx += math.cos(ang) * px(34) + r.uniform(-px(10), px(10))
                by += math.sin(ang) * px(34) + r.uniform(-px(10), px(10))
                rama.append((bx, by))
            d.line(rama, fill=color, width=max(1, grosor // 2))


def ojo_de_la_tormenta(W, H, cx, cy, semilla):
    """Las nubes girando alrededor del ojo de la tormenta, detras de ella:
    bandas en espiral que se aprietan hacia un centro claro."""
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = (xx - cx) / W, (yy - cy) / W * 1.35
    d = np.hypot(dx, dy) + 1e-6
    ang = np.arctan2(dy, dx)
    espiral = 0.5 + 0.5 * np.sin(ang * 3 + np.log(d) * 7.0)
    ruido = np.array(Image.fromarray((np.random.default_rng(semilla).random((H // 8 + 1, W // 8 + 1)) * 255).astype(np.uint8))
                     .resize((W, H), Image.BICUBIC)).astype(float) / 255
    nubes = np.clip(espiral * 0.7 + ruido * 0.6 - 0.35, 0, 1) * np.exp(-((d - 0.24) / 0.2) ** 2)
    centro = np.exp(-(d / 0.06) ** 2)
    return nubes, centro


def barra_jefe(escala):
    """La barra de jefe de Aeralis, compuesta igual que en AeralisBarraHud."""
    def tex(n):
        return Image.open(os.path.join(GUI, n + '.png')).convert('RGBA')

    def tenir(im, rgb):
        a = np.array(im).astype(float)
        a[..., :3] *= np.array(rgb)[None, None] / 255.0
        return Image.fromarray(a.astype(np.uint8))
    color = (0xB0, 0x7C, 0xFF)
    vida = 0.42
    lienzo = Image.new('RGBA', (240, 44), (0, 0, 0, 0))
    lienzo.alpha_composite(tex(f'aeralis_barra_marco_{FASE}'))
    relleno = tex(f'aeralis_barra_relleno_{FASE}')
    lleno = round(190 * vida)
    for x in range(0, lleno, 64):
        lienzo.alpha_composite(relleno.crop((0, 0, min(64, lleno - x), 9)), (40 + x, 22))
    for corte in (0.75, 0.5, 0.25):
        ojo = tex('aeralis_barra_ojo_apagado') if vida < corte else tenir(tex('aeralis_barra_ojo'), color)
        lienzo.alpha_composite(ojo, (40 + round(190 * corte) - 3, 29))
    lienzo.alpha_composite(tex(f'aeralis_barra_nucleo_{FASE}'), (19 - 12, 26 - 12))
    lienzo.alpha_composite(tex('aeralis_barra_nombre'), (100, 9))
    lienzo.alpha_composite(tenir(tex(f'aeralis_barra_fase_{FASE}'), color), (40 + 190 - 64 + 1, 8))
    return lienzo.resize((lienzo.width * escala, lienzo.height * escala), Image.NEAREST)


# La cuchilla del Aleteo que viene hacia quien mira: (x, y del poster,
# profundidad), cuanto se aparta de venir de frente (para que se le vea la
# curva), cuanto se ladea, cuanto cae y su tamano.
CUCHILLA = ((1450, 955), 7.5, 48.0, -10.0, 12.0, 0.95)
# Las columnas rotas de la meseta: (x del poster, profundidad, alto, rota), a
# los lados, que debajo de ella no estorben
COLUMNAS = [(700, 46.0, 6, True), (1590, 50.0, 8, True), (420, 54.0, 4, True)]
# Los dos tornados de la meseta: (x del poster donde tocan el suelo, a que
# profundidad, alto, ancho, edad)
TORNADOS = [(880, 33.0, 14.0, 1.25, 7.0), (1820, 31.0, 14.5, 1.3, 31.0)]


def main():
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = vs.NieblaCielo(ini=18.0, largo=46.0)

    # la meseta y sus columnas rotas
    vs.suelo(lz, CAM, ext=26, prof=44, niebla=niebla)
    for i, (sx, prof, alto, rota) in enumerate(COLUMNAS):
        b = desproyectar(sx, 900, prof)
        nm.dibujar(lz, CAM, vs.columna(b[0], b[2], alto, rota, i), vs.LUCES_CIELO, vs.AMB_CIELO, niebla)

    # Aeralis: lo opaco primero
    tex = vr.cargar(os.path.join(A, f'entity/aeralis/aeralis_f{FASE}.png'))
    brillo = vr.cargar(os.path.join(A, f'entity/aeralis/aeralis_brillo_f{FASE}.png'))
    pose = pose_poster()
    M = vr.entidad_a_mundo(*AERALIS_EN, GUINADA, vj.ESCALA)
    uv, alto_atlas = vj.empaquetar()
    qs = vj.quads(pose, uv, alto_atlas, M)
    pintar_opaco(lz, qs, tex, brillo, niebla)

    # las siluetas: el cuerpo solo (para apartarle el viento de la cara) y el
    # cuerpo con las alas (para el contraluz y lo que pasa por detras)
    solo = vr.Lienzo(W * SS, H * SS)
    pintar_opaco(solo, qs, tex, brillo, niebla, silueta=True)
    cuerpo = flotante(a_imagen(solo.alfa))
    for Pq, UVq, _, mat in qs:
        if mat in vj.PLANOS:
            for tri in ((0, 1, 2), (0, 2, 3)):
                solo.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, np.ones(3))
    figura = flotante(a_imagen(solo.alfa))

    # todo lo traslucido junto, de atras a delante
    detras, delante, filos = rachas()
    velos = velos_aeralis(qs, tex, brillo) + detras
    bases = []
    for sx, prof, alto_t, ancho_t, edad in TORNADOS:
        b = desproyectar(sx, 900, prof)
        bases.append((b[0], b[2]))
        velos += tornado(b[0], b[2], alto_t, ancho_t, edad)
    (cx_, cy_), prof_c, aparta, ladeo, cae, esc_c = CUCHILLA
    centro_c = desproyectar(cx_, cy_, prof_c)
    nucleo = (M @ np.array([*vj.punto(pose, 'nucleo'), 1.0]))[:3]
    hacia = (CAM.ojo - centro_c) / np.linalg.norm(CAM.ojo - centro_c)   # viene hacia la camara...
    hacia = (vr.Ry(math.radians(aparta))[:3, :3] @ hacia)                # ...pasando de lado...
    frente_c = hacia * math.cos(math.radians(cae)) - CAM.u * math.sin(math.radians(cae))   # ...y cayendo
    lado_c = np.cross(frente_c, [0, 1, 0])
    lado_c = lado_c / np.linalg.norm(lado_c)
    gira = math.radians(ladeo)
    fn = frente_c / np.linalg.norm(frente_c)
    lado_c = lado_c * math.cos(gira) + np.cross(fn, lado_c) * math.sin(gira)
    velos += cuchilla(centro_c, frente_c, lado_c, esc_c)
    pintar_velos(lz, velos, niebla)
    # el viento que pasa por delante de su pecho va aparte: se le aparta de la cara
    alto_lz = vr.Lienzo(W * SS, H * SS)
    alto_lz.z = lz.z.copy()
    pintar_velos(alto_lz, delante, niebla)

    ojos = [(M @ np.array([*vj.punto(pose, 'ojo_' + n), 1.0]))[:3] for n in ('izq', 'der')]

    def en_ala(nombre, u, v):
        """Un punto del ala en fracciones de su ancho y su alto."""
        s = 1 if nombre.endswith('izq') else -1
        tam = vj.TAM_SUP if 'sup' in nombre else vj.TAM_INF
        y0 = -tam[1] * (0.42 if 'sup' in nombre else 0.08)
        return (M @ np.array([*vj.punto(pose, nombre, (s * tam[0] * u, y0 + tam[1] * v, 0)), 1.0]))[:3]

    # --- a resolucion final ---
    color = flotante(a_imagen(lz.color))
    alfa = flotante(a_imagen(lz.alfa))[..., None]
    emis = a_imagen(lz.emis)

    lejos = np.array([CAM.ojo[0] + CAM.f[0] * 300, 0.0, CAM.ojo[2] + CAM.f[2] * 300])
    horiz = CAM.proyectar(lejos)[1] / SS
    fondo = vs.cielo(W, H, horiz, 11, rayos=0.35) * np.array([0.8, 0.8, 0.92])
    yy, xx = np.mgrid[0:H, 0:W]
    # el ojo de la tormenta: las nubes giran detras de ella y su pecho las enciende
    ncx, ncy, _ = pantalla(nucleo)
    nubes, centro = ojo_de_la_tormenta(W, H, ncx, ncy - px(60), 4)
    fondo += nubes[..., None] * np.array([0.32, 0.3, 0.58]) * 0.42
    fondo += centro[..., None] * np.array([0.5, 0.45, 0.85]) * 0.4
    dd = np.hypot((xx - ncx) / (W * 0.3), (yy - ncy) / (H * 0.42))
    fondo += np.array([0.3, 0.18, 0.6])[None, None] * np.exp(-dd ** 2 * 1.3)[..., None] * 0.36
    # rayos de luz que bajan por los claros de las nubes
    luz = ne.rayos(W, H, 23, n=6)[..., None] * np.array([0.5, 0.48, 0.85]) * 0.32
    fondo += luz
    # el contraluz: el aire brilla justo detras de su silueta
    halo = flotante(Image.fromarray((figura * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(px(46))))
    fondo += halo[..., None] * np.array([0.28, 0.22, 0.55]) * 0.35
    fondo_img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

    # relampagos lejanos, detras de todo
    capa_r = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    rayo(capa_r, [(px(1890), -px(10)), (px(1850), px(260)), (px(1880), px(540))], 3, max(1, px(6)), (230, 218, 255, 255))
    rayo(capa_r, [(px(850), -px(10)), (px(870), px(220)), (px(900), px(430))], 8, max(1, px(5)), (210, 230, 255, 230))
    for radio in (px(30), px(12), px(4)):
        fondo_img.alpha_composite(capa_r.filter(ImageFilter.GaussianBlur(radio)))
    fondo_img.alpha_composite(capa_r)

    # bruma baja: las nubes que suben por el borde de la meseta
    bruma = np.exp(-((yy - horiz - px(10)) / px(70)) ** 2) * (0.55 + 0.45 * flotante(
        Image.fromarray((np.random.default_rng(6).random((H // 24 + 1, W // 24 + 1)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)))
    fondo_bruma = np.array([0.36, 0.36, 0.56])[None, None] * bruma[..., None] * 0.6

    # la escena, que ya viene premultiplicada (lo traslucido sobre el vacio
    # solo deja su parte)
    f = flotante(fondo_img)[..., :3]
    f = color + f * (1 - alfa)
    f = f + fondo_bruma * (1 - figura[..., None])
    # el viento que le pasa por delante del pecho, apartado de su cara
    _, cintura, _ = pantalla((AERALIS_EN[0], FRENTE_MAX, AERALIS_EN[2]))
    arriba = np.clip((cintura + px(40) - yy) / px(80), 0, 1)
    deja = (1 - cuerpo * arriba)[..., None]
    a_alto = flotante(a_imagen(alto_lz.alfa))[..., None] * deja
    f = f * (1 - a_alto) + flotante(a_imagen(alto_lz.color)) * deja
    img = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

    e = np.array(emis).astype(float) + np.array(a_imagen(alto_lz.emis)).astype(float) * deja
    e = Image.fromarray(np.clip(e, 0, 255).astype(np.uint8)).convert('RGB')
    for radio, k in ((px(5), 0.85), (px(18), 0.7), (px(60), 0.5)):
        img = sumar(img, e.filter(ImageFilter.GaussianBlur(radio)), k)
    img = sumar(img, e, 1.0).convert('RGBA')

    # rayos que saltan entre las alas: de la de arriba a la de abajo en cada
    # lado y uno de ala a ala por detras de ella
    capa_r = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for n, sem in (('izq', 21), ('der', 22)):
        a = pantalla(en_ala('ala_sup_' + n, 0.62, 0.8))
        b = pantalla(en_ala('ala_inf_' + n, 0.55, 0.4))
        rayo(capa_r, [a[:2], ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b[:2]], sem, max(1, px(5)), (236, 226, 255, 255), temblor=30)
    a = pantalla(en_ala('ala_sup_izq', 0.42, 0.1))
    b = pantalla(en_ala('ala_sup_der', 0.42, 0.1))
    arco = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - px(90) * math.sin(math.pi * t)) for t in np.linspace(0, 1, 7)]
    rayo(capa_r, arco, 31, max(1, px(4)), (228, 218, 255, 245), temblor=22)
    capa_r.putalpha(Image.fromarray((np.array(capa_r.getchannel('A')).astype(float) * (1 - cuerpo)).astype(np.uint8)))
    for radio in (px(30), px(12), px(4)):
        img.alpha_composite(capa_r.filter(ImageFilter.GaussianBlur(radio)))
    img.alpha_composite(capa_r)

    # el ojo de la tormenta brilla en su pecho
    dd = np.hypot(xx - ncx, yy - ncy)
    img = sumar(img, Image.fromarray((np.clip(np.exp(-(dd / px(80)) ** 2)[..., None] * np.array([150, 120, 255]) * 0.7
                                              + np.exp(-(dd / px(24)) ** 2)[..., None] * np.array([230, 225, 255]) * 0.25,
                                              0, 255)).astype(np.uint8)), 1.0).convert('RGBA')

    # contraluces: el borde que mira al cielo, blanco azulado; el que mira a
    # los rayos, violeta
    f = np.array(img).astype(float)
    for (dx, dy), rgb, k, mascara in (((-1, -1), (205, 225, 255), 0.7, cuerpo), ((1, 0), (170, 120, 255), 0.6, cuerpo),
                                      ((-1, -1), (205, 225, 255), 0.35, figura)):
        n_ = max(1, px(3))
        vecino = np.roll(mascara, (-dy * n_, -dx * n_), axis=(0, 1))
        borde = np.clip(mascara - vecino, 0, 1)
        borde = flotante(Image.fromarray((borde * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(1, px(1.5)))))
        f[..., :3] += borde[..., None] * np.array(rgb) * k
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))

    # --- particulas propias, en 2D ---
    r = random.Random(9)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for k in range(30):                          # motas que giran alrededor del ojo de la tormenta
        a = k * 0.62
        d = px(40) + k * px(4.5)
        s = sprite(f'aeralis_luz_{r.randint(0, 2)}.png', px(r.choice([12, 16, 20])))
        capa.alpha_composite(s, (int(ncx + math.cos(a) * d - s.width / 2), int(ncy + math.sin(a) * d * 0.8 - s.height / 2)))
    for o in ojos:                               # destellos en los ojos, hacia fuera y arriba
        ox, oy, _ = pantalla(o)
        for _ in range(3):
            a = r.uniform(-math.pi * 0.95, -math.pi * 0.05)
            d = r.uniform(px(30), px(80))
            s = sprite(f'aeralis_luz_{r.randint(0, 2)}.png', px(r.choice([12, 16])))
            capa.alpha_composite(s, (int(ox + math.cos(a) * d - s.width / 2), int(oy + math.sin(a) * d - s.height / 2)))
    for n in ('ala_sup_izq', 'ala_sup_der', 'ala_inf_izq', 'ala_inf_der'):   # chispas dentro de las alas (fase III)
        for _ in range(4):
            tx, ty, _ = pantalla(en_ala(n, r.uniform(0.3, 0.9), r.uniform(0.2, 0.8)))
            s = sprite(f'aeralis_rayo_{r.randint(0, 2)}.png', px(r.choice([36, 48, 60])))
            s = s.rotate(r.uniform(0, 360), expand=True)
            capa.alpha_composite(s, (int(tx - s.width / 2), int(ty - s.height / 2)))
    for p_ in filos:                             # el viento arrastra jirones y polvo por sus filos
        if r.random() > 0.35:
            continue
        sx, sy, prof = pantalla(p_)
        if prof < 3 or (delante_del_eje(p_) and p_[1] > FRENTE_MAX - 0.5):
            continue
        s = sprite(f'aeralis_viento_{r.randint(0, 2)}.png', max(4, int(px(900) / prof)), max(2, int(px(220) / prof)))
        capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
    for x, z in bases:                           # el remolino de polvo al pie de cada tornado
        bx, by, prof = pantalla((x, 0.2, z))
        for k in range(7):
            s = sprite(f'aeralis_polvo_{r.randint(0, 2)}.png', max(3, int(px(r.choice([500, 700, 900])) / prof)))
            capa.alpha_composite(s, (int(bx + r.uniform(-1, 1) * px(2600) / prof - s.width / 2),
                                     int(by + r.uniform(-0.3, 0.2) * px(1400) / prof - s.height / 2)))
        s = sprite(f'aeralis_remolino_{r.randint(0, 2)}.png', int(px(2600) / prof), int(px(900) / prof))
        s.putalpha(s.getchannel('A').point(lambda v: int(v * 0.6)))
        capa.alpha_composite(s, (int(bx - s.width / 2), int(by - s.height / 2)))
    for _ in range(40):                          # motas de luz que arrastra el vendaval
        mx_, my_ = int(r.uniform(px(820), W - px(40))), int(r.uniform(px(140), H - px(120)))
        if cuerpo[min(H - 1, my_), min(W - 1, mx_)] > 0.1:
            continue
        s = sprite(f'aeralis_luz_{r.randint(0, 2)}.png', px(r.choice([10, 14, 18, 24])))
        capa.alpha_composite(s, (mx_ - s.width // 2, my_ - s.height // 2))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(px(5))))
    img.alpha_composite(capa)
    # escamas que se le caen de las alas, con profundidad: lejos pequenas y
    # nitidas, cerca grandes y desenfocadas
    for capa_prof, (n_esc, tams, desenfoque) in enumerate(((50, (10, 14, 18), 0), (14, (36, 48, 60), 6))):
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        puestas = 0
        while puestas < n_esc:
            ex, ey = int(r.uniform(px(860), W - px(30))), int(r.uniform(px(130), H - px(40)))
            if cuerpo[min(H - 1, ey), min(W - 1, ex)] > 0.1:
                continue
            s = sprite(f'aeralis_escama_{r.randint(0, 2)}.png', px(r.choice(tams))).rotate(r.uniform(0, 360), expand=True)
            capa.alpha_composite(s, (ex - s.width // 2, ey - s.height // 2))
            puestas += 1
        if desenfoque:
            capa = capa.filter(ImageFilter.GaussianBlur(px(desenfoque)))
            capa.putalpha(capa.getchannel('A').point(lambda v: int(v * 0.7)))
        img.alpha_composite(capa)
    # la cuchilla corta el aire: rayas que vienen desde ella hacia quien mira
    cx_p, cy_p, cz_p = pantalla(centro_c)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for k in range(16):
        t = r.uniform(-1, 1)
        x0 = cx_p + t * px(2000) * esc_c / cz_p
        y0 = cy_p - abs(t) * px(300) / cz_p + r.uniform(-px(20), px(20))
        x1, y1 = x0 + (ncx - x0) * r.uniform(0.2, 0.38), y0 + (ncy - y0) * r.uniform(0.2, 0.38)
        d.line([(x0, y0), (x1, y1)], fill=(214, 226, 255, r.randint(60, 140)), width=max(1, px(2)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(max(1, px(1)))))
    # estelas de viento cruzando la escena
    vs.estelas(img, int(18 * ESCALA) + 10, 21, zona=((px(780), W - px(60)), (px(140), H - px(200))), alfa=60)
    vs.estelas(img, 12, 22, zona=((0, px(700)), (px(700), H - px(140))), alfa=34)

    # --- grado y vineta ---
    f = np.array(img).astype(float) / 255.0
    vin = 1 - 0.6 * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.32, 0, 1) ** 1.4
    f[..., :3] *= vin[..., None]
    f[..., :3] = np.clip(f[..., :3] * np.array([0.96, 0.97, 1.05]) + np.random.default_rng(2).normal(0, 0.01, (H, W, 1)), 0, 1)
    img = Image.fromarray((f * 255).astype(np.uint8)).convert('RGBA')

    # --- el anuncio ---
    gr = np.zeros((H, W, 4), np.uint8)
    gr[..., :3] = (6, 8, 20)
    gr[..., 3] = (np.clip(1 - xx / (W * 0.5), 0, 1) ** 1.6 * 215).astype(np.uint8)
    img.alpha_composite(Image.fromarray(gr))
    d = ImageDraw.Draw(img)

    x0 = px(110)
    texto_espaciado(d, (x0, px(300)), 'ATALAYA  ·  JEFE DEL AIRE', fuente('Montserrat-Bold.ttf', 22), CIELO, px(5))
    brillo_texto(img, (x0 - px(6), px(320)), 'AERALIS', fuente('Oswald-Bold.ttf', 196), BLANCO, (120, 150, 255, 210), px(24))
    d = ImageDraw.Draw(img)
    d.text((x0, px(562)), 'La Mariposa del Vendaval', font=fuente('Montserrat-SemiBoldItalic.ttf', 34), fill=(205, 214, 236, 255))
    d.text((x0, px(608)), 'Calma la tormenta. Apaga el ojo de su pecho.', font=fuente('Montserrat-Medium.ttf', 24), fill=GRIS)
    d.rectangle((x0, px(656), x0 + px(90), px(661)), fill=VIOLETA)

    # la barra de jefe, como en el juego, sobre ella
    barra = barra_jefe(max(1, px(2)))
    img.alpha_composite(barra, (int(float(os.environ.get('BARRA_X', '1210')) * ESCALA) - barra.width // 2, px(36)))
    d = ImageDraw.Draw(img)

    fs = fuente('Oswald-Bold.ttf', 26)
    fp = fuente('Montserrat-Medium.ttf', 18)
    tw = d.textlength('HARDCORE', font=fs)
    bx, by = W - px(110) - tw - px(36), px(60)
    d.rectangle((bx, by, bx + tw + px(36), by + px(52)), outline=VIOLETA, width=max(1, px(3)))
    d.text((bx + px(18), by + px(6)), 'HARDCORE', font=fs, fill=VIOLETA)
    d.text((W - px(110) - d.textlength('Minecraft 26.2 · Fabric', font=fp), H - px(70)),
           'Minecraft 26.2 · Fabric', font=fp, fill=(168, 178, 204, 255))
    img.convert('RGB').save(SALIDA)
    print('ok', W, H)


def texto_espaciado(d, xy, txt, f, color, sep):
    x, y = xy
    for ch in txt:
        d.text((x, y), ch, font=f, fill=color)
        x += d.textlength(ch, font=f) + sep
    return x


def brillo_texto(base, xy, txt, f, color, halo, radio):
    capa = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).text(xy, txt, font=f, fill=halo)
    capa = capa.filter(ImageFilter.GaussianBlur(radio))
    base.alpha_composite(capa)
    base.alpha_composite(capa)
    ImageDraw.Draw(base).text(xy, txt, font=f, fill=color)


main()

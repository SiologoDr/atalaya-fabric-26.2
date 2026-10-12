"""
Renders de la ficha de los tres jefes de otros tipos (12-10-2026): cada uno en su
sitio y con su luz, su cabeza de cerca, los tres juntos con un jugador para la
escala y la lamina de materiales.

  A  Boreala    la tundra de noche, bajo la aurora
  B  Nocturna   la llanura sin cielo: arriba no queda ninguna estrella
  C  Duneara    el desierto al caer la tarde: dos soles, y uno es su cola

Uso: python elementales_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
     (con RAPIDO=1 en el entorno, a media resolucion para probar)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne            # el jugador de escala
import quimeras_modelo as qm
import quimeras_escenas as qe         # el lienzo, la niebla y el revelado
import elementales_modelo as el

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
FUENTE = 'C:/Windows/Fonts/'
TAU = math.tau
D = vr.D2R


# ----------------------------------------------------------------------
#  Los tres sitios
# ----------------------------------------------------------------------
SITIO = {
    'A': dict(
        luces=[((-0.25, 1.0, 0.7), (0.72, 0.84, 1.0), 0.9, 'llave'), ((-0.4, 0.5, -1.0), (0.35, 1.0, 0.62), 0.85, 'contra'),
               ((0.9, 0.25, -0.3), (0.62, 0.45, 1.0), 0.5, 'contra')],
        amb=(0.14, 0.17, 0.24), niebla=(0.06, 0.11, 0.17), suelo='suelo_nieve',
        motas=((235, 245, 255), (170, 255, 215)),
    ),
    'B': dict(
        luces=[((-0.5, 0.8, 0.7), (0.55, 0.58, 0.85), 0.55, 'llave'), ((0.3, 0.3, -1.0), (0.35, 0.95, 0.9), 0.95, 'contra'),
               ((-0.9, 0.2, -0.2), (0.6, 0.38, 1.0), 0.55, 'contra'), ((0.0, -0.3, 1.0), (0.3, 0.75, 0.75), 0.25, 'llave')],
        amb=(0.09, 0.09, 0.13), niebla=(0.03, 0.025, 0.05), suelo='suelo_noche',
        motas=((150, 255, 240), (170, 140, 255)),
    ),
    'C': dict(
        luces=[((0.86, 0.3, 0.3), (1.0, 0.8, 0.58), 1.1, 'llave'), ((0.6, 0.35, -0.8), (1.0, 0.5, 0.25), 0.7, 'contra'),
               ((-0.5, 1.0, 0.4), (0.5, 0.62, 1.0), 0.5, 'llave'), ((0.0, -0.5, 1.0), (0.8, 0.55, 0.35), 0.2, 'llave')],
        amb=(0.2, 0.15, 0.14), niebla=(0.62, 0.42, 0.3), suelo='suelo_arena',
        motas=((255, 220, 160), (240, 190, 130)),
    ),
    'T': dict(
        luces=[((0.3, 1.0, 0.6), (0.72, 0.74, 0.9), 0.7, 'llave'), ((-0.3, 0.3, -1.0), (1.0, 0.6, 0.45), 0.55, 'contra')],
        amb=(0.14, 0.13, 0.18), niebla=(0.2, 0.15, 0.22), suelo='suelo_trio',
        motas=((255, 220, 200), (200, 210, 255)),
    ),
}
NIEBLA_D = {'A': (45, 150), 'B': (40, 130), 'C': (55, 190), 'T': (150, 320)}
qm._reg('suelo_trio', qm._suelo_grande(75, qm._r('201e2a', '24222e', '282633', '2c2a38', '32303f'), nm._hex('4a4658'), grietas=False))


def suelo(lz, cam, niebla, sitio, ext=160, paso=32, cerca=64, paso_cerca=8):
    """El suelo en baldosas: pequenas cerca (una baldosa que cruza la camara no se pinta)
    y grandes lejos."""
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], SITIO[sitio]['suelo']))

    cx, cz = cam.ojo[0], cam.ojo[2]
    for gx in range(-ext, ext, paso):
        for gz in range(-ext, ext, paso):
            if abs(gx + paso / 2 - cx) < cerca and abs(gz + paso / 2 - cz) < cerca:
                for a in range(gx, gx + paso, paso_cerca):
                    for b in range(gz, gz + paso, paso_cerca):
                        baldosa(a, b, paso_cerca)
            else:
                baldosa(gx, gz, paso)
    qm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


def decorado(lz, cam, niebla, sitio, semilla=3, lejos=14):
    """Lo de alrededor: agujas de hielo (A), rocas con estrellas caidas (B), dunas y
    los huesos de lo que se trago (C)."""
    r = random.Random(semilla)
    qs = []

    def sitio_libre():
        while True:
            x, z = r.uniform(-60, 60), r.uniform(-60, 45)
            if math.hypot(x, z) > lejos and math.hypot(x - cam.ojo[0], z - cam.ojo[2]) > 16:
                return x, z

    if sitio == 'A':
        for _ in range(16):
            x, z = sitio_libre()
            for j in range(r.randint(3, 7)):
                M = vr.T(x + r.uniform(-1.6, 1.6), -0.2, z + r.uniform(-1.6, 1.6)) @ vr.Ry(r.uniform(0, 90) * D) @ vr.Rx(r.uniform(-28, 28) * D)
                el.cristal(qs, M, r.uniform(0.3, 0.75), r.uniform(1.5, 6.5) * (1.0 if j else 1.3), 'hielo_claro')
            el.ovoide(qs, vr.T(x, -0.6, z) @ vr.Ry(r.uniform(0, 3)), 2.6, 0.9, 3.4, 'nieve', capas=6, lados=16)
    elif sitio == 'B':
        for _ in range(12):
            x, z = sitio_libre()
            for j in range(r.randint(1, 3)):
                M = vr.T(x + r.uniform(-1.5, 1.5), -0.3, z + r.uniform(-1.5, 1.5)) @ vr.Ry(r.uniform(0, 90) * D) @ vr.Rz(r.uniform(-16, 16) * D)
                el.cristal(qs, M, r.uniform(0.7, 1.5), r.uniform(3.0, 9.0) * (1.0 if j == 0 else 0.6), 'basalto')
        for _ in range(30):
            x, z = sitio_libre()
            qm.oct_y(qs, vr.T(x, 0.0, z), 0, 0.12, 0.12, 'anillo')                  # estrellas caidas
    elif sitio == 'C':
        for _ in range(10):
            x, z = sitio_libre()
            w = r.uniform(5, 11)
            el.ovoide(qs, vr.T(x, -w * 0.22, z) @ vr.Ry(r.uniform(0, 3)), w, w * 0.4, w * 1.6, 'duna', capas=9, lados=16)
        for _ in range(3):                                                           # costillares enterrados
            x, z = sitio_libre()
            giro = r.uniform(0, TAU)
            for j in range(6):
                M = vr.T(x, 0, z) @ vr.Ry(giro) @ vr.T(0, 0, j * 1.6)
                alto = 4.5 - abs(j - 2.5) * 0.6
                el.segmento(qs, qm.punto(M, (-2.2, -0.4, 0)), qm.punto(M, (-1.6, alto, 0.3)), 0.3, 'diente_sol', 0.22)
                el.segmento(qs, qm.punto(M, (-1.6, alto, 0.3)), qm.punto(M, (0.2, alto + 1.4, 0.6)), 0.22, 'diente_sol', 0.08)
    qm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


# ----------------------------------------------------------------------
#  Los cielos (pintados en 2D) y lo lejano
# ----------------------------------------------------------------------
def _gradiente(W, H, horizonte, arriba, medio, abajo):
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    return np.broadcast_to(col[:, None, :], (H, W, 3)).copy()


def _estrellas(col, horizonte, n, semilla, tope=0.8):
    H, W = col.shape[:2]
    r = random.Random(semilla)
    for _ in range(n):
        x, y = r.randint(0, W - 1), r.randint(0, max(1, int(horizonte * 0.9)))
        col[y, x] = np.clip(col[y, x] + r.uniform(0.2, tope) * (1 - y / max(horizonte, 1)), 0, 1)


def cielo_A(W, H, horizonte):
    col = _gradiente(W, H, horizonte, np.array((0.006, 0.012, 0.04)), np.array((0.02, 0.05, 0.1)), np.array((0.06, 0.16, 0.2)))
    _estrellas(col, horizonte, int(W * H / 3000), 7)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    for b, (alto, amp, frec, fase, fuerza) in enumerate(((0.30, 0.07, 1.6, 0.4, 1.0), (0.18, 0.05, 2.3, 2.1, 0.7), (0.42, 0.04, 1.1, 4.0, 0.5))):
        yc = horizonte * (1 - alto) + H * amp * np.sin(xx / W * TAU * frec + fase) + H * 0.02 * np.sin(xx / W * TAU * 5.3 + fase)
        d = (yc - yy) / H                                         # positivo por encima del filo
        largo = 0.2
        perfil = np.where(d < 0, np.exp(d / 0.006), np.exp(-d / largo))
        rayos = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(xx * 0.045 + 3 * np.sin(xx * 0.006 + b))) ** 3
        c = np.clip(d / largo, 0, 1)[..., None]
        color = np.array((0.25, 1.0, 0.6)) * (1 - c) + np.array((0.55, 0.32, 1.0)) * c
        col += (perfil * rayos)[..., None] * color * 0.26 * fuerza
    banda = np.exp(-((yy - horizonte) / (H * 0.035)) ** 2)[..., None]
    col += banda * np.array((0.04, 0.09, 0.11))
    return np.clip(col, 0, 1)


def cielo_B(W, H, horizonte):
    """Sin una estrella: se las ha comido. Solo un resplandor violeta a ras del suelo."""
    col = _gradiente(W, H, horizonte, np.array((0.003, 0.003, 0.008)), np.array((0.012, 0.01, 0.025)), np.array((0.09, 0.05, 0.13)))
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    banda = np.exp(-((yy - horizonte) / (H * 0.09)) ** 2)[..., None]
    col += banda * (np.array((0.16, 0.07, 0.22)) + np.array((0.0, 0.1, 0.1)) * (0.5 + 0.5 * np.sin(xx / W * TAU))[..., None])
    return np.clip(col, 0, 1)


def cielo_C(W, H, horizonte):
    col = _gradiente(W, H, horizonte, np.array((0.1, 0.12, 0.3)), np.array((0.5, 0.3, 0.36)), np.array((1.0, 0.62, 0.3)))
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    sx, sy = W * 0.9, horizonte - H * 0.05
    d = np.hypot((xx - sx) / W, (yy - sy) / H)
    col += np.clip(1 - d / 0.55, 0, 1)[..., None] ** 2.0 * np.array((1.0, 0.55, 0.2))
    disco = ((xx - sx) ** 2 + (yy - sy) ** 2) < (H * 0.045) ** 2
    col = np.where(disco[..., None], np.array((1.0, 0.95, 0.8)), col)
    return np.clip(col, 0, 1)


def lejanias(img, horizonte, sitio, semilla=5):
    """Lo que se ve a lo lejos: montes de hielo (A), mesetas negras (B), dunas (C)."""
    W, H = img.size
    d = ImageDraw.Draw(img)
    r = random.Random(semilla)

    def cresta(alto, rugoso, pasos):
        pts = [0.0] * (pasos + 1)
        pts[0], pts[-1] = r.uniform(0.2, 1), r.uniform(0.2, 1)
        paso, amp = pasos, 1.0
        while paso > 1:
            for i in range(0, pasos, paso):
                pts[i + paso // 2] = (pts[i] + pts[i + paso]) / 2 + r.uniform(-amp, amp) * 0.5
            paso //= 2
            amp *= rugoso
        m0, m1 = min(pts), max(pts)
        return [(W * i / pasos, horizonte - alto * H * (p - m0) / max(m1 - m0, 1e-6)) for i, p in enumerate(pts)]

    if sitio == 'A':
        for alto, rugoso, color, nieve in ((0.13, 0.62, (26, 42, 62), (120, 150, 175)), (0.07, 0.55, (16, 26, 40), (90, 115, 140))):
            pts = cresta(alto, rugoso, 128)
            d.polygon(pts + [(W, horizonte + 2), (0, horizonte + 2)], fill=color)
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                if y1 < horizonte - alto * H * 0.5 or y0 < horizonte - alto * H * 0.5:
                    d.line((x0, y0 + 1, x1, y1 + 1), fill=nieve, width=max(1, int(W / 800)))
    elif sitio == 'B':
        pts = cresta(0.05, 0.5, 64)
        d.polygon(pts + [(W, horizonte + 2), (0, horizonte + 2)], fill=(7, 6, 13))
    elif sitio == 'C':
        for k, (alto, color) in enumerate(((0.06, (196, 120, 80)), (0.035, (150, 86, 56)))):
            pts = [(x, horizonte - alto * H * (0.5 + 0.5 * math.sin(x / W * TAU * (1.3 + k) + k * 2.0)) ** 1.5) for x in range(0, W + 8, 8)]
            d.polygon(pts + [(W, horizonte + 2), (0, horizonte + 2)], fill=color)
    return img


def cielo_T(W, H, horizonte):
    """El anochecer neutro de la lamina de escala."""
    col = _gradiente(W, H, horizonte, np.array((0.03, 0.035, 0.09)), np.array((0.16, 0.12, 0.22)), np.array((0.62, 0.36, 0.34)))
    _estrellas(col, horizonte, int(W * H / 6000), 9, tope=0.6)
    return np.clip(col, 0, 1)


CIELO = {'A': cielo_A, 'B': cielo_B, 'C': cielo_C, 'T': cielo_T}


def motas(img, n, semilla, colores, viento=(0.0, 1.0), largo=(1, 5)):
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H)
        c = colores[0] if r.random() < 0.6 else colores[1]
        l = r.uniform(*largo) * W / 1600
        d.line((x, y, x + viento[0] * l, y + viento[1] * l), fill=(*c, r.randint(110, 220)), width=max(1, int(r.choice((1, 1, 1.5, 2)) * W / 1600)))
    glow = capa.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)


def componer(lz, cam, W, H, sitio, n_motas=150, semilla=3, fuerza_vineta=0.5):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = CIELO[sitio](W, H, horiz)
    fondo = np.array(lejanias(Image.fromarray((fondo * 255).astype(np.uint8)), int(horiz), sitio)).astype(float) / 255
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis, radios=((3 * K, 0.8), (14 * K, 0.6), (44 * K, 0.45))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    viento = {'A': (0.25, 1.0), 'B': (0.0, 1.0), 'C': (1.0, 0.08), 'T': (0.0, 1.0)}[sitio]
    largo = {'A': (1, 4), 'B': (1, 2), 'C': (4, 14), 'T': (1, 2)}[sitio]
    return motas(img, int(n_motas * W / 1600), semilla, SITIO[sitio]['motas'], viento, largo)


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    print('ok', nombre, flush=True)
    return img


def jefe(cual, **k):
    return {'A': el.boreala, 'B': el.nocturna, 'C': el.duneara}[cual](**k)


# ----------------------------------------------------------------------
#  Las escenas
# ----------------------------------------------------------------------
NOMBRE = {'A': 'Boreala, la Zancuda del Norte', 'B': 'Nocturna, la Bestia sin Cielo', 'C': 'Duneara, la que Nada en la Arena'}
CAMARA_HEROE = {
    'A': ((-34.0, 12.0, 20.0), (0.0, 16.0, 1.0), 52),
    'B': ((12.0, 6.0, 30.0), (0.0, 10.5, 3.0), 50),
    'C': ((-21.0, 15.0, 25.0), (0.0, 4.0, 0.0), 50),
}
CAMARA_CABEZA = {
    'A': ((-12.5, 23.0, 14.5), (0.0, 22.2, 14.0), 50),
    'B': ((2.5, 11.5, 24.0), (0.0, 10.4, 8.5), 46),
    'C': ((-4.0, 4.6, 20.5), (0.0, 3.0, 10.0), 50),
}
DE_CERCA = {'A': dict(boca=30.0), 'B': dict(abre=34.0), 'C': dict(abre=36.0)}
DE_LEJOS = {'A': {}, 'B': dict(abre=8.0), 'C': {}}
SUB_HEROE = {
    'A': 'zancuda de seis patas + caparazon de glaciar + cuello de garza + la aurora por vela',
    'B': 'bestia de nudillos + alas plegadas como un manto + la luna llena por cara',
    'C': 'aletas de raya + escarabajo de lapislazuli + cola de escorpion + un segundo sol',
}
SUB_CABEZA = {
    'A': 'la lanza de hielo, las barbas de carambano y tres ojos por lado',
    'B': 'la luna se parte en dos y se abre: detras, el vacio',
    'C': 'la boca es un pozo de arena que gira hacia el ambar',
}


def escena(cual, camara, kw, nombre, sub, n_motas):
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    niebla = qe.Niebla(SITIO[cual]['niebla'], *NIEBLA_D[cual])
    ojo, obj, fov = camara
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, cual)
    decorado(lz, cam, niebla, cual)
    qs, info = jefe(cual, **kw)
    el.dibujar(lz, cam, qs, SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    img = componer(lz, cam, W, H, cual, n_motas=n_motas)
    return qe.rotular(img, nombre, sub)


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE[cual], DE_LEJOS[cual], NOMBRE[cual], SUB_HEROE[cual], 170), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA[cual], DE_CERCA[cual], NOMBRE[cual].split(',')[0], SUB_CABEZA[cual], 110), 'cabeza_' + cual)


def trio():
    """Los tres juntos, con un jugador delante: la escala."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    niebla = qe.Niebla(SITIO['T']['niebla'], *NIEBLA_D['T'])
    cam = vr.Camara((4.0, 10.0, 170.0), (2.0, 10.0, 0.0), 23, W * SS, H * SS)
    suelo(lz, cam, niebla, 'T', ext=320, paso=32)
    for cual, x, giro in (('A', -42.0, 25), ('B', 0.0, 10), ('C', 40.0, -25)):
        qs, info = jefe(cual, **DE_LEJOS[cual])
        el.dibujar(lz, cam, qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(giro * D)), SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(2.0, 40.0, 0)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)
    img = componer(lz, cam, W, H, 'T', n_motas=40)
    guardar(qe.rotular(img, 'Los tres, a escala', 'un jugador (1,8) delante · de alto: Boreala 28 (29 con la aurora) · Nocturna 20 · Duneara 15 con el sol'), 'trio')


def materiales():
    """La lamina de materiales: cada loseta ampliada, con su nombre."""
    W = 1600
    hojas = [
        ('hielo', 'glaciar con la aurora dentro'), ('hielo_claro', 'carambano y cristal'), ('hueso_frio', 'hueso con escarcha'),
        ('escarcha', 'escarcha en helecho'), ('aurora', 'LUZ: la cortina de aurora'), ('ojo_aurora', 'LUZ: ojo'),
        ('noche', 'piel de cielo con constelacion'), ('membrana_noche', 'el ala plegada'), ('plata', 'hueso de plata'),
        ('luna', 'la cara: la luna llena'), ('vacio', 'el vacio'), ('anillo', 'LUZ: anillo de la estrella'),
        ('nebulosa', 'LUZ: nebulosa'),
        ('lapis', 'lapislazuli con pirita'), ('aleta', 'aleta con ocelos'),
        ('aleta_punta', 'aleta deshecha en arena'), ('duna', 'arena rizada'), ('remolino', 'la arena que cae al pozo'),
        ('diente_sol', 'diente y hueso al sol'), ('ambar', 'LUZ: el sol de la cola'), ('ojo_compuesto', 'ojo compuesto de ambar'),
    ]
    cols, celda = 5, 248
    filas = (len(hojas) + cols - 1) // cols
    H = 120 + filas * (celda + 70)
    img = Image.new('RGB', (W, H), (16, 15, 22))
    d = ImageDraw.Draw(img)
    try:
        f1 = ImageFont.truetype(FUENTE + 'georgiab.ttf', 40)
        f2 = ImageFont.truetype(FUENTE + 'consola.ttf', 18)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((48, 34), 'Materiales: dibujados aqui, ninguno de vanilla', font=f1, fill=(244, 234, 210))
    for k, (mat, nota) in enumerate(hojas):
        t = qm.MAT[mat]
        h, w = t.shape[:2]
        esc = min(200 / w, 200 / h)
        im = Image.fromarray(t).resize((int(w * esc), int(h * esc)), Image.NEAREST)
        cx = 60 + (k % cols) * 306
        cy = 120 + (k // cols) * (celda + 70)
        fondo = Image.new('RGBA', (200, 200), (34, 32, 46, 255))
        fondo.paste(im, ((200 - im.width) // 2, (200 - im.height) // 2), im)
        img.paste(fondo.convert('RGB'), (cx, cy))
        d.rectangle((cx - 1, cy - 1, cx + 200, cy + 200), outline=(80, 76, 100))
        d.text((cx, cy + 210), mat, font=f2, fill=(244, 234, 210))
        d.text((cx, cy + 234), nota[:27], font=f2, fill=(170, 164, 190))
    guardar(img, 'materiales')


ESCENAS = {
    'heroe_A': lambda: heroe('A'), 'heroe_B': lambda: heroe('B'), 'heroe_C': lambda: heroe('C'),
    'cabeza_A': lambda: cabeza('A'), 'cabeza_B': lambda: cabeza('B'), 'cabeza_C': lambda: cabeza('C'),
    'trio': trio, 'materiales': materiales,
}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

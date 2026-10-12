"""
Renders de la ficha de tres jefes hechos «de la cabeza hacia fuera» (12-10-2026):
cada uno en su sitio, de abajo y con la cabeza grande; la boca de cerca, de
frente; los tres juntos con un jugador; y la lamina de materiales. Un solo neon por
jefe, y el brillo como en las de Espinara.

  A  Lutia      el lago de noche, con bruma y lirios
  B  Farolera   la cueva de las telaranas
  C  Otonara    el bosque de otono al anochecer

Uso: python fauces_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import bestias_modelo as bm
import fauces_modelo as fm

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
FUENTE = 'C:/Windows/Fonts/'
TAU = math.tau
D = vr.D2R
_r = bm._r

SITIO = {
    'A': dict(
        luces=[((-0.3, 0.6, -1.0), (0.75, 0.9, 1.0), 1.1, 'contra'), ((0.5, 0.7, 0.8), (0.55, 0.62, 0.82), 0.7, 'llave'),
               ((0.0, -0.4, 1.0), (0.35, 0.8, 0.95), 0.45, 'llave')],
        amb=(0.16, 0.17, 0.23), niebla=(0.05, 0.08, 0.12), niebla_d=(26, 100),
        cielo=((0.005, 0.01, 0.025), (0.03, 0.05, 0.09), (0.08, 0.13, 0.2)),
        suelo=_r('05080e', '080c16', '0c121e', '101828', '162034'), motas=((190, 240, 255), (230, 245, 255)),
    ),
    'B': dict(
        luces=[((0.0, 0.5, -1.0), (1.0, 0.62, 0.25), 1.1, 'contra'), ((0.4, 0.8, 0.7), (0.66, 0.56, 0.48), 0.8, 'llave'),
               ((0.0, -0.3, 1.0), (1.0, 0.6, 0.2), 0.45, 'llave')],
        amb=(0.24, 0.19, 0.15), niebla=(0.07, 0.04, 0.02), niebla_d=(20, 80),
        cielo=((0.01, 0.006, 0.004), (0.03, 0.018, 0.01), (0.08, 0.045, 0.02)),
        suelo=_r('0c0a08', '14110e', '1c1814', '26201a', '322a22'), motas=((255, 200, 120), (230, 220, 200)),
    ),
    'C': dict(
        luces=[((0.2, 0.4, -1.0), (1.0, 0.5, 0.3), 1.1, 'contra'), ((-0.6, 0.6, 0.6), (0.78, 0.56, 0.5), 0.7, 'llave'),
               ((0.0, -0.4, 1.0), (1.0, 0.3, 0.2), 0.4, 'llave')],
        amb=(0.17, 0.12, 0.12), niebla=(0.2, 0.08, 0.07), niebla_d=(26, 100),
        cielo=((0.04, 0.02, 0.04), (0.24, 0.07, 0.07), (0.62, 0.22, 0.12)),
        suelo=_r('1a0a06', '2a1208', '3c1c0c', '522812', '6a3a1c'), motas=((255, 120, 60), (220, 140, 60)),
    ),
}
for _k, _s in SITIO.items():
    qm._reg('suelo_fau_' + _k, qm._suelo_grande(40 + ord(_k), _s['suelo'], None, grietas=_k == 'B'))


def p_roca(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 2.5)
    return bm._imagen(bm._luz(idx, cara), _r('0e0c0a', '1a1714', '26221e', '342e28', '463e36')), None


def p_tronco(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 2.0)
    idx[:, ::3] -= 1
    return bm._imagen(np.clip(bm._luz(idx, cara), 0, 4), _r('080606', '120e0c', '1c1612', '28201a', '362a22')), None


def p_hoja_flota(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 2.0)
    return bm._imagen(bm._luz(idx, cara), _r('06120c', '0c2014', '14301c', '1e4428', '2c5c36')), None


def suelo(lz, cam, niebla, sitio, ext=160, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_fau_' + sitio))

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


def decorado(lz, cam, niebla, sitio, semilla=3, lejos=12):
    r = random.Random(semilla)
    qs = []

    def libre():
        while True:
            x, z = r.uniform(-46, 46), r.uniform(-48, 36)
            if math.hypot(x, z) > lejos and math.hypot(x - cam.ojo[0], z - cam.ojo[2]) > 10:
                return x, z

    if sitio == 'A':
        for _ in range(40):                                   # nenufares con su lirio
            x, z = libre()
            w = r.uniform(0.8, 1.6)
            bm.redondo(qs, vr.T(x, 0.01, z), 0, 0.05, w, w, p_hoja_flota, n=3)
            if r.random() < 0.5:
                for j in range(6):
                    bm.cubo(qs, vr.T(x, 0.05, z) @ vr.Ry(j * 60 * D) @ vr.Rx(-55 * D), -0.1, 0, -0.03, 0.2, 0.5, 0.06, fm.p_lirio)
        for _ in range(30):                                   # juncos secos
            x, z = libre()
            for j in range(r.randint(2, 4)):
                h = r.uniform(1.5, 3.5)
                bm.caja_c(qs, vr.T(x + r.uniform(-0.6, 0.6), 0, z + r.uniform(-0.6, 0.6)) @ vr.Rz(r.uniform(-12, 12) * D), 0, h / 2, 0, 0.1, h, 0.1,
                          p_tronco)
    elif sitio == 'B':
        piedras = []
        for _ in range(14):
            x, z = libre()
            h = r.uniform(3, 10)
            M = vr.T(x, 0, z) @ vr.Rz(r.uniform(-6, 6) * D)
            for k in range(3):
                g = 1.2 * (1 - k * 0.3)
                bm.cubo(qs, M, -g, h * k / 3, -g, 2 * g, h / 3 + 0.1, 2 * g, p_roca)
            piedras.append(np.array((x, h * 0.8, z)))
        for i in range(len(piedras)):                         # telaranas entre las rocas
            for j in range(i + 1, len(piedras)):
                if np.linalg.norm(piedras[i] - piedras[j]) < 18 and r.random() < 0.5:
                    bm.viga(qs, piedras[i], piedras[j], 0.05, 0.05, fm.p_seda)
        for _ in range(16):
            x, z = libre()
            bm.viga(qs, (x, 0, z), (x + r.uniform(-1, 1), 25, z + r.uniform(-1, 1)), 0.05, 0.05, fm.p_seda)
    elif sitio == 'C':
        for _ in range(14):                                   # arboles pelados
            x, z = libre()
            h = r.uniform(7, 15)
            M = vr.T(x, 0, z) @ vr.Rz(r.uniform(-6, 6) * D)
            bm.cubo(qs, M, -0.6, 0, -0.6, 1.2, h, 1.2, p_tronco)
            for k in range(r.randint(2, 4)):
                a = r.uniform(0, TAU)
                y0 = h * r.uniform(0.5, 0.9)
                bm.viga(qs, bm.punto(M, (0, y0, 0)), bm.punto(M, (math.cos(a) * 3, y0 + r.uniform(1, 3), math.sin(a) * 3)), 0.35, 0.35, p_tronco)
        for _ in range(140):                                  # hojarasca por el suelo
            x, z = r.uniform(-30, 30), r.uniform(-30, 26)
            if math.hypot(x - cam.ojo[0], z - cam.ojo[2]) < 3:
                continue
            fm.hoja(qs, vr.T(x, 0.03, z) @ vr.Ry(r.uniform(0, TAU)) @ vr.Rz(r.uniform(-10, 10) * D), r.uniform(0.6, 1.1), 0.5,
                    fm.HOJAS[r.randrange(3)])
    fm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


def hojas_al_aire(lz, cam, niebla, n=40, semilla=9):
    r = random.Random(semilla)
    qs = []
    for _ in range(n):
        p = np.array((r.uniform(-14, 14), r.uniform(1, 18), r.uniform(-8, 14)))
        M = vr.T(*p) @ vr.Ry(r.uniform(0, TAU)) @ vr.Rx(r.uniform(0, TAU)) @ vr.Rz(r.uniform(0, TAU))
        fm.hoja(qs, M, r.uniform(0.6, 1.0), 0.45, fm.HOJAS[r.randrange(3)])
    fm.dibujar(lz, cam, qs, SITIO['C']['luces'], SITIO['C']['amb'], niebla)


def cielo(W, H, horizonte, sitio):
    arriba, medio, abajo = (np.array(c) for c in SITIO[sitio]['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    if sitio in ('A', 'T'):
        mx, my, mr = W * 0.2, H * 0.17, H * 0.08
        d = np.hypot(xx - mx, yy - my) / mr
        col += np.clip(1 - (d - 1) / 5, 0, 1)[..., None] ** 2.5 * np.array((0.2, 0.26, 0.34))
        col = np.where((d < 1)[..., None], np.array((0.86, 0.92, 0.98)), col)
        r = random.Random(7)
        for _ in range(int(W * H / 4000)):
            x, yv = r.randint(0, W - 1), r.randint(0, max(1, int(horizonte * 0.85)))
            col[yv, x] = np.clip(col[yv, x] + r.uniform(0.2, 0.7), 0, 1)
    if sitio == 'C':
        sx, sy = W * 0.72, horizonte - H * 0.02
        d = np.hypot((xx - sx) / W, (yy - sy) / H)
        col += np.clip(1 - d / 0.5, 0, 1)[..., None] ** 2.0 * np.array((0.8, 0.28, 0.1))
    return np.clip(col, 0, 1)


def bruma(arr, horizonte, color, fuerza=0.35, alto=0.18):
    H, W = arr.shape[:2]
    yy = np.arange(H)[:, None].astype(float)
    m = np.exp(-((yy - horizonte) / (H * alto)) ** 2) * fuerza
    return arr * (1 - m[..., None]) + np.array(color) * m[..., None]


def motas(img, n, semilla, colores, viento=(0.0, 1.0), largo=(1, 3)):
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H)
        c = colores[0] if r.random() < 0.6 else colores[1]
        l = r.uniform(*largo) * W / 1600
        d.line((x, y, x + viento[0] * l, y + viento[1] * l), fill=(*c, r.randint(110, 220)), width=max(1, int(r.choice((1, 1, 2)) * W / 1600)))
    glow = capa.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)


def componer(lz, cam, W, H, sitio, n_motas=160, semilla=3, fuerza_vineta=0.5):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, sitio)
    arr = col * alfa + fondo * (1 - alfa)
    if sitio in SITIO and 'niebla' in SITIO[sitio]:
        arr = bruma(arr, horiz, SITIO[sitio]['niebla'], 0.3)
    arr = qe.tono(qe.bloom(arr, emis, radios=((3 * K, 0.8), (14 * K, 0.6), (44 * K, 0.45))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if n_motas <= 0:
        return img
    viento = {'A': (0.2, 0.2), 'B': (0.0, 0.6), 'C': (0.6, -0.6)}[sitio]
    largo = {'A': (1, 2), 'B': (1, 2), 'C': (1, 3)}[sitio]
    return motas(img, int(n_motas * W / 1600), semilla, SITIO[sitio]['motas'], viento, largo)


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    print('ok', nombre, flush=True)
    return img


def jefe(cual, **k):
    return {'A': fm.lutia, 'B': fm.farolera, 'C': fm.otonara}[cual](**k)


NOMBRE = {'A': 'Lutia, el Cisne de Luto', 'B': 'Farolera, la Arana de los Farolillos', 'C': 'Otonara, la Dragona de Hojarasca'}
CAMARA_HEROE = {
    'A': ((12.0, 5.0, 19.0), (0.0, 9.6, 2.5), 54),
    'B': ((3.5, 2.2, 12.5), (0.0, 5.0, 1.5), 60),
    'C': ((6.0, 6.0, 22.0), (0.0, 10.2, 2.0), 56),
}
CAMARA_CABEZA = {
    'A': ((6.0, 11.0, 13.5), (0.0, 12.2, 6.2), 46),
    'B': ((0.9, 3.4, 11.5), (0.0, 4.2, 4.0), 48),
    'C': ((3.0, 11.0, 15.5), (0.0, 13.0, 6.5), 50),
}
SUB_HEROE = {
    'A': 'cisne negro + fauces de lamprea + cresta de plumas + corona de lirios',
    'B': 'arana + saco de huevos que alumbra la cueva como un farol',
    'C': 'dragona de corteza + craneo de ciervo + alas de hojas de otono',
}
SUB_CABEZA = {
    'A': 'el pico se abre como unas fauces; dentro, la boca de lamprea encendida',
    'B': 'ocho ojos de ambar, los colmillos abiertos y la boca encendida',
    'C': 'las astas de rama y la boca que arde como una chimenea',
}


def escena(cual, camara, kw, nombre, sub, n_motas):
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    niebla = qe.Niebla(SITIO[cual]['niebla'], *SITIO[cual]['niebla_d'])
    ojo, obj, fov = camara
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, cual)
    decorado(lz, cam, niebla, cual)
    qs, info = jefe(cual, **kw)
    fm.dibujar(lz, cam, qs, SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    if cual == 'C':
        hojas_al_aire(lz, cam, niebla)
    img = componer(lz, cam, W, H, cual, n_motas=n_motas)
    return qe.rotular(img, nombre, sub)


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE[cual], {}, NOMBRE[cual], SUB_HEROE[cual], 170), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA[cual], {}, NOMBRE[cual].split(',')[0], SUB_CABEZA[cual], 110), 'cabeza_' + cual)


def tres():
    """Los tres juntos, con un jugador delante: la escala."""
    W, H = int(1800 * K), int(820 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    SITIO['T'] = dict(luces=[((0.3, 1.0, 0.6), (0.8, 0.82, 0.95), 0.75, 'llave'), ((-0.3, 0.3, -1.0), (1.0, 0.7, 0.55), 0.5, 'contra')],
                      amb=(0.17, 0.16, 0.21), cielo=((0.02, 0.025, 0.06), (0.1, 0.09, 0.17), (0.34, 0.24, 0.32)),
                      niebla=(0.14, 0.12, 0.18), niebla_d=(120, 260), suelo=_r('16141c', '1a1820', '1e1b24', '221f28', '26222c'))
    qm._reg('suelo_fau_T', qm._suelo_grande(97, SITIO['T']['suelo'], None, grietas=False))
    niebla = qe.Niebla(SITIO['T']['niebla'], *SITIO['T']['niebla_d'])
    cam = vr.Camara((0.0, 8.0, 100.0), (0.0, 7.5, 0.0), 26, W * SS, H * SS)
    suelo(lz, cam, niebla, 'T', ext=200, paso=32, cerca=40)
    for cual, x, giro in (('A', -24.0, 20), ('B', 0.0, 0), ('C', 25.0, -20)):
        qs, info = jefe(cual)
        qs = [q for q in qs if max(p[1] for p in q[0]) < 18]
        fm.dibujar(lz, cam, qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(giro * D)), SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(2.0, 14.0, 0)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)

    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    arr = col * alfa + cielo(W, H, horiz, 'T') * (1 - alfa)
    arr = qe.vineta(qe.tono(qe.bloom(arr, emis, radios=((3 * K, 0.8), (14 * K, 0.6), (44 * K, 0.45)))), 0.4)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    guardar(qe.rotular(img, 'Los tres, a escala', 'un jugador (1,8) delante · de alto: Lutia %s · Farolera %s con las patas en alto · Otonara %s con las astas' % _altos()),
            'tres')


def _altos():
    out = []
    for f in (fm.lutia, fm.farolera, fm.otonara):
        qs, _ = f()
        out.append('%.0f' % max(max(p[1] for p in q[0]) for q in qs if max(p[1] for p in q[0]) < 18))
    return tuple(out)


def materiales():
    W = 1600
    hojas = [
        (fm.p_pluma_luto, 'pluma de luto', 'negra con reflejo de plata'), (fm.p_boca_luz, 'boca', 'LUZ: el pico por dentro'),
        (fm.p_pico, 'pico', 'rojo de cisne negro'), (fm.p_disco, 'disco', 'LUZ: la boca de lamprea'), (fm.p_lirio, 'lirio', 'lirio de la corona'),
        (fm.p_quitina_a, 'quitina', 'placas con canto naranja'), (fm.p_farol_ar, 'saco', 'LUZ: el saco que alumbra'),
        (fm.p_colmillo, 'colmillo', 'hueso a negro'), (fm.p_disco_ambar, 'boca', 'LUZ: la boca de ambar'), (fm.p_seda, 'seda', 'hilo de seda'),
        (fm.p_corteza, 'corteza', 'con brasas en los surcos'), (fm.p_hoja_r, 'hoja roja', 'hoja de otono'), (fm.p_hoja_n, 'hoja naranja', 'hoja de otono'),
        (fm.p_hoja_o, 'hoja dorada', 'hoja de otono'), (bm.p_hueso, 'hueso', 'el craneo de ciervo'),
    ]
    cols, celda = 5, 248
    filas = (len(hojas) + cols - 1) // cols
    H = 120 + filas * (celda + 70)
    img = Image.new('RGB', (W, H), (18, 16, 20))
    d = ImageDraw.Draw(img)
    try:
        f1 = ImageFont.truetype(FUENTE + 'georgiab.ttf', 40)
        f2 = ImageFont.truetype(FUENTE + 'consola.ttf', 18)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((48, 34), 'Materiales: pintados por cara, a 16 pixeles por bloque', font=f1, fill=(244, 234, 210))
    for k, (pintor, nombre, nota) in enumerate(hojas):
        t, e = pintor(32, 32, 'frente', 7 + k)
        fondo = Image.new('RGBA', (32, 32), (40, 36, 46, 255))
        fondo.alpha_composite(Image.fromarray(t))
        im = fondo.resize((200, 200), Image.NEAREST)
        cx = 60 + (k % cols) * 306
        cy = 120 + (k // cols) * (celda + 70)
        img.paste(im.convert('RGB'), (cx, cy))
        d.rectangle((cx - 1, cy - 1, cx + 200, cy + 200), outline=(80, 74, 90))
        d.text((cx, cy + 210), nombre, font=f2, fill=(244, 234, 210))
        d.text((cx, cy + 234), nota[:27], font=f2, fill=(170, 162, 180))
    guardar(img, 'materiales')


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

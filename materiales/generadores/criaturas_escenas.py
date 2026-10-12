"""
Renders de la ficha de cuatro jefes que no salen de animales (12-10-2026): cada
uno en su sitio, su cabeza de cerca, los cuatro con un jugador para la escala y
la lamina de materiales.

  A  Micelia     la umbria de las setas, con esporas en el aire
  B  Betuna      el pozo de brea al caer la tarde
  C  Mandragora  el huerto abandonado, de noche y con bruma
  D  Velaria     la capilla en ruinas, con velas por el suelo

Uso: python criaturas_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import criaturas_modelo as cm

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
        luces=[((0.3, 0.9, 0.7), (0.62, 0.72, 0.8), 0.75, 'llave'), ((-0.3, 0.4, -1.0), (0.35, 0.95, 0.85), 0.8, 'contra'),
               ((0.9, 0.2, 0.2), (0.6, 0.45, 0.85), 0.35, 'llave')],
        amb=(0.14, 0.16, 0.18), niebla=(0.05, 0.12, 0.12), niebla_d=(24, 95),
        cielo=((0.01, 0.02, 0.03), (0.03, 0.07, 0.08), (0.08, 0.18, 0.18)),
        suelo=_r('0c120e', '142018', '1c2c22', '263a2c', '324a36'), motas=((140, 255, 235), (200, 255, 245)),
    ),
    'B': dict(
        luces=[((0.6, 0.5, 0.7), (1.0, 0.72, 0.52), 1.0, 'llave'), ((-0.4, 0.35, -1.0), (0.95, 0.45, 0.6), 0.75, 'contra'),
               ((-0.7, 0.8, 0.3), (0.5, 0.5, 0.75), 0.3, 'llave')],
        amb=(0.2, 0.17, 0.2), niebla=(0.32, 0.2, 0.24), niebla_d=(30, 120),
        cielo=((0.08, 0.06, 0.14), (0.36, 0.18, 0.26), (0.9, 0.5, 0.32)),
        suelo=_r('0a0a0e', '14141a', '1e1e26', '2a2a34', '3a3a46'), motas=((255, 180, 120), (180, 160, 200)),
    ),
    'C': dict(
        luces=[((-0.4, 0.85, 0.7), (0.72, 0.78, 0.92), 0.85, 'llave'), ((0.4, 0.35, -1.0), (0.75, 0.6, 1.0), 0.6, 'contra'),
               ((0.8, 0.15, 0.3), (0.9, 0.85, 0.5), 0.3, 'llave')],
        amb=(0.17, 0.17, 0.2), niebla=(0.16, 0.16, 0.2), niebla_d=(22, 90),
        cielo=((0.02, 0.025, 0.05), (0.08, 0.09, 0.14), (0.22, 0.22, 0.28)),
        suelo=_r('140e08', '22180e', '322416', '44321e', '58422a'), motas=((210, 215, 235), (200, 180, 240)),
    ),
    'D': dict(
        luces=[((0.4, 0.8, 0.7), (1.0, 0.78, 0.5), 0.8, 'llave'), ((0.0, 0.4, -1.0), (1.0, 0.6, 0.3), 0.6, 'contra'),
               ((-0.8, 0.4, 0.3), (0.45, 0.5, 0.8), 0.35, 'llave')],
        amb=(0.16, 0.14, 0.16), niebla=(0.08, 0.06, 0.08), niebla_d=(22, 85),
        cielo=((0.01, 0.01, 0.025), (0.03, 0.03, 0.06), (0.08, 0.07, 0.12)),
        suelo=_r('1a1816', '24221f', '302d29', '3c3834', '4a4540'), motas=((255, 210, 140), (255, 180, 110)),
    ),
}
for _k, _s in SITIO.items():
    qm._reg('suelo_cri_' + _k, qm._suelo_grande(60 + ord(_k), _s['suelo'], None, grietas=_k == 'D'))


def p_roca(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 2.5)
    return bm._imagen(bm._luz(idx, cara), _r('1c1a1c', '2c292c', '3e3a3e', '545056', '6e6a70')), None


def p_tronco(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 2.0)
    idx[:, ::3] -= 1
    return bm._imagen(np.clip(bm._luz(idx, cara), 0, 4), _r('0c0a08', '1a1610', '2a2418', '3c3422', '50462e')), None


def p_madera(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 2.0)
    idx[::3, :] -= 1
    return bm._imagen(np.clip(bm._luz(idx, cara), 0, 4), _r('1a120a', '2e2014', '46321e', '5e462c', '7a5e3e')), None


def suelo(lz, cam, niebla, sitio, ext=160, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_cri_' + sitio))

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
            x, z = r.uniform(-46, 46), r.uniform(-48, 38)
            if math.hypot(x, z) > lejos and math.hypot(x - cam.ojo[0], z - cam.ojo[2]) > 13:
                return x, z

    if sitio == 'A':
        for _ in range(16):
            x, z = libre()
            h = r.uniform(2.0, 7.0)
            M = vr.T(x, 0, z) @ vr.Rz(r.uniform(-8, 8) * D)
            bm.redondo(qs, M, 0, h, 0.45 + h * 0.06, 0.45 + h * 0.06, cm.p_pie, n=2)
            rr = 1.2 + h * 0.35
            bm.redondo(qs, M, h, h + 0.5, rr, rr, cm.p_sombrero, n=3, caras={'abajo': cm.p_laminas})
            bm.redondo(qs, M, h + 0.5, h + 0.85, rr * 0.65, rr * 0.65, cm.p_sombrero, n=3)
        for _ in range(40):
            x, z = libre()
            cm.setita(qs, vr.T(x, 0, z), r.uniform(0.3, 0.8), r.uniform(0.18, 0.32))
    elif sitio == 'B':
        for _ in range(8):
            x, z = libre()
            h = r.uniform(4, 9)
            M = vr.T(x, 0, z) @ vr.Rz(r.uniform(-12, 12) * D)
            bm.cubo(qs, M, -0.5, 0, -0.5, 1.0, h, 1.0, p_tronco)
            for k in range(r.randint(1, 3)):
                a = r.uniform(0, TAU)
                bm.viga(qs, bm.punto(M, (0, h * r.uniform(0.6, 0.95), 0)),
                        bm.punto(M, (math.cos(a) * 2.2, h * r.uniform(0.8, 1.1), math.sin(a) * 2.2)), 0.35, 0.35, p_tronco)
        for _ in range(10):
            x, z = libre()
            bm.redondo(qs, vr.T(x, 0, z), 0, 0.12, r.uniform(1.5, 4.0), r.uniform(1.2, 3.0), cm.p_brea, n=3)
        for _ in range(6):
            x, z = libre()
            g = r.uniform(0, TAU)
            for j in range(4):
                M = vr.T(x, 0, z) @ vr.Ry(g) @ vr.T(0, 0, j * 1.1)
                bm.viga(qs, bm.punto(M, (-1.2, -0.2, 0)), bm.punto(M, (-0.8, 2.0 - abs(j - 1.5) * 0.4, 0.2)), 0.22, 0.22, bm.p_hueso)
    elif sitio == 'C':
        for k in range(14):
            z = -40 + k * 3.0
            if abs(z) < 7:
                continue
            bm.cubo(qs, vr.T(0, 0, z), -60, 0, -0.6, 120, 0.35, 1.2, cm.p_tierra)
        for _ in range(10):
            x, z = libre()
            for j in range(r.randint(2, 4)):
                bm.cubo(qs, vr.T(x + j * 2.0, 0, z) @ vr.Rz(r.uniform(-12, 12) * D), -0.12, 0, -0.12, 0.24, r.uniform(1.4, 2.0), 0.24, p_madera)
            bm.cubo(qs, vr.T(x, 1.2, z), -0.3, 0, -0.08, 2.0 * (r.randint(2, 4) - 1) + 0.6, 0.18, 0.16, p_madera)
        for _ in range(26):
            x, z = libre()
            for j in range(3):
                a = r.uniform(0, TAU)
                bm.viga(qs, (x, 0, z), (x + math.cos(a) * 0.6, r.uniform(0.6, 1.2), z + math.sin(a) * 0.6), 0.12, 0.12, cm.p_hoja_m)
    elif sitio == 'D':
        for _ in range(9):
            x, z = libre()
            h = r.uniform(3, 9)
            M = vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 1.5))
            bm.cubo(qs, M, -0.9, 0, -0.9, 1.8, h, 1.8, p_roca)
            bm.cubo(qs, M, -1.1, h - 0.4, -1.1, 2.2, 0.5, 2.2, p_roca)
        for _ in range(60):
            x, z = libre()
            cm.vela(qs, vr.T(x, 0, z) @ vr.Rz(r.uniform(-6, 6) * D), r.uniform(0.3, 1.1), r.uniform(0.12, 0.22), semilla=r.randrange(9))
        for _ in range(6):
            x, z = libre()
            bm.cubo(qs, vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 1.5)), -1.4, 0, -0.7, 2.8, 0.5, 1.4, p_roca)
    cm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


def cielo(W, H, horizonte, sitio):
    arriba, medio, abajo = (np.array(c) for c in SITIO[sitio]['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    if sitio in ('C', 'T'):
        yy, xx = np.mgrid[0:H, 0:W].astype(float)
        mx, my, mr = W * 0.8, H * 0.2, H * 0.06
        d = np.hypot(xx - mx, yy - my) / mr
        col += np.clip(1 - (d - 1) / 4, 0, 1)[..., None] ** 2.5 * np.array((0.22, 0.22, 0.28))
        col = np.where((d < 1)[..., None], np.array((0.88, 0.9, 0.95)), col)
    return np.clip(col, 0, 1)


def lejanias(img, horizonte, sitio, semilla=5):
    W, H = img.size
    d = ImageDraw.Draw(img)
    r = random.Random(semilla)

    def cresta(alto, rugoso, pasos=64):
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

    colores = {'A': ((8, 20, 20), (5, 14, 14)), 'B': ((60, 34, 48), (40, 24, 34)), 'C': ((20, 20, 30), (14, 14, 22)),
               'D': ((8, 8, 12), (5, 5, 8))}[sitio]
    for (alto, rug), col in zip(((0.1, 0.62), (0.05, 0.55)), colores):
        pts = cresta(alto, rug)
        d.polygon(pts + [(W, horizonte + 2), (0, horizonte + 2)], fill=col)
    return img


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


def componer(lz, cam, W, H, sitio, n_motas=140, semilla=3, fuerza_vineta=0.45, lejos=True):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, sitio)
    if lejos:
        fondo = np.array(lejanias(Image.fromarray((fondo * 255).astype(np.uint8)), int(horiz), sitio)).astype(float) / 255
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * 0.8, radios=((3 * K, 0.6), (12 * K, 0.4), (36 * K, 0.25))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if n_motas <= 0:
        return img
    viento = {'A': (0.2, -0.6), 'B': (0.0, 0.3), 'C': (1.0, 0.2), 'D': (0.0, -0.5)}[sitio]
    largo = {'A': (1, 2), 'B': (1, 2), 'C': (2, 6), 'D': (1, 2)}[sitio]
    return motas(img, int(n_motas * W / 1600), semilla, SITIO[sitio]['motas'], viento, largo)


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    print('ok', nombre, flush=True)
    return img


def jefe(cual, **k):
    return {'A': cm.micelia, 'B': cm.betuna, 'C': cm.mandragora, 'D': cm.velaria}[cual](**k)


NOMBRE = {'A': 'Micelia, la Reina de las Esporas', 'B': 'Betuna, la que Todo lo Traga', 'C': 'Mandragora, la Raiz que Grita',
          'D': 'Velaria, la que se Derrite'}
CAMARA_HEROE = {
    'A': ((9.0, 6.5, 19.0), (0.0, 7.0, 0.5), 50),
    'B': ((10.0, 6.0, 17.0), (0.0, 3.4, 0.8), 50),
    'C': ((8.0, 5.5, 18.0), (0.0, 6.4, 0.5), 50),
    'D': ((8.0, 5.0, 17.0), (0.0, 5.8, 0.5), 50),
}
CAMARA_CABEZA = {
    'A': ((3.4, 6.6, 9.8), (0.0, 8.1, 1.6), 50),
    'B': ((3.5, 4.8, 10.5), (0.0, 4.0, 2.5), 46),
    'C': ((2.8, 8.4, 10.5), (0.0, 8.4, 1.8), 50),
    'D': ((3.0, 8.6, 9.0), (0.4, 8.6, 1.2), 46),
}
SUB_HEROE = {
    'A': 'una seta que anda: el sombrero por cabeza y las laminas por boca',
    'B': 'un charco de brea que se levanta, con lo que se trago dentro',
    'C': 'una raiz que grita, con corona de hojas y flores moradas',
    'D': 'una figura de cera que se derrite, con velas por corona',
}
SUB_CABEZA = {
    'A': 'el pie se raja y dentro brillan las laminas',
    'B': 'la boca hierve, y los ojos son burbujas con fuego',
    'C': 'dos huecos por ojos y la boca abierta del grito',
    'D': 'ojos de llama y la boca que se escurre',
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
    cm.dibujar(lz, cam, qs, SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    img = componer(lz, cam, W, H, cual, n_motas=n_motas)
    return qe.rotular(img, nombre, sub)


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE[cual], {}, NOMBRE[cual], SUB_HEROE[cual], 150), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA[cual], {}, NOMBRE[cual].split(',')[0], SUB_CABEZA[cual], 90), 'cabeza_' + cual)


def cuatro():
    """Los cuatro juntos, con un jugador delante: la escala."""
    W, H = int(1800 * K), int(820 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    SITIO['T'] = dict(luces=[((0.3, 1.0, 0.6), (0.85, 0.85, 0.95), 0.85, 'llave'), ((-0.3, 0.3, -1.0), (1.0, 0.7, 0.55), 0.5, 'contra')],
                      amb=(0.2, 0.19, 0.24), cielo=((0.04, 0.05, 0.1), (0.16, 0.14, 0.24), (0.5, 0.36, 0.42)),
                      niebla=(0.2, 0.17, 0.24), niebla_d=(120, 260), suelo=_r('201e26', '24222c', '282530', '2c2934', '302d38'),
                      motas=((255, 230, 210), (210, 215, 255)))
    qm._reg('suelo_cri_T', qm._suelo_grande(98, SITIO['T']['suelo'], None, grietas=False))
    niebla = qe.Niebla(SITIO['T']['niebla'], *SITIO['T']['niebla_d'])
    cam = vr.Camara((2.0, 6.5, 92.0), (2.0, 5.5, 0.0), 25, W * SS, H * SS)
    suelo(lz, cam, niebla, 'T', ext=200, paso=32, cerca=40)
    for cual, x, giro in (('A', -20.0, 20), ('B', -6.0, 10), ('C', 8.0, -10), ('D', 21.0, -20)):
        qs, info = jefe(cual)
        cm.dibujar(lz, cam, qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(giro * D)), SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(1.0, 14.0, 0)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)
    img = componer(lz, cam, W, H, 'T', n_motas=0, lejos=False)
    guardar(qe.rotular(img, 'Las cuatro, a escala', 'un jugador (1,8) delante · de alto: Micelia %s · Betuna %s · Mandragora %s · Velaria %s'
                       % _altos()), 'cuatro')


def _altos():
    out = []
    for f in (cm.micelia, cm.betuna, cm.mandragora, cm.velaria):
        qs, _ = f()
        out.append(('%.0f' % max(p[1] for q in qs for p in q[0])))
    return tuple(out)


def materiales():
    """La lamina de materiales: cada pintor en una cara de 4 x 4 bloques, a pixel grande."""
    W = 1600
    hojas = [
        (cm.p_sombrero, 'sombrero', 'ciruela con pecas de luz'), (cm.p_laminas, 'laminas', 'LUZ: laminas por boca'),
        (cm.p_pie, 'pie', 'pie de seta con fibra'), (cm.p_yesca, 'yesca', 'hongo de repisa'), (cm.p_micelio, 'micelio', 'micelio'),
        (cm.p_brea, 'brea', 'brea con brillo de aceite'), (cm.p_burbuja, 'burbuja', 'LUZ: ojo de burbuja'),
        (bm.p_boca_brasa, 'hervor', 'LUZ: la boca que hierve'), (cm.p_hierro, 'hierro', 'hierro con oxido'), (cm.p_farol, 'farol', 'LUZ: el farol tragado'),
        (cm.p_raiz, 'raiz', 'raiz con anillos y nudos'), (cm.p_raicilla, 'raicilla', 'raicillas'), (cm.p_hoja_m, 'hoja', 'hoja con su nervio'),
        (cm.p_flor_m, 'flor', 'flor de mandragora'), (cm.p_hueco, 'hueco', 'LUZ: el fondo del grito'),
        (cm.p_cera, 'cera', 'cera con goterones'), (cm.p_cera_roja, 'lacre', 'manto de lacre'), (cm.p_llama, 'llama', 'LUZ: llama'),
        (cm.p_mecha, 'mecha', 'mecha quemada'), (cm.p_tierra, 'tierra', 'tierra pegada'),
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
    d.text((48, 34), 'Materiales: pintados por cara, a 8 pixeles por bloque', font=f1, fill=(244, 234, 210))
    for k, (pintor, nombre, nota) in enumerate(hojas):
        t, e = pintor(32, 32, 'arriba' if pintor is cm.p_yesca else 'frente', 7 + k)
        im = Image.fromarray(t).resize((200, 200), Image.NEAREST)
        cx = 60 + (k % cols) * 306
        cy = 120 + (k // cols) * (celda + 70)
        img.paste(im.convert('RGB'), (cx, cy))
        d.rectangle((cx - 1, cy - 1, cx + 200, cy + 200), outline=(80, 74, 90))
        d.text((cx, cy + 210), nombre, font=f2, fill=(244, 234, 210))
        d.text((cx, cy + 234), nota[:27], font=f2, fill=(170, 162, 180))
    guardar(img, 'materiales')


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABCD'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABCD'})
ESCENAS.update({'cuatro': cuatro, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

"""
Renders de la ficha de cuatro jefes (12-10-2026): cada uno en su sitio y con su
luz, su cabeza de cerca, los cuatro con un jugador para la escala y la lamina de
materiales. Luz contenida: el brillo va en la boca y en poco mas.

  A  Yelmora   un valle de hielo al anochecer, con nieve que cae
  B  Cienara   la cienaga de noche, con luciernagas y niebla verde
  C  Osaria    el campo de huesos al ponerse el sol
  D  Geodra    la cueva de amatista

Uso: python bestias_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
FUENTE = 'C:/Windows/Fonts/'
TAU = math.tau
D = vr.D2R
_r = bm._r


# ----------------------------------------------------------------------
#  Los cuatro sitios
# ----------------------------------------------------------------------
SITIO = {
    'A': dict(
        luces=[((-0.5, 0.8, 0.8), (0.86, 0.9, 1.0), 1.0, 'llave'), ((0.5, 0.4, -1.0), (0.45, 0.85, 1.0), 0.7, 'contra')],
        amb=(0.26, 0.29, 0.36), niebla=(0.36, 0.44, 0.56), niebla_d=(30, 120),
        cielo=((0.1, 0.13, 0.24), (0.32, 0.4, 0.56), (0.66, 0.74, 0.84)),
        suelo=_r('7a8aa2', '98a8be', 'b6c4d6', 'd0dae6', 'e8eef6'), motas=((240, 246, 255), (200, 220, 245)),
    ),
    'B': dict(
        luces=[((0.4, 0.9, 0.6), (0.62, 0.72, 0.6), 0.8, 'llave'), ((-0.4, 0.3, -1.0), (0.55, 1.0, 0.3), 0.75, 'contra')],
        amb=(0.16, 0.2, 0.15), niebla=(0.1, 0.16, 0.1), niebla_d=(26, 100),
        cielo=((0.02, 0.04, 0.04), (0.06, 0.12, 0.08), (0.16, 0.26, 0.14)),
        suelo=_r('0e140a', '18220e', '222e14', '2e3c1a', '3c4c22'), motas=((210, 255, 120), (170, 230, 90)),
    ),
    'C': dict(
        luces=[((0.7, 0.45, 0.6), (1.0, 0.72, 0.5), 1.05, 'llave'), ((-0.3, 0.3, -1.0), (1.0, 0.45, 0.25), 0.7, 'contra')],
        amb=(0.24, 0.18, 0.18), niebla=(0.46, 0.28, 0.22), niebla_d=(30, 130),
        cielo=((0.12, 0.08, 0.14), (0.48, 0.22, 0.2), (0.96, 0.56, 0.3)),
        suelo=_r('3a3028', '4e4236', '625446', '78685a', '908070'), motas=((255, 200, 150), (200, 170, 150)),
    ),
    'D': dict(
        luces=[((0.4, 0.8, 0.7), (0.8, 0.76, 0.95), 0.95, 'llave'), ((0.0, 0.4, -1.0), (0.75, 0.45, 1.0), 0.8, 'contra'),
               ((-0.8, 0.1, 0.4), (0.7, 0.4, 1.0), 0.45, 'llave')],
        amb=(0.2, 0.18, 0.26), niebla=(0.07, 0.04, 0.1), niebla_d=(24, 90),
        cielo=((0.02, 0.015, 0.03), (0.04, 0.025, 0.06), (0.09, 0.05, 0.13)),
        suelo=_r('141218', '1e1a22', '2a252e', '36303c', '443d4c'), motas=((220, 170, 255), (180, 130, 240)),
    ),
}
for _k, _s in SITIO.items():
    qm._reg('suelo_bst_' + _k, qm._suelo_grande(80 + ord(_k), _s['suelo'], _s['suelo'][4] if _k == 'A' else None, grietas=_k in 'CD'))


def p_roca(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 2.5)
    return bm._imagen(bm._luz(idx, cara), _r('1c1a20', '2c2932', '3e3a46', '545060', '6e6a7a')), None


def p_roca_c(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 2.5)
    return bm._imagen(bm._luz(idx, cara), _r('2a221c', '3c322a', '52463a', '6a5c4c', '86766a')), None


def p_tronco(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 2.0)
    idx[:, ::3] -= 1
    return bm._imagen(np.clip(bm._luz(idx, cara), 0, 4), _r('0e0c08', '1c1810', '2c2618', '3e3622', '524830')), None


def p_nieve(tw, th, cara, s):
    idx = bm._tonos(tw, th, s, 3.0)
    return bm._imagen(bm._luz(idx + 1, cara), SITIO['A']['suelo']), None


def suelo(lz, cam, niebla, sitio, ext=160, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_bst_' + sitio))

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


def decorado(lz, cam, niebla, sitio, semilla=3, lejos=13):
    r = random.Random(semilla)
    qs = []

    def libre():
        while True:
            x, z = r.uniform(-48, 48), r.uniform(-50, 40)
            if math.hypot(x, z) > lejos and math.hypot(x - cam.ojo[0], z - cam.ojo[2]) > 14:
                return x, z

    if sitio == 'A':
        for _ in range(12):
            x, z = libre()
            for j in range(r.randint(2, 5)):
                M = vr.T(x + r.uniform(-1.5, 1.5), 0, z + r.uniform(-1.5, 1.5)) @ vr.Rz(r.uniform(-20, 20) * D) @ vr.Rx(r.uniform(-20, 20) * D)
                bm.cristal(qs, M, r.uniform(0.3, 0.7), r.uniform(1.5, 5.0), bm.p_hielo, semilla=j)
            bm.redondo(qs, vr.T(x, -0.4, z), 0, 1.0, 2.4, 2.0, p_nieve, n=3)
    elif sitio == 'B':
        for _ in range(9):
            x, z = libre()
            h = r.uniform(5, 11)
            M = vr.T(x, 0, z) @ vr.Rz(r.uniform(-8, 8) * D)
            bm.cubo(qs, M, -0.6, 0, -0.6, 1.2, h, 1.2, p_tronco)
            for k in range(r.randint(1, 3)):
                a = r.uniform(0, TAU)
                bm.viga(qs, bm.punto(M, (0, h * r.uniform(0.6, 0.95), 0)),
                        bm.punto(M, (math.cos(a) * 2.5, h * r.uniform(0.8, 1.15), math.sin(a) * 2.5)), 0.45, 0.45, p_tronco)
        for _ in range(40):
            x, z = libre()
            for j in range(r.randint(2, 4)):
                h = r.uniform(1.0, 2.6)
                bm.caja_c(qs, vr.T(x + r.uniform(-0.6, 0.6), 0, z + r.uniform(-0.6, 0.6)) @ vr.Rz(r.uniform(-10, 10) * D), 0, h / 2, 0, 0.12, h,
                          0.12, bm.p_junco)
    elif sitio == 'C':
        for _ in range(10):
            x, z = libre()
            g = r.uniform(0, TAU)
            for j in range(5):
                M = vr.T(x, 0, z) @ vr.Ry(g) @ vr.T(0, 0, j * 1.3)
                alto = 3.2 - abs(j - 2) * 0.5
                bm.viga(qs, bm.punto(M, (-1.6, -0.2, 0)), bm.punto(M, (-1.2, alto, 0.2)), 0.28, 0.28, bm.p_hueso)
                bm.viga(qs, bm.punto(M, (-1.2, alto, 0.2)), bm.punto(M, (0.3, alto + 0.9, 0.4)), 0.24, 0.24, bm.p_hueso)
        for _ in range(14):
            x, z = libre()
            w = r.uniform(1.0, 3.0)
            bm.cubo(qs, vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 1.5)), -w / 2, 0, -w / 2, w, r.uniform(0.5, 1.6), w * 0.8, p_roca_c)
    elif sitio == 'D':
        for _ in range(16):
            x, z = libre()
            w = r.uniform(2.0, 5.0)
            bm.cubo(qs, vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 1.5)), -w / 2, 0, -w / 2, w, r.uniform(1.0, 4.0), w * 0.9, p_roca)
            for j in range(r.randint(1, 4)):
                M = vr.T(x + r.uniform(-1.2, 1.2), 0, z + r.uniform(-1.2, 1.2)) @ vr.Rz(r.uniform(-30, 30) * D) @ vr.Rx(r.uniform(-30, 30) * D)
                bm.cristal(qs, M, r.uniform(0.25, 0.55), r.uniform(1.0, 3.2), bm.p_amatista, semilla=j)
    bm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


# ----------------------------------------------------------------------
#  El cielo, lo lejano y el revelado
# ----------------------------------------------------------------------
def cielo(W, H, horizonte, sitio):
    arriba, medio, abajo = (np.array(c) for c in SITIO[sitio]['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    if sitio == 'C':
        yy, xx = np.mgrid[0:H, 0:W].astype(float)
        sx, sy = W * 0.18, horizonte - H * 0.03
        d = np.hypot((xx - sx) / W, (yy - sy) / H)
        col += np.clip(1 - d / 0.45, 0, 1)[..., None] ** 2.2 * np.array((0.9, 0.45, 0.15))
        col = np.where((((xx - sx) ** 2 + (yy - sy) ** 2) < (H * 0.035) ** 2)[..., None], np.array((1.0, 0.86, 0.62)), col)
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

    colores = {'A': ((108, 122, 146), (84, 98, 122)), 'B': ((14, 24, 14), (10, 18, 10)), 'C': ((92, 52, 46), (64, 38, 36)),
               'D': ((10, 8, 14), (6, 5, 9))}[sitio]
    for (alto, rug), col in zip(((0.12, 0.62), (0.06, 0.55)), colores):
        pts = cresta(alto, rug)
        d.polygon(pts + [(W, horizonte + 2), (0, horizonte + 2)], fill=col)
    return img


def motas(img, n, semilla, colores, viento=(0.0, 1.0), largo=(1, 4)):
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


def componer(lz, cam, W, H, sitio, n_motas=140, semilla=3, fuerza_vineta=0.45):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, sitio)
    fondo = np.array(lejanias(Image.fromarray((fondo * 255).astype(np.uint8)), int(horiz), sitio)).astype(float) / 255
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * 0.8, radios=((3 * K, 0.6), (12 * K, 0.4), (36 * K, 0.25))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    viento = {'A': (0.3, 1.0), 'B': (0.0, 0.2), 'C': (1.0, 0.1), 'D': (0.0, 0.3), 'T': (0.0, 1.0)}[sitio]
    largo = {'A': (1, 3), 'B': (1, 2), 'C': (3, 9), 'D': (1, 2), 'T': (1, 2)}[sitio]
    return motas(img, int(n_motas * W / 1600), semilla, SITIO[sitio]['motas'], viento, largo)


def perfilar(lz, mascara, grosor, color=(1.0, 0.97, 1.0)):
    """El contorno blanco: los pixeles de fuera que tocan al bicho y quedan detras de el."""
    zc = np.where(mascara, lz.z, np.inf)
    for _ in range(grosor):
        e = zc.copy()
        e[1:] = np.minimum(e[1:], zc[:-1])
        e[:-1] = np.minimum(e[:-1], zc[1:])
        e[:, 1:] = np.minimum(e[:, 1:], zc[:, :-1])
        e[:, :-1] = np.minimum(e[:, :-1], zc[:, 1:])
        zc = np.where(mascara, zc, e)
    borde = ~mascara & np.isfinite(zc) & (lz.z > zc)
    lz.color[borde] = color
    lz.alfa[borde] = 1.0
    lz.emis[borde] = np.array(color) * 0.15


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    print('ok', nombre, flush=True)
    return img


def jefe(cual, **k):
    return {'A': bm.yelmora, 'B': bm.cienara, 'C': bm.osaria, 'D': bm.geodra}[cual](**k)


# ----------------------------------------------------------------------
#  Las escenas
# ----------------------------------------------------------------------
NOMBRE = {'A': 'Yelmora, la Bestia del Glaciar', 'B': 'Cienara, la Reina del Fango', 'C': 'Osaria, la Carronera',
          'D': 'Geodra, la Topa de Amatista'}
CAMARA_HEROE = {
    'A': ((11.0, 6.5, 22.0), (0.4, 7.8, 1.0), 52),
    'B': ((15.0, 6.5, 18.0), (0.0, 2.4, 0.5), 50),
    'C': ((6.0, 6.0, 19.5), (0.0, 6.2, 1.0), 52),
    'D': ((13.0, 5.5, 17.0), (0.0, 3.4, 1.0), 50),
}
CAMARA_CABEZA = {
    'A': ((4.0, 8.2, 14.5), (0.4, 8.7, 4.5), 46),
    'B': ((5.0, 5.4, 13.0), (0.0, 2.8, 5.6), 46),
    'C': ((5.5, 7.8, 12.0), (0.2, 7.6, 4.6), 42),
    'D': ((-5.0, 4.4, 16.0), (0.0, 2.8, 7.5), 44),
}
SUB_HEROE = {
    'A': 'bruto de pelo blanco + colmillos de morsa + un glaciar en el lomo',
    'B': 'sapo + caiman: la boca de lado a lado y un saco que brilla',
    'C': 'buitre + chacal: alas rotas, pico con dientes y brasas en el pecho',
    'D': 'topo + armadillo: drusas de amatista, palas de cavar y nariz de estrella',
}
SUB_CABEZA = {
    'A': 'la boca de morsa, que echa frio, y los huesos dentro del hielo',
    'B': 'la boca de caiman de lado a lado y los ojos de sapo',
    'C': 'el pico con dientes de sierra y los ojos de brasa',
    'D': 'la nariz de estrella y los dientes de cristal',
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
    z0 = lz.z.copy()
    bm.dibujar(lz, cam, qs, SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return componer(lz, cam, W, H, cual, n_motas=n_motas)                    # sin letras (13-10-2026)


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE[cual], {}, NOMBRE[cual], SUB_HEROE[cual], 150), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA[cual], {}, NOMBRE[cual].split(',')[0], SUB_CABEZA[cual], 90), 'cabeza_' + cual)


def cuatro():
    """Los cuatro juntos, con un jugador delante: la escala."""
    W, H = int(1800 * K), int(820 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    niebla = qe.Niebla((0.2, 0.17, 0.24), 120, 260)
    cam = vr.Camara((2.0, 7.0, 95.0), (2.0, 5.5, 0.0), 26, W * SS, H * SS)
    SITIO['T'] = dict(luces=[((0.3, 1.0, 0.6), (0.85, 0.85, 0.95), 0.85, 'llave'), ((-0.3, 0.3, -1.0), (1.0, 0.7, 0.55), 0.5, 'contra')],
                      amb=(0.2, 0.19, 0.24), cielo=((0.05, 0.06, 0.12), (0.2, 0.16, 0.26), (0.6, 0.42, 0.42)),
                      motas=((255, 230, 210), (210, 215, 255)))
    qm._reg('suelo_bst_T', qm._suelo_grande(99, _r('2a2832', '302d38', '35323e', '3a3744', '403c4a'), None, grietas=False))
    suelo(lz, cam, niebla, 'T', ext=200, paso=32, cerca=40)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x, giro in (('A', -24.0, 25), ('B', -7.0, 15), ('C', 9.0, -10), ('D', 25.0, -25)):
        qs, info = jefe(cual)
        z0 = lz.z.copy()
        bm.dibujar(lz, cam, qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(giro * D)), SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(1.0, 14.0, 0)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)
    guardar(componer_t(lz, cam, W, H), 'cuatro')                             # sin letras


def componer_t(lz, cam, W, H):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, 'T')
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * 0.8, radios=((3 * K, 0.6), (12 * K, 0.4), (36 * K, 0.25))))
    arr = qe.vineta(arr, 0.4)
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


def _altos():
    out = []
    for f in (bm.yelmora, bm.cienara, bm.osaria, bm.geodra):
        qs, _ = f()
        out.append(('%.0f' % max(p[1] for q in qs for p in q[0])))
    return tuple(out)


ALTOS = _altos()


def materiales():
    """La lamina de materiales: cada pintor en una cara de 4 x 4 bloques, a pixel grande."""
    W = 1600
    hojas = [
        (bm.p_pelo, 'pelo', 'pelo de mechones'), (bm.p_hielo, 'hielo', 'hielo de glaciar'), (bm.p_hielo_huesos, 'hielo_huesos', 'con lo que cazo dentro'),
        (bm.p_marfil, 'marfil', 'colmillo con anillos'), (bm.p_piel, 'piel', 'piel de morsa'),
        (bm.p_verruga, 'verruga', 'sapo con pustulas'), (bm.p_vientre, 'vientre', 'tripa a franjas'), (bm.p_saco, 'saco', 'LUZ: el saco verde'),
        (bm.p_encia, 'encia', 'la boca por dentro'), (bm.p_escudo, 'escudo', 'escudos de caiman'),
        (bm.p_pluma, 'pluma', 'plumas rotas'), (bm.p_cuero, 'cuero', 'cuero de buitre'), (bm.p_hueso, 'hueso', 'hueso viejo'),
        (bm.p_brasa, 'brasa', 'LUZ: brasas del pecho'), (bm.p_escama, 'escama', 'canilla de ave'),
        (bm.p_placa, 'placa', 'coraza de bandas'), (bm.p_amatista, 'amatista', 'LUZ: drusa de amatista'), (bm.p_topo, 'topo', 'pelo de topo'),
        (bm.p_nariz, 'nariz', 'la estrella de la nariz'), (bm.p_garra_topo, 'garra', 'unas de cavar'),
    ]
    cols, celda = 5, 248                                                     # sin letras: solo las texturas
    filas = (len(hojas) + cols - 1) // cols
    H = 60 + filas * (celda + 20)
    img = Image.new('RGB', (W, H), (18, 16, 20))
    d = ImageDraw.Draw(img)
    for k, (pintor, nombre, nota) in enumerate(hojas):
        t, e = pintor(32, 32, 'frente', 7 + k)
        im = Image.fromarray(t).resize((200, 200), Image.NEAREST)
        cx = 60 + (k % cols) * 306
        cy = 40 + (k // cols) * (celda + 20)
        img.paste(im.convert('RGB'), (cx, cy))
        d.rectangle((cx - 1, cy - 1, cx + 200, cy + 200), outline=(80, 74, 90))
    guardar(img, 'materiales')


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABCD'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABCD'})
ESCENAS.update({'cuatro': cuatro, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

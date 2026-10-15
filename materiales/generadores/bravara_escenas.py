"""
Renders de Bravara (15-10-2026): sus tres tipos sobre un estanque de lotos al atardecer (el agua quieta, las hojas
flotando, las flores, las hojas altas sobre su tallo, los juncos de la orilla, los bancales de arroz en las lomas y los
montes al fondo, con el cielo de color melocoton y violeta y las luciernagas); su cartel (de cerca y desde abajo); la
cabeza (de cerca, para mirar dentro de la boca); los tres juntos con un jugador; y la lamina de materiales.

Es la primera ficha que no va de noche: la luz es la del sol que se pone, y la de la garganta y las branquias.
Las fotos salen sin letras y con el contorno blanco.

Uso: python bravara_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
     (con RAPIDO=1 en el entorno, a media resolucion para probar)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne            # el jugador de escala
import quimeras_modelo as qm
import quimeras_escenas as qe         # el lienzo, la niebla y el revelado
import bestias_modelo as bm
import sierpe_modelo as sm
import bravara_modelo as am

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
TAU = math.tau
D = vr.D2R
_r = bm._r


def _c(h):
    return tuple(c / 255 for c in nm._hex(h))


# el atardecer de cada tipo: (cielo arriba, en medio, en el horizonte), niebla, ambiente, sol
ATARDECER = {
    'A': (((0.12, 0.08, 0.22), (0.62, 0.3, 0.36), (1.0, 0.66, 0.36)), (0.62, 0.42, 0.4), (0.3, 0.26, 0.36), (1.0, 0.74, 0.5)),
    'B': (((0.06, 0.07, 0.2), (0.4, 0.26, 0.46), (0.96, 0.56, 0.5)), (0.44, 0.34, 0.46), (0.26, 0.26, 0.38), (1.0, 0.72, 0.62)),
    'C': (((0.14, 0.1, 0.24), (0.7, 0.4, 0.4), (1.0, 0.76, 0.5)), (0.66, 0.48, 0.44), (0.32, 0.28, 0.36), (1.0, 0.8, 0.6)),
}


def sitio(v):
    """El mismo estanque para los tres, al atardecer: el sol se pone a la izquierda, por detras."""
    cielo, niebla, amb, sol = ATARDECER[v]
    return dict(
        luces=[((-0.75, 0.32, 0.45), sol, 1.05, 'llave'), ((-0.6, 0.25, -1.0), sol, 1.0, 'contra'),
               ((0.6, 0.4, 0.6), (0.42, 0.46, 0.7), 0.35, 'llave')],
        amb=amb, niebla=niebla, niebla_d=(90, 330), cielo=cielo, sol=sol,
        motas=(255, 236, 140),
    )


# ----------------------------------------------------------------------
#  El estanque: el agua, las hojas, las flores, los juncos, los bancales y los montes
# ----------------------------------------------------------------------
AGUA = _r('0c1a26', '12263a', '1a3450', '264866', '3a6482')


def _agua():
    """El agua quieta: azul hondo con las rizaduras en rayas largas y claras, de traves."""
    n = 128
    rng = random.Random(41)
    t = np.zeros((n, n, 4), np.uint8)
    t[...] = (*AGUA[1], 255)
    for _ in range(140):
        y, x, L = rng.randrange(n), rng.randrange(n), rng.randint(6, 26)
        c = AGUA[rng.choice((2, 2, 3, 3, 4))]
        for k in range(L):
            t[y, (x + k) % n] = (*c, 255)
    for _ in range(60):
        y, x, L = rng.randrange(n), rng.randrange(n), rng.randint(8, 30)
        for k in range(L):
            t[y, (x + k) % n] = (*AGUA[0], 255)
    return t


qm._reg('agua_bra', _agua())


def p_hoja(tw, th, cara, s):
    """La hoja de loto: verde, con los nervios que salen del centro y el canto mas claro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    cx, cy = (tw - 1) / 2, (th - 1) / 2
    ang = np.arctan2(ys - cy, xs - cx)
    idx = np.where((np.round(ang / (TAU / 12)) * (TAU / 12) - ang) ** 2 < 0.004, 3, 2)
    idx[(abs(xs - cx) < 1) & (abs(ys - cy) < 1)] = 1
    return bm._imagen(sm._bisel(idx, 1, 1), _r('0c2210', '163a18', '22561e', '3a7a2a', '5a9a3a')), None


def p_tallo(tw, th, cara, s):
    return bm._imagen(np.full((th, tw), 2), _r('12280e', '1c3a14', '2a5420', '3a6e2a', '4e8a3a')), None


def p_petalo(tw, th, cara, s):
    """El petalo de loto: blanco en la base, rosa hacia la punta, con su vena."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t_ = ys / max(th - 1, 1)
    idx = np.where(t_ < 0.3, 4, np.where(t_ < 0.65, 3, 2))
    idx = np.where(abs(xs - tw / 2 + 0.5) < 0.6, np.clip(idx - 1, 0, 4), idx)
    return bm._imagen(idx, _r('8a2a5a', 'c84a84', 'e87aaa', 'f6b6d0', 'fff0f6')), None


def p_centro(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs + ys) % 3 == 0, 2, 3)
    return bm._imagen(idx, _r('5a4a06', '9a7e10', 'd8b420', 'f2d84a', 'fff08a')), None


def p_junco(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(xs % 3 == 0, 1, 2)
    return bm._imagen(idx, _r('101e0c', '1a3014', '284620', '3a5e2c', '507a3a')), None


def p_espiga(tw, th, cara, s):
    return bm._imagen(sm._bisel(np.full((th, tw), 2), 1, 1), _r('1e0e06', '361a0c', '522a14', '6e3e20', '8a5430')), None


def p_bancal(tw, th, cara, s):
    """El bancal de arroz: verde tierno arriba (el agua en una franja clara) y el muro de tierra en el canto."""
    if cara == 'arriba':
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((ys // 2) % 2 == 0, 3, 2)
        return bm._imagen(idx, _r('1a2e14', '2e4a1e', '4a6a2a', '6a8a3a', '8aa84a')), None
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(ys < 2, 3, 1)
    return bm._imagen(idx, _r('1a140e', '2a2014', '3a2e1e', '4e3e2a', '665238')), None


def p_monte(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=12.0, umbral=0.6, alto=0.85)
    idx = np.array([1, 1, 2, 2, 3])[idx]
    return bm._imagen(idx, _r('141626', '1a1c30', '20223a', '282a44', '30324e')), None


def p_roca(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=6.0, umbral=0.6, alto=0.85)
    if cara == 'arriba':
        return bm._imagen(np.clip(idx, 1, 3), _r('142010', '1e3016', '2a421e', '3a5628', '4a6a32')), None
    return bm._imagen(sm._bisel(np.array([1, 2, 2, 3, 3])[idx]), _r('1a1a1e', '26262c', '34343c', '44444e', '565662')), None


def p_onda(tw, th, cara, s):
    return bm._imagen(np.full((th, tw), 3), _r('2a4a62', '4a6e86', '7a9aae', 'b2c8d4', 'e2eef2')), None


for _f in (p_hoja, p_tallo, p_petalo, p_centro, p_junco, p_espiga, p_bancal, p_monte, p_roca, p_onda):
    _f.__name__ = 'braE_' + _f.__name__


def agua(lz, cam, niebla, S, ext=300, paso=32, cerca=56, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'agua_bra'))

    cx, cz = cam.ojo[0], cam.ojo[2]
    for gx in range(-ext, ext, paso):
        for gz in range(-ext, ext, paso):
            if abs(gx + paso / 2 - cx) < cerca and abs(gz + paso / 2 - cz) < cerca:
                for a in range(gx, gx + paso, paso_cerca):
                    for b in range(gz, gz + paso, paso_cerca):
                        baldosa(a, b, paso_cerca)
            else:
                baldosa(gx, gz, paso)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def loto(qs, x, z, r, semilla, flor=False, alto=0.0):
    """Una hoja de loto (flotando o alta sobre su tallo) y, a veces, la flor."""
    M = vr.T(x, alto + 0.05, z) @ vr.Ry(semilla * 0.7)
    if alto > 0.5:
        bm.cubo(qs, vr.T(x - 0.12, 0.0, z - 0.12), 0, 0, 0, 0.24, alto, 0.24, p_tallo, semilla=semilla)
        M = M @ vr.Rx(0.12)
    bm.redondo(qs, M, 0.0, 0.14, r, r, p_hoja, n=2, semilla=semilla)
    if flor:
        Mf = vr.T(x + r * 0.3, 0.0, z + r * 0.2)
        bm.cubo(qs, Mf, -0.1, 0.0, -0.1, 0.2, 0.8, 0.2, p_tallo, semilla=semilla)
        Mc = Mf @ vr.T(0, 0.8, 0)
        bm.cubo(qs, Mc, -0.35, 0.0, -0.35, 0.7, 0.4, 0.7, p_centro, semilla=semilla)
        for capa, (n, ab, L) in enumerate(((8, 0.55, 1.4), (6, 0.25, 1.6))):
            for j in range(n):
                g = TAU * (j + 0.5 * capa) / n
                Mp = Mc @ vr.Ry(g) @ vr.T(0.0, 0.0, 0.25) @ vr.Rx(-ab)
                bm.cubo(qs, Mp, -0.4, 0.0, -0.06, 0.8, L, 0.12, p_petalo, semilla=semilla + j)


def estanque(lz, cam, niebla, S, semilla=6, libre=None):
    """Las hojas y las flores sobre el agua (sin nada entre la camara y el jefe), los juncos de la orilla, los bancales de
    arroz en las lomas y los montes."""
    r = random.Random(semilla)
    qs = []
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    for k in range(120):
        a = r.uniform(0, TAU)
        rr = r.uniform(9, 120)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.5 and rr < 70:
            continue
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if libre is not None and libre(x, z):
            continue
        alto = r.choice((0.0, 0.0, 0.0, r.uniform(1.0, 3.0))) if rr > 34 else 0.0
        loto(qs, x, z, r.uniform(1.4, 3.4), k, flor=r.random() < 0.1, alto=alto)
    for k in range(70):                                                 # los juncos de la orilla, lejos
        a = r.uniform(0, TAU)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.9:
            continue
        rr = r.uniform(130, 150)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        for j in range(5):
            h = r.uniform(3.0, 6.0)
            M = vr.T(x + r.uniform(-2, 2), 0.0, z + r.uniform(-2, 2)) @ vr.Rz(r.uniform(-0.15, 0.15))
            bm.cubo(qs, M, -0.12, 0.0, -0.12, 0.24, h, 0.24, p_junco, semilla=j)
            if j % 2 == 0:
                bm.cubo(qs, M, -0.25, h * 0.7, -0.25, 0.5, h * 0.22, 0.5, p_espiga, semilla=j)
    lejos = hacia_camara + math.pi                                      # las lomas con sus bancales
    for k in range(9):
        a = lejos + r.uniform(-1.0, 1.0)
        rr = r.uniform(180, 230)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w = r.uniform(50, 80)
        giro = r.uniform(0, 3)
        for j in range(7):
            f = 1.0 - j / 7 * 0.8
            M = vr.T(x, 0, z) @ vr.Ry(giro)
            bm.cubo(qs, M, -w * f / 2, 0, -w * f * 0.3, w * f, 2.6 * (j + 1), w * f * 0.6, p_bancal, semilla=k + j)
    for k in range(12):                                                 # los montes, al fondo
        a = lejos + r.uniform(-1.4, 1.4)
        rr = r.uniform(300, 380)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w, alto = r.uniform(80, 130), r.uniform(40, 80)
        giro = r.uniform(0, 3)
        for j in range(6):
            f = 1.0 - j / 6 * 0.85
            M = vr.T(x, 0, z) @ vr.Ry(giro)
            bm.cubo(qs, M, -w * f / 2, 0, -w * f * 0.3, w * f, alto * (j + 1) / 6, w * f * 0.6, p_monte, semilla=k + j)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def ondas(lz, cam, niebla, S, centro, radios=(3.5, 6.2, 9.4)):
    """Las ondas que deja en el agua: anillos finos y claros."""
    qs = []
    cx, cz = centro
    for R in radios:
        n = 24
        for j in range(n):
            g0, g1 = TAU * j / n, TAU * (j + 1) / n
            p0 = np.array((cx + math.cos(g0) * R, 0.03, cz + math.sin(g0) * R))
            p1 = np.array((cx + math.cos(g1) * R, 0.03, cz + math.sin(g1) * R))
            M = vr.T(*p0) @ vr.Ry(-math.atan2(p1[2] - p0[2], p1[0] - p0[0]))
            bm.cubo(qs, M, 0.0, 0.0, -0.07, float(np.linalg.norm(p1 - p0)), 0.04, 0.14, p_onda, semilla=j)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S, sol_x=0.18):
    """El atardecer: violeta arriba, rosa en medio y melocoton en el horizonte, con el resplandor del sol a la izquierda
    y unas nubes largas y finas, encendidas por debajo."""
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.55, arriba + (medio - arriba) * (k / 0.55), medio + (abajo - medio) * ((k - 0.55) / 0.45))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W * sol_x) / W, (yy - horizonte) / H * 1.6)
    col += np.array(S['sol'])[None, None, :] * (np.exp(-(d / 0.22) ** 2) * 0.45)[..., None]
    r = random.Random(11)
    for _ in range(9):                                                  # las nubes
        cy = r.uniform(0.18, 0.62) * horizonte
        cx, L, g = r.uniform(-0.1, 1.0) * W, r.uniform(0.12, 0.4) * W, max(2, int(r.uniform(0.006, 0.014) * H))
        luz = np.array(S['sol']) * (0.55 + 0.35 * cy / max(horizonte, 1))
        sombra = np.array(S['cielo'][1]) * 0.85
        y0, y1 = int(cy), int(cy + g)
        x0, x1 = int(max(0, cx)), int(min(W, cx + L))
        if x1 > x0 and y1 > y0:
            col[y0:y1, x0:x1] = sombra
            col[y1 - 1:y1 + max(1, g // 3), x0 + 2:x1 - 2] = luz
    return np.clip(col, 0, 1)


def motas(img, n, semilla, color):
    """Las luciernagas: puntos calidos que flotan sobre el agua, con su halo."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(H * 0.35, H)
        g = max(1, int(r.choice((1, 2, 2, 3)) * W / 1600))
        d.rectangle((x, y, x + g, y + g), fill=(*color, r.randint(150, 240)))
    glow = capa.filter(ImageFilter.GaussianBlur(4))
    return Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), glow), capa)


def revelar(lz, cam, W, H, S, n_motas=60, semilla=3, fuerza_vineta=0.35, brillo=0.9):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, S)
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * brillo, radios=((2 * K, 0.5), (10 * K, 0.4), (40 * K, 0.35))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if n_motas > 0:
        img = motas(img, int(n_motas * W / 1600), semilla, S['motas'])
    return img


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=92)
    print('ok', nombre, flush=True)
    return img


def perfilar(lz, mascara, grosor, color=(1.0, 0.97, 1.0)):
    """El contorno blanco: los pixeles de fuera que tocan al monstruo y quedan detras de el."""
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


MODELOS = {}


def modelo(cual):
    if cual not in MODELOS:
        qs, info = am.bravara(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras: 'heroe' (de cuerpo entero, a ras del agua y de tres cuartos, para ver la cabeza y las aletas),
    'cabeza' (de cerca y un poco por debajo, para mirar dentro de la boca) y 'cartel' (de cerca y desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    centro = (lo + hi) / 2
    b = np.asarray(info['boca'], float)
    if vista == 'heroe':
        alto = max(hi[1], (hi[2] - lo[2]) * 0.62)
        d = alto * 0.5 / math.tan(25 * D) * 1.35
        obj = np.array((centro[0], hi[1] * 0.5, centro[2] + 1.5))
        v = np.array((0.82, -0.02, 0.57))
        ojo = obj + v / np.linalg.norm(v) * d
        ojo[1] = 2.2
        return tuple(ojo), tuple(obj), 50
    if vista == 'lado':
        return (60.0, 9.0, -2.0), (0.0, 9.0, -2.0), 40
    if vista == 'cabeza':
        ojo = b + np.array((6.5, 1.2, 11.0))
        ojo[1] = max(ojo[1], 1.6)
        return tuple(ojo), tuple(b + np.array((0.0, -0.4, -2.5))), 56
    alto = max(hi[1], (hi[2] - lo[2]) * 0.62)
    obj = np.array((centro[0], hi[1] * 0.62, centro[2] + 3.0))
    v = np.array((0.7, 0.0, 0.72)) / np.linalg.norm((0.7, 0.0, 0.72))
    ojo = obj + v * alto * 1.1
    ojo[1] = 1.4
    return tuple(ojo), tuple(obj), 64


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: el estanque; Bravara, con la luz de su garganta; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    agua(lz, cam, niebla, S)
    estanque(lz, cam, niebla, S, libre=lambda x, z: lo[0] - 3 < x < hi[0] + 3 and lo[2] - 3 < z < hi[2] + 3)
    ondas(lz, cam, niebla, S, (0.0, -6.0))
    neo = _c(am.VARIANTES[cual]['neon'][1])
    luces = S['luces'] + [(tuple(p) + (8.0,), neo, 1.0, 'punto') for p in info['luces'][:2]]
    z0 = lz.z.copy()
    am.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe', 60), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 30), 'cabeza_' + cual)


def cartel(cual):
    """La presentacion del cartel: de cerca y desde abajo, con el cielo de su atardecer."""
    guardar(escena(cual, 'cartel', 40, brillo=1.2), 'cartel_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos, con la misma luz y un jugador delante, sobre una roca."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 200, 420)
    cam = vr.Camara((0.0, 10.0, 170.0), (0.0, 9.0, 0.0), 22, W * SS, H * SS)
    agua(lz, cam, niebla, S, ext=340, paso=32, cerca=40)
    estanque(lz, cam, niebla, S, semilla=9, libre=lambda x, z: -60 < x < 60 and -24 < z < 40)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -34.0), ('B', 0.0), ('C', 34.0)):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(70 * D))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    qr = []
    bm.cubo(qr, vr.T(16.0, -0.4, 30.0), -1.6, 0.0, -1.4, 3.2, 0.9, 2.8, p_roca, semilla=1)
    qm.dibujar(lz, cam, qr, S['luces'], S['amb'], niebla)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, vr.T(0, 0.5, 0) @ ne.jugador_a_mundo(16.0, 30.0, 0)), S['luces'], S['amb'],
               niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo y, de izquierda a derecha, las escamas, el antifaz, la
    agalla, la raiz y la punta de la aleta, la barba, el ojo, las branquias, la garganta, el colmillo y lo de la
    frente."""
    W = 2100
    filas = []
    for c in formas:
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['escamas'], 'der', 32, 32), (P['antifaz'], 'der', 24, 24), (P['operculo'], 'der', 36, 36),
                      (P['aleta_raiz'], 'frente', 16, 24), (P['aleta_punta'], 'frente', 16, 24), (P['barba'], 'frente', 16, 24),
                      (P['ojo'], 'frente', 12, 12), (P['branquia'], 'der', 16, 24), (P['garganta'], 'frente', 24, 18),
                      (P['colmillo'], 'frente', 8, 20), (P['cuerno'], 'der', 24, 6)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (20, 18, 24))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (44, 40, 50, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 184
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(74, 68, 84))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})
PRUEBAS = {'lado_' + c: (lambda c=c: guardar(escena(c, 'lado', 0), 'lado_' + c)) for c in 'ABC'}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        (ESCENAS.get(k) or PRUEBAS[k])()

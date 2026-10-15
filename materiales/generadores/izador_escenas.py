"""
Renders del Izador (15-10-2026), el mob que te agarra y te lleva al aire: en las cumbres al atardecer (el prado, las
rocas, los pinos, las montanas nevadas y el cielo con nubes), a la escala de Minecraft; la cabeza (de cerca); la foto
de lo que hace (un jugador dentro de la jaula, muy alto: el de Tormenta con el rayo que cae en la jaula y el de Cienaga
camino de su nido); los tres juntos con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python izador_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
     (con RAPIDO=1 en el entorno, a media resolucion para probar)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne            # el jugador
import quimeras_modelo as qm
import quimeras_escenas as qe         # el lienzo, la niebla y el revelado
import bestias_modelo as bm
import izador_modelo as iz

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
TAU = math.tau
D = vr.D2R
_r = bm._r
VUELO = 3.0                # a cuantos bloques del suelo flota en las fotos de cuerpo entero


def _c(h):
    return tuple(c / 255 for c in nm._hex(h))


# el cielo de cada tipo: (arriba, en medio, en el horizonte), niebla, ambiente, sol
CIELO = {
    'A': (((0.12, 0.1, 0.24), (0.56, 0.32, 0.4), (1.0, 0.62, 0.36)), (0.6, 0.44, 0.44), (0.34, 0.3, 0.36), (1.0, 0.7, 0.42)),
    'B': (((0.06, 0.07, 0.12), (0.2, 0.22, 0.3), (0.42, 0.42, 0.48)), (0.3, 0.31, 0.36), (0.24, 0.26, 0.32), (0.7, 0.76, 0.9)),
    'C': (((0.1, 0.12, 0.2), (0.4, 0.4, 0.38), (0.86, 0.7, 0.42)), (0.48, 0.48, 0.42), (0.3, 0.32, 0.3), (1.0, 0.78, 0.5)),
}


def sitio(v):
    """Las mismas cumbres para los tres, al atardecer (el de Tormenta, bajo un cielo de tormenta)."""
    cielo, niebla, amb, sol = CIELO[v]
    return dict(
        luces=[((-0.6, 0.45, 0.4), sol, 0.95, 'llave'), ((-0.5, 0.3, -1.0), sol, 1.0, 'contra'),
               ((0.6, 0.6, 0.6), (0.5, 0.55, 0.7), 0.3, 'llave')],
        amb=amb, niebla=niebla, niebla_d=(30, 140), cielo=cielo, sol=sol,
        motas=(255, 236, 200),
    )


# ----------------------------------------------------------------------
#  Las cumbres: el prado, las rocas, los pinos y las montanas
# ----------------------------------------------------------------------
PRADO = _r('2a3a1a', '34481e', '405826', '4e6a2e', '5e7c36')
PIEDRA = _r('3a3836', '4a4846', '5c5a56', '706c68', '86827c')
NIEVE = _r('a8b0bc', 'c4ccd6', 'dce2ea', 'eef2f6', 'fafcfe')
PINO = _r('0e1c14', '14281a', '1c3622', '26462c', '305436')
CORTEZA = _r('1e140c', '2a1c12', '382618', '46321e', '523c24')


def _prado(semilla):
    rng = random.Random(semilla)
    n = 16
    idx = np.full((n, n), 2)
    for _ in range(30):
        x, y = rng.randrange(n), rng.randrange(n)
        idx[y, x] = rng.choice((1, 3, 3))
        if rng.random() < 0.5:
            idx[(y + 1) % n, x] = idx[y, x]
    return bm._imagen(idx, PRADO)


qm._reg('prado_iz', _prado(7))


def p_piedra(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(((xs // 4) * 3 + (ys // 3) * 5 + s) % 7 == 0, 3, 2)
    idx[(ys % 6) == 5] = 1
    return bm._imagen(idx, PIEDRA), None


def p_nieve(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where(((xs // 3) + (ys // 3) + s) % 5 == 0, 2, 3), NIEVE), None


def p_pino(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = 2 + (((xs // 2) * 5 + (ys // 2) * 3 + s) % 4 == 0).astype(int) - (ys == th - 1)
    return bm._imagen(np.clip(idx, 0, 4), PINO), None


def p_corteza(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where((xs + s) % 3 == 0, 1, 2), CORTEZA), None


def p_palo(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where((ys + xs * 2 + s) % 4 == 0, 3, 2), CORTEZA), None


def p_rayo(tw, th, cara, s):
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (220, 248, 255, 255)
    return t, None


for _n, _f in (('piedra', p_piedra), ('nieve', p_nieve), ('pino', p_pino), ('corteza', p_corteza), ('palo', p_palo),
               ('rayo', p_rayo)):
    _f.__name__ = 'izE_' + _n
bm.PLENOS.add(p_rayo)


def suelo(lz, cam, niebla, S, ext=160, paso=16, cerca=24, paso_cerca=2):
    qs = []

    def baldosa(gx, gz, p):
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(p, 0), (0, 0), (0, p), (p, p)], 'prado_iz'))

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


def pino(qs, x, z, alto, semilla):
    M = vr.T(x, 0.0, z)
    bm.cubo(qs, M, -0.5, 0.0, -0.5, 1.0, alto, 1.0, p_corteza, semilla=semilla)
    n = int(alto / 1.4)
    for j in range(n):
        w = 1.0 + (n - j) * 0.75
        y = alto * 0.3 + j * (alto * 0.72 / n)
        bm.cubo(qs, M, -w / 2, y, -w / 2, w, 1.0, w, p_pino, semilla=semilla + j)


def roca(qs, x, z, alto, ancho, semilla, nieve=False):
    """Una roca o una montana: pisos de piedra que se estrechan y, si es alta, la nieve en lo alto."""
    for j in range(6):
        f = 1.0 - j / 6 * 0.8
        y = alto * j / 6
        pin = p_nieve if nieve and j >= 4 else p_piedra
        bm.cubo(qs, vr.T(x, y, z) @ vr.Ry(semilla), -ancho * f / 2, 0.0, -ancho * f / 2, ancho * f, alto / 6 + 0.01,
                ancho * f, pin, semilla=semilla + j)


def bioma(lz, cam, niebla, S, semilla=4, libre=None, nido=None):
    """Alrededor (sin nada entre la camara y el Izador): pinos y rocas sueltas, y las montanas nevadas al fondo. 'nido'
    pone en (x, z) un pilar de roca con el nido del de Cienaga encima."""
    r = random.Random(semilla)
    qs = []
    libre = libre or (lambda x, z: False)
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    lejos = hacia_camara + math.pi
    for k in range(16):                                                                   # los pinos
        a = lejos + r.uniform(-1.6, 1.6)
        rr = r.uniform(20, 44)
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        if libre(x, z):
            continue
        pino(qs, x + 0.5, z + 0.5, r.uniform(6, 11), semilla + k)
    for k in range(5):                                                                    # las rocas
        a = lejos + r.uniform(-1.3, 1.3)
        rr = r.uniform(18, 34)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if libre(x, z):
            continue
        roca(qs, x, z, r.uniform(3, 7), r.uniform(3, 6), semilla + k)
    for k in range(9):                                                                    # las montanas
        a = lejos + r.uniform(-1.5, 1.5)
        rr = r.uniform(90, 130)
        roca(qs, math.cos(a) * rr, math.sin(a) * rr, r.uniform(40, 70), r.uniform(40, 60), k, nieve=True)
    if nido is not None:
        x, z, alto = nido
        roca(qs, x, z, alto, 7.0, 3)
        for k in range(14):                                                               # el nido, de palos
            g = k / 14 * TAU
            bm.cubo(qs, vr.T(x, alto + 0.2, z) @ vr.Ry(g), -1.8, 0.0, 1.0, 3.6, 0.5, 0.4, p_palo, semilla=k)
            bm.cubo(qs, vr.T(x, alto + 0.6, z) @ vr.Ry(g + 0.2), -1.6, 0.0, 1.2, 3.2, 0.4, 0.4, p_palo, semilla=k + 1)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S, sol_x=0.18):
    """El atardecer con el resplandor del sol a la izquierda y nubes largas encendidas por debajo (en el de Tormenta,
    nubes oscuras y bajas)."""
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.55, arriba + (medio - arriba) * (k / 0.55), medio + (abajo - medio) * ((k - 0.55) / 0.45))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W * sol_x) / W, (yy - horizonte) / H * 1.6)
    col += np.array(S['sol'])[None, None, :] * (np.exp(-(d / 0.22) ** 2) * 0.45)[..., None]
    r = random.Random(11)
    for _ in range(12):
        cy = r.uniform(0.1, 0.7) * horizonte
        cx, L, g = r.uniform(-0.1, 1.0) * W, r.uniform(0.15, 0.45) * W, max(2, int(r.uniform(0.008, 0.02) * H))
        luz = np.array(S['sol']) * (0.55 + 0.35 * cy / max(horizonte, 1))
        sombra = np.array(S['cielo'][1]) * 0.8
        y0, y1 = int(cy), int(cy + g)
        x0, x1 = int(max(0, cx)), int(min(W, cx + L))
        if x1 > x0 and y1 > y0:
            col[y0:y1, x0:x1] = sombra
            col[y1 - 1:y1 + max(1, g // 3), x0 + 2:x1 - 2] = luz
    return np.clip(col, 0, 1)


def motas(img, n, semilla, color):
    """Las motas de polen y polvo del atardecer."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(H * 0.2, H)
        g = max(1, int(r.choice((1, 2)) * W / 1600))
        d.rectangle((x, y, x + g, y + g), fill=(*color, r.randint(90, 180)))
    glow = capa.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)


def revelar(lz, cam, W, H, S, n_motas=60, semilla=3, fuerza_vineta=0.3, brillo=0.9):
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


def modelo(cual, alto=VUELO):
    clave = (cual, alto)
    if clave not in MODELOS:
        qs, info = iz.izador(cual)
        qs = qm.transformar(qs, vr.T(0.0, alto, 0.0))
        for c in ('cabeza', 'nucleo', 'jaula'):
            info[c] = np.asarray(info[c]) + np.array((0.0, alto, 0.0))
        info['luces'] = [np.asarray(p) + np.array((0.0, alto, 0.0)) for p in info['luces']]
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[clave] = (qs, info, P)
    return MODELOS[clave]


ARRIBA = {'bi': {'rot': (168, 0, 12)}, 'bd': {'rot': (160, 0, -18)}, 'cabeza': {'rot': (-20, 0, 0)}}


def jugador_en_jaula(info, giro=200.0):
    """El jugador dentro de la jaula, con los brazos arriba, agarrado a las costillas."""
    j = info['jaula']
    return nm.quads(ne.jugador(), ARRIBA, vr.T(j[0], j[1] + 0.05, j[2] - 0.05) @ ne.jugador_a_mundo(0.0, 0.0, giro))


def rayo(qs, de, a, semilla=1):
    """Un rayo en zigzag de 'de' a 'a', de cajas finas que brillan."""
    r = random.Random(semilla)
    de, a = np.asarray(de, float), np.asarray(a, float)
    pts = [de]
    n = 9
    for k in range(1, n):
        p = de + (a - de) * k / n + np.array((r.uniform(-1.2, 1.2), 0.0, r.uniform(-0.8, 0.8)))
        pts.append(p)
    pts.append(a)
    for p, q in zip(pts[:-1], pts[1:]):
        bm.viga(qs, p, q, 0.22, 0.22, p_rayo, semilla=semilla)


def camara(cual, vista, alto=VUELO):
    qs, info, P = modelo(cual, alto)
    lo, hi = P.min(axis=0), P.max(axis=0)
    medio = (lo + hi) / 2
    tam = max(hi[1] - lo[1], (hi[0] - lo[0]) * 0.8)
    c = np.asarray(info['cabeza'], float)
    if vista == 'heroe':
        obj = np.array((0.0, medio[1] - 0.2, 0.0))
        ojo = obj + np.array((0.45, 0.0, 0.9)) * tam * 1.05
        ojo[1] = 2.2
        return tuple(ojo), tuple(obj), 52
    if vista == 'cabeza':
        ojo = c + np.array((0.6, -1.0, 2.4))
        return tuple(ojo), tuple(c + np.array((0.0, 0.1, -0.5))), 54
    # la accion: a su altura y un poco por encima, para que se vea el suelo muy abajo y el jugador en la jaula
    j = np.asarray(info['jaula'], float)
    obj = np.array((0.0, j[1] + 2.4, 0.0))
    ojo = obj + np.array((1.0, 0.28, 0.3)) * tam * 1.0
    return tuple(ojo), tuple(obj), 60


def escena(cual, vista, n_motas, brillo=0.9, alto=VUELO, extra=None, nido=None):
    """Una foto: las cumbres; el Izador, con la luz de su corazon y de su boca; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista, alto)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    qs, info, P = modelo(cual, alto)
    lo, hi = P.min(axis=0), P.max(axis=0)
    suelo(lz, cam, niebla, S)
    bioma(lz, cam, niebla, S, libre=lambda x, z: lo[0] - 4 < x < hi[0] + 4 and lo[2] - 4 < z < hi[2] + 4
          or math.hypot(x - ojo[0], z - ojo[2]) < 6, nido=nido)
    neo = _c(info['luz'])
    luces = S['luces'] + [(tuple(p) + (2.5,), neo, 0.9, 'punto') for p in info['luces'][:2]]
    z0 = lz.z.copy()
    iz.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    if extra:
        extra(lz, cam, info, luces, S, niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe', 50), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 25), 'cabeza_' + cual)


def accion(cual):
    """Lo que hace: muy alto, con un jugador dentro de la jaula. El de Tormenta, con el rayo que cae en la jaula; el de
    Cienaga, camino de su nido, en lo alto de un pilar de roca."""
    alto = 16.0

    def jugador(lz, cam, info, luces, S, niebla):
        nm.dibujar(lz, cam, jugador_en_jaula(info), luces, S['amb'], niebla)
        if cual == 'B':
            qs = []
            j = info['jaula']
            rayo(qs, (j[0] + 2.0, j[1] + 22.0, j[2] - 3.0), (j[0], j[1] + 2.6, j[2] - 0.1), semilla=3)
            qm.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    nido = (-9.0, -12.0, 9.0) if cual == 'C' else None
    guardar(escena(cual, 'accion', 40, brillo=1.1, alto=alto, extra=jugador, nido=nido), 'accion_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos, flotando bajo, con un jugador en el suelo."""
    W, H = int(1800 * K), int(900 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 60, 160)
    cam = vr.Camara((0.0, 3.0, 26.0), (0.0, 4.4, 0.0), 34, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    bioma(lz, cam, niebla, S, semilla=8, libre=lambda x, z: abs(x) < 18 and -6 < z < 30)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -8.5), ('B', 0.5), ('C', 9.5)):
        qs, info, P = modelo(cual, 1.6)
        qs = qm.transformar(qs, vr.T(x, 0, 0))
        z0 = lz.z.copy()
        iz.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-4.0, 3.0, 180)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=40), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo, con el saco (abajo y arriba), el hueso, la piel, la boca
    y el corazon."""
    W = 1240
    filas = []
    for c in 'ABC':
        P = iz.pintores(iz.VARIANTES[c])
        filas.append([(P['saco1'], 'frente', 18, 8), (P['saco6'], 'frente', 18, 8), (P['hueso'], 'der', 2, 12),
                      (P['piel'], 'frente', 10, 7), (P['boca'], 'abajo', 10, 13), (P['nucleo'], 'frente', 4, 4)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (22, 20, 24))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (44, 40, 46, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 192
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(72, 66, 76))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'accion_' + c: (lambda c=c: accion(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})
PRUEBAS = {}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        (ESCENAS.get(k) or PRUEBAS[k])()

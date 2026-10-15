"""
Renders del Oni (15-10-2026): sus tres tipos en un santuario de noche (la grava, el torii bermellon detras, los
faroles de piedra encendidos, los arces rojos y los montes), con la luna y las hojas rojas que caen; su cartel (de
cerca y desde abajo); la cara (de cerca, para mirar dentro de la boca); los tres juntos con un jugador; y la lamina de
materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python oni_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import eclipse_modelo as em
import oni_modelo as am

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


# la noche de cada tipo: (cielo arriba, en medio, en el horizonte), niebla, ambiente, luna
NOCHE = {
    'A': (((0.02, 0.02, 0.05), (0.12, 0.06, 0.1), (0.36, 0.14, 0.12)), (0.14, 0.07, 0.08), (0.22, 0.2, 0.26), (0.9, 0.86, 0.96)),
    'B': (((0.01, 0.02, 0.06), (0.04, 0.1, 0.2), (0.1, 0.24, 0.36)), (0.05, 0.1, 0.16), (0.2, 0.22, 0.28), (0.8, 0.9, 1.0)),
    'C': (((0.02, 0.01, 0.03), (0.1, 0.03, 0.06), (0.3, 0.06, 0.1)), (0.12, 0.04, 0.06), (0.2, 0.18, 0.24), (0.92, 0.84, 0.9)),
}


def sitio(v):
    """El mismo santuario para los tres, de noche: la luna, detras a la izquierda, y la luz calida de los faroles."""
    cielo, niebla, amb, luna = NOCHE[v]
    return dict(
        luces=[((-0.5, 0.75, 0.45), luna, 0.75, 'llave'), ((-0.5, 0.4, -1.0), luna, 1.1, 'contra'),
               ((0.7, 0.2, 0.7), (1.0, 0.6, 0.3), 0.45, 'llave')],
        amb=amb, niebla=niebla, niebla_d=(80, 280), cielo=cielo, sol=luna, motas=(240, 70, 40),
    )


# ----------------------------------------------------------------------
#  El santuario: la grava, el camino de losas, el torii, los faroles de piedra, los arces y los montes
# ----------------------------------------------------------------------
GRAVA = _r('2a2a2c', '343436', '403f40', '4c4a4a', '5a5856')
qm._reg('grava_oni', qm._suelo_grande(733, GRAVA, (110, 106, 100), grietas=False))


def p_piedra(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = sm._manchas(tw, th, s, celda=6.0, umbral=0.62, alto=0.88)
    idx = np.array([2, 2, 2, 3, 3])[idx]
    return bm._imagen(sm._bisel(idx, 1, 1), _r('201e1c', '2e2c28', '3e3a34', '504a42', '645c52')), None


def p_bermellon(tw, th, cara, s):
    """La laca bermellon del torii, con el bisel."""
    return bm._imagen(sm._bisel(np.full((th, tw), 2), 1, 1), _r('3a0604', '6a0e08', '9a1a0e', 'c42c16', 'e04a26')), None


def p_negro(tw, th, cara, s):
    return bm._imagen(sm._bisel(np.full((th, tw), 2), 1, 1), _r('060606', '0e0e0e', '181818', '242424', '303030')), None


def p_farol(tw, th, cara, s):
    """La ventana del farol de piedra, encendida."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (255, 170, 70, 255)
    t[(abs(xs - (tw - 1) / 2) < tw * 0.18) | (abs(ys - (th - 1) / 2) < th * 0.18)] = (255, 230, 160, 255)
    return t, None


def p_corteza(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    a = ys if th >= tw else xs
    idx = np.where(a % 5 == 0, 1, 2)
    return bm._imagen(sm._bisel(idx, 1, 1), _r('120c0a', '1e1612', '2c201a', '3c2c22', '4e3a2c')), None


def p_arce(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=4.0, umbral=0.5, alto=0.8)
    return bm._imagen(np.array([1, 2, 2, 3, 4])[idx], _r('3a0604', '640c06', '901a0a', 'bc3012', 'e0541e')), None


def p_monte(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=12.0, umbral=0.6, alto=0.85)
    return bm._imagen(np.array([1, 1, 2, 2, 3])[idx], _r('08080c', '0c0c12', '101018', '14141e', '181824')), None


for _f in (p_piedra, p_bermellon, p_negro, p_farol, p_corteza, p_arce, p_monte):
    _f.__name__ = 'oniE_' + _f.__name__
bm.PLENOS.add(p_farol)


def suelo(lz, cam, niebla, S, ext=300, paso=32, cerca=56, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'grava_oni'))

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


def torii(qs, x, z, ancho, alto, giro=0.0):
    """El torii: dos pilares bermellon con su base negra, el travesano de abajo y el de arriba, curvo y negro."""
    M = vr.T(x, 0.0, z) @ vr.Ry(giro)
    for s in (-1, 1):
        bm.cubo(qs, M, s * ancho / 2 - 1.6, 0.0, -1.6, 3.2, 2.4, 3.2, p_negro, semilla=1)
        bm.cubo(qs, M, s * ancho / 2 - 1.2, 2.4, -1.2, 2.4, alto - 2.4, 2.4, p_bermellon, semilla=2)
    bm.cubo(qs, M, -ancho / 2 - 3.0, alto * 0.78, -0.9, ancho + 6.0, 1.8, 1.8, p_bermellon, semilla=3)
    bm.cubo(qs, M, -ancho / 2 - 5.0, alto, -1.6, ancho + 10.0, 2.0, 3.2, p_bermellon, semilla=4)
    for s in (-1, 1):                                                   # las puntas del travesano, que suben
        bm.cubo(qs, M @ vr.T(s * (ancho / 2 + 5.0), alto + 2.0, 0.0) @ vr.Rz(s * 0.25), -3.0 if s > 0 else 0.0, -1.0, -1.8,
                3.0, 2.0, 3.6, p_negro, semilla=5)
    bm.cubo(qs, M, -ancho / 2 - 5.4, alto + 2.0, -1.8, ancho + 10.8, 1.4, 3.6, p_negro, semilla=6)


def farol(qs, x, z):
    """Un farol de piedra (toro): la base, el fuste, la caja de luz, el tejadillo y su remate."""
    M = vr.T(x, 0.0, z)
    bm.cubo(qs, M, -1.6, 0.0, -1.6, 3.2, 0.8, 3.2, p_piedra, semilla=1)
    bm.cubo(qs, M, -0.7, 0.8, -0.7, 1.4, 3.6, 1.4, p_piedra, semilla=2)
    bm.cubo(qs, M, -1.5, 4.4, -1.5, 3.0, 0.6, 3.0, p_piedra, semilla=3)
    bm.cubo(qs, M, -1.1, 5.0, -1.1, 2.2, 2.0, 2.2, p_farol, semilla=1)
    bm.cubo(qs, M, -2.0, 7.0, -2.0, 4.0, 0.8, 4.0, p_piedra, semilla=4)
    bm.cubo(qs, M, -1.0, 7.8, -1.0, 2.0, 0.8, 2.0, p_piedra, semilla=5)


def arce(qs, x, z, alto, semilla):
    """Un arce rojo: el tronco torcido y las copas en racimos."""
    rng = random.Random(semilla)
    M = vr.T(x, 0.0, z)
    bm.cubo(qs, M, -0.8, 0.0, -0.8, 1.6, alto, 1.6, p_corteza, semilla=semilla)
    for j in range(5):
        w = rng.uniform(5.0, 9.0)
        bm.cubo(qs, M @ vr.T(rng.uniform(-4, 4), alto - 1.0 + rng.uniform(-1.5, 3.0), rng.uniform(-4, 4)), -w / 2, 0.0, -w / 2, w,
                rng.uniform(2.4, 3.6), w, p_arce, semilla=j)


def santuario(lz, cam, niebla, S, semilla=4, libre=None):
    """El torii detras, los faroles de piedra a los lados del camino, los arces y los montes (sin nada entre la camara y
    el jefe)."""
    r = random.Random(semilla)
    qs = []
    torii(qs, 0.0, -40.0, 40.0, 30.0)
    torii(qs, 0.0, -90.0, 40.0, 30.0)
    hc = math.atan2(cam.ojo[2], cam.ojo[0])
    for z in (-14.0, 6.0, 26.0, -60.0):
        for s in (-1, 1):
            x = s * 28.0
            if libre is not None and libre(x, z):
                continue
            if math.hypot(x, z) > 20 and abs(((math.atan2(z, x) - hc + math.pi) % TAU) - math.pi) < 0.35:
                continue
            farol(qs, x, z)
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    for k in range(18):
        a = r.uniform(0, TAU)
        rr = r.uniform(42, 110)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if libre is not None and libre(x, z):
            continue
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.75:
            continue
        if abs(x) < 26 and z < 0:
            continue
        arce(qs, x, z, r.uniform(8, 14), k)
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    lejos = hacia_camara + math.pi
    for k in range(10):
        a = lejos + r.uniform(-1.3, 1.3)
        rr = r.uniform(220, 300)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w, alto = r.uniform(70, 120), r.uniform(40, 90)
        for j in range(7):
            f = 1.0 - j / 7 * 0.85
            bm.cubo(qs, vr.T(x, 0, z) @ vr.Ry(k), -w * f / 2, 0, -w * f / 2, w * f, alto * (j + 1) / 7, w * f, p_monte,
                    semilla=k + j)
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
    """Las hojas rojas de los arces, que caen, con un poco de halo."""
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
        qs, info = am.oni(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras: 'heroe' (de cuerpo entero, de tres cuartos y desde abajo), 'cabeza' (de cerca y un poco por debajo,
    para mirar dentro del arco de la boca) y 'cartel' (de cerca y muy desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    b = np.asarray(info['boca'], float)
    if vista == 'heroe':
        d = max(h, hi[0] - lo[0]) * 0.5 / math.tan(25 * D) * 1.35
        obj = np.array((0.0, h * 0.46, 2.0))
        v = np.array((0.5, 0.0, 0.87))
        ojo = obj + v * d
        ojo[1] = 2.4
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        ojo = b + np.array((6.0, -3.6, 15.0))
        ojo[1] = max(ojo[1], 1.6)
        return tuple(ojo), tuple(b + np.array((0.0, 1.6, -2.0))), 56
    obj = np.array((0.0, h * 0.6, 3.0))
    ojo = obj + np.array((0.45, 0.0, 0.89)) * h * 1.15
    ojo[1] = 1.6
    return tuple(ojo), tuple(obj), 64


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: el santuario; el Oni, con la luz de su boca y de sus ojos; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    suelo(lz, cam, niebla, S)
    santuario(lz, cam, niebla, S, libre=lambda x, z: lo[0] - 4 < x < hi[0] + 4 and lo[2] - 4 < z < hi[2] + 4
              or abs(x - ojo[0]) < 8 and abs(z - ojo[2]) < 8)
    neo = _c(am.VARIANTES[cual]['neon'][1])
    luces = S['luces'] + [(tuple(p) + (9.0,), neo, 1.1, 'punto') for p in info['luces'][:2]]
    z0 = lz.z.copy()
    am.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe', 60), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 30), 'cabeza_' + cual)


def cartel(cual):
    """La presentacion del cartel: de cerca y desde abajo, con el cielo de su noche."""
    guardar(escena(cual, 'cartel', 40, brillo=1.2), 'cartel_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos, con la misma luz y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 200, 420)
    cam = vr.Camara((0.0, 8.0, 185.0), (0.0, 16.0, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=340, paso=32, cerca=40)
    santuario(lz, cam, niebla, S, semilla=8, libre=lambda x, z: abs(x) < 60 and -20 < z < 60 or z > 60)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -34.0), ('B', 0.0), ('C', 34.0)):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(14.0, 26.0, 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo y, de izquierda a derecha, la piel, el pecho, la nariz, el
    ojo, el paladar, la garganta, los dientes, el mechon de la melena, el cuerno, el colmillo, la piel de tigre, la cuerda
    sagrada, el papel en zigzag y el hierro."""
    W = 2760
    filas = []
    for c in formas:
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['piel'], 'frente', 36, 36), (P['musculo'], 'frente', 30, 30), (P['nariz'], 'frente', 22, 16),
                      (P['ojo_d'], 'frente', 24, 14), (P['paladar'], 'abajo', 30, 30), (P['garganta'], 'frente', 30, 20),
                      (P['dientes_arriba'], 'frente', 30, 9), (P['mechon'], 'frente', 18, 48), (P['cuerno'], 'der', 30, 8),
                      (P['colmillo'], 'der', 24, 6), (P['tigre'], 'frente', 36, 24), (P['cuerda'], 'frente', 36, 9),
                      (P['shide'], 'frente', 8, 24), (P['hierro'], 'frente', 24, 24)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (22, 20, 24))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (46, 42, 50, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 192
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(76, 70, 84))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})
PRUEBAS = {}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        (ESCENAS.get(k) or PRUEBAS[k])()

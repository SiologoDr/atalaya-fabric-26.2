"""
Renders del Ciclope (15-10-2026): sus tres tipos en la costa de Sicilia al atardecer (el cabo de roca donde esta de pie,
el acantilado, el mar, el Etna humeando al fondo y el barco de Ulises, pequeno, en el agua); su cartel (de cerca y desde
abajo, con el cielo de cada uno: oro para Polifemo, fragua para Brontes y tormenta para Arges); la cabeza (de cerca,
para mirarle el ojo y la boca); los tres juntos con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python ciclope_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import ciclope_modelo as am

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


# el cielo de cada tipo: (arriba, en medio, en el horizonte), niebla, ambiente, sol
CIELO = {
    'A': (((0.14, 0.12, 0.26), (0.66, 0.42, 0.34), (1.0, 0.74, 0.4)), (0.6, 0.46, 0.4), (0.3, 0.27, 0.32), (1.0, 0.78, 0.5)),
    'B': (((0.16, 0.06, 0.08), (0.6, 0.2, 0.12), (1.0, 0.5, 0.2)), (0.5, 0.26, 0.2), (0.3, 0.22, 0.24), (1.0, 0.6, 0.36)),
    'C': (((0.06, 0.08, 0.14), (0.22, 0.28, 0.4), (0.52, 0.6, 0.72)), (0.3, 0.34, 0.42), (0.26, 0.28, 0.34), (0.82, 0.88, 1.0)),
}


def sitio(v):
    """La misma costa para los tres; el sol se pone detras, a la izquierda."""
    cielo, niebla, amb, sol = CIELO[v]
    return dict(
        luces=[((-0.6, 0.45, 0.65), sol, 1.0, 'llave'), ((-0.5, 0.3, -1.0), sol, 1.1, 'contra'),
               ((0.7, 0.4, 0.5), (0.42, 0.46, 0.64), 0.3, 'llave')],
        amb=amb, niebla=niebla, niebla_d=(110, 420), cielo=cielo, sol=sol, motas=(255, 220, 170),
    )


# ----------------------------------------------------------------------
#  La costa: la roca del cabo, el acantilado, el mar, el Etna y el barco
# ----------------------------------------------------------------------
COSTA = _r('2a2622', '3c3630', '50483e', '665c4e', '7e7260')
qm._reg('costa_cic', qm._suelo_grande(611, COSTA, None, grietas=True))
MAR = _r('123444', '1a4a5e', '24607a', '347a94', '5a9cb2')


def _mar():
    """El mar: azul hondo con las crestas de las olas en rayas largas y claras."""
    n = 128
    rng = random.Random(23)
    t = np.zeros((n, n, 4), np.uint8)
    t[...] = (*MAR[1], 255)
    for _ in range(170):
        y, x, L = rng.randrange(n), rng.randrange(n), rng.randint(5, 22)
        c = MAR[rng.choice((2, 2, 3, 3, 4))]
        for k in range(L):
            t[y, (x + k) % n] = (*c, 255)
    return t


qm._reg('mar_cic', _mar())


def p_roca(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=7.0, umbral=0.6, alto=0.85)
    if cara == 'arriba':
        return bm._imagen(np.clip(idx, 1, 3), _r('2e2a24', '403a32', '544c42', '6a6052', '827664')), None
    return bm._imagen(sm._bisel(np.array([1, 2, 2, 3, 3])[idx]), _r('1a1816', '28241f', '38332c', '4a443a', '5e574a')), None


def p_lava(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (255, 120, 30, 255)
    t[(xs + ys) % 3 == 0] = (255, 200, 90, 255)
    return t, None


def p_humo(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=6.0, umbral=0.55, alto=0.85)
    return bm._imagen(np.array([1, 2, 2, 3, 3])[idx], _r('2a2628', '3a3638', '4c4648', '5e585a', '726a6c')), None


def p_volcan(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=12.0, umbral=0.6, alto=0.85)
    return bm._imagen(np.array([1, 1, 2, 2, 3])[idx], _r('12100e', '1a1714', '221e1a', '2c2721', '36302a')), None


def p_casco(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(ys % 3 == 0, 1, 2)
    return bm._imagen(idx, _r('140c08', '22140c', '341e12', '48301c', '604028')), None


def p_vela(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(abs(ys - th / 2) < th / 8, 1, 3)
    return bm._imagen(idx, _r('5a1a12', '8a2a1a', 'c8b89a', 'e4d8bc', 'f6eedc')), None


for _f in (p_roca, p_lava, p_humo, p_volcan, p_casco, p_vela):
    _f.__name__ = 'cicE_' + _f.__name__
bm.PLENOS.add(p_lava)

COSTA_Z = -26.0                 # donde acaba el cabo y empieza el acantilado
MAR_Y = -9.0


def suelo(lz, cam, niebla, S, ext=420, paso=32, cerca=60, paso_cerca=8):
    """La roca del cabo (delante) y el mar, mas abajo (detras y a los lados)."""
    qs = []

    def baldosa(gx, gz, p, y, mat, k):
        P = [(gx + p, y, gz), (gx, y, gz), (gx, y, gz + p), (gx + p, y, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], mat))

    cx, cz = cam.ojo[0], cam.ojo[2]
    for gx in range(-ext, ext, paso):
        for gz in range(-ext, ext, paso):
            fino = abs(gx + paso / 2 - cx) < cerca and abs(gz + paso / 2 - cz) < cerca
            pasos = [(a, b, paso_cerca) for a in range(gx, gx + paso, paso_cerca) for b in range(gz, gz + paso, paso_cerca)] \
                if fino else [(gx, gz, paso)]
            for a, b, p in pasos:
                if b + p > COSTA_Z and abs(a + p / 2) < 70:
                    baldosa(a, b, p, 0.0, 'costa_cic', p / 4)
                else:
                    baldosa(a, b, p, MAR_Y, 'mar_cic', p / 4)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def costa(lz, cam, niebla, S, semilla=4, libre=None):
    """El acantilado del cabo, las rocas sueltas, el Etna con su humo y el barco de Ulises."""
    r = random.Random(semilla)
    qs = []
    for k in range(30):                                                 # el canto del acantilado
        x = -70 + k * 4.8 + r.uniform(-1, 1)
        h = r.uniform(7.0, 12.0)
        M = vr.T(x, MAR_Y - 1.0, COSTA_Z + r.uniform(-2.0, 1.0)) @ vr.Ry(r.uniform(-0.3, 0.3))
        bm.cubo(qs, M, -3.2, 0.0, -3.0, 6.4, h, 4.0, p_roca, semilla=k)
    for k in range(28):                                                 # las rocas del cabo
        x, z = r.uniform(-65, 65), r.uniform(COSTA_Z + 2, 70)
        if libre is not None and libre(x, z):
            continue
        w, h = r.uniform(1.5, 4.5), r.uniform(0.8, 3.0)
        M = vr.T(x, -0.2, z) @ vr.Ry(r.uniform(0, 3))
        bm.cubo(qs, M, -w / 2, 0.0, -w / 2, w, h, w * 0.8, p_roca, semilla=k + 40)
    for k in range(6):                                                  # escollos en el mar
        x, z = r.uniform(-120, 120), r.uniform(-140, -50)
        w, h = r.uniform(3, 8), r.uniform(4, 10)
        bm.cubo(qs, vr.T(x, MAR_Y - 1, z) @ vr.Ry(r.uniform(0, 3)), -w / 2, 0.0, -w / 2, w, h, w, p_roca, semilla=k + 80)
    ex, ez = -180.0, -420.0                                             # el Etna
    n = 40
    for j in range(n):                                                  # en capas finas, que hacen un cono
        f = 1.0 - j / n * 0.9
        w = 260 * f
        for g in (0.0, 0.785):
            bm.cubo(qs, vr.T(ex, MAR_Y + j * 2.7, ez) @ vr.Ry(0.3 + g), -w / 2, 0.0, -w / 2, w, 2.8, w, p_volcan, semilla=j % 5)
    bm.cubo(qs, vr.T(ex, MAR_Y + 108.0, ez) @ vr.Ry(0.3), -10.0, 0.0, -8.0, 20.0, 1.5, 16.0, p_lava, semilla=1)
    for j in range(12):                                                 # el humo, que se va con el viento
        y = MAR_Y + 112.0 + j * 9.0
        w = 14.0 + j * 4.0
        bm.cubo(qs, vr.T(ex + j * 9.0, y, ez + j * 2.0) @ vr.Ry(j * 0.4), -w / 2, 0.0, -w / 2, w, 9.0, w * 0.7, p_humo, semilla=j)
    bx, bz = 46.0, -80.0                                                # el barco de Ulises
    M = vr.T(bx, MAR_Y, bz) @ vr.Ry(0.5)
    bm.cubo(qs, M, -1.6, 0.0, -9.0, 3.2, 1.8, 18.0, p_casco, semilla=1)
    bm.cubo(qs, M, -1.0, 1.6, 8.4, 2.0, 1.6, 2.0, p_casco, semilla=2)
    bm.cubo(qs, M, -0.2, 1.8, -0.2, 0.4, 11.0, 0.4, p_casco, semilla=3)
    bm.cubo(qs, M, -4.5, 6.0, -0.4, 9.0, 6.0, 0.2, p_vela, semilla=4)
    for k in range(7):
        Mr = M @ vr.T(1.6, 0.8, -6.0 + k * 2.0) @ vr.Rz(-0.6)
        bm.cubo(qs, Mr, 0.0, -0.1, -0.1, 4.0, 0.2, 0.2, p_casco, semilla=5)
        Mr = M @ vr.T(-1.6, 0.8, -6.0 + k * 2.0) @ vr.Rz(math.pi + 0.6)
        bm.cubo(qs, Mr, 0.0, -0.1, -0.1, 4.0, 0.2, 0.2, p_casco, semilla=5)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S, sol_x=0.2):
    """El cielo de la tarde: el color de arriba, el del medio y el del horizonte, el resplandor del sol a la izquierda y
    unas nubes largas, encendidas por debajo."""
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.55, arriba + (medio - arriba) * (k / 0.55), medio + (abajo - medio) * ((k - 0.55) / 0.45))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W * sol_x) / W, (yy - horizonte) / H * 1.6)
    col += np.array(S['sol'])[None, None, :] * (np.exp(-(d / 0.22) ** 2) * 0.45)[..., None]
    r = random.Random(13)
    for _ in range(10):
        cy = r.uniform(0.12, 0.6) * horizonte
        cx, L, g = r.uniform(-0.1, 1.0) * W, r.uniform(0.12, 0.42) * W, max(2, int(r.uniform(0.007, 0.016) * H))
        luz = np.array(S['sol']) * (0.55 + 0.35 * cy / max(horizonte, 1))
        sombra = np.array(S['cielo'][1]) * 0.8
        y0, y1 = int(cy), int(cy + g)
        x0, x1 = int(max(0, cx)), int(min(W, cx + L))
        if x1 > x0 and y1 > y0:
            col[y0:y1, x0:x1] = sombra
            col[y1 - 1:y1 + max(1, g // 3), x0 + 2:x1 - 2] = luz
    return np.clip(col, 0, 1)


def motas(img, n, semilla, color):
    """El polvo y la sal que levanta el viento, calidos con el sol."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(H * 0.2, H)
        g = max(1, int(r.choice((1, 1, 2)) * W / 1600))
        d.rectangle((x, y, x + g, y + g), fill=(*color, r.randint(110, 200)))
    glow = capa.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)


def revelar(lz, cam, W, H, S, n_motas=60, semilla=3, fuerza_vineta=0.35, brillo=0.9):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, MAR_Y, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
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
        qs, info = am.ciclope(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras: 'heroe' (de cuerpo entero, de tres cuartos y desde abajo), 'cabeza' (de cerca, un poco por debajo
    para mirarle el ojo y la boca) y 'cartel' (de cerca y muy desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    o = np.asarray(info['ojo'], float)
    if vista == 'heroe':
        d = h * 0.5 / math.tan(25 * D) * 1.25
        obj = np.array((0.0, h * 0.5, 0.0))
        v = _u3((0.45, 0.0, 0.89))
        ojo = obj + v * d
        ojo[1] = 3.0
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        ojo = o + np.array((7.0, -5.0, 15.0))
        return tuple(ojo), tuple(o + np.array((0.0, -1.5, 0.0))), 52
    obj = np.array((0.0, h * 0.62, 2.0))
    ojo = obj + _u3((0.5, 0.0, 0.86)) * h * 0.95
    ojo[1] = 2.0
    return tuple(ojo), tuple(obj), 66


def _u3(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: la costa; el Ciclope, con la luz de su ojo y de su boca; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    costa(lz, cam, niebla, S, libre=lambda x, z: abs(x) < 16 and abs(z) < 14 or abs(x - ojo[0]) < 8 and abs(z - ojo[2]) < 8)
    qs, info, P = modelo(cual)
    neo = _c(am.VARIANTES[cual]['neon'][1])
    luces = S['luces'] + [(tuple(p) + (9.0,), neo, 0.9, 'punto') for p in info['luces'][:2]]
    z0 = lz.z.copy()
    am.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe', 60), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 30), 'cabeza_' + cual)


def cartel(cual):
    """La presentacion del cartel: de cerca y muy desde abajo, con el cielo de su tipo."""
    guardar(escena(cual, 'cartel', 40, brillo=1.2), 'cartel_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos, con la misma luz y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 220, 480)
    cam = vr.Camara((0.0, 12.0, 190.0), (0.0, 13.0, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=420, paso=32, cerca=40)
    costa(lz, cam, niebla, S, semilla=8, libre=lambda x, z: abs(x) < 60 and -16 < z < 45)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -34.0), ('B', 0.0), ('C', 34.0)):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(-12 * D if x > 0 else 12 * D if x < 0 else 0))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(16.0, 32.0, 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo y, de izquierda a derecha, la piel, el pelo, lo de encima,
    el ojo, la boca, los dientes, el colmillo, el hierro, el cuerno y la roca."""
    W = 2000
    filas = []
    for c in formas:
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['piel'], 'der', 32, 32), (P['pelo'], 'der', 24, 24), (P['ropa'], 'der', 24, 24),
                      (P['ojo'], 'frente', 20, 18), (P['boca'], 'frente', 16, 16), (P['dientes'], 'frente', 28, 8),
                      (P['colmillo'], 'frente', 6, 14), (P['hierro'], 'der', 16, 16), (P['cuerno'], 'der', 24, 6),
                      (P['roca'], 'arriba', 32, 32)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (20, 18, 22))
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
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(74, 68, 80))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

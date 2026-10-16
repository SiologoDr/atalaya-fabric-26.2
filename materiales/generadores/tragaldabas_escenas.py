"""
Renders del Tragaldabas (15-10-2026), el mob que te traga: en una cueva frondosa (el suelo de musgo, el lago, las
lianas con bayas que brillan, las estalactitas y las hojas grandes de goteo), a la escala de Minecraft; la cara (de
cerca); la foto de lo que hace, con un jugador (el de Lengua atrapandolo con la lengua, el de Cebo abriendose bajo sus
pies y el Escupidor con el jugador dentro del buche); los tres juntos con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python tragaldabas_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import tragaldabas_modelo as tm

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


def sitio(v):
    """La misma cueva para los tres: verde y humeda, con la luz calida de las bayas y un poco de luz fria de arriba."""
    return dict(
        luces=[((-0.3, 0.9, 0.4), (0.6, 0.8, 0.9), 0.55, 'llave'), ((0.5, 0.4, -1.0), (0.5, 0.75, 0.7), 0.75, 'contra'),
               ((0.7, 0.2, 0.6), (1.0, 0.65, 0.35), 0.35, 'llave')],
        amb=(0.2, 0.24, 0.22), niebla=(0.03, 0.05, 0.05), niebla_d=(8, 34), fondo=(0.015, 0.025, 0.025),
        motas=(200, 255, 190),
    )


# ----------------------------------------------------------------------
#  La cueva
# ----------------------------------------------------------------------
MUSGO = _r('14240e', '1c3214', '264218', '32541e', '406826')
ROCA = _r('1a1c1c', '262828', '323434', '404240', '504f4c')
AGUA = _r('061418', '0a1e24', '10282e', '18363a', '24484a')
HOJA = _r('14300e', '1e4414', '2c5c1c', '3c7626', '50902e')
BAYA = _r('8a3a0a', 'd06a14', 'ff9a2a', 'ffc860', 'ffeab0')


def _losa(semilla, rampa):
    rng = random.Random(semilla)
    n = 16
    idx = np.full((n, n), 2)
    for _ in range(10):
        x, y = rng.randrange(0, n, 2), rng.randrange(0, n, 2)
        idx[y:y + 2, x:x + 2] = rng.choice((1, 3, 3))
    return bm._imagen(idx, rampa)


qm._reg('musgo_tm', _losa(5, MUSGO))
qm._reg('roca_tm', _losa(9, ROCA))
qm._reg('agua_tm', _losa(3, AGUA))


def p_roca(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((((xs // 2) * 5 + (ys // 2) * 3 + s) % 7) == 0, 1, np.where((((xs // 2) * 3 + (ys // 2) * 7 + s) % 11) == 0, 3, 2))
    return bm._imagen(idx, ROCA), None


def p_hoja(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(np.abs(xs - (tw - 1) / 2) < 0.6, 4, 3)
    idx[(xs == 0) | (xs == tw - 1)] = 2
    return bm._imagen(idx, HOJA), None


def p_tallo(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where((ys % 3) == 0, 1, 2), HOJA), None


def p_baya(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    t = bm._imagen(np.where((xs + ys) % 2 == 0, 3, 2), BAYA)
    return t, None


for _n, _f in (('roca', p_roca), ('hoja', p_hoja), ('tallo', p_tallo), ('baya', p_baya)):
    _f.__name__ = 'tmE_' + _n
bm.PLENOS.add(p_baya)

ANCHO, ALTO = 9.0, 7.0


def cueva(lz, cam, niebla, S, hueco=None, libre=None, semilla=3):
    """La cueva: el suelo de musgo (con un hueco redondo en 'hueco', si se pide), el lago al fondo, las paredes y el
    techo de roca, las estalactitas, las lianas con bayas que brillan y las hojas grandes de goteo. Devuelve donde estan
    las bayas, para las luces."""
    qs = []
    r = random.Random(semilla)

    def losa(x, z, p, y, mat):
        P = [np.array(q, float) for q in ((x + p, y, z), (x, y, z), (x, y, z + p), (x + p, y, z + p))]
        qs.append((P, [(p, 0), (0, 0), (0, p), (p, p)], mat))

    for x in np.arange(-ANCHO, ANCHO, 1.0):
        for z in np.arange(-14.0, 14.0, 1.0):
            if hueco is not None and math.hypot(x + 0.5 - hueco[0], z + 0.5 - hueco[1]) < hueco[2]:
                continue
            lago = (x + 0.5 - 2.5) ** 2 / 25 + (z + 0.5 + 7.0) ** 2 / 9 < 1
            losa(x, z, 1.0, -0.2 if lago else 0.0, 'agua_tm' if lago else 'musgo_tm')
    for z in np.arange(-14.0, 14.0, 2.0):                                                  # las paredes y el techo
        for lado in (-1, 1):
            x = lado * ANCHO
            P = [np.array(q, float) for q in ((x, ALTO, z), (x, ALTO, z + 2), (x, 0.0, z + 2), (x, 0.0, z))]
            qs.append((P, [(0, 0), (2, 0), (2, ALTO), (0, ALTO)], 'roca_tm'))
        for x in np.arange(-ANCHO, ANCHO, 2.0):
            P = [np.array(q, float) for q in ((x, ALTO, z), (x + 2, ALTO, z), (x + 2, ALTO, z + 2), (x, ALTO, z + 2))]
            qs.append((P, [(0, 0), (2, 0), (2, 2), (0, 2)], 'roca_tm'))
    P = [np.array(q, float) for q in ((-ANCHO, ALTO, -14.0), (ANCHO, ALTO, -14.0), (ANCHO, 0.0, -14.0), (-ANCHO, 0.0, -14.0))]
    qs.append((P, [(0, 0), (18, 0), (18, ALTO), (0, ALTO)], 'roca_tm'))                     # el fondo
    for k in range(16):                                                                    # las estalactitas
        x, z = r.uniform(-ANCHO + 1, ANCHO - 1), r.uniform(-13.0, 6.0)
        largo = r.uniform(0.8, 2.4)
        for j in range(4):
            w = 0.7 * (1 - j / 4)
            bm.cubo(qs, vr.T(x, ALTO - largo * (j + 1) / 4, z), -w / 2, 0.0, -w / 2, w, largo / 4 + 0.01, w, p_roca,
                    semilla=k)
    bayas = []
    for k in range(14):                                                                    # las lianas con bayas
        x, z = r.uniform(-ANCHO + 1, ANCHO - 1), r.uniform(-13.0, 5.0)
        largo = r.uniform(1.5, 4.0)
        bm.cubo(qs, vr.T(x, ALTO - largo, z), -0.06, 0.0, -0.06, 0.12, largo, 0.12, p_tallo, semilla=k)
        for j in range(int(largo / 0.9)):
            y = ALTO - 0.5 - j * 0.9
            bm.cubo(qs, vr.T(x + 0.1, y, z), -0.12, -0.12, -0.12, 0.24, 0.24, 0.24, p_baya, semilla=k)
            bayas.append(np.array((x, y, z)))
    for k in range(7):                                                                     # las hojas grandes de goteo
        x, z = r.uniform(-ANCHO + 1.5, ANCHO - 1.5), r.uniform(-12.0, 4.0)
        if hueco is not None and math.hypot(x - hueco[0], z - hueco[1]) < 2.5 or libre and libre(x, z):
            continue
        alto = r.uniform(0.8, 2.2)
        bm.cubo(qs, vr.T(x, 0.0, z), -0.06, 0.0, -0.06, 0.12, alto, 0.12, p_tallo, semilla=k)
        bm.cubo(qs, vr.T(x, alto, z) @ vr.Ry(r.uniform(0, TAU)), -0.6, 0.0, -0.6, 1.2, 0.06, 1.2, p_hoja, semilla=k)
    if hueco is not None:                                                                  # el borde de tierra del hueco
        for k in range(14):
            g = k / 14 * TAU
            x, z = hueco[0] + math.cos(g) * (hueco[2] + 0.1), hueco[1] + math.sin(g) * (hueco[2] + 0.1)
            bm.cubo(qs, vr.T(x, 0.0, z) @ vr.Ry(g), -0.3, 0.0, -0.25, 0.6, r.uniform(0.15, 0.4), 0.5, p_roca, semilla=k)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
    return bayas


def luces_bayas(bayas, cam, n=3):
    cerca = sorted(bayas, key=lambda f: np.linalg.norm(f - cam.ojo))[:n]
    return [(tuple(f) + (3.0,), (1.0, 0.62, 0.3), 0.6, 'punto') for f in cerca]


def revelar(lz, cam, W, H, S, n_motas=30, semilla=3, fuerza_vineta=0.45, brillo=0.9):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    fondo = np.broadcast_to(np.array(S['fondo']), (H, W, 3))
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * brillo, radios=((2 * K, 0.5), (10 * K, 0.4), (40 * K, 0.35))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if n_motas > 0:                                                                       # las esporas que flotan
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        r = random.Random(semilla)
        for _ in range(int(n_motas * W / 1600)):
            x, y = r.uniform(0, W), r.uniform(0, H)
            g = max(1, int(W / 1600))
            d.rectangle((x, y, x + g, y + g), fill=(*S['motas'], r.randint(70, 150)))
        glow = capa.filter(ImageFilter.GaussianBlur(3))
        img = Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)
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


# ----------------------------------------------------------------------
#  Las fotos
# ----------------------------------------------------------------------
SENTADO = {'pi': {'rot': (-90, 0, -8)}, 'pd': {'rot': (-90, 0, 8)}, 'bi': {'rot': (-60, 0, -20)},
           'bd': {'rot': (-60, 0, 20)}, 'cabeza': {'rot': (20, 0, 0)}}
ARRASTRADO = {'bi': {'rot': (-100, 0, -30)}, 'bd': {'rot': (-110, 0, 25)}, 'pi': {'rot': (25, 0, 0)},
              'pd': {'rot': (-20, 0, 0)}}
CAYENDO = {'bi': {'rot': (-170, 0, -30)}, 'bd': {'rot': (-170, 0, 30)}, 'pi': {'rot': (-15, 0, -6)},
           'pd': {'rot': (10, 0, 6)}}


def jugador_accion(cual, info):
    """El jugador de la foto de accion: arrastrado por la lengua, cayendo en las fauces o sentado dentro del buche."""
    if cual == 'A':
        return nm.quads(ne.jugador(), ARRASTRADO, vr.T(0.0, 0.25, 0.0) @ ne.jugador_a_mundo(0.3, 4.2, 10) @ np.eye(4))
    if cual == 'B':
        return nm.quads(ne.jugador(), CAYENDO, vr.T(0.0, -0.55, 0.0) @ ne.jugador_a_mundo(0.0, 0.0, 200))
    b = np.asarray(info['buche'], float)
    return nm.quads(ne.jugador(), SENTADO, vr.T(b[0], b[1] - 1.2, b[2] + 0.1) @ ne.jugador_a_mundo(0.0, 0.0, 150))


def modelo(cual, accion=False):
    if not accion:
        return tm.tragaldabas(cual, abre=0.55)
    if cual == 'A':
        return tm.tragaldabas(cual, abre=0.75, lengua=(4.0, 20.0, 66.0))
    if cual == 'B':
        return tm.tragaldabas(cual, abre=0.85, enterrado=True)
    return tm.tragaldabas(cual, abre=0.04, lleno=True)


def camara(cual, vista, info):
    c = np.asarray(info['cabeza'], float)
    if vista == 'heroe':
        return (2.8, 1.4, 4.8), (0.0, 1.15, 0.3), 50
    if vista == 'cabeza':
        return tuple(c + np.array((0.9, 0.35, 2.2))), tuple(c + np.array((0.0, -0.2, 0.0))), 52
    if cual == 'A':
        return (4.6, 1.8, 3.4), (0.2, 1.1, 2.0), 52
    if cual == 'B':
        return (2.0, 2.7, 3.4), (0.0, 0.6, 0.0), 52
    return (2.3, 1.05, 3.9), (0.0, 0.85, 0.2), 50


def escena(cual, vista, n_motas=30, brillo=0.9):
    """Una foto: la cueva; el Tragaldabas (y, en la de accion, el jugador); el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    accion = vista == 'accion'
    qs, gel, info = modelo(cual, accion)
    ojo, obj, fov = camara(cual, vista, info)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    bayas = cueva(lz, cam, niebla, S, hueco=(0.0, 0.0, 1.5) if (accion and cual == 'B') else None)
    luces = S['luces'] + luces_bayas(bayas, cam) + [(tuple(info['boca']) + (2.0,), _c(info['luz']), 0.8, 'punto')]
    z0 = lz.z.copy()
    if accion:
        nm.dibujar(lz, cam, jugador_accion(cual, info), luces, S['amb'], niebla)
    tm.dibujar(lz, cam, qs, gel, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe'), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 15), 'cabeza_' + cual)


def accion(cual):
    guardar(escena(cual, 'accion', 25, brillo=1.0), 'accion_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos en la cueva, con un jugador de pie al lado."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 10, 40)
    cam = vr.Camara((0.0, 2.2, 13.0), (0.0, 1.2, 0.0), 40, W * SS, H * SS)
    bayas = cueva(lz, cam, niebla, S, libre=lambda x, z: abs(x) < 8.5 and -4 < z < 12)
    luces = S['luces'] + luces_bayas(bayas, cam, 4)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -4.2), ('B', 0.4), ('C', 5.0)):
        qs, gel, info = tm.tragaldabas(cual, abre=0.55)
        M = vr.T(x, 0, 0) @ vr.Ry(-0.25)
        qs, gel = qm.transformar(qs, M), qm.transformar(gel, M)
        z0 = lz.z.copy()
        tm.dibujar(lz, cam, qs, gel, luces, S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-7.4, 0.8, 180)), luces, S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=30), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo, con la piel, el vientre, el buche, la boca, el ojo y el
    diente."""
    W = 1240
    filas = []
    for c in 'ABC':
        P = tm.pintores(tm.VARIANTES[c])
        filas.append([(P['piel'], 'frente', 16, 12), (P['vientre'], 'frente', 12, 8), (P['buche'], 'frente', 14, 12),
                      (P['boca'], 'abajo', 12, 12), (P['ojo'], 'frente', 6, 4), (P['diente'], 'frente', 2, 4)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (16, 20, 20))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (38, 44, 44, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 192
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(62, 72, 70))
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

"""
Renders del Fogonazo (16-10-2026), el mob-luciernaga que estalla como un creeper y te deja la pantalla en blanco: en un campo de noche (la
hierba alta, las flores, la cerca de madera, los robles y los montes a lo lejos, la luna cuadrada), donde su luz es lo
unico que alumbra; la cara (de cerca); la foto de lo que hace (estallando delante de un jugador que se tapa los ojos);
lo que ve el jugador (el bicho que se abre, la pantalla en blanco y como se va); los tres juntos con un jugador; y la
lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python fogonazo_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import fogonazo_modelo as fg

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
TAU = math.tau
_r = bm._r


def _c(h):
    return tuple(c / 255 for c in nm._hex(h))


def sitio():
    """El campo de noche: la luna detras a la izquierda, la luz fria y poca; lo que alumbra de verdad es el bicho."""
    luna = (0.66, 0.78, 1.0)
    return dict(
        luces=[((-0.5, 0.75, 0.4), luna, 0.6, 'llave'), ((-0.45, 0.5, -1.0), luna, 0.9, 'contra')],
        amb=(0.16, 0.19, 0.26), niebla=(0.025, 0.035, 0.06), niebla_d=(12, 60),
        cielo=((0.008, 0.012, 0.03), (0.02, 0.035, 0.08), (0.06, 0.09, 0.16)), luna=luna,
    )


# ----------------------------------------------------------------------
#  El campo: el cesped, la hierba alta, las flores, la cerca, los robles y los montes
# ----------------------------------------------------------------------
CESPED = _r('16240e', '1e3014', '283c1a', '334a20', '405a28')
TIERRA = _r('1e140c', '2a1c12', '382618', '46301e', '563c26')
HIERBA = _r('14240c', '1c3212', '284418', '34561e', '426a26')
MADERA = _r('2a1c10', '3a2816', '4e361e', '644628', '7a5832')
TRONCO = _r('1a120a', '261a10', '342416', '42301c', '503a22')
HOJAS = _r('0c180a', '12220e', '1a2e14', '223a18', '2c481e')


def _cesped(semilla):
    """El cesped de noche, 16 x 16 por bloque: verde oscuro con matas de dos pixeles mas claras y alguna mas oscura."""
    rng = random.Random(semilla)
    n = 16
    idx = np.full((n, n), 2)
    for _ in range(24):
        x, y = rng.randrange(n), rng.randrange(n)
        idx[y, x] = rng.choice((1, 3, 3))
        if rng.random() < 0.5:
            idx[(y + 1) % n, x] = idx[y, x]
    return bm._imagen(idx, CESPED)


qm._reg('cesped_fg', _cesped(5))


def p_tierra(tw, th, cara, s):
    """El costado de un bloque de cesped: la tierra con la franja de cesped arriba, que cae en dientes."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t = bm._imagen(np.where((((xs // 2) * 5 + (ys // 2) * 3 + s) % 6) == 0, 1, 2), TIERRA)
    borde = ys < 3 + ((xs * 7 + s) % 3 == 0)
    t[borde] = bm._imagen(np.full((th, tw), 2), CESPED)[borde]
    return t, None


def p_cesped(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where((xs * 3 + ys * 5 + s) % 7 == 0, 3, 2), CESPED), None


def p_hierba(tw, th, cara, s):
    """La hierba alta: hojas finas de abajo arriba, mas claras en la punta, con huecos (se ve a traves)."""
    t = np.zeros((th, tw, 4), np.uint8)
    rng = random.Random(s)
    for x in range(tw):
        if rng.random() < 0.45:
            continue
        alto = int(th * rng.uniform(0.45, 1.0))
        for y in range(th - alto, th):
            c = HIERBA[3] if y < th - alto + 2 else HIERBA[2 if (x + y) % 3 else 1]
            t[y, x] = (*c, 255)
    return t, None


def p_flor(tw, th, cara, s):
    """Una flor del campo (una azulina): el tallo y la corola de cuatro pixeles."""
    t = np.zeros((th, tw, 4), np.uint8)
    cx = tw // 2
    t[th // 3:, cx] = (*HIERBA[2], 255)
    for dx, dy in ((0, 0), (-1, 1), (1, 1), (0, 2), (0, 1)):
        if 0 <= cx + dx < tw:
            t[1 + dy, cx + dx] = (120, 150, 230, 255) if (dx, dy) != (0, 1) else (240, 230, 160, 255)
    return t, None


def p_madera(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    if cara in ('arriba', 'abajo'):
        idx = np.where((xs + ys) % 4 == 0, 3, 2)
    else:
        idx = np.where((xs % 4) == 0, 1, 2)
        idx[(ys % 7) == 3] = 3
    return bm._imagen(idx, MADERA), None


def p_tronco(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs + s) % 4 == 0, 1, 2)
    idx[((ys // 3) + xs + s) % 7 == 0] = 3
    return bm._imagen(idx, TRONCO), None


def p_hojas(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = 2 + (((xs // 2) * 5 + (ys // 2) * 3 + s) % 4 == 0).astype(int) - (((xs // 2) * 3 + (ys // 2) * 7 + s) % 5 == 0)
    return bm._imagen(np.clip(idx, 0, 4), HOJAS), None


def p_monte(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where(((xs // 3) + (ys // 3) + s) % 5 == 0, 1, 0), HOJAS), None


for _n, _f in (('tierra', p_tierra), ('cesped', p_cesped), ('hierba', p_hierba), ('flor', p_flor), ('madera', p_madera),
               ('tronco', p_tronco), ('hojas', p_hojas), ('monte', p_monte)):
    _f.__name__ = 'fgE_' + _n


def _plano(qs, centro, ancho, alto, giro, pintor, semilla):
    """Dos planos cruzados (la hierba y las flores de Minecraft)."""
    x, y, z = centro
    for a in (giro, giro + math.pi / 2):
        dx, dz = math.cos(a) * ancho / 2, math.sin(a) * ancho / 2
        P4 = ((x - dx, y, z - dz), (x + dx, y, z + dz), (x + dx, y + alto, z + dz), (x - dx, y + alto, z - dz))
        fg.hoja(qs, P4, pintor, ancho * 2, alto * 2, semilla)           # a 16 pixeles por bloque (bm.PPB = 8)


def roble(qs, x, z, alto, semilla):
    M = vr.T(x, 0.0, z)
    bm.cubo(qs, M, -0.5, 0.0, -0.5, 1.0, alto, 1.0, p_tronco, semilla=semilla)
    bm.cubo(qs, M, -2.5, alto - 1.5, -2.5, 5.0, 2.0, 5.0, p_hojas, semilla=semilla)
    bm.cubo(qs, M, -1.5, alto + 0.5, -1.5, 3.0, 1.2, 3.0, p_hojas, semilla=semilla + 1)


def campo(lz, cam, niebla, S, luces, libre=None, cerca=True, semilla=4):
    """El cesped por bloques (cerca) y por losas grandes (lejos), algun escalon de un bloque, la hierba alta y las
    flores (sin tapar al bicho ni a la camara), la cerca de madera detras, los robles y los montes."""
    libre = libre or (lambda x, z: False)
    r = random.Random(semilla)
    qs = []

    def baldosa(gx, gz, p, y):
        P = [(gx + p, y, gz), (gx, y, gz), (gx, y, gz + p), (gx + p, y, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(p, 0), (0, 0), (0, p), (p, p)], 'cesped_fg'))

    ext = 64
    for gx in range(-ext, ext, 8):
        for gz in range(-ext, ext, 8):
            if not (-16 <= gx < 16 and -16 <= gz < 16):
                baldosa(gx, gz, 8, 0.0)
    escalones = set()
    for _ in range(14):                                                              # escalones de un bloque, lejos
        a, d = r.uniform(0, TAU), r.uniform(9, 15)
        bx, bz = int(math.cos(a) * d), int(math.sin(a) * d)
        for dx in range(r.randint(2, 4)):
            for dz in range(r.randint(2, 4)):
                escalones.add((bx + dx, bz + dz))
    for gx in range(-16, 16):
        for gz in range(-16, 16):
            if (gx, gz) in escalones and not libre(gx + 0.5, gz + 0.5):
                bm.cubo(qs, vr.T(gx, 0.0, gz), 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, p_tierra,
                        caras={'arriba': p_cesped}, semilla=(gx * 7 + gz) % 5)
            else:
                baldosa(gx, gz, 1, 0.0)
    ojo = cam.ojo
    for k in range(260):                                                             # la hierba alta y las flores
        x, z = r.uniform(-13, 13), r.uniform(-13, 13)
        if libre(x, z) or (int(math.floor(x)), int(math.floor(z))) in escalones:
            continue
        if math.hypot(x - ojo[0], z - ojo[2]) < 3.0:
            continue
        if r.random() < 0.14:
            _plano(qs, (x, 0.0, z), 0.5, 0.55, r.uniform(0, 1), p_flor, k % 5)
        else:
            _plano(qs, (x, 0.0, z), 0.9, r.uniform(0.5, 0.9), r.uniform(0, 1), p_hierba, k % 7)
    if cerca:                                                                        # la cerca, detras
        zc = -4.5
        for x in range(-9, 10, 2):
            if libre(x, zc):
                continue
            bm.cubo(qs, vr.T(x, 0.0, zc), -0.13, 0.0, -0.13, 0.26, 1.5, 0.26, p_madera, semilla=x % 5)
            if x < 9:
                for y in (0.55, 1.1):
                    bm.cubo(qs, vr.T(x, y, zc), 0.0, 0.0, -0.07, 2.0, 0.2, 0.14, p_madera, semilla=1)
    for k, (x, z, alto) in enumerate(((-11, -12, 5), (8, -14, 6), (15, -9, 5), (-17, -6, 6), (3, -22, 5),
                                      (-6, -26, 6), (20, -20, 5))):
        if not libre(x, z):
            roble(qs, x + 0.5, z + 0.5, alto, semilla + k)
    for k in range(12):                                                              # los montes de lo lejos
        a = -math.pi / 2 + r.uniform(-1.4, 1.4)
        d = r.uniform(46, 60)
        x, z = math.cos(a) * d, math.sin(a) * d
        w, alto = r.uniform(10, 18), r.uniform(5, 11)
        bm.cubo(qs, vr.T(x, 0.0, z) @ vr.Ry(k), -w / 2, 0.0, -w / 2, w, alto, w, p_monte, semilla=k)
    qm.dibujar(lz, cam, qs, luces, S['amb'], niebla)


def cielo(W, H, horizonte, S, luna_x=0.18):
    """La noche: negra azulada arriba, mas clara en el horizonte, la luna cuadrada con sus manchas y su halo, y
    estrellas."""
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.55, arriba + (medio - arriba) * (k / 0.55), medio + (abajo - medio) * ((k - 0.55) / 0.45))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    r = random.Random(5)
    for _ in range(int(110 * W / 1600)):
        x, yy = r.randrange(W), r.randrange(max(1, int(horizonte * 0.8)))
        g = max(1, int(W / 1600 * r.choice((1, 1, 2))))
        col[yy:yy + g, x:x + g] = np.array((0.75, 0.82, 0.95)) * r.uniform(0.35, 0.9)
    lado = int(H * 0.085)
    lx, ly = int(W * luna_x), int(min(horizonte * 0.35, H * 0.2))
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - lx) / W, (yy - ly) / H * 0.62)
    col += np.array(S['luna'])[None, None, :] * (np.exp(-(d / 0.08) ** 2) * 0.2)[..., None]
    celda = max(1, lado // 8)
    for j in range(8):
        for i in range(8):
            tono = 0.92 if (i * 3 + j * 5) % 7 not in (0, 3) else 0.74
            if (i, j) in ((2, 2), (5, 4), (3, 5), (6, 1)):
                tono = 0.66
            col[ly - lado // 2 + j * celda: ly - lado // 2 + (j + 1) * celda,
                lx - lado // 2 + i * celda: lx - lado // 2 + (i + 1) * celda] = np.array((0.86, 0.9, 0.95)) * tono
    return np.clip(col, 0, 1)


def revelar(lz, cam, W, H, S, brillo=0.9, fuerza_vineta=0.4, motas=0, color_motas=(255, 240, 200), semilla=3):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, S)
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * brillo, radios=((2 * K, 0.5), (10 * K, 0.45), (40 * K, 0.4))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if motas:                                                                        # motas de luz que flotan
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        r = random.Random(semilla)
        for _ in range(int(motas * W / 1600)):
            x, y = r.uniform(0, W), r.uniform(H * 0.25, H * 0.9)
            g = max(1, int(r.choice((1, 2, 2)) * W / 1600))
            d.rectangle((x, y, x + g, y + g), fill=(*color_motas, r.randint(150, 240)))
        glow = capa.filter(ImageFilter.GaussianBlur(4))
        img = Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)
    return img


def destello(img, centro, color, fuerza=1.0, rayos=10, semilla=2):
    """El fogonazo encima de la foto: un halo blanco enorme y unos rayos finos que salen del centro."""
    W, H = img.size
    arr = np.array(img.convert('RGB')).astype(float) / 255
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = centro
    d = np.hypot(xx - cx, yy - cy) / W
    col = np.array(_c(color))
    halo = (np.exp(-(d / 0.05) ** 2) * 1.0 + np.exp(-(d / 0.16) ** 2) * 0.45 + np.exp(-(d / 0.45) ** 2) * 0.18) * fuerza
    ang = np.arctan2(yy - cy, xx - cx)
    r = random.Random(semilla)
    rayo = np.zeros_like(d)
    for k in range(rayos):
        a = k * TAU / rayos + r.uniform(-0.15, 0.15)
        dif = np.abs((ang - a + math.pi) % TAU - math.pi)
        rayo += np.exp(-(dif / 0.012) ** 2) * np.exp(-d / r.uniform(0.18, 0.32)) * r.uniform(0.4, 0.8)
    luz = halo + rayo * fuerza * 0.8
    blanco = (col * 0.35 + 0.65)
    arr = 1 - (1 - arr) * (1 - np.clip(luz, 0, 1)[..., None] * blanco[None, None, :])
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


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


def luz_bicho(info, fuerza=1.0, alcance=2.2):
    """La luz que sale del bicho: del farol y, mas floja, de la boca."""
    c = _c(info['luz'])
    return [(tuple(info['nucleo']) + (alcance,), c, 1.3 * fuerza, 'punto'),
            (tuple(info['boca']) + (alcance * 0.6,), c, 0.6 * fuerza, 'punto')]


# el jugador que se tapa los ojos (los brazos: 'bi' el izquierdo, 'bd' el derecho)
TAPADO = {'bi': {'rot': (-150, 0, -48)}, 'bd': {'rot': (-150, 0, 48)}, 'cabeza': {'rot': (12, 0, 0)}}


def camara(vista, info):
    c = np.asarray(info['cabeza'], float)
    if vista == 'heroe':
        return (1.75, 0.48, 2.95), (0.0, 0.66, 0.1), 48
    if vista == 'lado':
        return (3.2, 0.75, 0.3), (0.0, 0.62, 0.0), 45
    if vista == 'arriba':
        return (1.8, 2.6, 1.6), (0.0, 0.5, 0.0), 45
    if vista == 'cabeza':
        return tuple(c + np.array((0.42, 0.1, 0.78))), tuple(c + np.array((0.0, -0.04, 0.0))), 50
    return (4.4, 1.25, 1.9), (0.0, 0.85, 1.3), 48


def escena(cual, vista, brillo=0.9, motas=20):
    """Una foto: el campo de noche; el Fogonazo (en la de accion, estallando delante de un jugador); el contorno blanco;
    y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio()
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    accion = vista == 'accion'
    qs, info = fg.fogonazo(cual, 'estalla' if accion else 'acecho')
    ojo, obj, fov = camara(vista, info)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    luces = S['luces'] + luz_bicho(info, 3.2 if accion else 1.0, 4.5 if accion else 2.2)
    libre = (lambda x, z: math.hypot(x, z) < (2.6 if accion else 1.2) or (accion and math.hypot(x, z - 2.6) < 1.2))
    campo(lz, cam, niebla, S, luces, libre)
    z0 = lz.z.copy()
    if accion:
        nm.dibujar(lz, cam, nm.quads(ne.jugador(), TAPADO, ne.jugador_a_mundo(0.0, 2.6, 0)), luces, S['amb'], niebla)
    fg.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    img = revelar(lz, cam, W, H, S, brillo=brillo, motas=motas, color_motas=tuple(nm._hex(info['luz'])))
    if accion:
        x, y = cam.proyectar(np.asarray(info['nucleo'], float))[:2]
        img = destello(img, (x / SS, y / SS), info['luz'], 0.85)
    return img


def heroe(cual):
    guardar(escena(cual, 'heroe'), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', motas=8), 'cabeza_' + cual)


def accion(cual):
    guardar(escena(cual, 'accion', brillo=1.1, motas=40), 'accion_' + cual)


def pantalla(cual='A'):
    """Lo que ve el jugador, en tres tiempos: el bicho que se abre delante (a tres bloques), la pantalla en blanco y
    como se va el blanco."""
    W, H = int(640 * K), int(400 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio()
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    qs, info = fg.fogonazo(cual, 'estalla')
    qs = qm.transformar(qs, vr.T(0.0, 0.0, 0.0))
    cam = vr.Camara((0.15, 1.62, 3.1), (0.0, 0.75, 0.0), 70, W * SS, H * SS)
    luces = S['luces'] + luz_bicho(info, 3.2, 4.5)
    campo(lz, cam, niebla, S, luces, lambda x, z: math.hypot(x, z) < 1.2, cerca=True)
    fg.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    uno = revelar(lz, cam, W, H, S, brillo=1.1, motas=25, color_motas=tuple(nm._hex(info['luz'])))
    x, y = cam.proyectar(np.asarray(info['nucleo'], float))[:2]
    uno = destello(uno, (x / SS, y / SS), info['luz'], 0.6)
    blanco = Image.new('RGB', (W, H), (255, 253, 248))
    dos = Image.blend(uno.convert('RGB'), blanco, 0.97)
    tres_ = Image.blend(uno.convert('RGB'), blanco, 0.6)
    hueco = int(14 * K)
    hoja_ = Image.new('RGB', (W * 3 + hueco * 2, H), (16, 16, 20))
    for k, im in enumerate((uno, dos, tres_)):
        hoja_.paste(im.convert('RGB'), (k * (W + hueco), 0))
    guardar(hoja_, 'pantalla_' + cual)


def tres(nombre='tres'):
    """Los tres juntos en el campo, con un jugador de pie al lado."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio()
    niebla = qe.Niebla(S['niebla'], 10, 60)
    cam = vr.Camara((0.4, 1.0, 6.4), (0.4, 0.55, 0.0), 40, W * SS, H * SS)
    modelos = []
    luces = list(S['luces'])
    for cual, x in (('A', -2.4), ('B', 0.0), ('C', 2.4)):
        qs, info = fg.fogonazo(cual, 'acecho')
        M = vr.T(x, 0, 0) @ vr.Ry(0.25 if x < 0 else (-0.25 if x > 0 else 0.0))
        qs = qm.transformar(qs, M)
        info = dict(info, nucleo=fg.pt(M, info['nucleo']), boca=fg.pt(M, info['boca']))
        luces += luz_bicho(info, 1.0, 2.0)
        modelos.append(qs)
    libre = (lambda x, z: -1.3 < z < 5.5 and -3.8 < x < 5.2)
    campo(lz, cam, niebla, S, luces, libre)
    figura = np.zeros(lz.z.shape, bool)
    for qs in modelos:
        z0 = lz.z.copy()
        fg.dibujar(lz, cam, qs, luces, S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(4.2, 0.0, 180)), luces, S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, motas=30), nombre)


def materiales(nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo, con el escudo de la cabeza, el ojo compuesto, la placa
    del lomo, la luz del farol (en el Argos, su ojo cerrado; en el Racimo, la vaina), el paladar, la antena y el
    diente."""
    W = 1480
    filas = []
    for c in 'ABC':
        P = fg.pintores(fg.VARIANTES[c])
        farol = {'A': (P['luz'], 'frente', 10, 10), 'B': (P['ojo'], 'frente', 7, 5), 'C': (P['vaina'], 'frente', 6, 6)}[c]
        fila = [(P['escudo'], 'arriba', 12, 10), (P['compuesto'], 'frente', 5, 5), (P['placa'], 'arriba', 13, 6), farol,
                (P['paladar'], 'arriba', 8, 10), (P['antena'], 'der', 12, 2), (P['diente'], 'frente', 2, 6)]
        filas.append(fila)
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
            cx = 40 + k * 178
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(70, 64, 72))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'accion_' + c: (lambda c=c: accion(c)) for c in 'ABC'})
ESCENAS.update({'pantalla': pantalla, 'tres': tres, 'materiales': materiales})
for _c_ in 'ABC':                                                                    # vistas de prueba
    for _v in ('lado', 'arriba'):
        ESCENAS['%s_%s' % (_v, _c_)] = (lambda c=_c_, v=_v: guardar(escena(c, v, motas=0), '%s_%s' % (v, c)))
    ESCENAS['lado_estalla_' + _c_] = (lambda c=_c_: guardar(escena(c, 'accion', motas=0), 'accion_' + c))

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

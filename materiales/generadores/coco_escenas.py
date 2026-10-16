"""
Renders del Coco (16-10-2026), el mob que te mete en la barriga: a las afueras de una aldea al anochecer (las casas de
madera con las ventanas encendidas, el camino de tierra, la cerca y el farol), que es por donde viene el Coco de la
nana; la cara (de cerca); las fotos de lo que hace (agarrando a un jugador, y con el jugador ya dentro y el aviso
encima: el icono de alerta, el nombre y «¡ha sido atrapado!»); los tres juntos con un jugador; y la lamina de
materiales.

Las fotos salen sin letras (lo unico escrito es el aviso, que es del juego) y con el contorno blanco.

Uso: python coco_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
     (con RAPIDO=1 en el entorno, a media resolucion para probar)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne            # el jugador
import quimeras_modelo as qm
import quimeras_escenas as qe         # el lienzo, la niebla y el revelado
import bestias_modelo as bm
import coco_modelo as co

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
    """El anochecer: el cielo todavia con luz por el oeste (detras de la aldea), la luz fria por delante y la calida de
    las ventanas y el farol."""
    return dict(
        luces=[((0.45, 0.65, 0.75), (0.62, 0.7, 0.98), 0.55, 'llave'), ((-0.4, 0.3, -1.0), (1.0, 0.62, 0.42), 1.0, 'contra')],
        amb=(0.2, 0.21, 0.3), niebla=(0.1, 0.09, 0.16), niebla_d=(14, 70),
        cielo=((0.035, 0.045, 0.12), (0.16, 0.13, 0.3), (0.62, 0.34, 0.26)),
    )


# ----------------------------------------------------------------------
#  La aldea: las texturas, a 16 pixeles por bloque, como las de Minecraft (pero nuestras)
# ----------------------------------------------------------------------
CESPED = _r('1a2a16', '22361c', '2c4422', '36522a', '426232')
TIERRA = _r('2a1e14', '3a2a1c', '4a3624', '5a432e', '6a5038')
CAMINO = _r('3e3222', '4e402c', '5e4e36', '6e5c40', '7e6a4a')
TABLA = _r('2e2014', '4a3420', '644830', '7a5a3c', '8e6c48')
TRONCO = _r('1e150c', '2c2014', '3a2a1a', '4a3822', '5a462c')
TEJA = _r('1a1214', '281c1e', '36262a', '443036', '523a42')
PIEDRA = _r('1e1e22', '2e2e34', '3e3e46', '505058', '64646c')
HOJA = _r('0e1a10', '142616', '1c321c', '244024', '2e4e2c')


def _cesped(semilla):
    """El cesped, 16 x 16 por bloque: verde de anochecer con matas de dos pixeles mas claras y alguna mas oscura."""
    rng = random.Random(semilla)
    n = 16
    idx = np.full((n, n), 2)
    for _ in range(26):
        x, y = rng.randrange(n), rng.randrange(n)
        idx[y, x] = rng.choice((1, 3, 3))
        if rng.random() < 0.5:
            idx[(y + 1) % n, x] = idx[y, x]
    return bm._imagen(idx, CESPED)


def _camino(semilla):
    """El camino de tierra pisada: manchas limpias de dos pixeles."""
    rng = random.Random(semilla)
    n = 16
    idx = np.full((n, n), 2)
    for _ in range(14):
        x, y = rng.randrange(0, n, 2), rng.randrange(0, n, 2)
        idx[y:y + 2, x:x + 2] = rng.choice((1, 3, 3, 4))
    return bm._imagen(idx, CAMINO)


qm._reg('cesped_co', _cesped(5))
qm._reg('camino_co', _camino(7))


def p_tablas(tw, th, cara, s):
    """Tablas de roble: cuatro por bloque, con la raya oscura entre ellas y la junta de cada una en otro sitio."""
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.full((th, tw), 2)
    fila = ys // 4
    idx[(ys % 4) == 0] = 0
    idx[((xs + fila * 7 + s) % 16) == 0] = 1
    idx[((ys % 4) == 2) & (((xs + fila * 5) % 9) < 3)] = 3
    return bm._imagen(idx, TABLA), None


def p_tronco(tw, th, cara, s):
    """El tronco de las esquinas: la corteza a vetas de arriba abajo; las puntas, en anillos."""
    ys, xs = np.mgrid[0:th, 0:tw]
    if cara in ('arriba', 'abajo'):
        r = np.maximum(np.abs(xs - (tw - 1) / 2), np.abs(ys - (th - 1) / 2))
        return bm._imagen(np.where(r > tw / 2 - 1.5, 1, np.where((r.astype(int) % 3) == 0, 2, 3)), TABLA), None
    idx = np.where((xs + s) % 4 == 0, 1, 2)
    idx[((ys // 3) + xs + s) % 7 == 0] = 3
    return bm._imagen(idx, TRONCO), None


def p_teja(tw, th, cara, s):
    """El tejado, de tablas oscuras."""
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.full((th, tw), 2)
    idx[(ys % 4) == 0] = 0
    idx[(ys % 4) == 1] = 3
    idx[((xs + (ys // 4) * 6 + s) % 12) == 0] = 1
    return bm._imagen(idx, TEJA), None


def p_piedra(tw, th, cara, s):
    """La piedra del zocalo: piedras de cuatro a seis pixeles con la junta oscura."""
    ys, xs = np.mgrid[0:th, 0:tw]
    fila = ys // 5
    col = (xs + (fila % 2) * 3) // 6
    idx = np.where(((col * 3 + fila * 5 + s) % 4) == 0, 3, 2)
    idx[(ys % 5) == 0] = 0
    idx[((xs + (fila % 2) * 3) % 6) == 0] = 0
    idx[((ys % 5) == 1) & (((xs + (fila % 2) * 3) % 6) == 1)] = 4
    return bm._imagen(idx, PIEDRA), None


def p_ventana(tw, th, cara, s):
    """La ventana encendida: el cristal calido (mas claro en medio), con la cruz del marco oscura."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (255, 178, 84, 255)
    cen = (np.abs(xs - (tw - 1) / 2) < tw / 3.2) & (np.abs(ys - (th - 1) / 2) < th / 3.2)
    t[cen] = (255, 222, 150, 255)
    marco = (xs == 0) | (ys == 0) | (xs == tw - 1) | (ys == th - 1) | (np.abs(xs - (tw - 1) / 2) < 0.6) | \
            (np.abs(ys - (th - 1) / 2) < 0.6)
    t[marco] = (40, 28, 18, 255)
    return t, bm._emis(t, ~marco, 255)


def p_puerta(tw, th, cara, s):
    """La puerta, de tablas oscuras de arriba abajo, con dos cuarterones y el tirador."""
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs % 4) == 0, 0, 1)
    idx[(ys == th // 3) | (ys == (2 * th) // 3)] = 0
    t = bm._imagen(idx, TEJA)
    if tw >= 6:
        t[th // 2, tw - 4] = (150, 130, 90, 255)
    return t, None


def p_camino_lado(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where((((xs // 2) * 5 + (ys // 2) * 3 + s) % 6) == 0, 1, 2), TIERRA), None


def p_hoja(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = 2 + (((xs // 2) * 5 + (ys // 2) * 3 + s) % 4 == 0).astype(int) - (((xs // 2) * 3 + (ys // 2) * 7 + s) % 5 == 0)
    return bm._imagen(np.clip(idx, 0, 4), HOJA), None


def p_farol(tw, th, cara, s):
    """El farol: el cristal calido que brilla con el marco de hierro oscuro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (255, 196, 100, 255)
    t[(np.abs(xs - (tw - 1) / 2) < tw / 4) & (np.abs(ys - (th - 1) / 2) < th / 4)] = (255, 240, 190, 255)
    t[(xs == 0) | (xs == tw - 1) | (ys == 0) | (ys == th - 1)] = (34, 30, 30, 255)
    return t, None


def p_monte(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where(((xs // 3) + (ys // 3) + s) % 5 == 0, 1, 0), HOJA), None


for _n, _f in (('tablas', p_tablas), ('tronco', p_tronco), ('teja', p_teja), ('piedra', p_piedra),
               ('ventana', p_ventana), ('puerta', p_puerta), ('camino_lado', p_camino_lado), ('hoja', p_hoja),
               ('farol', p_farol), ('monte', p_monte)):
    _f.__name__ = 'coE_' + _n
bm.PLENOS.add(p_farol)


def casa(qs, x, z, ancho, fondo, alto, ventanas=(), puerta=None, semilla=0):
    """Una casa de la aldea, con la fachada hacia +z en z: el zocalo de piedra, las paredes de tablas, los troncos de
    las esquinas, las ventanas encendidas y la puerta, y el tejado a dos aguas en escalones (a lo largo de x)."""
    x0, x1, z0, z1 = x - ancho / 2, x + ancho / 2, z - fondo, z
    I = np.eye(4)
    bm.cubo(qs, I, x0, 0.0, z0, ancho, 1.0, fondo, p_piedra, semilla=semilla)
    bm.cubo(qs, I, x0 + 0.02, 1.0, z0 + 0.02, ancho - 0.04, alto - 1.0, fondo - 0.04, p_tablas, semilla=semilla)
    for cx in (x0, x1 - 1.0):
        for cz in (z0, z1 - 1.0):
            bm.cubo(qs, I, cx, 0.0, cz, 1.0, alto, 1.0, p_tronco, semilla=semilla)
    bm.cubo(qs, I, x0, alto - 1.0, z1 - 1.0, ancho, 1.0, 1.0, p_tronco, semilla=semilla + 1)       # la viga de la fachada
    for vx, vy in ventanas:
        bm.cubo(qs, I, x + vx - 0.5, vy, z1 - 0.02, 1.0, 1.0, 0.06, p_ventana, semilla=semilla)
    if puerta is not None:
        bm.cubo(qs, I, x + puerta - 0.5, 1.0, z1 - 0.02, 1.0, 2.0, 0.06, p_puerta, semilla=semilla)
    n = int(math.ceil(fondo / 2 + 0.5))
    for i in range(n):                                                                         # el tejado
        za, zb = z0 - 0.5 + i * 0.5, z1 + 0.5 - i * 0.5
        if zb - za < 0.5:
            break
        bm.cubo(qs, I, x0 - 0.4, alto + i * 0.5, za, ancho + 0.8, 0.5, zb - za, p_teja, semilla=semilla + 2)
        bm.cubo(qs, I, x0 + 0.02, alto + i * 0.5 - 0.5, za + 0.5, ancho - 0.04, 0.5, max(0.1, zb - za - 1.0), p_tablas,
                semilla=semilla + 3)


def cerca(qs, puntos, semilla=0):
    """Una cerca de madera: postes en cada punto y dos travesaños entre ellos."""
    I = np.eye(4)
    for (xa, za), (xb, zb) in zip(puntos[:-1], puntos[1:]):
        bm.cubo(qs, I, xa - 0.125, 0.0, za - 0.125, 0.25, 1.5, 0.25, p_tablas, semilla=semilla)
        L = math.hypot(xb - xa, zb - za)
        M = vr.T(xa, 0.0, za) @ vr.Ry(-math.atan2(zb - za, xb - xa))
        for y in (0.4, 1.0):
            bm.cubo(qs, M, 0.0, y, -0.06, L, 0.18, 0.12, p_tablas, semilla=semilla + 1)
    xb, zb = puntos[-1]
    bm.cubo(qs, I, xb - 0.125, 0.0, zb - 0.125, 0.25, 1.5, 0.25, p_tablas, semilla=semilla)


def arbol(qs, x, z, alto, semilla):
    I = vr.T(x, 0.0, z)
    bm.cubo(qs, I, -0.5, 0.0, -0.5, 1.0, alto, 1.0, p_tronco, semilla=semilla)
    bm.cubo(qs, I, -2.5, alto - 1.5, -2.5, 5.0, 2.0, 5.0, p_hoja, semilla=semilla)
    bm.cubo(qs, I, -1.5, alto + 0.5, -1.5, 3.0, 1.2, 3.0, p_hoja, semilla=semilla + 1)


FAROL = (2.6, 2.1, -2.6)


def aldea(lz, cam, niebla, S, luces, libre=None, cercas=True, semilla=4):
    """El cesped (por bloques cerca y por losas lejos), el camino de tierra hasta la calle, las casas con las ventanas
    encendidas, la cerca, el farol, los arboles y los montes del fondo."""
    libre = libre or (lambda x, z: False)
    r = random.Random(semilla)
    qs = []
    ppb = bm.PPB
    bm.PPB = 16
    try:
        def baldosa(gx, gz, p, mat):
            P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
            qs.append(([np.array(q, float) for q in P], [(p, 0), (0, 0), (0, p), (p, p)], mat))

        def es_camino(gx, gz):
            return (-2 <= gx <= 1 and gz <= 14) or (-6.0 <= gz <= -3.0 and -24 <= gx <= 24)

        ext = 72
        for gx in range(-ext, ext, 8):
            for gz in range(-ext, ext, 8):
                if not (-24 <= gx < 24 and -24 <= gz < 24):
                    baldosa(gx, gz, 8, 'cesped_co')
        for gx in range(-24, 24):
            for gz in range(-24, 24):
                baldosa(gx, gz, 1, 'camino_co' if es_camino(gx, gz) else 'cesped_co')
        casa(qs, -6.5, -7.5, 7.0, 6.0, 4.0, ventanas=((-1.8, 2.0), (1.8, 2.0)), puerta=0.0, semilla=1)
        casa(qs, 6.0, -8.0, 6.0, 6.0, 4.0, ventanas=((-1.5, 2.0),), puerta=1.0, semilla=2)
        casa(qs, -16.5, -9.0, 7.0, 6.0, 5.0, ventanas=((-2.0, 2.0), (2.0, 2.0), (0.0, 3.4)), puerta=None, semilla=3)
        casa(qs, 15.5, -9.5, 7.0, 7.0, 4.0, ventanas=((0.0, 2.0),), puerta=-2.0, semilla=4)
        casa(qs, 0.5, -20.0, 8.0, 6.0, 5.0, ventanas=((-2.4, 2.0), (2.4, 2.0), (0.0, 3.4)), puerta=None, semilla=5)
        if cercas:
            cerca(qs, [(-2.6, -2.0), (-2.6, 0.0), (-2.6, 2.0), (-2.6, 4.0), (-4.6, 4.0), (-6.6, 4.0), (-8.6, 4.0)], semilla=6)
            cerca(qs, [(3.0, -1.0), (5.0, -1.0), (7.0, -1.0), (9.0, -1.0)], semilla=7)
        fx, fy, fz = FAROL                                                                     # el farol, en un poste
        bm.cubo(qs, np.eye(4), fx - 0.125, 0.0, fz - 0.125, 0.25, 1.8, 0.25, p_tronco, semilla=8)
        bm.cubo(qs, np.eye(4), fx - 0.2, 1.8, fz - 0.2, 0.4, 0.45, 0.4, p_farol, semilla=8)
        for k, (x, z, alto) in enumerate(((-11.0, -16.0, 5), (10.5, -18.0, 6), (-4.0, -27.0, 5), (20.0, -22.0, 5),
                                          (-23.0, -14.0, 6), (9.0, -30.0, 6))):
            if not libre(x, z):
                arbol(qs, x + 0.5, z + 0.5, alto, semilla + k)
        for k in range(12):                                                                    # los montes de lo lejos
            a = -math.pi / 2 + r.uniform(-1.4, 1.4)
            d = r.uniform(50, 64)
            x, z = math.cos(a) * d, math.sin(a) * d
            w, alto = r.uniform(10, 18), r.uniform(5, 11)
            bm.cubo(qs, vr.T(x, 0.0, z) @ vr.Ry(k), -w / 2, 0.0, -w / 2, w, alto, w, p_monte, semilla=k)
    finally:
        bm.PPB = ppb
    qm.dibujar(lz, cam, qs, luces, S['amb'], niebla)


def luces_aldea(cam):
    """La luz calida de las ventanas mas cercanas y la del farol."""
    fuentes = [np.array(FAROL), np.array((-8.3, 2.5, -7.0)), np.array((-4.7, 2.5, -7.0)), np.array((4.5, 2.5, -7.5))]
    return [(tuple(f) + (5.0 if k == 0 else 4.0,), (1.0, 0.7, 0.38), 1.0 if k == 0 else 0.6, 'punto')
            for k, f in enumerate(fuentes)]


def cielo(W, H, horizonte, S):
    """El anochecer: azul de noche arriba, morado en medio y el resplandor naranja que queda en el horizonte, con
    alguna estrella arriba."""
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.6, arriba + (medio - arriba) * (k / 0.6), medio + (abajo - medio) * np.clip((k - 0.6) / 0.4, 0, 1) ** 1.4)
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    r = random.Random(5)
    for _ in range(int(60 * W / 1600)):
        x, yy = r.randrange(W), r.randrange(max(1, int(horizonte * 0.45)))
        g = max(1, int(W / 1600 * r.choice((1, 1, 2))))
        col[yy:yy + g, x:x + g] = np.array((0.8, 0.84, 0.95)) * r.uniform(0.3, 0.8)
    return np.clip(col, 0, 1)


def revelar(lz, cam, W, H, S, brillo=0.9, fuerza_vineta=0.4):
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


# ----------------------------------------------------------------------
#  El aviso de encima: el icono de alerta, el nombre y «¡ha sido atrapado!»
# ----------------------------------------------------------------------
_ATLAS = None


def _atlas():
    """Los glifos de la letra del juego (la de Minecraft, que es la que pintara el aviso), con su ancho."""
    global _ATLAS
    if _ATLAS is None:
        ruta = os.environ.get('FUENTE_MC') or os.path.join(os.path.dirname(os.path.abspath(OUT)), 'fuente', 'ascii.png')
        im = np.array(Image.open(ruta).convert('RGBA'))
        glifos = {}
        for c in range(32, 127):
            cx, cy = (c % 16) * 8, (c // 16) * 8
            g = im[cy:cy + 8, cx:cx + 8, 3] > 0
            cols = np.where(g.any(axis=0))[0]
            ancho = (cols.max() + 1) if len(cols) else 3
            glifos[chr(c)] = (g[:, :ancho], ancho)
        g, a = glifos['!']
        glifos['¡'] = (g[::-1], a)
        _ATLAS = glifos
    return _ATLAS


def _texto(cadena):
    """La mascara de una linea de texto, en pixeles de la letra (8 de alto, un pixel entre letras)."""
    gl = _atlas()
    ancho = sum(gl[c][1] + 1 for c in cadena) - 1
    m = np.zeros((8, ancho), bool)
    x = 0
    for c in cadena:
        g, a = gl[c]
        m[:, x:x + a] |= g
        x += a + 1
    return m


def icono_alerta():
    """El icono de alerta (nuestro, de pixeles): un triangulo rojo de canto oscuro, con la luz en el lado de la
    izquierda y la exclamacion blanca. 15 x 14."""
    W, H = 15, 14
    t = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        media = 0.5 + y * 0.5
        for x in range(W):
            d = abs(x - (W - 1) / 2)
            if d <= media:
                borde = d > media - 1.0 or y == H - 1
                t[y, x] = (70, 8, 10, 255) if borde else ((255, 96, 80, 255) if x < (W - 1) / 2 - media + 2.4 else
                                                         (214, 34, 34, 255))
    for y in (4, 5, 6, 7, 8):
        t[y, 7] = (255, 250, 240, 255)
    t[10, 7] = (255, 250, 240, 255)
    t[t[..., 3] == 0] = 0
    return t


def aviso(img, punto, nombre, escala):
    """El aviso encima del Coco, como lo pinta el juego sobre una entidad (el fondo oscuro translucido de los nombres):
    arriba el icono de alerta, debajo el nombre del jugador (blanco) y debajo «¡ha sido atrapado!» (rojo)."""
    img = img.convert('RGBA')
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    a = np.array(capa)
    cx, base = int(punto[0]), int(punto[1])
    lineas = [(_texto(nombre), (255, 255, 255)), (_texto('¡ha sido atrapado!'), (255, 85, 85))]
    alto_linea = 10 * escala
    y = base - len(lineas) * alto_linea
    for m, col in lineas:
        w = m.shape[1] * escala
        x0 = cx - w // 2
        a[y - escala:y + 9 * escala, x0 - 2 * escala:x0 + w + 1 * escala] = (0, 0, 0, 64)  # el fondo de los nombres
        big = np.kron(m, np.ones((escala, escala), bool))
        sub = a[y:y + big.shape[0], x0:x0 + big.shape[1]]
        sub[big] = (*col, 255)
        y += alto_linea
    ic = icono_alerta()
    e2 = escala * 2
    big = np.kron(ic, np.ones((e2, e2, 1), np.uint8))
    y0 = base - len(lineas) * alto_linea - big.shape[0] - 3 * escala
    x0 = cx - big.shape[1] // 2
    sub = a[y0:y0 + big.shape[0], x0:x0 + big.shape[1]]
    m = big[..., 3] > 0
    sub[m] = big[m]
    return Image.alpha_composite(img, Image.fromarray(a))


# ----------------------------------------------------------------------
#  Las fotos
# ----------------------------------------------------------------------
# el amigo que viene a salvarlo, con la espada alzada (los brazos: 'bi' el izquierdo, 'bd' el derecho)
nm.MAT.update({'hoja_esp': ne._plano('d8dde2', 'b8c0c8', 45), 'guarda_esp': ne._plano('5a4a30', '4a3a26', 46)})


def jugador_espada():
    j = ne.jugador()
    bd = j[4][0][4][2]                                                                         # el brazo derecho
    bd[3].extend([((-0.5, 8.0, -3.0, 1.0, 4.0, 1.0), 'guarda_esp'), ((-0.5, 9.5, -1.6, 1.0, 1.0, 3.0), 'guarda_esp'),
                  ((-0.5, 9.2, -15.0, 1.0, 1.6, 12.0), 'hoja_esp')])
    return j


GOLPE = {'bd': {'rot': (-150, 0, 20)}, 'bi': {'rot': (-30, 0, -20)}, 'cabeza': {'rot': (-8, 0, 0)},
         'pi': {'rot': (25, 0, 0)}, 'pd': {'rot': (-25, 0, 0)}}
AGARRADO = {'bi': {'rot': (-165, 0, -30)}, 'bd': {'rot': (-40, 0, 45)}, 'cabeza': {'rot': (-12, 0, 8)},
            'pi': {'rot': (-25, 0, -6)}, 'pd': {'rot': (18, 0, 6)}}
CORRE = {'bd': {'rot': (40, 0, 8)}, 'bi': {'rot': (-45, 0, -8)}, 'pi': {'rot': (-35, 0, 0)}, 'pd': {'rot': (35, 0, 0)}}


def camara(vista, info):
    c = np.asarray(info['cabeza'], float)
    if vista == 'heroe':
        return (2.3, 0.6, 5.5), (0.0, 1.6, 0.2), 52
    if vista == 'cabeza':
        return tuple(c + np.array((0.95, -0.3, 2.3))), tuple(c + np.array((0.0, -0.12, 0.1))), 46
    if vista == 'accion_A':
        return (3.3, 1.6, 6.1), (-0.55, 2.25, 0.2), 54
    if vista == 'accion_B':
        return (4.3, 1.45, 3.9), (0.25, 1.8, 1.0), 50
    return (3.4, 1.9, 10.4), (0.0, 1.85, 0.0), 42


def escena(cual, vista, brillo=0.9):
    """Una foto: la aldea al anochecer; el Coco (y, en las de accion, los jugadores y el aviso); el contorno blanco."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio()
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    postura = {'accion_A': 'lleno', 'accion_B': 'agarra', 'accion_C': 'lleno'}.get(vista, 'acecho')
    qs, info = co.coco(cual, postura, lleno=postura == 'lleno')
    ojo, obj, fov = camara(vista, info)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    luz = _c(info['luz'])
    luces = S['luces'] + luces_aldea(cam) + [(tuple(info['ojos']) + (1.6,), luz, 0.7, 'punto')]
    aldea(lz, cam, niebla, S, luces, libre=lambda x, z: math.hypot(x, z) < 2.5)
    z0 = lz.z.copy()
    jugadores = []
    if vista == 'accion_A':
        jugadores.append(nm.quads(jugador_espada(), GOLPE, ne.jugador_a_mundo(-1.9, 1.7, -125)))
    elif vista == 'accion_B':
        jugadores.append(nm.quads(ne.jugador(), AGARRADO, vr.T(0.0, 0.78, 0.0) @ ne.jugador_a_mundo(0.0, 1.95, -113)))
    elif vista == 'accion_C':
        jugadores.append(nm.quads(ne.jugador(), CORRE, ne.jugador_a_mundo(-2.3, 3.4, 20)))
    co.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    for q in jugadores:
        nm.dibujar(lz, cam, q, luces, S['amb'], niebla)
    img = revelar(lz, cam, W, H, S, brillo=brillo)
    if postura == 'lleno':
        alto = {'A': 1.05, 'B': 0.9, 'C': 1.2}[cual]                                        # encima de la cresta o la cascara
        x, y = cam.proyectar(np.asarray(info['cabeza'], float) + np.array((0.0, alto, 0.0)))[:2]
        img = aviso(img, (x / SS, y / SS), 'Steve', max(2, int(round((3 if vista == 'accion_A' else 2.4) * K * 1.3))))
    return img


def heroe(cual):
    guardar(escena(cual, 'heroe'), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza'), 'cabeza_' + cual)


def accion(cual):
    guardar(escena(cual, 'accion_' + cual, brillo=1.0), 'accion_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos en el camino, con un jugador de pie al lado."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio()
    niebla = qe.Niebla(S['niebla'], 16, 80)
    cam = vr.Camara((0.0, 1.5, 9.2), (0.0, 1.35, 0.0), 40, W * SS, H * SS)
    luces = S['luces'] + luces_aldea(cam)
    aldea(lz, cam, niebla, S, luces, libre=lambda x, z: abs(z) < 2.5 and abs(x) < 6, cercas=False)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -3.4), ('B', 0.0), ('C', 3.4)):
        qs, info = co.coco(cual, 'acecho')
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(-0.12 * x / 3.4))
        z0 = lz.z.copy()
        luces_c = luces + [(tuple(np.asarray(info['ojos']) + np.array((x, 0, 0))) + (1.6,), _c(info['luz']), 0.6, 'punto')]
        co.dibujar(lz, cam, qs, luces_c, S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(5.6, 0.6, 200)), luces, S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo, con la cascara, la carne de los dientes, el ojo, la
    piel, la barriga y lo de cada uno (la estopa de la cresta, la arpillera o la barba)."""
    W = 1240
    filas = []
    for c in 'ABC':
        P = co.pintores(co.VARIANTES[c])
        propio = {'A': (P['fibra'], 'frente', 4, 12), 'B': (P['arpillera'], 'frente', 12, 12),
                  'C': (P['fibra'], 'frente', 4, 12)}[c]
        filas.append([(P['cascara'], 'frente', 14, 10), (P['diente'], 'frente', 8, 12), (P['cuenca'], 'frente', 5, 5),
                      (P['piel'], 'frente', 10, 10), (P['panza'], 'frente', 16, 16), propio])
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
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(70, 64, 72))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'accion_' + c: (lambda c=c: accion(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

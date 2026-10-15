"""
Renders del rediseno del Slime (15-10-2026): los tres en la cienaga de noche, donde salen los slimes (el agua oscura
con nenufares, las islas de cesped, los robles de pantano con sus lianas, las setas, la luna cuadrada y las
luciernagas), a la escala de Minecraft; su cartel (de cerca y desde abajo); la cara (de cerca); los tres juntos con el
Slime de vanilla y un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python slime_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import slime_modelo as sl

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
    """La misma cienaga para los tres, de noche: la luna detras a la izquierda y la niebla verdosa del pantano."""
    luna = (0.72, 0.84, 1.0)
    return dict(
        luces=[((-0.5, 0.8, 0.5), luna, 0.8, 'llave'), ((-0.4, 0.45, -1.0), luna, 1.05, 'contra'),
               ((0.7, 0.25, 0.6), (0.5, 0.7, 0.6), 0.3, 'llave')],
        amb=(0.2, 0.25, 0.27), niebla=(0.06, 0.11, 0.11), niebla_d=(14, 70),
        cielo=((0.01, 0.015, 0.035), (0.03, 0.07, 0.09), (0.1, 0.2, 0.18)), sol=luna,
        motas=(200, 255, 110),
    )


# ----------------------------------------------------------------------
#  La cienaga: el agua, las islas de cesped, los nenufares, los robles de pantano con lianas y las setas
# ----------------------------------------------------------------------
CESPED = _r('1a2410', '24301a', '2e3c1e', '3a4a24', '4a5c2c')
AGUA = _r('08161a', '0c1e22', '12282c', '1a3436', '284844')
TRONCO = _r('1e160e', '2a1e12', '362818', '44321e', '503c24')
HOJAS = _r('101c0c', '182812', '203418', '2a421e', '365226')


def _cesped(semilla):
    """El cesped del pantano, 16 x 16 por bloque: verde oscuro con matas de dos pixeles mas claras."""
    rng = random.Random(semilla)
    n = 16
    idx = np.full((n, n), 2)
    for _ in range(26):
        x, y = rng.randrange(n), rng.randrange(n)
        idx[y, x] = rng.choice((1, 3, 3))
        if rng.random() < 0.5:
            idx[(y + 1) % n, x] = idx[y, x]
    return bm._imagen(idx, CESPED)


def _agua(semilla):
    """El agua oscura: lisa, con las ondas en rayas cortas mas claras."""
    rng = random.Random(semilla)
    n = 16
    idx = np.full((n, n), 1)
    for _ in range(7):
        x, y = rng.randrange(n), rng.randrange(n)
        for k in range(rng.choice((2, 3, 4))):
            idx[y, (x + k) % n] = 3
    return bm._imagen(idx, AGUA)


qm._reg('cesped_sl', _cesped(5))
qm._reg('agua_sl', _agua(6))


def p_tronco(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs + s) % 4 == 0, 1, 2)
    idx[((ys // 3) + xs + s) % 7 == 0] = 3
    if cara in ('arriba', 'abajo'):
        idx = np.where((np.abs(xs - tw / 2 + 0.5) + np.abs(ys - th / 2 + 0.5)) % 3 < 1, 3, 2)
    return bm._imagen(idx, TRONCO), None


def p_hojas(tw, th, cara, s):
    """Las hojas del roble de pantano: oscuras, en manchas limpias de dos pixeles."""
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = 2 + (((xs // 2) * 5 + (ys // 2) * 3 + s) % 4 == 0).astype(int) - (((xs // 2) * 3 + (ys // 2) * 7 + s) % 5 == 0)
    return bm._imagen(np.clip(idx, 0, 4), HOJAS), None


def p_liana(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where((ys + s) % 3 == 0, 3, 2), HOJAS), None


def p_nenufar(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs + ys) % 4 == 0, 4, 3)
    cx, cy = tw / 2, th / 2
    idx[(np.abs(xs - cx) < 1) & (ys < cy)] = 1                                   # la muesca
    return bm._imagen(idx, _r('1e3a14', '2a4e1a', '386424', '4a7a2e', '5e9238')), None


def p_seta(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    t = bm._imagen(np.full((th, tw), 2), _r('5a1010', '801818', 'a82420', 'c83a2c', 'e85a40'))
    t[((xs + ys * 2 + s) % 5 == 0)] = (240, 230, 220, 255)
    return t, None


def p_pie(tw, th, cara, s):
    return bm._imagen(np.full((th, tw), 3), _r('6a6250', '8a8268', 'b0a888', 'cec6a6', 'e6dec2')), None


def p_monte(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where(((xs // 3) + (ys // 3) + s) % 5 == 0, 2, 1), HOJAS), None


for _n, _f in (('tronco', p_tronco), ('hojas', p_hojas), ('liana', p_liana), ('nenufar', p_nenufar),
               ('seta', p_seta), ('pie', p_pie), ('monte', p_monte)):
    _f.__name__ = 'slE_' + _n


ISLA = [lambda x, z: math.hypot(x, z) < 6.5]          # donde hay tierra seguro (en la foto de los tres, una isla larga)


def _tierra(x, z):
    """Si en (x, z) hay isla de cesped o agua: tierra alrededor del slime y en manchas sueltas."""
    if ISLA[0](x, z):
        return True
    n = math.sin(x * 0.33 + 1.0) + math.cos(z * 0.27) + math.sin((x + z) * 0.19 + 2.0)
    return n > 1.2


def suelo(lz, cam, niebla, S, ext=60, paso=8, cerca=16, paso_cerca=1):
    """El agua entera un poco mas baja y, encima, las islas de cesped por bloques; los nenufares sobre el agua."""
    qs = []

    def baldosa(gx, gz, p, y, mat):
        P = [(gx + p, y, gz), (gx, y, gz), (gx, y, gz + p), (gx + p, y, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(p, 0), (0, 0), (0, p), (p, p)], mat))

    for gx in range(-ext, ext, paso):
        for gz in range(-ext, ext, paso):
            baldosa(gx, gz, paso, -0.18, 'agua_sl')
    cx, cz = cam.ojo[0], cam.ojo[2]
    r = random.Random(3)
    for gx in range(-ext // 2, ext // 2):
        for gz in range(-ext // 2, ext // 2):
            if _tierra(gx + 0.5, gz + 0.5):
                baldosa(gx, gz, 1, 0.0, 'cesped_sl')
            elif r.random() < 0.06 and math.hypot(gx - cx, gz - cz) > 2.5:
                M = vr.T(gx + 0.5, -0.16, gz + 0.5) @ vr.Ry(r.uniform(0, TAU))
                bm.cubo(qs, M, -0.4, 0.0, -0.4, 0.8, 0.02, 0.8, p_nenufar, semilla=r.randrange(7))
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def roble(qs, x, z, alto, semilla):
    """Un roble de pantano: el tronco, la copa ancha y plana en dos pisos y las lianas que cuelgan de los bordes."""
    r = random.Random(semilla)
    M = vr.T(x, 0.0, z)
    bm.cubo(qs, M, -0.5, -0.2, -0.5, 1.0, alto + 0.2, 1.0, p_tronco, semilla=semilla)
    bm.cubo(qs, M, -3.5, alto - 0.6, -3.5, 7.0, 1.2, 7.0, p_hojas, semilla=semilla)
    bm.cubo(qs, M, -2.5, alto + 0.6, -2.5, 5.0, 1.0, 5.0, p_hojas, semilla=semilla + 1)
    for _ in range(9):
        lado = r.randrange(4)
        t = r.uniform(-3.2, 3.2)
        px, pz = [(t, 3.5), (t, -3.5), (3.5, t), (-3.5, t)][lado]
        largo = r.uniform(1.2, 3.6)
        bm.cubo(qs, M, px - 0.08, alto - 0.6 - largo, pz - 0.08, 0.16, largo, 0.16, p_liana, semilla=semilla)


def bioma(lz, cam, niebla, S, semilla=4, libre=None):
    """La cienaga alrededor (sin nada entre la camara y el slime): los robles de pantano, las setas en las islas y la
    linea de arboles a lo lejos."""
    r = random.Random(semilla)
    qs = []
    libre = libre or (lambda x, z: False)
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    lejos = hacia_camara + math.pi
    for k, (rr, dg) in enumerate(((14, -0.85), (15, 0.75), (18, -0.3), (19, 0.3), (22, -1.3), (22, 1.25), (28, 0.0),
                                  (27, -0.7), (28, 0.75))):
        a = lejos + dg
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        if libre(x, z):
            continue
        roble(qs, x + 0.5, z + 0.5, r.uniform(6.0, 8.5), semilla + k)
    for k in range(10):                                                                   # las setas
        a = r.uniform(0, TAU)
        rr = r.uniform(4.0, 9.0)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if libre(x, z) or not _tierra(x, z):
            continue
        M = vr.T(x, 0.0, z)
        bm.cubo(qs, M, -0.08, 0.0, -0.08, 0.16, 0.35, 0.16, p_pie, semilla=k)
        bm.cubo(qs, M, -0.22, 0.35, -0.22, 0.44, 0.18, 0.44, p_seta, semilla=k)
    for k in range(14):                                                                   # los arboles de lo lejos
        a = lejos + r.uniform(-1.5, 1.5)
        rr = r.uniform(44, 58)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w, alto = r.uniform(8, 14), r.uniform(8, 14)
        bm.cubo(qs, vr.T(x, 0.0, z) @ vr.Ry(k), -w / 2, 0.0, -w / 2, w, alto, w, p_monte, semilla=k)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S, luna_x=0.2):
    """La noche del pantano: negra azulada arriba y verdosa en el horizonte, con la luna cuadrada (con sus manchas) a
    la izquierda, su halo y unas pocas estrellas."""
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.55, arriba + (medio - arriba) * (k / 0.55), medio + (abajo - medio) * ((k - 0.55) / 0.45))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    r = random.Random(5)
    for _ in range(int(70 * W / 1600)):                                                    # las estrellas
        x, yy = r.randrange(W), r.randrange(max(1, int(horizonte * 0.7)))
        g = max(1, int(W / 1600 * r.choice((1, 1, 2))))
        col[yy:yy + g, x:x + g] = np.array((0.7, 0.8, 0.9)) * r.uniform(0.4, 0.9)
    lado = int(H * 0.09)                                                                    # la luna
    lx, ly = int(W * luna_x), int(min(horizonte * 0.35, H * 0.22))
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - lx) / W, (yy - ly) / H * 0.62)
    col += np.array(S['sol'])[None, None, :] * (np.exp(-(d / 0.09) ** 2) * 0.22)[..., None]
    celda = max(1, lado // 8)
    for j in range(8):
        for i in range(8):
            tono = 0.92 if (i * 3 + j * 5) % 7 not in (0, 3) else 0.74
            if (i, j) in ((2, 2), (5, 4), (3, 5), (6, 1)):
                tono = 0.66
            col[ly - lado // 2 + j * celda: ly - lado // 2 + (j + 1) * celda,
                lx - lado // 2 + i * celda: lx - lado // 2 + (i + 1) * celda] = np.array((0.86, 0.9, 0.95)) * tono
    return np.clip(col, 0, 1)


def motas(img, n, semilla, color):
    """Las luciernagas del pantano, con su halo."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(H * 0.3, H * 0.95)
        g = max(1, int(r.choice((1, 2, 2)) * W / 1600))
        d.rectangle((x, y, x + g, y + g), fill=(*color, r.randint(170, 250)))
    glow = capa.filter(ImageFilter.GaussianBlur(5))
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
        qs, gel, info = sl.slime(cual)
        P = np.array([p for q in qs + gel for p in q[0]])
        MODELOS[cual] = (qs, gel, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras, a la escala de un mob: 'heroe' (de cuerpo entero, de tres cuartos y bajo), 'cabeza' (la cara, de
    cerca) y 'cartel' (de cerca y desde abajo)."""
    qs, gel, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    alto = max(h, (hi[0] - lo[0]) * 0.7)
    c = np.asarray(info['cabeza'], float)
    if vista == 'heroe':
        obj = np.array((0.0, h * 0.45, 0.2))
        ojo = obj + np.array((0.42, 0.0, 0.9)) * alto * 2.0
        ojo[1] = 1.2
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        ojo = c + np.array((0.9, -0.2, 2.6))
        return tuple(ojo), tuple(c + np.array((0.0, -0.35, -0.4))), 56
    obj = np.array((0.0, h * 0.55, 0.3))
    ojo = obj + np.array((0.38, 0.0, 0.92)) * alto * 1.35
    ojo[1] = 0.45
    return tuple(ojo), tuple(obj), 66


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: la cienaga; el slime, con la luz de su nucleo; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    qs, gel, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    suelo(lz, cam, niebla, S)
    bioma(lz, cam, niebla, S, libre=lambda x, z: lo[0] - 3 < x < hi[0] + 3 and lo[2] - 3 < z < hi[2] + 3
          or abs(x - ojo[0]) < 4 and abs(z - ojo[2]) < 4)
    neo = _c(info['luz'])
    luces = S['luces'] + [(tuple(p) + (2.0,), neo, 0.9, 'punto') for p in info['luces'][:1]]
    z0 = lz.z.copy()
    sl.dibujar(lz, cam, qs, gel, luces, S['amb'], niebla, transl=info['transl'], brilla=info['brilla'])
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe', 50), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 25), 'cabeza_' + cual)


def cartel(cual):
    """La presentacion del cartel: de cerca y desde abajo, con la luna."""
    guardar(escena(cual, 'cartel', 35, brillo=1.15), 'cartel_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos, con la misma luz, el Slime de vanilla y un jugador al lado, en la cienaga."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 30, 80)
    cam = vr.Camara((-1.0, 2.4, 21.0), (-1.0, 1.4, 0.0), 32, W * SS, H * SS)
    ISLA[0] = lambda x, z: abs(x) < 14 and -5 < z < 5.5 or math.hypot(x, z) < 6.5
    suelo(lz, cam, niebla, S)
    bioma(lz, cam, niebla, S, semilla=8, libre=lambda x, z: abs(x) < 13 and -5 < z < 18)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('V', -11.0), ('A', -4.6), ('B', 1.2), ('C', 7.2)):
        if cual == 'V':
            qs, gel = sl.vanilla_a_escala()
            info = {'transl': 0.55, 'brilla': False}
        else:
            qs, gel, info, P = modelo(cual)
        qs, gel = qm.transformar(qs, vr.T(x, 0, 0)), qm.transformar(gel, vr.T(x, 0, 0))
        z0 = lz.z.copy()
        sl.dibujar(lz, cam, qs, gel, S['luces'], S['amb'], niebla, transl=info['transl'], brilla=info['brilla'])
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-8.4, 1.6, 180)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=40), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por slime. Tragón: la gelatina, el nucleo, el ojo, el diente, la
    garganta y el hueso. Erizo: la gelatina, el nucleo, el ojo, la boca, el hierro y el escudo. Fundido: la gelatina, el
    nucleo, el ojo, la boca, el acido y el charco."""
    W = 1240
    A, B, C = (sl.pintores(sl.VARIANTES[c]) for c in 'ABC')
    filas = [[(A['gel'], 'frente', 30, 26), (A['nucleo'], 'frente', 12, 10), (A['ojo_der'], 'frente', 6, 4),
              (A['diente'], 'frente', 2, 5), (A['garganta'], 'frente', 26, 6), (A['hueso'], 'der', 1, 9)],
             [(B['gel'], 'frente', 30, 26), (B['nucleo'], 'frente', 12, 11), (B['ojo_der'], 'frente', 6, 4),
              (B['boca'], 'frente', 18, 6), (B['hierro'], 'der', 3, 14), (B['escudo'], 'frente', 9, 11)],
             [(C['gel'], 'frente', 30, 26), (C['nucleo'], 'frente', 11, 10), (C['ojo_der'], 'frente', 6, 4),
              (C['boca'], 'frente', 15, 5), (C['acido'], 'frente', 6, 6), (C['charco'], 'arriba', 16, 16)]]
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (18, 22, 20))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (40, 46, 44, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 192
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(66, 76, 72))
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

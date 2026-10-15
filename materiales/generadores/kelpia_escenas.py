"""
Renders de Kelpia (14-10-2026). La aprobada es la Acechadora (la C): sus escenas son heroe_C, cabeza_C, cartel_C,
escala_C y materiales_C. Las demas son de la primera ficha, con los dos caballos descartados.

Sus tres formas en la orilla de un lago de noche (el agua negra con las ondas, los
juncos, las piedras mojadas y, al otro lado, los montes), con la luz de su neon (las fauces alumbran); su cartel (de
cerca y desde abajo); la cabeza (desde abajo, para mirar dentro de las fauces); las tres juntas con un jugador; y la
lamina de materiales.

Las fotos salen sin letras y con el contorno blanco alrededor de ella.

Uso: python kelpia_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import kelpia_modelo as am

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
    """La misma orilla para las tres, con la luna fria; el cielo y la niebla toman el color de su neon."""
    neo = _c(am.VARIANTES[v]['neon'][1])
    return dict(
        luces=[((-0.5, 0.8, 0.7), (0.7, 0.76, 0.9), 0.85, 'llave'), ((0.3, 0.5, -1.0), neo, 1.0, 'contra'),
               ((0.0, -0.5, 1.0), neo, 0.35, 'llave')],
        amb=(0.2, 0.21, 0.25), niebla=tuple(0.04 + 0.1 * c for c in neo), niebla_d=(60, 260),
        cielo=((0.015, 0.02, 0.04), tuple(0.04 + 0.14 * c for c in neo), tuple(0.08 + 0.28 * c for c in neo)),
        motas=tuple(int(255 * (0.6 + 0.4 * c)) for c in neo),
    )


# ----------------------------------------------------------------------
#  La orilla: la tierra, el agua, los juncos, las piedras y los montes
# ----------------------------------------------------------------------
TIERRA = _r('0b0c0b', '111311', '171a17', '1e221e', '262b26')
qm._reg('suelo_kel', qm._suelo_grande(131, TIERRA, None, grietas=False))
AGUA = _r('05080c', '0a1018', '121c28', '22344a', '3a5470')


def _agua(semilla):
    """El agua del lago (128 x 128 = 4 bloques): casi negra, con las ondas de traves en rayas cortas."""
    rng = np.random.default_rng(semilla)
    n = 128
    idx = np.full((n, n), 1)
    for y in range(0, n, 3):
        for _ in range(rng.integers(1, 5)):
            x0, L = int(rng.integers(0, n)), int(rng.integers(6, 22))
            v = 2 if rng.random() < 0.75 else 3
            for x in range(x0, x0 + L):
                idx[y, x % n] = v
            if v == 3 and rng.random() < 0.5:
                idx[y, (x0 + L // 2) % n] = 4
    t = np.zeros((n, n, 4), np.uint8)
    for i in range(5):
        t[idx == i] = (*AGUA[i], 255)
    return t


qm._reg('agua_kel', _agua(17))


def costa(x, z):
    """Cuanto se mete en el agua un punto: el agua queda detras del monstruo, mirandolo desde la camara."""
    u = (x * 0.6 + z * 0.8)
    return u < -30.0 + 4.0 * math.sin(x * 0.07) + 3.0 * math.sin(z * 0.11)


def p_roca(tw, th, cara, s):
    """La piedra mojada de la orilla, con el musgo arriba."""
    idx = sm._manchas(tw, th, s, celda=7.0, umbral=0.62, alto=0.85)
    idx = np.array([1, 2, 2, 3, 3])[idx]
    if cara == 'arriba':
        return bm._imagen(sm._bisel(idx), _r('0c140c', '142014', '1c2c1a', '263a22', '30482a')), None
    return bm._imagen(sm._bisel(idx), _r('0a0b0e', '121418', '1a1d22', '24282e', '30343a')), None


def p_junco(tw, th, cara, s):
    """El junco: verde oscuro, mas claro hacia la punta, con un nudo cada poco."""
    ys = np.arange(th)[:, None] + np.zeros((1, tw), int)
    idx = np.where(ys < th * 0.25, 3, np.where(ys < th * 0.6, 2, 1))
    idx = np.where(ys % 11 == 5, idx - 1, idx)
    return bm._imagen(np.clip(idx, 0, 4), _r('0a1006', '121a0a', '1c2810', '283a16', '384e1e')), None


def p_monte(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=10.0, umbral=0.6, alto=0.85)
    idx = np.array([1, 1, 2, 2, 3])[idx]
    return bm._imagen(idx, _r('06080a', '0a0d10', '0e1216', '14191e', '1a2026')), None


for _f in (p_roca, p_junco, p_monte):
    _f.__name__ = 'kel_' + _f.__name__


def suelo(lz, cam, niebla, S, ext=280, paso=32, cerca=56, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        mat = 'agua_kel' if costa(gx + p / 2, gz + p / 2) else 'suelo_kel'
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], mat))

    cx, cz = cam.ojo[0], cam.ojo[2]
    for gx in range(-ext, ext, paso):
        for gz in range(-ext, ext, paso):
            cerca_cam = abs(gx + paso / 2 - cx) < cerca and abs(gz + paso / 2 - cz) < cerca
            cerca_costa = abs((gx + paso / 2) * 0.6 + (gz + paso / 2) * 0.8 + 30.0) < 36.0 and abs(gx) < 120 and abs(gz) < 120
            if cerca_cam or cerca_costa:
                for a in range(gx, gx + paso, paso_cerca):
                    for b in range(gz, gz + paso, paso_cerca):
                        baldosa(a, b, paso_cerca)
            else:
                baldosa(gx, gz, paso)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def orilla(lz, cam, niebla, S, semilla=6):
    """La orilla del lago: piedras mojadas y matas de juncos por la tierra (sin nada entre la camara y ella) y, al
    otro lado del agua, los montes en escalones."""
    r = random.Random(semilla)
    qs = []
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    for k in range(34):                                                 # las piedras y los juncos
        a = r.uniform(0, TAU)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.75:
            continue
        rr = r.uniform(24, 62)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if costa(x, z):
            continue
        if k % 2 == 0:
            w, h = r.uniform(2.0, 5.0), r.uniform(1.0, 2.8)
            M = vr.T(x, -0.2, z) @ vr.Ry(r.uniform(0, 3)) @ vr.Rz(r.uniform(-0.2, 0.2))
            bm.cubo(qs, M, -w / 2, 0, -w / 2, w, h, w * 0.8, p_roca, semilla=k)
            bm.cubo(qs, M, -w * 0.35, h * 0.9, -w * 0.3, w * 0.7, h * 0.4, w * 0.55, p_roca, semilla=k + 1)
        else:
            for j in range(r.randint(5, 9)):
                h = r.uniform(2.5, 6.0)
                g = r.uniform(0.25, 0.4)
                M = vr.T(x + r.uniform(-1.6, 1.6), 0, z + r.uniform(-1.6, 1.6)) @ vr.Ry(r.uniform(0, 3)) @ \
                    vr.Rz(r.uniform(-0.25, 0.25)) @ vr.Rx(r.uniform(-0.2, 0.2))
                bm.cubo(qs, M, -g, 0, -g, 2 * g, h, 2 * g, p_junco, semilla=j)
    lejos = hacia_camara + math.pi                                      # los montes, al otro lado del agua
    for k in range(11):                                                 # cada monte, en gradas que se estrechan
        a = lejos + r.uniform(-1.2, 1.2)
        rr = r.uniform(180, 250)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w, alto = r.uniform(50, 90), r.uniform(14, 34)
        giro = r.uniform(0, 3)
        n = 6
        for j in range(n):
            f = 1.0 - j / n * 0.85
            M = vr.T(x + r.uniform(-3, 3), 0, z + r.uniform(-3, 3)) @ vr.Ry(giro)
            bm.cubo(qs, M, -w * f / 2, 0, -w * f * 0.3, w * f, alto * (j + 1) / n, w * f * 0.6, p_monte, semilla=k + j)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S):
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    r = random.Random(7)
    for _ in range(int(W * H / 5000)):
        x, yv = r.randint(0, W - 1), r.randint(0, max(1, int(horizonte * 0.7)))
        col[yv, x] = np.clip(col[yv, x] + r.uniform(0.1, 0.35), 0, 1)
    return np.clip(col, 0, 1)


def motas(img, n, semilla, color):
    """Gotas del color del neon que flotan despacio."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(H * 0.1, H)
        g = max(1, int(r.choice((1, 1, 2, 2, 3)) * W / 1600))
        d.rectangle((x, y, x + g, y + g), fill=(*color, r.randint(120, 220)))
    glow = capa.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), glow), capa)


def revelar(lz, cam, W, H, S, n_motas=150, semilla=3, fuerza_vineta=0.45, brillo=0.9):
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
        qs, info = am.kelpia(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras, segun lo que mide cada forma: 'heroe' (de cuerpo entero, plano bajo y de tres cuartos), 'cabeza'
    (desde abajo y de cerca, para mirar dentro de las fauces) y 'cartel' (de cerca y desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    centro = (lo + hi) / 2
    b = np.asarray(info['boca'], float)
    if vista == 'heroe':
        alto = max(h, max(hi[0] - lo[0], hi[2] - lo[2]) * 0.62)
        d = alto * 0.5 / math.tan(25 * D) * 1.5
        obj = np.array((centro[0], h * 0.45, centro[2]))
        v = np.array((0.62, -0.08, 0.78))
        ojo = obj + v / np.linalg.norm(v) * d
        ojo[1] = max(ojo[1], 3.0)
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        ojo = b + np.array((12.0, -4.0, 12.0))
        ojo[1] = max(ojo[1], 2.5)                                                # nunca por debajo del suelo
        return tuple(ojo), tuple(b + np.array((0.0, 1.0, -3.0))), 54
    alto = max(h, max(hi[0] - lo[0], hi[2] - lo[2]) * 0.62)
    obj = np.array((centro[0], h * 0.6, centro[2] + 2.0))
    v = np.array((0.72, 0.0, 0.7)) / np.linalg.norm((0.72, 0.0, 0.7))
    ojo = obj + v * alto * 1.05
    ojo[1] = 3.0
    return tuple(ojo), tuple(obj), 64


# el cartel de cada una con el cielo y la luz de su neon: (cielo, niebla, ambiente, luz de frente)
CARTEL_LUZ = {
    'A': (((0.005, 0.04, 0.03), (0.03, 0.28, 0.2), (0.08, 0.6, 0.44)), (0.02, 0.17, 0.12), (0.24, 0.31, 0.29), (0.84, 1.0, 0.94)),
    'B': (((0.05, 0.005, 0.01), (0.34, 0.03, 0.07), (0.72, 0.08, 0.14)), (0.2, 0.02, 0.04), (0.31, 0.22, 0.24), (1.0, 0.84, 0.86)),
    'C': (((0.05, 0.03, 0.005), (0.36, 0.22, 0.03), (0.74, 0.46, 0.08)), (0.22, 0.13, 0.02), (0.31, 0.28, 0.22), (1.0, 0.92, 0.78)),
}


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: la orilla y el lago; Kelpia, con la luz de sus fauces; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    orilla(lz, cam, niebla, S)
    qs, info, P = modelo(cual)
    neo = _c(am.VARIANTES[cual]['neon'][1])
    luces = S['luces'] + [(tuple(p) + (9.0,), neo, 0.9, 'punto') for p in info['luces'][:3]]
    z0 = lz.z.copy()
    am.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe', 150), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 90), 'cabeza_' + cual)


def cartel(cual):
    """La presentacion del cartel: de cerca y desde abajo, con el cielo y la luz de su neon."""
    cielo_, niebla_, amb_, llave = CARTEL_LUZ[cual]
    S = sitio(cual)
    S.update(cielo=cielo_, niebla=niebla_, amb=amb_, luces=[((-0.6, 0.35, 0.8), llave, 0.95, 'llave')] + S['luces'][1:])
    guardar(escena(cual, 'cartel', 60, brillo=1.25, S=S), 'cartel_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Las tres formas juntas (o una sola, en 'escala_C'), con la misma luz neutra y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = dict(luces=[((-0.4, 0.8, 0.8), (0.82, 0.82, 0.9), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.9, 0.85, 1.0), 0.8, 'contra')],
             amb=(0.22, 0.21, 0.26), niebla=(0.05, 0.06, 0.09), niebla_d=(260, 420),
             cielo=((0.01, 0.012, 0.03), (0.05, 0.06, 0.1), (0.14, 0.15, 0.22)), motas=(230, 230, 255))
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    cerca = len(formas) == 1
    cam = vr.Camara((0.0, 12.0, 120.0) if cerca else (0.0, 16.0, 210.0), (0.0, 10.0 if cerca else 13.0, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=320, paso=32, cerca=40)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in ((('C', 0.0),) if cerca else (('A', -40.0), ('B', 0.0), ('C', 40.0))):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(55 * D))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    j = (16.0, 22.0) if cerca else (18.0, 30.0)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(j[0], j[1], 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por forma (la Kelpia, el Hipocampo y la Acechadora) y, de
    izquierda a derecha, la piel, la escama, la cinta de alga, la aleta, el casco, el ojo, el paladar, el suelo de la
    boca, los dientes y el nucleo. La de la Acechadora sola ('materiales_C') cambia la escama y la aleta, que no
    tiene, por el hueso y la vejiga."""
    W = 1800
    filas = []
    for c in formas:
        P = am.pintores(am.VARIANTES[c])
        if formas == 'C':
            filas.append([(P['piel'], 'der', 32, 32), (P['hueso'], 'der', 32, 32), (P['alga'], 'frente', 16, 32),
                          (P['luz'], 'frente', 12, 12), (P['casco'], 'frente', 16, 16), (P['ojo'], 'frente', 12, 12),
                          (P['fauces'], 'abajo', 16, 24), (P['boca'], 'arriba', 16, 24), (P['dientes_arriba'], 'frente', 24, 10),
                          (P['nucleo'], 'frente', 24, 24)])
            continue
        filas.append([(P['piel'], 'der', 32, 32), (P['escama'], 'der', 32, 32), (P['alga'], 'frente', 16, 32),
                      (P['aleta'], 'frente', 24, 16), (P['casco'], 'frente', 16, 16), (P['ojo'], 'frente', 12, 12),
                      (P['fauces'], 'abajo', 16, 24), (P['boca'], 'arriba', 16, 24), (P['dientes_arriba'], 'frente', 24, 10),
                      (P['nucleo'], 'frente', 24, 24)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (16, 15, 20))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (40, 36, 46, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 174
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(70, 64, 80))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales, 'materiales_C': lambda: materiales('C', 'materiales_C'),
                'escala_C': lambda: tres('C', 'escala_C')})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

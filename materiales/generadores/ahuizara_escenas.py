"""
Renders de Ahuizara (15-10-2026): sus tres tipos en las chinampas de noche (los canales de agua negra entre las
parcelas, las flores de cempasuchil, los juncos, los ahuejotes y, al fondo, los volcanes), con la luz de su neon (las
fauces alumbran); su cartel (de cerca y desde abajo); la cabeza (de cerca, para mirar dentro de las fauces); los tres
juntos con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco alrededor de ella.

Uso: python ahuizara_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import ahuizara_modelo as am

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
    """Las mismas chinampas para los tres, con la luna; el cielo y la niebla toman el color de su neon."""
    neo = _c(am.VARIANTES[v]['neon'][1])
    return dict(
        luces=[((-0.5, 0.8, 0.7), (0.7, 0.76, 0.9), 0.85, 'llave'), ((0.3, 0.5, -1.0), neo, 1.0, 'contra'),
               ((0.0, -0.5, 1.0), neo, 0.35, 'llave')],
        amb=(0.2, 0.21, 0.25), niebla=tuple(0.04 + 0.1 * c for c in neo), niebla_d=(60, 260),
        cielo=((0.015, 0.02, 0.04), tuple(0.04 + 0.14 * c for c in neo), tuple(0.08 + 0.28 * c for c in neo)),
        motas=tuple(int(255 * (0.6 + 0.4 * c)) for c in neo),
    )


# ----------------------------------------------------------------------
#  Las chinampas: la tierra, los canales, las flores, los juncos, los ahuejotes y los volcanes
# ----------------------------------------------------------------------
TIERRA = _r('0a0c08', '10140c', '161c10', '1e2616', '28321c')
qm._reg('suelo_ahu', qm._suelo_grande(149, TIERRA, None, grietas=False))
AGUA = _r('05080c', '0a1018', '121c28', '22344a', '3a5470')


def _agua(semilla):
    """El agua de los canales (128 x 128 = 4 bloques): casi negra, con las ondas de traves en rayas cortas."""
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


qm._reg('agua_ahu', _agua(23))
PASO_CH, CANAL = 40.0, 8.0


def canal(x, z):
    """Si un punto cae en un canal: las chinampas son parcelas cuadradas con canales entre ellas; la del monstruo, mas
    grande, va en medio."""
    if abs(x) < 26.0 and abs(z) < 30.0:
        return False
    return ((x + 26.0) % PASO_CH) < CANAL or ((z + 30.0) % PASO_CH) < CANAL


def p_flor(tw, th, cara, s):
    """El cempasuchil: la bola de petalos naranjas en capas, mas clara arriba."""
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs + ys) % 3 == 0, 2, 3)
    if cara == 'arriba':
        idx = np.where((xs + ys) % 3 == 0, 3, 4)
    return bm._imagen(idx, _r('3a1404', '6a2a06', '9a4a0a', 'd2740e', 'f2a024')), None


def p_hoja(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(xs % 3 == 0, 1, 2)
    return bm._imagen(idx, _r('0a1206', '121e0a', '1c2c10', '283c16', '344e1e')), None


def p_junco(tw, th, cara, s):
    """El junco: verde oscuro, mas claro hacia la punta, con un nudo cada poco."""
    ys = np.arange(th)[:, None] + np.zeros((1, tw), int)
    idx = np.where(ys < th * 0.25, 3, np.where(ys < th * 0.6, 2, 1))
    idx = np.where(ys % 11 == 5, idx - 1, idx)
    return bm._imagen(np.clip(idx, 0, 4), _r('0a1006', '121a0a', '1c2810', '283a16', '384e1e')), None


def p_corteza(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(xs % 3 == 0, 1, 2)
    return bm._imagen(idx, _r('0c0a08', '16120e', '201a14', '2c241c', '3a3024')), None


def p_copa(tw, th, cara, s):
    """La copa del ahuejote: alta y estrecha, de hojas pequenas."""
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs // 2 + ys // 3) % 3 == 0, 1, 2)
    return bm._imagen(idx, _r('060a06', '0c120a', '121a0e', '1a2414', '22301a')), None


def p_monte(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=10.0, umbral=0.6, alto=0.85)
    idx = np.array([1, 1, 2, 2, 3])[idx]
    return bm._imagen(idx, _r('06080a', '0a0d10', '0e1216', '14191e', '1a2026')), None


for _f in (p_flor, p_hoja, p_junco, p_corteza, p_copa, p_monte):
    _f.__name__ = 'ahu_' + _f.__name__


def suelo(lz, cam, niebla, S, ext=280, paso=8):
    qs = []
    for gx in range(-ext, ext, paso):
        for gz in range(-ext, ext, paso):
            p = paso
            k = p / 4
            P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
            mat = 'agua_ahu' if canal(gx + p / 2, gz + p / 2) else 'suelo_ahu'
            y = -0.6 if mat == 'agua_ahu' else 0.0
            qs.append(([np.array((q[0], y, q[2]), float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], mat))
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def orilla(lz, cam, niebla, S, semilla=6):
    """Las chinampas: matas de cempasuchil y de juncos por las parcelas, ahuejotes en los bordes de los canales (sin
    nada entre la camara y ella) y, al fondo, los volcanes en gradas."""
    r = random.Random(semilla)
    qs = []
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    for k in range(70):
        a = r.uniform(0, TAU)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.7:
            continue
        rr = r.uniform(24, 90)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if canal(x, z):
            continue
        tipo = k % 3
        if tipo == 0:                                                   # una mata de cempasuchil
            for j in range(r.randint(4, 8)):
                fx, fz = x + r.uniform(-2.5, 2.5), z + r.uniform(-2.5, 2.5)
                h = r.uniform(0.8, 1.8)
                M = vr.T(fx, 0.0, fz)
                bm.cubo(qs, M, -0.15, 0.0, -0.15, 0.3, h, 0.3, p_hoja, semilla=j)
                g = r.uniform(0.45, 0.7)
                bm.cubo(qs, M, -g, h, -g, 2 * g, g * 1.4, 2 * g, p_flor, semilla=j)
        elif tipo == 1:                                                 # juncos
            for j in range(r.randint(5, 9)):
                h = r.uniform(2.5, 5.5)
                g = r.uniform(0.25, 0.4)
                M = vr.T(x + r.uniform(-1.6, 1.6), 0, z + r.uniform(-1.6, 1.6)) @ vr.Ry(r.uniform(0, 3)) @ vr.Rz(r.uniform(-0.25, 0.25))
                bm.cubo(qs, M, -g, 0, -g, 2 * g, h, 2 * g, p_junco, semilla=j)
        elif rr > 34:                                                   # un ahuejote: tronco fino y copa alta y estrecha
            h = r.uniform(14, 22)
            M = vr.T(x, 0.0, z)
            bm.cubo(qs, M, -0.6, 0.0, -0.6, 1.2, h * 0.5, 1.2, p_corteza, semilla=k)
            for j in range(4):
                f = 1.0 - j * 0.2
                bm.cubo(qs, M, -2.2 * f, h * (0.35 + j * 0.16), -2.2 * f, 4.4 * f, h * 0.2, 4.4 * f, p_copa, semilla=k + j)
    lejos = hacia_camara + math.pi                                      # los volcanes
    for k in range(7):
        a = lejos + r.uniform(-1.0, 1.0)
        rr = r.uniform(200, 260)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w, alto = r.uniform(70, 110), r.uniform(30, 55)
        giro = r.uniform(0, 3)
        n = 7
        for j in range(n):
            f = 1.0 - j / n * 0.82
            M = vr.T(x, 0, z) @ vr.Ry(giro)
            bm.cubo(qs, M, -w * f / 2, 0, -w * f * 0.35, w * f, alto * (j + 1) / n, w * f * 0.7, p_monte, semilla=k + j)
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
        qs, info = am.ahuizara(cual)
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
        ojo = b + np.array((10.0, -2.0, 15.0))
        ojo[1] = max(ojo[1], 2.5)                                                # nunca por debajo del suelo
        return tuple(ojo), tuple(b + np.array((0.0, 1.0, -3.0))), 54
    alto = max(h, max(hi[0] - lo[0], hi[2] - lo[2]) * 0.62)
    obj = np.array((centro[0], h * 0.6, centro[2] + 2.0))
    v = np.array((0.72, 0.0, 0.7)) / np.linalg.norm((0.72, 0.0, 0.7))
    ojo = obj + v * alto * 1.05
    ojo[1] = 3.0
    return tuple(ojo), tuple(obj), 64


# el cartel de cada tipo con el cielo y la luz de su neon: (cielo, niebla, ambiente, luz de frente)
CARTEL_LUZ = {
    'A': (((0.005, 0.04, 0.04), (0.03, 0.27, 0.25), (0.08, 0.58, 0.54)), (0.02, 0.16, 0.15), (0.24, 0.31, 0.3), (0.84, 1.0, 0.98)),
    'B': (((0.05, 0.005, 0.025), (0.34, 0.03, 0.17), (0.72, 0.08, 0.36)), (0.2, 0.02, 0.1), (0.31, 0.22, 0.27), (1.0, 0.84, 0.92)),
    'C': (((0.05, 0.02, 0.005), (0.36, 0.17, 0.03), (0.76, 0.38, 0.08)), (0.22, 0.1, 0.02), (0.31, 0.27, 0.22), (1.0, 0.9, 0.78)),
}


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: las chinampas; Ahuizara, con la luz de sus fauces; el contorno blanco; y sin letras."""
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
    suelo(lz, cam, niebla, S, ext=320, paso=16)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in ((('C', 0.0),) if cerca else (('A', -36.0), ('B', 0.0), ('C', 36.0))):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(25 * D))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    j = (16.0, 22.0) if cerca else (18.0, 30.0)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(j[0], j[1], 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo (la Mano, la Garra y la Gemela) y, de izquierda a
    derecha, el pelo mojado, la palma, la garra, el hueso de los nudillos, el ojo, el paladar, el suelo de la boca, los
    dientes y el nucleo."""
    W = 1800
    filas = []
    for c in formas:
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['piel'], 'der', 32, 32), (P['palma'], 'der', 32, 32), (P['casco'], 'frente', 16, 16),
                      (P['hueso'], 'frente', 16, 16), (P['ojo'], 'frente', 12, 12), (P['fauces'], 'abajo', 16, 24),
                      (P['boca'], 'arriba', 16, 24), (P['dientes_arriba'], 'frente', 24, 10), (P['nucleo'], 'frente', 24, 24)])
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
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

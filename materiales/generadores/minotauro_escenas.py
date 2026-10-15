"""
Renders del Minotauro (13-10-2026): sus tres formas, cada una en el claro de un laberinto en ruinas, de
noche, con columnas griegas rotas detras y con la luz de su neon (la boca alumbra); su cartel (de cerca y
desde abajo); la cabeza (desde abajo, para mirar dentro de las fauces); las tres juntas con un jugador; y
la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco alrededor de el, cuernos y armas incluidos.

Uso: python minotauro_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import minotauro_modelo as am

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
    """El mismo claro para las tres; el cielo y la niebla toman el color de su neon."""
    neo = _c(am.VARIANTES[v]['neon'][1])
    return dict(
        luces=[((-0.5, 0.8, 0.7), (0.72, 0.7, 0.86), 0.8, 'llave'), ((0.3, 0.5, -1.0), neo, 1.0, 'contra'),
               ((0.0, -0.5, 1.0), neo, 0.35, 'llave')],
        amb=(0.2, 0.19, 0.24), niebla=tuple(0.05 + 0.12 * c for c in neo), niebla_d=(40, 150),
        cielo=((0.02, 0.015, 0.04), tuple(0.05 + 0.16 * c for c in neo), tuple(0.1 + 0.32 * c for c in neo)),
        motas=tuple(int(255 * (0.6 + 0.4 * c)) for c in neo),
    )


SUELO = _r('14100e', '1a1512', '201a16', '28201b', '302620')
qm._reg('suelo_min', qm._suelo_grande(93, SUELO, None, grietas=True))


def p_muro(tw, th, cara, s):
    """La piedra del laberinto: sillares en hiladas, con la junta oscura."""
    ys, xs = np.mgrid[0:th, 0:tw]
    fila = ys // 5
    idx = np.where((ys % 5) == 0, 1, 2)
    idx = np.where(((xs + (fila % 2) * 4) % 8) == 0, 1, idx)
    idx = np.where(((ys % 5) == 1) & (((xs + (fila % 2) * 4) % 8) == 1), 3, idx)
    return bm._imagen(sm._bisel(idx), _r('0e0c0c', '181414', '221c1a', '2c2522', '3a302c')), None


def p_columna(tw, th, cara, s):
    """El fuste de las columnas: estrias de arriba abajo."""
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs % 4) == 0, 1, np.where((xs % 4) == 2, 3, 2))
    return bm._imagen(sm._bisel(idx), _r('0c0a0c', '161214', '1e1a1c', '282224', '342c2e')), None


for _f in (p_muro, p_columna):
    _f.__name__ = 'min_' + _f.__name__


def suelo(lz, cam, niebla, S, ext=180, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_min'))

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


def laberinto(lz, cam, niebla, S, semilla=6):
    """El claro del laberinto: tramos de muro rotos en tres anillos a su alrededor (abiertos hacia la
    camara, como si se mirara por un pasillo), algun sillar caido y, al fondo, columnas griegas rotas."""
    r = random.Random(semilla)
    qs = []
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    for anillo, radio in enumerate((19.0, 28.0, 38.0)):
        n = 9 + 4 * anillo
        for k in range(n):
            a0 = k * TAU / n + r.uniform(-0.06, 0.06)
            a1 = a0 + TAU / n * r.uniform(0.5, 0.85)
            am_ = (a0 + a1) / 2
            delta = abs(((am_ - hacia_camara + math.pi) % TAU) - math.pi)
            if delta < 0.75 or r.random() < 0.22:                      # el pasillo hacia la camara y algun hueco
                continue
            p0 = np.array((math.cos(a0) * radio, 0.0, math.sin(a0) * radio))
            p1 = np.array((math.cos(a1) * radio, 0.0, math.sin(a1) * radio))
            L = float(np.linalg.norm(p1 - p0))
            M = vr.T(*p0) @ vr.Ry(-math.atan2(p1[2] - p0[2], p1[0] - p0[0]))
            alto = r.uniform(3.0, 5.2)
            corte = r.uniform(0.35, 0.75)
            bm.cubo(qs, M, 0.0, 0.0, -0.7, L * corte, alto, 1.4, p_muro, semilla=k)
            bm.cubo(qs, M, L * corte - 0.05, 0.0, -0.7, L * (1 - corte), alto * r.uniform(0.45, 0.8), 1.4, p_muro, semilla=k + 3)
            if r.random() < 0.4:                                        # un sillar caido al pie
                Mc = vr.T(*(p0 + (p1 - p0) * r.uniform(0.2, 0.8) + np.array((r.uniform(-2, 2), 0.0, r.uniform(-2, 2)))))
                bm.cubo(qs, Mc @ vr.Ry(r.uniform(0, 3)) @ vr.Rz(r.uniform(-0.3, 0.3)), -0.9, 0.0, -0.6, 1.8, 1.1, 1.2, p_muro, semilla=k + 5)
    for _ in range(10):                                                  # las columnas rotas, al fondo
        a = hacia_camara + math.pi + r.uniform(-1.2, 1.2)
        rr = r.uniform(52, 95)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        h = r.uniform(10, 26)
        g = r.uniform(1.4, 2.2)
        M = vr.T(x, 0, z)
        bm.cubo(qs, M, -g * 1.4, 0.0, -g * 1.4, g * 2.8, 1.2, g * 2.8, p_muro, semilla=1)              # la basa
        for kx, kz in ((1.0, 0.7), (0.7, 1.0)):
            bm.cubo(qs, M, -g * kx, 1.2, -g * kz, 2 * g * kx, h, 2 * g * kz, p_columna, semilla=2)
        if r.random() < 0.55:                                           # el capitel, si no esta rota
            bm.cubo(qs, M, -g * 1.5, 1.2 + h, -g * 1.5, g * 3.0, 1.4, g * 3.0, p_muro, semilla=3)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S):
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    r = random.Random(7)
    for _ in range(int(W * H / 6000)):
        x, yv = r.randint(0, W - 1), r.randint(0, max(1, int(horizonte * 0.7)))
        col[yv, x] = np.clip(col[yv, x] + r.uniform(0.1, 0.35), 0, 1)
    return np.clip(col, 0, 1)


def motas(img, n, semilla, color):
    """Ascuas del color del neon que suben despacio."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(H * 0.1, H)
        g = max(1, int(r.choice((1, 1, 2, 2, 3)) * W / 1600))
        d.rectangle((x, y, x + g, y + g * 2), fill=(*color, r.randint(120, 220)))
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
        qs, info = am.minotauro(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras, segun lo que mide cada forma: 'heroe' (de cuerpo entero, plano bajo), 'cabeza' (desde
    abajo y de cerca, para mirar dentro de las fauces) y 'cartel' (de cerca y desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    centro = (lo + hi) / 2
    b = np.asarray(info['boca'], float)
    if vista == 'heroe':
        alto = max(h, (hi[0] - lo[0]) * 0.72)
        d = alto * 0.5 / math.tan(25 * D) * (0.98 if cual == 'A' else 1.18)
        obj = np.array((centro[0], h * 0.5, centro[2]))
        ojo = obj + np.array((0.42, -0.12, 0.9)) / np.linalg.norm((0.42, -0.12, 0.9)) * d
        ojo[1] = max(ojo[1], 3.0)
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        return tuple(b + np.array((-8.5, -6.0, 19.0))), tuple(b + np.array((0.0, 2.0, -1.5))), 48
    alto = max(h, (hi[0] - lo[0]) * 0.8)
    obj = np.array((centro[0], h * 0.56, centro[2]))
    return (-0.32 * alto, 3.0, 0.82 * alto + centro[2]), tuple(obj), 64


# el cartel de cada uno con el cielo y la luz de su neon: (cielo, niebla, ambiente, luz de frente)
CARTEL_LUZ = {
    'A': (((0.05, 0.03, 0.01), (0.32, 0.17, 0.05), (0.66, 0.36, 0.1)), (0.2, 0.1, 0.03), (0.32, 0.27, 0.22), (1.0, 0.86, 0.66)),
    'B': (((0.01, 0.04, 0.035), (0.04, 0.2, 0.17), (0.1, 0.46, 0.38)), (0.03, 0.15, 0.12), (0.24, 0.3, 0.29), (0.8, 1.0, 0.94)),
    'C': (((0.05, 0.01, 0.015), (0.3, 0.04, 0.07), (0.6, 0.1, 0.14)), (0.2, 0.03, 0.05), (0.3, 0.22, 0.24), (1.0, 0.78, 0.8)),
}


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: el suelo y el laberinto; el minotauro, con la luz de su boca; el contorno blanco; y sin
    letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    laberinto(lz, cam, niebla, S)
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


def tres():
    """Las tres formas juntas, con la misma luz neutra y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = dict(luces=[((-0.4, 0.8, 0.8), (0.82, 0.82, 0.9), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.9, 0.85, 1.0), 0.8, 'contra')],
             amb=(0.22, 0.21, 0.26), niebla=(0.06, 0.05, 0.09), niebla_d=(200, 360),
             cielo=((0.01, 0.012, 0.03), (0.05, 0.05, 0.1), (0.16, 0.13, 0.22)), motas=(230, 230, 255))
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    cam = vr.Camara((0.0, 16.0, 196.0), (0.0, 19.0, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=280, paso=32, cerca=40)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -40.0), ('B', 0.0), ('C', 42.0)):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(-24 * D))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(16.0, 24.0, 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), 'tres')


def materiales():
    """La lamina de materiales, sin letras: una fila por forma (Asterion, el Calcotauro y el Bucentauro) y,
    de izquierda a derecha, la piel, el pelo, el cuerno, el metal (las placas encendidas en el Calcotauro),
    el cuero, el paladar, el suelo de la boca, los dientes y el nucleo."""
    W = 1600
    filas = []
    for c in 'ABC':
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['piel'], 'der', 24, 24), (P['pelaje'], 'der', 12, 32), (P['cuerno'], 'der', 32, 10),
                      (P['placa'] if c == 'B' else P['metal'], 'frente', 24, 16), (P['cuero'], 'frente', 8, 32),
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
            cx = 48 + k * 168
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(70, 64, 80))
    guardar(img, 'materiales')


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

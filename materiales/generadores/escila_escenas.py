"""
Renders de Escila (14-10-2026): sus tres formas, cada una en las rocas del estrecho de noche (las rocas y las
columnas de basalto), con la luz de su neon (las fauces de los perros alumbran); su cartel (de cerca y desde
abajo); las cabezas (desde abajo, para mirar dentro de las fauces); las tres juntas con un jugador; y la lamina de
materiales.

Las fotos salen sin letras y con el contorno blanco alrededor de ella, perros y tentaculos incluidos.

Uso: python escila_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import escila_modelo as am

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
    """La misma orilla para las tres; el cielo y la niebla toman el color de su neon."""
    neo = _c(am.VARIANTES[v]['neon'][1])
    return dict(
        luces=[((-0.5, 0.8, 0.7), (0.72, 0.7, 0.86), 0.8, 'llave'), ((0.3, 0.5, -1.0), neo, 1.0, 'contra'),
               ((0.0, -0.5, 1.0), neo, 0.35, 'llave')],
        amb=(0.2, 0.19, 0.24), niebla=tuple(0.05 + 0.12 * c for c in neo), niebla_d=(40, 150),
        cielo=((0.02, 0.015, 0.04), tuple(0.05 + 0.16 * c for c in neo), tuple(0.1 + 0.32 * c for c in neo)),
        motas=tuple(int(255 * (0.6 + 0.4 * c)) for c in neo),
    )


SUELO = _r('0c0b0d', '121115', '18171b', '1f1d22', '26242a')
qm._reg('suelo_esc', qm._suelo_grande(97, SUELO, None, grietas=False))


def p_roca(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=7.0, umbral=0.62, alto=0.85)
    idx = np.array([1, 2, 2, 3, 3])[idx]
    return bm._imagen(sm._bisel(idx), _r('0c0c0e', '161618', '201f22', '2c2a2e', '3a383c')), None


def p_basalto(tw, th, cara, s):
    """El basalto de las columnas: oscuro, con las juntas de traves cada pocos pixeles."""
    ys = np.arange(th)[:, None] + np.zeros((1, tw), int)
    idx = np.where((ys % 9) == 0, 1, np.where((ys % 9) == 1, 3, 2))
    return bm._imagen(sm._bisel(idx), _r('0a0a0c', '121216', '1a1a20', '24242c', '30303a')), None


for _f in (p_roca, p_basalto):
    _f.__name__ = 'cer_' + _f.__name__


def suelo(lz, cam, niebla, S, ext=180, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_esc'))

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


def orilla(lz, cam, niebla, S, semilla=6):
    """La orilla del Estigio: rocas sueltas alrededor y, al fondo, grupos de columnas de basalto de alturas
    distintas, alguna partida en el suelo (sin nada entre la camara y ella)."""
    r = random.Random(semilla)
    qs = []
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    for k in range(26):                                                 # las rocas
        a = r.uniform(0, TAU)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.7:
            continue
        rr = r.uniform(26, 60)
        w, h = r.uniform(2.0, 5.0), r.uniform(1.0, 3.2)
        M = vr.T(math.cos(a) * rr, -0.2, math.sin(a) * rr) @ vr.Ry(r.uniform(0, 3)) @ vr.Rz(r.uniform(-0.25, 0.25))
        bm.cubo(qs, M, -w / 2, 0, -w / 2, w, h, w * 0.8, p_roca, semilla=k)
        bm.cubo(qs, M, -w * 0.35, h * 0.9, -w * 0.3, w * 0.7, h * 0.4, w * 0.55, p_roca, semilla=k + 1)
    for k in range(9):                                                  # los grupos de columnas al fondo
        a = hacia_camara + math.pi + r.uniform(-1.4, 1.4)
        rr = r.uniform(62, 110)
        cx, cz = math.cos(a) * rr, math.sin(a) * rr
        for j in range(r.randint(3, 6)):
            x, z = cx + r.uniform(-5, 5), cz + r.uniform(-5, 5)
            h, g = r.uniform(5, 24), r.uniform(1.4, 2.4)
            M = vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 1.0))
            bm.cubo(qs, M, -g, 0, -g * 0.7, 2 * g, h, 1.4 * g, p_basalto, semilla=j)       # dos cajas cruzadas: seis lados
            bm.cubo(qs, M, -g * 0.7, 0, -g, 1.4 * g, h, 2 * g, p_basalto, semilla=j + 1)
            if r.random() < 0.3:                                        # un trozo partido en el suelo
                Mt = vr.T(x + r.uniform(2, 4), 0, z + r.uniform(-2, 2)) @ vr.Ry(r.uniform(0, 3)) @ vr.Rz(1.45)
                bm.cubo(qs, Mt, -g * 0.7, -g * 0.7, 0, 1.4 * g, 1.4 * g, r.uniform(3, 6), p_basalto, semilla=j + 2)
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
        qs, info = am.escila(cual)
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
        alto = max(h, max(hi[0] - lo[0], hi[2] - lo[2]) * 0.62)
        d = alto * 0.5 / math.tan(25 * D) * 1.35
        obj = np.array((centro[0], h * 0.45, centro[2]))
        ojo = obj + np.array((0.35, -0.1, 0.93)) / np.linalg.norm((0.35, -0.1, 0.93)) * d
        ojo[1] = max(ojo[1], 3.0)
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        return tuple(b + np.array((-12.0, -6.0, 24.0))), tuple(b + np.array((3.0, 4.0, -4.0))), 56
    alto = max(h, max(hi[0] - lo[0], hi[2] - lo[2]) * 0.62)
    obj = np.array((centro[0], h * 0.6, centro[2] + 2.0))
    return (-0.3 * alto, 3.0, 0.95 * alto + hi[2] * 0.4), tuple(obj), 64


# el cartel de cada uno con el cielo y la luz de su neon: (cielo, niebla, ambiente, luz de frente)
CARTEL_LUZ = {
    'A': (((0.005, 0.03, 0.03), (0.03, 0.22, 0.2), (0.08, 0.48, 0.42)), (0.02, 0.13, 0.12), (0.24, 0.3, 0.3), (0.84, 1.0, 0.96)),
    'B': (((0.05, 0.015, 0.01), (0.36, 0.08, 0.06), (0.74, 0.2, 0.14)), (0.22, 0.05, 0.04), (0.32, 0.25, 0.24), (1.0, 0.88, 0.84)),
    'C': (((0.05, 0.035, 0.005), (0.36, 0.25, 0.03), (0.74, 0.54, 0.08)), (0.22, 0.16, 0.02), (0.31, 0.29, 0.22), (1.0, 0.96, 0.78)),
}


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: el suelo y la orilla; Escila, con la luz de las fauces de sus perros; el contorno blanco; y sin letras."""
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


def tres():
    """Las tres formas juntas, con la misma luz neutra y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = dict(luces=[((-0.4, 0.8, 0.8), (0.82, 0.82, 0.9), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.9, 0.85, 1.0), 0.8, 'contra')],
             amb=(0.22, 0.21, 0.26), niebla=(0.06, 0.05, 0.09), niebla_d=(200, 360),
             cielo=((0.01, 0.012, 0.03), (0.05, 0.05, 0.1), (0.16, 0.13, 0.22)), motas=(230, 230, 255))
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    cam = vr.Camara((0.0, 18.0, 230.0), (0.0, 15.0, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=280, paso=32, cerca=40)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -52.0), ('B', 0.0), ('C', 52.0)):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(20 * D))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(22.0, 34.0, 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), 'tres')


def materiales():
    """La lamina de materiales, sin letras: una fila por forma (Escila, la de las Morenas y la Madre de los Perros)
    y, de izquierda a derecha, el corpino de escamas, la piel del monstruo, el tentaculo, la ventosa, la aleta, el
    coral, el paladar, los dientes y el nucleo."""
    W = 1600
    filas = []
    for c in 'ABC':
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['escama'], 'der', 16, 16), (P['mar'], 'der', 24, 24), (P['tentaculo'], 'der', 16, 28),
                      (P['ventosa'], 'frente', 12, 12), (P['aleta'], 'frente', 24, 16), (P['coral'], 'frente', 8, 24),
                      (P['fauces'], 'abajo', 16, 24), (P['dientes_arriba'], 'frente', 24, 10), (P['nucleo'], 'frente', 24, 24)])
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

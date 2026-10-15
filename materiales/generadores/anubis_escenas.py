"""
Renders de Anubis (14-10-2026): sus tres formas, cada una en una necropolis del desierto de noche (la arena, los
muros de arenisca rotos, las columnas de papiro, los obeliscos y una piramide al fondo), con la luz de su neon
(los ojos y lo que lleva alumbran); su cartel (de cerca y desde abajo); la cabeza (de cerca); las tres juntas con
un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco alrededor de el, orejas y armas incluidas.

Uso: python anubis_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import anubis_modelo as am

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
    """La misma necropolis para las tres; el cielo y la niebla toman el color de su neon."""
    neo = _c(am.VARIANTES[v]['neon'][1])
    return dict(
        luces=[((-0.5, 0.8, 0.7), (0.72, 0.7, 0.86), 0.8, 'llave'), ((0.3, 0.5, -1.0), neo, 1.0, 'contra'),
               ((0.0, -0.5, 1.0), neo, 0.35, 'llave')],
        amb=(0.2, 0.19, 0.24), niebla=tuple(0.05 + 0.12 * c for c in neo), niebla_d=(40, 150),
        cielo=((0.02, 0.015, 0.04), tuple(0.05 + 0.16 * c for c in neo), tuple(0.1 + 0.32 * c for c in neo)),
        motas=tuple(int(255 * (0.6 + 0.4 * c)) for c in neo),
    )


SUELO = _r('3a2a18', '46331e', '523c24', '5e452a', '6a4e30')
qm._reg('suelo_anu', qm._suelo_grande(93, SUELO, None, grietas=False))


def p_arenisca(tw, th, cara, s):
    """La arenisca de los muros y las columnas: sillares en hiladas, con la junta oscura y el canto claro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    fila = ys // 6
    x = (xs + (fila % 2) * 5) % 10
    idx = np.where((ys % 6) == 0, 1, np.where(x == 0, 1, np.where((ys % 6) == 1, 3, 2)))
    return bm._imagen(idx, _r('3a2814', '5a4024', '7a5a34', '9a7646', 'b8925c')), None


def p_fuste(tw, th, cara, s):
    """El fuste de las columnas: estrias verticales y, de trecho en trecho, una banda de color desvaido."""
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs % 4) == 0, 1, np.where((xs % 4) == 1, 3, 2))
    t = bm._imagen(idx, _r('3a2814', '5a4024', '7a5a34', '9a7646', 'b8925c'))
    banda = (ys % 24) < 3
    t[banda, :3] = (np.array((40, 70, 130)) * 0.8).astype(np.uint8)
    return t, None


def p_obelisco(tw, th, cara, s):
    """El obelisco: piedra lisa con una columna de signos grabados por el medio."""
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.full((th, tw), 2)
    c = tw // 2
    idx = np.where((abs(xs - c) <= 1) & ((ys % 5) < 3), 1, idx)
    return bm._imagen(idx, _r('3a2814', '5a4024', '7a5a34', '9a7646', 'b8925c')), None


for _f in (p_arenisca, p_fuste, p_obelisco):
    _f.__name__ = 'anu_' + _f.__name__


def suelo(lz, cam, niebla, S, ext=220, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_anu'))

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


def necropolis(lz, cam, niebla, S, semilla=6):
    """La necropolis en el desierto: tramos de muro de arenisca rotos alrededor (abiertos hacia la camara),
    sillares caidos, columnas con el capitel de papiro, dos obeliscos y, muy al fondo, una piramide."""
    r = random.Random(semilla)
    qs = []
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    for anillo, radio in enumerate((24.0, 36.0)):
        n = 10 + 4 * anillo
        for k in range(n):
            a0 = k * TAU / n + r.uniform(-0.06, 0.06)
            a1 = a0 + TAU / n * r.uniform(0.45, 0.75)
            am_ = (a0 + a1) / 2
            delta = abs(((am_ - hacia_camara + math.pi) % TAU) - math.pi)
            if delta < 0.8 or r.random() < 0.3:
                continue
            p0 = np.array((math.cos(a0) * radio, 0.0, math.sin(a0) * radio))
            p1 = np.array((math.cos(a1) * radio, 0.0, math.sin(a1) * radio))
            L = float(np.linalg.norm(p1 - p0))
            M = vr.T(*p0) @ vr.Ry(-math.atan2(p1[2] - p0[2], p1[0] - p0[0]))
            alto = r.uniform(2.5, 4.6)
            corte = r.uniform(0.35, 0.75)
            bm.cubo(qs, M, 0.0, 0.0, -0.8, L * corte, alto, 1.6, p_arenisca, semilla=k)
            bm.cubo(qs, M, L * corte - 0.05, 0.0, -0.8, L * (1 - corte), alto * r.uniform(0.4, 0.75), 1.6, p_arenisca, semilla=k + 3)
            if r.random() < 0.45:
                Mc = vr.T(*(p0 + (p1 - p0) * r.uniform(0.2, 0.8) + np.array((r.uniform(-2, 2), 0.0, r.uniform(-2, 2)))))
                bm.cubo(qs, Mc @ vr.Ry(r.uniform(0, 3)) @ vr.Rz(r.uniform(-0.3, 0.3)), -1.0, 0.0, -0.7, 2.0, 1.2, 1.4, p_arenisca, semilla=k + 5)
    for _ in range(9):                                                   # las columnas de papiro, al fondo
        a = hacia_camara + math.pi + r.uniform(-1.2, 1.2)
        rr = r.uniform(50, 90)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        h, g = r.uniform(10, 22), r.uniform(1.6, 2.3)
        M = vr.T(x, 0, z)
        bm.cubo(qs, M, -g * 1.5, 0.0, -g * 1.5, g * 3.0, 1.0, g * 3.0, p_arenisca, semilla=1)
        for kx, kz in ((1.0, 0.72), (0.72, 1.0)):
            bm.cubo(qs, M, -g * kx, 1.0, -g * kz, 2 * g * kx, h, 2 * g * kz, p_fuste, semilla=2)
        if r.random() < 0.6:                                            # el capitel de papiro, abierto
            for j, w in enumerate((1.2, 1.6, 2.0)):
                bm.cubo(qs, M, -g * w, 1.0 + h + j * 0.9, -g * w, g * 2 * w, 0.9, g * 2 * w, p_arenisca, semilla=3)
            bm.cubo(qs, M, -g * 2.1, 1.0 + h + 2.7, -g * 2.1, g * 4.2, 0.8, g * 4.2, p_arenisca, semilla=4)
    for k in range(2):                                                   # los obeliscos
        a = hacia_camara + math.pi + (-0.55 if k == 0 else 0.6)
        rr = 62.0 + 10 * k
        M = vr.T(math.cos(a) * rr, 0, math.sin(a) * rr)
        bm.cubo(qs, M, -3.0, 0.0, -3.0, 6.0, 2.0, 6.0, p_arenisca, semilla=5)
        bm.cubo(qs, M, -1.9, 2.0, -1.9, 3.8, 26.0, 3.8, p_obelisco, semilla=6)
        bm.cubo(qs, M, -1.5, 28.0, -1.5, 3.0, 2.0, 3.0, p_obelisco, semilla=6)
        bm.cubo(qs, M, -0.8, 30.0, -0.8, 1.6, 1.6, 1.6, p_obelisco, semilla=6)
    a = hacia_camara + math.pi + 0.2                                     # la piramide, muy al fondo
    M = vr.T(math.cos(a) * 170, 0, math.sin(a) * 170)
    for j in range(12):
        w = 46.0 - j * 3.8
        bm.cubo(qs, M, -w, j * 3.4, -w, 2 * w, 3.4, 2 * w, p_arenisca, semilla=7)
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
        qs, info = am.anubis(cual)
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
        d = alto * 0.5 / math.tan(25 * D) * 1.15
        obj = np.array((centro[0], h * 0.5, centro[2]))
        ojo = obj + np.array((0.42, -0.12, 0.9)) / np.linalg.norm((0.42, -0.12, 0.9)) * d
        ojo[1] = max(ojo[1], 3.0)
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        return tuple(b + np.array((-7.0, -5.5, 17.0))), tuple(b + np.array((0.0, -0.5, -2.5))), 50
    alto = max(h, (hi[0] - lo[0]) * 0.8) * (0.74 if cual == 'C' else 1.0)    # la momia es muy alta: mas cerca
    obj = np.array((centro[0], h * (0.64 if cual == 'C' else 0.56), centro[2]))
    return (-0.32 * alto, (h * 0.32 if cual == 'C' else 3.0), 0.82 * alto + centro[2]), tuple(obj), 64


# el cartel de cada uno con el cielo y la luz de su neon: (cielo, niebla, ambiente, luz de frente)
CARTEL_LUZ = {
    'A': (((0.01, 0.02, 0.06), (0.06, 0.12, 0.36), (0.16, 0.3, 0.7)), (0.04, 0.08, 0.24), (0.24, 0.26, 0.32), (0.84, 0.9, 1.0)),
    'B': (((0.05, 0.015, 0.005), (0.34, 0.1, 0.03), (0.7, 0.24, 0.08)), (0.22, 0.07, 0.02), (0.32, 0.25, 0.22), (1.0, 0.86, 0.76)),
    'C': (((0.005, 0.04, 0.03), (0.03, 0.24, 0.18), (0.1, 0.52, 0.4)), (0.02, 0.16, 0.12), (0.24, 0.3, 0.28), (0.82, 1.0, 0.94)),
}


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: la arena y la necropolis; Anubis, con la luz de sus ojos; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    necropolis(lz, cam, niebla, S)
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
    cam = vr.Camara((0.0, 16.0, 200.0), (0.0, 18.0, 0.0), 22, W * SS, H * SS)
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
    """La lamina de materiales, sin letras: una fila por forma (el Pesador, el Chacal y el Embalsamado) y, de
    izquierda a derecha, la piel negra, las rayas del nemes, el collar de cuentas, el oro, el lino plisado, la
    venda, la pluma de Maat, el bronce de la jopesh y la luz."""
    W = 1600
    filas = []
    for c in 'ABC':
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['piel'], 'der', 24, 24), (P['nemes'], 'der', 24, 24), (P['collar'], 'frente', 24, 24),
                      (P['oro'], 'frente', 16, 16), (P['lino'], 'frente', 24, 24), (P['venda'], 'frente', 24, 24),
                      (P['pluma'], 'frente', 8, 32), (P['filo'], 'frente', 12, 24), (P['luz'], 'frente', 16, 16)])
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

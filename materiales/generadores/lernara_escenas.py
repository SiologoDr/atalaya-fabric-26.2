"""
Renders de la ficha de Lernara en sus tres variantes (12-10-2026): las tres en la misma
cienaga de noche (para compararlas bien), cada una alumbrada por su neon; las cabezas de
cerca; las tres juntas con un jugador; y la lamina de materiales.

Uso: python lernara_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
     (con RAPIDO=1 en el entorno, a media resolucion para probar)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne            # el jugador de escala
import quimeras_modelo as qm
import quimeras_escenas as qe         # el lienzo, la niebla y el revelado
import bestias_modelo as bm
import sierpe_modelo as sm
import lernara_modelo as lm

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
FUENTE = 'C:/Windows/Fonts/'
TAU = math.tau
D = vr.D2R
_r = bm._r


def _c(h, k=1.0):
    return tuple(min(1.0, c / 255 * k) for c in nm._hex(h))


def sitio(v):
    """La misma cienaga para las tres; cambia solo el color que le da su neon."""
    neo = _c(lm.VARIANTES[v]['neon'][1])
    return dict(
        luces=[((-0.4, 0.8, 0.8), (0.62, 0.68, 0.74), 0.75, 'llave'), ((0.3, 0.5, -1.0), neo, 1.0, 'contra'),
               ((0.0, -0.5, 1.0), neo, 0.35, 'llave')],
        amb=(0.17, 0.19, 0.2), niebla=tuple(0.04 + 0.08 * c for c in neo), niebla_d=(34, 125),
        cielo=((0.008, 0.01, 0.014), tuple(0.03 + 0.05 * c for c in neo), tuple(0.08 + 0.14 * c for c in neo)),
        motas=tuple(int(255 * (0.55 + 0.45 * c)) for c in neo),
    )


SUELO = _r('0a0e0c', '101612', '161e18', '1c261e', '243026')
qm._reg('suelo_ler', qm._suelo_grande(77, SUELO, None, grietas=False))


def p_roca(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=7.0, umbral=0.62, alto=0.85)
    idx = np.array([1, 2, 2, 3, 3])[idx]
    return bm._imagen(sm._bisel(idx), _r('0a0c0c', '141818', '1e2424', '2a3232', '3a4444')), None


def p_columna(tw, th, cara, s):
    """Marmol viejo de la columna: estrias verticales y manchas limpias."""
    xs = np.arange(tw)[None, :] * np.ones((th, 1), int)
    idx = np.where(xs % 3 == 0, 1, 2)
    m = sm._manchas(tw, th, s, celda=7.0, umbral=0.66, alto=0.9)
    idx = np.where(m >= 3, 3, idx)
    return bm._imagen(sm._bisel(idx), _r('1a1e1c', '2a302c', '3c4440', '525a56', '6c7470')), None


def p_tronco(tw, th, cara, s):
    xs = np.arange(tw)[None, :] * np.ones((th, 1), int)
    ys = np.arange(th)[:, None] * np.ones((1, tw), int)
    idx = np.where((xs + (ys // 4) % 2) % 3 == 0, 1, 2)
    return bm._imagen(sm._bisel(idx), _r('0a0806', '15100c', '201812', '2c2218', '3a2e20')), None


def p_junco(tw, th, cara, s):
    idx = np.full((th, tw), 2)
    if th >= 4:
        idx[: th // 4, :] = 3
    return bm._imagen(idx, _r('0c1208', '141e0e', '1e2c14', '2a3c1c', '3a5026')), None


for _f in (p_roca, p_columna, p_tronco, p_junco):
    _f.__name__ = 'ler_' + _f.__name__


def suelo(lz, cam, niebla, S, ext=180, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_ler'))

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


def cienaga(lz, cam, niebla, S, semilla=4):
    """Rocas y juncos a sus pies; detras, arboles muertos y columnas rotas de un templo."""
    r = random.Random(semilla)
    qs = []
    for k in range(9):                                     # rocas, ninguna delante de la camara
        a = r.uniform(math.pi * 0.95, math.pi * 2.05)
        rr = r.uniform(9.0, 16.0)
        w, h = r.uniform(1.6, 3.2), r.uniform(0.5, 1.4)
        M = vr.T(math.cos(a) * rr, -0.1, math.sin(a) * rr - 2.0) @ vr.Ry(r.uniform(0, 1.5)) @ vr.Rz(r.uniform(-8, 8) * D)
        bm.cubo(qs, M, -w / 2, 0, -w / 2, w, h, w * 0.8, p_roca, semilla=k)
    for k in range(40):                                    # juncos en matas
        a = r.uniform(math.pi * 0.85, math.pi * 2.15)
        rr = r.uniform(8.0, 22.0)
        x, z = math.cos(a) * rr, math.sin(a) * rr - 2.0
        for j in range(3):
            h = r.uniform(1.2, 2.6)
            M = vr.T(x + r.uniform(-0.6, 0.6), 0, z + r.uniform(-0.6, 0.6)) @ vr.Rz(r.uniform(-12, 12) * D)
            bm.cubo(qs, M, -0.08, 0, -0.08, 0.16, h, 0.16, p_junco, semilla=j)
    for k in range(10):                                    # arboles muertos
        a = r.uniform(math.pi * 1.05, math.pi * 1.95)
        rr = r.uniform(22, 56)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        h = r.uniform(9, 16)
        M = vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 3))
        bm.cubo(qs, M @ vr.Rz(r.uniform(-6, 6) * D), -0.7, 0, -0.7, 1.4, h, 1.4, p_tronco, semilla=1)
        for j in range(3):
            y = h * r.uniform(0.5, 0.9)
            Mb = M @ vr.T(0, y, 0) @ vr.Ry(r.uniform(0, TAU)) @ vr.Rz(r.uniform(35, 60) * D)
            bm.cubo(qs, Mb, -0.3, 0, -0.3, 0.6, r.uniform(3, 5), 0.6, p_tronco, semilla=2 + j)
    for k in range(6):                                     # columnas rotas
        a = r.uniform(math.pi * 1.1, math.pi * 1.9)
        rr = r.uniform(18, 40)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        h = r.uniform(4, 13)
        M = vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 1.5)) @ vr.Rz(r.uniform(-7, 7) * D)
        bm.cubo(qs, M, -1.6, 0, -1.6, 3.2, 0.8, 3.2, p_roca, semilla=3)
        bm.cubo(qs, M, -1.1, 0.8, -1.1, 2.2, h, 2.2, p_columna, semilla=4)
        if r.random() < 0.5:
            bm.cubo(qs, M, -1.5, 0.8 + h, -1.5, 3.0, 0.7, 3.0, p_roca, semilla=5)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S):
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    r = random.Random(7)
    for _ in range(int(W * H / 5000)):
        x, yv = r.randint(0, W - 1), r.randint(0, max(1, int(horizonte * 0.75)))
        col[yv, x] = np.clip(col[yv, x] + r.uniform(0.12, 0.4), 0, 1)
    return np.clip(col, 0, 1)


def luna(img, horizonte):
    """Una luna de pixel, pequena y alta, detras de la niebla."""
    W, H = img.size
    p = max(2, int(W / 300))
    R = int(W * 0.035 / p)
    mini = Image.new('RGBA', (2 * R + 1, 2 * R + 1), (0, 0, 0, 0))
    d = ImageDraw.Draw(mini)
    d.ellipse((0, 0, 2 * R, 2 * R), fill=(214, 222, 214, 255))
    d.ellipse((int(R * 0.5), int(R * 0.3), int(R * 0.9), int(R * 0.7)), fill=(176, 186, 180, 255))
    d.ellipse((int(R * 1.1), int(R * 1.0), int(R * 1.5), int(R * 1.4)), fill=(186, 196, 190, 255))
    grande = mini.resize((mini.width * p, mini.height * p), Image.NEAREST)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    capa.paste(grande, (int(W * 0.78), int(horizonte * 0.18)), grande)
    halo = capa.filter(ImageFilter.GaussianBlur(W / 60))
    return Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), halo), capa)


def motas(img, n, semilla, color):
    """Luciernagas del color del neon: puntos que brillan y suben despacio."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(H * 0.15, H)
        g = max(1, int(r.choice((1, 1, 2, 2, 3)) * W / 1600))
        d.rectangle((x, y, x + g, y + g), fill=(*color, r.randint(140, 230)))
    glow = capa.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), glow), capa)


def revelar(lz, cam, W, H, S, n_motas=150, semilla=3, fuerza_vineta=0.45, con_luna=True):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, S)
    img_f = Image.fromarray((fondo * 255).astype(np.uint8))
    if con_luna:
        img_f = luna(img_f, horiz).convert('RGB')
    fondo = np.array(img_f).astype(float) / 255
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * 0.9, radios=((2 * K, 0.5), (10 * K, 0.4), (40 * K, 0.35))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if n_motas > 0:
        img = motas(img, int(n_motas * W / 1600), semilla, S['motas'])
    return img


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=92)
    print('ok', nombre, flush=True)
    return img


NOMBRE = {'A': 'Lernara de Tres Cabezas', 'B': 'Lernara de Cinco Cabezas', 'C': 'Lernara de Dos Cabezas'}
SUB_HEROE = {
    'A': 'tres cuellos en abanico, cabezas con cuernos hacia atras y escamas verde negro',
    'B': 'cinco cuellos unidos por una membrana que se abre como una capucha, y piel lisa con manchas',
    'C': 'dos cuellos trenzados como una soga que arriba se abren en dos cabezas con capucha',
}
SUB_CABEZA = {
    'A': 'cada cabeza con sus fauces encendidas, dientes en peine y cuatro ojos',
    'B': 'cada cabeza con sus fauces encendidas y una cresta de aleta en la frente',
    'C': 'cada cabeza con sus fauces encendidas y una capucha de varillas detras',
}
CAMARA_HEROE = ((5.5, 3.2, 28.5), (0.0, 10.2, 2.0), 56)
CAMARA_CABEZA = {'A': ((4.0, 9.6, 27.0), (0.0, 13.6, 7.0), 50), 'B': ((4.0, 9.2, 28.0), (0.0, 12.8, 6.0), 56),
                 'C': ((3.5, 10.0, 27.0), (0.0, 14.4, 7.0), 52)}


def escena(cual, camara, nombre, sub, n_motas):
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    cienaga(lz, cam, niebla, S)
    qs, info = lm.lernara(cual)
    lm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
    img = revelar(lz, cam, W, H, S, n_motas=n_motas)
    return qe.rotular(img, nombre, sub)


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE, NOMBRE[cual], SUB_HEROE[cual], 160), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA[cual], NOMBRE[cual], SUB_CABEZA[cual], 90), 'cabeza_' + cual)


def tres():
    """Las tres juntas, con la misma luz neutra y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = dict(luces=[((-0.4, 0.8, 0.8), (0.82, 0.82, 0.9), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.9, 0.85, 1.0), 0.8, 'contra')],
             amb=(0.22, 0.21, 0.26), niebla=(0.06, 0.05, 0.09), niebla_d=(170, 320),
             cielo=((0.01, 0.012, 0.03), (0.05, 0.05, 0.1), (0.16, 0.13, 0.22)), motas=(230, 230, 255))
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    cam = vr.Camara((0.0, 11.0, 118.0), (0.0, 8.5, 0.0), 24, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=260, paso=32, cerca=40)
    altos = []
    for cual, x in (('A', -33.0), ('B', 0.0), ('C', 33.0)):
        qs, info = lm.lernara(cual)
        P = np.array([p for q in qs for p in q[0]])
        altos.append(P[:, 1].max())
        lm.dibujar(lz, cam, qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(-12 * D)), S['luces'], S['amb'], niebla)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(10.0, 18.0, 0)), S['luces'], S['amb'], niebla)
    img = revelar(lz, cam, W, H, S, n_motas=0, con_luna=False)
    guardar(qe.rotular(img, 'Las tres variantes, a escala', 'de Tres Cabezas · de Cinco Cabezas · de Dos Cabezas · '
                       'un jugador (1,8) delante · de alto: %.0f · %.0f · %.0f bloques' % tuple(altos)), 'tres')


def materiales():
    W = 1600
    filas = []
    for c in 'ABC':
        P = lm.pintores(lm.VARIANTES[c])
        fila = [(P['cuerpo'], 'piel', 'der', 24, 24), (P['vientre'], 'vientre', 'abajo', 16, 16), (P['hueso'], 'hueso', 'der', 8, 16),
                (P['diente'], 'diente', 'frente', 4, 12), (P['fauces'], 'fauces', 'abajo', 16, 16), (P['nucleo'], 'nucleo', 'frente', 24, 24),
                (P['bronce'], 'bronce', 'frente', 24, 8), (P['membrana'], 'membrana', 'frente', 24, 24)]
        filas.append((c, fila))
    celda = 168
    H = 130 + len(filas) * (celda + 76)
    img = Image.new('RGB', (W, H), (16, 15, 20))
    d = ImageDraw.Draw(img)
    try:
        f1 = ImageFont.truetype(FUENTE + 'georgiab.ttf', 40)
        f2 = ImageFont.truetype(FUENTE + 'consola.ttf', 17)
        f3 = ImageFont.truetype(FUENTE + 'georgiab.ttf', 24)
    except OSError:
        f1 = f2 = f3 = ImageFont.load_default()
    d.text((48, 34), 'Materiales: dibujados a 8 pixeles por bloque, sin ruido', font=f1, fill=(244, 234, 210))
    for fi, (c, fila) in enumerate(filas):
        y0 = 120 + fi * (celda + 76)
        d.text((48, y0 + celda // 2 - 14), c, font=f3, fill=(244, 234, 210))
        for k, (pintor, nombre, cara, tw, th) in enumerate(fila):
            t, e = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (40, 36, 46, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 96 + k * 186
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(70, 64, 80))
            d.text((cx, y0 + celda + 8), nombre, font=f2, fill=(220, 212, 196))
    guardar(img, 'materiales')


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

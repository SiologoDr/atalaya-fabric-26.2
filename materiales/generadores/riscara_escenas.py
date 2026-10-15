"""
Renders de la ficha de Riscara en sus tres tipos (12-10-2026): cada tipo en su risco,
de abajo y con las alas abiertas; la cabeza de cerca; los tres juntos con un jugador; y
la lamina de materiales.

  A  de Tormenta   el risco bajo la tormenta, con lluvia y un rayo en el cielo
  B  de Escarcha   la cumbre nevada de noche, con nieve que cae
  C  de Ponzona    el risco del pantano, con niebla verde y esporas

Uso: python riscara_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import riscara_modelo as rm

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
FUENTE = 'C:/Windows/Fonts/'
TAU = math.tau
D = vr.D2R
_r = bm._r

SITIO = {
    'A': dict(
        luces=[((-0.4, 0.8, 0.8), (0.66, 0.72, 0.86), 0.8, 'llave'), ((0.3, 0.5, -1.0), (1.0, 0.92, 0.45), 1.0, 'contra'),
               ((0.0, -0.5, 1.0), (1.0, 0.85, 0.3), 0.35, 'llave')],
        amb=(0.2, 0.22, 0.27), niebla=(0.08, 0.09, 0.12), niebla_d=(40, 140),
        cielo=((0.02, 0.025, 0.04), (0.08, 0.09, 0.12), (0.2, 0.21, 0.24)),
        suelo=_r('101216', '181b20', '20242a', '2a2e36', '363b44'), motas=((200, 210, 230), (230, 236, 255)), viento=(-0.35, 1.0),
        largo=(6, 16), rayo=True,
    ),
    'B': dict(
        luces=[((-0.4, 0.8, 0.8), (0.8, 0.88, 1.0), 0.85, 'llave'), ((0.3, 0.5, -1.0), (0.7, 0.9, 1.0), 0.9, 'contra'),
               ((0.0, -0.5, 1.0), (0.6, 0.8, 1.0), 0.3, 'llave')],
        amb=(0.26, 0.3, 0.38), niebla=(0.2, 0.26, 0.36), niebla_d=(40, 140),
        cielo=((0.02, 0.035, 0.07), (0.1, 0.16, 0.26), (0.32, 0.42, 0.56)),
        suelo=_r('56667a', '6e8094', '8a9cae', 'a8b8c8', 'c8d4e0'), motas=((240, 246, 255), (210, 225, 245)), viento=(0.2, 1.0),
        largo=(1, 3), rayo=False,
    ),
    'C': dict(
        luces=[((-0.4, 0.8, 0.8), (0.62, 0.7, 0.56), 0.75, 'llave'), ((0.3, 0.5, -1.0), (0.6, 1.0, 0.3), 1.0, 'contra'),
               ((0.0, -0.5, 1.0), (0.5, 0.9, 0.2), 0.35, 'llave')],
        amb=(0.18, 0.21, 0.16), niebla=(0.06, 0.12, 0.05), niebla_d=(36, 130),
        cielo=((0.01, 0.02, 0.01), (0.04, 0.08, 0.03), (0.14, 0.24, 0.08)),
        suelo=_r('0e120a', '161c10', '1e2616', '28321c', '323e22'), motas=((180, 255, 90), (220, 255, 150)), viento=(0.0, -0.4),
        largo=(1, 2), rayo=False,
    ),
}
for _k, _s in SITIO.items():
    qm._reg('suelo_ris_' + _k, qm._suelo_grande(20 + ord(_k), _s['suelo'], None, grietas=False))


def p_roca(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=7.0, umbral=0.62, alto=0.85)
    idx = np.array([1, 2, 2, 3, 3])[idx]
    return bm._imagen(sm._bisel(idx), _r('0c0c10', '1a1a20', '28282e', '38383e', '4c4c54')), None


def p_nieve(tw, th, cara, s):
    idx = np.full((th, tw), 3)
    idx = sm._bisel(idx)
    return bm._imagen(idx, SITIO['B']['suelo']), None


def suelo(lz, cam, niebla, sitio, ext=180, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_ris_' + sitio))

    cx, cz = cam.ojo[0], cam.ojo[2]
    for gx in range(-ext, ext, paso):
        for gz in range(-ext, ext, paso):
            if abs(gx + paso / 2 - cx) < cerca and abs(gz + paso / 2 - cz) < cerca:
                for a in range(gx, gx + paso, paso_cerca):
                    for b in range(gz, gz + paso, paso_cerca):
                        baldosa(a, b, paso_cerca)
            else:
                baldosa(gx, gz, paso)
    qm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


def risco(lz, cam, niebla, sitio, semilla=4):
    """El risco donde se planta: losas rotas bajo las patas y agujas de roca detras."""
    r = random.Random(semilla)
    qs = []
    for k in range(9):
        a = k * TAU / 9 + r.uniform(-0.2, 0.2)
        rr = r.uniform(2.0, 4.5)
        w, h = r.uniform(2.0, 3.6), r.uniform(0.3, 0.8)
        M = vr.T(math.cos(a) * rr, -0.15, math.sin(a) * rr - 1.0) @ vr.Ry(r.uniform(0, 1.5)) @ vr.Rz(r.uniform(-6, 6) * D)
        bm.cubo(qs, M, -w / 2, 0, -w / 2, w, h, w * 0.8, p_roca, semilla=k)
    for _ in range(16):
        a = r.uniform(math.pi * 1.05, math.pi * 1.95)
        rr = r.uniform(18, 46)
        px, pz = math.cos(a) * rr, math.sin(a) * rr
        h = r.uniform(6, 20)
        M = vr.T(px, 0, pz) @ vr.Ry(r.uniform(0, 1.5))
        for j in range(4):
            g = 2.0 * (1 - j * 0.22)
            bm.cubo(qs, M, -g, h * j / 4, -g, 2 * g, h / 4 + 0.05, 2 * g, p_nieve if sitio == 'B' and j == 3 else p_roca, semilla=j)
    sm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


def cielo(W, H, horizonte, sitio):
    arriba, medio, abajo = (np.array(c) for c in SITIO[sitio]['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    if sitio in ('B', 'T'):
        r = random.Random(7)
        for _ in range(int(W * H / 4500)):
            x, yv = r.randint(0, W - 1), r.randint(0, max(1, int(horizonte * 0.8)))
            col[yv, x] = np.clip(col[yv, x] + r.uniform(0.15, 0.5), 0, 1)
    return np.clip(col, 0, 1)


def rayo(img, semilla=5):
    """Un rayo limpio en el cielo, de pixel, con su halo."""
    W, H = img.size
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    x, y = W * 0.82, 0
    pts = [(x, y)]
    while y < H * 0.55:
        y += H * r.uniform(0.04, 0.08)
        x += W * r.uniform(-0.03, 0.03)
        pts.append((x, y))
    d.line(pts, fill=(255, 250, 210, 255), width=max(2, int(W / 400)))
    halo = capa.filter(ImageFilter.GaussianBlur(W / 120))
    base = img.convert('RGBA')
    base = Image.alpha_composite(base, halo)
    base = Image.alpha_composite(base, halo)
    return Image.alpha_composite(base, capa)


def motas(img, n, semilla, colores, viento, largo):
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H)
        c = colores[0] if r.random() < 0.6 else colores[1]
        l = r.uniform(*largo) * W / 1600
        g = max(1, int(r.choice((1, 1, 2)) * W / 1600))
        d.line((x, y, x + viento[0] * l, y + viento[1] * l), fill=(*c, r.randint(110, 220)), width=g)
    glow = capa.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)


def revelar(lz, cam, W, H, sitio, n_motas=150, semilla=3, fuerza_vineta=0.45):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, sitio)
    img_f = Image.fromarray((fondo * 255).astype(np.uint8))
    if SITIO[sitio].get('rayo'):
        img_f = rayo(img_f).convert('RGB')
    fondo = np.array(img_f).astype(float) / 255
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * 0.9, radios=((2 * K, 0.5), (10 * K, 0.4), (40 * K, 0.35))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if n_motas > 0:
        img = motas(img, int(n_motas * W / 1600), semilla, SITIO[sitio]['motas'], SITIO[sitio]['viento'], SITIO[sitio]['largo'])
    return img


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=92)
    print('ok', nombre, flush=True)
    return img


NOMBRE = {'A': 'Riscara de Tormenta', 'B': 'Riscara de Escarcha', 'C': 'Riscara de Ponzona'}
SUB_HEROE = {
    'A': 'escamas de pizarra, cuernos como pararrayos y alas con nervios de rayo',
    'B': 'escamas de escarcha, corona de carambanos y alas con nervios de hielo',
    'C': 'escamas con manchas de veneno, gorguera de membrana y bulbos de esporas',
}
SUB_CABEZA = {
    'A': 'las fauces encendidas y el nucleo de rayo en la garganta',
    'B': 'las fauces encendidas y el nucleo de hielo en la garganta',
    'C': 'las fauces encendidas y el nucleo de ponzona en la garganta',
}
CAMARA_HEROE = ((6.0, 4.5, 27.5), (0.0, 12.0, 1.0), 58)
CAMARA_CABEZA = ((3.0, 11.0, 21.5), (0.0, 14.2, 8.0), 50)


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


def escena(cual, camara, nombre, sub, n_motas):
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    niebla = qe.Niebla(SITIO[cual]['niebla'], *SITIO[cual]['niebla_d'])
    ojo, obj, fov = camara
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, cual)
    risco(lz, cam, niebla, cual)
    qs, info = rm.riscara(cual)
    z0 = lz.z.copy()
    rm.dibujar(lz, cam, qs, SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    img = revelar(lz, cam, W, H, cual, n_motas=n_motas)
    return img


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE, NOMBRE[cual], SUB_HEROE[cual], 220), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA, NOMBRE[cual], SUB_CABEZA[cual], 120), 'cabeza_' + cual)


def tres():
    """Los tres tipos juntos, con la misma luz neutra y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    SITIO['T'] = dict(luces=[((-0.4, 0.8, 0.8), (0.82, 0.82, 0.9), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.9, 0.85, 1.0), 0.8, 'contra')],
                      amb=(0.22, 0.21, 0.26), niebla=(0.06, 0.05, 0.09), niebla_d=(170, 320),
                      cielo=((0.01, 0.012, 0.03), (0.05, 0.05, 0.1), (0.16, 0.13, 0.22)),
                      suelo=_r('12111a', '16141e', '1a1822', '1e1c26', '22202a'), motas=((230, 230, 255), (200, 200, 240)), viento=(0, 1),
                      largo=(1, 2), rayo=False)
    qm._reg('suelo_ris_T', qm._suelo_grande(95, SITIO['T']['suelo'], None, grietas=False))
    niebla = qe.Niebla(SITIO['T']['niebla'], *SITIO['T']['niebla_d'])
    cam = vr.Camara((0.0, 10.0, 150.0), (0.0, 10.0, 0.0), 24, W * SS, H * SS)
    suelo(lz, cam, niebla, 'T', ext=260, paso=32, cerca=40)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -40.0), ('B', 0.0), ('C', 40.0)):
        qs, info = rm.riscara(cual)
        z0 = lz.z.copy()
        rm.dibujar(lz, cam, qm.transformar(qs, vr.T(x, 0, 0)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(8.0, 14.0, 0)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)
    img = revelar(lz, cam, W, H, 'T', n_motas=0)
    guardar(img, 'tres')


def materiales():
    W = 1600
    filas = []
    for c in 'ABC':
        P = rm.pintores(rm.TIPOS[c])
        fila = [(P['cuerpo'], 'cuerpo', 'der', 16, 24), (P['vientre'], 'vientre', 'abajo', 16, 16), (P['hueso'], 'hueso', 'der', 8, 16),
                (P['diente'], 'diente', 'frente', 4, 12), (P['fauces'], 'fauces', 'abajo', 16, 16), (P['nucleo'], 'nucleo', 'frente', 24, 24),
                (P['membrana'], 'ala', 'frente', 32, 40)]
        filas.append((c, fila))
    cols, celda = 7, 196
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (16, 15, 20))
    d = ImageDraw.Draw(img)
    for fi, (c, fila) in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, nombre, cara, tw, th) in enumerate(fila):
            t, e = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (40, 36, 46, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 66 + k * 212
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(70, 64, 80))
    guardar(img, 'materiales')


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

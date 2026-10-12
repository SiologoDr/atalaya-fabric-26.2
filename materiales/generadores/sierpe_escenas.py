"""
Renders de la ficha de Simara en sus tres tipos (12-10-2026): cada tipo en su sima, de
abajo y con las fauces abiertas; la cabeza de cerca; los tres juntos con un jugador; y
la lamina de materiales.

  A  Abisal      la sima inundada, de noche, con plancton que brilla
  B  Volcanica   la sima de lava, con ascuas en el aire
  C  Espectral   la sima de la cripta, con almas que suben

Uso: python sierpe_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
        luces=[((-0.4, 0.8, 0.8), (0.62, 0.74, 0.92), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.4, 0.95, 1.0), 1.0, 'contra'),
               ((0.0, -0.5, 1.0), (0.3, 0.8, 0.95), 0.4, 'llave')],
        amb=(0.2, 0.24, 0.3), niebla=(0.03, 0.08, 0.12), niebla_d=(30, 110),
        cielo=((0.004, 0.012, 0.03), (0.02, 0.06, 0.1), (0.05, 0.14, 0.2)),
        suelo=_r('0a1218', '101c24', '16262e', '1e323a', '283e46'), motas=((140, 240, 255), (200, 250, 255)), sima=None,
    ),
    'B': dict(
        luces=[((-0.4, 0.8, 0.8), (0.86, 0.66, 0.56), 0.75, 'llave'), ((0.3, 0.5, -1.0), (1.0, 0.55, 0.2), 1.0, 'contra'),
               ((0.0, -0.6, 1.0), (1.0, 0.5, 0.15), 0.55, 'llave')],
        amb=(0.24, 0.17, 0.16), niebla=(0.16, 0.05, 0.03), niebla_d=(30, 110),
        cielo=((0.02, 0.008, 0.01), (0.12, 0.03, 0.02), (0.36, 0.1, 0.04)),
        suelo=_r('0c0808', '161010', '201818', '2c2222', '3a2e2c'), motas=((255, 170, 70), (255, 220, 140)), sima=('fff0b0', 'ff6a10'),
    ),
    'C': dict(
        luces=[((-0.4, 0.8, 0.8), (0.74, 0.7, 0.86), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.95, 0.45, 1.0), 1.0, 'contra'),
               ((0.0, -0.5, 1.0), (0.9, 0.35, 0.8), 0.35, 'llave')],
        amb=(0.22, 0.2, 0.27), niebla=(0.08, 0.04, 0.12), niebla_d=(30, 110),
        cielo=((0.012, 0.006, 0.025), (0.06, 0.03, 0.1), (0.18, 0.08, 0.22)),
        suelo=_r('121018', '1a1822', '24202c', '2e2a38', '3a3546'), motas=((240, 150, 255), (255, 220, 250)), sima=None,
    ),
}
for _k, _s in SITIO.items():
    qm._reg('suelo_sim_' + _k, qm._suelo_grande(30 + ord(_k), _s['suelo'], None, grietas=False))


def p_roca(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=7.0, umbral=0.62, alto=0.85)
    idx = np.array([1, 2, 2, 3, 3])[idx]
    return bm._imagen(sm._bisel(idx), _r('0c0a0e', '1a171c', '28242c', '38323e', '4c4454')), None


def p_negro(tw, th, cara, s):
    return bm._imagen(np.zeros((th, tw), int), _r('010102', '030305', '050508', '07070b', '0a0a10')), None


def suelo(lz, cam, niebla, sitio, ext=160, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_sim_' + sitio))

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


def sima(lz, cam, niebla, sitio, x=-2.6, z=-8.0, semilla=4):
    """La sima de donde sale: un agujero negro con el borde de roca rota (y lava en la volcanica)."""
    r = random.Random(semilla)
    qs = []
    bm.redondo(qs, vr.T(x, 0.02, z), 0, 0.04, 4.6, 4.2, p_negro, n=4)
    if SITIO[sitio]['sima']:
        c1, c2 = SITIO[sitio]['sima']

        def p_lava(tw, th, cara, s, c1=c1, c2=c2):
            return qm._emisivo(c1, c2, max(2, tw), max(2, th)), None
        p_lava.__name__ = 'lava_sima_' + sitio
        bm.PLENOS.add(p_lava)
        bm.redondo(qs, vr.T(x, 0.03, z), 0, 0.04, 3.4, 3.0, p_lava, n=4)
    for k in range(22):
        a = k * TAU / 22 + r.uniform(-0.1, 0.1)
        rr = r.uniform(4.4, 5.6)
        w = r.uniform(0.9, 1.8)
        h = r.uniform(0.4, 1.6)
        M = vr.T(x + math.cos(a) * rr, -0.1, z + math.sin(a) * rr * 0.92) @ vr.Ry(-a) @ vr.Rz(r.uniform(-18, 18) * D)
        bm.cubo(qs, M, -w / 2, 0, -w / 2, w, h, w, p_roca, semilla=k)
    for _ in range(14):                                       # agujas de roca alrededor
        a = r.uniform(0, TAU)
        rr = r.uniform(14, 34)
        px, pz = x + math.cos(a) * rr, z + math.sin(a) * rr
        if pz > -2 and abs(px) < 30:
            continue
        h = r.uniform(3, 10)
        M = vr.T(px, 0, pz) @ vr.Ry(r.uniform(0, 1.5))
        for j in range(3):
            g = 1.3 * (1 - j * 0.28)
            bm.cubo(qs, M, -g, h * j / 3, -g, 2 * g, h / 3 + 0.05, 2 * g, p_roca, semilla=j)
    sm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


def cielo(W, H, horizonte, sitio):
    arriba, medio, abajo = (np.array(c) for c in SITIO[sitio]['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    r = random.Random(7)
    for _ in range(int(W * H / 5000)):
        x, yv = r.randint(0, W - 1), r.randint(0, max(1, int(horizonte * 0.8)))
        col[yv, x] = np.clip(col[yv, x] + r.uniform(0.15, 0.5), 0, 1)
    return np.clip(col, 0, 1)


def motas(img, n, semilla, colores, viento=(0.0, -1.0), largo=(1, 3)):
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H)
        c = colores[0] if r.random() < 0.6 else colores[1]
        l = r.uniform(*largo) * W / 1600
        g = max(1, int(r.choice((1, 1, 2)) * W / 1600))
        d.rectangle((x, y, x + g, y + g + viento[1] * 0 + l * 0.2), fill=(*c, r.randint(120, 230)))
    glow = capa.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)


def revelar(lz, cam, W, H, sitio, n_motas=150, semilla=3, fuerza_vineta=0.45):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    arr = col * alfa + cielo(W, H, horiz, sitio) * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * 0.9, radios=((2 * K, 0.5), (10 * K, 0.4), (40 * K, 0.35))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if n_motas > 0:
        img = motas(img, int(n_motas * W / 1600), semilla, SITIO[sitio]['motas'])
    return img


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=92)
    print('ok', nombre, flush=True)
    return img


NOMBRE = {'A': 'Simara Abisal', 'B': 'Simara Volcanica', 'C': 'Simara Espectral'}
SUB_HEROE = {
    'A': 'escamas con fotoforos, aletas en abanico y barbillones con un bulbo de luz',
    'B': 'placas de obsidiana con grietas de magma, corona de cuernos y latigos de lava',
    'C': 'vertebras de hueso con manchas de alma, astas, mortaja y farolillos de almas',
}
SUB_CABEZA = {
    'A': 'en la garganta gira un remolino de agua',
    'B': 'en la garganta gira un remolino de magma',
    'C': 'en la garganta gira un remolino de almas',
}
CAMARA_HEROE = ((6.5, 6.5, 20.0), (0.0, 12.6, 3.0), 58)
CAMARA_CABEZA = ((3.2, 10.6, 18.5), (0.0, 14.0, 7.0), 48)


def escena(cual, camara, nombre, sub, n_motas):
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    niebla = qe.Niebla(SITIO[cual]['niebla'], *SITIO[cual]['niebla_d'])
    ojo, obj, fov = camara
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, cual)
    sima(lz, cam, niebla, cual)
    qs, info = sm.simara(cual)
    sm.dibujar(lz, cam, qs, SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    img = revelar(lz, cam, W, H, cual, n_motas=n_motas)
    return qe.rotular(img, nombre, sub)


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE, NOMBRE[cual], SUB_HEROE[cual], 170), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA, NOMBRE[cual], SUB_CABEZA[cual], 100), 'cabeza_' + cual)


def tres():
    """Los tres tipos juntos, con la misma luz neutra y un jugador delante: para compararlos."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    SITIO['T'] = dict(luces=[((-0.4, 0.8, 0.8), (0.82, 0.82, 0.9), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.9, 0.85, 1.0), 0.8, 'contra')],
                      amb=(0.22, 0.21, 0.26), niebla=(0.06, 0.05, 0.09), niebla_d=(140, 280),
                      cielo=((0.01, 0.012, 0.03), (0.05, 0.05, 0.1), (0.16, 0.13, 0.22)),
                      suelo=_r('12111a', '16141e', '1a1822', '1e1c26', '22202a'), motas=((230, 230, 255), (200, 200, 240)))
    qm._reg('suelo_sim_T', qm._suelo_grande(96, SITIO['T']['suelo'], None, grietas=False))
    niebla = qe.Niebla(SITIO['T']['niebla'], *SITIO['T']['niebla_d'])
    cam = vr.Camara((6.0, 8.0, 104.0), (0.0, 8.5, 0.0), 25, W * SS, H * SS)
    suelo(lz, cam, niebla, 'T', ext=220, paso=32, cerca=40)
    for cual, x in (('A', -27.0), ('B', 0.0), ('C', 27.0)):
        qs, info = sm.simara(cual)
        qs = [q for q in qs if min(p[1] for p in q[0]) > -0.5]
        sm.dibujar(lz, cam, qm.transformar(qs, vr.T(x, 0, 0)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(6.0, 10.0, 0)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)
    img = revelar(lz, cam, W, H, 'T', n_motas=0)
    alto = max(max(p[1] for p in q[0]) for q in sm.simara('A')[0])
    guardar(qe.rotular(img, 'Los tres tipos, a escala', 'Abisal · Volcanica · Espectral · un jugador (1,8) delante · unos %.0f bloques de alto' % alto),
            'tres')


def materiales():
    """La lamina: para cada tipo, sus texturas principales a pixel grande."""
    W = 1600
    filas = []
    for c in 'ABC':
        P = sm.pintores(sm.TIPOS[c])
        fila = [(P['cuerpo'], 'cuerpo', 'der'), (P['vientre'], 'vientre', 'abajo'), (P['cinto'], 'cinturon', 'arriba'),
                (P['diente'], 'diente', 'frente'), (P['fauces'], 'fauces', 'abajo'), (P['remolino'], 'remolino', 'frente')]
        extra = {'A': (P.get('membrana'), 'aleta', 'der'), 'B': (P.get('cuerno'), 'cuerno', 'der'), 'C': (P.get('tela'), 'mortaja', 'frente')}[c]
        fila.append(extra)
        filas.append((c, fila))
    cols, celda = 7, 196
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
        for k, (pintor, nombre, cara) in enumerate(fila):
            tw, th = (16, 24) if nombre in ('cuerpo', 'aleta', 'mortaja', 'cuerno') else (16, 16)
            if nombre == 'diente':
                tw, th = 4, 12
            if nombre == 'remolino':
                tw, th = 24, 24
            t, e = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (40, 36, 46, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 100 + k * 212
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

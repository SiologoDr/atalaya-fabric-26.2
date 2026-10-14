"""
Renders de la Gorgona (13-10-2026): sus tres tipos, cada uno en la explanada
de noche con agujas de catedral detras y con la luz de su neon; su cartel (de cerca y desde abajo); su
retrato; el primer plano de la cara; las tres juntas con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco alrededor de ella, serpientes y alas incluidas.

Uso: python vulpina_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import gorgona_modelo as am

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
    """La misma explanada para los tres; el cielo y la niebla toman el color de su neon."""
    neo = _c(am.VARIANTES[v]['neon'][1])
    return dict(
        luces=[((-0.5, 0.8, 0.7), (0.72, 0.7, 0.86), 0.8, 'llave'), ((0.3, 0.5, -1.0), neo, 1.0, 'contra'),
               ((0.0, -0.5, 1.0), neo, 0.35, 'llave')],
        amb=(0.2, 0.19, 0.25), niebla=tuple(0.05 + 0.12 * c for c in neo), niebla_d=(36, 140),
        cielo=((0.02, 0.015, 0.05), tuple(0.05 + 0.16 * c for c in neo), tuple(0.1 + 0.32 * c for c in neo)),
        motas=tuple(int(255 * (0.6 + 0.4 * c)) for c in neo),
    )


SUELO = _r('120e1c', '181424', '1e1a2c', '262036', '2e2842')
qm._reg('suelo_gor', qm._suelo_grande(91, SUELO, None, grietas=False))


def p_roca(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=7.0, umbral=0.62, alto=0.85)
    idx = np.array([1, 2, 2, 3, 3])[idx]
    return bm._imagen(sm._bisel(idx), _r('0c0a14', '16121e', '201a2a', '2c2438', '3a3048')), None


def p_torre(tw, th, cara, s):
    """La piedra de las agujas: sillares en hiladas y alguna ventana ojival oscura."""
    ys, xs = np.mgrid[0:th, 0:tw]
    fila = ys // 4
    idx = np.where((ys % 4) == 0, 1, 2)
    idx = np.where(((xs + (fila % 2) * 3) % 6) == 0, 1, idx)
    return bm._imagen(sm._bisel(idx), _r('08060e', '100c18', '181222', '201a2e', '2a223a')), None


for _f in (p_roca, p_torre):
    _f.__name__ = 'gor_' + _f.__name__


def suelo(lz, cam, niebla, S, ext=180, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_gor'))

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


def explanada(lz, cam, niebla, S, semilla=4):
    """Losas rotas alrededor de la dama y, detras, agujas de catedral."""
    r = random.Random(semilla)
    qs = []
    for k in range(10):                                    # el cerco de losas levantadas
        a = k * TAU / 10 + r.uniform(-0.15, 0.15)
        rr = r.uniform(5.6, 7.4)
        w, h = r.uniform(1.6, 2.8), r.uniform(0.4, 1.0)
        M = (vr.T(math.cos(a) * rr, -0.1, math.sin(a) * rr - 0.4) @ vr.Ry(-a) @ vr.Rz(r.uniform(-25, -8) * D))
        bm.cubo(qs, M, -w / 2, 0, -w / 2, w, h, w * 0.7, p_roca, semilla=k)
    for _ in range(9):                                     # agujas
        a = r.uniform(math.pi * 1.1, math.pi * 1.9)
        rr = r.uniform(34, 80)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        h = r.uniform(14, 34)
        g = r.uniform(2.4, 4.2)
        M = vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 1.5))
        bm.cubo(qs, M, -g, 0, -g, 2 * g, h, 2 * g, p_torre, semilla=1)
        for j in range(4):                                 # el chapitel, en escalones
            gg = g * (0.8 - j * 0.2)
            bm.cubo(qs, M, -gg, h + j * h * 0.12, -gg, 2 * gg, h * 0.12, 2 * gg, p_torre, semilla=2 + j)
        bm.cubo(qs, M, -0.2, h + 0.48 * h, -0.2, 0.4, h * 0.18, 0.4, p_torre, semilla=6)
        for s in (1, -1):                                  # dos pinaculos a los lados
            Mp = M @ vr.T(s * g * 1.2, 0, 0)
            bm.cubo(qs, Mp, -0.5, 0, -0.5, 1.0, h * 0.7, 1.0, p_torre, semilla=7)
            bm.cubo(qs, Mp, -0.25, h * 0.7, -0.25, 0.5, h * 0.12, 0.5, p_torre, semilla=8)
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
    """El contorno blanco: los pixeles de fuera que tocan la figura y quedan detras de ella."""
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


def escena(cual, camara, n_motas, brillo=0.9, S=None):
    """Una foto: el suelo, las losas y las agujas; la dama, con la luz de sus fuegos; el contorno
    blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    explanada(lz, cam, niebla, S)
    qs, info = am.gorgona(cual)
    neo = _c(am.VARIANTES[cual]['neon'][1])
    luces = S['luces'] + [(tuple(p) + (8.0,), neo, 0.85, 'punto') for p in info['luces'][:3]]
    z0 = lz.z.copy()
    am.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


CAMARA_HEROE = ((24.0, 6.0, 42.0), (0.0, 15.5, -1.0), 56)
CAMARA_CABEZA = ((-8.5, 25.4, 22.0), (0.0, 26.6, 1.0), 44)
CAMARA_CARTEL = ((-7.5, 3.5, 21.0), (0.0, 20.5, 0.0), 62)

# el cartel de cada uno con el cielo y la luz de su neon: (cielo, niebla, ambiente, luz de frente)
CARTEL_LUZ = {
    'A': (((0.02, 0.04, 0.02), (0.1, 0.24, 0.08), (0.3, 0.52, 0.2)), (0.07, 0.16, 0.05), (0.28, 0.32, 0.26), (0.92, 1.0, 0.84)),
    'B': (((0.05, 0.03, 0.01), (0.32, 0.17, 0.05), (0.66, 0.4, 0.14)), (0.22, 0.12, 0.04), (0.32, 0.27, 0.22), (1.0, 0.88, 0.72)),
    'C': (((0.05, 0.01, 0.015), (0.28, 0.04, 0.05), (0.6, 0.12, 0.12)), (0.18, 0.03, 0.03), (0.28, 0.2, 0.2), (1.0, 0.76, 0.74)),
}


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE, 150), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA, 90), 'cabeza_' + cual)


def cartel(cual):
    """La presentacion del cartel: de cerca y desde abajo, con el cielo y la luz de su neon."""
    cielo_, niebla_, amb_, llave = CARTEL_LUZ[cual]
    S = sitio(cual)
    S.update(cielo=cielo_, niebla=niebla_, amb=amb_, luces=[((-0.6, 0.35, 0.8), llave, 0.95, 'llave')] + S['luces'][1:])
    guardar(escena(cual, CAMARA_CARTEL, 60, brillo=1.25, S=S), 'cartel_' + cual)


def tres():
    """Los tres juntos, con la misma luz neutra y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = dict(luces=[((-0.4, 0.8, 0.8), (0.82, 0.82, 0.9), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.9, 0.85, 1.0), 0.8, 'contra')],
             amb=(0.22, 0.21, 0.26), niebla=(0.06, 0.05, 0.09), niebla_d=(180, 330),
             cielo=((0.01, 0.012, 0.03), (0.05, 0.05, 0.1), (0.16, 0.13, 0.22)), motas=(230, 230, 255))
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    cam = vr.Camara((0.0, 14.0, 170.0), (0.0, 15.5, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=280, paso=32, cerca=40)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -34.0), ('B', 0.0), ('C', 34.0)):
        qs, info = am.gorgona(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(-20 * D))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(14.0, 20.0, 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), 'tres')


def materiales():
    """La lamina de materiales, sin letras: una fila por hermana (Medusa, Esteno y Euriale) y, de
    izquierda a derecha, la cara C3 con sus ojos, la piel, las escamas de serpiente, el quiton, la greca,
    el oro, el cuero de las tiras y la pluma."""
    W = 1600
    filas = []
    for c in 'ABC':
        P = am.pintores(am.VARIANTES[c])
        am.jm.pintor_cara(P, am.VARIANTES[c])
        filas.append([(P['cara'], 'frente', 16, 16), (P['piel'], 'der', 16, 16), (P['serpiente'], 'der', 24, 24),
                      (P['tela'], 'frente', 24, 32), (P['greca'], 'der', 36, 12), (P['oro'], 'der', 16, 16),
                      (P['tiras'], 'frente', 8, 32), (P['pluma'], 'arriba', 10, 48)])
    celda = 168
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
            cx = 48 + k * 192
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(70, 64, 80))
    guardar(img, 'materiales')


def cara(cual):
    """El primer plano de la cara, con el fondo de estudio y la luz del muestrario de jefas, para ver bien la
    mirada (la C3 con mirada de jefa)."""
    ppb = bm.PPB
    import catalogo_dama as cd                        # pone su propio PPB al importarse: se devuelve el de aqui
    bm.PPB = ppb
    qs, info = am.gorgona(cual)
    c = np.asarray(info['cara'], float)
    cd.foto(qs, tuple(c + np.array((-1.8, 0.6, 8.5))), tuple(c + np.array((0.0, -0.2, 0.0))), 30, 'cara_' + cual, OUT)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'ABC'})
ESCENAS.update({'cara_' + c: (lambda c=c: cara(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

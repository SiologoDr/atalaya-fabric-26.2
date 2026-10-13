"""
Renders del estudio de Ofidia (12-10-2026): la original recreada y sus tres variantes, cada
una en la misma explanada de noche con agujas de catedral detras (como el cartel de Dedsafio 4)
y alumbrada por su neon; las cabezas de cerca; las cuatro juntas con un jugador; y la lamina
de materiales.

Uso: python ofidia_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import ofidia_modelo as om

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
FUENTE = 'C:/Windows/Fonts/'
TAU = math.tau
D = vr.D2R
_r = bm._r


def _c(h):
    return tuple(c / 255 for c in nm._hex(h))


def sitio(v):
    """La misma explanada para las cuatro; el cielo y la niebla toman el color de su neon."""
    neo = _c(om.VARIANTES[v]['neon'][1])
    return dict(
        luces=[((-0.5, 0.8, 0.7), (0.72, 0.7, 0.86), 0.8, 'llave'), ((0.3, 0.5, -1.0), neo, 1.0, 'contra'),
               ((0.0, -0.5, 1.0), neo, 0.35, 'llave')],
        amb=(0.2, 0.19, 0.25), niebla=tuple(0.05 + 0.12 * c for c in neo), niebla_d=(36, 140),
        cielo=((0.02, 0.015, 0.05), tuple(0.05 + 0.16 * c for c in neo), tuple(0.1 + 0.32 * c for c in neo)),
        motas=tuple(int(255 * (0.6 + 0.4 * c)) for c in neo),
    )


SUELO = _r('120e1c', '181424', '1e1a2c', '262036', '2e2842')
qm._reg('suelo_ofi', qm._suelo_grande(91, SUELO, None, grietas=False))


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
    _f.__name__ = 'ofi_' + _f.__name__


def suelo(lz, cam, niebla, S, ext=180, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_ofi'))

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
    """Losas rotas alrededor de donde sale del suelo y, detras, agujas de catedral."""
    r = random.Random(semilla)
    qs = []
    for k in range(12):                                    # el cerco de losas levantadas
        a = k * TAU / 12 + r.uniform(-0.15, 0.15)
        rr = r.uniform(3.0, 4.6)
        w, h = r.uniform(1.6, 2.8), r.uniform(0.4, 1.0)
        M = (vr.T(math.cos(a) * rr - 0.8, -0.1, math.sin(a) * rr - 6.2) @ vr.Ry(-a) @ vr.Rz(r.uniform(-25, -8) * D))
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


def revelar(lz, cam, W, H, S, n_motas=150, semilla=3, fuerza_vineta=0.45):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, S)
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


NOMBRE = {'O': 'Ofidia, la original (estudio)', 'A': 'Ofidia de la Capucha', 'B': 'Ofidia de los Faroles', 'C': 'Ofidia Encadenada'}
SUB_HEROE = {
    'O': 'flota: costillar abierto, alas de murcielago, boca de dos mitades y la cola hasta la aleta roja',
    'A': 'el mismo cuerpo; la capucha se abre en una capucha de cobra con dos ojos falsos; azul hielo',
    'B': 'el mismo cuerpo; los cebos son faroles con almas: en la cabeza, a los lados y en las alas',
    'C': 'el mismo cuerpo, encadenado: grilletes en las alas, barrotes en el pecho, bozal roto y cuernos',
}
SUB_CABEZA = {
    'O': 'la boca: dos mitades de una caja que se abren en triangulo, colmillos arriba y dientes rojos abajo',
    'A': 'la capucha de cobra se abre detras de la cabeza y sus dos ojos falsos miran',
    'B': 'de cada varilla cuelga un farol con un alma dentro',
    'C': 'el bozal se le ha roto por delante y la mandibula ha quedado libre',
}
CAMARA_HEROE = ((7.0, 4.0, 30.0), (0.0, 15.2, 0.0), 62)
CAMARA_CABEZA = ((-8.0, 13.5, 22.0), (0.0, 19.8, 3.0), 52)


def escena(cual, camara, nombre, sub, n_motas):
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    explanada(lz, cam, niebla, S)
    qs, info = om.ofidia(cual)
    om.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
    img = revelar(lz, cam, W, H, S, n_motas=n_motas)
    return qe.rotular(img, nombre, sub)


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE, NOMBRE[cual], SUB_HEROE[cual], 150), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA, NOMBRE[cual], SUB_CABEZA[cual], 90), 'cabeza_' + cual)


def cuatro():
    """Las cuatro juntas, con la misma luz neutra y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = dict(luces=[((-0.4, 0.8, 0.8), (0.82, 0.82, 0.9), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.9, 0.85, 1.0), 0.8, 'contra')],
             amb=(0.22, 0.21, 0.26), niebla=(0.06, 0.05, 0.09), niebla_d=(180, 330),
             cielo=((0.01, 0.012, 0.03), (0.05, 0.05, 0.1), (0.16, 0.13, 0.22)), motas=(230, 230, 255))
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    cam = vr.Camara((0.0, 14.0, 215.0), (0.0, 14.0, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=280, paso=32, cerca=40)
    for cual, x in (('O', -60.0), ('A', -20.0), ('B', 20.0), ('C', 60.0)):
        qs, info = om.ofidia(cual)
        om.dibujar(lz, cam, qm.transformar(qs, vr.T(x, 0, 0)), S['luces'], S['amb'], niebla)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(0.0, 20.0, 0)), S['luces'], S['amb'], niebla)
    img = revelar(lz, cam, W, H, S, n_motas=0)
    P = np.array([p for q in om.ofidia('O')[0] for p in q[0]])
    guardar(qe.rotular(img, 'La original y sus tres variantes', 'la original · de la Capucha · de los Faroles · Encadenada · '
                       'un jugador (1,8) delante · unos %.0f bloques de alto' % P[:, 1].max()), 'cuatro')


def materiales():
    W = 1600
    filas = []
    for c in 'OABC':
        P = om.pintores(om.VARIANTES[c])
        propio = {'O': ('vara', 'varilla', 'der', 4, 20), 'A': ('cobra', 'capucha', 'frente', 40, 34),
                  'B': ('hierro', 'hierro', 'der', 8, 16), 'C': ('oxido', 'oxido', 'der', 8, 16)}[c]
        fila = [(P['marmol'], 'marmol', 'der', 24, 24), (P['cinto'], 'cinturon', 'frente', 24, 6), (P['capucha'], 'capucha', 'arriba', 24, 24),
                (P['colmillo'], 'colmillo', 'frente', 4, 16), (P['pecho'], 'costillar', 'frente', 24, 24),
                (P['membrana'], 'membrana', 'frente', 32, 24), (P['nucleo'], 'garganta', 'frente', 24, 24),
                (P[propio[0]], propio[1], propio[2], propio[3], propio[4])]
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


CAMARA_CARTEL = ((-9.0, 10.0, 25.0), (0.0, 18.6, 2.0), 46)
CAMARA_FRENTE = ((0.0, 16.0, 24.0), (0.0, 19.4, 3.0), 44)
CAMARA_LADO = ((-52.0, 15.0, 2.0), (0.0, 15.5, 1.5), 44)


def cartel(cual):
    """La misma vista que el cartel (de abajo y de tres cuartos), para compararla con el."""
    guardar(escena(cual, CAMARA_CARTEL, NOMBRE[cual], SUB_CABEZA[cual], 60), 'cartel_' + cual)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'OABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'OABC'})
ESCENAS.update({'cuatro': cuatro, 'materiales': materiales})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'OABC'})
ESCENAS.update({'lado_' + c: (lambda c=c: guardar(escena(c, CAMARA_LADO, NOMBRE[c], SUB_CABEZA[c], 30), 'lado_' + c)) for c in 'OABC'})
ESCENAS.update({'frente_' + c: (lambda c=c: guardar(escena(c, CAMARA_FRENTE, NOMBRE[c], SUB_CABEZA[c], 40), 'frente_' + c)) for c in 'OABC'})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

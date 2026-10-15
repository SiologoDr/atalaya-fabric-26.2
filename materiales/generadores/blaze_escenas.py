"""
Renders del rediseno del Blaze (15-10-2026): los tres disenos en la fortaleza del Nether (el suelo de ladrillo, los
pilares con sus braseros, la muralla, las cascadas de lava y los riscos), a la escala de Minecraft; su cartel (de cerca
y desde abajo); la cabeza (de cerca); los tres juntos con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python blaze_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import eclipse_modelo as em
import blaze_modelo as am

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


# el aire del Nether de cada diseno: (cielo arriba, en medio, en el horizonte), niebla, ambiente, luz de la lava
NETHER = {
    'A': (((0.06, 0.01, 0.01), (0.22, 0.05, 0.03), (0.46, 0.12, 0.05)), (0.24, 0.06, 0.03), (0.3, 0.16, 0.14), (1.0, 0.56, 0.24)),
    'B': (((0.05, 0.01, 0.01), (0.2, 0.03, 0.02), (0.42, 0.08, 0.04)), (0.22, 0.04, 0.03), (0.28, 0.14, 0.13), (1.0, 0.46, 0.2)),
    'C': (((0.01, 0.02, 0.05), (0.04, 0.08, 0.14), (0.1, 0.2, 0.28)), (0.05, 0.1, 0.14), (0.16, 0.2, 0.26), (0.5, 0.8, 1.0)),
}


def sitio(v):
    """La misma fortaleza para los tres (en el de las Lanzas, el aire azul del valle de las almas); la luz sube de la
    lava."""
    cielo, niebla, amb, luz = NETHER[v]
    return dict(
        luces=[((-0.4, 0.7, 0.5), tuple(0.7 * c for c in luz), 0.7, 'llave'), ((-0.5, 0.35, -1.0), luz, 1.0, 'contra'),
               ((0.5, -0.4, 0.7), luz, 0.45, 'llave')],
        amb=amb, niebla=niebla, niebla_d=(10, 60), cielo=cielo, sol=luz,
        motas=tuple(int(255 * min(1.0, 0.4 + c)) for c in luz),
    )


# ----------------------------------------------------------------------
#  La fortaleza: el suelo de ladrillo, los pilares, la valla, las cascadas y los lagos de lava
# ----------------------------------------------------------------------
def _ladrillo(semilla, rampa, junta):
    """El ladrillo de la fortaleza, 16 x 16 por bloque: hiladas desfasadas, la junta oscura y el canto claro arriba."""
    n = 16
    rng = random.Random(semilla)
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        fila = y // 4
        for x in range(n):
            xx = (x + (fila % 2) * 4) % 8
            if y % 4 == 3 or xx == 7:
                c = junta
            elif y % 4 == 0:
                c = rampa[3]
            else:
                c = rampa[2]
            t[y, x] = (*c, 255)
    for _ in range(10):
        x, y = rng.randrange(n), rng.randrange(n)
        if t[y, x, 0] != junta[0]:
            t[y, x] = (*rampa[1], 255)
    return t


LADRILLO = _r('120608', '1e0a0e', '2c1016', '3c181e', '4c2228')
JUNTA = (8, 3, 4)
qm._reg('suelo_bzA', _ladrillo(31, LADRILLO, JUNTA))
qm._reg('suelo_bzB', _ladrillo(31, LADRILLO, JUNTA))
qm._reg('suelo_bzC', _ladrillo(31, LADRILLO, JUNTA))


def p_ladrillo(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    fila = ys // 4
    xx = (xs + (fila % 2) * 4) % 8
    idx = np.where((ys % 4 == 3) | (xx == 7), 0, np.where(ys % 4 == 0, 3, 2))
    return bm._imagen(idx, LADRILLO), None


def p_roca(tw, th, cara, s):
    """La roca del Nether: roja oscura, con manchas limpias."""
    idx = sm._manchas(tw, th, s, celda=4.0, umbral=0.58, alto=0.85)
    return bm._imagen(np.array([1, 2, 2, 3, 3])[idx], _r('1e0606', '300a0a', '461212', '5c1a18', '742620')), None


def p_lava(tw, th, cara, s):
    """La lava: naranja con las vetas claras que corren, y la costra oscura en manchas."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (255, 120, 20, 255)
    t[((xs + ys * 2 + s) % 7) < 2] = (255, 200, 80, 255)
    t[((xs * 3 + ys + s) % 11) == 0] = (200, 60, 10, 255)
    return t, None


def p_alma(tw, th, cara, s):
    """El fuego de alma de los braseros del Heraldo: azul, con el centro claro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (60, 200, 255, 255)
    t[((xs + ys) % 3) == 0] = (200, 250, 255, 255)
    return t, None


for _n, _f in (('ladrillo', p_ladrillo), ('roca', p_roca), ('lava', p_lava), ('alma', p_alma)):
    _f.__name__ = 'bzE_' + _n
bm.PLENOS.add(p_lava)
bm.PLENOS.add(p_alma)


def suelo(lz, cam, niebla, S, ext=60, paso=8, cerca=16, paso_cerca=2, tipo='A'):
    qs = []

    def baldosa(gx, gz, p):
        k = p
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_bz' + tipo))

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


def bioma(lz, cam, niebla, S, tipo='A', semilla=4, libre=None):
    """La fortaleza alrededor (sin nada entre la camara y el blaze): los pilares de ladrillo con su remate, la valla
    entre ellos, los braseros, las cascadas de lava a lo lejos y los riscos del Nether."""
    r = random.Random(semilla)
    qs = []
    libre = libre or (lambda x, z: False)
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    lejos = hacia_camara + math.pi
    fuego = p_alma if tipo == 'C' else p_lava
    for k, (rr, dg) in enumerate(((9, -0.9), (9, 0.9), (13, -0.35), (13, 0.35), (17, -1.4), (17, 1.4))):
        a = lejos + dg
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        if libre(x, z):
            continue
        M = vr.T(x, 0.0, z)
        bm.cubo(qs, M, -1.0, 0.0, -1.0, 2.0, 9.0, 2.0, p_ladrillo, semilla=k)                     # el pilar
        bm.cubo(qs, M, -1.4, 9.0, -1.4, 2.8, 1.0, 2.8, p_ladrillo, semilla=k + 1)
        bm.cubo(qs, M, -0.5, 10.0, -0.5, 1.0, 0.6, 1.0, fuego, semilla=k)                          # el brasero
    for k in range(-6, 7):                                                                          # la muralla del fondo
        a = lejos
        cx, cz = math.cos(a) * 22, math.sin(a) * 22
        tx, tz = -math.sin(a), math.cos(a)
        x, z = cx + tx * k * 2.0, cz + tz * k * 2.0
        M = vr.T(x, 0.0, z) @ vr.Ry(-a)
        bm.cubo(qs, M, -1.0, 0.0, -1.0, 2.0, 5.0 + (k % 2) * 1.0, 2.0, p_ladrillo, semilla=k + 20)
        if k % 3 == 0:
            for y in (5.6, 6.6):                                                                     # la valla de arriba
                bm.cubo(qs, M, -0.1, y, -1.0, 0.2, 0.2, 2.0, p_ladrillo, semilla=k)
    for k in range(4):                                                                              # las cascadas de lava
        a = lejos + r.uniform(-1.0, 1.0)
        x, z = math.cos(a) * r.uniform(34, 44), math.sin(a) * r.uniform(34, 44)
        bm.cubo(qs, vr.T(x, 0.0, z) @ vr.Ry(-a), -1.0, 0.0, -1.0, 2.0, 30.0, 0.6, fuego, semilla=k)
        bm.cubo(qs, vr.T(x, 0.0, z) @ vr.Ry(-a), -3.0, 0.0, -3.0, 6.0, 0.3, 6.0, fuego, semilla=k)
    for k in range(10):                                                                             # los riscos del Nether
        a = lejos + r.uniform(-1.4, 1.4)
        rr = r.uniform(46, 60)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w, alto = r.uniform(10, 18), r.uniform(14, 34)
        for j in range(5):
            f = 1.0 - j / 5 * 0.7
            bm.cubo(qs, vr.T(x, alto * j / 5, z) @ vr.Ry(k), -w * f / 2, 0.0, -w * f / 2, w * f, alto / 5, w * f, p_roca,
                    semilla=k + j)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S, sol_x=0.18):
    """El atardecer: violeta arriba, rosa en medio y melocoton en el horizonte, con el resplandor del sol a la izquierda
    y unas nubes largas y finas, encendidas por debajo."""
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.55, arriba + (medio - arriba) * (k / 0.55), medio + (abajo - medio) * ((k - 0.55) / 0.45))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W * sol_x) / W, (yy - horizonte) / H * 1.6)
    col += np.array(S['sol'])[None, None, :] * (np.exp(-(d / 0.22) ** 2) * 0.45)[..., None]
    r = random.Random(11)
    for _ in range(9):                                                  # las nubes
        cy = r.uniform(0.18, 0.62) * horizonte
        cx, L, g = r.uniform(-0.1, 1.0) * W, r.uniform(0.12, 0.4) * W, max(2, int(r.uniform(0.006, 0.014) * H))
        luz = np.array(S['sol']) * (0.55 + 0.35 * cy / max(horizonte, 1))
        sombra = np.array(S['cielo'][1]) * 0.85
        y0, y1 = int(cy), int(cy + g)
        x0, x1 = int(max(0, cx)), int(min(W, cx + L))
        if x1 > x0 and y1 > y0:
            col[y0:y1, x0:x1] = sombra
            col[y1 - 1:y1 + max(1, g // 3), x0 + 2:x1 - 2] = luz
    return np.clip(col, 0, 1)


def motas(img, n, semilla, color):
    """Las chispas y la ceniza que suben de la lava."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(H * 0.35, H)
        g = max(1, int(r.choice((1, 2, 2, 3)) * W / 1600))
        d.rectangle((x, y, x + g, y + g), fill=(*color, r.randint(150, 240)))
    glow = capa.filter(ImageFilter.GaussianBlur(4))
    return Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), glow), capa)


def revelar(lz, cam, W, H, S, n_motas=60, semilla=3, fuerza_vineta=0.35, brillo=0.9):
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
        qs, info = am.blaze(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras, a la escala de un mob: 'heroe' (de cuerpo entero, de tres cuartos y bajo), 'cabeza' (de cerca y un
    poco por debajo) y 'cartel' (de cerca y desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    alto = max(h, (hi[0] - lo[0]) * 0.7)
    c = np.asarray(info['cabeza'], float)
    if vista == 'heroe':
        obj = np.array((0.0, h * 0.5, 0.2))
        ojo = obj + np.array((0.42, 0.0, 0.9)) * alto * 1.75
        ojo[1] = 0.8
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        ojo = c + np.array((0.7, -0.4, 1.9))
        return tuple(ojo), tuple(c + np.array((0.0, -0.1, -0.4))), 56
    obj = np.array((0.0, h * 0.6, 0.3))
    ojo = obj + np.array((0.4, 0.0, 0.92)) * alto * 1.15
    ojo[1] = 0.4
    return tuple(ojo), tuple(obj), 66


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: la fortaleza; el blaze, con la luz de su nucleo y de su cara; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    suelo(lz, cam, niebla, S, tipo=cual)
    bioma(lz, cam, niebla, S, tipo=cual, libre=lambda x, z: lo[0] - 1.5 < x < hi[0] + 1.5 and lo[2] - 1.5 < z < hi[2] + 1.5
          or abs(x - ojo[0]) < 2 and abs(z - ojo[2]) < 2)
    neo = _c(info['luz'])
    luces = S['luces'] + [(tuple(p) + (1.6,), neo, 1.0, 'punto') for p in info['luces'][:2]]
    z0 = lz.z.copy()
    am.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe', 60), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 30), 'cabeza_' + cual)


def cartel(cual):
    """La presentacion del cartel: de cerca y desde abajo, con el cielo de su noche."""
    guardar(escena(cual, 'cartel', 40, brillo=1.2), 'cartel_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos, con la misma luz y un jugador al lado, en la fortaleza."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 30, 80)
    cam = vr.Camara((0.0, 1.8, 19.0), (0.0, 2.4, 0.0), 32, W * SS, H * SS)
    suelo(lz, cam, niebla, S, tipo='A')
    bioma(lz, cam, niebla, S, tipo='A', semilla=8, libre=lambda x, z: abs(x) < 9 and -4 < z < 18)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('V', -7.6), ('A', -3.6), ('B', 1.4), ('C', 6.0)):
        qs, info, P = modelo(cual) if cual != 'V' else (am.vanilla_a_escala()[0], None, None)
        qs = qm.transformar(qs, vr.T(x, 0, 0))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-5.8, 2.4, 180)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=40), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por blaze. Espadas: la piel, la cara, la vara, la hoja, la guarda y
    el puno. Cristales: la piel, la cara, el nucleo, el cuerno y el cristal en la base y en la punta. Lanzas: la piel, la cara, el asta, la
    punta y el cuerno."""
    W = 1240
    A, B, C = (am.pintores(am.VARIANTES[c]) for c in 'ABC')
    filas = [[(A['piel'], 'der', 12, 12), (A['cara'], 'frente', 8, 8), (A['vara'], 'der', 4, 16),
              (A['hoja_espada'], 'frente', 10, 36), (A['guarda'], 'frente', 4, 4), (A['puno'], 'der', 2, 7)],
             [(B['piel'], 'der', 12, 12), (B['cara'], 'frente', 10, 12), (B['nucleo'], 'frente', 3, 3),
              (B['cuerno'], 'der', 3, 6), (B['cristal0'], 'der', 5, 8), (B['cristal2'], 'der', 3, 5)],
             [(C['piel'], 'der', 12, 12), (C['cara'], 'frente', 10, 10), (C['asta'], 'der', 2, 18),
              (C['punta'], 'frente', 7, 9), (C['cuerno'], 'der', 2, 6)]]
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (22, 18, 20))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (46, 40, 44, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 192
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(76, 66, 72))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})
PRUEBAS = {}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        (ESCENAS.get(k) or PRUEBAS[k])()

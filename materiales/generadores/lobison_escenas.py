"""
Renders del Lobison (15-10-2026), el primer mob normal: cada tipo en su sitio y de noche con luna llena (el del Monte en
un bosque de arboles de bloques, el de la Nieve entre abetos nevados y el del Paramo entre cactos y mesetas de
terracota), a la escala de Minecraft; su cartel (de cerca y desde abajo); la cabeza (de cerca); los tres juntos con un
jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python lobison_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import lobison_modelo as am

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


# la noche de luna llena de cada tipo: (cielo arriba, en medio, en el horizonte), niebla, ambiente, luna
NOCHE = {
    'A': (((0.01, 0.02, 0.05), (0.05, 0.09, 0.16), (0.16, 0.22, 0.32)), (0.06, 0.09, 0.14), (0.2, 0.22, 0.3), (0.86, 0.9, 1.0)),
    'B': (((0.02, 0.03, 0.07), (0.1, 0.14, 0.24), (0.28, 0.34, 0.46)), (0.14, 0.18, 0.26), (0.26, 0.28, 0.36), (0.88, 0.94, 1.0)),
    'C': (((0.03, 0.02, 0.05), (0.14, 0.07, 0.12), (0.4, 0.18, 0.16)), (0.16, 0.08, 0.08), (0.24, 0.2, 0.26), (0.98, 0.9, 0.86)),
}


def sitio(v):
    """Cada tipo en su sitio, de noche con luna llena: la luna detras, a la izquierda."""
    cielo, niebla, amb, luna = NOCHE[v]
    return dict(
        luces=[((-0.5, 0.7, 0.5), luna, 0.85, 'llave'), ((-0.5, 0.45, -1.0), luna, 1.1, 'contra'),
               ((0.7, 0.3, 0.6), (0.4, 0.46, 0.6), 0.3, 'llave')],
        amb=amb, niebla=niebla, niebla_d=(10, 70), cielo=cielo, sol=luna, motas=(230, 236, 255),
    )


# ----------------------------------------------------------------------
#  Los tres sitios, a la escala de Minecraft (16 texeles por bloque): el monte, la nieve y el paramo
# ----------------------------------------------------------------------
def _suelo_bloque(semilla, rampa, motas=None, rayas=False):
    """Un suelo de 16 x 16 por bloque, repetido: el tono de fondo con manchas pequenas y limpias de dos tonos."""
    n = 16
    rng = random.Random(semilla)
    t = np.zeros((n, n, 4), np.uint8)
    t[...] = (*rampa[2], 255)
    for _ in range(26):
        x, y = rng.randrange(n), rng.randrange(n)
        c = rampa[rng.choice((1, 3, 3))]
        t[y, x] = (*c, 255)
        if rng.random() < 0.5:
            t[y, (x + 1) % n] = (*c, 255)
    if rayas:
        for y in range(n):
            if y % 5 == 0:
                t[y, :] = (*rampa[1], 255)
    if motas:
        for _ in range(6):
            x, y = rng.randrange(n), rng.randrange(n)
            t[y, x] = (*motas, 255)
    return t


SUELOS = {
    'A': _suelo_bloque(11, _r('142410', '1e3416', '28461c', '345a24', '42702e')),
    'B': _suelo_bloque(12, _r('8c96a8', 'b4bcc8', 'd6dce4', 'eaeef2', 'f8fafc')),
    'C': _suelo_bloque(13, _r('5a2410', '7c3416', '9c461c', 'b85a26', 'd07234'), rayas=False),
}
for _k, _t in SUELOS.items():
    qm._reg('suelo_lob' + _k, _t)


def _pin(rampa, borde=True):
    def f(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where(((xs + ys * 3 + s) % 7) < 2, 3, np.where(((xs * 5 + ys + s) % 9) < 2, 1, 2))
        if cara == 'arriba':
            idx = np.clip(idx + 1, 0, 4)
        return bm._imagen(sm._bisel(idx, 1, 1) if borde else idx, rampa), None
    return f


p_tronco = _pin(_r('1e140c', '2c1e12', '3c2a1a', '4e3824', '624830'))
p_hojas = _pin(_r('08160a', '0e2010', '142c16', '1c3a1e', '264a28'), borde=False)
p_abeto = _pin(_r('061210', '0a1a16', '10241e', '163028', '1e3e34'), borde=False)
p_nieve = _pin(_r('9aa4b4', 'c0c8d4', 'dce2ea', 'eef2f6', 'fafcfe'), borde=False)
p_roca = _pin(_r('1e1e22', '2c2c32', '3c3c44', '4e4e58', '62626e'))
p_terracota = _pin(_r('3a160a', '5a2210', '7a3016', 'a0441e', 'c45a28'))
p_terracota2 = _pin(_r('4a3a2a', '6a5640', '8a7458', 'aa9272', 'c8b08e'))
p_cacto = _pin(_r('0c2010', '123018', '1a4422', '24582c', '307038'))
p_arbusto = _pin(_r('2a1a0c', '3e2814', '54381e', '6c4a28', '865e34'), borde=False)
for _n, _f in (('tronco', p_tronco), ('hojas', p_hojas), ('abeto', p_abeto), ('nieve', p_nieve), ('roca', p_roca),
               ('terracota', p_terracota), ('terracota2', p_terracota2), ('cacto', p_cacto), ('arbusto', p_arbusto)):
    _f.__name__ = 'lobE_' + _n


def suelo(lz, cam, niebla, S, ext=80, paso=8, cerca=16, paso_cerca=2, tipo='A'):
    qs = []

    def baldosa(gx, gz, p):
        k = p
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_lob' + tipo))

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


def arbol(qs, x, z, alto, semilla, nevado=False):
    """Un arbol de bloques: el tronco de 1 x 1 y la copa de hojas en capas (en la nieve, un abeto con nieve encima)."""
    rng = random.Random(semilla)
    M = vr.T(x, 0.0, z)
    bm.cubo(qs, M, -0.5, 0.0, -0.5, 1.0, alto, 1.0, p_tronco, semilla=semilla)
    if nevado:
        for j, w in enumerate((5, 5, 3, 3, 1)):
            y = alto - 4 + j
            bm.cubo(qs, M, -w / 2, y, -w / 2, w, 1.0, w, p_abeto, caras={'arriba': p_nieve}, semilla=j)
        bm.cubo(qs, M, -0.5, alto + 1, -0.5, 1.0, 1.0, 1.0, p_abeto, caras={'arriba': p_nieve}, semilla=9)
        return
    for j, w in enumerate((5, 5, 3, 3)):
        y = alto - 3 + j
        bm.cubo(qs, M, -w / 2, y, -w / 2, w, 1.0, w, p_hojas, semilla=j + rng.randrange(3))


def paramo(qs, r, libre, hacia_camara):
    """El paramo: los cactos, las matas secas y, al fondo, las mesetas de terracota en franjas."""
    for k in range(40):
        a = r.uniform(0, TAU)
        rr = r.uniform(4, 30)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.5 and rr < 18:
            continue
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        if libre(x, z):
            continue
        if k % 3 == 0:
            h = r.randint(2, 3)
            bm.cubo(qs, vr.T(x, 0.0, z), -0.44, 0.0, -0.44, 0.88, h, 0.88, p_cacto, semilla=k)
        else:
            for j in range(3):
                bm.cubo(qs, vr.T(x + r.uniform(-0.3, 0.3), 0.0, z + r.uniform(-0.3, 0.3)) @ vr.Ry(j), -0.05, 0.0, -0.4, 0.1,
                        r.uniform(0.5, 0.9), 0.8, p_arbusto, semilla=j)
    lejos = hacia_camara + math.pi
    for k in range(8):
        a = lejos + r.uniform(-1.2, 1.2)
        rr = r.uniform(40, 70)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w, alto = r.uniform(12, 24), r.randint(8, 16)
        for j in range(alto):
            f = 1.0 - (j / alto) ** 3 * 0.3
            pin = p_terracota if (j // 2) % 2 == 0 else p_terracota2
            bm.cubo(qs, vr.T(x, j, z) @ vr.Ry(k), -w * f / 2, 0.0, -w * f / 2, w * f, 1.0, w * f * 0.8, pin, semilla=k + j)


def bioma(lz, cam, niebla, S, tipo='A', semilla=4, libre=None):
    """Los arboles (o los abetos nevados, o el paramo) alrededor, sin nada entre la camara y el mob, y las rocas."""
    r = random.Random(semilla)
    qs = []
    libre = libre or (lambda x, z: False)
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    if tipo == 'C':
        paramo(qs, r, libre, hacia_camara)
    else:
        for k in range(46):
            a = r.uniform(0, TAU)
            rr = r.uniform(5, 40)
            if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.55 and rr < 24:
                continue
            x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
            if libre(x, z):
                continue
            arbol(qs, x, z, r.randint(5, 8), k, nevado=tipo == 'B')
    for k in range(10):
        a = r.uniform(0, TAU)
        rr = r.uniform(3, 14)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.6:
            continue
        x, z = round(math.cos(a) * rr), round(math.sin(a) * rr)
        if libre(x, z):
            continue
        bm.cubo(qs, vr.T(x, 0.0, z), -0.5, 0.0, -0.5, 1.0, 1.0, 1.0, p_roca,
                caras={'arriba': p_nieve} if tipo == 'B' else None, semilla=k)
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
    """Las motas de polvo que brillan con la luna."""
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
        qs, info = am.lobison(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras, a la escala de un mob: 'heroe' (de cuerpo entero, de tres cuartos y bajo), 'cabeza' (de cerca, un
    poco por debajo, para mirar la boca) y 'cartel' (de cerca y desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    b = np.asarray(info['boca'], float)
    if vista == 'heroe':
        obj = np.array((0.0, h * 0.5, 0.3))
        ojo = obj + np.array((0.5, 0.0, 0.87)) * 5.2
        ojo[1] = 0.6
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        ojo = b + np.array((0.6, -0.3, 1.3))
        return tuple(ojo), tuple(b + np.array((0.0, 0.05, -0.3))), 56
    obj = np.array((0.0, h * 0.62, 0.4))
    ojo = obj + np.array((0.45, 0.0, 0.89)) * 3.4
    ojo[1] = 0.35
    return tuple(ojo), tuple(obj), 66


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: el sitio de cada tipo; el Lobison, con la luz de su boca y de sus ojos; el contorno blanco; sin letras."""
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
    neo = _c(am.VARIANTES[cual]['neon'][1])
    luces = S['luces'] + [(tuple(p) + (0.6,), neo, 0.8, 'punto') for p in info['luces'][:2]]
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
    """Los tres juntos, con la misma luz y un jugador al lado, en la nieve del monte (un claro)."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 20, 70)
    cam = vr.Camara((0.0, 1.3, 11.0), (0.0, 1.3, 0.0), 32, W * SS, H * SS)
    suelo(lz, cam, niebla, S, tipo='A')
    bioma(lz, cam, niebla, S, tipo='A', semilla=8, libre=lambda x, z: abs(x) < 7 and -3 < z < 12)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -3.2), ('B', 0.0), ('C', 3.2)):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(0.25))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-1.6, 1.4, 180)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo y, de izquierda a derecha, el pelo, el pelo largo, el
    pecho, la cara, el hocico, la boca, los dientes, la oreja, la garra y el hueso."""
    W = 2000
    filas = []
    for c in formas:
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['pelo'], 'der', 16, 16), (P['pelo_largo'], 'arriba', 8, 16), (P['pecho'], 'frente', 12, 12),
                      (P['cara'], 'frente', 8, 7), (P['hocico'], 'frente', 4, 3), (P['boca'], 'abajo', 4, 5),
                      (P['dientes'], 'frente', 4, 2), (P['oreja'], 'frente', 3, 4), (P['garra'], 'frente', 2, 4),
                      (P['hueso'], 'frente', 2, 4)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (22, 20, 24))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (46, 42, 50, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 192
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(76, 70, 84))
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

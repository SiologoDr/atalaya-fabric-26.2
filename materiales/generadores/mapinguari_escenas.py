"""
Renders del Mapinguari (15-10-2026): sus tres tipos en la selva de noche, con la luna que entra en haces entre los arboles
(los troncos gigantes con sus raices en tabla, las lianas, las hojas grandes, los helechos, la hojarasca y las
luciernagas); su cartel (de cerca y desde abajo); el pecho y la cabeza (de cerca, para mirar las fauces de costillas y el
corazon); los tres juntos con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python mapinguari_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import mapinguari_modelo as am

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


# el cielo de cada tipo, entre las copas: (arriba, en medio, en el horizonte), niebla, ambiente, luna
CIELO = {
    'A': (((0.02, 0.05, 0.06), (0.06, 0.16, 0.16), (0.16, 0.32, 0.3)), (0.08, 0.16, 0.14), (0.2, 0.26, 0.26), (0.62, 0.82, 0.86)),
    'B': (((0.05, 0.02, 0.06), (0.16, 0.06, 0.12), (0.34, 0.14, 0.2)), (0.14, 0.08, 0.12), (0.24, 0.2, 0.26), (0.82, 0.7, 0.86)),
    'C': (((0.06, 0.05, 0.04), (0.2, 0.14, 0.08), (0.44, 0.3, 0.16)), (0.18, 0.14, 0.08), (0.26, 0.24, 0.2), (0.9, 0.8, 0.62)),
}


def sitio(v):
    """La misma selva para los tres, de noche: la luna entra por arriba, a la izquierda."""
    cielo, niebla, amb, luna = CIELO[v]
    return dict(
        luces=[((-0.45, 0.8, 0.4), luna, 0.85, 'llave'), ((-0.4, 0.5, -1.0), luna, 0.9, 'contra'),
               ((0.6, 0.3, 0.6), (0.3, 0.36, 0.4), 0.3, 'llave')],
        amb=amb, niebla=niebla, niebla_d=(40, 190), cielo=cielo, sol=luna, motas=(214, 255, 120),
    )


# ----------------------------------------------------------------------
#  La selva: la hojarasca, los troncos con sus raices en tabla, las lianas, las hojas grandes y los helechos
# ----------------------------------------------------------------------
HOJARASCA = _r('120e08', '1c160c', '2a2012', '3a2e18', '4a3c20')
qm._reg('suelo_map', qm._suelo_grande(733, HOJARASCA, (70, 90, 40), grietas=False))


def p_corteza(tw, th, cara, s):
    """La corteza: surcos a lo largo, oscuros, con manchas de musgo."""
    ys, xs = np.mgrid[0:th, 0:tw]
    a_lo_largo, de_traves = (ys, xs) if cara in ('arriba', 'abajo') else (xs, ys)
    idx = np.where(de_traves % 4 == 0, 1, 2)
    idx = np.where((de_traves + a_lo_largo // 6) % 9 == 0, 3, idx)
    img = bm._imagen(sm._bisel(idx, 1, 1), _r('0e0c0a', '1a1612', '28221a', '383024', '4a4030'))
    m = sm._manchas(tw, th, s, celda=6.0, umbral=0.68, alto=0.9) >= 3
    img = np.where(m[..., None], bm._imagen(np.full((th, tw), 2), _r('0e1a0c', '162812', '22381a', '304a24', '405e30')), img)
    return img, None


def p_hoja_grande(tw, th, cara, s):
    """La hoja grande, de oreja de elefante: verde oscuro con el nervio y los nervios de los lados, en punta."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t_ = ys / max(th - 1, 1)
    ancho = np.sin(np.pi * np.clip(t_ * 0.9 + 0.1, 0, 1))
    dentro = abs(xs - (tw - 1) / 2) <= (tw / 2) * ancho + 0.3
    idx = np.where(abs(xs - (tw - 1) / 2) < 0.7, 3, np.where((ys + abs(xs - tw // 2)) % 6 == 0, 3, 2))
    img = bm._imagen(idx, _r('06120a', '0c2012', '14301a', '1e4424', '2c5c30'))
    img[..., 3] = np.where(dentro, 255, 0)
    return img, None


def p_tallo(tw, th, cara, s):
    return bm._imagen(np.full((th, tw), 2), _r('08140a', '0e2010', '163018', '204220', '2c582a')), None


def p_copa(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=5.0, umbral=0.55, alto=0.8)
    return bm._imagen(np.array([1, 1, 2, 2, 3])[idx], _r('040806', '060e08', '0a160c', '0e1e10', '142814')), None


for _f in (p_corteza, p_hoja_grande, p_tallo, p_copa):
    _f.__name__ = 'mapE_' + _f.__name__


def suelo(lz, cam, niebla, S, ext=320, paso=32, cerca=60, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_map'))

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


def arbol(qs, x, z, r, alto, semilla):
    """Un arbol gigante: el tronco recto que se pierde arriba y las raices en tabla que salen en estrella."""
    rng = random.Random(semilla)
    for kx, kz in ((1.0, 0.72), (0.72, 1.0)):
        bm.cubo(qs, vr.T(x, 0.0, z), -r * kx, 0.0, -r * kz, 2 * r * kx, alto, 2 * r * kz, p_corteza, semilla=semilla)
    for j in range(5):
        g = TAU * j / 5 + rng.uniform(-0.3, 0.3)
        L, h = r * rng.uniform(2.0, 3.2), r * rng.uniform(2.2, 3.6)
        M = vr.T(x, 0.0, z) @ vr.Ry(g)
        for i in range(4):                                              # la tabla, en escalones que bajan hacia fuera
            f = i / 4
            bm.cubo(qs, M, r * 0.6 + L * f, 0.0, -0.35, L / 4 + 0.2, h * (1 - f), 0.7, p_corteza, semilla=semilla + i)


def mata(qs, x, z, semilla):
    """Una mata de hojas grandes, de oreja de elefante, sobre sus tallos."""
    rng = random.Random(semilla)
    for j in range(6):
        g = TAU * j / 6 + rng.uniform(-0.3, 0.3)
        h = rng.uniform(1.5, 4.0)
        b = np.array((x, h, z))
        bm.cubo(qs, vr.T(x, 0.0, z), -0.12, 0.0, -0.12, 0.24, h, 0.24, p_tallo, semilla=j)
        d = np.array((math.cos(g), -0.25, math.sin(g)))
        l = np.array((-math.sin(g), 0.0, math.cos(g))) * rng.uniform(1.4, 2.2)
        L = rng.uniform(3.0, 5.0)
        p = b + d * L + np.array((0.0, -0.6, 0.0))
        sm.lamina(qs, (p - l * 0.2, p + l * 0.2, b + l, b - l), p_hoja_grande, float(np.linalg.norm(l)) * 2, L, semilla=j)


def selva(lz, cam, niebla, S, semilla=4, libre=None):
    """Los arboles gigantes (sin nada entre la camara y el jefe), las lianas que cuelgan, las matas de hojas grandes y las
    copas, oscuras, arriba."""
    r = random.Random(semilla)
    qs = []
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    for k in range(26):
        a = r.uniform(0, TAU)
        rr = r.uniform(26, 120)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.45 and rr < 80:
            continue
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if libre is not None and libre(x, z):
            continue
        arbol(qs, x, z, r.uniform(2.5, 5.0), 90.0, k)
        for j in range(r.randint(1, 3)):                                # las lianas que cuelgan cerca
            lx, lz_ = x + r.uniform(-8, 8), z + r.uniform(-8, 8)
            if libre is not None and libre(lx, lz_):
                continue
            h0 = r.uniform(4.0, 16.0)
            bm.cubo(qs, vr.T(lx, h0, lz_) @ vr.Rz(r.uniform(-0.08, 0.08)), -0.18, 0.0, -0.18, 0.36, 90.0 - h0, 0.36, p_tallo,
                    semilla=j)
    for k in range(60):
        a = r.uniform(0, TAU)
        rr = r.uniform(12, 90)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.35 and rr < 50:
            continue
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if libre is not None and libre(x, z):
            continue
        mata(qs, x, z, k)
    for k in range(40):                                                 # las copas, arriba, que tapan casi todo el cielo
        a = r.uniform(0, TAU)
        rr = r.uniform(30, 160)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w = r.uniform(20, 46)
        bm.cubo(qs, vr.T(x, r.uniform(58, 80), z) @ vr.Ry(r.uniform(0, 3)), -w / 2, 0.0, -w / 2, w, r.uniform(6, 12), w, p_copa,
                semilla=k)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S, sol_x=0.2):
    """El cielo de la tarde: el color de arriba, el del medio y el del horizonte, el resplandor del sol a la izquierda y
    unas nubes largas, encendidas por debajo."""
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.55, arriba + (medio - arriba) * (k / 0.55), medio + (abajo - medio) * ((k - 0.55) / 0.45))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W * sol_x) / W, (yy - horizonte) / H * 1.6)
    col += np.array(S['sol'])[None, None, :] * (np.exp(-(d / 0.22) ** 2) * 0.45)[..., None]
    r = random.Random(13)
    for _ in range(10):
        cy = r.uniform(0.12, 0.6) * horizonte
        cx, L, g = r.uniform(-0.1, 1.0) * W, r.uniform(0.12, 0.42) * W, max(2, int(r.uniform(0.007, 0.016) * H))
        luz = np.array(S['sol']) * (0.55 + 0.35 * cy / max(horizonte, 1))
        sombra = np.array(S['cielo'][1]) * 0.8
        y0, y1 = int(cy), int(cy + g)
        x0, x1 = int(max(0, cx)), int(min(W, cx + L))
        if x1 > x0 and y1 > y0:
            col[y0:y1, x0:x1] = sombra
            col[y1 - 1:y1 + max(1, g // 3), x0 + 2:x1 - 2] = luz
    return np.clip(col, 0, 1)


def motas(img, n, semilla, color):
    """Las luciernagas de la selva, con su halo."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(H * 0.2, H)
        g = max(1, int(r.choice((1, 1, 2)) * W / 1600))
        d.rectangle((x, y, x + g, y + g), fill=(*color, r.randint(110, 200)))
    glow = capa.filter(ImageFilter.GaussianBlur(3))
    return Image.alpha_composite(Image.alpha_composite(img.convert('RGBA'), glow), capa)


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
        qs, info = am.mapinguari(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras: 'heroe' (de cuerpo entero, de tres cuartos y desde abajo), 'cabeza' (de cerca, el pecho abierto y la
    cabeza, un poco por debajo) y 'cartel' (de cerca y muy desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    c = np.asarray(info['corazon'], float)
    o = np.asarray(info['ojo'], float)
    if vista == 'heroe':
        d = h * 0.5 / math.tan(25 * D) * 1.3
        obj = np.array((0.0, h * 0.48, 2.0))
        ojo = obj + _u3((0.42, 0.0, 0.9)) * d
        ojo[1] = 2.6
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        m = (c + o) / 2
        ojo = m + np.array((6.0, -6.0, 17.0))
        return tuple(ojo), tuple(m + np.array((0.0, -0.5, 0.0))), 52
    obj = np.array((0.0, h * 0.6, 4.0))
    ojo = obj + _u3((0.5, 0.0, 0.86)) * h * 1.05
    ojo[1] = 1.8
    return tuple(ojo), tuple(obj), 66


def _u3(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: la selva; el Mapinguari, con la luz de su corazon y de sus ojos; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    selva(lz, cam, niebla, S, libre=lambda x, z: abs(x) < 18 and abs(z) < 16 or abs(x - ojo[0]) < 10 and abs(z - ojo[2]) < 10)
    qs, info, P = modelo(cual)
    neo = _c(am.VARIANTES[cual]['neon'][1])
    luces = S['luces'] + [(tuple(p) + (10.0,), neo, 1.2, 'punto') for p in info['luces'][:2]]
    z0 = lz.z.copy()
    am.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe', 60), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 30), 'cabeza_' + cual)


def cartel(cual):
    """La presentacion del cartel: de cerca y muy desde abajo, con el cielo de su tipo."""
    guardar(escena(cual, 'cartel', 40, brillo=1.2), 'cartel_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos, con la misma luz y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 220, 480)
    cam = vr.Camara((0.0, 10.0, 170.0), (0.0, 11.0, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=420, paso=32, cerca=40)
    selva(lz, cam, niebla, S, semilla=8, libre=lambda x, z: abs(x) < 60 and -20 < z < 60 or z > 60 and abs(x) < 110)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -34.0), ('B', 0.0), ('C', 34.0)):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(-12 * D if x > 0 else 12 * D if x < 0 else 0))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(16.0, 32.0, 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=30), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo y, de izquierda a derecha, el pelo, el mechon, la cara, la
    cara de hueso, el hueso, la garra, el hueco del pecho, el corazon, el musgo, la liana y la hoja."""
    W = 2200
    filas = []
    for c in formas:
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['pelo'], 'der', 32, 32), (P['mechon'], 'frente', 10, 32), (P['cara'], 'frente', 24, 24),
                      (P['craneo'], 'frente', 26, 24), (P['hueso'], 'der', 24, 6), (P['garra'], 'der', 6, 18),
                      (P['hueco'], 'frente', 24, 32), (P['corazon'], 'frente', 16, 18), (P['musgo'], 'arriba', 24, 24),
                      (P['liana'], 'der', 24, 4), (P['hoja'], 'frente', 12, 18)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (18, 20, 18))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (40, 44, 40, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 194
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(70, 78, 70))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

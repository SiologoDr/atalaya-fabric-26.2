"""
Renders de Salitre, el Capitan Hundido (15-10-2026): sus tres tipos en unas ruinas hundidas (la arena, las torres rotas con
sus faroles de mar, las algas, el coral y un pecio al fondo), con los haces de luz que bajan de la superficie y las
burbujas; su cartel (de cerca y desde abajo); la cabeza (de cerca, con el sombrero y los ojos que arden); los tres juntos
con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python salitre_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import salitre_modelo as am

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


# el agua de cada tipo: (arriba, en medio, abajo), niebla, ambiente, luz de la superficie
AGUA = {
    'A': (((0.36, 0.78, 0.86), (0.06, 0.32, 0.46), (0.02, 0.1, 0.18)), (0.03, 0.16, 0.24), (0.16, 0.3, 0.36), (0.7, 0.96, 1.0)),
    'B': (((0.4, 0.74, 0.62), (0.08, 0.3, 0.3), (0.02, 0.1, 0.1)), (0.04, 0.16, 0.16), (0.2, 0.3, 0.3), (0.86, 1.0, 0.86)),
    'C': (((0.2, 0.4, 0.7), (0.04, 0.12, 0.3), (0.01, 0.03, 0.1)), (0.02, 0.06, 0.16), (0.14, 0.18, 0.3), (0.7, 0.82, 1.0)),
}


def sitio(v):
    """Las mismas ruinas para los tres, bajo el agua: la luz entra desde arriba."""
    cielo, niebla, amb, luz = AGUA[v]
    return dict(
        luces=[((-0.3, 0.9, 0.35), luz, 0.95, 'llave'), ((0.4, 0.6, -1.0), luz, 0.8, 'contra'),
               ((0.6, -0.2, 0.7), (0.2, 0.36, 0.5), 0.3, 'llave')],
        amb=amb, niebla=niebla, niebla_d=(30, 150), cielo=cielo, sol=luz, motas=(190, 240, 255),
    )


# ----------------------------------------------------------------------
#  Las ruinas hundidas: la arena, las torres rotas con sus faroles, las algas, el coral y el pecio
# ----------------------------------------------------------------------
ARENA = _r('2c3a36', '3c4c46', '4e605a', '62766e', '7a8e86')
qm._reg('arena_cap', qm._suelo_grande(919, ARENA, (110, 130, 120), grietas=False))


def p_piedra(tw, th, cara, s):
    """La piedra de las torres: sillares en hileras desfasadas, verdosos, con el musgo del mar."""
    ys, xs = np.mgrid[0:th, 0:tw]
    fila = ys // 4
    junta = (ys % 4 == 3) | (((xs + (fila % 2) * 4) % 8) == 7)
    idx = np.where(junta, 1, 2)
    img = bm._imagen(sm._bisel(idx, 1, 1), _r('0c1616', '142220', '1e302c', '2a403a', '38544c'))
    m = sm._manchas(tw, th, s, celda=6.0, umbral=0.66, alto=0.9) >= 3
    return np.where(m[..., None], bm._imagen(np.full((th, tw), 2), _r('08201a', '0e3024', '164430', '20583c', '2c704a')), img), None


def p_ventana(tw, th, cara, s):
    """La ventana con su farol de mar dentro, encendida."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (150, 240, 230, 255)
    t[(xs + ys) % 3 == 0] = (220, 255, 250, 255)
    t[(xs == 0) | (xs == tw - 1) | (ys == 0)] = (40, 90, 90, 255)
    return t, None


def p_alga(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(ys % 5 == 0, 3, 2)
    return bm._imagen(idx, _r('061a0e', '0c2c16', '144020', '1e582c', '2c703a')), None


def p_coral(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs + ys) % 3 == 0, 4, 2)
    paleta = (_r('4a0a24', '7a1238', 'a81e50', 'd43a6e', 'f46a96'), _r('4a2a04', '7a460a', 'a86812', 'd48c22', 'f4b444'),
              _r('2a0a4a', '42127a', '601ea8', '843ad4', 'aa6af4'))[s % 3]
    return bm._imagen(sm._bisel(idx, 1, 1), paleta), None


def p_casco(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where(ys % 3 == 0, 1, 2)
    return bm._imagen(idx, _r('0c0a08', '18140e', '261e14', '34281a', '443422')), None


for _f in (p_piedra, p_ventana, p_alga, p_coral, p_casco):
    _f.__name__ = 'capE_' + _f.__name__
bm.PLENOS.add(p_ventana)


def suelo(lz, cam, niebla, S, ext=240, paso=32, cerca=60, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'arena_cap'))

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


def torre(qs, x, z, w, alto, semilla):
    """Una torre hundida y rota: el cuerpo de sillares, la corona mordida y las ventanas con su farol."""
    rng = random.Random(semilla)
    M = vr.T(x, 0.0, z) @ vr.Ry(rng.uniform(0, 1.5))
    bm.cubo(qs, M, -w / 2, 0.0, -w / 2, w, alto, w, p_piedra, semilla=semilla)
    for i in range(5):                                                  # la corona rota: almenas de distinta altura
        a = -w / 2 + w * i / 5
        h = rng.uniform(0.0, 5.0)
        if h > 1.0:
            bm.cubo(qs, M, a, alto, -w / 2, w / 5 * 0.8, h, w / 5 * 0.8, p_piedra, semilla=semilla + i)
    for k in range(int(alto // 9)):
        y = 6.0 + k * 9.0
        if rng.random() < 0.6:
            bm.cubo(qs, M, -1.0, y, w / 2 - 0.1, 2.0, 3.0, 0.3, p_ventana, semilla=1)
    bm.cubo(qs, M, -w / 2 - 0.6, alto * 0.3, -w / 2 - 0.6, w + 1.2, 1.2, w + 1.2, p_piedra, semilla=semilla + 7)


def alga(qs, x, z, alto, semilla):
    """Un alga larga que sube ondulando."""
    rng = random.Random(semilla)
    p = np.array((x, 0.0, z))
    n = 8
    for i in range(n):
        q = p + np.array((math.sin(i * 0.9 + semilla) * 0.8, alto / n, math.cos(i * 0.7 + semilla) * 0.5))
        d = q - p
        M = em.marco(p, d, up=(0.0, 0.0, 1.0) if abs(d[1]) > 0.9 * np.linalg.norm(d) else (0.0, 1.0, 0.0))
        bm.cubo(qs, M, -0.7, -0.15, 0.0, 1.4, 0.3, float(np.linalg.norm(d)), p_alga, semilla=i % 3)
        p = q


def ruinas(lz, cam, niebla, S, semilla=5, libre=None):
    """Las torres rotas, las columnas caidas, el pecio, las algas y el coral (sin nada entre la camara y el jefe)."""
    r = random.Random(semilla)
    qs = []
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    for k in range(14):
        a = r.uniform(0, TAU)
        rr = r.uniform(34, 110)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.6 and rr < 90:
            continue
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if libre is not None and libre(x, z):
            continue
        torre(qs, x, z, r.uniform(7, 12), r.uniform(18, 46), k)
    for k in range(70):
        a = r.uniform(0, TAU)
        rr = r.uniform(10, 90)
        if abs(((a - hacia_camara + math.pi) % TAU) - math.pi) < 0.4 and rr < 60:
            continue
        x, z = math.cos(a) * rr, math.sin(a) * rr
        if libre is not None and libre(x, z):
            continue
        if k % 3 == 0:
            alga(qs, x, z, r.uniform(12, 30), k)
        else:                                                           # un racimo de coral
            for j in range(r.randint(2, 4)):
                g = r.uniform(0, TAU)
                h = r.uniform(1.5, 3.5)
                bm.cubo(qs, vr.T(x + math.cos(g), 0.0, z + math.sin(g)) @ vr.Rz(r.uniform(-0.4, 0.4)), -0.4, 0.0, -0.4, 0.8, h, 0.8,
                        p_coral, semilla=k)
    lejos = hacia_camara + math.pi                                      # el pecio, al fondo
    bx, bz = math.cos(lejos + 0.5) * 120, math.sin(lejos + 0.5) * 120
    M = vr.T(bx, -1.0, bz) @ vr.Ry(lejos + 1.2) @ vr.Rz(0.35)
    bm.cubo(qs, M, -5.0, 0.0, -18.0, 10.0, 7.0, 36.0, p_casco, semilla=1)
    bm.cubo(qs, M, -0.5, 7.0, -2.0, 1.0, 26.0, 1.0, p_casco, semilla=2)
    bm.cubo(qs, M, -6.0, 18.0, -1.5, 12.0, 1.0, 1.0, p_casco, semilla=3)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)


def cielo(W, H, horizonte, S, sol_x=0.42):
    """El agua, vista hacia arriba: clara arriba, donde entra la luz, y honda abajo, con los haces de luz que bajan en
    abanico desde la superficie."""
    arriba, medio, abajo = (np.array(c) for c in S['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.5, arriba + (medio - arriba) * (k / 0.5), medio + (abajo - medio) * ((k - 0.5) / 0.5))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    ang = np.arctan2(xx - W * sol_x, yy + H * 0.4)
    r = random.Random(17)
    for _ in range(9):                                                  # los haces de luz
        a0, ancho = r.uniform(-0.6, 0.6), r.uniform(0.02, 0.05)
        m = np.exp(-((ang - a0) / ancho) ** 2) * np.clip(1.0 - yy / (H * 0.95), 0, 1)
        col += np.array(S['sol'])[None, None, :] * (m * r.uniform(0.12, 0.25))[..., None]
    return np.clip(col, 0, 1)


def motas(img, n, semilla, color):
    """Las burbujas que suben: aros pequenos y claros."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H)
        g = max(2, int(r.choice((2, 3, 3, 4, 6)) * W / 1600))
        d.ellipse((x, y, x + g, y + g), outline=(*color, r.randint(120, 220)))
    glow = capa.filter(ImageFilter.GaussianBlur(2))
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
        qs, info = am.salitre(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras: 'heroe' (de cuerpo entero, de tres cuartos y desde abajo), 'cabeza' (de cerca, el sombrero y los ojos)
    y 'cartel' (de cerca y muy desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    o = np.asarray(info['ojos'], float)
    if vista == 'heroe':
        d = h * 0.5 / math.tan(25 * D) * 1.3
        obj = np.array((0.0, h * 0.5, 1.0))
        ojo = obj + _u3((0.35, 0.0, 0.94)) * d
        ojo[1] = 2.4
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        ojo = o + np.array((4.5, -2.6, 11.0))
        return tuple(ojo), tuple(o + np.array((0.0, -0.8, 0.0))), 54
    obj = np.array((0.0, h * 0.6, 2.0))
    ojo = obj + _u3((0.45, 0.0, 0.89)) * h * 1.05
    ojo[1] = 1.6
    return tuple(ojo), tuple(obj), 66


def _u3(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: las ruinas hundidas; Salitre, con la luz de sus ojos; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, S)
    ruinas(lz, cam, niebla, S, libre=lambda x, z: abs(x) < 18 and abs(z) < 14 or abs(x - ojo[0]) < 8 and abs(z - ojo[2]) < 8)
    qs, info, P = modelo(cual)
    neo = _c(am.VARIANTES[cual]['neon'][1])
    luces = S['luces'] + [(tuple(p) + (6.0,), neo, 0.45, 'punto') for p in info['luces'][:2]]
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
    niebla = qe.Niebla(S['niebla'], 150, 320)
    cam = vr.Camara((0.0, 8.0, 175.0), (0.0, 11.0, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=420, paso=32, cerca=40)
    ruinas(lz, cam, niebla, S, semilla=8, libre=lambda x, z: abs(x) < 60 and -20 < z < 60 or z > 60 and abs(x) < 110)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -38.0), ('B', 0.0), ('C', 38.0)):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(-12 * D if x > 0 else 12 * D if x < 0 else 0))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(16.0, 30.0, 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=40), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo y, de izquierda a derecha, la placa, la placa con ribete,
    el bronce, el brazal, el cinturon, el faldon, la cara de la calavera, el tentaculo, sus ventosas, el emblema del
    sombrero, la hoja de la espada y sus dientes."""
    W = 2400
    filas = []
    for c in formas:
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['placa'], 'frente', 36, 36), (P['placa_rib'], 'frente', 24, 26), (P['bronce'], 'frente', 16, 16),
                      (P['brazal'], 'der', 24, 16), (P['cinturon'], 'frente', 30, 10), (P['faldon'], 'frente', 14, 32),
                      (P['cara'], 'frente', 22, 22), (P['tentaculo'], 'der', 24, 4), (P['ventosas'], 'abajo', 4, 24),
                      (P['emblema'], 'frente', 16, 13), (P['hoja'], 'frente', 24, 12), (P['sierra'], 'frente', 24, 6)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (14, 20, 26))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (34, 44, 52, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 194
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(60, 76, 88))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'cartel_' + c: (lambda c=c: cartel(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

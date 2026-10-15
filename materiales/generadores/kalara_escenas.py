"""
Renders de Kalara (15-10-2026): sus tres tipos en el patio de un templo en ruinas al amanecer (las losas, la escalinata
y la puerta del templo detras, los pilares abrazados por las raices de las higueras, los braseros con su humo y los
montes en la niebla); su cartel (de cerca y desde abajo); la cara (de cerca, para mirar dentro de la boca); los tres
juntos con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python kalara_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import kalara_modelo as am

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


# el amanecer de cada tipo: (cielo arriba, en medio, en el horizonte), niebla, ambiente, sol
AMANECER = {
    'A': (((0.22, 0.26, 0.42), (0.78, 0.6, 0.6), (1.0, 0.82, 0.6)), (0.7, 0.62, 0.6), (0.36, 0.34, 0.4), (1.0, 0.84, 0.6)),
    'B': (((0.2, 0.3, 0.42), (0.64, 0.7, 0.66), (0.96, 0.9, 0.7)), (0.62, 0.68, 0.64), (0.32, 0.36, 0.38), (1.0, 0.92, 0.72)),
    'C': (((0.16, 0.14, 0.3), (0.62, 0.42, 0.52), (0.98, 0.66, 0.5)), (0.56, 0.44, 0.5), (0.3, 0.28, 0.36), (1.0, 0.76, 0.56)),
}


def sitio(v):
    """El mismo patio para los tres, al amanecer: el sol sale a la izquierda, detras, entre la niebla."""
    cielo, niebla, amb, sol = AMANECER[v]
    return dict(
        luces=[((-0.7, 0.35, 0.55), sol, 1.0, 'llave'), ((-0.6, 0.3, -1.0), sol, 1.0, 'contra'),
               ((0.6, 0.5, 0.6), (0.5, 0.56, 0.72), 0.32, 'llave')],
        amb=amb, niebla=niebla, niebla_d=(70, 260), cielo=cielo, sol=sol, motas=(255, 238, 200),
    )


# ----------------------------------------------------------------------
#  El patio del templo: las losas, la escalinata, la puerta, los pilares con raices, el incienso y los montes
# ----------------------------------------------------------------------
LOSA = _r('262420', '302d28', '3a3630', '443f38', '4e4840')


def _losas():
    """Las losas del patio: grandes y desiguales, con la junta oscura y el musgo en algunas."""
    n = 128
    rng = random.Random(77)
    t = np.zeros((n, n, 4), np.uint8)
    filas = [0, 30, 52, 88, 128]
    for i in range(len(filas) - 1):
        y0, y1 = filas[i], filas[i + 1]
        x = rng.randrange(0, 40)
        cortes = []
        while x < n + 40:
            cortes.append(x)
            x += rng.randrange(26, 52)
        for j in range(len(cortes) - 1):
            tono = rng.choice((1, 2, 2, 3))
            for y in range(y0, y1):
                for xx in range(cortes[j], cortes[j + 1]):
                    c = LOSA[tono]
                    if y == y0 or xx == cortes[j]:
                        c = LOSA[0]
                    elif y == y0 + 1 or xx == cortes[j] + 1:
                        c = LOSA[min(4, tono + 1)]
                    t[y % n, xx % n] = (*c, 255)
    return t


qm._reg('losas_kal', _losas())


def p_piedra(tw, th, cara, s):
    """La piedra labrada del templo: sillares en hileras, con su junta y el bisel."""
    ys, xs = np.mgrid[0:th, 0:tw]
    fila = ys // 8
    junta = (ys % 8 == 7) | (((xs + (fila % 2) * 7) % 14) == 13)
    idx = np.where(junta, 1, 2)
    idx = np.where((ys % 8 == 0) & ~junta, 3, idx)
    return bm._imagen(idx, _r('2a2622', '3c3730', '4e4840', '625a50', '766e62')), None


def p_raiz(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    a = xs if tw >= th else ys
    idx = np.where(a % 5 == 0, 1, 2)
    return bm._imagen(sm._bisel(idx, 1, 1), _r('1a140e', '2a2016', '3c2e20', '50402c', '665238')), None


def p_hojas(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=4.0, umbral=0.5, alto=0.8)
    return bm._imagen(np.array([1, 2, 2, 3, 3])[idx], _r('0c1a0c', '142a12', '1e3c1a', '2a5224', '386a2e')), None


def p_monte(tw, th, cara, s):
    idx = sm._manchas(tw, th, s, celda=12.0, umbral=0.6, alto=0.85)
    return bm._imagen(np.array([1, 1, 2, 2, 3])[idx], _r('3a3c4c', '444658', '4e5062', '585a6c', '626476')), None


def p_humo(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((xs + ys) % 5 == 0, 3, 2)
    return bm._imagen(idx, _r('8a8078', 'a89e94', 'c4bab0', 'ddd4ca', 'f0e8e0')), None


def p_brasa(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (255, 140, 40, 255)
    t[(xs + ys) % 3 == 0] = (255, 220, 120, 255)
    return t, None


for _f in (p_piedra, p_raiz, p_hojas, p_monte, p_humo, p_brasa):
    _f.__name__ = 'kalE_' + _f.__name__
bm.PLENOS.add(p_brasa)


def suelo(lz, cam, niebla, S, ext=300, paso=32, cerca=56, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 16
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'losas_kal'))

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


def pilar(qs, x, z, alto, semilla):
    """Un pilar del templo, roto arriba, con las raices de una higuera que lo abrazan y su copa encima."""
    rng = random.Random(semilla)
    M = vr.T(x, 0.0, z)
    bm.cubo(qs, M, -3.6, 0.0, -3.6, 7.2, 2.4, 7.2, p_piedra, semilla=semilla)
    bm.cubo(qs, M, -2.6, 2.4, -2.6, 5.2, alto, 5.2, p_piedra, semilla=semilla + 1)
    bm.cubo(qs, M, -3.4, 2.4 + alto, -3.4, 6.8, 1.8, 6.8, p_piedra, semilla=semilla + 2)
    for j in range(5):                                                  # las raices que bajan
        g = rng.uniform(0, TAU)
        a = np.array((x + math.cos(g) * 2.8, alto * rng.uniform(0.6, 1.0), z + math.sin(g) * 2.8))
        b = np.array((x + math.cos(g) * 5.0, 0.0, z + math.sin(g) * 5.0))
        d = b - a
        Mr = em.marco(a, d, up=(0.0, 0.0, 1.0) if abs(d[1]) > 0.9 * np.linalg.norm(d) else (0.0, 1.0, 0.0))
        bm.cubo(qs, Mr, -0.5, -0.5, 0.0, 1.0, 1.0, float(np.linalg.norm(d)), p_raiz, semilla=j)
    for j in range(3):                                                  # la copa
        w = rng.uniform(8.0, 13.0)
        bm.cubo(qs, M @ vr.T(rng.uniform(-3, 3), 4.2 + alto + j * 2.0, rng.uniform(-3, 3)), -w / 2, 0.0, -w / 2, w, 3.4, w,
                p_hojas, semilla=j)


def templo(lz, cam, niebla, S, semilla=4, libre=None):
    """La escalinata y la puerta del templo detras, los pilares a los lados, los braseros con su humo y los montes en la
    niebla (sin nada entre la camara y el jefe)."""
    r = random.Random(semilla)
    qs = []
    zt = -34.0                                                          # la escalinata y la puerta, detras
    for j in range(7):
        bm.cubo(qs, vr.T(0.0, 0.0, zt - j * 2.4), -30.0 + j * 1.2, 0.0, -2.4, 60.0 - j * 2.4, 1.6 * (j + 1), 2.4, p_piedra,
                semilla=j)
    zp = zt - 18.0
    bm.cubo(qs, vr.T(0.0, 0.0, zp), -26.0, 0.0, -10.0, 52.0, 11.2, 10.0, p_piedra, semilla=10)
    for s in (-1, 1):
        bm.cubo(qs, vr.T(s * 13.0, 11.2, zp), -6.0, 0.0, -9.0, 12.0, 26.0, 9.0, p_piedra, semilla=11)
    bm.cubo(qs, vr.T(0.0, 37.2, zp), -20.0, 0.0, -9.0, 40.0, 6.0, 9.0, p_piedra, semilla=12)
    for j in range(4):
        w = 34.0 - j * 7.0
        bm.cubo(qs, vr.T(0.0, 43.2 + j * 5.0, zp), -w / 2, 0.0, -8.0, w, 5.0, 8.0, p_piedra, semilla=13 + j)
    for k, (x, z) in enumerate(((-40, 2), (40, -4), (-52, -20), (54, -24), (-34, 34), (38, 40))):
        if libre is not None and libre(x, z):
            continue
        pilar(qs, x, z, r.uniform(10, 20), k)
    for x, z in ((-22, 18), (24, 14)):                                  # los braseros
        if libre is not None and libre(x, z):
            continue
        M = vr.T(x, 0.0, z)
        bm.cubo(qs, M, -1.6, 0.0, -1.6, 3.2, 3.6, 3.2, p_piedra, semilla=1)
        bm.cubo(qs, M, -2.4, 3.6, -2.4, 4.8, 1.4, 4.8, p_piedra, semilla=2)
        bm.cubo(qs, M, -1.8, 5.0, -1.8, 3.6, 0.8, 3.6, p_brasa, semilla=1)
    hacia_camara = math.atan2(cam.ojo[2], cam.ojo[0])
    lejos = hacia_camara + math.pi                                      # los montes, en la niebla
    for k in range(10):
        a = lejos + r.uniform(-1.3, 1.3)
        rr = r.uniform(220, 300)
        x, z = math.cos(a) * rr, math.sin(a) * rr
        w, alto = r.uniform(70, 120), r.uniform(50, 110)
        for j in range(7):
            f = 1.0 - j / 7 * 0.85
            bm.cubo(qs, vr.T(x, 0, z) @ vr.Ry(k), -w * f / 2, 0, -w * f / 2, w * f, alto * (j + 1) / 7, w * f, p_monte,
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
    """Las motas de polvo y de ceniza del incienso, que brillan con el sol."""
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
        qs, info = am.kalara(cual)
        P = np.array([p for q in qs for p in q[0]])
        MODELOS[cual] = (qs, info, P)
    return MODELOS[cual]


def camara(cual, vista):
    """Las camaras: 'heroe' (de cuerpo entero, de tres cuartos y desde abajo), 'cabeza' (de cerca y un poco por debajo,
    para mirar dentro del arco de la boca) y 'cartel' (de cerca y muy desde abajo)."""
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    h = hi[1]
    b = np.asarray(info['boca'], float)
    if vista == 'heroe':
        d = max(h, hi[0] - lo[0]) * 0.5 / math.tan(25 * D) * 1.35
        obj = np.array((0.0, h * 0.46, 2.0))
        v = np.array((0.5, 0.0, 0.87))
        ojo = obj + v * d
        ojo[1] = 2.4
        return tuple(ojo), tuple(obj), 50
    if vista == 'cabeza':
        ojo = b + np.array((6.0, -3.6, 15.0))
        ojo[1] = max(ojo[1], 1.6)
        return tuple(ojo), tuple(b + np.array((0.0, 1.6, -2.0))), 56
    obj = np.array((0.0, h * 0.6, 3.0))
    ojo = obj + np.array((0.45, 0.0, 0.89)) * h * 1.15
    ojo[1] = 1.6
    return tuple(ojo), tuple(obj), 64


def escena(cual, vista, n_motas, brillo=0.9, S=None):
    """Una foto: el patio del templo; Kalara, con la luz de su boca; el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = S or sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    ojo, obj, fov = camara(cual, vista)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    qs, info, P = modelo(cual)
    lo, hi = P.min(axis=0), P.max(axis=0)
    suelo(lz, cam, niebla, S)
    templo(lz, cam, niebla, S, libre=lambda x, z: lo[0] - 4 < x < hi[0] + 4 and lo[2] - 4 < z < hi[2] + 4
           or abs(x - ojo[0]) < 8 and abs(z - ojo[2]) < 8)
    neo = _c(am.VARIANTES[cual]['neon'][1])
    luces = S['luces'] + [(tuple(p) + (9.0,), neo, 1.1, 'punto') for p in info['luces'][:2]]
    z0 = lz.z.copy()
    am.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe', 60), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 30), 'cabeza_' + cual)


def cartel(cual):
    """La presentacion del cartel: de cerca y desde abajo, con el cielo de su amanecer."""
    guardar(escena(cual, 'cartel', 40, brillo=1.2), 'cartel_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos, con la misma luz y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 200, 420)
    cam = vr.Camara((0.0, 8.0, 150.0), (0.0, 9.0, 0.0), 22, W * SS, H * SS)
    suelo(lz, cam, niebla, S, ext=340, paso=32, cerca=40)
    templo(lz, cam, niebla, S, semilla=8, libre=lambda x, z: abs(x) < 60 and -20 < z < 60 or z > 60)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -30.0), ('B', 0.0), ('C', 30.0)):
        qs, info, P = modelo(cual)
        qs = qm.transformar(qs, vr.T(x, 0, 0))
        z0 = lz.z.copy()
        am.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(14.0, 26.0, 0)), S['luces'], S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=0), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo y, de izquierda a derecha, la piel, el oro, la nariz, la
    carne de la boca, el paladar, la garganta, los dientes, el colmillo, el ojo, el mechon de llama, el mechon de
    detras, el cuerno y la punta de la corona."""
    W = 2560
    filas = []
    for c in formas:
        P = am.pintores(am.VARIANTES[c])
        filas.append([(P['piel'], 'frente', 36, 36), (P['oro'], 'frente', 16, 12), (P['nariz'], 'frente', 36, 18),
                      (P['carne'], 'der', 24, 24), (P['paladar'], 'abajo', 36, 30), (P['garganta'], 'frente', 30, 22),
                      (P['dientes'], 'frente', 30, 11), (P['colmillo'], 'frente', 7, 32), (P['ojo_d'], 'frente', 30, 21),
                      (P['llama'], 'frente', 22, 48), (P['mechon'], 'frente', 18, 48), (P['cuerno'], 'der', 30, 10),
                      (P['punta_oro'], 'frente', 26, 52)])
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

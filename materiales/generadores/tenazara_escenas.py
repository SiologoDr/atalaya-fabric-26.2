"""
Renders de la ficha de Tenazara en sus tres tipos (12-10-2026): cada tipo en su sitio, de
abajo y con las tenazas abiertas; las tenazas de cerca; los tres juntos con un jugador; y
la lamina de materiales.

  A  del Desierto   las dunas al ponerse el sol, con mesas de arenisca y arena que vuela
  B  de la Geoda    la cueva de amatista, con cristales gigantes y destellos que caen
  C  del Arrecife   el arrecife bajo el agua, con corales, rayos de luz y burbujas

Uso: python tenazara_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
import tenazara_modelo as tm

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
        luces=[((-0.6, 0.55, 0.7), (1.0, 0.78, 0.55), 0.9, 'llave'), ((0.4, 0.35, -1.0), (1.0, 0.62, 0.3), 1.0, 'contra'),
               ((0.0, -0.5, 1.0), (1.0, 0.7, 0.3), 0.3, 'llave')],
        amb=(0.24, 0.19, 0.17), niebla=(0.3, 0.17, 0.12), niebla_d=(40, 150),
        cielo=((0.04, 0.035, 0.09), (0.3, 0.13, 0.13), (0.78, 0.4, 0.18)),
        suelo=_r('4a301a', '5e3e22', '72502c', '886238', 'a07646'), roca=_r('2a1a10', '4a301c', '6a4628', '8c6036', 'b07e48'),
        motas=((240, 196, 140), (255, 226, 170)), viento=(1.0, 0.1), largo=(8, 22), sol=True,
    ),
    'B': dict(
        luces=[((-0.4, 0.8, 0.8), (0.86, 0.78, 1.0), 0.95, 'llave'), ((0.3, 0.5, -1.0), (0.85, 0.55, 1.0), 1.1, 'contra'),
               ((0.0, -0.5, 1.0), (0.75, 0.5, 1.0), 0.4, 'llave')],
        amb=(0.24, 0.2, 0.3), niebla=(0.08, 0.04, 0.12), niebla_d=(36, 130),
        cielo=((0.008, 0.004, 0.016), (0.04, 0.016, 0.07), (0.12, 0.05, 0.18)),
        suelo=_r('0e0a14', '16101e', '1e1628', '281e34', '342842'), roca=_r('0a0810', '141018', '1e1824', '2a2232', '3a3044'),
        motas=((220, 180, 255), (250, 236, 255)), viento=(0.05, 1.0), largo=(1, 2),
    ),
    'C': dict(
        luces=[((-0.2, 1.0, 0.5), (0.6, 0.9, 0.95), 0.85, 'llave'), ((0.3, 0.5, -1.0), (1.0, 0.55, 0.65), 0.9, 'contra'),
               ((0.0, -0.5, 1.0), (1.0, 0.5, 0.6), 0.3, 'llave')],
        amb=(0.14, 0.21, 0.23), niebla=(0.03, 0.14, 0.16), niebla_d=(26, 110),
        cielo=((0.1, 0.3, 0.32), (0.04, 0.16, 0.19), (0.02, 0.08, 0.1)),
        suelo=_r('0e2224', '143032', '1c3c3c', '264a48', '345a56'), roca=_r('081414', '0e2020', '162e2c', '203c3a', '2e4e4a'),
        motas=((200, 250, 250), (255, 210, 220)), viento=(0.0, -1.0), largo=(1, 2), burbujas=True, rayos=True,
    ),
}
for _k, _s in SITIO.items():
    qm._reg('suelo_ten_' + _k, qm._suelo_grande(40 + ord(_k), _s['suelo'], None, grietas=False))


def pintor_roca(sitio):
    rampa = SITIO[sitio]['roca']

    def roca(tw, th, cara, s):
        if sitio == 'A':                       # arenisca en estratos
            ys = np.arange(th)[:, None] * np.ones((1, tw), int)
            v = (ys + (s % 3)) % 6
            idx = np.where(v < 2, 3, np.where(v < 5, 2, 1))
            if cara == 'arriba':
                idx = np.full((th, tw), 3)
        else:
            idx = sm._manchas(tw, th, s, celda=7.0, umbral=0.62, alto=0.85)
            idx = np.array([1, 2, 2, 3, 3])[idx]
        return bm._imagen(sm._bisel(idx), rampa), None
    roca.__name__ = 'ten_roca_' + sitio
    return roca


def pintor_gema():
    rampa = _r('2a0e4a', '4a1a7a', '7234b4', 'a468e6', 'dcbcff')

    def gema(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        diag = xs * th - ys * tw
        idx = np.where(diag > 0, 3, 2)
        idx = np.where(np.abs(diag) < max(tw, th) * 0.8, 4, idx)
        if tw >= 3:
            idx[:, -1] = 1
        tex = bm._imagen(idx, rampa)
        return tex, bm._emis(tex, idx >= 4, 120)
    gema.__name__ = 'ten_gema'
    return gema


def pintor_coral(nombre, rampa):
    def coral(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.where((ys % 3) == 0, 3, 2)
        if cara == 'arriba':
            idx[:] = 4
        if tw >= 3:
            idx[:, -1] = 1
        return bm._imagen(idx, rampa), None
    coral.__name__ = 'ten_coral_' + nombre
    return coral


def suelo(lz, cam, niebla, sitio, ext=180, paso=32, cerca=48, paso_cerca=8):
    qs = []

    def baldosa(gx, gz, p):
        k = p / 4
        P = [(gx + p, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + p), (gx + p, 0.0, gz + p)]
        qs.append(([np.array(q, float) for q in P], [(k, 0), (0, 0), (0, k), (k, k)], 'suelo_ten_' + sitio))

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


def entorno(lz, cam, niebla, sitio, semilla=4):
    """Lo que rodea a la alacrana: rocas a sus pies y, detras, mesas de arenisca, cristales
    gigantes o cabezas de coral."""
    r = random.Random(semilla)
    roca = pintor_roca(sitio)
    qs = []
    for k in range(8):                                     # rocas sueltas alrededor, ninguna delante
        a = r.uniform(math.pi * 0.95, math.pi * 2.05)
        rr = r.uniform(9.0, 15.0)
        w, h = r.uniform(1.6, 3.2), r.uniform(0.6, 1.6)
        M = vr.T(math.cos(a) * rr, -0.1, math.sin(a) * rr - 2.0) @ vr.Ry(r.uniform(0, 1.5)) @ vr.Rz(r.uniform(-8, 8) * D)
        bm.cubo(qs, M, -w / 2, 0, -w / 2, w, h, w * 0.8, roca, semilla=k)
        bm.cubo(qs, M, -w * 0.35, h, -w * 0.3, w * 0.7, h * 0.4, w * 0.55, roca, semilla=k + 1)
    if sitio == 'A':
        for _ in range(9):                                 # mesas de arenisca a lo lejos
            a = r.uniform(math.pi * 1.08, math.pi * 1.92)
            rr = r.uniform(40, 90)
            px, pz = math.cos(a) * rr, math.sin(a) * rr
            h, g = r.uniform(8, 22), r.uniform(4, 10)
            M = vr.T(px, 0, pz) @ vr.Ry(r.uniform(0, 1.5))
            bm.cubo(qs, M, -g * 1.25, 0, -g, 2.5 * g, h * 0.3, 2.0 * g, roca, semilla=1)
            bm.cubo(qs, M, -g, h * 0.3, -g * 0.8, 2 * g, h * 0.45, 1.6 * g, roca, semilla=2)
            bm.cubo(qs, M, -g * 0.8, h * 0.75, -g * 0.65, 1.6 * g, h * 0.25, 1.3 * g, roca, semilla=3)
    elif sitio == 'B':
        gema = pintor_gema()
        for _ in range(14):                                # cristales gigantes y columnas de roca
            a = r.uniform(math.pi * 1.02, math.pi * 1.98)
            rr = r.uniform(18, 50)
            px, pz = math.cos(a) * rr, math.sin(a) * rr
            M = vr.T(px, 0, pz) @ vr.Rz(r.uniform(-22, 22) * D) @ vr.Rx(r.uniform(-15, 15) * D)
            if r.random() < 0.6:
                bm.cristal(qs, M, r.uniform(1.2, 2.6), r.uniform(8, 20), gema, semilla=3)
            else:
                h = r.uniform(10, 26)
                for j in range(4):
                    g = 2.2 * (1 - j * 0.2)
                    bm.cubo(qs, M, -g, h * j / 4, -g, 2 * g, h / 4 + 0.05, 2 * g, roca, semilla=j)
        for _ in range(7):                                 # drusas pequenas en el suelo, cerca
            a = r.uniform(math.pi * 0.9, math.pi * 2.1)
            rr = r.uniform(10, 17)
            M = vr.T(math.cos(a) * rr, 0, math.sin(a) * rr - 2.0)
            for j in range(3):
                bm.cristal(qs, M @ vr.Rz(r.uniform(-30, 30) * D) @ vr.Rx(r.uniform(-30, 30) * D), r.uniform(0.3, 0.55),
                           r.uniform(1.4, 3.0), gema, semilla=j)
    else:
        corales = [pintor_coral('rosa', _r('4a1424', '7a2a3e', 'b04a5c', 'd8707e', 'f4a4a8')),
                   pintor_coral('naranja', _r('4a2410', '7a4018', 'b0642a', 'd88a44', 'f4b46e')),
                   pintor_coral('lila', _r('2a1a44', '44306a', '644c94', '8a72ba', 'b8a4dc'))]
        for n in range(16):                                # cabezas de coral a lo lejos y cerca
            a = r.uniform(math.pi * 0.95, math.pi * 2.05)
            rr = r.uniform(12, 46)
            px, pz = math.cos(a) * rr, math.sin(a) * rr - 2.0
            M = vr.T(px, 0, pz) @ vr.Ry(r.uniform(0, 3))
            bm.cubo(qs, M, -1.6, 0, -1.4, 3.2, 1.2, 2.8, roca, semilla=n)
            P = {'coral': corales[n % 3]}
            for j in range(3):
                tm.rama_coral(qs, M @ vr.T(r.uniform(-1, 1), 1.1, r.uniform(-1, 1)) @ vr.Rz(r.uniform(-15, 15) * D),
                              P, alto=r.uniform(2.0, 4.5), semilla=n * 5 + j)
    qm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


def cielo(W, H, horizonte, sitio):
    arriba, medio, abajo = (np.array(c) for c in SITIO[sitio]['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.62, arriba + (medio - arriba) * (k / 0.62), medio + (abajo - medio) * ((k - 0.62) / 0.38))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    return np.clip(col, 0, 1)


def sol(img, horizonte):
    """Un sol de pixel enorme que se pone detras de las mesas."""
    W, H = img.size
    p = max(2, int(W / 260))                              # el tamano de un pixel del sol
    R = int(W * 0.085 / p)
    mini = Image.new('RGBA', (2 * R + 1, 2 * R + 1), (0, 0, 0, 0))
    d = ImageDraw.Draw(mini)
    for rr, c in ((R, (255, 150, 60, 255)), (int(R * 0.86), (255, 190, 90, 255)), (int(R * 0.7), (255, 226, 150, 255))):
        d.ellipse((R - rr, R - rr, R + rr, R + rr), fill=c)
    for j in range(3):                                    # tres franjas que lo cruzan
        y = int(R * (1.25 + 0.22 * j))
        d.rectangle((0, y, 2 * R, y + max(1, int(R * 0.05))), fill=(0, 0, 0, 0))
    grande = mini.resize((mini.width * p, mini.height * p), Image.NEAREST)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    cx, cy = int(W * 0.8), int(horizonte - grande.height * 0.36)
    capa.paste(grande, (cx - grande.width // 2, cy - grande.height // 2), grande)
    halo = capa.filter(ImageFilter.GaussianBlur(W / 40))
    base = Image.alpha_composite(img.convert('RGBA'), halo)
    return Image.alpha_composite(base, capa)


def rayos_de_luz(img, semilla=2):
    """Rayos de luz que bajan del agua, suaves y en diagonal."""
    W, H = img.size
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    for _ in range(7):
        x = r.uniform(-0.1, 1.0) * W
        a = r.uniform(0.02, 0.06) * W
        d.polygon([(x, 0), (x + a, 0), (x + a + W * 0.18, H), (x + W * 0.18 - a * 0.3, H)], fill=(170, 240, 235, r.randint(26, 48)))
    capa = capa.filter(ImageFilter.GaussianBlur(W / 90))
    return Image.alpha_composite(img.convert('RGBA'), capa)


def motas(img, n, semilla, sitio):
    S = SITIO[sitio]
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H)
        c = S['motas'][0] if r.random() < 0.6 else S['motas'][1]
        if S.get('burbujas'):                             # burbujas de pixel: un aro con su brillo
            if r.random() < 0.55:
                continue
            g = max(2, int(r.choice((2, 2, 3, 4)) * W / 1600))
            d.rectangle((x, y, x + 2 * g, y + 2 * g), outline=(*c, r.randint(80, 150)), width=1)
            d.rectangle((x + g * 0.5, y + g * 0.5, x + g * 0.9, y + g * 0.9), fill=(255, 255, 255, 170))
            continue
        l = r.uniform(*S['largo']) * W / 1600
        g = max(1, int(r.choice((1, 1, 2)) * W / 1600))
        d.line((x, y, x + S['viento'][0] * l, y + S['viento'][1] * l), fill=(*c, r.randint(110, 220)), width=g)
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
    if SITIO[sitio].get('sol'):
        img_f = sol(img_f, horiz).convert('RGB')
    fondo = np.array(img_f).astype(float) / 255
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * 0.9, radios=((2 * K, 0.5), (10 * K, 0.4), (40 * K, 0.35))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if SITIO[sitio].get('rayos'):
        img = rayos_de_luz(img)
    if n_motas > 0:
        img = motas(img, int(n_motas * W / 1600), semilla, sitio)
    return img


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=92)
    print('ok', nombre, flush=True)
    return img


NOMBRE = {'A': 'Tenazara del Desierto', 'B': 'Tenazara de la Geoda', 'C': 'Tenazara del Arrecife'}
SUB_HEROE = {
    'A': 'quitina negra en bandas, anillos de oro con remaches y puas en el lomo',
    'B': 'quitina violeta en manchas y drusas de amatista en el lomo, la cola y las tenazas',
    'C': 'quitina verdeazul con lunares, corales de cuerno y percebes',
}
SUB_CABEZA = {
    'A': 'las tenazas son fauces: se abren encendidas, con dientes en peine y el nucleo al fondo',
    'B': 'las tenazas son fauces: se abren encendidas, con dientes en peine y el nucleo al fondo',
    'C': 'las tenazas son fauces: se abren encendidas, con dientes en peine y el nucleo al fondo',
}
CAMARA_HEROE = ((6.0, 2.8, 28.0), (0.0, 7.8, -1.0), 56)
CAMARA_CABEZA = ((9.0, 4.6, 22.0), (2.0, 5.6, 8.0), 46)


def escena(cual, camara, nombre, sub, n_motas):
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    niebla = qe.Niebla(SITIO[cual]['niebla'], *SITIO[cual]['niebla_d'])
    ojo, obj, fov = camara
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, cual)
    entorno(lz, cam, niebla, cual)
    qs, info = tm.tenazara(cual)
    tm.dibujar(lz, cam, qs, SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    img = revelar(lz, cam, W, H, cual, n_motas=n_motas)
    return qe.rotular(img, nombre, sub)


def heroe(cual):
    guardar(escena(cual, CAMARA_HEROE, NOMBRE[cual], SUB_HEROE[cual], 200), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, CAMARA_CABEZA, NOMBRE[cual], SUB_CABEZA[cual], 110), 'cabeza_' + cual)


def tres():
    """Los tres tipos juntos, con la misma luz neutra y un jugador delante."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    SITIO['T'] = dict(luces=[((-0.4, 0.8, 0.8), (0.82, 0.82, 0.9), 0.8, 'llave'), ((0.3, 0.5, -1.0), (0.9, 0.85, 1.0), 0.8, 'contra')],
                      amb=(0.22, 0.21, 0.26), niebla=(0.06, 0.05, 0.09), niebla_d=(170, 320),
                      cielo=((0.01, 0.012, 0.03), (0.05, 0.05, 0.1), (0.16, 0.13, 0.22)),
                      suelo=_r('12111a', '16141e', '1a1822', '1e1c26', '22202a'), motas=((230, 230, 255), (200, 200, 240)), viento=(0, 1),
                      largo=(1, 2))
    qm._reg('suelo_ten_T', qm._suelo_grande(95, SITIO['T']['suelo'], None, grietas=False))
    niebla = qe.Niebla(SITIO['T']['niebla'], *SITIO['T']['niebla_d'])
    cam = vr.Camara((0.0, 13.0, 106.0), (0.0, 7.0, 0.0), 24, W * SS, H * SS)
    suelo(lz, cam, niebla, 'T', ext=260, paso=32, cerca=40)
    for cual, x in (('A', -29.0), ('B', 0.0), ('C', 29.0)):
        qs, info = tm.tenazara(cual)
        tm.dibujar(lz, cam, qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(20 * D)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(9.0, 17.0, 0)), SITIO['T']['luces'], SITIO['T']['amb'], niebla)
    img = revelar(lz, cam, W, H, 'T', n_motas=0)
    P = np.array([p for q in tm.tenazara('A')[0] for p in q[0]])
    guardar(qe.rotular(img, 'Los tres tipos, a escala', 'del Desierto · de la Geoda · del Arrecife · un jugador (1,8) delante · '
                       '%.0f bloques de alto, %.0f de largo y %.0f de ancho'
                       % (P[:, 1].max(), P[:, 2].max() - P[:, 2].min(), P[:, 0].max() - P[:, 0].min())), 'tres')


def materiales():
    W = 1600
    filas = []
    for c in 'ABC':
        P = tm.pintores(tm.TIPOS[c])
        clave, nombre, cara, tw, th = {'A': ('oro', 'oro', 'frente', 24, 8), 'B': ('cristal', 'amatista', 'der', 8, 16),
                                       'C': ('coral', 'coral', 'der', 4, 16)}[c]
        propio = (P[clave], nombre, cara, tw, th)
        fila = [(P['caparazon'], 'caparazon', 'arriba', 24, 24), (P['junta'], 'junta', 'abajo', 16, 16), (P['pata'], 'pata', 'der', 8, 16),
                (P['diente'], 'diente', 'frente', 4, 12), (P['fauces'], 'fauces', 'abajo', 16, 16), (P['nucleo'], 'nucleo', 'frente', 24, 24),
                (P['veneno'], 'veneno', 'der', 16, 16), propio]
        filas.append((c, fila))
    cols, celda = 8, 168
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

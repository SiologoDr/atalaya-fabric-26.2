"""
Renders del boceto de la Mariposa del Vendaval para su ficha de diseno.

La arena es la Cima del Vendaval: una meseta de roca por encima de las nubes,
con columnas rotas alrededor y el cielo en tormenta.

Uso: python viento_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne          # el jugador de escala y sus materiales
import viento_modelo as vm
import viento_bc_modelo as bc

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
FUENTE = 'C:/Windows/Fonts/'
SS = 2

# ----------------------------------------------------------------------
#  Materiales de la cima
# ----------------------------------------------------------------------
ROCA = vm._rampa('3a3f4a', '4a505c', '5b616e', '6d7482', '8a909c')
nm.MAT.update({
    'roca': nm._loseta(201, nm.piedra(ROCA, 0.12)),
    'roca_osc': nm._loseta(202, nm.piedra(vm._rampa('23272f', '2d323b', '383e48', '444a55', '565c68'), 0.08)),
    'grava': nm._loseta(203, lambda x, y, r: ROCA[r.choice([0, 1, 2, 2, 3, 4])]),
    'musgo': nm._loseta(204, lambda x, y, r: vm._hex(r.choice(['3c5a48', '4a6a52', '557a5c', '35503f']))),
})

LUCES_CIELO = [
    ((-0.4, 1.0, -0.6), (0.78, 0.86, 1.0), 1.0, 'llave'),     # la luz plana de la tormenta
    ((0.8, 0.3, 0.7), (0.45, 0.7, 1.0), 0.9, 'contra'),       # el cielo la recorta en azul
    ((-0.9, 0.2, 0.4), (0.7, 0.55, 1.0), 0.5, 'contra'),
]
AMB_CIELO = (0.2, 0.24, 0.32)


class NieblaCielo:
    color = (0.17, 0.21, 0.3)

    def __init__(self, ini=14.0, largo=40.0):
        self.ini, self.largo = ini, largo

    def __call__(self, z):
        return np.clip((z - self.ini) / self.largo, 0, 0.9)


def cielo(W, H, horizonte, semilla, rayos=0.0):
    """Cielo de tormenta: azul noche arriba, gris azulado en el horizonte, nubes
    en capas, estelas de viento y algun relampago lejano."""
    r = random.Random(semilla)
    y = np.linspace(0, 1, H)[:, None, None]
    arriba, abajo = np.array([0.04, 0.06, 0.12]), np.array([0.3, 0.36, 0.48])
    col = arriba + (abajo - arriba) * np.clip(y / max(horizonte / H, 0.3), 0, 1) ** 1.4
    col = np.broadcast_to(col, (H, W, 3)).copy()
    nubes = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(nubes)
    for _ in range(60):
        cx, cy = r.uniform(-0.1, 1.1) * W, r.uniform(0.0, 0.75) * H
        rx, ry = r.uniform(0.08, 0.25) * W, r.uniform(0.02, 0.06) * H
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=r.randint(18, 60))
    nubes = np.array(nubes.filter(ImageFilter.GaussianBlur(W / 70))).astype(float)[..., None] / 255
    col += nubes * np.array([0.45, 0.52, 0.66])
    if rayos > 0:
        for _ in range(3):
            cx, cy = r.uniform(0.55, 0.95) * W, r.uniform(0.05, 0.3) * H
            yy, xx = np.mgrid[0:H, 0:W]
            g = np.exp(-(((xx - cx) / (W * 0.18)) ** 2 + ((yy - cy) / (H * 0.14)) ** 2))
            col += g[..., None] * np.array([0.45, 0.4, 0.75]) * rayos * r.uniform(0.5, 1.0)
    return np.clip(col, 0, 1)


def estelas(img, n, semilla, zona=None, alfa=70):
    """Lineas finas de viento que cruzan el aire."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x0 = r.uniform(*(zona[0] if zona else (0, W)))
        y0 = r.uniform(*(zona[1] if zona else (0, H)))
        L = r.uniform(0.06, 0.2) * W
        curva = r.uniform(-0.04, 0.04) * H
        pts = [(x0 + L * t, y0 + curva * math.sin(t * math.pi)) for t in np.linspace(0, 1, 12)]
        d.line(pts, fill=(225, 238, 255, r.randint(alfa // 2, alfa)), width=max(1, int(W / 900)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(0.6)))


def suelo(lz, cam, ext=22, prof=40, niebla=None):
    r = random.Random(5)
    qs = []
    for gx in range(-ext, ext):
        for gz in range(-34, prof):
            if math.hypot(gx + 0.5, gz + 0.5 - 4) > 34:     # la meseta acaba en un borde
                continue
            mat = r.choice(['roca', 'roca', 'roca', 'grava', 'roca_osc', 'musgo'])
            h = 0.0 if math.hypot(gx, gz) < 12 else r.choice([0, 0, 0, 0.0625, 0.125])
            qs.append(([(gx, h, gz), (gx + 1, h, gz), (gx + 1, h, gz + 1), (gx, h, gz + 1)], [(0, 0), (1, 0), (1, 1), (0, 1)], mat))
    nm.dibujar(lz, cam, qs, LUCES_CIELO[:1], (0.24, 0.27, 0.34), niebla)


def columna(x, z, alto, rota=True, semilla=0):
    """Columna antigua de la cima, rota a cierta altura."""
    r = random.Random(semilla)
    cajas = [((-14, -16, -14, 28, 16, 28), 'roca_osc'), ((-11, -alto * 16, -11, 22, alto * 16, 22), 'roca')]
    for k in range(1, alto):
        cajas.append(((-11.6, -k * 16 - 2, -11.6, 23.2, 2, 23.2), 'roca_osc'))
    if rota:
        cajas.append(((-9, -alto * 16 - 6, -6, 12, 6, 14), 'roca'))
    else:
        cajas.append(((-14, -alto * 16 - 6, -14, 28, 6, 28), 'roca_osc'))
    raiz = nm.nodo('col', (0, 0, 0), (0, r.uniform(-20, 20), 0), cajas)
    return nm.quads(raiz, {}, vr.T(x, 0, z) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1]))


# ----------------------------------------------------------------------
#  Viento hecho malla: tornados, cuchillas, el circulo del Juicio
# ----------------------------------------------------------------------
def _tex_viento(semilla, w=24, h=48):
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        for x in range(w):
            if (x + y // 3 + r.randint(0, 2)) % 6 < 2:
                t[y, x] = (236, 244, 255, r.randint(90, 170))
            elif r.random() < 0.35:
                t[y, x] = (190, 208, 236, r.randint(30, 70))
    return t


TEX_VIENTO = _tex_viento(1)
TEX_VIENTO[..., 3] = np.minimum(255, TEX_VIENTO[..., 3].astype(int) * 3 // 2).astype(np.uint8)


def tornado(x, z, alto=6.0, r0=0.35, r1=2.4, giro=0.0, anillos=16, segs=14, base=0.0):
    """Embudo de viento: anillos que se abren al subir, retorcidos, con huecos."""
    out = []
    for k in range(anillos):
        t0, t1 = k / anillos, (k + 1) / anillos
        ra, rb = r0 + (r1 - r0) * t0 ** 1.5, r0 + (r1 - r0) * t1 ** 1.5
        ya, yb = base + alto * t0, base + alto * t1
        for s in range(segs):
            if (s + k) % 3 == 0:
                continue                                  # huecos: se ve a traves
            a0 = giro + 2 * math.pi * s / segs + t0 * 4.0
            a1 = giro + 2 * math.pi * (s + 1) / segs + t0 * 4.0
            b0, b1 = a0 + 0.25, a1 + 0.25
            P = [(x + ra * math.cos(a0), ya, z + ra * math.sin(a0)), (x + ra * math.cos(a1), ya, z + ra * math.sin(a1)),
                 (x + rb * math.cos(b1), yb, z + rb * math.sin(b1)), (x + rb * math.cos(b0), yb, z + rb * math.sin(b0))]
            out.append((P, [(0, 1), (1, 1), (1, 0), (0, 0)]))
    return out


def cuchilla(cx, cz, radio, a_centro, abre=0.5, y0=0.5, y1=1.7, segs=10):
    """Onda del Aleteo Cortante: un arco vertical de viento a ras de suelo."""
    out = []
    for s in range(segs):
        a0 = a_centro - abre / 2 + abre * s / segs
        a1 = a_centro - abre / 2 + abre * (s + 1) / segs
        P = [(cx + radio * math.cos(a0), y0, cz + radio * math.sin(a0)), (cx + radio * math.cos(a1), y0, cz + radio * math.sin(a1)),
             (cx + radio * math.cos(a1), y1, cz + radio * math.sin(a1)), (cx + radio * math.cos(a0), y1, cz + radio * math.sin(a0))]
        out.append((P, [(s / segs, 1), ((s + 1) / segs, 1), ((s + 1) / segs, 0), (s / segs, 0)]))
    return out


def _tex_cuchilla(w=64, h=16):
    t = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        for x in range(w):
            u, v = x / (w - 1), abs(y - (h - 1) / 2) / ((h - 1) / 2)
            fin = math.sin(math.pi * u) ** 0.6
            a = (1 - v) ** 1.6 * fin
            if a > 0.03:
                t[y, x] = (240, 248, 255, int(255 * min(1, a * 1.3)))
    return t


TEX_CUCHILLA = _tex_cuchilla()


def _tex_circulo(n=192, fase=1):
    """El circulo del Juicio del Ciclon: anillos y runas de viento que brillan."""
    P = vm.FASES[fase]
    c, b = vm._hex(P['brillo_c']), vm._hex(P['brillo_b'])
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - n / 2, y + 0.5 - n / 2
            d = math.hypot(dx, dy) / (n / 2)
            ang = math.atan2(dy, dx)
            if 0.94 < d < 0.99 or 0.78 < d < 0.8:
                t[y, x] = (*c, 230)
            elif 0.8 < d < 0.94 and (int((ang + math.pi) / (2 * math.pi) * 48) % 3 == 0):
                t[y, x] = (*b, 180)
            elif d < 0.78 and (ang - 3.0 * math.log(max(d, 0.02))) % (math.pi / 2) < 0.18:
                t[y, x] = (*b, int(140 * (1 - d) + 40))
    return t


def dibujar_translucido(lz, cam, qs, tex, k=0.85, niebla=None, glow=0.0):
    qs = sorted(qs, key=lambda q: -cam.proyectar(np.mean(q[0], axis=0))[2])
    for P, UV in qs:
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3) * 1.05, None, niebla, translucido=k)
            if glow:
                lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, aditivo=True, brillo=glow)


def jugador(lz, cam, x, z, guinada, y=0.0, niebla=None):
    M = vr.T(0, y, 0) @ ne.jugador_a_mundo(x, z, guinada)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, M), LUCES_CIELO, AMB_CIELO, niebla)


def componer(lz, W, H, horizonte, semilla, fase=1, rayos=0.0, n_estelas=40):
    alfa = np.array(Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float)[..., None] / 255
    col = np.array(Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    emis = np.array(Image.fromarray((np.clip(lz.emis, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    fondo = cielo(W, H, horizonte, semilla, rayos)
    arr = col * alfa + fondo * (1 - alfa)
    arr = ne.bloom(arr, emis, radios=((4, 0.7), (14, 0.5), (44, 0.35)))
    arr = ne.vineta(arr, 0.55)
    arr = np.clip(arr * np.array([0.95, 0.98, 1.05]), 0, 1)
    img = Image.fromarray((arr * 255).astype(np.uint8)).convert('RGBA')
    estelas(img, n_estelas, semilla)
    return img


# ----------------------------------------------------------------------
#  Poses
# ----------------------------------------------------------------------
HEROICA = {
    'torax': {'rot': (-16, 0, 0)},
    'cabeza': {'rot': (24, 0, 0)},
    'ala_sup_izq': {'rot': (0, -10, -34)}, 'ala_sup_der': {'rot': (0, 10, 34)},
    'ala_inf_izq': {'rot': (0, -20, -22)}, 'ala_inf_der': {'rot': (0, 20, 22)},
    'antena_izq': {'rot': (-20, 0, 20)}, 'antena_der': {'rot': (-20, 0, -20)},
    'colmillo_izq': {'rot': (-30, 0, -26)}, 'colmillo_der': {'rot': (-30, 0, 26)},
}
ALETEO = {
    'torax': {'rot': (-12, 0, 0)},
    'cabeza': {'rot': (22, 0, 0)},
    'ala_sup_izq': {'rot': (0, -32, 26)}, 'ala_sup_der': {'rot': (0, 32, -26)},
    'ala_inf_izq': {'rot': (0, -30, 6)}, 'ala_inf_der': {'rot': (0, 30, -6)},
    'colmillo_izq': {'rot': (-34, 0, -30)}, 'colmillo_der': {'rot': (-34, 0, 30)},
}
JUICIO = {
    'torax': {'rot': (6, 0, 0)},
    'cabeza': {'rot': (30, 0, 0)},
    'ala_sup_izq': {'rot': (0, -4, -42)}, 'ala_sup_der': {'rot': (0, 4, 42)},
    'ala_inf_izq': {'rot': (0, -8, -14)}, 'ala_inf_der': {'rot': (0, 8, 14)},
}


HEROICA_B = {
    'ala_b_izq': {'rot': (0, -8, -26)}, 'ala_b_der': {'rot': (0, 8, 26)},
    'cuello': {'rot': (-14, 0, 0)}, 'cabeza': {'rot': (26, 0, 0)}, 'mandibula': {'rot': (26, 0, 0)},
    'brazo_izq': {'rot': (-30, 0, 20)}, 'brazo_der': {'rot': (-30, 0, -20)},
}
HEROICA_C = {
    'torax': {'rot': (-14, 0, 0)}, 'cabeza': {'rot': (22, 0, 0)},
    'ala_c_sup_izq': {'rot': (0, -10, -30)}, 'ala_c_sup_der': {'rot': (0, 10, 30)},
    'ala_c_inf_izq': {'rot': (0, -18, -12)}, 'ala_c_inf_der': {'rot': (0, 18, 12)},
}


def jefe(lz, cam, cual, x, z, guinada, pose=None, niebla=None, luces=None, amb=None, brillo=1.5, fase=1):
    """Dibuja el diseno A, B o C, cada uno a su escala y su altura de vuelo."""
    luces = LUCES_CIELO if luces is None else luces
    amb = AMB_CIELO if amb is None else amb
    if cual == 'a':
        M = vm.entidad_a_mundo(x, 0, z, guinada)
        vm.dibujar(lz, cam, vm.quads(vm.esqueleto(), HEROICA if pose is None else pose, M), luces, amb, fase=fase,
                   niebla=niebla, brillo=brillo)
    elif cual == 'b':
        M = vm.entidad_a_mundo(x, 0, z, guinada, bc.ESCALA_B)
        bc.dibujar(lz, cam, bc.quads(bc.esqueleto_b(), HEROICA_B if pose is None else pose, M), luces, amb,
                   niebla=niebla, brillo=brillo)
    else:
        M = vm.entidad_a_mundo(x, 0, z, guinada, bc.ESCALA_C)
        bc.dibujar(lz, cam, bc.quads(bc.esqueleto_c(), HEROICA_C if pose is None else pose, M), luces, amb,
                   niebla=niebla, brillo=brillo)


def mariposa(lz, cam, x, z, guinada, pose, fase=1, altura=4.5, niebla=None, escala=1.0):
    M = vm.entidad_a_mundo(x, 0, z, guinada, escala)
    vm.dibujar(lz, cam, vm.quads(vm.esqueleto(altura), pose, M), LUCES_CIELO, AMB_CIELO, fase=fase, niebla=niebla,
               brillo=1.5)


# ----------------------------------------------------------------------
#  1. Heroica
# ----------------------------------------------------------------------
def heroica(W=1600, H=900, fase=1, nombre='heroica', cual='a'):
    if cual == 'a':
        cam = vr.Camara(ojo=(-9.0, 0.9, -22.0), objetivo=(1.2, 8.8, 0), fov=44, ancho=W * SS, alto=H * SS)
    else:
        cam = vr.Camara(ojo=(-11.5, 0.9, -31.0), objetivo=(1.0, 9.6, 0), fov=46, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaCielo()
    suelo(lz, cam, niebla=niebla)
    for i, (x, z, alto, rota) in enumerate(((-13, 10, 5, True), (12, 12, 7, True), (-17, -2, 3, True), (18, 2, 4, False))):
        nm.dibujar(lz, cam, columna(x, z, alto, rota, i), LUCES_CIELO, AMB_CIELO, niebla)
    for (x, z, g) in ((-4.5, -5.0, 210), (2.6, -4.5, 160), (-1.5, -7.5, 190), (6.5, -1.0, 120), (-7.5, -2.0, 240)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    if cual == 'a':
        mariposa(lz, cam, 0, 0, 24, HEROICA, fase, 9.0, niebla)
    else:
        jefe(lz, cam, cual, 0, 0, 24, niebla=niebla)
    dibujar_translucido(lz, cam, tornado(-9.0, 4.0, 6.5, 0.3, 2.6, 0.4), TEX_VIENTO, 0.8, niebla, 0.25)
    dibujar_translucido(lz, cam, tornado(9.5, 6.0, 7.5, 0.3, 2.9, 2.0), TEX_VIENTO, 0.8, niebla, 0.25)
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 300, 0.0, cam.ojo[2] + cam.f[2] * 300]))[1] / SS
    img = componer(lz, W, H, horiz, 3, fase, rayos=0.6, n_estelas=46)
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)


# ----------------------------------------------------------------------
#  2. Vistas: frente, perfil, espalda
# ----------------------------------------------------------------------
def vistas(W=1800, H=600, cual='a'):
    lienzos = []
    luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
    for g in (0, -90, 180):
        cam = vr.Camara(ojo=(0, 9.4, -95), objetivo=(0, 9.4, 0), fov=17.5, ancho=600 * SS, alto=H * SS)
        lz = vr.Lienzo(600 * SS, H * SS)
        jefe(lz, cam, cual, 0, 0, g, luces=luces, amb=(0.32, 0.34, 0.38), brillo=1.2)
        col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
        a = lz.alfa[..., None]
        arr = col * a + np.array([0.93, 0.95, 0.96]) * (1 - a)
        lienzos.append(Image.fromarray((arr * 255).astype(np.uint8)).resize((600, H), Image.LANCZOS))
    img = Image.new('RGB', (W, H), (237, 242, 245))
    for i, im in enumerate(lienzos):
        img.paste(im, (i * 600, 0))
    img.save(os.path.join(OUT, 'vistas.jpg' if cual == 'a' else f'vistas_{cual}.jpg'), quality=92)


# ----------------------------------------------------------------------
#  3. Fases: el mismo bicho, de frente, en sus cuatro fases
# ----------------------------------------------------------------------
def fases(W=1600, H=520):
    lienzos = []
    for f in (1, 2, 3, 4):
        w = W // 4
        cam = vr.Camara(ojo=(0, 10.0, -80), objetivo=(0, 10.0, 0), fov=15, ancho=w * SS, alto=H * SS)
        lz = vr.Lienzo(w * SS, H * SS)
        vm.dibujar(lz, cam, vm.quads(vm.esqueleto(), HEROICA, vm.entidad_a_mundo(0, 0, 0, 0)), LUCES_CIELO, AMB_CIELO,
                   fase=f, brillo=1.5)
        fondo = cielo(w, H, H * 0.95, 10 + f, rayos=[0, 0.2, 0.6, 1.0][f - 1])
        a = np.array(Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((w, H), Image.LANCZOS)).astype(float)[..., None] / 255
        col = np.array(Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((w, H), Image.LANCZOS)).astype(float) / 255
        em = np.array(Image.fromarray((np.clip(lz.emis, 0, 1) * 255).astype(np.uint8)).resize((w, H), Image.LANCZOS)).astype(float) / 255
        arr = ne.bloom(col * a + fondo * (1 - a), em, radios=((3, 0.8), (10, 0.6), (30, 0.4)))
        lienzos.append(Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)))
    img = Image.new('RGB', (W, H))
    for i, im in enumerate(lienzos):
        img.paste(im, (i * (W // 4), 0))
    img.save(os.path.join(OUT, 'fases.jpg'), quality=92)


# ----------------------------------------------------------------------
#  4. Escala: jugador, Vigia, Nerea y la Mariposa
# ----------------------------------------------------------------------
def escala(W=1600, H=820):
    cam = vr.Camara(ojo=(1.2, 8.4, -150), objetivo=(1.2, 8.4, 0), fov=7.4, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
    amb = (0.32, 0.34, 0.38)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-12.6, 0, -20)), luces, amb)
    vt = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia.png'))
    vb = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia_ojo.png'))
    vr.dibujar_quads(lz, cam, vr.quads_del_modelo({}, modelo_a_mundo=vr.entidad_a_mundo(-10.6, 0, 0, -20)), vt, emis=vb,
                     luces=luces, ambiente=amb, brillo=1.2)
    nm.dibujar(lz, cam, nm.quads(nm.esqueleto(), ne.REPOSO, nm.entidad_a_mundo(-6.6, 0, 0, -20, 1.57)), luces, amb, brillo=1.2)
    vm.dibujar(lz, cam, vm.quads(vm.esqueleto(), HEROICA, vm.entidad_a_mundo(6.5, 0, 0, 0)), luces, amb, fase=1, brillo=1.2)
    col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.93, 0.95, 0.96]) * (1 - a)
    img = Image.fromarray((arr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).convert('RGBA')
    rej = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rej)
    f = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 18)
    for b in range(0, 19):
        _, y, _ = cam.proyectar((1.2, b, 0)); y /= SS
        d.line((60, y, W - 20, y), fill=(40, 60, 90, 110 if b else 220), width=2 if b == 0 else 1)
        if b % 2 == 0:
            d.text((18, y - 11), f'{b}', font=f, fill=(40, 60, 90, 255))
    img = Image.alpha_composite(img, rej)
    img.convert('RGB').save(os.path.join(OUT, 'escala.jpg'), quality=92)
    pos = {}
    for nombre, x, alto in (('jugador', -12.6, 2.0), ('vigia', -10.6, 3.1), ('nerea', -6.6, 9.0), ('mariposa', 6.5, 17.0)):
        px_, py, _ = cam.proyectar((x, alto, 0))
        pos[nombre] = (round(px_ / SS / W, 4), round(py / SS / H, 4))
    return pos


# ----------------------------------------------------------------------
#  5. Aleteo Cortante: tres ondas de viento a ras de suelo
# ----------------------------------------------------------------------
def aleteo(W=1600, H=900):
    cam = vr.Camara(ojo=(-15.0, 8.5, -17.0), objetivo=(0.8, 4.2, 1.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaCielo(16, 40)
    suelo(lz, cam, niebla=niebla)
    nm.dibujar(lz, cam, columna(-14, 9, 5, True, 2), LUCES_CIELO, AMB_CIELO, niebla)
    jugador(lz, cam, -5.5, -9.5, 200, niebla=niebla)
    jugador(lz, cam, -1.0, -10.5, 180, y=1.4, niebla=niebla)         # salta la onda
    jugador(lz, cam, 4.0, -9.0, 160, niebla=niebla)
    jugador(lz, cam, 7.5, -4.0, 130, niebla=niebla)                   # retrocede por el golpe
    mariposa(lz, cam, 0, 6, 10, ALETEO, 1, 8.0, niebla)
    qs = []
    for k, rad in enumerate((6.0, 10.0, 14.5)):
        qs += cuchilla(0, 6, rad, -math.pi / 2 + (k - 1) * 0.18, abre=1.0, y0=0.2 + 0.6 * (k % 2), y1=2.0 + 0.6 * (k % 2))
    dibujar_translucido(lz, cam, qs, TEX_CUCHILLA, 0.85, niebla, 0.22)
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 300, 0.0, cam.ojo[2] + cam.f[2] * 300]))[1] / SS
    img = componer(lz, W, H, horiz, 7, 1, rayos=0.3, n_estelas=70)
    img.convert('RGB').save(os.path.join(OUT, 'aleteo.jpg'), quality=90)


# ----------------------------------------------------------------------
#  6. Juicio del Ciclon: el circulo, el tornado gigante y los cuatro nucleos
# ----------------------------------------------------------------------
def juicio(W=1600, H=900):
    fase = 3
    cam = vr.Camara(ojo=(-17.0, 13.0, -31.0), objetivo=(0.5, 10.2, 2.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaCielo(22, 46)
    suelo(lz, cam, niebla=niebla)
    for i, (x, z) in enumerate(((-11, -9), (11, -9), (-11, 11), (11, 11))):
        # pedestal y nucleo de viento
        raiz = nm.nodo('nuc', (0, 0, 0), (0, 45, 0), [((-10, -14, -10, 20, 14, 20), 'roca_osc'),
                                                       ((-8, -40, -8, 16, 16, 16), 'brillo')])
        qs = vm.quads(raiz, {}, vr.T(x, 0, z) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1]))
        vm.dibujar(lz, cam, qs, LUCES_CIELO, AMB_CIELO, fase=fase, niebla=niebla)
    for (x, z, g) in ((-6, -4, 30), (5, -5, -40), (-4, 6, 160), (6, 5, 200), (1.5, -8, 0)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    jugador(lz, cam, 0.5, 0.5, 20, y=4.5, niebla=niebla)              # el marcado, en el aire
    mariposa(lz, cam, 0.5, 3.0, 20, JUICIO, fase, 20.0, niebla, escala=1.0)
    circ = _tex_circulo(fase=fase)
    R = 13.0
    plano = [([(-R, 0.06, -R + 0.5), (R, 0.06, -R + 0.5), (R, 0.06, R + 0.5), (-R, 0.06, R + 0.5)],
              [(0, 0), (1, 0), (1, 1), (0, 1)])]
    plano = [([(p[0] + 0.5, p[1], p[2]) for p in P], UV) for P, UV in plano]
    dibujar_translucido(lz, cam, plano, circ, 0.85, None, 1.0)
    dibujar_translucido(lz, cam, tornado(0.5, 0.5, 13.0, 1.6, 6.5, 1.0, anillos=22, segs=18), TEX_VIENTO, 0.75, niebla, 0.3)
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 300, 0.0, cam.ojo[2] + cam.f[2] * 300]))[1] / SS
    img = componer(lz, W, H, horiz, 11, fase, rayos=1.0, n_estelas=60)
    img.convert('RGB').save(os.path.join(OUT, 'juicio.jpg'), quality=90)


def escala_abc(W=2000, H=640):
    """Los tres disenos juntos, con el jugador, el Vigia y Nerea de referencia."""
    cam = vr.Camara(ojo=(21.0, 8.6, -260), objetivo=(21.0, 8.6, 0), fov=6.6, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
    amb = (0.32, 0.34, 0.38)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-22.5, 0, -20)), luces, amb)
    vt = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia.png'))
    vb = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia_ojo.png'))
    vr.dibujar_quads(lz, cam, vr.quads_del_modelo({}, modelo_a_mundo=vr.entidad_a_mundo(-20.0, 0, 0, -20)), vt, emis=vb,
                     luces=luces, ambiente=amb, brillo=1.2)
    nm.dibujar(lz, cam, nm.quads(nm.esqueleto(), ne.REPOSO, nm.entidad_a_mundo(-15.0, 0, 0, -20, 1.57)), luces, amb, brillo=1.2)
    for cual, x in (('a', 54.0), ('b', 27.0), ('c', 1.0)):
        jefe(lz, cam, cual, x, 0, 0, luces=luces, amb=amb, brillo=1.2)
    col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.93, 0.95, 0.96]) * (1 - a)
    img = Image.fromarray((arr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).convert('RGBA')
    rej = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rej)
    f = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 18)
    for b in range(0, 19, 2):
        _, y, _ = cam.proyectar((21.0, b, 0)); y /= SS
        d.line((48, y, W - 16, y), fill=(40, 60, 90, 110 if b else 220), width=2 if b == 0 else 1)
        d.text((12, y - 11), f'{b}', font=f, fill=(40, 60, 90, 255))
    img = Image.alpha_composite(img, rej)
    d = ImageDraw.Draw(img)
    fn = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 30)
    for letra, x in (('A', 54.0), ('B', 27.0), ('C', 1.0)):
        px_, _, _ = cam.proyectar((x, 0, 0))
        d.text((px_ / SS - 10, H - 44), letra, font=fn, fill=(16, 40, 70, 255))
    img.convert('RGB').save(os.path.join(OUT, 'escala_abc.jpg'), quality=92)


ESCENAS = {'heroica': heroica, 'vistas': vistas, 'fases': fases, 'escala': escala, 'aleteo': aleteo, 'juicio': juicio,
           'heroica_b': lambda: heroica(nombre='heroica_b', cual='b'), 'heroica_c': lambda: heroica(nombre='heroica_c', cual='c'),
           'vistas_b': lambda: vistas(cual='b'), 'vistas_c': lambda: vistas(cual='c'), 'escala_abc': escala_abc}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        r = ESCENAS[k]()
        print(k, r if r else '')

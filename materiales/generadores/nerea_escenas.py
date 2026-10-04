"""
Renders del boceto de Nerea para la ficha de diseno.

Uso: python nerea_escenas.py <raiz del proyecto> <carpeta de salida>
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
FUENTE = 'C:/Windows/Fonts/'
SS = 2

# ----------------------------------------------------------------------
#  Materiales extra para el jugador de escala (sin piel de vanilla)
# ----------------------------------------------------------------------
def _plano(c1, c2, semilla):
    a, b = nm._hex(c1), nm._hex(c2)
    return nm._loseta(semilla, lambda x, y, r: a if r.random() < 0.7 else b)

nm.MAT.update({
    'piel': _plano('c9956c', 'b8845e', 40),
    'pelo': _plano('3b2a1e', '2c1f16', 41),
    'camisa': _plano('2f8f8a', '27807b', 42),
    'pantalon': _plano('3a3f7a', '30356a', 43),
    'bota': _plano('4a4a4a', '3a3a3a', 44),
})

def jugador():
    n = nm.nodo
    return n('raiz', (0, 0, 0), (0, 0, 0), [], [
        n('cuerpo', (0, 0, 0), (0, 0, 0), [((-4, 0, -2, 8, 12, 4), 'camisa')], [
            n('cabeza', (0, 0, 0), (0, 0, 0), [((-4, -8, -4, 8, 8, 8), 'piel'), ((-4.2, -8.2, -4.2, 8.4, 3, 8.4), 'pelo'),
                                               ((-3, -4.5, -4.3, 2, 1, 0.4), 'pelo'), ((1, -4.5, -4.3, 2, 1, 0.4), 'pelo')]),
            n('bi', (6, 2, 0), (0, 0, 0), [((-2, -2, -2, 4, 12, 4), 'piel'), ((-2.1, -2.1, -2.1, 4.2, 5, 4.2), 'camisa')]),
            n('bd', (-6, 2, 0), (0, 0, 0), [((-2, -2, -2, 4, 12, 4), 'piel'), ((-2.1, -2.1, -2.1, 4.2, 5, 4.2), 'camisa')]),
        ]),
        n('pi', (2, 12, 0), (0, 0, 0), [((-2, 0, -2, 4, 12, 4), 'pantalon'), ((-2.1, 9, -2.1, 4.2, 3, 4.2), 'bota')]),
        n('pd', (-2, 12, 0), (0, 0, 0), [((-2, 0, -2, 4, 12, 4), 'pantalon'), ((-2.1, 9, -2.1, 4.2, 3, 4.2), 'bota')]),
    ])

def jugador_a_mundo(x, z, guinada):
    # el jugador mide 32 px: de y=0 (cabeza -8) a y=24
    return vr.T(x, 0, z) @ vr.Ry(guinada * vr.D2R) @ vr.T(0, 1.5, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])

# ----------------------------------------------------------------------
#  Poses
# ----------------------------------------------------------------------
REPOSO = {'tridente': {'rot': (180, 0, 0)}, 'mano_der': {'rot': (0, 0, 0)}}

HEROICA = {
    'torso': {'rot': (-6, 12, 0)},
    'cuello': {'rot': (6, 0, 0)},
    'cabeza': {'rot': (10, -14, 6)},
    'mandibula': {'rot': (28, 0, 0)},
    'hombro_der': {'rot': (0, 0, 0)},
    'brazo_der': {'rot': (-112, -10, -22)},
    'antebrazo_der': {'rot': (-28, 0, 0)},
    'tridente': {'rot': (-8, 0, 0)},
    'brazo_izq': {'rot': (-48, 0, -62)},
    'antebrazo_izq': {'rot': (-35, 0, 0)},
    'cadena_mano': {'rot': (-70, 30, 0)},
    'pierna_izq': {'rot': (-16, 0, -10)},
    'espinilla_izq': {'rot': (18, 0, 0)},
    'pierna_der': {'rot': (14, 0, 12)},
    'espinilla_der': {'rot': (8, 0, 0)},
}

MOLINO = {
    'torso': {'rot': (-4, 0, 0)},
    'cabeza': {'rot': (14, 0, 0)},
    'mandibula': {'rot': (20, 0, 0)},
    'brazo_der': {'rot': (-20, 0, 25)}, 'antebrazo_der': {'rot': (-20, 0, 0)}, 'tridente': {'rot': (180, 0, 0)},
    'brazo_izq': {'rot': (0, 0, -95)}, 'antebrazo_izq': {'rot': (0, 0, 0)}, 'cadena_mano': {'oculto': True},
    'pierna_izq': {'rot': (0, 0, -10)}, 'pierna_der': {'rot': (0, 0, 10)},
}

LIBERADO = {
    'pelvis': {'pos': (0, 14, 0)},
    'torso': {'rot': (6, 0, 0)},
    'cabeza': {'rot': (-16, 0, 0)},
    'mandibula': {'rot': (6, 0, 0)},
    'pierna_izq': {'rot': (-80, 0, -4)}, 'espinilla_izq': {'rot': (85, 0, 0)}, 'pie_izq': {'rot': (0, 0, 0)},
    'pierna_der': {'rot': (6, 0, 6)}, 'espinilla_der': {'rot': (100, 0, 0)}, 'pie_der': {'rot': (-30, 0, 0)},
    'brazo_der': {'rot': (-30, 0, 0)}, 'antebrazo_der': {'rot': (-60, 0, 0)}, 'tridente': {'rot': (150, 0, 0)},
    'brazo_izq': {'rot': (-20, 0, -6)}, 'antebrazo_izq': {'rot': (-40, 0, 0)}, 'cadena_mano': {'oculto': True},
}

# ----------------------------------------------------------------------
#  Ambiente submarino
# ----------------------------------------------------------------------
LUCES_MAR = [
    ((-0.3, 1.0, -0.4), (0.55, 0.85, 0.95), 1.0, 'llave'),     # luz de superficie
    ((0.7, 0.2, 0.8), (0.95, 0.25, 0.55), 0.9, 'contra'),      # el corazon tine la espalda
    ((-0.9, 0.1, 0.3), (0.2, 0.7, 0.9), 0.5, 'contra'),
]
AMB_MAR = (0.12, 0.2, 0.26)

class NieblaMar:
    color = (0.03, 0.14, 0.2)
    def __init__(self, ini=6.0, largo=26.0):
        self.ini, self.largo = ini, largo
    def __call__(self, z):
        return np.clip((z - self.ini) / self.largo, 0, 0.94)

def fondo_mar(W, H, horizonte):
    y = np.linspace(0, 1, H)[:, None, None]
    arriba, abajo = np.array([0.10, 0.42, 0.50]), np.array([0.01, 0.06, 0.10])
    col = arriba + (abajo - arriba) * np.clip(y / max(horizonte / H, 0.3), 0, 1) ** 0.8
    return np.broadcast_to(col, (H, W, 3)).copy()

def rayos(W, H, semilla, n=7):
    capa = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    for _ in range(n):
        x = r.uniform(0.05, 0.95) * W
        ancho = r.uniform(0.02, 0.06) * W
        inc = r.uniform(-0.25, 0.1) * W
        d.polygon([(x, 0), (x + ancho, 0), (x + ancho + inc + ancho, H), (x + inc - ancho * 0.3, H)], fill=r.randint(30, 70))
    return np.array(capa.filter(ImageFilter.GaussianBlur(W / 60))).astype(float) / 255.0

def burbujas(img, n, semilla, zona=None):
    d = ImageDraw.Draw(img, 'RGBA')
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x = r.uniform(*(zona[0] if zona else (0, W))); y = r.uniform(*(zona[1] if zona else (0, H)))
        rad = r.choice([2, 3, 3, 4, 6, 9]) * W / 1600
        d.ellipse((x - rad, y - rad, x + rad, y + rad), outline=(190, 240, 255, 150), width=max(1, int(rad / 3)))
        d.ellipse((x - rad * 0.4, y - rad * 0.55, x - rad * 0.05, y - rad * 0.2), fill=(230, 255, 255, 160))
    for _ in range(n * 3):   # nieve marina
        x, y = r.uniform(0, W), r.uniform(0, H)
        d.point((x, y), fill=(200, 230, 235, r.randint(40, 120)))

def bloom(img_np, emis_np, radios=((4, 0.9), (16, 0.7), (48, 0.5))):
    e = Image.fromarray((np.clip(emis_np, 0, 1) * 255).astype(np.uint8))
    out = img_np.copy()
    for r_, k in radios:
        out += np.array(e.filter(ImageFilter.GaussianBlur(r_))).astype(float) / 255.0 * k
    return np.clip(out + emis_np * 0.6, 0, 1)

def vineta(arr, fuerza=0.6):
    H, W = arr.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - fuerza * np.clip(np.hypot((xx - W / 2) / (W * 0.6), (yy - H / 2) / (H * 0.6)) - 0.3, 0, 1) ** 1.3
    return arr * v[..., None]

def suelo(lienzo, cam, ext=14, prof=34, luces=LUCES_MAR[:1], niebla=None):
    qs = []
    r = random.Random(5)
    for gx in range(-ext, ext):
        for gz in range(-10, prof):
            mat = 'arena' if r.random() < 0.75 else 'prisma_osc'
            h = 0.0 if abs(gx) < 6 and abs(gz) < 6 else r.choice([0, 0, 0, 0.0625])
            qs.append(([(gx, h, gz), (gx + 1, h, gz), (gx + 1, h, gz + 1), (gx, h, gz + 1)],
                       [(0, 0), (1, 0), (1, 1), (0, 1)], mat))
    nm.dibujar(lienzo, cam, qs, luces, (0.16, 0.24, 0.3), niebla)

def pilar(x, z, alto=7):
    """Pilar-ancla: columna de prismarina con el sello brillante arriba."""
    raiz = nm.nodo('pilar', (0, 0, 0), (0, 0, 0), [
        ((-12, -alto * 16, -12, 24, alto * 16, 24), 'prisma_osc'),
        ((-14, -16, -14, 28, 16, 28), 'prisma'),
        ((-14, -alto * 16 - 4, -14, 28, 6, 28), 'prisma'),
        ((-6, -alto * 16 + 14, -12.6, 12, 12, 1), 'sello'),
        ((-12.6, -alto * 16 + 14, -6, 1, 12, 12), 'sello'),
    ], [nm.coral_rama('pc1', (8, -alto * 16 - 4, 4), (0, 0, 14), 'coral_r', 14),
        nm.coral_rama('pc2', (-6, -16, -14), (-20, 0, -10), 'coral_n', 10)])
    M = vr.T(x, 0, z) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1])
    return nm.quads(raiz, {}, M)

def componer(lz, W, H, horizonte, semilla, extra_rayos=1.0):
    alfa = Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    col = np.array(Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    emis = np.array(Image.fromarray((np.clip(lz.emis, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    a = np.array(alfa).astype(float)[..., None] / 255
    fondo = fondo_mar(W, H, horizonte)
    arr = col * a + fondo * (1 - a)
    arr += rayos(W, H, semilla)[..., None] * np.array([0.45, 0.85, 0.9]) * 0.55 * extra_rayos
    arr = bloom(arr, emis)
    arr = vineta(arr)
    # grado: sombras hacia el azul petroleo
    arr = np.clip(arr * np.array([0.92, 1.0, 1.04]) + np.array([0.0, 0.01, 0.02]), 0, 1)
    img = Image.fromarray((arr * 255).astype(np.uint8))
    burbujas(img, int(40 * W / 1600), semilla)
    return img

# ----------------------------------------------------------------------
#  1. Heroica
# ----------------------------------------------------------------------
def heroica(W=1600, H=900, libre=False, pose=HEROICA, nombre='heroica', guinada=24, cam_ojo=(-7.6, 0.9, -14.2),
            cam_obj=(0.2, 4.6, 0), fov=46, cadenas=True):
    cam = vr.Camara(ojo=cam_ojo, objetivo=cam_obj, fov=fov, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaMar()
    suelo(lz, cam, niebla=niebla)
    pil = pilar(-6.5, 8) + pilar(7.5, 7)
    nm.dibujar(lz, cam, pil, LUCES_MAR, AMB_MAR, niebla)
    if cadenas:
        for p0, p1 in (((-0.7, 3.9, 0.7), (-6.5, 6.4, 7.2)), ((0.8, 3.7, 0.7), (7.5, 6.4, 6.2)),
                       ((-0.6, 2.1, 0.6), (-6.2, 1.3, 7.2)), ((0.7, 2.0, 0.6), (7.2, 1.3, 6.2))):
            nm.dibujar(lz, cam, nm.cadena_mundo(p0, p1, 1.8), LUCES_MAR, AMB_MAR, niebla)
    M = nm.entidad_a_mundo(0, 0, 0, guinada)
    q = nm.quads(nm.esqueleto(libre), pose, M)
    nm.dibujar(lz, cam, q, LUCES_MAR, AMB_MAR, niebla, brillo=1.5)
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 300, 0.0, cam.ojo[2] + cam.f[2] * 300]))[1] / SS
    img = componer(lz, W, H, horiz, 3)
    img.save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    return img

# ----------------------------------------------------------------------
#  2. Escala: jugador, Vigia y Nerea sobre la reticula de bloques
# ----------------------------------------------------------------------
def escala(W=1600, H=820):
    cam = vr.Camara(ojo=(0.4, 3.2, -60), objetivo=(0.4, 3.2, 0), fov=7.4, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
    amb = (0.32, 0.34, 0.38)
    nm.dibujar(lz, cam, nm.quads(jugador(), {}, jugador_a_mundo(-4.6, 0, -20)), luces, amb)
    vt = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia.png'))
    vb = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia_ojo.png'))
    vq = vr.quads_del_modelo({}, modelo_a_mundo=vr.entidad_a_mundo(-2.0, 0, 0, -20))
    vr.dibujar_quads(lz, cam, vq, vt, emis=vb, luces=luces, ambiente=amb, brillo=1.2)
    nq = nm.quads(nm.esqueleto(), REPOSO, nm.entidad_a_mundo(3.2, 0, 0, -20))
    nm.dibujar(lz, cam, nq, luces, amb, brillo=1.2)
    col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
    a = lz.alfa[..., None]
    bg = np.array([0.93, 0.95, 0.96])
    arr = col * a + bg * (1 - a)
    img = Image.fromarray((arr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).convert('RGBA')
    # reticula de bloques: una linea por bloque de alto, numerada
    rej = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rej)
    f = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 20)
    for b in range(0, 7):
        _, y, _ = cam.proyectar((0.4, b, 0)); y /= SS
        d.line((70, y, W - 20, y), fill=(40, 70, 80, 110 if b else 220), width=2 if b == 0 else 1)
        d.text((20, y - 12), f'{b}', font=f, fill=(40, 70, 80, 255))
    for x in range(-6, 7):
        xx, _, _ = cam.proyectar((x, 0, 0)); xx /= SS
        d.line((xx, 0, xx, H), fill=(40, 70, 80, 35), width=1)
    img = Image.alpha_composite(img, rej)
    # la altura de cada uno, encima de su cabeza
    d = ImageDraw.Draw(img)
    fn = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 30)
    fa = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 19)
    for nombre, x, alto, techo in (('JUGADOR', -4.6, 1.8, 2.15), ('VIGÍA', -2.0, 2.9, 3.45), ('NEREA', 3.2, 5.6, 6.55)):
        px_, py, _ = cam.proyectar((x, techo, 0)); px_ /= SS; py /= SS
        cifra = f'{alto:.1f}'.replace('.', ',') + ' bloques'
        wn = d.textlength(nombre, font=fn); wa = d.textlength(cifra, font=fa)
        d.text((px_ - wn / 2, py - 66), nombre, font=fn, fill=(16, 52, 60, 255))
        d.text((px_ - wa / 2, py - 26), cifra, font=fa, fill=(60, 96, 104, 255))
    img.convert('RGB').save(os.path.join(OUT, 'escala.jpg'), quality=92)
    # alturas proyectadas, para colocar las etiquetas en la pagina
    alturas = {}
    for nombre, x, alto in (('jugador', -4.6, 1.8), ('vigia', -2.0, 2.9), ('nerea', 3.2, 5.6)):
        px_, py, _ = cam.proyectar((x, alto, 0))
        alturas[nombre] = (round(px_ / SS / W, 4), round(py / SS / H, 4))
    return alturas

# ----------------------------------------------------------------------
#  3. Vistas: frente, perfil, espalda
# ----------------------------------------------------------------------
def vistas(W=1500, H=760):
    lienzos = []
    for g in (0, -90, 180):
        cam = vr.Camara(ojo=(0, 3.0, -45), objetivo=(0, 3.0, 0), fov=8.5, ancho=500 * SS, alto=H * SS)
        lz = vr.Lienzo(500 * SS, H * SS)
        luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
        nq = nm.quads(nm.esqueleto(), REPOSO, nm.entidad_a_mundo(0, 0, 0, g))
        nm.dibujar(lz, cam, nq, luces, (0.32, 0.34, 0.38), brillo=1.2)
        col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
        a = lz.alfa[..., None]
        arr = col * a + np.array([0.93, 0.95, 0.96]) * (1 - a)
        lienzos.append(Image.fromarray((arr * 255).astype(np.uint8)).resize((500, H), Image.LANCZOS))
    img = Image.new('RGB', (W, H), (237, 242, 245))
    for i, im in enumerate(lienzos):
        img.paste(im, (i * 500, 0))
    img.save(os.path.join(OUT, 'vistas.jpg'), quality=92)

# ----------------------------------------------------------------------
#  4. Molino de cadenas: vista alta, el anillo de cadenas girando
# ----------------------------------------------------------------------
def molino(W=1600, H=900):
    cam = vr.Camara(ojo=(-7.5, 10.5, -11.5), objetivo=(0, 1.2, 0), fov=46, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaMar(9, 30)
    suelo(lz, cam, niebla=niebla)
    M = nm.entidad_a_mundo(0, 0, 0, 20)
    nm.dibujar(lz, cam, nm.quads(nm.esqueleto(), MOLINO, M), LUCES_MAR, AMB_MAR, niebla, brillo=1.5)
    # cuatro cadenas desde el cuerpo hasta el anillo, y el anillo de eslabones
    R, alto = 7.0, 0.9
    for k in range(4):
        a = math.radians(20 + k * 90)
        nm.dibujar(lz, cam, nm.cadena_mundo((0.25 * math.cos(a), 2.4, 0.25 * math.sin(a)),
                                            (R * math.cos(a), alto, R * math.sin(a)), 1.8), LUCES_MAR, AMB_MAR, niebla)
    n = 26
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        p0 = (R * math.cos(a0), alto, R * math.sin(a0)); p1 = (R * math.cos(a1), alto, R * math.sin(a1))
        nm.dibujar(lz, cam, nm.cadena_mundo(p0, p1, 1.8), LUCES_MAR, AMB_MAR, niebla)
    # jugadores alrededor, uno saltando la cadena
    for (x, z, g, y) in ((-5.5, -6.0, 40, 0.0), (6.4, -3.6, -60, 1.1), (2.0, 7.8, 200, 0.0), (-8.6, 2.0, 100, 0.0)):
        M = vr.T(0, y, 0) @ jugador_a_mundo(x, z, g)
        nm.dibujar(lz, cam, nm.quads(jugador(), {}, M), LUCES_MAR, AMB_MAR, niebla)
    horiz = 0
    img = componer(lz, W, H, H * 0.25, 9, 0.6)
    # estela de giro: arcos difuminados sobre el anillo
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    pts = []
    for k in range(0, 361, 4):
        a = math.radians(k)
        x, y, _ = cam.proyectar((R * math.cos(a), alto + 0.1, R * math.sin(a)))
        pts.append((x / SS, y / SS))
    d.line(pts, fill=(180, 240, 255, 90), width=int(14 * W / 1600))
    img = Image.alpha_composite(img.convert('RGBA'), capa.filter(ImageFilter.GaussianBlur(6)))
    img.convert('RGB').save(os.path.join(OUT, 'molino.jpg'), quality=90)

def main():
    import sys as _s
    solo = _s.argv[3].split(',') if len(_s.argv) > 3 else None
    if solo:
        for k in solo:
            {'heroica': heroica, 'escala': escala, 'vistas': vistas, 'molino': molino,
             'liberado': lambda: heroica(libre=True, pose=LIBERADO, nombre='liberado', guinada=10,
                                         cam_ojo=(-3.8, 1.6, -8.4), cam_obj=(0.3, 2.2, 0), fov=40, cadenas=False)}[k]()
        return
    heroica()
    print('heroica')
    alturas = escala()
    print('escala', alturas)
    vistas()
    print('vistas')
    molino()
    print('molino')
    heroica(libre=True, pose=LIBERADO, nombre='liberado', guinada=10, cam_ojo=(-3.8, 1.6, -8.4),
            cam_obj=(0.3, 2.2, 0), fov=40, cadenas=False)
    print('liberado')

if __name__ == '__main__':
    main()

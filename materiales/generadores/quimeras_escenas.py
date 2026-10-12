"""
Renders de la ficha de las tres quimeras (quinto jefe, 12-10-2026): cada una en
su sitio y con su luz, su cabeza de cerca, las tres juntas con un jugador para la
escala y la lamina de materiales.

  A  Quelvora   el paramo de las atalayas caidas, al ocaso
  B  Ixtara     la noche de luna, con niebla baja
  C  Espinara   la cienaga de noche, con esporas que flotan

Uso: python quimeras_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne            # el jugador de escala
import quimeras_modelo as qm

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
FUENTE = 'C:/Windows/Fonts/'
SS = 2
TAU = math.tau
D = vr.D2R


# ----------------------------------------------------------------------
#  El lienzo: lo opaco que tapa algo le borra tambien el brillo
# ----------------------------------------------------------------------
class Lienzo(vr.Lienzo):
    def triangulo(self, cam, P_, UV, tex, luz_fn, emis_tex=None, niebla=None, aditivo=False, brillo=1.0, envolver=False,
                  translucido=0.0):
        if aditivo or translucido > 0:
            return super().triangulo(cam, P_, UV, tex, luz_fn, emis_tex, niebla, aditivo, brillo, envolver, translucido)
        s = [cam.proyectar(p) for p in P_]
        if min(q[2] for q in s) < 0.05:
            return
        xs = [q[0] for q in s]
        ys = [q[1] for q in s]
        x0, x1 = max(int(math.floor(min(xs))), 0), min(int(math.ceil(max(xs))), self.W - 1)
        y0, y1 = max(int(math.floor(min(ys))), 0), min(int(math.ceil(max(ys))), self.H - 1)
        if x0 > x1 or y0 > y1:
            return
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = s
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            return
        l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l3 = 1 - l1 - l2
        dentro = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        if not dentro.any():
            return
        z = 1 / (l1 / az + l2 / bz + l3 / cz)
        u = (l1 * UV[0][0] / az + l2 * UV[1][0] / bz + l3 * UV[2][0] / cz) * z
        v = (l1 * UV[0][1] / az + l2 * UV[1][1] / bz + l3 * UV[2][1] / cz) * z
        th, tw = tex.shape[:2]
        if envolver:
            tu, tv = np.floor(u * tw).astype(int) % tw, np.floor(v * th).astype(int) % th
        else:
            tu, tv = np.clip((u * tw).astype(int), 0, tw - 1), np.clip((v * th).astype(int), 0, th - 1)
        texel = tex[tv, tu]
        zb = self.z[y0:y1 + 1, x0:x1 + 1]
        m = dentro & (texel[..., 3] > 25) & (z < zb)
        if not m.any():
            return
        rgb = texel[..., :3] / 255.0 * luz_fn
        if niebla is not None:
            f = niebla(z)[..., None]
            rgb = rgb * (1 - f) + np.array(niebla.color) * f
        col = self.color[y0:y1 + 1, x0:x1 + 1]
        col[m] = rgb[m]
        self.alfa[y0:y1 + 1, x0:x1 + 1][m] = 1.0
        zb[m] = z[m]
        emg = self.emis[y0:y1 + 1, x0:x1 + 1]
        emg[m] = 0.0
        if emis_tex is not None:
            et = emis_tex[tv, tu]
            ea = et[..., 3] / 255.0
            me = m & (ea > 0.01)
            k = 1.0 if niebla is None else (1 - niebla(z))[..., None]
            emg[me] = (et[..., :3] / 255.0 * ea[..., None] * brillo * k)[me]
            col[me] = np.maximum(col, et[..., :3] / 255.0 * k * ea[..., None])[me]


class Niebla:
    def __init__(self, color, d0, d1, tope=0.96):
        self.color, self.d0, self.d1, self.tope = color, d0, d1, tope

    def __call__(self, z):
        return np.clip((z - self.d0) / (self.d1 - self.d0), 0, self.tope)


# ----------------------------------------------------------------------
#  Las tres luces y los tres sitios
# ----------------------------------------------------------------------
SITIO = {
    'A': dict(
        luces=[((-0.75, 0.42, 0.55), (1.0, 0.6, 0.3), 1.1, 'llave'), ((0.7, 0.3, -0.6), (0.4, 0.5, 0.95), 0.55, 'contra'),
               ((0.3, 0.12, -1.0), (1.0, 0.45, 0.2), 0.4, 'contra')],
        amb=(0.17, 0.15, 0.2), niebla=(0.24, 0.13, 0.13), suelo='suelo_a',
        cielo=((0.03, 0.03, 0.09), (0.26, 0.11, 0.16), (0.96, 0.46, 0.18)),
        motas=((255, 170, 90), (120, 112, 108)),
    ),
    'B': dict(
        luces=[((0.35, 1.0, 0.5), (0.78, 0.84, 1.0), 0.95, 'llave'), ((-0.6, 0.2, -0.7), (1.0, 0.25, 0.32), 0.8, 'contra'),
               ((0.8, 0.1, -0.3), (0.6, 0.62, 0.95), 0.3, 'contra')],
        amb=(0.13, 0.12, 0.17), niebla=(0.07, 0.06, 0.1), suelo='suelo_b',
        cielo=((0.008, 0.008, 0.025), (0.06, 0.04, 0.09), (0.2, 0.08, 0.14)),
        motas=((255, 90, 110), (170, 170, 200)),
    ),
    'C': dict(
        luces=[((-0.2, 1.0, 0.6), (0.72, 0.82, 0.95), 0.85, 'llave'), ((0.6, 0.2, -0.8), (0.5, 1.0, 0.4), 0.65, 'contra'),
               ((-0.8, 0.2, -0.3), (0.45, 0.4, 0.95), 0.35, 'contra')],
        amb=(0.11, 0.14, 0.13), niebla=(0.04, 0.08, 0.07), suelo='suelo_c',
        cielo=((0.006, 0.012, 0.012), (0.03, 0.07, 0.065), (0.09, 0.2, 0.16)),
        motas=((190, 255, 110), (230, 255, 160)),
    ),
}


def suelo(lz, cam, niebla, sitio, ext=96, paso=16):
    """El suelo en baldosas grandes (la loseta de 128 px cubre 4 bloques)."""
    qs = []
    k = paso / 4
    for gx in range(-ext, ext, paso):
        for gz in range(-ext, ext, paso):
            P = [(gx + paso, 0.0, gz), (gx, 0.0, gz), (gx, 0.0, gz + paso), (gx + paso, 0.0, gz + paso)]
            qs.append(([np.array(p) for p in P], [(k, 0), (0, 0), (0, k), (k, k)], SITIO[sitio]['suelo']))
    qm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


def decorado(lz, cam, niebla, sitio, semilla=3):
    """Lo de alrededor: atalayas caidas (A), hebras por el suelo (B), zarzas y farolillos (C)."""
    r = random.Random(semilla)
    qs = []
    if sitio == 'A':
        for (x, z, alto) in ((-30, -38, 7.0), (24, -46, 9.5), (-52, -10, 6.0), (44, -14, 5.0), (8, -70, 11.0)):
            qm._torre(qs, vr.T(x, -0.3, z), alto, r, ruina=True, bandera=r.random() < 0.5)
        for _ in range(26):
            x, z = r.uniform(-40, 40), r.uniform(-30, 40)
            if math.hypot(x, z) < 12:
                continue
            w = r.uniform(0.4, 1.6)
            qm.caja(qs, vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 90) * D) @ vr.Rz(r.uniform(-12, 12) * D), -w / 2, 0, -w / 2, w,
                    r.uniform(0.3, 1.2), w, 'sillar')
    elif sitio == 'B':
        for k in range(16):
            a = k * TAU / 16 + r.uniform(-0.1, 0.1)
            p = np.array((math.cos(a) * 9, 0.05, math.sin(a) * 9))
            for _ in range(5):
                a += r.uniform(-0.25, 0.25)
                q = p + np.array((math.cos(a) * 3.2, 0, math.sin(a) * 3.2))
                qm.hebra(qs, p, q, 0.06, 'hilo_luz')
                p = q
    elif sitio == 'C':
        for _ in range(14):
            x, z = r.uniform(-36, 36), r.uniform(-30, 32)
            if math.hypot(x, z) < 13:
                continue
            p = np.array((x, -0.4, z))
            a = r.uniform(0, TAU)
            for j in range(5):
                q = p + np.array((math.cos(a) * 1.2, 0.5 - j * 0.3, math.sin(a) * 1.2))
                qm.hebra(qs, p, q, 0.3, 'tallo')
                for _ in range(2):
                    qm.caja(qs, qm.em.marco(q, (r.uniform(-1, 1), r.uniform(0.2, 1), r.uniform(-1, 1))), -0.05, -0.05, 0,
                            0.1, 0.1, 0.5, 'espina')
                p = q
                a += r.uniform(-0.6, 0.6)
    qm.dibujar(lz, cam, qs, SITIO[sitio]['luces'], SITIO[sitio]['amb'], niebla)


def haz(lz, cam, p, d, largo=34.0, radio=6.0, brillo=0.55):
    """El haz del faro: un cono de luz aditivo (no atraviesa lo opaco)."""
    tex = np.zeros((32, 32, 4), np.uint8)
    for y in range(32):
        for x in range(32):
            k = y / 31
            a = (1 - k) ** 1.6 * 230
            tex[y, x] = (255, 236, 196, int(a))
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    u = np.cross(d, (0, 1, 0))
    u = u / max(np.linalg.norm(u), 1e-6)
    w = np.cross(u, d)
    fin = p + d * largo
    anillo = [fin + (u * math.cos(a) + w * math.sin(a)) * radio for a in np.linspace(0, TAU, 13)]
    for i in range(12):
        lz.triangulo(cam, [p, anillo[i], anillo[i + 1]], [(0.5, 0.0), (0.0, 1.0), (1.0, 1.0)], tex, np.ones(3),
                     aditivo=True, brillo=brillo)


# ----------------------------------------------------------------------
#  El cielo y la composicion
# ----------------------------------------------------------------------
def cielo(W, H, horizonte, sitio):
    arriba, medio, abajo = (np.array(c) for c in SITIO[sitio]['cielo'])
    y = np.linspace(0, 1, H)[:, None]
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.66, arriba + (medio - arriba) * (k / 0.66), medio + (abajo - medio) * ((k - 0.66) / 0.34))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy().reshape(H, W, 3)
    r = random.Random(7)
    for _ in range(int(W * H / (5200 if sitio != 'A' else 14000))):
        x, yy = r.randint(0, W - 1), r.randint(0, H - 1)
        if yy < horizonte * 0.7:
            col[yy, x] = np.clip(col[yy, x] + r.uniform(0.2, 0.8) * (1 - yy / max(horizonte, 1)), 0, 1)
    yy, xx = np.mgrid[0:H, 0:W]
    if sitio == 'A':
        # el sol que se pone detras, a la izquierda, y las atalayas lejanas recortadas
        sx, sy = W * 0.22, horizonte - H * 0.02
        d = np.hypot((xx - sx) / W, (yy - sy) / H)
        col += np.clip(1 - d / 0.42, 0, 1)[..., None] ** 2.2 * np.array((0.9, 0.42, 0.14))
        col = np.where(((xx - sx) ** 2 + (yy - sy) ** 2 < (H * 0.024) ** 2)[..., None], np.array((1.0, 0.9, 0.7)), col)
    if sitio == 'B':
        mx, my, mr = W * 0.78, H * 0.2, H * 0.085
        d = np.hypot(xx - mx, yy - my) / mr
        col += np.clip(1 - (d - 1) / 5, 0, 1)[..., None] ** 2.5 * np.array((0.3, 0.32, 0.42))
        disco = np.clip(1.2 - d, 0, 1) ** 0.5
        luna = np.array((0.86, 0.88, 0.96)) - ((np.sin(xx * 0.05) * np.cos(yy * 0.07)) > 0.6)[..., None] * 0.08
        col = col * (1 - disco[..., None]) + disco[..., None] * luna
    if sitio in ('B', 'C'):
        banda = np.exp(-((yy - horizonte) / (H * 0.06)) ** 2)[..., None]
        col += banda * (np.array((0.12, 0.1, 0.14)) if sitio == 'B' else np.array((0.06, 0.16, 0.12)))
    return np.clip(col, 0, 1)


def siluetas_atalayas(img, horizonte, semilla=4):
    """Atalayas lejanas recortadas contra el ocaso (2D), con alguna ventana encendida."""
    d = ImageDraw.Draw(img)
    W, H = img.size
    r = random.Random(semilla)
    x = 0
    while x < W:
        w = r.randint(int(W * 0.012), int(W * 0.03))
        h = r.randint(int(H * 0.03), int(H * 0.12))
        base = horizonte + 2
        col = (22, 15, 20)
        d.rectangle((x, base - h, x + w, base), fill=col)
        for k in range(0, w, max(3, w // 4)):
            d.rectangle((x + k, base - h - max(2, w // 6), x + k + max(2, w // 8), base - h), fill=col)
        if r.random() < 0.5:
            wy = base - h * r.uniform(0.4, 0.8)
            d.rectangle((x + w // 2 - 1, wy, x + w // 2 + 1, wy + 3), fill=(255, 160, 70))
        x += w + r.randint(int(W * 0.03), int(W * 0.12))
    return img


def tono(x, blanco=0.35):
    m = x.max(axis=-1, keepdims=True)
    exceso = np.clip(m - 1, 0, None)
    y = x / np.maximum(1, m)
    return np.clip(y + (1 - y) * np.clip(exceso * blanco, 0, 1), 0, 1)


def bloom(arr, emis, radios=((3, 0.8), (14, 0.6), (44, 0.45))):
    e = Image.fromarray((np.clip(emis, 0, 1) * 255).astype(np.uint8))
    out = arr.copy()
    for r_, k in radios:
        out += np.array(e.filter(ImageFilter.GaussianBlur(r_))).astype(float) / 255.0 * k
    return out + emis * 0.55


def vineta(arr, fuerza=0.5):
    H, W = arr.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - fuerza * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.3, 0, 1) ** 1.3
    return arr * v[..., None]


def motas(img, n, semilla, colores):
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H)
        c = colores[0] if r.random() < 0.6 else colores[1]
        rad = r.choice((1, 1, 1.5, 2)) * W / 1600
        largo = r.uniform(1, 5) * W / 1600
        d.line((x, y, x + r.uniform(-1, 1), y + largo), fill=(*c, r.randint(110, 220)), width=max(1, int(rad)))
    glow = capa.filter(ImageFilter.GaussianBlur(2))
    out = Image.alpha_composite(img.convert('RGBA'), glow)
    return Image.alpha_composite(out, capa)


def componer(lz, cam, W, H, sitio, n_motas=150, semilla=3, fuerza_vineta=0.5):
    alfa = np.array(Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float)[..., None] / 255
    col = np.array(Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    emis = np.array(Image.fromarray((np.clip(tono(lz.emis), 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz, sitio)
    if sitio == 'A':
        fimg = siluetas_atalayas(Image.fromarray((fondo * 255).astype(np.uint8)), int(horiz))
        fondo = np.array(fimg).astype(float) / 255
    arr = col * alfa + fondo * (1 - alfa)
    arr = tono(bloom(arr, emis))
    arr = vineta(arr, fuerza_vineta)
    return motas(Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)), int(n_motas * W / 1600), semilla,
                 SITIO[sitio]['motas'])


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    print('ok', nombre, flush=True)
    return img


def rotular(img, texto, sub=None):
    d = ImageDraw.Draw(img)
    W, H = img.size
    try:
        f1 = ImageFont.truetype(FUENTE + 'georgiab.ttf', int(H * 0.052))
        f2 = ImageFont.truetype(FUENTE + 'georgia.ttf', int(H * 0.026))
    except OSError:
        f1 = f2 = ImageFont.load_default()
    x, y = int(W * 0.035), int(H * 0.045)
    d.text((x + 2, y + 2), texto, font=f1, fill=(8, 6, 12, 255))
    d.text((x, y), texto, font=f1, fill=(244, 234, 210, 255))
    if sub:
        d.text((x + 2, y + int(H * 0.072) + 2), sub, font=f2, fill=(8, 6, 12, 255))
        d.text((x, y + int(H * 0.072)), sub, font=f2, fill=(206, 196, 214, 255))
    return img


def quimera(cual, **k):
    if cual == 'A':
        return qm.quelvora(**k)
    if cual == 'B':
        return qm.ixtara(**k)
    return qm.espinara(**k)


# ----------------------------------------------------------------------
#  Las escenas
# ----------------------------------------------------------------------
NOMBRE = {'A': 'Quelvora, la Devoradora de Atalayas', 'B': 'Ixtara, la Hilandera', 'C': 'Espinara, la Zarza que Florece'}
CAMARA_HEROE = {
    'A': ((27.0, 9.0, 42.0), (1.5, 8.5, -2.0), 44),
    'B': ((14.0, 9.0, 36.0), (0.0, 13.0, 0.0), 52),
    'C': ((16.0, 8.5, 25.0), (0.5, 10.5, 0.0), 46),
}
CAMARA_CABEZA = {
    'A': ((-5.5, 13.0, 13.0), (4.0, 15.0, -1.0), 46),
    'B': ((7.5, 18.0, 15.0), (0.2, 18.4, 1.8), 40),
    'C': ((8.0, 15.0, 15.5), (2.0, 14.6, 3.2), 42),
}
DE_CERCA = {'A': dict(boca=30.0), 'B': dict(partida=0.55), 'C': dict(abre=56.0)}
SUB_HEROE = {
    'A': 'gusano excavador + craneo de tres mandibulas + las atalayas que se trago + el ultimo faro por ojo',
    'B': 'sierpe de carretes + brazos de aguja + mascara de porcelana + un telar de luz entre las manos',
    'C': 'zarza trenzada + flor carnivora por cabeza + un craneo dentro que mira + estambres que muerden',
}
SUB_CABEZA = {
    'A': 'el faro es su unico ojo; las mandibulas se abren en tres, con dientes de almena',
    'B': 'la mascara se parte en dos: detras, la boca de agujas',
    'C': 'los petalos son las fauces; dentro, el craneo que mira',
}


def heroe(cual):
    W, H = 1600, 1000
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(SITIO[cual]['niebla'], 40, 140)
    ojo, obj, fov = CAMARA_HEROE[cual]
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, cual)
    decorado(lz, cam, niebla, cual)
    qs, info = quimera(cual)
    qm.dibujar(lz, cam, qs, SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    if cual == 'A':
        haz(lz, cam, *info['faro'])
    img = componer(lz, cam, W, H, cual, n_motas=170)
    guardar(rotular(img, NOMBRE[cual], SUB_HEROE[cual]), 'heroe_' + cual)


def cabeza(cual):
    W, H = 1600, 1000
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla(SITIO[cual]['niebla'], 40, 140)
    ojo, obj, fov = CAMARA_CABEZA[cual]
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    suelo(lz, cam, niebla, cual)
    decorado(lz, cam, niebla, cual)
    qs, info = quimera(cual, **DE_CERCA[cual])
    qm.dibujar(lz, cam, qs, SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    if cual == 'A':
        haz(lz, cam, *info['faro'], brillo=0.35)
    img = componer(lz, cam, W, H, cual, n_motas=110)
    guardar(rotular(img, NOMBRE[cual].split(',')[0], SUB_CABEZA[cual]), 'cabeza_' + cual)


def trio():
    """Las tres juntas, con un jugador delante: la escala."""
    W, H = 1800, 860
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla((0.05, 0.04, 0.08), 160, 330)
    cam = vr.Camara((4.0, 9.0, 170.0), (2.0, 8.0, 0.0), 23, W * SS, H * SS)
    suelo(lz, cam, niebla, 'B', ext=160, paso=32)
    for cual, x, giro in (('A', -42.0, 20), ('B', 0.0, 0), ('C', 40.0, -15)):
        qs, info = quimera(cual)
        M = vr.T(x, 0, 0) @ vr.Ry(giro * D)
        qm.dibujar(lz, cam, qm.transformar(qs, M), SITIO[cual]['luces'], SITIO[cual]['amb'], niebla)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(2.0, 40.0, 0)), SITIO['B']['luces'], SITIO['B']['amb'], niebla)
    img = componer(lz, cam, W, H, 'B', n_motas=90)
    guardar(rotular(img, 'Las tres, a escala', 'un jugador (1,8) delante · de alto: Quelvora 23 con el faro · Ixtara 21 · Espinara 20'), 'trio')


def materiales():
    """La lamina de materiales: cada loseta ampliada, con su nombre."""
    W = 1600
    hojas = [
        ('quitina', 'quitina, con anillos de crecimiento'), ('vientre_q', 'vientre de quitina palida'), ('hueso', 'hueso poroso'),
        ('sillar', 'sillares comidos por el caparazon'), ('pizarra', 'pizarra en escamas'), ('bronce', 'bronce con cardenillo'),
        ('estandarte', 'estandarte de las atalayas'), ('ventana', 'ventana encendida'), ('faro', 'la lente del faro'),
        ('laca', 'laca con su tela de oro'), ('porcelana', 'porcelana craquelada'), ('porcelana_rota', 'porcelana rota (late)'),
        ('hilo', 'hilo devanado'), ('oro', 'oro grabado'), ('tapiz', 'el tapiz del telar'),
        ('tallo', 'corteza de zarza con savia'), ('espina', 'espina'), ('petalo', 'petalo de terciopelo'),
        ('hoja', 'hoja encerada'), ('vaina', 'farolillo de semilla'), ('vidriera', 'LUZ: vidriera del faro'),
        ('ascua', 'LUZ: ascua'),
        ('hilo_luz', 'LUZ: hilo de luz'), ('savia', 'LUZ: savia'), ('polen', 'LUZ: polen'),
    ]
    cols, celda = 5, 248
    filas = (len(hojas) + cols - 1) // cols
    H = 120 + filas * (celda + 70)
    img = Image.new('RGB', (W, H), (18, 15, 22))
    d = ImageDraw.Draw(img)
    try:
        f1 = ImageFont.truetype(FUENTE + 'georgiab.ttf', 40)
        f2 = ImageFont.truetype(FUENTE + 'consola.ttf', 18)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((48, 34), 'Materiales: dibujados aqui, ninguno de vanilla', font=f1, fill=(244, 234, 210))
    for k, (mat, nota) in enumerate(hojas):
        t = qm.MAT[mat]
        h, w = t.shape[:2]
        esc = min(200 / w, 200 / h)
        im = Image.fromarray(t).resize((int(w * esc), int(h * esc)), Image.NEAREST)
        cx = 60 + (k % cols) * 306
        cy = 120 + (k // cols) * (celda + 70)
        fondo = Image.new('RGBA', (200, 200), (36, 30, 44, 255))
        fondo.paste(im, ((200 - im.width) // 2, (200 - im.height) // 2), im)
        img.paste(fondo.convert('RGB'), (cx, cy))
        d.rectangle((cx - 1, cy - 1, cx + 200, cy + 200), outline=(80, 70, 96))
        d.text((cx, cy + 210), mat, font=f2, fill=(244, 234, 210))
        d.text((cx, cy + 234), nota[:27], font=f2, fill=(170, 160, 186))
    guardar(img, 'materiales')


ESCENAS = {
    'heroe_A': lambda: heroe('A'), 'heroe_B': lambda: heroe('B'), 'heroe_C': lambda: heroe('C'),
    'cabeza_A': lambda: cabeza('A'), 'cabeza_B': lambda: cabeza('B'), 'cabeza_C': lambda: cabeza('C'),
    'trio': trio, 'materiales': materiales,
}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

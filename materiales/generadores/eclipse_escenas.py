"""
Renders de la ficha de diseno de la Serpiente del Eclipse: las tres variantes
(retrato y fauces), el plano heroe contra el eclipse, la escala junto a Novilis
y un jugador, y la lamina de paleta.

Escenario: un paramo de ceniza bajo un eclipse total: el cielo de noche subita,
las estrellas que salen a destiempo y el anillo de corona en lo alto.

Uso: python eclipse_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne            # el jugador de escala
import fuego_modelo as fm             # Novilis, para la escala
import eclipse_modelo as em

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
FUENTE = 'C:/Windows/Fonts/'
SS = 2
TAU = math.tau

# La luz del eclipse: una llave palida de corona, el contraluz rosado de la
# cromosfera y un ambiente de noche subita.
LUCES = [((0.25, 1.0, 0.45), (1.0, 0.93, 0.78), 1.05, 'llave'),
         ((-0.55, 0.25, -0.8), (0.95, 0.38, 0.6), 0.6, 'contra'),
         ((0.7, 0.15, 0.5), (0.5, 0.45, 0.95), 0.42, 'contra')]
AMB = (0.2, 0.17, 0.26)
# Donde esta el eclipse en el cielo (para el disco y los reflejos)
ECLIPSE = np.array([-26.0, 54.0, -88.0])


# ----------------------------------------------------------------------
#  El lienzo de fuego_escenas: lo opaco borra el brillo que tapa
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
            col[me] = np.maximum(col, et[..., :3] / 255.0 * k)[me]


class Niebla:
    def __init__(self, color, d0, d1):
        self.color, self.d0, self.d1 = color, d0, d1

    def __call__(self, z):
        return np.clip((z - self.d0) / (self.d1 - self.d0), 0, 0.96)


# ----------------------------------------------------------------------
#  El paramo de ceniza
# ----------------------------------------------------------------------
def _ceniza(semilla=30):
    r = random.Random(semilla)
    rampa = nm._rampa('100c14', '18131d', '211a28', '2c2434', '3a3042')
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            b = r.choice((1, 1, 2, 2, 2, 3))
            if x % 8 == 0 or y % 8 == 0:
                b = 0
            elif r.random() < 0.05:
                b = 4
            t[y, x] = (*rampa[b], 255)
    return t


em.MAT['ceniza'] = _ceniza()


def suelo(lz, cam, niebla, ext=70):
    qs = []
    paso = 14
    for gx in range(-ext, ext, paso):
        for gz in range(-ext, ext, paso):
            em.caja(qs, np.eye(4), gx, -1.0, gz, paso, 1.0, paso, 'ceniza')
    r = random.Random(12)
    for _ in range(26):
        x, z = r.uniform(-34, 34), r.uniform(-30, 34)
        if math.hypot(x, z) < 15:
            continue
        w = r.uniform(0.6, 2.4)
        h = r.uniform(0.4, 2.8)
        M = vr.T(x, 0, z) @ vr.Ry(r.uniform(0, 360) * vr.D2R) @ vr.Rz(r.uniform(-14, 14) * vr.D2R)
        em.caja(qs, M, -w / 2, 0, -w / 2, w, h, w, 'obsidiana')
    em.dibujar(lz, cam, qs, LUCES, AMB, niebla)


# ----------------------------------------------------------------------
#  El cielo del eclipse
# ----------------------------------------------------------------------
def cielo(W, H, horizonte):
    y = np.linspace(0, 1, H)[:, None]
    arriba = np.array([0.015, 0.012, 0.035])
    medio = np.array([0.1, 0.055, 0.14])
    abajo = np.array([0.42, 0.16, 0.2])          # la franja del ocaso subito
    k = np.clip(y / max(horizonte / H, 0.2), 0, 1)
    col = np.where(k < 0.68, arriba + (medio - arriba) * (k / 0.68), medio + (abajo - medio) * ((k - 0.68) / 0.32))
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy().reshape(H, W, 3)
    # las estrellas que salen a destiempo
    r = random.Random(7)
    for _ in range(int(W * H / 6200)):
        x, yy = r.randint(0, W - 1), r.randint(0, H - 1)
        if yy / H < horizonte / H * 0.75:
            b = r.uniform(0.25, 0.95) * (1 - yy / max(horizonte, 1))
            col[yy, x] = np.clip(col[yy, x] + b, 0, 1)
            if b > 0.5 and x + 1 < W:
                col[yy, x + 1] = np.clip(col[yy, x + 1] + b * 0.4, 0, 1)
    return col


def eclipse_en_cielo(arr, cam, W, H, pos=None, radio=4.6):
    """El sol devorado: el disco negro, el anillo de corona y sus llamaradas."""
    pos = ECLIPSE if pos is None else pos
    x, y, z = cam.proyectar(pos)
    if z <= 0:
        return arr
    x, y = x / SS, y / SS
    rp = cam.foco / SS * radio / z
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot(xx - x, yy - y) / max(rp, 1)
    nuc = np.array(nm._hex('fff6d8')) / 255
    pri = np.array(nm._hex('ffc23a')) / 255
    rojo = np.array(nm._hex('ff3a4a')) / 255
    # el resplandor largo y los rayos de la corona
    corona = np.clip(1 - (d - 1) / 7.0, 0, 1) ** 2.6
    a = np.arctan2(yy - y, xx - x)
    rayos = (np.abs(np.cos(a * 3 + 0.7)) ** 10 + np.abs(np.cos(a * 5 - 1.2)) ** 14) * np.clip(1 - (d - 1) / 5.5, 0, 1) * (d > 1)
    out = arr + corona[..., None] * pri * 0.5 + rayos[..., None] * nuc * 0.28
    # el anillo fino, casi blanco
    anillo = np.clip(1 - np.abs(d - 1.03) * rp / 2.6, 0, 1) ** 1.6
    out += anillo[..., None] * (nuc * 0.9 + pri * 0.35)
    # las protuberancias rojas, pegadas al borde
    r = random.Random(5)
    for _ in range(7):
        aa = r.uniform(0, TAU)
        px, py = x + math.cos(aa) * rp * 1.04, y + math.sin(aa) * rp * 1.04
        dd = np.hypot(xx - px, yy - py)
        out += np.clip(1 - dd / (rp * 0.1), 0, 1)[..., None] ** 1.5 * rojo * 0.5
    # el disco, negro del todo
    disco = np.clip(1.0 - (d - 0.985) * rp / 1.4, 0, 1)
    out = out * (1 - disco[..., None]) + disco[..., None] * np.array([0.004, 0.003, 0.01])
    return np.clip(out, 0, 1)


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


def motas(img, n, semilla):
    """Pavesas de corona que suben, y ceniza que flota."""
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    r = random.Random(semilla)
    W, H = img.size
    for _ in range(n):
        x, y = r.uniform(0, W), r.uniform(0, H)
        oro = r.random() < 0.55
        c = (255, 206, 92, r.randint(110, 220)) if oro else (164, 150, 180, r.randint(60, 130))
        largo = r.uniform(2, 6) * W / 1600 if oro else r.uniform(1, 2.5) * W / 1600
        d.line((x, y, x + r.uniform(-1, 1), y + largo), fill=c, width=max(1, int(r.choice([1, 1, 2]) * W / 1600)))
    glow = capa.filter(ImageFilter.GaussianBlur(2))
    out = Image.alpha_composite(img.convert('RGBA'), glow)
    return Image.alpha_composite(out, capa)


def componer(lz, cam, W, H, eclipse=True, n_motas=150, semilla=3, fuerza_vineta=0.5):
    alfa = np.array(Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float)[..., None] / 255
    col = np.array(Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    emis = np.array(Image.fromarray((np.clip(tono(lz.emis), 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 400, 0.0, cam.ojo[2] + cam.f[2] * 400]))[1] / SS
    fondo = cielo(W, H, horiz)
    if eclipse:
        fondo = eclipse_en_cielo(fondo, cam, W, H)
    arr = col * alfa + fondo * (1 - alfa)
    arr = tono(bloom(arr, emis))
    arr = vineta(arr, fuerza_vineta)
    arr = np.clip(arr * np.array([1.02, 0.98, 1.04]), 0, 1)
    return motas(Image.fromarray((arr * 255).astype(np.uint8)), int(n_motas * W / 1600), semilla)


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    print('ok', nombre, flush=True)
    return img


def rotular(img, texto, sub=None):
    d = ImageDraw.Draw(img)
    W, H = img.size
    try:
        f1 = ImageFont.truetype(FUENTE + 'georgiab.ttf', int(H * 0.055))
        f2 = ImageFont.truetype(FUENTE + 'georgia.ttf', int(H * 0.027))
    except OSError:
        f1 = f2 = ImageFont.load_default()
    x = int(W * 0.035)
    y = int(H * 0.045)
    d.text((x + 2, y + 2), texto, font=f1, fill=(10, 8, 16, 255))
    d.text((x, y), texto, font=f1, fill=(244, 232, 200, 255))
    if sub:
        d.text((x + 2, y + int(H * 0.075) + 2), sub, font=f2, fill=(10, 8, 16, 255))
        d.text((x, y + int(H * 0.075)), sub, font=f2, fill=(205, 188, 214, 255))
    return img


# ----------------------------------------------------------------------
#  Las escenas
# ----------------------------------------------------------------------
NOMBRE = {'A': 'A · Corona del Eclipse', 'B': 'B · Fauces del Ocaso', 'C': 'C · Devorasoles'}


def retrato(v):
    W, H = 1600, 1000
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla((0.05, 0.035, 0.08), 46, 120)
    if v == 'B':
        cam = vr.Camara((15.0, 10.5, -27.5), (-3.0, 8.8, 4.0), 44, W * SS, H * SS)
    else:
        cam = vr.Camara((16.5, 8.0, 23.0), (-1.0, 6.6, -0.5), 44, W * SS, H * SS)
    suelo(lz, cam, niebla)
    em.dibujar(lz, cam, em.serpiente(em.camino_alzada(), v, boca=20), LUCES, AMB, niebla)
    img = componer(lz, cam, W, H)
    guardar(rotular(img, NOMBRE[v], 'alzada: 13 bloques · 55 de largo'), 'retrato_' + v)


def fauces(v):
    W, H = 1600, 950
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla((0.05, 0.035, 0.08), 40, 110)
    cam = vr.Camara((4.2, 6.8, -18.0), (0.6, 5.4, -7.5), 40, W * SS, H * SS)
    suelo(lz, cam, niebla)
    em.dibujar(lz, cam, em.serpiente(em.camino_fauces(), v, boca=34, R=1.45), LUCES, AMB, niebla)
    img = componer(lz, cam, W, H, n_motas=90)
    guardar(rotular(img, NOMBRE[v], 'las fauces: la cromosfera dentro'), 'fauces_' + v)


def corona():
    """El plano heroe: la variante A de perfil, el anillo y el eclipse en el cielo detras."""
    W, H = 1600, 1000
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla((0.05, 0.035, 0.08), 50, 130)
    cam = vr.Camara((2.0, 2.2, 26.0), (-5.0, 9.0, -14.0), 42, W * SS, H * SS)
    suelo(lz, cam, niebla)
    em.dibujar(lz, cam, em.serpiente(em.camino_alzada(), 'A', boca=26), LUCES, AMB, niebla)
    img = componer(lz, cam, W, H, n_motas=200, semilla=8)
    guardar(rotular(img, 'La noche subita', 'el eclipse en lo alto; solo su corona alumbra'), 'corona')


def escala():
    W, H = 1800, 860
    lz = Lienzo(W * SS, H * SS)
    niebla = Niebla((0.05, 0.035, 0.08), 80, 220)
    cam = vr.Camara((4.0, 7.0, 80.0), (0.5, 6.6, -2.0), 15.5, W * SS, H * SS)
    suelo(lz, cam, niebla)
    em.dibujar(lz, cam, em.serpiente(em.camino_escala(), 'A', boca=8), LUCES, AMB, niebla)
    M = fm.entidad_a_mundo(8.5, 0, 8.0, 24)
    fm.dibujar(lz, cam, fm.quads('N', fm.HEROICA, M), LUCES, AMB, niebla, fase=1)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(14.5, 10.0, 12)), LUCES, AMB, niebla)
    img = componer(lz, cam, W, H, n_motas=120)
    guardar(rotular(img, 'La escala', 'un jugador (1,8) · Novilis (11,5) · la Serpiente (alzada, 13)'), 'escala')


def paleta():
    """La lamina de materiales y rampas, sin render: losetas ampliadas."""
    W, H = 1600, 790
    img = Image.new('RGB', (W, H), (16, 12, 22))
    d = ImageDraw.Draw(img)
    try:
        f1 = ImageFont.truetype(FUENTE + 'georgiab.ttf', 42)
        f2 = ImageFont.truetype(FUENTE + 'consola.ttf', 22)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((56, 36), 'Materiales del boceto', font=f1, fill=(244, 232, 200))
    filas = [
        ('escama', 'obsidiana ciruela, a tresbolillo'), ('escama_osc', 'la misma, honda'),
        ('vientre', 'placas de ceniza palida'), ('obsidiana', 'vitrea: cresta, cuernos y anillo'),
        ('placa', 'placa forjada y remachada'), ('oro', 'oro quemado batido'), ('marfil', 'colmillos'),
        ('corona', 'LUZ: la corona del eclipse'), ('cromo', 'LUZ: la cromosfera (fauces)'), ('ojo', 'LUZ: el ojo en rendija'),
    ]
    x0, y0 = 56, 130
    for i, (mat, nota) in enumerate(filas):
        cx = x0 + (i % 4) * 390
        cy = y0 + (i // 4) * 205
        t = em.MAT[mat]
        loseta = Image.fromarray(t).resize((160, 160), Image.NEAREST)
        img.paste(loseta, (cx, cy))
        d.rectangle((cx - 1, cy - 1, cx + 160, cy + 160), outline=(90, 78, 104))
        d.text((cx + 176, cy + 30), mat, font=f2, fill=(244, 232, 200))
        for j, linea in enumerate(_partir(nota, 24)):
            d.text((cx + 176, cy + 60 + j * 26), linea, font=f2, fill=(180, 166, 192))
    guardar(img, 'paleta')


def _partir(s, ancho):
    out, linea = [], ''
    for p in s.split():
        if len(linea) + len(p) + 1 > ancho:
            out.append(linea)
            linea = p
        else:
            linea = (linea + ' ' + p).strip()
    if linea:
        out.append(linea)
    return out


ESCENAS = {
    'retrato_A': lambda: retrato('A'), 'retrato_B': lambda: retrato('B'), 'retrato_C': lambda: retrato('C'),
    'fauces_A': lambda: fauces('A'), 'fauces_B': lambda: fauces('B'), 'fauces_C': lambda: fauces('C'),
    'corona': corona, 'escala': escala, 'paleta': paleta,
}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        ESCENAS[k]()

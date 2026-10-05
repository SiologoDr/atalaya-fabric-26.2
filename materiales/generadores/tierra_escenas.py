"""
Renders del boceto de Rajang, el Jaguar de Jade, para su ficha de diseno.

La arena es el Templo del Jaguar: una plaza de piedra con musgo en lo hondo
de la selva, con su piramide escalonada detras y los arboles cerrando el
cielo.

Uso: python tierra_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne
import viento_modelo as vm
import tierra_modelo as tm
import tierra_ataques as ta

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
FUENTE = 'C:/Windows/Fonts/'
SS = 2
_hex = nm._hex

# ----------------------------------------------------------------------
#  Materiales de la selva y el templo
# ----------------------------------------------------------------------
TIERRA = nm._rampa('3a2a1a', '4e3822', '62472c', '765838', '8e6c46')
MADERA = nm._rampa('2e1f12', '3e2a18', '50371f', '624528', '765434')
HOJAS = nm._rampa('12301a', '1a4222', '22562c', '2e6c36', '3e8644')


def _tierra(x, y, r):
    return TIERRA[r.choice([1, 2, 2, 3, 3, 4])] if r.random() > 0.05 else _hex('9a9a86')


def _madera(x, y, r):
    return MADERA[0] if x % 5 == 0 else MADERA[r.choice([1, 2, 2, 3, 4])]


def _hojas(x, y, r):
    return HOJAS[r.choice([0, 1, 2, 2, 3, 4])] if r.random() > 0.12 else _hex('0c2010')


def _roca_tierra(x, y, r):
    R = nm._rampa('4a4436', '5c5442', '6e6650', '827a62', '9a9278')
    return TIERRA[1] if (x + y * 3) % 11 == 0 else R[r.choice([1, 2, 2, 3])]


def _suelo_selva(n=256, semilla=15):
    """Suelo de selva continuo (8x8 bloques por textura): tierra oscura,
    hojarasca, raices y musgo."""
    r = random.Random(semilla)
    base = ta._mezcla(('1a1a0e', '242414', '30301a', '3c3c20', '4a4a28'), 0.5 + 0.6 * (ta._fbm2(n, n, (6, 6), semilla) - 0.5))
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(img)
    for _ in range(900):
        x, y = r.uniform(0, n), r.uniform(0, n)
        a = r.uniform(0, math.pi)
        l = r.uniform(2, 5)
        col = r.choice([(58, 74, 30), (74, 90, 36), (92, 84, 40), (110, 92, 46), (44, 62, 26), (70, 52, 30)])
        d.line((x, y, x + math.cos(a) * l, y + math.sin(a) * l), fill=(*col, 255), width=2)
    for _ in range(14):
        x, y = r.uniform(0, n), r.uniform(0, n)
        a = r.uniform(0, math.tau)
        for k in range(14):
            a += r.uniform(-0.4, 0.4)
            x1, y1 = x + math.cos(a) * 5, y + math.sin(a) * 5
            d.line((x, y, x1, y1), fill=(52, 38, 22, 255), width=2)
            x, y = x1, y1
    t = np.array(img)
    mm = ta._fbm2(n, n, (12, 12), semilla + 4)
    musgo = mm > 0.6
    k = np.clip((mm[musgo] - 0.6) / 0.1, 0, 1)[:, None] * 0.75
    verde = ta._mezcla(('22381a', '2c4420', '385426'), ta._fbm2(n, n, (24, 24), semilla + 5)[musgo])
    t[musgo, :3] = np.clip(t[musgo, :3] * (1 - k) + verde * k, 0, 255)
    return t


def _losas_templo(n=128, semilla=16):
    """Las losas de la plaza (4x4 bloques por textura): hiladas desfasadas de
    piedra tallada, juntas con musgo, alguna rota."""
    r = random.Random(semilla)
    ruido = ta._fbm2(n, n, (8, 8), semilla)
    fino = ta._fbm2(n, n, (32, 32), semilla + 1)
    t = np.zeros((n, n, 3))
    junta = np.zeros((n, n), bool)
    fila = 0
    while fila < n:
        alto = r.choice([16, 16, 24])
        x = -r.randint(0, 20)
        while x < n:
            ancho = r.choice([16, 24, 32])
            tono = r.uniform(-0.12, 0.12)
            y0, y1 = fila, min(n, fila + alto)
            x0, x1 = max(0, x), min(n, x + ancho)
            t[y0:y1, x0:x1] = ta._mezcla(tm._rampa('3a3a2e', '4a4a3a', '5c5c48', '6e6e58', '84846a'),
                                         0.5 + tono + 0.4 * (ruido[y0:y1, x0:x1] - 0.5) + 0.2 * (fino[y0:y1, x0:x1] - 0.5))
            junta[y0:y1, x0] = True
            junta[y0, x0:x1] = True
            x += ancho
        fila += alto
    t[junta] = ta._mezcla(('1e2414', '2c3a1c', '3a5022'), fino[junta])
    return np.c_[np.clip(t, 0, 255).reshape(-1, 3), np.full(n * n, 255)].reshape(n, n, 4).astype(np.uint8)


SELVA = {
    'tierra': nm._loseta(401, _tierra),
    'madera': nm._loseta(402, _madera),
    'hojas': nm._loseta(403, _hojas),
    'roca_tierra': nm._loseta(404, _roca_tierra),
    'selva': _suelo_selva(),
    'plaza': _losas_templo(),
}

LUCES_SELVA = [
    ((-0.5, 1.0, -0.35), (1.0, 0.9, 0.7), 1.1, 'llave'),         # el sol que se cuela entre los arboles
    ((0.7, 0.35, 0.7), (0.45, 1.0, 0.55), 0.8, 'contra'),        # el jade lo recorta en verde
    ((-0.8, 0.2, 0.6), (0.9, 0.8, 0.5), 0.4, 'contra'),
]
AMB_SELVA = (0.24, 0.3, 0.24)


class NieblaSelva:
    color = (0.42, 0.55, 0.46)

    def __init__(self, ini=16.0, largo=50.0):
        self.ini, self.largo = ini, largo

    def __call__(self, z):
        return np.clip((z - self.ini) / self.largo, 0, 0.85)


def cielo_selva(W, H, horizonte, semilla=1, oscuro=0.0):
    """Cielo de selva: claro y brumoso en el horizonte, cerrado arriba por las
    copas de los arboles; con 'oscuro' se vuelve tormenta verde (Cataclismo)."""
    r = random.Random(semilla)
    y = np.linspace(0, 1, H)[:, None, None]
    arriba, abajo = np.array([0.24, 0.4, 0.36]), np.array([0.74, 0.84, 0.66])
    col = arriba + (abajo - arriba) * np.clip(y / max(horizonte / H, 0.3), 0, 1) ** 1.2
    col = np.broadcast_to(col, (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    sol = np.exp(-(((xx - W * 0.22) / (W * 0.25)) ** 2 + ((yy - H * 0.18) / (H * 0.3)) ** 2))
    col += sol[..., None] * np.array([0.35, 0.3, 0.15])
    copas = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(copas)
    for _ in range(26):
        cx = r.choice([r.uniform(-0.1, 0.25), r.uniform(0.75, 1.1)]) * W
        cy = r.uniform(-0.1, 0.35) * H
        rr = r.uniform(0.06, 0.16) * W
        d.ellipse((cx - rr, cy - rr * 0.7, cx + rr, cy + rr * 0.7), fill=r.randint(160, 255))
    copas = np.array(copas.filter(ImageFilter.GaussianBlur(W / 160))).astype(float)[..., None] / 255
    col = col * (1 - copas * 0.6) + np.array([0.1, 0.2, 0.12]) * copas * 0.6
    if oscuro:
        col = col * (1 - oscuro) + (np.array([0.06, 0.1, 0.08]) + np.array([0.15, 0.4, 0.15]) * sol[..., None]) * oscuro
    return np.clip(col, 0, 1)


def rayos_sol(W, H, semilla=3, n=7, k=0.18):
    """Haces de luz que bajan entre las copas."""
    r = random.Random(semilla)
    capa = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(capa)
    for _ in range(n):
        x0 = r.uniform(0.0, 0.6) * W
        ancho = r.uniform(0.02, 0.06) * W
        x1 = x0 + r.uniform(0.15, 0.35) * W
        d.polygon([(x0, 0), (x0 + ancho, 0), (x1 + ancho * 3, H), (x1, H)], fill=r.randint(40, 90))
    return np.array(capa.filter(ImageFilter.GaussianBlur(W / 60))).astype(float)[..., None] / 255 * k


def caja(x, y, z, w, h, d, mat):
    """Una caja en bloques de mundo (y hacia arriba), como quads."""
    raiz = nm.nodo('c', (0, 0, 0), (0, 0, 0), [((0, -h * 16, 0, w * 16, h * 16, d * 16), mat)])
    return nm.quads(raiz, {}, vr.T(x, y, z) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1]))


def dibujar_mundo(lz, cam, qs, niebla=None, fase=1, luces=None, amb=None):
    mats = dict(tm.materiales(fase))
    mats.update(SELVA)
    mats['plaza_losa'] = SELVA['plaza']
    luces = LUCES_SELVA if luces is None else luces
    amb = AMB_SELVA if amb is None else amb
    for P, UV, mat in qs:
        tex = mats[mat]
        emis = None
        if isinstance(tex, tuple):
            tex, emis = tex
        if mat in tm.EMISIVOS:
            luz, emis = np.ones(3), tex
        else:
            luz = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, amb)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla, brillo=1.3, envolver=True)


def plaza(radio=24, prof=44, ext=26):
    """La plaza de losas y, alrededor, el suelo de la selva; las dos texturas
    corren seguidas de bloque a bloque."""
    qs = []
    for gx in range(-ext, ext):
        for gz in range(-30, prof):
            d = math.hypot(gx + 0.5, gz + 0.5)
            if d < radio:
                k, mat = 4.0, 'plaza'
            else:
                k, mat = 8.0, 'selva'
            qs.append(([(gx, 0, gz), (gx + 1, 0, gz), (gx + 1, 0, gz + 1), (gx, 0, gz + 1)],
                       [(gx / k, gz / k), ((gx + 1) / k, gz / k), ((gx + 1) / k, (gz + 1) / k), (gx / k, (gz + 1) / k)], mat))
    return qs


def piramide(x, z, niveles=6, base=22, alto=2.2):
    qs = []
    for k in range(niveles):
        w = base - k * 3.2
        qs += caja(x - w / 2, k * alto, z - w / 2, w, alto, w, 'templo')
    w = base - niveles * 3.2
    qs += caja(x - w / 2 + 1, niveles * alto, z - w / 2 + 1, w - 2, 3.0, w - 2, 'templo')
    qs += caja(x - 1.6, niveles * alto + 1.0, z - w / 2 + 0.8, 3.2, 1.6, 0.4, 'oro')
    # la escalera, por delante
    for k in range(niveles * 3):
        qs += caja(x - 2.5, k * alto / 3, z - base / 2 - 1.2 + k * (3.2 / 2) / 3, 5, alto / 3, 1.2, 'templo')
    return qs


def arbol(x, z, alto, copa, semilla):
    r = random.Random(semilla)
    qs = caja(x - 0.6, 0, z - 0.6, 1.2, alto, 1.2, 'madera')
    for _ in range(5):
        cx, cz = x + r.uniform(-copa / 2, copa / 2), z + r.uniform(-copa / 2, copa / 2)
        w = r.uniform(copa * 0.5, copa)
        qs += caja(cx - w / 2, alto - r.uniform(0, 2), cz - w / 2, w, r.uniform(2, 3.5), w, 'hojas')
    return qs


def jugador(lz, cam, x, z, guinada, y=0.0, niebla=None):
    M = vr.T(0, y, 0) @ ne.jugador_a_mundo(x, z, guinada)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, M), LUCES_SELVA, AMB_SELVA, niebla)


def rajang(lz, cam, x, z, guinada, pose, fase=1, niebla=None, y=0.0, luces=None, amb=None, brillo=1.5, escala=1.0):
    M = tm.entidad_a_mundo(x, y, z, guinada, escala)
    tm.dibujar(lz, cam, tm.quads(tm.esqueleto(fase), pose, M), LUCES_SELVA if luces is None else luces,
               AMB_SELVA if amb is None else amb, fase=fase, niebla=niebla, brillo=brillo)


def componer(lz, W, H, horizonte, semilla=1, oscuro=0.0, rayos=True, cielo_extra=None):
    alfa = np.array(Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float)[..., None] / 255
    col = np.array(Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    emis = np.array(Image.fromarray((np.clip(lz.emis, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(float) / 255
    fondo = cielo_selva(W, H, horizonte, semilla, oscuro)
    if cielo_extra is not None:
        fondo, emis_cielo = cielo_extra(fondo)
        emis = emis + emis_cielo * (1 - alfa)
    arr = col * alfa + fondo * (1 - alfa)
    if rayos and not oscuro:
        arr = arr + rayos_sol(W, H, semilla) * np.array([1.0, 0.95, 0.7])
    arr = ne.bloom(arr, emis, radios=((4, 0.7), (14, 0.5), (44, 0.35)))
    arr = ne.vineta(arr, 0.5)
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert('RGBA')


def polvo(img, n, zona, semilla, color=(150, 120, 80)):
    r = random.Random(semilla)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for _ in range(n):
        x, y = r.uniform(*zona[0]), r.uniform(*zona[1])
        rr = r.uniform(12, 50) * img.size[0] / 1600
        d.ellipse((x - rr, y - rr * 0.6, x + rr, y + rr * 0.6), fill=(*color, r.randint(40, 110)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(img.size[0] / 200)))


def horizonte(cam):
    return cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 300, 0.0, cam.ojo[2] + cam.f[2] * 300]))[1] / SS


# ----------------------------------------------------------------------
#  1. Heroica: ruge en la plaza del templo
# ----------------------------------------------------------------------
def heroica(W=1600, H=900, fase=1, nombre='heroica'):
    cam = vr.Camara(ojo=(-10.0, 1.0, -15.0), objetivo=(1.5, 5.2, 2.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaSelva()
    escena = plaza() + piramide(4, 34)
    for i, (x, z, alto, copa) in enumerate(((-24, 18, 14, 9), (24, 22, 16, 10), (-30, 34, 18, 11), (30, 4, 13, 8),
                                            (-20, -4, 12, 7))):
        escena += arbol(x, z, alto, copa, i)
    dibujar_mundo(lz, cam, escena, niebla, fase)
    for (x, z, g) in ((-9.0, 3.0, 120),):
        jugador(lz, cam, x, z, g, niebla=niebla)
    rajang(lz, cam, 2.5, 5.0, -20, tm.RUGIDO, fase, niebla)
    img = componer(lz, W, H, horizonte(cam), 3)
    polvo(img, 30, ((W * 0.35, W * 0.95), (H * 0.62, H * 0.8)), 4)
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)


# ----------------------------------------------------------------------
#  2. Vistas: frente, perfil y espalda
# ----------------------------------------------------------------------
def vistas(W=1800, H=600):
    lienzos = []
    luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 1, 0.7), 0.5, 'contra')]
    for g, ojo in ((0, (0, 6.0, -60)), (-90, (0, 6.0, -60)), (180, (0, 6.0, -60))):
        cam = vr.Camara(ojo=ojo, objetivo=(0, 5.0, 0) if g != -90 else (0, 5.0, -1.5), fov=27 if g == -90 else 15, ancho=600 * SS, alto=H * SS)
        lz = vr.Lienzo(600 * SS, H * SS)
        rajang(lz, cam, 0, 0, g, tm.ACECHO, 1, luces=luces, amb=(0.34, 0.36, 0.32), brillo=1.2)
        lienzos.append(lz)
    img = Image.new('RGB', (W, H), (238, 242, 236))
    for k, lz in enumerate(lienzos):
        col = np.clip(lz.color + lz.emis * 0.4, 0, 1)
        a = lz.alfa[..., None]
        arr = col * a + np.array([0.93, 0.95, 0.92]) * (1 - a)
        im = Image.fromarray((arr * 255).astype(np.uint8)).resize((600, H), Image.LANCZOS)
        img.paste(im, (k * 600, 0))
    img.save(os.path.join(OUT, 'vistas.jpg'), quality=92)


# ----------------------------------------------------------------------
#  3. Las cuatro fases
# ----------------------------------------------------------------------
def fases(W=1600, H=520):
    img = Image.new('RGB', (W, H), (0, 0, 0))
    w = W // 4
    for k in range(4):
        fase = k + 1
        cam = vr.Camara(ojo=(-23.0, 5.0, -30.0), objetivo=(-1.0, 4.6, 1.0), fov=46, ancho=w * SS, alto=H * SS)
        lz = vr.Lienzo(w * SS, H * SS)
        dibujar_mundo(lz, cam, plaza(16, 18, 16), NieblaSelva(18, 30), fase)
        rajang(lz, cam, 1.0, 2, -62, tm.RUGIDO if fase >= 3 else tm.ACECHO, fase, NieblaSelva(18, 30))
        im = componer(lz, w, H, horizonte(cam), 5 + k, oscuro=0.25 * (fase - 1), rayos=fase <= 2)
        img.paste(im.convert('RGB'), (k * w, 0))
    img.save(os.path.join(OUT, 'fases.jpg'), quality=90)


# ----------------------------------------------------------------------
#  4. Garra Terrestre: clava la zarpa; por la grieta revientan cumulos de
#     esquirlas de roca, cada uno mas grande, hasta el ultimo, el mas alto,
#     dentro del aro verde que avisaba donde iba a salir.
#
#  En todas las escenas de ataques se pinta primero lo opaco (mundo, mallas,
#  jugadores, Rajang) y al final lo que brilla sumado (grietas, calcos,
#  halos, estelas), para que el brillo del suelo no atraviese a nadie.
# ----------------------------------------------------------------------
ta._TEX['plaza_losa'] = (SELVA['plaza'], None)


def _arboles(*sitios):
    qs = []
    for i, (x, z, alto, copa) in enumerate(sitios):
        qs += arbol(x, z, alto, copa, i)
    return qs


def _tex_aro_aviso(n=256, color=(150, 255, 120)):
    """El aro fino que avisa donde va a reventar el ultimo pico."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    a = np.exp(-((d - 0.94) / 0.025) ** 2) + 0.25 * np.exp(-((d - 0.94) / 0.09) ** 2) + 0.12 * np.clip(1 - d, 0, 1) ** 2
    t = np.zeros((n, n, 4))
    t[..., :3] = color
    t[..., 3] = np.clip(a, 0, 1) * 255
    return t.astype(np.uint8)


ARO_AVISO = _tex_aro_aviso()


def garra(W=1600, H=900):
    cam = vr.Camara(ojo=(-19.0, 2.6, -12.0), objetivo=(0.0, 3.5, -11.5), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaSelva(20, 50)
    escena = plaza() + piramide(14, 34)
    dibujar_mundo(lz, cam, escena, niebla, 1)
    r = random.Random(3)
    golpe = (1.6, -5.4)
    final = (-0.6, -24.0)
    ramas = [(-3.5, -2.0), (3.8, -1.6), (-2.6, 1.8), (3.0, 2.4)]
    ta.grieta(lz, cam, *golpe, final[0], final[1] - 1.0, 1.1, semilla=5, parte='oscura')
    for k, (dx, dz) in enumerate(ramas):
        ta.grieta(lz, cam, *golpe, golpe[0] + dx, golpe[1] + dz, 0.5, semilla=20 + k, parte='oscura')
    mallas, polvos = [], []
    n = 8
    for k in range(n):
        t = k / (n - 1)
        z = golpe[1] - 2.0 - t * (golpe[1] - 2.0 - final[1])
        x = golpe[0] + (final[0] - golpe[0]) * t + 0.3 * math.sin(k * 1.7)
        alto = 1.2 + 5.6 * t ** 1.6
        mallas += ta.pico(x, z, alto, 0.35 + 0.75 * t ** 1.3, (r.uniform(-0.12, 0.12), -0.16), semilla=k + 1)
        polvos.append((x, 0.2, z, 1.0 + 1.6 * t))
    # terrones que saltan, mas altos cuanto mas lejos
    for j in range(26):
        t = r.uniform(0.2, 1)
        z = golpe[1] - 2.0 - t * (golpe[1] - 2.0 - final[1])
        x = golpe[0] + (final[0] - golpe[0]) * t + r.uniform(-2.4, 2.4)
        mallas += ta.roca_cubica(x, r.uniform(1.0, 2.0 + 7.0 * t), z + r.uniform(-1.5, 1.5), r.uniform(0.12, 0.35), semilla=300 + j)
    ta.dibujar(lz, cam, mallas, LUCES_SELVA, AMB_SELVA, niebla)
    jugador(lz, cam, final[0] + 0.6, final[1] - 1.4, 60, y=8.2, niebla=niebla)
    rajang(lz, cam, 1.0, 2.5, 0, tm.ZARPAZO, 1, niebla)
    # lo que brilla
    ta.grieta(lz, cam, *golpe, final[0], final[1] - 1.0, 1.1, semilla=5, brillo=1.5, parte='brillo')
    for k, (dx, dz) in enumerate(ramas):
        ta.grieta(lz, cam, *golpe, golpe[0] + dx, golpe[1] + dz, 0.5, semilla=20 + k, brillo=1.0, parte='brillo')
    ta.calco(lz, cam, *golpe, 3.2, ta.ONDA, 0.9)
    ta.calco(lz, cam, final[0], final[1], 3.4, ARO_AVISO, 1.6, y=0.06)
    img = componer(lz, W, H, horizonte(cam), 6)
    ta.polvo_en(img, cam, polvos, SS, (128, 110, 80), 7)
    ta.polvo_en(img, cam, [(golpe[0], 0.0, golpe[1], 2.4)], SS, (120, 104, 76), 8, 1.6)
    img.convert('RGB').save(os.path.join(OUT, 'garra.jpg'), quality=90)


# ----------------------------------------------------------------------
#  5. Terremoto Ancestral: golpea el suelo con las dos manos; la onda
#     levanta las losas, las grietas corren y por toda la plaza revientan
#     pilares de roca. A los jugadores, el lastre (lentitud); a el, la
#     coraza de runas (resistencia).
# ----------------------------------------------------------------------
def _tex_lastre(n=128, color=(230, 170, 90)):
    """El lastre bajo los pies: aro con tres flechas hacia dentro."""
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    d.ellipse((n * 0.08, n * 0.08, n * 0.92, n * 0.92), outline=(*color, 210), width=max(2, n // 32))
    for k in range(3):
        a = math.tau * k / 3
        for s in (0.0, 0.1):
            r0 = n * (0.36 - s)
            p = [(c + math.cos(a - 0.3) * r0, c + math.sin(a - 0.3) * r0),
                 (c + math.cos(a) * (r0 - n * 0.09), c + math.sin(a) * (r0 - n * 0.09)),
                 (c + math.cos(a + 0.3) * r0, c + math.sin(a + 0.3) * r0)]
            d.line(p, fill=(*color, 230), width=max(2, n // 36))
    return np.array(img.filter(ImageFilter.GaussianBlur(0.8)))


def _tex_runas(w=512, h=32, color=(255, 210, 110)):
    """La banda de runas de la coraza: dos filetes y la greca."""
    t = np.zeros((h, w, 4))
    t[..., :3] = color
    a = np.zeros((h, w))
    a[1:3] = 0.9
    a[h - 3:h - 1] = 0.9
    g = ta._greca_banda(w, h - 10)
    a[5:h - 5][g] = 0.75
    t[..., 3] = a * 255
    return t.astype(np.uint8)


LASTRE = _tex_lastre()
RUNAS = _tex_runas()


def aro_runas(lz, cam, x, y, z, radio, alto, brillo=1.0, n=40, giro=0.0):
    for k in range(n):
        a0, a1 = giro + math.tau * k / n, giro + math.tau * (k + 1) / n
        P = [(x + math.cos(a0) * radio, y + alto / 2, z + math.sin(a0) * radio),
             (x + math.cos(a1) * radio, y + alto / 2, z + math.sin(a1) * radio),
             (x + math.cos(a1) * radio, y - alto / 2, z + math.sin(a1) * radio),
             (x + math.cos(a0) * radio, y - alto / 2, z + math.sin(a0) * radio)]
        UV = [(k / n, 0), ((k + 1) / n, 0), ((k + 1) / n, 1), (k / n, 1)]
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], RUNAS, np.ones(3), None, None, aditivo=True, brillo=brillo)


def terremoto(W=1600, H=900):
    cam = vr.Camara(ojo=(-16.5, 9.0, -19.5), objetivo=(0.0, 2.8, 3.5), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaSelva(26, 60)
    escena = plaza() + piramide(4, 36)
    dibujar_mundo(lz, cam, escena, niebla, 2)
    r = random.Random(12)
    bx, bz = 0.0, 4.0
    grietas = []
    for k in range(9):
        a = math.tau * k / 9 + r.uniform(-0.2, 0.2)
        d0, d1 = 3.0, r.uniform(11, 19)
        grietas.append((bx + math.cos(a) * d0, bz + math.sin(a) * d0, bx + math.cos(a) * d1, bz + math.sin(a) * d1,
                        r.uniform(0.5, 0.8), 40 + k))
    for g in grietas:
        ta.grieta(lz, cam, *g[:5], semilla=g[5], parte='oscura')
    mallas, polvos = [], []
    # la onda: un anillo de losas levantadas que se aleja
    for k in range(30):
        a = math.tau * k / 30 + r.uniform(-0.05, 0.05)
        d = 10.5 + r.uniform(-0.5, 0.5)
        mallas += ta.losa(bx + math.cos(a) * d, bz + math.sin(a) * d, r.uniform(0.9, 1.3), r.uniform(35, 65),
                          -math.degrees(a) + 90, r.uniform(0.15, 0.45), 0.35, semilla=500 + k, mat='plaza_losa')
        if k % 2 == 0:
            polvos.append((bx + math.cos(a) * d, 0.3, bz + math.sin(a) * d, 1.5))
    # los pilares de roca, en grupos repartidos alrededor
    grupos = []
    for k in range(11):
        a = math.tau * k / 11 + r.uniform(-0.15, 0.15)
        d = r.choice([r.uniform(6.0, 8.0), r.uniform(13.5, 19.0)])
        grupos.append((bx + math.cos(a) * d, bz + math.sin(a) * d, k % 4 != 3))
    avisos = []
    for i, (x, z, sale) in enumerate(grupos):
        if sale:
            for j in range(r.randint(3, 5)):
                a = r.uniform(0, math.tau)
                dd = 0 if j == 0 else r.uniform(1.3, 2.2)
                mallas += ta.pilar_tierra(x + math.cos(a) * dd, z + math.sin(a) * dd,
                                          r.uniform(4.0, 7.5) * (1 if j == 0 else r.uniform(0.45, 0.8)), r.uniform(1.3, 1.9),
                                          semilla=i * 10 + j + 1)
            for j in range(5):
                a = r.uniform(0, math.tau)
                mallas += ta.losa(x + math.cos(a) * 3.0, z + math.sin(a) * 3.0, r.uniform(0.5, 0.8), r.uniform(20, 55),
                                  -math.degrees(a) + 90, 0.05, 0.25, semilla=700 + i * 10 + j, mat='plaza_losa')
            for j in range(6):
                mallas += ta.roca_cubica(x + r.uniform(-2.5, 2.5), r.uniform(2, 9), z + r.uniform(-2.5, 2.5), r.uniform(0.15, 0.4),
                                         semilla=900 + i * 10 + j)
            polvos.append((x, 0.3, z, 3.0))
        else:
            avisos.append((x, z))
    ta.dibujar(lz, cam, mallas, LUCES_SELVA, AMB_SELVA, niebla)
    jugadores = ((-8.0, -9.0, 200), (-2.0, -11.5, 180), (6.0, -8.5, 150), (-11.0, 0.5, 230))
    for (x, z, g) in jugadores:
        jugador(lz, cam, x, z, g, niebla=niebla)
        piedras = []
        for k, a in enumerate(np.linspace(0, math.tau, 6)[:-1]):
            piedras += ta.roca_cubica(x + math.cos(a) * 0.8, 0.25 + 0.2 * math.sin(a * 3), z + math.sin(a) * 0.8, 0.1,
                                      semilla=k + int(x * 10))
        ta.dibujar(lz, cam, piedras, LUCES_SELVA, AMB_SELVA, niebla)
    rajang(lz, cam, bx, bz, 20, tm.AGAZAPADO, 2, niebla)
    # lo que brilla
    for g in grietas:
        ta.grieta(lz, cam, *g[:5], semilla=g[5], brillo=1.1, parte='brillo')
    ta.calco(lz, cam, bx, bz, 7.5, ta.ONDA, 0.7)
    ta.calco(lz, cam, bx, bz, 15.0, ta.ONDA, 0.5)
    for x, z in avisos:
        ta.calco(lz, cam, x, z, 2.4, ta.AVISO, 1.2, giro=r.uniform(0, 60))
    for (x, z, g) in jugadores:
        ta.calco(lz, cam, x, z, 1.3, LASTRE, 1.0, giro=g)
    aro_runas(lz, cam, bx, 2.0, bz, 6.4, 0.7, 1.0)
    aro_runas(lz, cam, bx, 5.2, bz, 5.4, 0.5, 0.8, giro=0.3)
    img = componer(lz, W, H, horizonte(cam), 8)
    ta.polvo_en(img, cam, polvos, SS, (128, 112, 84), 9)
    img.convert('RGB').save(os.path.join(OUT, 'terremoto.jpg'), quality=90)


# ----------------------------------------------------------------------
#  6. Sello de la Tierra: cuatro totems en lo alto de plataformas de tierra;
#     se sube saltando por las piedras que flotan alrededor y hay que
#     romperlos. Dos ya han caido. Detras, el coloso de tierra se alza para
#     el rugido; el aro de fuera del circulo es el tiempo que queda.
# ----------------------------------------------------------------------
def _tex_linea(w=16, h=256, color=(140, 255, 150)):
    u = np.abs(np.linspace(-1, 1, w))[None] * np.ones((h, 1))
    t = np.zeros((h, w, 4))
    t[..., :3] = color
    t[..., 3] = np.clip(1 - u, 0, 1) ** 3 * 230
    return t.astype(np.uint8)


LINEA = _tex_linea()
ARO_PIEDRA = ta._tex_onda(128, (140, 255, 140))


def sello(W=1600, H=900):
    cam = vr.Camara(ojo=(-5.0, 3.2, -25.0), objetivo=(1.5, 9.5, 16.0), fov=66, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaSelva(34, 90)
    escena = plaza(26, 96, 60)
    dibujar_mundo(lz, cam, escena, niebla, 2)
    r = random.Random(17)
    cx, cz, d = 0.0, 4.0, 14.0
    tot = []
    estados = ('roto', 'on', 'on', 'roto')
    for k in range(4):
        a = math.tau * k / 4 + math.tau / 8 + math.pi
        x, z = cx + math.sin(a) * d, cz - math.cos(a) * d
        tot.append((x, z, r.uniform(7.5, 9.0), estados[k], a))
    mallas, pasos, polvos = [], [], []
    for i, (x, z, alto, est, a) in enumerate(tot):
        mallas += ta.plataforma(x, z, alto, 4.6, semilla=i + 1)
        mallas += ta.totem(x, alto - 0.05, z, 'on', 1.5, giro=math.degrees(a) + 45, semilla=i, roto=(est == 'roto'))
        # las piedras flotantes, en espiral alrededor de la plataforma
        a0 = a + math.pi * 0.6
        for j in range(5):
            h = 1.3 + (alto - 1.6) * j / 4.6
            aj = a0 + j * 0.95
            rr = 2.3 + 2.0
            px, pz = x + math.cos(aj) * rr, z + math.sin(aj) * rr
            mallas += ta.piedra_flotante(px, h, pz, r.uniform(1.05, 1.3), semilla=i * 10 + j)
            pasos.append((px, h, pz))
    # el coloso de tierra, detras, saliendo del suelo
    for j in range(30):
        mallas += ta.roca_cubica(r.uniform(10, 56), r.uniform(8, 44), r.uniform(62, 78), r.uniform(0.8, 2.2), semilla=600 + j)
    ta.dibujar(lz, cam, mallas, LUCES_SELVA, AMB_SELVA, niebla)
    coloso = dict(tm.GARRA)
    coloso.update({'cabeza': {'rot': (-26, 6, 0)}, 'mandibula': {'rot': (28, 0, 0)}, 'cuello': {'rot': (-10, 6, 0)},
                   'cuerpo': {'rot': (-16, 0, 0), 'pos': (0, -4, 6)}})
    rajang(lz, cam, 34.0, 84.0, 40, coloso, 5, niebla, y=-21.0, escala=5.4, brillo=1.3)
    # jugadores: uno arriba rompiendo un totem, uno saltando, otro en una piedra, otro corriendo
    x1, z1, h1 = tot[1][0], tot[1][1], tot[1][2]
    jugador(lz, cam, x1 + 1.3, z1 - 0.9, 130, y=h1, niebla=niebla)
    p2 = pasos[7]
    jugador(lz, cam, p2[0] + 0.3, p2[2] - 0.6, 40, y=p2[1] + 1.1, niebla=niebla)
    p3 = pasos[11]
    jugador(lz, cam, p3[0], p3[2], 200, y=p3[1], niebla=niebla)
    jugador(lz, cam, 6.0, -1.0, 120, niebla=niebla)
    rajang(lz, cam, cx, cz, 10, tm.RUGIDO, 2, niebla)
    # lo que brilla: el circulo, los haces de los totems vivos hacia el, los aros bajo las piedras
    ta.calco(lz, cam, cx, cz, d / 0.72, ta.sello(0.3), 1.0, giro=180)
    for (x, z, alto, est, a) in tot:
        if est == 'on':
            ta.cinta(lz, cam, (x, alto + 4.6, z), (cx, 6.5, cz), 0.45, LINEA, 1.2)
            ta.cartel(lz, cam, (x, alto + 4.7, z), 1.4, ta.HALO, 1.1)
            ta.cinta(lz, cam, (x, alto + 4.6, z), (x, alto + 22, z), 1.3, ta.HAZ, 0.9)
    for (px, h, pz) in pasos:
        ta.calco(lz, cam, px, pz, 1.0, ARO_PIEDRA, 0.8, y=h - 0.75)
    ta.cartel(lz, cam, (32.0, 30.0, 76.0), 22.0, ta.HALO_SUAVE, 0.3)
    img = componer(lz, W, H, horizonte(cam), 10, oscuro=0.3)
    ta.polvo_en(img, cam, [(32.0, 0.5, 70.0, 16.0), (12, 0.5, 70, 10), (50, 0.5, 70, 10)], SS, (110, 96, 70), 11, 1.5)
    img.convert('RGB').save(os.path.join(OUT, 'sello.jpg'), quality=90)


# ----------------------------------------------------------------------
#  7. Cataclismo de Jade: alzado, ruge al cielo; el cielo se raja y llueven
#     fragmentos sobre sus marcas. Donde ya cayeron, crateres.
# ----------------------------------------------------------------------
def grieta_cielo(fondo, semilla=4):
    """La grieta verde que se abre en el cielo, con el remolino de nubes."""
    H, W = fondo.shape[:2]
    r = random.Random(semilla)
    cx, cy = W * 0.5, H * 0.1
    yy, xx = np.mgrid[0:H, 0:W]
    dx, dy = (xx - cx) / W, (yy - cy) / H * 0.6
    d = np.hypot(dx, dy)
    ang = np.arctan2(dy, dx)
    remolino = 0.5 + 0.5 * np.sin(ang * 3 + d * 28)
    k = np.clip(1 - d / 0.5, 0, 1) ** 1.5
    fondo = fondo * (1 - 0.35 * k[..., None]) + np.array([0.12, 0.32, 0.16]) * (k * remolino * 0.5)[..., None]
    capa = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(capa)
    for rama in range(5):
        x, y = cx, cy
        a = math.pi * r.uniform(0.15, 0.85)
        for s in range(9):
            a += r.uniform(-0.45, 0.45)
            l = W * r.uniform(0.02, 0.05) * (1 - s / 12)
            x1, y1 = x + math.cos(a) * l * (1 if rama % 2 else -1), y + math.sin(a) * l * 0.4
            dr.line((x, y, x1, y1), fill=255, width=max(1, int(W / 300 * (1 - s / 10) * 3)))
            x, y = x1, y1
    g = np.array(capa).astype(float) / 255
    halo = np.array(capa.filter(ImageFilter.GaussianBlur(W / 90))).astype(float) / 255
    emis = g[..., None] * np.array([0.8, 1.0, 0.7]) + halo[..., None] * np.array([0.3, 0.9, 0.35]) * 1.4
    return np.clip(fondo, 0, 1), np.clip(emis, 0, 1)


def cataclismo(W=1600, H=900):
    cam = vr.Camara(ojo=(-18.0, 3.0, -26.0), objetivo=(0.0, 8.0, 2.0), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = NieblaSelva(22, 55)
    niebla.color = (0.1, 0.18, 0.12)
    luces = [((-0.3, 1.0, -0.3), (0.6, 1.0, 0.5), 0.8, 'llave'), ((0.7, 0.3, 0.7), (0.6, 1.0, 0.4), 1.2, 'contra'),
             ((-0.8, 0.2, -0.5), (0.5, 0.7, 0.5), 0.5, 'llave')]
    amb = (0.14, 0.2, 0.14)
    escena = plaza() + piramide(4, 34)
    dibujar_mundo(lz, cam, escena, niebla, 4, luces, amb)
    r = random.Random(21)
    caen, crateres = [], []
    for _ in range(80):
        a = r.uniform(0, math.tau)
        d = r.uniform(5, 21)
        x, z = math.cos(a) * d, 5 + math.sin(a) * d
        if any(math.hypot(x - q[0], z - q[1]) < 4.2 for q in caen + crateres):
            continue
        if len(crateres) < 3 and r.random() < 0.3:
            crateres.append((x, z, r.uniform(1.6, 2.3)))
        elif len(caen) < 12:
            caen.append((x, z, r.uniform(7, 30), r.uniform(0.6, 1.2)))
    direccion = (0.22, -1.0, -0.18)
    mallas, polvos = [], []
    for k, (x, z, rad) in enumerate(crateres):
        ta.calco(lz, cam, x, z, rad, ta.CRATER, giro=r.uniform(0, 90), y=0.035, opaco=True, luz=np.array([0.6, 0.65, 0.6]))
        for j in range(9):
            a = math.tau * j / 9 + r.uniform(-0.2, 0.2)
            mallas += ta.losa(x + math.cos(a) * rad * 1.05, z + math.sin(a) * rad * 1.05, r.uniform(0.4, 0.7), r.uniform(30, 60),
                              -math.degrees(a) + 90, 0.0, 0.3, semilla=1100 + k * 20 + j, mat='plaza_losa')
        mallas += ta.cristal(x + 0.2, 0.6, z, 0.75, 'fragmento', (0.25, 1.0, 0.15), 1.7, 6, semilla=k)
        for j in range(4):
            a = r.uniform(0, math.tau)
            mallas += ta.cristal(x + math.cos(a) * rad * 0.6, 0.15, z + math.sin(a) * rad * 0.6, 0.28, 'fragmento',
                                 (math.cos(a), 1.2, math.sin(a)), 1.4, 5, semilla=k * 7 + j)
        polvos.append((x, 0.5, z, 2.8))
    ta.dibujar(lz, cam, mallas, luces, amb, niebla, brillo=1.4)
    for k, (x, z, y, t) in enumerate(caen):
        ta.fragmento_cayendo(lz, cam, (x, y, z), direccion, t, luces, amb, semilla=k, parte='malla')
    for (x, z, g) in ((-7.0, -8.0, 200), (4.0, -11.0, 170)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    rajang(lz, cam, -1.0, 5.0, -35, tm.ALZADO, 4, niebla, luces=luces, amb=amb)
    # lo que brilla
    for k, (x, z, rad) in enumerate(crateres):
        ta.calco(lz, cam, x, z, rad * 2.6, ta.ONDA, 0.9)
        ta.cartel(lz, cam, (x + 0.2, 1.4, z), 1.6, ta.HALO, 0.8)
    for k, (x, z, y, t) in enumerate(caen):
        cuenta = float(np.clip(1 - y / 32, 0.05, 0.95))
        ta.calco(lz, cam, x, z, 1.3 + t, ta.marca_cataclismo(round(cuenta * 20) / 20), 1.3, giro=r.uniform(0, 90))
        ta.fragmento_cayendo(lz, cam, (x, y, z), direccion, t, luces, amb, semilla=k, largo_estela=7.0, parte='brillo')
    img = componer(lz, W, H, horizonte(cam), 12, oscuro=0.75, cielo_extra=grieta_cielo)
    ta.polvo_en(img, cam, polvos, SS, (80, 120, 80), 13)
    img.convert('RGB').save(os.path.join(OUT, 'cataclismo.jpg'), quality=90)


# ----------------------------------------------------------------------
#  8. Escala: el jugador, el Vigia, Nerea, Aeralis y Rajang
# ----------------------------------------------------------------------
def escala(W=2000, H=640):
    cam = vr.Camara(ojo=(12.0, 8.6, -260), objetivo=(12.0, 8.6, 0), fov=6.6, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    luces = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]
    amb = (0.32, 0.34, 0.38)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-22.5, 0, -20)), luces, amb)
    vt = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia.png'))
    vb = vr.cargar(os.path.join(TEX, 'entity/vigia/vigia_ojo.png'))
    vr.dibujar_quads(lz, cam, vr.quads_del_modelo({}, modelo_a_mundo=vr.entidad_a_mundo(-20.0, 0, 0, -20)), vt, emis=vb,
                     luces=luces, ambiente=amb, brillo=1.2)
    nm.dibujar(lz, cam, nm.quads(nm.esqueleto(), ne.REPOSO, nm.entidad_a_mundo(-15.0, 0, 0, -20, 1.57)), luces, amb, brillo=1.2)
    heroica_a = {'torax': {'rot': (-16, 0, 0)}, 'cabeza': {'rot': (24, 0, 0)},
                 'ala_sup_izq': {'rot': (0, -10, -34)}, 'ala_sup_der': {'rot': (0, 10, 34)},
                 'ala_inf_izq': {'rot': (0, -20, -22)}, 'ala_inf_der': {'rot': (0, 20, 22)}}
    vm.dibujar(lz, cam, vm.quads(vm.esqueleto(), heroica_a, vm.entidad_a_mundo(1.0, 0, 0, 0)), luces, amb, fase=1, brillo=1.2)
    rajang(lz, cam, 34.0, 0, -90, tm.ACECHO, 1, luces=luces, amb=amb, brillo=1.2)
    col = np.clip(lz.color + lz.emis * 0.5, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.93, 0.95, 0.96]) * (1 - a)
    img = Image.fromarray((arr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).convert('RGBA')
    rej = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rej)
    f = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 18)
    for b in range(0, 19):
        _, y, _ = cam.proyectar((12.0, b, 0))
        y /= SS
        d.line((60, y, W - 20, y), fill=(40, 60, 90, 110 if b else 220), width=2 if b == 0 else 1)
        if b % 2 == 0:
            d.text((18, y - 11), f'{b}', font=f, fill=(40, 60, 90, 255))
    img = Image.alpha_composite(img, rej)
    img.convert('RGB').save(os.path.join(OUT, 'escala.jpg'), quality=92)


ESCENAS = {'heroica': heroica, 'vistas': vistas, 'fases': fases, 'garra': garra, 'terremoto': terremoto,
           'sello': sello, 'cataclismo': cataclismo, 'escala': escala}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for n in pedidas:
        ESCENAS[n]()
        print('ok', n, flush=True)

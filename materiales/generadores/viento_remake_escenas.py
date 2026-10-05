"""
Renders de la ficha del remake de Aeralis: el antes (la malla y las pieles de
antes del remake, vendaval_juego_v1.py) y el despues (vendaval_juego.py, la del
juego), con la misma camara y la misma luz; y las escenas de los ataques nuevos
o rehechos.

Uso: python viento_remake_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne
import viento_modelo as vm
import viento_escenas as ve              # la cima, el cielo, el jugador, los tornados y las cuchillas
import vendaval_juego_v1 as vj           # el antes: la malla de antes del remake
import vendaval_juego_anim as vja        # sus poses
import vendaval_juego as rm              # el despues: la del juego

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/aeralis')
FUENTE = 'C:/Windows/Fonts/'
SS = 2
LUCES = ve.LUCES_CIELO
AMB = ve.AMB_CIELO

# ----------------------------------------------------------------------
#  Las dos Aeralis: su malla, su atlas y como se dibujan
# ----------------------------------------------------------------------
_ATLAS = {}


def atlas(cual, fase):
    """(tex, emis, uv, alto) en float [0, 1] como los quiere el rasterizador."""
    k = (cual, fase)
    if k not in _ATLAS:
        if cual == 'antes':
            uv, alto = vj.empaquetar()
            base, brillo = vj.pintar_atlas(uv, alto, fase)
        else:
            uv, alto = rm.empaquetar()
            base, brillo = rm.pintar_atlas(uv, alto, fase)
        _ATLAS[k] = (base, brillo, uv, alto)
    return _ATLAS[k]


def modulo(cual):
    return vj if cual == 'antes' else rm


def pose_vuelo_antes(s=0.25):
    return vja.pose_en('VUELO', s)


def aeralis(lz, cam, cual, x, y, z, guinada, pose=None, fase=1, niebla=None, luces=None, amb=None, brillo=1.5,
            escala=1.0):
    """Dibuja una Aeralis con su origen (los 'pies' de la entidad) en (x, y, z)."""
    mod = modulo(cual)
    base, emis, uv, alto = atlas(cual, fase)
    if pose is None:
        pose = pose_vuelo_antes() if cual == 'antes' else rm.HEROICA
    luces = LUCES if luces is None else luces
    amb = AMB if amb is None else amb
    M = vr.T(0, y, 0) @ vr.entidad_a_mundo(x, 0, z, guinada, escala)
    qs = mod.quads(pose, uv, alto, M)
    planos = set(mod.PLANOS) | {mod.NUCLEO}
    for Pq, UV, _, mat in [q for q in qs if q[3] not in planos]:
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), luces, amb) * brillo / 1.5
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UV[k] for k in tri], base, luz, emis, niebla)
    for Pq, UV, _, mat in [q for q in qs if q[3] == mod.NUCLEO]:
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UV[k] for k in tri], base, np.ones(3), emis, niebla)
    trans = sorted([q for q in qs if q[3] in mod.PLANOS], key=lambda q: -cam.proyectar(np.mean(q[0], axis=0))[2])
    for Pq, UV, _, mat in trans:
        luz = 0.55 + 0.6 * vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), luces, amb)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UV[k] for k in tri], base, luz, emis, niebla, translucido=1.0)


def fondo_liso(lz, W, H, color=(0.93, 0.95, 0.96), emis=0.5):
    col = np.clip(lz.color + lz.emis * emis, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array(color) * (1 - a)
    return Image.fromarray((arr * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)


def rotulo(img, texto, x, y, tam=30, color=(16, 32, 58), fuente='Oswald-Bold.ttf'):
    d = ImageDraw.Draw(img)
    d.text((x, y), texto, font=ImageFont.truetype(FUENTE + fuente, tam), fill=color)


# ----------------------------------------------------------------------
#  Prueba rapida: las dos de frente
# ----------------------------------------------------------------------
def prueba(W=1600, H=700, fase=1):
    img = Image.new('RGB', (W, H), (237, 242, 245))
    for i, cual in enumerate(('antes', 'despues')):
        w = W // 2
        cam = vr.Camara(ojo=(0, 12.0, -70), objetivo=(0, 12.0, 0), fov=36, ancho=w * SS, alto=H * SS)
        lz = vr.Lienzo(w * SS, H * SS)
        aeralis(lz, cam, cual, 0, Y_VUELO if cual == 'antes' else Y_VUELO_NUEVA, 0, 0, fase=fase, luces=[((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'),
                                                               ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')],
                amb=(0.34, 0.36, 0.4), brillo=1.3)
        img.paste(fondo_liso(lz, w, H), (i * w, 0))
        rotulo(img, cual.upper(), i * w + 20, 14)
    img.save(os.path.join(OUT, f'prueba_f{fase}.jpg'), quality=90)


# ----------------------------------------------------------------------
#  Texturas de los efectos (RGBA uint8; las pinta el rasterizador)
# ----------------------------------------------------------------------
def tex_cuchilla(color, w=96, h=28, semilla=1):
    """Una media luna de viento: el filo casi blanco, el cuerpo del color y
    hebras que se deshacen hacia atras."""
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    col = np.array(color, float)
    for y in range(h):
        for x in range(w):
            u, v = x / (w - 1), y / (h - 1)
            grueso = max(0.05, math.sin(math.pi * u) ** 0.7)
            d = abs(v - 0.5) / (0.5 * grueso)
            if d > 1:
                continue
            if d < 0.22:
                c, a = np.array((250, 253, 255.0)), 255
            else:
                k = (d - 0.22) / 0.78
                c, a = col * (1 - 0.3 * k) + 30 * (1 - k), 235 * (1 - k ** 1.6)
            if r.random() < 0.08:
                a *= 0.5
            t[y, x] = (*np.clip(c, 0, 255).astype(int), int(a))
    return t


def tex_viento2(color, semilla, w=32, h=64, densidad=0.45):
    """Bandas de viento para los embudos, en el color de la fase."""
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    col = np.array(color, float)
    for y in range(h):
        for x in range(w):
            q = (x + y // 3 + r.randint(0, 2)) % 7
            if q < 2:
                t[y, x] = (*np.clip(col * 0.35 + 170, 0, 255).astype(int), r.randint(150, 220))
            elif q < 4 and r.random() < densidad:
                t[y, x] = (*np.clip(col, 0, 255).astype(int), r.randint(90, 150))
            elif r.random() < 0.25:
                t[y, x] = (*np.clip(col * 0.6, 0, 255).astype(int), r.randint(40, 90))
    return t


def tex_aro(color, n=128, grueso=0.06, marcas=24, relleno=0):
    """Un aro en el suelo, con muescas y, si se pide, un relleno tenue."""
    t = np.zeros((n, n, 4), np.uint8)
    y, x = np.mgrid[0:n, 0:n] + 0.5
    d = np.hypot(x - n / 2, y - n / 2) / (n / 2)
    a = np.arctan2(y - n / 2, x - n / 2)
    col = np.array(color)
    t[(d > 1 - grueso) & (d < 1)] = (*col, 235)
    m = (d > 0.84) & (d < 0.9) & (((a + math.pi) / (2 * math.pi) * marcas) % 1 < 0.45)
    t[m] = (*col, 200)
    if relleno:
        t[d < 0.84] = (*col, relleno)
    return t


def tex_chevrones(color, w=32, h=32):
    """Un galon de viento para la linea del Picado (se repite a lo largo)."""
    t = np.zeros((h, w, 4), np.uint8)
    col = np.array(color)
    for y in range(h):
        for x in range(w):
            u, v = x / (w - 1), y / (h - 1)
            cen = abs(u - 0.5)
            if abs(v - (0.25 + cen * 0.9)) < 0.11:
                t[y, x] = (*np.minimum(255, col + 60), 245)
            elif u < 0.06 or u > 0.94:
                t[y, x] = (*col, 200)
            else:
                t[y, x] = (*(col * 0.5).astype(int), 70)
    return t


def tex_polilla(color, n=24):
    """Una polilla de viento (la rafaga de la Caceria): cuatro alas de luz."""
    t = np.zeros((n, n, 4), np.uint8)
    col = np.array(color)
    c = (n - 1) / 2
    for y in range(n):
        for x in range(n):
            dx, dy = (x - c) / c, (y - c) / c
            ea = ((abs(dx) - 0.48) / 0.48) ** 2 + ((dy + 0.25) / 0.38) ** 2
            eb = ((abs(dx) - 0.32) / 0.32) ** 2 + ((dy - 0.35) / 0.32) ** 2
            if abs(dx) < 0.08 and abs(dy) < 0.6:
                t[y, x] = (250, 252, 255, 255)
            elif ea < 1 or eb < 1:
                borde = 0.6 < ea < 1
                t[y, x] = (*(np.minimum(255, col + 70) if borde else col), 235 if borde else 170)
    return t


def tex_plano(color, alfa=255):
    t = np.zeros((4, 4, 4), np.uint8)
    t[...] = (*color, alfa)
    return t


def tex_cristal(color, n=32):
    t = np.zeros((n, n, 4), np.uint8)
    col = np.array(color, float)
    for y in range(n):
        for x in range(n):
            k = 1 - abs(y - n / 2) / (n / 2)
            c = col * (0.55 + 0.45 * k) + 120 * k ** 3
            t[y, x] = (*np.clip(c, 0, 255).astype(int), 225)
    return t


def cinta3d(pts, ancho, cam):
    """Una tira que sigue una polilinea, de cara a la camara (rayos, ataduras, estelas)."""
    out = []
    for i in range(len(pts) - 1):
        a, b = np.array(pts[i], float), np.array(pts[i + 1], float)
        v = cam.ojo - (a + b) / 2
        lado = np.cross(b - a, v)
        lado = lado / (np.linalg.norm(lado) + 1e-9) * ancho
        u0, u1 = i / (len(pts) - 1), (i + 1) / (len(pts) - 1)
        out.append(([a - lado, b - lado, b + lado, a + lado], [(u0, 1), (u1, 1), (u1, 0), (u0, 0)]))
    return out


def rayo(p0, p1, semilla, pasos=9, sacude=0.7):
    r = random.Random(semilla)
    p0, p1 = np.array(p0, float), np.array(p1, float)
    pts = [p0]
    for k in range(1, pasos):
        q = p0 + (p1 - p0) * k / pasos
        pts.append(q + np.array([r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 1)]) * sacude)
    pts.append(p1)
    return pts


def cuadrado_suelo(cx, cz, R, y=0.06, giro=0.0):
    c, s_ = math.cos(giro) * R, math.sin(giro) * R
    P = [(cx - c + s_, y, cz - s_ - c), (cx + c + s_, y, cz + s_ - c), (cx + c - s_, y, cz + s_ + c), (cx - c - s_, y, cz - s_ + c)]
    return [(P, [(0, 0), (1, 0), (1, 1), (0, 1)])]


def billboard(p, tam, cam, giro=0.0):
    p = np.array(p, float)
    c, s_ = math.cos(giro), math.sin(giro)
    rr, uu = cam.r * c + cam.u * s_, -cam.r * s_ + cam.u * c
    P = [p - rr * tam - uu * tam, p + rr * tam - uu * tam, p + rr * tam + uu * tam, p - rr * tam + uu * tam]
    return ([tuple(q) for q in P], [(0, 1), (1, 1), (1, 0), (0, 0)])


def octaedro(c, R, alto):
    """El cristal de un nucleo del Juicio: ocho caras."""
    cx, cy, cz = c
    arr, ab = (cx, cy + alto, cz), (cx, cy - alto, cz)
    anillo = [(cx + R * math.cos(k * math.pi / 2 + 0.4), cy, cz + R * math.sin(k * math.pi / 2 + 0.4)) for k in range(4)]
    out = []
    for k in range(4):
        a, b = anillo[k], anillo[(k + 1) % 4]
        out.append(([a, b, arr, arr], [(0, 1), (1, 1), (0.5, 0), (0.5, 0)]))
        out.append(([b, a, ab, ab], [(0, 0), (1, 0), (0.5, 1), (0.5, 1)]))
    return out


# ----------------------------------------------------------------------
#  La cima (de viento_escenas) y el montaje de una escena
# ----------------------------------------------------------------------
def cima(lz, cam, niebla, columnas=True, jugadores=()):
    ve.suelo(lz, cam, niebla=niebla)
    if columnas:
        for i, (x, z, alto, rota) in enumerate(((-13, 10, 5, True), (12, 12, 7, True), (-17, -2, 3, True), (18, 2, 4, False))):
            nm.dibujar(lz, cam, ve.columna(x, z, alto, rota, i), LUCES, AMB, niebla)
    for j in jugadores:
        ve.jugador(lz, cam, *j[:3], y=j[3] if len(j) > 3 else 0.0, niebla=niebla)


def acabar(lz, cam, W, H, nombre, semilla, fase=1, rayos=0.4, estelas=50):
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 300, 0.0, cam.ojo[2] + cam.f[2] * 300]))[1] / SS
    img = ve.componer(lz, W, H, horiz, semilla, fase, rayos=rayos, n_estelas=estelas)
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)


Y_VUELO = 2.5          # el origen de la entidad sobre el suelo, volando (la de hoy)
Y_VUELO_NUEVA = 7.0    # la nueva vuela 4,5 bloques mas alto: sus colas son mas largas
BLANCO = (236, 232, 255)


def luz_fase(P):
    return vm._hex(P['brillo_c'])


# ----------------------------------------------------------------------
#  1. Heroica: la misma camara, antes y despues
# ----------------------------------------------------------------------
def heroica(cual, W=1600, H=900, fase=1):
    cam = vr.Camara(ojo=(-12.0, 1.0, -34.0), objetivo=(1.0, 11.0, 0), fov=54, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(18, 46)
    cima(lz, cam, niebla, jugadores=((-4.5, -6.0, 210), (2.6, -5.5, 160), (-1.5, -8.5, 190), (6.5, -2.0, 120),
                                     (-7.5, -3.0, 240)))
    aeralis(lz, cam, cual, 0, Y_VUELO if cual == 'antes' else Y_VUELO_NUEVA, 2, 24, fase=fase, niebla=niebla)
    tv = ve.TEX_VIENTO if cual == 'antes' else tex_viento2(rm.paleta(fase)['halo'], 3)
    ve.dibujar_translucido(lz, cam, ve.tornado(-10.0, 5.0, 6.5, 0.3, 2.6, 0.4), tv, 0.8, niebla, 0.25)
    ve.dibujar_translucido(lz, cam, ve.tornado(10.5, 7.0, 7.5, 0.3, 2.9, 2.0), tv, 0.8, niebla, 0.25)
    acabar(lz, cam, W, H, f'heroica_{cual}' + ('' if fase == 1 else f'_f{fase}'), 3, fase, rayos=0.6, estelas=46)


# ----------------------------------------------------------------------
#  2. Vistas: frente, perfil y espalda
# ----------------------------------------------------------------------
LUZ_ESTUDIO = [((-0.4, 0.8, -0.8), (1, 1, 1), 0.85, 'llave'), ((0.6, 0.3, 0.8), (0.6, 0.8, 1), 0.5, 'contra')]


def vistas(cual, W=1800, H=640):
    img = Image.new('RGB', (W, H), (237, 242, 245))
    w = W // 3
    for i, g in enumerate((0, -90, 180)):
        cam = vr.Camara(ojo=(0, 12.0, -95), objetivo=(0, 12.0, 0), fov=28, ancho=w * SS, alto=H * SS)
        lz = vr.Lienzo(w * SS, H * SS)
        pose = pose_vuelo_antes() if cual == 'antes' else rm.HEROICA
        aeralis(lz, cam, cual, 0, 1.5 if cual == 'antes' else 0.0, 0, g, pose=pose, luces=LUZ_ESTUDIO, amb=(0.34, 0.36, 0.4), brillo=1.3)
        img.paste(fondo_liso(lz, w, H), (i * w, 0))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 20)
    for i, t in enumerate(('FRENTE', 'PERFIL', 'ESPALDA')):
        d.text((i * w + 16, 12), t, font=f, fill=(40, 60, 90))
    img.save(os.path.join(OUT, f'vistas_{cual}.jpg'), quality=92)


# ----------------------------------------------------------------------
#  3. Las cuatro fases, de frente
# ----------------------------------------------------------------------
def fases(cual, W=1600, H=560):
    img = Image.new('RGB', (W, H))
    w = W // 4
    for f in (1, 2, 3, 4):
        cam = vr.Camara(ojo=(0, 12.0, -86), objetivo=(0, 12.0, 0), fov=31, ancho=w * SS, alto=H * SS)
        lz = vr.Lienzo(w * SS, H * SS)
        pose = pose_vuelo_antes() if cual == 'antes' else rm.HEROICA
        aeralis(lz, cam, cual, 0, 1.5 if cual == 'antes' else 0.0, 0, 0, pose=pose, fase=f)
        fondo = ve.cielo(w, H, H * 0.95, 10 + f, rayos=[0, 0.2, 0.6, 1.0][f - 1])
        a = np.array(Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((w, H), Image.LANCZOS)).astype(float)[..., None] / 255
        col = np.array(Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((w, H), Image.LANCZOS)).astype(float) / 255
        em = np.array(Image.fromarray((np.clip(lz.emis, 0, 1) * 255).astype(np.uint8)).resize((w, H), Image.LANCZOS)).astype(float) / 255
        arr = ne.bloom(col * a + fondo * (1 - a), em, radios=((3, 0.8), (10, 0.6), (30, 0.4)))
        img.paste(Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)), ((f - 1) * w, 0))
    d = ImageDraw.Draw(img)
    fn = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 26)
    for f, t in zip((1, 2, 3, 4), ('I  BRISA', 'II  RÁFAGA', 'III  TEMPESTAD', 'IV  OJO DE LA TORMENTA')):
        d.text(((f - 1) * w + 14, H - 42), t, font=fn, fill=(236, 242, 255))
    img.save(os.path.join(OUT, f'fases_{cual}.jpg'), quality=92)


# ----------------------------------------------------------------------
#  4. Escala: un jugador, la de hoy y la nueva
# ----------------------------------------------------------------------
def escala(W=1600, H=760):
    cam = vr.Camara(ojo=(-2.0, 12.0, -175), objetivo=(-2.0, 12.0, 0), fov=12.0, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    amb = (0.34, 0.36, 0.4)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-4.0, 0, -20)), LUZ_ESTUDIO, amb)
    aeralis(lz, cam, 'antes', -20.0, Y_VUELO, 0, 0, luces=LUZ_ESTUDIO, amb=amb, brillo=1.3)
    aeralis(lz, cam, 'despues', 14.0, Y_VUELO_NUEVA, 0, 0, luces=LUZ_ESTUDIO, amb=amb, brillo=1.3)
    img = fondo_liso(lz, W, H).convert('RGBA')
    rej = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rej)
    f = ImageFont.truetype(FUENTE + 'Montserrat-SemiBold.ttf', 18)
    for b in range(0, 29, 2):
        _, y, _ = cam.proyectar((0, b, 0)); y /= SS
        d.line((48, y, W - 16, y), fill=(40, 60, 90, 110 if b else 220), width=2 if b == 0 else 1)
        if b % 4 == 0:
            d.text((10, y - 11), f'{b}', font=f, fill=(40, 60, 90, 255))
    img = Image.alpha_composite(img, rej)
    d = ImageDraw.Draw(img)
    fn = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 30)
    for texto, x in (('HOY · 22 DE ENVERGADURA', -20.0), ('REMAKE · 35', 14.0)):
        px_, _, _ = cam.proyectar((x, 0, 0))
        d.text((px_ / SS - 130, H - 50), texto, font=fn, fill=(16, 40, 70, 255))
    img.convert('RGB').save(os.path.join(OUT, 'escala.jpg'), quality=92)


# ----------------------------------------------------------------------
#  5. Ataques (despues)
# ----------------------------------------------------------------------
def aleteo(W=1600, H=900, fase=1):
    """Medias lunas: las bajas en el color de la fase (saltar), las altas blancas
    (apartarse). El abanico se marca en el suelo antes de que salgan."""
    P = rm.paleta(fase)
    cam = vr.Camara(ojo=(-16.0, 7.5, -19.0), objetivo=(0.8, 4.4, 1.0), fov=58, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(18, 42)
    cima(lz, cam, niebla, jugadores=((-5.5, -9.5, 200), (-1.0, -11.0, 180, 1.4), (4.5, -9.0, 160), (8.0, -5.0, 130)))
    aeralis(lz, cam, 'despues', 0, Y_VUELO_NUEVA, 7, 10, pose=rm.ALETEO, fase=fase, niebla=niebla)
    baja, alta = tex_cuchilla(P['borde']), tex_cuchilla(BLANCO, semilla=2)
    suelo = []
    for k in range(-3, 4):
        a = -math.pi / 2 + k * 0.17
        suelo += cinta3d([(math.cos(a) * 3, 0.07, 7 + math.sin(a) * 3), (math.cos(a) * 20, 0.07, 7 + math.sin(a) * 20)], 0.08, cam)
    ve.dibujar_translucido(lz, cam, suelo, tex_plano(P['borde'], 120), 0.6, niebla, 0.3)
    for k, rad in enumerate((6.0, 10.5, 15.0)):
        bajo = k % 2 == 0
        y0, y1 = (0.15, 1.7) if bajo else (1.9, 3.4)
        for paso, al in ((0.0, 0.92), (-0.7, 0.45), (-1.4, 0.22)):
            q = ve.cuchilla(0, 7, rad + paso, -math.pi / 2 + (k - 1) * 0.18, abre=1.1, y0=y0, y1=y1, segs=14)
            ve.dibujar_translucido(lz, cam, q, baja if bajo else alta, al, niebla, 0.5 if paso == 0 else 0.15)
    acabar(lz, cam, W, H, 'ataque_aleteo', 7, fase, rayos=0.3, estelas=70)


def tornados(W=1600, H=900, fase=3):
    """Embudos de dos capas en el color de la fase, con escombros, el aro en el
    suelo hasta donde atrapan y tres anillos (los tres golpes que lo deshacen)."""
    P = rm.paleta(fase)
    cam = vr.Camara(ojo=(-14.0, 6.5, -24.0), objetivo=(1.0, 6.0, 4.0), fov=56, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(20, 46)
    cima(lz, cam, niebla, jugadores=((-3.0, -9.0, 200), (5.0, -6.5, 150), (-8.5, -3.0, 240), (1.5, 1.5, 30, 3.2)))
    aeralis(lz, cam, 'despues', 2, Y_VUELO_NUEVA + 2, 14, 0, pose=rm.HEROICA, fase=fase, niebla=niebla)
    for i, (x, z, alto, giro) in enumerate(((-7.0, -1.0, 8.0, 0.3), (1.5, 1.5, 9.0, 1.4), (9.0, 2.0, 7.5, 2.6))):
        ve.dibujar_translucido(lz, cam, cuadrado_suelo(x, z, 3.4), tex_aro(P['borde']), 0.85, niebla, 0.5)
        ve.dibujar_translucido(lz, cam, ve.tornado(x, z, alto, 0.25, 1.6, giro, anillos=16, segs=12),
                               tex_viento2(P['tormenta'], 5 + i, densidad=0.9), 0.75, niebla, 0.0)
        ve.dibujar_translucido(lz, cam, ve.tornado(x, z, alto * 1.04, 0.45, 2.7, giro + 1.0, anillos=18, segs=16),
                               tex_viento2(P['halo'], 9 + i), 0.8, niebla, 0.3)
        for hh in (0.3, 0.55, 0.8):
            rr = 0.45 + (2.7 - 0.45) * hh ** 1.5 + 0.25
            aro = [(x + rr * math.cos(a), alto * hh, z + rr * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 25)]
            ve.dibujar_translucido(lz, cam, cinta3d(aro, 0.07, cam), tex_plano(luz_fase(P)), 1.0, niebla, 0.9)
        r = random.Random(i)
        esc = []
        for _ in range(14):
            a, hh = r.uniform(0, 6.3), r.uniform(0.1, 0.9)
            rr = 0.45 + (2.7 - 0.45) * hh ** 1.5
            esc.append(billboard((x + rr * math.cos(a), alto * hh, z + rr * math.sin(a)), r.uniform(0.08, 0.16), cam, r.uniform(0, 3)))
        ve.dibujar_translucido(lz, cam, esc, tex_plano((70, 66, 74)), 1.0, niebla, 0.0)
        if P['rayos'] > 0:
            for k in range(2):
                pts = rayo((x, alto * 0.95, z), (x + r.uniform(-1, 1), alto * 0.2, z + r.uniform(-1, 1)), 30 + i * 5 + k, 7, 0.5)
                ve.dibujar_translucido(lz, cam, cinta3d(pts, 0.05, cam), tex_plano(luz_fase(P)), 1.0, None, 1.5)
    acabar(lz, cam, W, H, 'ataque_tornados', 9, fase, rayos=0.7, estelas=60)


def caceria(W=1600, H=900, fase=2):
    """La marca: una espiral bajo la presa y un ojo encima, con un hilo de viento
    hasta ella. Las rafagas son polillas de viento que la persiguen."""
    P = rm.paleta(fase)
    cam = vr.Camara(ojo=(-16.0, 6.0, -24.0), objetivo=(3.0, 8.0, 6.0), fov=62, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(22, 50)
    presa = (8.0, -4.0)
    cima(lz, cam, niebla, jugadores=((presa[0], presa[1], 250), (-4.0, -8.0, 200), (0.5, -10.0, 170)))
    aeralis(lz, cam, 'despues', -2, Y_VUELO_NUEVA, 20, -40, pose=rm.ALETEO, fase=fase, niebla=niebla)
    ve.dibujar_translucido(lz, cam, cuadrado_suelo(presa[0], presa[1], 2.4), ve._tex_circulo(fase=fase), 0.9, None, 1.0)
    ojo = billboard((presa[0], 3.6, presa[1]), 0.55, cam)
    ve.dibujar_translucido(lz, cam, [ojo], tex_aro(luz_fase(P), 48, 0.18, 8, 90), 1.0, None, 1.2)
    hilo = rayo((-1.5, 14.5, 18.0), (presa[0], 3.6, presa[1]), 3, 14, 0.25)
    ve.dibujar_translucido(lz, cam, cinta3d(hilo, 0.04, cam), tex_plano(P['borde']), 0.8, niebla, 0.8)
    pol = tex_polilla(P['borde'])
    r = random.Random(4)
    for k in range(7):
        t = (k + 1) / 8
        cx = -1.5 + (presa[0] + 1.5) * t + r.uniform(-1.5, 1.5)
        cy = 14.0 + (2.0 - 14.0) * t + r.uniform(-1.0, 1.0)
        cz = 18.0 + (presa[1] - 18.0) * t + r.uniform(-2.0, 2.0)
        estela = [(cx - 1.6 * (presa[0] + 1.5) / 24 * q, cy + 0.9 * q, cz - 1.6 * (presa[1] - 18) / 24 * q) for q in np.linspace(0, 1, 6)]
        ve.dibujar_translucido(lz, cam, cinta3d(estela, 0.16, cam), tex_cuchilla(P['borde'], 48, 12, k), 0.55, niebla, 0.3)
        ve.dibujar_translucido(lz, cam, [billboard((cx, cy, cz), 0.8, cam, r.uniform(-0.4, 0.4))], pol, 1.0, niebla, 0.9)
    acabar(lz, cam, W, H, 'ataque_caceria', 13, fase, rayos=0.4, estelas=50)


def juicio(W=1600, H=900, fase=4):
    """El ciclon oscuro con rayos; los cuatro nucleos son cristales de tormenta
    atados a ella con un rayo cada uno (se corta al romperlo)."""
    P = rm.paleta(fase)
    cam = vr.Camara(ojo=(-18.0, 12.0, -32.0), objetivo=(0.5, 10.5, 2.0), fov=62, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(22, 50)
    cima(lz, cam, niebla, columnas=False, jugadores=((-6, -4, 30), (5, -5, -40), (-4, 6, 160), (6, 5, 200), (1.5, -8, 0),
                                                       (0.5, 0.5, 20, 4.5)))
    ve.dibujar_translucido(lz, cam, cuadrado_suelo(0.5, 0.5, 13.0), ve._tex_circulo(fase=fase), 0.85, None, 1.0)
    pecho = (0.5, 21.5, 3.0)
    aeralis(lz, cam, 'despues', 0.5, 13.0, 3.0, 20, pose=rm.JUICIO, fase=fase, niebla=niebla)
    cris = tex_cristal(P['borde'])
    for i, (x, z) in enumerate(((-11, -9), (11, -9), (-11, 11), (11, 11))):
        raiz = nm.nodo('ped', (0, 0, 0), (0, 45, 0), [((-12, -16, -12, 24, 16, 24), 'roca_osc'), ((-9, -22, -9, 18, 6, 18), 'roca')])
        nm.dibujar(lz, cam, nm.quads(raiz, {}, vr.T(x, 0, z) @ np.diag([1 / 16, -1 / 16, 1 / 16, 1])), LUCES, AMB, niebla)
        ve.dibujar_translucido(lz, cam, octaedro((x, 3.4, z), 1.0, 1.8), cris, 1.0, niebla, 1.0)
        pts = rayo((x, 4.6, z), pecho, 50 + i, 10, 0.6)
        ve.dibujar_translucido(lz, cam, cinta3d(pts, 0.07, cam), tex_plano(luz_fase(P)), 1.0, None, 1.6)
    ve.dibujar_translucido(lz, cam, ve.tornado(0.5, 0.5, 14.0, 1.6, 6.5, 1.0, anillos=24, segs=18),
                           tex_viento2(P['tormenta'], 21, densidad=1.0), 0.8, niebla, 0.0)
    ve.dibujar_translucido(lz, cam, ve.tornado(0.5, 0.5, 14.5, 2.0, 7.4, 2.0, anillos=24, segs=20),
                           tex_viento2(P['halo'], 22), 0.7, niebla, 0.3)
    for k in range(4):
        r = random.Random(70 + k)
        a = r.uniform(0, 6.3)
        pts = rayo((0.5 + 3 * math.cos(a), 13.5, 0.5 + 3 * math.sin(a)), (0.5 + 4 * math.cos(a + 1), 2.0, 0.5 + 4 * math.sin(a + 1)),
                   80 + k, 9, 0.9)
        ve.dibujar_translucido(lz, cam, cinta3d(pts, 0.06, cam), tex_plano(luz_fase(P)), 1.0, None, 1.4)
    acabar(lz, cam, W, H, 'ataque_juicio', 11, fase, rayos=1.0, estelas=60)


def picado(W=1600, H=900, fase=2):
    """NUEVO. Sube, marca en el suelo una linea de galones hacia su presa y se
    lanza en picado por ella con las alas plegadas."""
    P = rm.paleta(fase)
    cam = vr.Camara(ojo=(-24.0, 7.0, -30.0), objetivo=(2.0, 8.0, 4.0), fov=64, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(20, 50)
    cima(lz, cam, niebla, jugadores=((14.0, 2.0, 270), (8.5, -3.5, 240), (2.0, 5.5, 200), (-4.0, -6.0, 300)))
    gal = tex_chevrones(P['borde'])
    a, b = np.array([-14.0, 10.0]), np.array([20.0, 0.0])
    d = (b - a) / np.linalg.norm(b - a)
    lado = np.array([-d[1], d[0]]) * 2.2
    linea = []
    for k in range(int(np.linalg.norm(b - a) // 2.2)):
        p0, p1 = a + d * k * 2.2, a + d * (k + 1) * 2.2
        Pq = [p0 - lado, p0 + lado, p1 + lado, p1 - lado]
        linea.append(([(q[0], 0.07, q[1]) for q in Pq], [(0, 1), (1, 1), (1, 0), (0, 0)]))
    ve.dibujar_translucido(lz, cam, linea, gal, 0.9, None, 0.8)
    pos = a + d * 2.0
    aeralis(lz, cam, 'despues', pos[0], 12.0, pos[1], math.degrees(math.atan2(d[0], -d[1])) + 180, pose=rm.PICADO,
            fase=fase, niebla=niebla)
    for k in range(3):
        cola = [(pos[0] - d[0] * q * 8 + (k - 1) * 1.6 * -d[1], 18.0 + q * 7, pos[1] - d[1] * q * 8 + (k - 1) * 1.6 * d[0])
                for q in np.linspace(0, 1, 8)]
        ve.dibujar_translucido(lz, cam, cinta3d(cola, 0.35, cam), tex_cuchilla(P['borde'], 64, 16, k), 0.5, niebla, 0.25)
    acabar(lz, cam, W, H, 'nuevo_picado', 17, fase, rayos=0.5, estelas=80)


def posada(W=1600, H=900, fase=2):
    """NUEVO. Al acabar el picado se posa: 3 s en el suelo, jadeando, con dano
    doble. La ventana para la espada."""
    P = rm.paleta(fase)
    cam = vr.Camara(ojo=(-16.0, 5.0, -22.0), objetivo=(2.0, 7.0, 5.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(18, 44)
    cima(lz, cam, niebla, jugadores=((-2.0, -2.0, 220), (5.0, -3.5, 170), (-5.0, 3.0, 260), (8.0, 1.0, 120)))
    ve.dibujar_translucido(lz, cam, cuadrado_suelo(2.0, 5.0, 9.0), tex_aro(P['borde'], 128, 0.03, 32), 0.8, None, 0.6)
    aeralis(lz, cam, 'despues', 2.0, -3.6, 5.0, 200, pose=rm.POSADA, fase=fase, niebla=niebla)
    acabar(lz, cam, W, H, 'nuevo_posada', 19, fase, rayos=0.3, estelas=40)


def escamas(W=1600, H=900, fase=3):
    """NUEVO (fase III). Sacude las alas sobre la cima: cae una nube de escamas
    que brillan y, donde se posan, el suelo se carga y descarga."""
    P = rm.paleta(fase)
    cam = vr.Camara(ojo=(-16.0, 9.0, -24.0), objetivo=(1.0, 7.0, 3.0), fov=60, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(20, 46)
    cima(lz, cam, niebla, jugadores=((-4.0, -7.0, 200), (3.0, -4.0, 160), (7.0, 3.0, 120), (-7.0, 2.0, 240)))
    aeralis(lz, cam, 'despues', 1.0, Y_VUELO_NUEVA + 4, 8.0, 10, pose=rm.ESCAMAS, fase=fase, niebla=niebla)
    r = random.Random(5)
    manchas = []
    for _ in range(9):
        x, z = r.uniform(-12, 14), r.uniform(-9, 12)
        manchas.append((x, z))
        ve.dibujar_translucido(lz, cam, cuadrado_suelo(x, z, 2.4, giro=r.uniform(0, 3)), tex_aro(P['borde'], 64, 0.12, 12, 70), 0.9,
                               None, 0.8)
    for x, z in manchas[:4]:
        pts = rayo((x, 0.1, z), (x + r.uniform(-0.5, 0.5), 2.2, z + r.uniform(-0.5, 0.5)), int(x * 10), 5, 0.4)
        ve.dibujar_translucido(lz, cam, cinta3d(pts, 0.05, cam), tex_plano(luz_fase(P)), 1.0, None, 1.6)
    esc = []
    for _ in range(170):
        x, z, y = r.uniform(-14, 16), r.uniform(-10, 14), r.uniform(0.5, 13)
        esc.append(billboard((x, y, z), r.uniform(0.07, 0.15), cam, r.uniform(0, 3)))
    ve.dibujar_translucido(lz, cam, esc, tex_plano(luz_fase(P)), 1.0, niebla, 1.2)
    acabar(lz, cam, W, H, 'nuevo_escamas', 23, fase, rayos=0.8, estelas=50)


def corriente(W=1600, H=900, fase=2):
    """NUEVO. Un tornado deshecho deja una corriente que sube: quien entra vuela
    hasta su altura y le puede pegar con la espada."""
    P = rm.paleta(fase)
    cam = vr.Camara(ojo=(-14.0, 5.0, -18.0), objetivo=(2.0, 8.0, 4.0), fov=62, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(20, 46)
    cima(lz, cam, niebla, jugadores=((-3.0, -6.0, 210), (6.0, -4.0, 150), (-1.2, -1.0, 40, 9.0)))
    aeralis(lz, cam, 'despues', 2.5, Y_VUELO_NUEVA, 4.0, 200, pose=rm.HEROICA, fase=fase, niebla=niebla)
    ve.dibujar_translucido(lz, cam, cuadrado_suelo(-1.0, -1.0, 2.2), tex_aro(P['borde'], 64, 0.1, 16, 60), 0.9, None, 0.8)
    ve.dibujar_translucido(lz, cam, ve.tornado(-1.0, -1.0, 13.0, 1.6, 2.0, 0.0, anillos=20, segs=12),
                           tex_viento2(P['halo'], 31, densidad=0.6), 0.6, niebla, 0.35)
    r = random.Random(8)
    hojas = [billboard((-1.0 + r.uniform(-1.5, 1.5), r.uniform(0.5, 12), -1.0 + r.uniform(-1.5, 1.5)), 0.12, cam, r.uniform(0, 3))
             for _ in range(30)]
    ve.dibujar_translucido(lz, cam, hojas, tex_plano(luz_fase(P)), 1.0, niebla, 0.8)
    for k in range(5):
        x = -1.0 + r.uniform(-1.2, 1.2)
        flecha = [(x, 1.0 + k * 2.2, -1.0 + r.uniform(-1.2, 1.2)), (x, 2.4 + k * 2.2, -1.0)]
        ve.dibujar_translucido(lz, cam, cinta3d(flecha, 0.06, cam), tex_plano(P['borde']), 1.0, None, 1.0)
    acabar(lz, cam, W, H, 'nuevo_corriente', 29, fase, rayos=0.3, estelas=60)


ESCENAS = {
    'prueba': prueba, 'prueba4': lambda: prueba(fase=4),
    'heroica_antes': lambda: heroica('antes'), 'heroica_despues': lambda: heroica('despues'),
    'heroica_despues_f4': lambda: heroica('despues', fase=4),
    'vistas_antes': lambda: vistas('antes'), 'vistas_despues': lambda: vistas('despues'),
    'fases_antes': lambda: fases('antes'), 'fases_despues': lambda: fases('despues'),
    'escala': escala,
    'aleteo': aleteo, 'tornados': tornados, 'caceria': caceria, 'juicio': juicio,
    'picado': picado, 'posada': posada, 'escamas': escamas, 'corriente': corriente,
}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        r = ESCENAS[k]()
        print(k, r if r else '')

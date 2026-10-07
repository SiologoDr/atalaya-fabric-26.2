"""
Renders de la ficha de las mecanicas nuevas de Novilis, el Caballero Solar
(octubre de 2026: "que cada jefe haga que los jugadores cooperen con mecanicas
suyas"). Cada propuesta en el Altar del Sol de su ficha, con Novilis a su
tamano del juego (16 bloques al yelmo) y jugadores; usa las ayudas de
fuego_escenas (el altar, los braseros, el cielo con su sol, las llamas, los
haces, las poses y el acabado).

  duelo     Duelo de Honor: un anillo de fuego encierra a Novilis y al retado,
            que alza la espada; fuera, un companero echa un cubo de agua al
            anillo y abre un hueco
  armadura  Armadura al Rojo: placas de la armadura al rojo vivo; los de
            alrededor le tiran pociones arrojadizas de agua; una ya enfriada,
            gris y echando vapor
  espejos   Espejos del Sol: alza la espada y su sol carga el rayo; tres losas
            espejo con un jugador en cada una le devuelven el rayo
  llama     Llama Viva: un jugador envuelto en una llama que crece corre hacia
            un companero para pasarsela; encima, la cuenta atras

Uso: python novilis_mecanicas_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import io, math, os, random, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fuego_escenas as fe  # lee la raiz y la carpeta de salida de sys.argv
from fuego_escenas import vr, nm, ne, fm

OUT = fe.OUT
SS = fe.SS
TAU = math.tau
FUENTE = fe.FUENTE
V = 'N'
ESCALA = 256.0 / 146.0      # la del juego (novilis_juego.ESCALA): 16 bloques al yelmo

ORO = (255, 194, 58)
ORO_CLARO = (255, 240, 190)
BRASA = (255, 138, 30)
ROJO = (255, 64, 44)
AGUA = (70, 160, 255)
AGUA_CLARO = (196, 232, 255)
BLANCO = (255, 246, 232)
SOMBRA = (20, 8, 6)


# ----------------------------------------------------------------------
#  Texturas (RGBA uint8)
# ----------------------------------------------------------------------
def _rgba(col, a):
    t = np.zeros(col.shape[:2] + (4,))
    t[..., :3] = col
    t[..., 3] = np.clip(a, 0, 1) * 255
    return np.clip(t, 0, 255).astype(np.uint8)


def _ruido(n, semilla, escala=8):
    r = np.random.RandomState(semilla)
    g = r.rand(escala + 1, escala + 1)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
    return np.array(im).astype(float) / 255


def tex_vapor(n=64, semilla=1):
    """Una bocanada de vapor: una nube blanda, blanca y algo gris."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    a = np.clip(1 - d, 0, 1) ** 1.3 * (0.55 + 0.45 * _ruido(n, semilla, 5))
    col = np.ones((n, n, 3)) * np.array([236, 238, 242])
    return _rgba(col, a * 0.95)


def tex_salpicon(n=128, color=AGUA, semilla=2):
    """La corona de agua al chocar: chorros que se abren hacia arriba y gotas."""
    r = random.Random(semilla)
    im = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(im)
    base = (n / 2, n * 0.9)
    for k in range(13):
        a = math.radians(-75 + 150 * k / 12 + r.uniform(-5, 5))
        largo = n * r.uniform(0.45, 0.8) * (1 - 0.35 * abs(math.sin(a)))
        fin = (base[0] + math.sin(a) * largo, base[1] - math.cos(a) * largo)
        d.line([base, fin], fill=255, width=max(2, int(n / 28)))
        rad = n * r.uniform(0.02, 0.035)
        d.ellipse((fin[0] - rad, fin[1] - rad, fin[0] + rad, fin[1] + rad), fill=255)
    for _ in range(14):
        a = r.uniform(-1.4, 1.4)
        l = n * r.uniform(0.3, 0.85)
        q = (base[0] + math.sin(a) * l, base[1] - math.cos(a) * l)
        rad = n * r.uniform(0.012, 0.025)
        d.ellipse((q[0] - rad, q[1] - rad, q[0] + rad, q[1] + rad), fill=255)
    d.ellipse((n * 0.2, n * 0.8, n * 0.8, n * 0.98), fill=200)
    m = np.array(im.filter(ImageFilter.GaussianBlur(n / 120))).astype(float) / 255
    halo = np.array(im.filter(ImageFilter.GaussianBlur(n / 25))).astype(float) / 255
    k = np.clip(m * 1.3 - 0.3, 0, 1)[..., None]
    col = np.array(color) * (1 - k) + np.array(AGUA_CLARO) * k
    return _rgba(col, np.clip(m + halo * 0.35, 0, 1))


def tex_chorro(w=64, h=16, semilla=3):
    """El chorro de agua (u a lo largo, v de lado a lado): el alma clara, vetas."""
    r = np.random.RandomState(semilla)
    v = np.abs(np.linspace(-1, 1, h))[:, None] * np.ones((1, w))
    vetas = np.repeat(r.rand(h, w // 8 + 1), 8, axis=1)[:, :w]
    a = np.clip(1 - v ** 2, 0, 1) * (0.75 + 0.25 * vetas)
    k = np.clip(1 - v * 2.2, 0, 1)[..., None]
    col = np.array(AGUA) * (1 - k) + np.array(AGUA_CLARO) * k
    return _rgba(col, a)


def tex_gota(n=32, color=AGUA):
    """Una gota de agua (para las estelas de las pociones)."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    a = np.clip(1.15 - d, 0, 1) ** 0.8
    brillo = np.clip(1 - np.hypot(xx + 0.5 - n * 0.38, yy + 0.5 - n * 0.36) / (n * 0.18), 0, 1)[..., None]
    col = np.array(color) * (1 - brillo) + np.array([255, 255, 255]) * brillo
    return _rgba(col, a)


def tex_rojo_vivo(n=16, semilla=4):
    """El metal al rojo (se suma encima de las placas): rojo oscuro con grietas
    amarillas que lo cruzan."""
    r = random.Random(semilla)
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            grieta = (x + 2 * y) % 9 == 0 or (3 * x - y) % 13 == 0
            if grieta:
                t[y, x] = (255, 214, 110, 255)
            else:
                c = (250, 96, 34) if r.random() < 0.4 else (205, 40, 18)
                t[y, x] = (*c, 170)
    return t


def tex_ceniza(n=16, semilla=5):
    """La placa ya enfriada: gris ceniza, con motas mas claras."""
    r = random.Random(semilla)
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            g = r.choice((118, 132, 140, 150, 170))
            t[y, x] = (g, g, g + 6, 255)
    return t


def tex_espejo(n=96):
    """La cara del espejo: el cielo reflejado (de oro palido a blanco), con
    vetas de luz en diagonal y un filete claro por dentro del marco."""
    yy, xx = np.mgrid[0:n, 0:n]
    u, v = (xx + 0.5) / n, (yy + 0.5) / n
    base = np.array([255, 214, 140]) * (1 - v[..., None]) * 0.7 + np.array([255, 250, 232]) * (0.3 + 0.7 * v[..., None]) * 0.9
    s = (u + v) * 3.0 % 1.0
    veta = (np.abs(s - 0.3) < 0.07) | (np.abs(s - 0.52) < 0.03)
    col = np.where(veta[..., None], np.array([255, 255, 255]), base)
    borde = (np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v)) < 0.05)
    col = np.where(borde[..., None], np.array([255, 236, 170]), col)
    return _rgba(col, np.ones((n, n)))


def tex_trazo(color, w=48, h=12):
    """Una raya de la linea de puntos (u a lo largo): un trazo con las puntas romas."""
    u = np.linspace(-1, 1, w)[None, :] * np.ones((h, 1))
    v = np.linspace(-1, 1, h)[:, None] * np.ones((1, w))
    a = np.clip(1.2 - np.hypot(np.maximum(np.abs(u) - 0.6, 0) / 0.4, v), 0, 1) ** 0.7
    return _rgba(np.ones((h, w, 3)) * np.array(color), a)


def _item_vanilla(nombre):
    """El sprite de un objeto vanilla, del jar del cliente que deja loom (si esta)."""
    jar = os.path.join(os.path.expanduser('~'), '.gradle/caches/fabric-loom/26.2/minecraft-client-only.jar')
    try:
        with zipfile.ZipFile(jar) as z:
            return Image.open(io.BytesIO(z.read('assets/minecraft/textures/item/' + nombre))).convert('RGBA')
    except (OSError, KeyError):
        return None


def _sprite_simple(tipo):
    """Si no hay jar: un dibujo sencillo del objeto."""
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tipo == 'cubo':
        d.polygon([(3, 4), (12, 4), (11, 14), (4, 14)], fill=(180, 184, 190, 255))
        d.rectangle((3, 4, 12, 6), fill=(60, 110, 230, 255))
    elif tipo == 'pocion':
        d.ellipse((3, 6, 12, 15), fill=(60, 100, 220, 255))
        d.rectangle((6, 2, 9, 7), fill=(200, 220, 240, 255))
        d.rectangle((6, 1, 9, 2), fill=(170, 90, 50, 255))
    else:
        d.line([(3, 12), (13, 2)], fill=(230, 232, 236, 255), width=2)
        d.line([(2, 9), (6, 13)], fill=(60, 50, 40, 255), width=2)
    return im


def sprite_item(tipo):
    if tipo == 'cubo':
        im = _item_vanilla('water_bucket.png')
    elif tipo == 'pocion':
        # la arrojadiza de agua: el cristal encima del liquido tenido del color del agua (0x385DC6)
        botella, liquido = _item_vanilla('splash_potion.png'), _item_vanilla('potion_overlay.png')
        im = None
        if botella is not None and liquido is not None:
            l = np.array(liquido).astype(float)
            l[..., :3] = l[..., :3] / 255.0 * np.array([0x38, 0x5D, 0xC6]) * 1.25
            im = Image.alpha_composite(Image.fromarray(np.clip(l, 0, 255).astype(np.uint8)), botella)
    else:
        im = _item_vanilla('iron_sword.png')
    return np.array(im if im is not None else _sprite_simple(tipo))


def sprites_fuego(fase):
    """Los dos fuegos de vanilla (el primer fotograma de fire_0 y fire_1), o las
    lenguas de fuego_escenas si no hay jar."""
    jar = os.path.join(os.path.expanduser('~'), '.gradle/caches/fabric-loom/26.2/minecraft-client-only.jar')
    try:
        with zipfile.ZipFile(jar) as z:
            return [np.array(Image.open(io.BytesIO(z.read(f'assets/minecraft/textures/block/fire_{i}.png'))).convert('RGBA')
                             .crop((0, 0, 16, 16))) for i in (0, 1)]
    except (OSError, KeyError):
        return [fe.tex_llama_sprite(fase, i) for i in (0, 1)]


VAPOR = [tex_vapor(64, s) for s in range(4)]
SALPICON = tex_salpicon()
CHORRO = tex_chorro()
GOTA = tex_gota()
ROJO_VIVO = tex_rojo_vivo()
CENIZA = tex_ceniza()
ESPEJO = tex_espejo()


# ----------------------------------------------------------------------
#  Novilis: las poses de esta ficha y lo que brilla de su armadura
# ----------------------------------------------------------------------
_POSES = {}


def pose(nombre):
    """Las poses de fuego_escenas y las de esta ficha (los brazos por IK)."""
    if nombre in _POSES:
        return {k: dict(v) for k, v in _POSES[nombre].items()}
    if nombre == 'SENALA':
        # el reto: la espada tendida hacia el retado, la otra mano al pecho
        p = fe._une(fe.PIERNAS_GUARDIA, fe.CAPA_VIENTO, {'torso': {'rot': (4, 8, 0)}, 'cabeza': {'rot': (14, -6, 0)}})
        p, _ = fm.alcanzar(p, 'der', (-16, -66, -40))
        p, _ = fm.alcanzar(p, 'izq', (10, -78, -20))
        p = fm.apuntar_espada(p, (0.05, 0.42, -0.9))
    elif nombre == 'MARCA':
        # senala con la mano izquierda al que prende; la espada baja
        p = fe._une(fe.PIERNAS_GUARDIA, fe.CAPA_VIENTO, {'torso': {'rot': (0, -12, 0)}, 'cabeza': {'rot': (10, 14, 0)}})
        p, _ = fm.alcanzar(p, 'izq', (40, -76, -46))
        p, _ = fm.alcanzar(p, 'der', (-24, -40, -16))
        p = fm.apuntar_espada(p, (-0.2, 0.62, -0.76))
    elif nombre == 'ALZA_SOL':
        # la espada en alto y de lado, hacia el cielo: en la punta carga su sol
        p = fe._une(fe.PIERNAS_GUARDIA, fe.CAPA_VIENTO, {'cabeza': {'rot': (-22, 10, 0)}, 'torso': {'rot': (-6, -8, 0)}})
        p, _ = fm.alcanzar(p, 'der', (-32, -104, -24))
        p, _ = fm.alcanzar(p, 'izq', (30, -52, -22))
        p = fm.apuntar_espada(p, (-0.62, -0.62, -0.48))
    else:
        p = fe.pose(nombre)
    _POSES[nombre] = p
    return {k: dict(v) for k, v in p.items()}


def caballero(lz, cam, x, z, guinada, p, fase, niebla, con_espada=True):
    return fe.caballero(lz, cam, x, z, guinada, p, V, fase, niebla, con_espada=con_espada, escala=ESCALA)


def quads_por_pieza(p, M, con_espada=True):
    """Los cuadrilateros de Novilis con el nombre de la pieza a la que van."""
    out = []

    def visitar(n, Mp):
        nombre, off, rot, cajas, hijos = n
        ex = p.get(nombre, {})
        if ex.get('oculto'):
            return
        r = [rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        q = [off[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        L = vr.T(*q) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R) @ vr.S(ex.get('esc', 1.0))
        Mn = Mp @ L
        for box, mat in cajas:
            for pts, uv in nm.caja_mosaico(box):
                out.append(([(M @ Mn @ np.array([*c, 1.0]))[:3] for c in pts], uv, mat, nombre))
        for h in hijos:
            visitar(h, Mn)

    visitar(fm.esqueleto(V, con_espada), np.eye(4))
    return out


def capa_sobre(lz, cam, qs, tex, modo='aditivo', k=1.0, brillo=1.0):
    """Pinta otra vez unos cuadrilateros, un pelo hacia la camara, con otra
    textura: sumada (al rojo) o mezclada (la ceniza)."""
    for P, UV, _, _ in qs:
        P = [np.array(c) + (cam.ojo - np.array(c)) / np.linalg.norm(cam.ojo - np.array(c)) * 0.04 for c in P]
        for tri in ((0, 1, 2), (0, 2, 3)):
            if modo == 'aditivo':
                lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, aditivo=True,
                             brillo=brillo, envolver=True)
            else:
                # sin la luz calida del altar, para que el gris se lea gris
                luz = np.ones(3) * (0.55 + 0.4 * max(0.0, float(vr.normal(P) @ (cam.ojo - P[0])) /
                                                     np.linalg.norm(cam.ojo - P[0])))
                lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, None, None, translucido=k,
                             envolver=True)


PLACAS = {
    'hombrera_izq': ('hombro_izq', 'guarda_izq'),
    'hombrera_der': ('hombro_der', 'guarda_der'),
    'peto': ('torso',),
    'muslo_izq': ('pierna_izq',),
    'muslo_der': ('pierna_der',),
}
METAL = {'placa', 'placa_osc', 'grabado'}


def placa(qs, cual):
    return [q for q in qs if q[3] in PLACAS[cual] and q[2] in METAL]


# ----------------------------------------------------------------------
#  Los jugadores, con lo que llevan en la mano
# ----------------------------------------------------------------------
def _ruta(n, nombre, camino=()):
    if n[0] == nombre:
        return list(camino) + [n]
    for h in n[4]:
        r = _ruta(h, nombre, list(camino) + [n])
        if r:
            return r
    return None


def punto_jugador(M, p, nodo, local=(0, 0, 0)):
    """Donde cae en el mundo un punto de una pieza del jugador (px de su modelo)."""
    Mn = np.eye(4)
    for nombre, off, rot, _, _ in _ruta(ne.jugador(), nodo):
        ex = p.get(nombre, {})
        r = [rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        q = [off[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        Mn = Mn @ vr.T(*q) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R)
    return (M @ Mn @ np.array([*local, 1.0]))[:3]


def jugador(lz, cam, x, z, mira, p=None, y=0.0, niebla=None, extra=0.0):
    """Un jugador en (x, z) mirando hacia el punto 'mira' (x, z)."""
    p = p or {}
    M = vr.T(0, y, 0) @ ne.jugador_a_mundo(x, z, fe.guinada_hacia(x, z, *mira) + extra)
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), p, M), fe.LUCES, fe.AMB, niebla)
    return M, p


def sprite(lz, cam, c, tam, tex, giro=0.0, luz=1.0):
    """Un objeto plano (como los del inventario) de cara a la camara, opaco."""
    P, UV = fe.billboard(c, tam, cam, giro)
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3) * luz, None, None)


def en_mano(lz, cam, Mj, p, tipo, tam=0.32, giro=0.0, luz=1.0):
    """El objeto en la mano derecha del jugador (el mango en la mano)."""
    mano = punto_jugador(Mj, p, 'bd', (0, 10.5, 0))
    tex = sprite_item(tipo)
    if tipo == 'espada':
        # el mango (abajo a la izquierda del sprite) en la mano: la hoja hacia 'giro'
        g = giro
        rr = cam.r * math.cos(g) + cam.u * math.sin(g)
        uu = -cam.r * math.sin(g) + cam.u * math.cos(g)
        centro = mano + (rr + uu) * tam * 0.78
    else:
        centro = mano + cam.u * tam * 0.2
    sprite(lz, cam, centro, tam, tex, giro, luz)
    return mano


ALZAR = {'bd': {'rot': (-160, 0, 12)}, 'bi': {'rot': (-30, 0, -20)}, 'pi': {'rot': (-20, 0, 0)}, 'pd': {'rot': (22, 0, 0)}}
ECHAR = {'bd': {'rot': (-100, 0, 0)}, 'bi': {'rot': (-60, 0, 0)}, 'pi': {'rot': (-24, 0, 0)}, 'pd': {'rot': (18, 0, 0)}}
TIRAR = {'bd': {'rot': (-150, 0, 6)}, 'bi': {'rot': (30, 0, -10)}, 'pi': {'rot': (-26, 0, 0)}, 'pd': {'rot': (22, 0, 0)}}
CORRER = {'bi': {'rot': (40, 0, 0)}, 'bd': {'rot': (-44, 0, 0)}, 'pi': {'rot': (-40, 0, 0)}, 'pd': {'rot': (38, 0, 0)}}
PEDIR = {'bi': {'rot': (-110, 0, -16)}, 'bd': {'rot': (-100, 0, 16)}, 'pi': {'rot': (-10, 0, 0)}, 'pd': {'rot': (10, 0, 0)}}
QUIETO = {'bi': {'rot': (-12, 0, 0)}, 'bd': {'rot': (14, 0, 0)}}
MIRAR = {'bi': {'rot': (-20, 0, -8)}, 'bd': {'rot': (-30, 0, 8)}}


# ----------------------------------------------------------------------
#  Efectos
# ----------------------------------------------------------------------
def arco_pared(cx, cz, r, alto, a0, a1, n=48, rep=8.0, y0=0.0):
    """Un trozo de pared cilindrica (de a0 a a1, radianes), u a lo largo."""
    out = []
    for i in range(n):
        b0, b1 = a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n
        P = [(cx + math.cos(b0) * r, y0, cz + math.sin(b0) * r), (cx + math.cos(b1) * r, y0, cz + math.sin(b1) * r),
             (cx + math.cos(b1) * r, y0 + alto, cz + math.sin(b1) * r), (cx + math.cos(b0) * r, y0 + alto, cz + math.sin(b0) * r)]
        u0, u1 = i / n * rep, (i + 1) / n * rep
        out.append((P, [(u0, 1), (u1, 1), (u1, 0), (u0, 0)]))
    return out


def vapor(lz, cam, p, tam, n=6, semilla=0, k=0.55, sube=2.4):
    """Unas bocanadas de vapor que suben desde p."""
    r = random.Random(semilla)
    p = np.array(p, float)
    for i in range(n):
        t = i / max(1, n - 1)
        q = p + np.array([r.uniform(-0.5, 0.5) * tam, sube * t * tam, r.uniform(-0.5, 0.5) * tam])
        fe.trans(lz, cam, [fe.billboard(q, tam * (0.45 + 0.6 * t), cam, r.uniform(0, TAU))], VAPOR[i % 4],
                 k * (1 - 0.5 * t), None, 0.0, 1.0)


def salpicon(lz, cam, p, tam, k=0.95, glow=0.25):
    """La corona de agua al chocar (de pie en p)."""
    q = np.array(p, float) + cam.u * tam * 0.8
    fe.trans(lz, cam, [fe.billboard(q, tam, cam)], SALPICON, k, None, glow, 1.0)


def arco_gotas(lz, cam, a, b, alto, n=12, tam=(0.08, 0.2), k=0.9):
    """La estela de una pocion en el aire: gotas por un arco de a a b."""
    a, b = np.array(a, float), np.array(b, float)
    pts = []
    for i in range(n):
        t = (i + 0.5) / n
        q = a + (b - a) * t + np.array([0, alto * math.sin(math.pi * t), 0])
        pts.append(q)
        s = tam[0] + (tam[1] - tam[0]) * t
        fe.trans(lz, cam, [fe.billboard(q, s, cam)], GOTA, k, None, 0.35, 1.0)
    return pts


def linea_puntos(lz, cam, a, b, color, y=0.12, paso=0.9, largo=0.5, ancho=0.12, brillo=1.0):
    """Una linea de trazos en el suelo de a a b (x, z)."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    d /= L
    lado = np.array([-d[1], d[0]]) * ancho
    tex = tex_trazo(color)
    t = 0.0
    while t + largo <= L:
        p0, p1 = a + d * t, a + d * (t + largo)
        P = [(p0[0] - lado[0], y, p0[1] - lado[1]), (p1[0] - lado[0], y, p1[1] - lado[1]),
             (p1[0] + lado[0], y, p1[1] + lado[1]), (p0[0] + lado[0], y, p0[1] + lado[1])]
        fe.aditivo(lz, cam, [(P, [(0, 1), (1, 1), (1, 0), (0, 0)])], tex, brillo)
        t += paso


def llama_plana(lz, cam, base, ancho, alto, tex, brillo=0.7, k=None):
    """Un fuego plano de pie (como el de quien arde en vanilla): de cara a la
    camara pero vertical, con el pie en 'base'. Recortado y encendido, o
    translucido si se da k."""
    lado = np.array([cam.r[0], 0, cam.r[2]]) / np.linalg.norm([cam.r[0], cam.r[2]])
    b = np.array(base, float)
    arriba = np.array([0, alto, 0])
    P = [b - lado * ancho, b + lado * ancho, b + lado * ancho + arriba, b - lado * ancho + arriba]
    UV = [(0, 1), (1, 1), (1, 0), (0, 0)]
    for tri in ((0, 1, 2), (0, 2, 3)):
        if k is None:
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), tex, None, brillo=brillo)
        else:
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, translucido=k)
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, aditivo=True,
                         brillo=brillo)


def aro_suelo(lz, cam, x, z, R, color, k=0.8, glow=0.5, grueso=0.05, marcas=24, relleno=40):
    fe.trans(lz, cam, fe.suelo_cuad(x, z, R, 0.08), fe.tex_aro(color, 256, grueso, relleno, marcas), k, None, glow)


# ----------------------------------------------------------------------
#  Rotulos (sobre la imagen ya compuesta, en pixeles de 1600 de ancho)
# ----------------------------------------------------------------------
def rotulo(img, cam, p, texto, dx, dy, tam=30, color=BLANCO, linea=True, centro=False):
    """Un rotulo en mayusculas junto al punto p del mundo, desplazado (dx, dy),
    con su sombra y, si se pide, una linea fina hasta el punto."""
    sx, sy, z = cam.proyectar(p)
    if z < 0.5:
        return
    sx, sy = sx / SS, sy / SS
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', tam)
    d = ImageDraw.Draw(img)
    w = d.textlength(texto, font=f)
    tx, ty = sx + dx, sy + dy
    if centro:
        tx -= w / 2
    elif dx < 0:
        tx -= w
    tx = min(max(tx, 14), img.size[0] - w - 14)
    if linea:
        ax = min(max(sx, tx), tx + w)
        arriba, abajo = ty + tam * 0.3, ty + tam * 1.3
        ay = abajo if sy > abajo else (arriba if sy < arriba else sy)
        if arriba <= sy <= abajo:
            ax = tx - 6 if sx < tx else tx + w + 6
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        dc.line([(sx, sy), (ax, ay)], fill=(*SOMBRA, 160), width=5)
        dc.line([(sx, sy), (ax, ay)], fill=(*color, 230), width=2)
        dc.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=(*color, 255))
        img.alpha_composite(capa)
    for o in ((3, 3), (2, 2), (-1, 1)):
        d.text((tx + o[0], ty + o[1]), texto, font=f, fill=(*SOMBRA, 255))
    d.text((tx, ty), texto, font=f, fill=(*color, 255))


def cifra(img, cam, p, texto, tam, color, dy=0):
    """Una cifra grande que brilla (la cuenta atras), centrada sobre p."""
    sx, sy, _ = cam.proyectar(p)
    sx, sy = sx / SS, sy / SS + dy
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', tam)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    w = d.textlength(texto, font=f)
    d.text((sx - w / 2, sy - tam * 0.8), texto, font=f, fill=(*color, 255))
    halo = capa.filter(ImageFilter.GaussianBlur(tam / 7))
    img.alpha_composite(halo)
    img.alpha_composite(halo)
    sombra = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).text((sx - w / 2 + 3, sy - tam * 0.8 + 3), texto, font=f, fill=(*SOMBRA, 255))
    img.alpha_composite(sombra)
    img.alpha_composite(capa)


def acabar(lz, cam, W, H, fase, semilla, sol=False):
    return fe.componer(lz, cam, W, H, fase, sol=sol, semilla=semilla).convert('RGBA')


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)
    print('ok', nombre, flush=True)


# ----------------------------------------------------------------------
#  1. Duelo de Honor
#
#  Un anillo de fuego de 9 bloques encierra a Novilis y al retado, que alza la
#  espada; fuera, los demas. Uno echa un cubo de agua al anillo y abre un hueco
#  (las llamas se apagan ahi, el suelo mojado y el vapor).
# ----------------------------------------------------------------------
def duelo(W=1600, H=900, fase=2):
    cam = vr.Camara(ojo=(-17.0, 10.5, -24.0), objetivo=(0.5, 5.4, 1.5), fov=58, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    cx, cz, R = 0.0, 0.0, 9.0
    nov = (0.0, 4.6)
    retado = (-0.6, -4.8)
    hueco = math.radians(280)                  # donde le echan el agua (delante, a la izquierda de la foto)
    ancho_hueco = 0.24                         # radianes a cada lado
    hp = np.array([cx + math.cos(hueco) * R, 0.0, cz + math.sin(hueco) * R])
    # el retado, de cara a el y con la espada en alto
    Mr, pr = jugador(lz, cam, retado[0], retado[1], nov, ALZAR, niebla=niebla)
    en_mano(lz, cam, Mr, pr, 'espada', 0.42, giro=math.radians(40), luz=1.1)
    # los de fuera: el del cubo junto al hueco, uno con una pocion y otros dos que esperan
    a_c = math.radians(298)
    fuera = np.array([cx + math.cos(a_c) * (R + 2.6), cz + math.sin(a_c) * (R + 2.6)])
    Mc, pc = jugador(lz, cam, fuera[0], fuera[1], (hp[0], hp[2]), ECHAR, niebla=niebla)
    cubo = en_mano(lz, cam, Mc, pc, 'cubo', 0.34)
    Mp, pp = jugador(lz, cam, 12.6, -2.5, (cx, cz), TIRAR, niebla=niebla)
    en_mano(lz, cam, Mp, pp, 'pocion', 0.3)
    for (x, z) in ((-12.6, 3.0), (-10.0, -9.5)):
        jugador(lz, cam, x, z, (cx, cz), MIRAR, niebla=niebla)
    p = pose('SENALA')
    M = caballero(lz, cam, nov[0], nov[1], fe.guinada_hacia(*nov, *retado), p, fase, niebla)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase)
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[fase])
    # el hueco: el suelo mojado y oscuro (antes que las llamas)
    fe.trans(lz, cam, fe.suelo_cuad(hp[0], hp[2], 2.2, 0.09, 0.4), fe.tex_disco((26, 40, 64), (20, 30, 48), 64, 0.45, 0.9),
             0.85, None, 0.0)
    # el anillo: la pared de llamas, menos en el hueco (que se abre a los lados)
    a0, a1 = hueco + ancho_hueco, hueco + TAU - ancho_hueco
    pared = fe.tex_llamas(nuc, pri, hon, 64, 48, 7, 1.4)
    fe.trans(lz, cam, arco_pared(cx, cz, R, 2.4, a0, a1, 110, 26.0), pared, 0.85, None, 0.25)
    banda = np.transpose(fe.tex_haz(nuc, pri, 32, 8), (1, 0, 2)).copy()
    fe.aditivo(lz, cam, fe.banda_horizontal(cx, 0.08, cz, R - 0.4, R + 0.4, a0, a1, 110), banda, 0.55)
    r = random.Random(9)
    for i in range(96):
        a = a0 + (a1 - a0) * (i + 0.5) / 96
        borde = min(a - a0, a1 - a)
        t = min(1.0, 0.25 + borde / 0.3)            # junto al hueco, mas bajas
        alto = (1.0 + 1.1 * r.random()) * t
        q = np.array([cx + math.cos(a) * R, 0.2 + alto * 0.5, cz + math.sin(a) * R])
        fe.aditivo(lz, cam, [fe.billboard(q, alto * 0.42, cam, r.uniform(-0.2, 0.2), alto=alto * 0.55)],
                   fe.tex_llama_sprite(fase, i), 0.85)
    # el chorro del cubo, la salpicadura y el vapor en el hueco
    boca = cubo + cam.u * 0.25
    pts = [boca + (hp + np.array([0, 0.3, 0]) - boca) * t + np.array([0, 0.9 * math.sin(math.pi * t), 0])
           for t in np.linspace(0, 1, 12)]
    fe.trans(lz, cam, fe.cinta3d(pts, lambda t: 0.12 + 0.24 * t, cam), CHORRO, 0.92, None, 0.3, 1.0)
    salpicon(lz, cam, hp + np.array([0, 0.05, 0]), 1.4)
    for k, d in enumerate((-0.18, 0.0, 0.18)):
        a = hueco + d
        vapor(lz, cam, (cx + math.cos(a) * R, 0.5, cz + math.sin(a) * R), 1.2, 7, 3 + k, 0.5, 3.0)
    img = acabar(lz, cam, W, H, fase, 81)
    rotulo(img, cam, (cx + math.cos(math.radians(160)) * R, 2.6, cz + math.sin(math.radians(160)) * R), 'DUELO', 40, -150,
           60, ORO_CLARO)
    rotulo(img, cam, hp + np.array([0, 0.4, 0]), '¡AGUA AL FUEGO!', -150, 110, 44, AGUA_CLARO)
    guardar(img, 'duelo')


# ----------------------------------------------------------------------
#  2. Armadura al Rojo
#
#  Ruge con la armadura al rojo vivo: cuatro placas encendidas y una ya
#  enfriada (gris y echando vapor). Alrededor, los jugadores le tiran pociones
#  arrojadizas de agua (las gotas en arco) y una le acaba de dar.
# ----------------------------------------------------------------------
def fuego_cuerpo(lz, cam, M, p, fase, k=1.0, sin_hombro=None):
    """Como fuego_escenas.fuego_cuerpo (la variante N), pero sin las llamas del
    hombro que se pida (el de la placa ya enfriada)."""
    fe.brillo_en(lz, cam, fe.mundo_de(M, V, p, 'halo'), 3.6, fe.color_fase(fase), 0.35 * k)
    for lado in ('izq', 'der'):
        if lado != sin_hombro:
            fe.llamas_en(lz, cam, fe.mundo_de(M, V, p, 'hombro_' + lado, (6.5 if lado == 'izq' else -6.5, -13, 0)), 0.8,
                         fase, 3, 12, k)
    fe.brillo_en(lz, cam, fe.mundo_de(M, V, p, 'torso', (0, -34, -16)), 1.6, fe.color_fase(fase), 0.5 * k)
    for i in range(7):
        fe.llamas_en(lz, cam, fe.mundo_de(M, V, p, 'espada', (0, 16 + i * 9, 0)), 0.55, fase, 2, 40 + i, 0.8 * k)
    fe.brillo_en(lz, cam, fe.mundo_de(M, V, p, 'espada', (0, 9, 0)), 0.9, fe.color_fase(fase, 0), 0.6 * k)


def armadura(W=1600, H=900, fase=3):
    cam = vr.Camara(ojo=(-12.0, 4.2, -15.5), objetivo=(0.5, 8.6, 4.0), fov=62, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(28, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    nov = (0.0, 5.0)
    p = pose('GRITO')
    g = fe.guinada_hacia(*nov, -8.0, -10.0)
    M = caballero(lz, cam, nov[0], nov[1], g, p, fase, niebla)
    qs = quads_por_pieza(p, M)
    tiradores = [(-7.5, -2.0), (-3.2, -5.2), (4.6, -3.4), (-10.5, 4.0)]
    blancos = ['hombrera_izq', 'peto', 'muslo_der', 'muslo_izq']
    pociones = []
    for (x, z), b in zip(tiradores, blancos):
        Mj, pj = jugador(lz, cam, x, z, nov, TIRAR, niebla=niebla)
        mano = punto_jugador(Mj, pj, 'bd', (0, 10.5, 0))
        pociones.append((mano, b))
    # lo que brilla: las placas al rojo, la enfriada en gris
    enfriada = 'hombrera_der'
    for cual in PLACAS:
        if cual == enfriada:
            capa_sobre(lz, cam, placa(qs, cual), CENIZA, 'mezcla', 1.0)
        else:
            capa_sobre(lz, cam, placa(qs, cual), ROJO_VIVO, 'aditivo', brillo=0.5)
    fuego_cuerpo(lz, cam, M, p, fase, k=0.7, sin_hombro='der')
    centros = {c: np.mean([np.mean(q[0], axis=0) for q in placa(qs, c)], axis=0) for c in PLACAS}
    for cual, c in centros.items():
        if cual != enfriada:
            fe.brillo_en(lz, cam, c, 1.8, (255, 60, 24), 0.35)
    vapor(lz, cam, centros[enfriada] + np.array([0, 0.8, 0]), 1.5, 8, 5, 0.75, 2.6)
    # las pociones: tres en el aire y una que acaba de reventar contra el peto
    tex_p = sprite_item('pocion')
    for i, (mano, b) in enumerate(pociones):
        meta = centros[b]
        t_fin = 1.0 if b == 'peto' else (0.5 + 0.12 * i)
        pts = arco_gotas(lz, cam, mano, mano + (meta - mano) * t_fin, 2.6 * t_fin, int(14 * t_fin) + 2, (0.1, 0.24))
        if b == 'peto':
            hacia = (cam.ojo - meta) / np.linalg.norm(cam.ojo - meta)
            salpicon(lz, cam, meta - np.array([0, 1.0, 0]) + hacia * 1.6, 1.9)
            vapor(lz, cam, meta + hacia * 1.2 + np.array([0, 0.4, 0]), 1.2, 6, 8, 0.6, 2.4)
        else:
            sprite(lz, cam, pts[-1] + (pts[-1] - pts[-2]) * 0.9, 0.5, tex_p, 0.3 * i - 0.3, 1.15)
    img = acabar(lz, cam, W, H, fase, 82)
    rotulo(img, cam, centros['hombrera_izq'], '¡ENFRÍALA!', 90, -90, 54, AGUA_CLARO)
    rotulo(img, cam, centros[enfriada], 'YA ENFRIADA', -90, -110, 30, (226, 228, 234))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 64)
    for o in ((3, 3), (2, 2)):
        d.text((60 + o[0], 60 + o[1]), '1/5', font=f, fill=(*SOMBRA, 255))
    d.text((60, 60), '1/5', font=f, fill=(*ORO_CLARO, 255))
    f2 = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 26)
    d.text((62, 140), 'PLACAS ENFRIADAS', font=f2, fill=(*BLANCO, 255))
    guardar(img, 'armadura')


# ----------------------------------------------------------------------
#  3. Espejos del Sol
#
#  Alza la espada: su sol carga el rayo encima de la punta. Alrededor, tres
#  losas espejo con un jugador en cada una; el rayo baja a los espejos y
#  rebota contra su pecho.
# ----------------------------------------------------------------------
def losa_espejo(lz, cam, x, z, hacia, niebla, fase, inclina=12.0):
    """La losa: una peana de basalto con el marco de oro y el espejo encima,
    algo inclinado hacia 'hacia' (x, z). Devuelve el centro del espejo."""
    qs = fe.caja_mundo(x - 1.6, 0, z - 1.6, 3.2, 0.3, 3.2, 'basalto_j')
    for (a, b, w, d) in ((-1.6, -1.6, 3.2, 0.3), (-1.6, 1.3, 3.2, 0.3), (-1.6, -1.3, 0.3, 2.6), (1.3, -1.3, 0.3, 2.6)):
        qs += fe.caja_mundo(x + a, 0.3, z + b, w, 0.22, d, 'oro_bloque')
    fm.dibujar(lz, cam, qs, fe.LUCES, fe.AMB, niebla, 1.2, fase)
    g = math.atan2(hacia[1] - z, hacia[0] - x)
    dirx, dirz = math.cos(g), math.sin(g)
    s = math.tan(math.radians(inclina))
    P = []
    for (u, v) in ((-1.3, -1.3), (1.3, -1.3), (1.3, 1.3), (-1.3, 1.3)):
        h = 0.42 - (u * dirx + v * dirz) * s * 0.5
        P.append((x + u, h, z + v))
    UV = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], ESPEJO, np.ones(3) * 0.95, ESPEJO, niebla, brillo=0.35)
    return np.array([x, 0.45, z])


def flechas(img, cam, a, b, ts=(0.38, 0.62), tam=16, color=ORO_CLARO):
    """Unos angulos (>) sobre la foto a lo largo de a -> b: hacia donde va el rayo."""
    sa, sb = np.array(cam.proyectar(a)[:2]) / SS, np.array(cam.proyectar(b)[:2]) / SS
    d = sb - sa
    d /= np.linalg.norm(d) + 1e-9
    n = np.array([-d[1], d[0]])
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    for t in ts:
        c = sa + (sb - sa) * t
        pts = [tuple(c - d * tam + n * tam), tuple(c), tuple(c - d * tam - n * tam)]
        dc.line(pts, fill=(*SOMBRA, 170), width=9, joint='curve')
        dc.line(pts, fill=(*color, 255), width=4, joint='curve')
    img.alpha_composite(capa)


def espejos(W=1600, H=900, fase=3):
    cam = vr.Camara(ojo=(-18.0, 8.5, -26.0), objetivo=(0.0, 9.0, 2.5), fov=64, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    nov = (0.0, 4.0)
    sitios = [(-9.5, -2.5), (-1.5, -8.5), (8.5, -4.5)]
    centros = []
    for (x, z) in sitios:
        centros.append(losa_espejo(lz, cam, x, z, nov, niebla, fase))
        jugador(lz, cam, x, z, nov, QUIETO, y=0.45, niebla=niebla)
    p = pose('ALZA_SOL')
    M = caballero(lz, cam, nov[0], nov[1], fe.guinada_hacia(*nov, -3.0, -10.0), p, fase, niebla)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase)
    punta = fe.mundo_de(M, V, p, 'espada', (0, fm.PUNTA_ESPADA, 0))
    base = fe.mundo_de(M, V, p, 'espada', (0, 26, 0))
    pecho = fe.mundo_de(M, V, p, 'torso', (0, -34, -16))
    eje = (punta - base) / np.linalg.norm(punta - base)
    sol = punta + eje * 2.6
    # la hoja carga: el haz de la punta al sol
    fe.estela(lz, cam, [base + (sol - base) * t for t in np.linspace(0.3, 1, 8)], 0.35, fase, 0.8)
    fe.sol_mini(lz, cam, sol, 1.8, fase, 9, 1.0)
    for c in centros:
        # el rayo que baja del sol al espejo (fino) y el que rebota a su pecho (gordo)
        fe.estela(lz, cam, [sol + (c - sol) * t for t in np.linspace(0, 1, 14)], 0.13, fase, 0.5)
        fe.estela(lz, cam, [c + (pecho - c) * t for t in np.linspace(0, 1, 14)], lambda t: 0.3 + 0.25 * t, fase, 1.0)
        fe.brillo_en(lz, cam, c + np.array([0, 0.3, 0]), 1.6, nm._hex(fm.FASE[fase][1]), 0.6)
    fe.brillo_en(lz, cam, pecho, 3.4, nm._hex(fm.FASE[fase][1]), 0.8)
    fe.explosion(lz, cam, pecho - np.array([0, 1.2, 0]), 1.6, fase, 4, lava=False, k=0.6)
    img = acabar(lz, cam, W, H, fase, 83)
    for c in centros:
        flechas(img, cam, c, pecho)
    rotulo(img, cam, centros[0] + np.array([1.4, 0.4, -1.4]), 'ESPEJO', -40, 70, 42, ORO_CLARO)
    rotulo(img, cam, pecho, '¡SE LO DEVUELVEN!', 140, -60, 50, ORO_CLARO)
    guardar(img, 'espejos')


# ----------------------------------------------------------------------
#  4. Llama Viva
#
#  Novilis senala al que ha prendido: una llama grande lo envuelve y corre
#  hacia un companero para pasarsela (la linea de puntos); encima, la cuenta
#  atras. El aro rojo es lo que quemaria si explota; otro companero, mas lejos.
# ----------------------------------------------------------------------
def llama(W=1600, H=900, fase=2):
    cam = vr.Camara(ojo=(-10.5, 5.6, -19.5), objetivo=(1.5, 4.4, 1.0), fov=58, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(28, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    nov = (6.0, 13.0)
    prendido = np.array([-3.0, -7.5])
    amigo = np.array([3.4, -9.6])
    lejos = np.array([-9.5, 0.5])
    jugador(lz, cam, prendido[0], prendido[1], amigo, CORRER, niebla=niebla)
    jugador(lz, cam, amigo[0], amigo[1], prendido, PEDIR, niebla=niebla)
    jugador(lz, cam, lejos[0], lejos[1], prendido, MIRAR, niebla=niebla)
    p = pose('MARCA')
    M = caballero(lz, cam, nov[0], nov[1], fe.guinada_hacia(*nov, *prendido), p, fase, niebla)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase, k=0.8)
    # el aro de lo que quemaria al explotar y la linea hasta el companero
    aro_suelo(lz, cam, prendido[0], prendido[1], 4.0, ROJO, 0.75, 0.6, 0.04, 30, 30)
    linea_puntos(lz, cam, prendido + (amigo - prendido) * 0.1, amigo - (amigo - prendido) * 0.1, ORO_CLARO, paso=0.75,
                 largo=0.45, ancho=0.16, brillo=1.6)
    aro_suelo(lz, cam, amigo[0], amigo[1], 1.1, ORO, 0.8, 0.6, 0.12, 8, 50)
    # la llama que lo envuelve: el fuego de vanilla (el de quien arde), grande,
    # detras y a los lados (que se le vea el cuerpo), y bajo a sus pies
    c = np.array([prendido[0], 0.0, prendido[1]])
    lado = np.array([cam.r[0], 0, cam.r[2]]) / np.linalg.norm([cam.r[0], cam.r[2]])
    fondo = np.array([cam.f[0], 0, cam.f[2]]) / np.linalg.norm([cam.f[0], cam.f[2]])
    fuegos = sprites_fuego(fase)
    for k, (dl, df, ancho, alto, cual) in enumerate(((0.0, 0.7, 1.3, 4.2, 0), (-0.95, 0.45, 0.8, 3.1, 1), (0.95, 0.5, 0.8, 3.3, 0),
                                                     (-0.5, 0.95, 0.75, 4.6, 1), (0.55, 1.0, 0.7, 4.4, 1))):
        q = c + lado * dl + fondo * df
        llama_plana(lz, cam, q, ancho, alto, fuegos[cual], 0.75)
    for dl, alto, cual in ((-0.55, 1.2, 1), (0.1, 0.9, 0), (0.65, 1.3, 1)):
        q = c + lado * dl - fondo * 0.35
        llama_plana(lz, cam, q, 0.5, alto, fuegos[cual], 0.6, k=0.75)
    fe.brillo_en(lz, cam, c + np.array([0, 1.4, 0]) + fondo * 0.9, 2.8, BRASA, 0.3)
    img = acabar(lz, cam, W, H, fase, 84)
    cifra(img, cam, c + np.array([0, 5.3, 0]), '3', 120, (255, 214, 120))
    rotulo(img, cam, (amigo[0], 2.2, amigo[1]), '¡PÁSALA!', 30, -120, 50, ORO_CLARO)
    ang = math.radians(200)
    rotulo(img, cam, (prendido[0] + math.cos(ang) * 4.0, 0.1, prendido[1] + math.sin(ang) * 4.0), 'SI EXPLOTA, ARDE EL GRUPO',
           -20, 40, 30, (255, 160, 140))
    guardar(img, 'llama')


ESCENAS = {'duelo': duelo, 'armadura': armadura, 'espejos': espejos, 'llama': llama}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()

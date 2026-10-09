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

Segunda ficha (las cuatro de arriba no gustaron). La camara va mas cerca de
los jugadores; Novilis queda al fondo o cortado:

  sombra      Sombra del Escudo: un sol enorme y bajo a un lado; uno alza la
              Egida (un escudo grande, oscuro, con el canto de oro) y su sombra
              larga cubre a tres companeros; el que se queda fuera arde
  estandarte  Estandarte de Guerra: su estandarte de oro clavado, el circulo
              dorado alrededor con la barra de conquista al 60 %, tres
              jugadores dentro y Novilis al fondo lanzandoles un tajo de fuego
  escuderos   Escuderos de Fuego: Novilis de rodillas bajo una cupula de oro;
              tres escuderos de fuego (del tamano de un jugador) repartidos, cada
              uno unido a la cupula por un haz fino; los jugadores, por parejas
  sol_caido   Sol Caido: un sol pequeno rueda por el suelo dejando un rastro
              quemado; detras, los jugadores lo golpean (chispas) hacia las
              piernas de Novilis (la flecha de puntos); uno salta para esquivarlo

Tercera ficha (minijuegos, octubre de 2026: "a la gente le gustaron los
minijuegos de los jefes"). Camara cerca de los jugadores, como la segunda:

  choque   Choque de Espadas: por encima del hombro de un jugador, Novilis
           baja la espada en diagonal con la hoja encendida de oro (el
           destello); la punta choca contra el escudo alzado, chispas y
           "PARADA"; detras, otro con el escudo listo; el contador 2/3
  forja    Forja del Juramento: tres yunques de piedra con una hoja al rojo
           y un herrero con maza en cada uno; en el de cerca el aro de luz se
           ha cerrado sobre la hoja ("PERFECTO", con los aros por donde ha
           pasado); encima, los golpes buenos (4/6); Novilis de rodillas al
           fondo con la espada clavada
  justa    Justa del Sol: un jugador a lomos de un caballo de fuego (el de
           vanilla, oscuro con grietas de lava y la crin en llamas) con la
           lanza de luz; Novilis carga agachado tras un escudo grande con el
           sol en medio y la punta da en el emblema, que se enciende; el
           pasillo, dos lineas de fuego de vanilla; fuera, los demas
  brasas   Lluvia de Brasas: brasas doradas y rojas caen con estela, cada una
           con un hilo de luz a su marca del suelo; dos corren a la dorada,
           otro se aparta de una roja que estalla; Novilis ruge al fondo con
           su sol agitado; arriba, su barra del juego (las texturas de
           textures/gui) con la Corona del Sol al 60 %

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


# ======================================================================
#  Segunda ficha: ayudas comunes
# ======================================================================
def marco_camara(cam):
    """Los ejes de la camara sobre el suelo: delante (F) y a la derecha (R)."""
    F = np.array([cam.f[0], 0.0, cam.f[2]])
    R = np.array([cam.r[0], 0.0, cam.r[2]])
    return F / np.linalg.norm(F), R / np.linalg.norm(R)


def jugador_luz(lz, cam, x, z, mira, p=None, luz=1.0, tinte=(1.0, 1.0, 1.0), niebla=None, y=0.0, extra=0.0):
    """Un jugador con la luz que se pida (luz < 1: a la sombra)."""
    p = p or {}
    M = vr.T(0, y, 0) @ ne.jugador_a_mundo(x, z, fe.guinada_hacia(x, z, *mira) + extra)
    luces = [(d, tuple(c * t for c, t in zip(col, tinte)), k * luz, tipo) for d, col, k, tipo in fe.LUCES]
    amb = tuple(a * (0.6 + 0.4 * luz) * t for a, t in zip(fe.AMB, tinte))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), p, M), luces, amb, niebla)
    return M, p


def jugador_inclinado(lz, cam, pie, guinada, ladeo, p=None, niebla=None):
    """Un jugador en el aire, ladeado hacia un lado (el que salta para esquivar)."""
    M = vr.T(*pie) @ vr.Ry(math.radians(guinada)) @ vr.Rz(math.radians(ladeo)) @ vr.T(0, 1.5, 0) @ \
        np.diag([-1 / 16, -1 / 16, 1 / 16, 1])
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), p or {}, M), fe.LUCES, fe.AMB, niebla)
    return M


def modelo_en(x, y, z, guinada, inclina=0.0, escala=1.0):
    """De px de un modelo (16 = 1 bloque, Y hacia abajo, el frente en -Z) al mundo."""
    return vr.T(x, y, z) @ vr.Ry(math.radians(guinada)) @ vr.Rx(math.radians(inclina)) @ \
        np.diag([-escala / 16, -escala / 16, escala / 16, 1])


def punto_de(raiz, M, p, nodo, local=(0, 0, 0)):
    """Donde cae en el mundo un punto de una pieza de un modelo de nodos."""
    Mn = np.eye(4)
    for nombre, off, rot, _, _ in _ruta(raiz, nodo):
        ex = p.get(nombre, {})
        r = [rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        q = [off[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        Mn = Mn @ vr.T(*q) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R)
    return (M @ Mn @ np.array([*local, 1.0]))[:3]


def haz_oro(lz, cam, pts, ancho, k=1.0, color=ORO, claro=ORO_CLARO):
    """Un haz de luz dorada por una lista de puntos (el alma clara)."""
    tex = np.transpose(fe.tex_haz(claro, color, 32, 8), (1, 0, 2)).copy()
    fe.aditivo(lz, cam, fe.cinta3d(pts, ancho, cam), tex, k)


def curva(a, b, alto, n=16):
    """Un arco de a a b que sube 'alto' por el medio."""
    a, b = np.array(a, float), np.array(b, float)
    return [a + (b - a) * t + np.array([0, alto * math.sin(math.pi * t), 0]) for t in np.linspace(0, 1, n)]


def arde(lz, cam, pie, fase, escala=1.0, semilla=0):
    """Un jugador que arde: el fuego de vanilla detras y a los lados, y bajo a sus pies."""
    c = np.array(pie, float)
    lado = np.array([cam.r[0], 0, cam.r[2]]) / np.linalg.norm([cam.r[0], cam.r[2]])
    fondo = np.array([cam.f[0], 0, cam.f[2]]) / np.linalg.norm([cam.f[0], cam.f[2]])
    fuegos = sprites_fuego(fase)
    for dl, df, ancho, alto, cual in ((0.0, 0.5, 0.9, 2.9, 0), (-0.7, 0.35, 0.6, 2.3, 1), (0.7, 0.35, 0.6, 2.4, 0)):
        llama_plana(lz, cam, c + (lado * dl + fondo * df) * escala, ancho * escala, alto * escala, fuegos[cual], 0.7)
    for dl, alto, cual in ((-0.4, 0.9, 1), (0.45, 1.0, 0)):
        llama_plana(lz, cam, c + (lado * dl - fondo * 0.3) * escala, 0.4 * escala, alto * escala, fuegos[cual], 0.55, k=0.7)
    fe.brillo_en(lz, cam, c + np.array([0, 1.1, 0]) + fondo * 0.6, 2.2 * escala, BRASA, 0.35)
    r = random.Random(semilla)
    for _ in range(8):
        q = c + np.array([r.uniform(-0.8, 0.8), r.uniform(2.0, 3.6), r.uniform(-0.8, 0.8)]) * escala
        fe.brillo_en(lz, cam, q, 0.12, BRASA, 0.9)


def tex_sombra(w=64, h=64):
    """La sombra en el suelo (u a lo largo, v de lado a lado): oscura, con los
    bordes blandos y la punta que se apaga."""
    u = np.linspace(0, 1, w)[None, :] * np.ones((h, 1))
    v = np.abs(np.linspace(-1, 1, h))[:, None] * np.ones((1, w))
    a = np.clip((1 - v) / 0.18, 0, 1) * np.clip((1 - u) / 0.25, 0, 1) * np.clip(u / 0.04, 0, 1)
    col = np.ones((h, w, 3)) * np.array([10, 8, 22])
    return _rgba(col, a)


def tex_chispas(n=128, semilla=6, color=ORO):
    """El chispazo de un golpe: rayos finos que salen del centro, el alma blanca."""
    r = random.Random(semilla)
    im = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(im)
    c = n / 2
    for k in range(16):
        a = TAU * k / 16 + r.uniform(-0.15, 0.15)
        l = n * r.uniform(0.24, 0.48)
        d.line([(c + math.cos(a) * n * 0.07, c + math.sin(a) * n * 0.07), (c + math.cos(a) * l, c + math.sin(a) * l)],
               fill=255, width=max(2, n // 42))
    for _ in range(10):
        a, l = r.uniform(0, TAU), n * r.uniform(0.2, 0.46)
        q = (c + math.cos(a) * l, c + math.sin(a) * l)
        d.ellipse((q[0] - 2, q[1] - 2, q[0] + 2, q[1] + 2), fill=255)
    d.ellipse((c - n * 0.09, c - n * 0.09, c + n * 0.09, c + n * 0.09), fill=255)
    m = np.array(im.filter(ImageFilter.GaussianBlur(0.8))).astype(float) / 255
    halo = np.array(im.filter(ImageFilter.GaussianBlur(n / 14))).astype(float) / 255
    yy, xx = np.mgrid[0:n, 0:n]
    k = np.clip(1 - np.hypot(xx - c, yy - c) / (n * 0.3), 0, 1)[..., None]
    col = np.array(color) * (1 - k) + np.array([255, 255, 250]) * k
    return _rgba(col, np.clip(m + halo * 0.6, 0, 1))


def tex_quemado(w=64, h=32, semilla=7):
    """El rastro quemado (u a lo largo, v de lado a lado): costra negra con bordes rotos."""
    r = np.random.RandomState(semilla)
    v = np.abs(np.linspace(-1, 1, h))[:, None] * np.ones((1, w))
    borde = 0.75 + 0.25 * np.repeat(r.rand(1, w // 4 + 1), 4, axis=1)[:, :w]
    a = np.clip((borde - v) / 0.2, 0, 1) * (0.8 + 0.2 * r.rand(h, w))
    col = np.ones((h, w, 3)) * np.array([22, 12, 10]) + r.rand(h, w, 1) * 14
    return _rgba(col, a)


def tex_ascuas(w=64, h=32, semilla=8):
    """Ascuas sueltas que brillan sobre el rastro quemado."""
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    for _ in range(int(w * h * 0.05)):
        x, y = r.randrange(w), r.randrange(int(h * 0.15), int(h * 0.85))
        t[y, x] = (255, r.choice((120, 160, 200)), 40, r.randint(150, 255))
    return t


def tex_banda(color, w=8, h=32, k_alma=0.35):
    """Una banda plana de luz (para la barra de conquista): u de lado a lado."""
    t = np.zeros((h, w, 4), np.uint8)
    claro = fe._mez(color, (255, 255, 255), 0.55)
    for y in range(h):
        v = abs(y - (h - 1) / 2) / ((h - 1) / 2)
        c = claro if v < k_alma else fe._mez(claro, color, (v - k_alma) / (1 - k_alma))
        t[y, :] = (*c, int(255 * min(1.0, (1 - v) / 0.25)))
    return np.transpose(t, (1, 0, 2)).copy()


_GLOW = {}


def tex_halo(color, n=256):
    """Un resplandor blando, sin el nucleo duro de tex_disco (que a lo grande se ve a escalones)."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    k = np.clip(1 - d / 0.45, 0, 1)[..., None]
    col = np.array(color) * (1 - k) + np.array(fe._mez(color, (255, 255, 255), 0.6)) * k
    return _rgba(col, np.clip(1 - d, 0, 1) ** 2.0)


def resplandor(lz, cam, p, tam, color, k=1.0):
    """Como fe.brillo_en, pero blando y con la textura fina (para los resplandores grandes)."""
    if color not in _GLOW:
        _GLOW[color] = tex_halo(color)
    fe.aditivo(lz, cam, [fe.billboard(p, tam, cam)], _GLOW[color], k)


def _sup_fuego(semilla=51):
    """La superficie del Sol Caido: granulos de fuego naranja, amarillo y rojo (mas
    saturada que la del sol de cada fase, para que no se queme a blanco)."""
    r = random.Random(semilla)
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            t[y, x] = (*r.choice(((255, 196, 70), (255, 150, 34), (255, 150, 34), (240, 96, 24), (255, 226, 130))), 255)
    return t


fm.registrar('sol_caido', _sup_fuego(), _sup_fuego(), pleno=True)


def bola_de_fuego(lz, cam, p, R, semilla=3, brillo=0.3):
    """El Sol Caido: una bola de cubos de fuego, la corona naranja y lenguas
    alrededor (como fe.sol_mini, pero con su color y menos brillo)."""
    r = random.Random(semilla)
    p = np.array(p, float)
    for (w, h, d) in ((0.78, 0.48, 0.48), (0.48, 0.78, 0.48), (0.48, 0.48, 0.78),
                      (0.68, 0.68, 0.48), (0.68, 0.48, 0.68), (0.48, 0.68, 0.68)):
        fm.dibujar(lz, cam, fe.caja_mundo(p[0] - R * w, p[1] - R * h, p[2] - R * d, 2 * R * w, 2 * R * h, 2 * R * d, 'sol_caido'),
                   fe.LUCES, fe.AMB, None, brillo, 1)
    for i in range(16):
        a = TAU * i / 16 + r.uniform(-0.1, 0.1)
        dirv = cam.r * math.cos(a) + cam.u * math.sin(a)
        fe.aditivo(lz, cam, [fe.billboard(p + dirv * R * 1.05, R * 0.34, cam, a - math.pi / 2, alto=R * 0.6)],
                   fe.tex_llama_sprite(1, i), 0.85)


def disco_sol(lz, cam, p, R, brillo=0.6):
    """El disco del sol, encendido y con el borde neto, de cara a la camara (lo
    tapa lo que tenga delante, como el borde del suelo)."""
    n = 256
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    k1 = np.clip(d / 0.75, 0, 1)[..., None]
    col = np.array([255, 250, 228]) * (1 - k1) + np.array([255, 206, 96]) * k1
    k2 = np.clip((d - 0.75) / 0.25, 0, 1)[..., None]
    col = col * (1 - k2) + np.array([255, 140, 44]) * k2
    tex = _rgba(col, np.clip((1 - d) / 0.015, 0, 1))
    P, UV = fe.billboard(p, R, cam)
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), tex, None, brillo=brillo)


def estelas(img, cam, desde, atras, n=4, color=BLANCO):
    """Rayas de movimiento sobre la foto, detras de lo que se mueve (de 'desde' hacia 'atras')."""
    a = np.array(cam.proyectar(desde)[:2]) / SS
    b = np.array(cam.proyectar(atras)[:2]) / SS
    d = b - a
    L = np.linalg.norm(d)
    d /= L
    nrm = np.array([-d[1], d[0]])
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    for i in range(n):
        o = (i - (n - 1) / 2) * 18
        p0 = a + d * L * 0.4 + nrm * o
        p1 = a + d * L * (0.85 + 0.2 * (i % 2)) + nrm * o
        dc.line([tuple(p0), tuple(p1)], fill=(*SOMBRA, 150), width=7)
        dc.line([tuple(p0), tuple(p1)], fill=(*color, 235), width=3)
    img.alpha_composite(capa)


def tex_luz_suelo(color, n=128, dura=0.6):
    """Una mancha de luz en el suelo: el centro fuerte y el borde que se apaga."""
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    return _rgba(np.ones((n, n, 3)) * np.array(color), np.clip(1 - d, 0, 1) ** dura)


def capa_suelo(lz, cam, cx, cz, R, tex, k, paso=2.0, y=0.05):
    """Una capa translucida sobre el suelo, en losas pequenas (las que caen detras
    de la camara se saltan), con la textura extendida por todo el cuadrado."""
    qs = []
    n = int(math.ceil(2 * R / paso))
    for i in range(n):
        for j in range(n):
            x0, z0 = cx - R + i * paso, cz - R + j * paso
            x1, z1 = x0 + paso, z0 + paso
            if min(cam.proyectar((x, y, z))[2] for x in (x0, x1) for z in (z0, z1)) < 0.3:
                continue
            u0, v0, u1, v1 = i / n, j / n, (i + 1) / n, (j + 1) / n
            qs.append(([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]))
    fe.trans(lz, cam, qs, tex, k, None, 0.0, 1.0)


def con_sol_grande(radio):
    """Hace que la composicion pinte el sol del cielo con otro radio; devuelve
    la funcion de antes, para dejarla como estaba."""
    orig = fe.sol_en_cielo
    fe.sol_en_cielo = lambda arr, cam, W, H, fase=1, pos=None, radio_=5.0: orig(arr, cam, W, H, fase, pos, radio)
    return orig


def calima(img, cam, p, radio_mundo, amp=4.0, semilla=0.0, hueco=0.0):
    """La calima del calor: ondula la foto ya compuesta alrededor de p (sin
    tocar el circulo de dentro, de radio 'hueco' en bloques)."""
    sx, sy, z = cam.proyectar(p)
    sx, sy = sx / SS, sy / SS
    rp = cam.foco / SS * radio_mundo / z
    rh = cam.foco / SS * hueco / z
    arr = np.array(img)
    H, W = arr.shape[:2]
    x0, x1 = max(0, int(sx - rp)), min(W, int(sx + rp))
    y0, y1 = max(0, int(sy - rp)), min(H, int(sy + rp))
    if x0 >= x1 or y0 >= y1:
        return img
    yy, xx = np.mgrid[y0:y1, x0:x1]
    r = np.hypot(xx - sx, yy - sy)
    peso = np.clip(1 - r / rp, 0, 1) ** 0.7 * np.clip((r - rh) / max(1.0, rp * 0.15), 0, 1)
    dx = amp * peso * np.sin(yy * 0.23 + semilla)
    dy = amp * 0.5 * peso * np.sin(xx * 0.19 + semilla * 2)
    fx = np.clip((xx + dx).round().astype(int), 0, W - 1)
    fy = np.clip((yy + dy).round().astype(int), 0, H - 1)
    out = arr.copy()
    out[y0:y1, x0:x1] = arr[fy, fx]
    return Image.fromarray(out)


SOSTENER = {'bi': {'rot': (-150, 0, -14)}, 'bd': {'rot': (-150, 0, 14)}, 'pi': {'rot': (-22, 0, 0)}, 'pd': {'rot': (20, 0, 0)}}
GUARDIA = {'bd': {'rot': (-70, -20, 0)}, 'bi': {'rot': (-40, 0, -14)}, 'pi': {'rot': (-16, 0, -4)}, 'pd': {'rot': (14, 0, 4)}}
GOLPE = {'bd': {'rot': (-115, -25, 0)}, 'bi': {'rot': (30, 0, -10)}, 'pi': {'rot': (-28, 0, 0)}, 'pd': {'rot': (24, 0, 0)}}
SALTO = {'pi': {'rot': (-45, 0, 0)}, 'pd': {'rot': (30, 0, 0)}, 'bi': {'rot': (-30, 0, -50)}, 'bd': {'rot': (-20, 0, 60)}}


# ======================================================================
#  5. Sombra del Escudo
#
#  Un sol enorme y bajo, al fondo a la izquierda. Uno alza la Egida (un escudo
#  grande, oscuro, con el canto de oro y el sol en medio) de cara al sol y su
#  sombra larga cae hacia delante; dentro, tres companeros a la sombra (con
#  menos luz). El que se ha quedado fuera, al sol, arde.
# ======================================================================
def egida_modelo():
    """La Egida, en px (16 = 1 bloque): 2,6 x 3,2 bloques, el centro en el origen."""
    cajas = [((-21, -26, -1.2, 42, 52, 2.4), 'placa_osc')]
    for (x, y, w, h) in ((-22.5, -27.5, 45, 3.5), (-22.5, 24, 45, 3.5), (-22.5, -27.5, 3.5, 55), (19, -27.5, 3.5, 55)):
        cajas.append(((x, y, -2.0, w, h, 4.0), 'oro'))
    for z in (-1.9, 1.3):                        # el sol, por las dos caras
        cajas += [((-5, -5, z, 10, 10, 0.6), 'nucleo'), ((-7, -1.2, z + 0.1, 14, 2.4, 0.4), 'oro'),
                  ((-1.2, -7, z + 0.1, 2.4, 14, 0.4), 'oro')]
        for a in range(8):
            ang = TAU * a / 8 + TAU / 16
            cx, cy = math.cos(ang) * 10.5, math.sin(ang) * 10.5
            cajas.append(((cx - 1.4, cy - 1.4, z + 0.1, 2.8, 2.8, 0.4), 'oro'))
    return nm.nodo('egida', (0, 0, 0), (0, 0, 0), cajas)


def sombra(W=1600, H=900, fase=2):
    cam = vr.Camara(ojo=(-17.0, 6.6, -23.0), objetivo=(-8.0, 2.7, -7.5), fov=50, ancho=W * SS, alto=H * SS)
    F, R = marco_camara(cam)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    viejo = fe.SOL
    fe.SOL = fe.sol_en_pantalla(cam, 0.15, 0.24, 140.0)
    B = np.array([-8.5, 0.0, -7.0])              # el de la Egida
    s = fe.SOL - B
    s[1] = 0.0
    s /= np.linalg.norm(s)                       # hacia el sol, por el suelo
    lat = np.array([-s[2], 0.0, s[0]])
    # Novilis al fondo, a la derecha, con la espada alzada al cielo
    nov = B + F * 46 + R * 17
    p = pose('CASTIGO_ALZA')
    M = caballero(lz, cam, nov[0], nov[2], fe.guinada_hacia(nov[0], nov[2], B[0], B[2]), p, fase, niebla)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase, k=0.7)
    # la sombra: de la Egida hacia el lado contrario al sol
    L, w0, w1 = 12.5, 1.5, 3.2
    eje = -s

    def en_sombra(t, d):
        return B + eje * t + lat * d * (w0 + (w1 - w0) * t / L)

    dentro = [en_sombra(4.2, 0.3), en_sombra(7.0, -0.5), en_sombra(9.6, 0.4)]
    # el portador, de cara al sol, con los brazos arriba
    jugador(lz, cam, B[0], B[2], (B[0] + s[0], B[2] + s[2]), SOSTENER, niebla=niebla)
    C = B + s * 0.95 + np.array([0, 2.5, 0])
    fm.dibujar(lz, cam, nm.quads(egida_modelo(), {}, modelo_en(C[0], C[1], C[2], fe.guinada_hacia(C[0], C[2], C[0] + s[0], C[2] + s[2]), 10)),
               fe.LUCES, fe.AMB, niebla, 1.2, fase)
    # los de la sombra: con poca luz y fria
    for i, q in enumerate(dentro):
        jugador_luz(lz, cam, q[0], q[2], (B[0], B[2]), (MIRAR, QUIETO, MIRAR)[i], luz=0.25, tinte=(0.72, 0.8, 1.0),
                    niebla=niebla, extra=(0, 25, -20)[i])
    # el de fuera, al sol, que corre hacia la sombra mientras arde
    fuera = B - R * 4.6 - F * 3.0
    meta = en_sombra(5.5, -0.3)
    jugador(lz, cam, fuera[0], fuera[2], (meta[0], meta[2]), CORRER, niebla=niebla)
    # la luz del sol que abrasa el suelo, y encima la sombra
    centro = B + eje * 4.0
    capa_suelo(lz, cam, centro[0], centro[2], 20.0, tex_luz_suelo((255, 176, 96), 128, 0.5), 0.42)
    N0, F0 = B + eje * 0.2, B + eje * L
    P = [tuple(N0 - lat * w0 + [0, 0.07, 0]), tuple(N0 + lat * w0 + [0, 0.07, 0]),
         tuple(F0 + lat * w1 + [0, 0.07, 0]), tuple(F0 - lat * w1 + [0, 0.07, 0])]
    fe.trans(lz, cam, [(P, [(0, 0), (0, 1), (1, 1), (1, 0)])], tex_sombra(), 0.82, None, 0.0, 1.0)
    # el sol pega en la cara de la Egida: su canto brilla por detras
    resplandor(lz, cam, C + s * 0.9, 3.6, ORO, 0.6)
    arde(lz, cam, fuera, fase, 1.0, 3)
    # el resplandor del sol enorme del cielo
    lejos = cam.ojo + (fe.SOL - cam.ojo) * 0.9
    disco_sol(lz, cam, fe.SOL, 15.5, 0.55)
    resplandor(lz, cam, lejos, 60.0, BRASA, 0.3)
    resplandor(lz, cam, lejos, 26.0, ORO_CLARO, 0.25)
    antes = con_sol_grande(17.0)
    img = acabar(lz, cam, W, H, fase, 91, sol=True)
    fe.sol_en_cielo = antes
    img = calima(img, cam, fuera + np.array([0, 1.2, 0]), 2.2, 3.0, 1.0).convert('RGBA')
    fe.SOL = viejo
    rotulo(img, cam, C + np.array([0, 1.7, 0]), 'LA ÉGIDA', 40, -120, 50, ORO_CLARO)
    rotulo(img, cam, en_sombra(8.2, 0.0) + np.array([0, 0.1, 0]), '¡A SU SOMBRA!', 150, 40, 52, (200, 214, 255))
    rotulo(img, cam, fuera + np.array([0, 2.6, 0]), 'FUERA SE ARDE', -50, -100, 44, (255, 170, 120))
    guardar(img, 'sombra')


# ======================================================================
#  6. Estandarte de Guerra
#
#  Su estandarte de oro clavado en la arena (el asta, el travesano y el pano
#  carmesi con el sol bordado). Alrededor, el circulo dorado y la barra de
#  conquista al 60 %. Tres jugadores dentro, juntos; al fondo, Novilis les
#  lanza un barrido de fuego.
# ======================================================================
def estandarte_modelo():
    """El estandarte, en px (16 = 1 bloque), el pie del asta en el origen y el pano
    hacia -Z (de cara a quien mira)."""
    n = nm.nodo
    alto = 150                                    # el asta: 9,4 bloques
    asta = [((-6, -4, -6, 12, 4, 12), 'basalto_j'), ((-4.5, -7, -4.5, 9, 3, 9), 'oro'),
            ((-2.2, -alto, -2.2, 4.4, alto - 7, 4.4), 'oro'),
            ((-3.0, -alto * 0.55, -3.0, 6.0, 2.5, 6.0), 'oro'),
            ((-36, -alto + 6, -2.6, 72, 4, 4), 'oro'),                       # el travesano
            ((-38.5, -alto + 4, -3.2, 5, 8, 5.2), 'oro'), ((33.5, -alto + 4, -3.2, 5, 8, 5.2), 'oro'),
            ((-4, -alto - 8, -4, 8, 8, 8), 'nucleo')]                         # el sol de la punta
    # el pano: tres tiras con un poco de vuelo y la cola en dos picos
    top = -alto + 10
    pano = []
    for i, (x0, dz) in enumerate(((-32, -0.4), (-10.7, -1.4), (10.7, -0.6))):
        pano.append(((x0, top, -4.2 + dz, 21.4, 78, 1.0), 'capa'))
    for (x, w, h) in ((-32, 21.4, 16), (10.7, 21.4, 16), (-32, 10, 24), (22, 10, 24)):
        pano.append(((x, top + 78, -4.4, w, h - 8 if w > 15 else h, 1.0), 'capa'))
    # el ribete de oro y el sol bordado
    pano += [((-33, top, -5.6, 66, 3, 1.0), 'oro'), ((-33, top, -5.6, 3, 92, 1.0), 'oro'), ((30, top, -5.6, 3, 92, 1.0), 'oro'),
             ((-33, top + 76, -5.6, 66, 2.4, 1.0), 'oro')]
    cy = top + 38
    pano += [((-9, cy - 9, -5.9, 18, 18, 1.0), 'nucleo'), ((-12, cy - 5, -5.7, 24, 10, 0.8), 'oro'),
             ((-5, cy - 12, -5.7, 10, 24, 0.8), 'oro')]
    for a in range(12):
        ang = TAU * a / 12
        L = 21 if a % 2 == 0 else 17
        cx, cyy = math.cos(ang) * L, cy + math.sin(ang) * L
        pano.append(((cx - 2, cyy - 2, -5.7, 4, 4, 0.8), 'oro'))
    return n('estandarte', (0, 0, 0), (0, 0, 0), asta + pano)


def estandarte(W=1600, H=900, fase=2):
    E = np.array([-3.0, 0.0, -8.5])              # el estandarte (lejos del centro del altar)
    cam = vr.Camara(ojo=tuple(E + [-6.0, 8.5, -15.5]), objetivo=tuple(E + [1.0, 3.2, 1.0]), fov=54, ancho=W * SS, alto=H * SS)
    F, R = marco_camara(cam)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    RC = 6.0                                      # el radio del circulo
    nov = E + F * 25.0 + R * 13.5
    # Novilis al fondo, a la derecha, lanzando el barrido hacia ellos
    p = pose('BARRIDO')
    g = fe.guinada_hacia(nov[0], nov[2], E[0], E[2])
    M = caballero(lz, cam, nov[0], nov[2], g + 25, p, fase, niebla)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase, k=0.8)
    # el estandarte, el pano de cara a la camara
    fm.dibujar(lz, cam, nm.quads(estandarte_modelo(), {}, modelo_en(E[0], 0, E[2], fe.guinada_hacia(E[0], E[2], cam.ojo[0], cam.ojo[2]))),
               fe.LUCES, fe.AMB, niebla, 1.3, fase)
    # los tres de dentro, juntos y de cara a el
    dentro = [E - R * 2.6 - F * 2.0, E + R * 0.4 - F * 3.4, E + R * 2.8 - F * 1.4]
    poses = [ALZAR, GUARDIA, ALZAR]
    for i, q in enumerate(dentro):
        Mj, pj = jugador(lz, cam, q[0], q[2], (nov[0], nov[2]), poses[i], niebla=niebla)
        en_mano(lz, cam, Mj, pj, 'espada', 0.42, giro=math.radians(40 if poses[i] is ALZAR else 10), luz=1.1)
    # el circulo dorado y la barra de conquista (60 %): lo lleno, claro; lo que falta, apagado
    aro_suelo(lz, cam, E[0], E[2], RC, ORO, 0.85, 0.6, 0.03, 0, 40)
    a_cam = math.atan2(-F[2], -F[0])              # el punto del circulo mas cerca de la camara
    a0 = a_cam - math.radians(66)                 # la punta de la barra: delante, a la derecha
    a1 = a0 + 0.60 * TAU                          # y empieza detras, a la izquierda
    fe.trans(lz, cam, fe.banda_horizontal(E[0], 0.09, E[2], RC + 0.3, RC + 1.0, a1, a0 + TAU, 50),
             tex_banda((70, 40, 24)), 0.85, None, 0.0, 1.0)
    fe.aditivo(lz, cam, fe.banda_horizontal(E[0], 0.11, E[2], RC + 0.3, RC + 1.0, a0, a1, 90), tex_banda(ORO), 1.5)
    cabeza = np.array([E[0] + math.cos(a0) * (RC + 0.65), 0.15, E[2] + math.sin(a0) * (RC + 0.65)])
    resplandor(lz, cam, cabeza + np.array([0, 0.25, 0]), 1.3, ORO_CLARO, 1.0)
    # el brillo del estandarte (su bendicion)
    resplandor(lz, cam, E + np.array([0, 9.8, 0]), 1.8, ORO_CLARO, 0.5)
    fe.llamas_en(lz, cam, E + np.array([0, 9.9, 0]), 0.9, fase, 4, 21, 0.9)
    # el ataque: un tajo de fuego grande que vuela bajo hacia el circulo, con su estela
    nuc, pri, hon = (nm._hex(c) for c in fm.FASE[1])
    hacia = E - nov
    hacia[1] = 0
    hacia /= np.linalg.norm(hacia)
    tex_t = fe.tex_media_luna(nuc, pri, 128)
    # el tajo llega por la derecha, a la altura del pecho, con la panza hacia ellos
    tajo = E + R * (RC + 1.6) - F * 0.6 + np.array([0, 1.7, 0])
    va = (np.mean(dentro, axis=0) - tajo)
    va[1] = 0
    va /= np.linalg.norm(va)
    for j, (atras, tam, k) in enumerate(((4.6, 1.6, 0.22), (2.3, 2.0, 0.45), (0.0, 2.5, 1.1))):
        fe.aditivo(lz, cam, [fe.billboard(tajo - va * atras, tam * 0.5, cam, math.pi / 2, alto=tam)], tex_t, k)
    fe.llamas_en(lz, cam, tajo - np.array([0, 0.7, 0]), 1.0, 1, 5, 61, 1.0)
    fe.trans(lz, cam, fe.suelo_cuad(tajo[0], tajo[2], 2.2, 0.08), tex_luz_suelo(BRASA, 64, 1.2), 0.5, None, 0.4)
    espada = fe.mundo_de(M, V, p, 'espada', (0, 50, 0))
    haz_oro(lz, cam, curva(espada, tajo - va * 4.6, 1.5, 14), lambda t: 0.08 + 0.3 * t, 0.35, BRASA, ORO_CLARO)
    img = acabar(lz, cam, W, H, fase, 92)
    rotulo(img, cam, E + np.array([0, 9.0, 0]) - R * 2.3, 'SU ESTANDARTE', -40, -30, 48, ORO_CLARO)
    rotulo(img, cam, cabeza, 'CONQUISTANDO 60%', 70, 30, 46, ORO_CLARO)
    rotulo(img, cam, dentro[0] + np.array([0, 2.3, 0]), '¡AGUANTAD JUNTOS!', -60, -40, 50, BLANCO)
    guardar(img, 'estandarte')


# ======================================================================
#  7. Escuderos de Fuego
#
#  Novilis de rodillas (con la espada clavada) bajo una cupula de oro. Tres
#  escuderos de fuego (del tamano de un jugador: armadura oscura, costuras de
#  lava, el visor encendido y una espada pequena de fuego), repartidos, cada uno
#  unido a la cupula por un haz fino de oro. Los jugadores, por parejas.
# ======================================================================
def escudero_modelo():
    """Un escudero de fuego, en px como el jugador (las mismas piezas, para usar
    sus poses): armadura oscura con costuras de lava y una espada de fuego."""
    n = nm.nodo
    espada = n('espada_e', (0, 10.5, -0.5), (0, 0, 0), [
        ((-0.7, -0.7, -1.6, 1.4, 1.4, 3.4), 'cuero'), ((-2.8, -0.9, -2.6, 5.6, 1.8, 1.2), 'oro'),
        ((-0.8, -0.8, -15, 1.6, 1.6, 12.4), 'lava')])

    def brazo(nombre, x, hijos=()):
        return n(nombre, (x, 2, 0), (0, 0, 0), [((-2.2, -2, -2.2, 4.4, 12, 4.4), 'placa_osc'),
                                               ((-3.0, -2.9, -3.0, 6.0, 4.6, 6.0), 'placa'),
                                               ((-2.4, 6.5, -2.4, 4.8, 0.9, 4.8), 'lava')], hijos)

    def pierna(nombre, x):
        return n(nombre, (x, 12, 0), (0, 0, 0), [((-2.2, 0, -2.2, 4.4, 12, 4.4), 'placa_osc'),
                                                ((-2.4, 5, -2.4, 4.8, 0.9, 4.8), 'lava'),
                                                ((-2.4, 9, -2.8, 4.8, 3, 5.2), 'cota')])

    return n('raiz', (0, 0, 0), (0, 0, 0), [], [
        n('cuerpo', (0, 0, 0), (0, 0, 0), [
            ((-4.4, 0, -2.5, 8.8, 12, 5.0), 'placa_osc'),
            ((-4.6, 3.6, -2.8, 9.2, 0.9, 5.6), 'lava'), ((-0.45, 0, -2.75, 0.9, 10, 0.5), 'lava'),
            ((-4.7, 10, -2.9, 9.4, 1.7, 5.8), 'oro'), ((-1.6, 5.6, -3.0, 3.2, 3.2, 0.6), 'nucleo')], [
            n('cabeza', (0, 0, 0), (0, 0, 0), [
                ((-4.4, -8.8, -4.4, 8.8, 8.8, 8.8), 'placa'),
                ((-3.4, -5.5, -4.75, 6.8, 1.4, 0.6), 'nucleo'),          # el visor
                ((-0.6, -4.0, -4.75, 1.2, 3.6, 0.6), 'lava'),
                ((-1.1, -12.5, -3.5, 2.2, 3.8, 7.0), 'lava')]),          # la cresta
            brazo('bi', 6), brazo('bd', -6, [espada])]),
        pierna('pi', 2), pierna('pd', -2)])


ESCUDERO = escudero_modelo()


def escudero(lz, cam, x, z, mira, p, fase, niebla, escala=1.12):
    """Dibuja un escudero en (x, z) mirando a 'mira'; devuelve la punta y el pecho."""
    g = fe.guinada_hacia(x, z, *mira)
    M = vr.T(x, 0, z) @ vr.Ry(math.radians(g)) @ vr.T(0, 1.5 * escala, 0) @ np.diag([-escala / 16, -escala / 16, escala / 16, 1])
    fm.dibujar(lz, cam, nm.quads(ESCUDERO, p, M), fe.LUCES, fe.AMB, niebla, 1.3, fase)
    for i, t in enumerate((-5, -9, -13)):
        fe.llamas_en(lz, cam, punto_de(ESCUDERO, M, p, 'espada_e', (0, 0, t)), 0.32, fase, 2, 70 + i, 0.9)
    fe.llamas_en(lz, cam, punto_de(ESCUDERO, M, p, 'cabeza', (0, -12.5, 0)), 0.42, fase, 3, 80, 0.8)
    fe.brillo_en(lz, cam, punto_de(ESCUDERO, M, p, 'cuerpo', (0, 6, -3)), 0.9, BRASA, 0.4)
    return punto_de(ESCUDERO, M, p, 'cuerpo', (0, 4, 0)), punto_de(ESCUDERO, M, p, 'cabeza', (0, -10, 0))


ESC_ATACA = {'bd': {'rot': (-140, 10, 0)}, 'bi': {'rot': (-20, 0, -12)}, 'pi': {'rot': (-24, 0, 0)}, 'pd': {'rot': (22, 0, 0)}}
ESC_TAJO = {'bd': {'rot': (-70, -40, 0)}, 'bi': {'rot': (20, 0, -10)}, 'pi': {'rot': (-18, 0, 0)}, 'pd': {'rot': (26, 0, 0)}}


def escuderos(W=1600, H=900, fase=3):
    # cerca de la pelea de un escudero (a la izquierda); los otros dos y Novilis, detras
    cam = vr.Camara(ojo=(-9.5, 4.6, -17.0), objetivo=(0.0, 3.6, 2.0), fov=56, ancho=W * SS, alto=H * SS)
    F, R = marco_camara(cam)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    N = np.array([2.5, 0.0, 9.0])
    p = pose('CASTIGO_CLAVA')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], cam.ojo[0], cam.ojo[2]), p, fase, niebla, con_espada=False)
    fe.espada_clavada(lz, cam, M, 0, -30, V, fase, niebla, inclina=0.0)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase, espada=False, k=0.6)
    # los escuderos (de cara a la camara) y su pareja de jugadores delante de cada uno
    sitios = [np.array([-5.6, 0.0, -6.5]) - R * 3.2 + F * 0.8, np.array([6.0, 0.0, -3.0]), np.array([-10.0, 0.0, 3.5])]
    parejas = [((-1.9, -2.1), (1.9, -1.2)), ((-2.0, -1.8), (1.9, -2.0)), ((-2.0, -1.8), (2.0, -1.4))]
    poses_e = [ESC_ATACA, ESC_TAJO, ESC_ATACA]
    tops = []
    for i, S in enumerate(sitios):
        q1 = S + R * parejas[i][0][0] + F * parejas[i][0][1]
        q2 = S + R * parejas[i][1][0] + F * parejas[i][1][1]
        objetivo = (q1 + q2) / 2
        pecho, cima = escudero(lz, cam, S[0], S[2], (objetivo[0], objetivo[2]), poses_e[i], 1, niebla)
        tops.append(cima)
        for j, q in enumerate((q1, q2)):
            pj = ALZAR if j == 0 else GOLPE
            Mj, pj = jugador(lz, cam, q[0], q[2], (S[0], S[2]), pj, niebla=niebla)
            en_mano(lz, cam, Mj, pj, 'espada', 0.38, giro=math.radians(40 if j == 0 else -20), luz=1.1)
    # la cupula de oro sobre el
    cima_nov = fe.mundo_de(M, V, p, 'halo')
    RD = max(8.5, (cima_nov[1] + 1.5) / 1.15)
    c = np.array([N[0], 0.0, N[2]])
    fe.trans(lz, cam, fe.cupula(c, RD, 28, 10), fe.tex_cupula(ORO, 64), 0.36, None, 0.3)
    # los haces: del escudero a la cupula (al punto de la cupula que mira hacia el)
    mitades = []
    for cima in tops:
        d = cima - c
        d[1] = 0
        d /= np.linalg.norm(d)
        sup = c + d * RD * math.cos(math.asin(0.45)) + np.array([0, RD * 1.15 * 0.45, 0])
        pts = curva(cima, sup, 2.2, 24)
        haz_oro(lz, cam, pts, 0.06, 1.1, BRASA, ORO_CLARO)
        haz_oro(lz, cam, pts, 0.18, 0.3, ORO, ORO_CLARO)
        resplandor(lz, cam, sup, 1.8, ORO, 0.9)
        resplandor(lz, cam, cima, 0.8, ORO_CLARO, 0.7)
        mitades.append(pts[len(pts) // 2])
    img = acabar(lz, cam, W, H, fase, 93)
    rotulo(img, cam, c + R * RD * 0.62 + np.array([0, RD * 1.15 * 0.72, 0]), 'SU ESCUDO', 110, -60, 54, ORO_CLARO)
    rotulo(img, cam, tops[0] + np.array([0, 0.3, 0]), 'ESCUDERO', -80, -70, 50, (255, 190, 120))
    rotulo(img, cam, mitades[0], '¡SIN ELLOS CAE EL ESCUDO!', -40, -150, 48, BLANCO)
    guardar(img, 'escuderos')


# ======================================================================
#  8. Sol Caido
#
#  Su sol cae y rueda por la arena: una bola de fuego de 3 bloques que deja un
#  rastro quemado. Detras, los jugadores lo golpean (chispas) para mandarlo
#  contra las piernas de Novilis (la flecha de puntos). Delante, uno salta a un
#  lado para que no le pase por encima.
# ======================================================================
def sol_caido(W=1600, H=900, fase=3):
    # de lado: el sol rueda de izquierda a derecha, hacia las piernas de Novilis
    cam = vr.Camara(ojo=(-10.0, 6.8, -22.0), objetivo=(-2.0, 2.4, -6.0), fov=54, ancho=W * SS, alto=H * SS)
    F, R = marco_camara(cam)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    Q = np.array([cam.ojo[0], 0.0, cam.ojo[2]]) + F * 12.5
    RS = 1.5
    S = Q - R * 3.2                               # el sol, en el suelo
    N = Q + R * 11.0 + F * 3.5
    p = pose('GRITO')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], S[0], S[2]) + 15, p, fase, niebla)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase, k=0.7)
    piernas = (fe.mundo_de(M, V, p, 'pie_izq') + fe.mundo_de(M, V, p, 'pie_der')) / 2
    piernas[1] = 0.1
    hacia = piernas - S
    hacia[1] = 0
    hacia /= np.linalg.norm(hacia)
    lat = np.array([-hacia[2], 0, hacia[0]])
    if lat @ F < 0:
        lat = -lat                                # lat: hacia el fondo
    # el rastro quemado, de la izquierda hasta el sol (con una curva)
    ruta = [S - hacia * 11.5 * t + lat * 1.8 * math.sin(math.pi * t) for t in np.linspace(1, 0, 18)]
    quad, bordes = [], []
    for i in range(len(ruta) - 1):
        a, b = ruta[i], ruta[i + 1]
        d = b - a
        lado = np.array([-d[2], 0, d[0]]) / (np.linalg.norm(d) + 1e-9)
        ancho = 1.45 * (0.7 + 0.3 * i / (len(ruta) - 2))
        quad.append(([tuple(a - lado * ancho + [0, 0.07, 0]), tuple(b - lado * ancho + [0, 0.07, 0]),
                      tuple(b + lado * ancho + [0, 0.07, 0]), tuple(a + lado * ancho + [0, 0.07, 0])],
                     [(0, 1), (1, 1), (1, 0), (0, 0)]))
        for sg in (-1, 1):
            e0, e1 = a + lado * ancho * sg, b + lado * ancho * sg
            bordes.append(([tuple(e0 - lado * 0.14 + [0, 0.08, 0]), tuple(e1 - lado * 0.14 + [0, 0.08, 0]),
                            tuple(e1 + lado * 0.14 + [0, 0.08, 0]), tuple(e0 + lado * 0.14 + [0, 0.08, 0])],
                           [(0, 0), (0, 1), (1, 1), (1, 0)]))
    # los que lo golpean, detras (los dos de este lado) y otro que llega corriendo
    golpes = [S - hacia * 2.3 - lat * 1.5, S - hacia * 1.9 + lat * 2.1]
    for i, q in enumerate(golpes):
        Mj, pj = jugador(lz, cam, q[0], q[2], (S[0], S[2]), GOLPE, niebla=niebla)
        en_mano(lz, cam, Mj, pj, 'espada', 0.38, giro=math.radians(-30), luz=1.1)
    corre = S - hacia * 6.6 - lat * 2.2
    jugador(lz, cam, corre[0], corre[2], (S[0], S[2]), CORRER, niebla=niebla)
    # el que esquiva: estaba en su camino y salta hacia delante (hacia la camara)
    salta = S + hacia * 3.9 - lat * 3.0
    mira = (S - salta) / np.linalg.norm(S - salta)
    LADEO = 36 if np.cross([0, 1.0, 0], mira) @ (-lat) > 0 else -36    # que se incline hacia donde salta
    Ms = jugador_inclinado(lz, cam, salta + np.array([0, 1.6, 0]), fe.guinada_hacia(salta[0], salta[2], S[0], S[2]), LADEO,
                           SALTO, niebla)
    fe.trans(lz, cam, quad, tex_quemado(), 0.92, None, 0.0, 1.0)
    fe.aditivo(lz, cam, quad, tex_ascuas(), 1.4)
    fe.aditivo(lz, cam, bordes, tex_banda(BRASA), 0.6)
    r = random.Random(4)
    for i, q in enumerate(ruta[4:-2]):
        if i % 2 == 0:
            fe.llamas_en(lz, cam, q + lat * r.uniform(-0.7, 0.7), 0.55, 1, 2, 90 + i, 0.75)
    # su sombra en el suelo, donde estaba
    fe.trans(lz, cam, fe.suelo_cuad(salta[0], salta[2], 0.9, 0.08), tex_luz_suelo((10, 6, 6), 64, 0.8), 0.6, None, 0.0)
    # la flecha de puntos hasta sus pies
    a2 = np.array([S[0], S[2]]) + np.array([hacia[0], hacia[2]]) * (RS + 1.0)
    b2 = np.array([piernas[0], piernas[2]]) - np.array([hacia[0], hacia[2]]) * 2.6
    linea_puntos(lz, cam, a2, b2, ORO_CLARO, y=0.12, paso=1.0, largo=0.55, ancho=0.22, brillo=1.8)
    # el sol: la corona y el calor detras, la bola de fuego encima
    c = S + np.array([0, RS, 0])
    resplandor(lz, cam, c + (cam.ojo - c) / np.linalg.norm(cam.ojo - c) * 0.1, RS * 4.2, BRASA, 0.5)
    bola_de_fuego(lz, cam, c, RS, 11, 0.3)
    # las chispas de los golpes
    chis = tex_chispas()
    for i, q in enumerate(golpes):
        d = q - S
        d[1] = 0
        d /= np.linalg.norm(d)
        imp = c + d * RS * 1.0 + np.array([0, -0.1 + 0.35 * i, 0])
        fe.aditivo(lz, cam, [fe.billboard(imp, 1.0, cam, 0.4 * i)], chis, 1.4)
    img = acabar(lz, cam, W, H, fase, 94)
    img = calima(img, cam, c, RS * 2.8, 3.0, 2.0, hueco=RS * 1.15).convert('RGBA')
    estelas(img, cam, salta + np.array([0, 2.6, 0]), salta + np.array([0, 2.4, 0]) + lat * 2.6 + hacia * 0.4)
    flechas(img, cam, np.array([a2[0], 0.12, a2[1]]), np.array([b2[0], 0.12, b2[1]]), ts=(0.35, 0.65, 0.95), tam=18)
    rotulo(img, cam, c + np.array([0, RS * 1.3, 0]), 'SOL CAÍDO', -20, -150, 56, ORO_CLARO)
    rotulo(img, cam, np.array([b2[0], 0.2, b2[1]]), '¡EMPUJADLO CONTRA ÉL!', -40, 70, 52, BLANCO)
    guardar(img, 'sol_caido')


# ======================================================================
#  Tercera ficha (minijuegos): ayudas comunes
# ======================================================================
K_NOV = ESCALA / 16.0                             # bloques por px del modelo de Novilis


def _vanilla_tex(ruta):
    """Una textura de vanilla (bajo assets/minecraft/textures/), del jar del cliente que deja loom (si esta)."""
    jar = os.path.join(os.path.expanduser('~'), '.gradle/caches/fabric-loom/26.2/minecraft-client-only.jar')
    try:
        with zipfile.ZipFile(jar) as z:
            return Image.open(io.BytesIO(z.read('assets/minecraft/textures/' + ruta))).convert('RGBA')
    except (OSError, KeyError):
        return None


def frente(guinada):
    """Hacia donde mira (por el suelo) una entidad con esta guinada (el frente del modelo es -Z)."""
    g = math.radians(guinada)
    return np.array([-math.sin(g), 0.0, -math.cos(g)])


def _hombro(p, lado):
    return fm.matrices(fe.esq(V), p)['brazo_' + lado][:3, 3]


def _alcance(p, lado, direccion, largo=38.0):
    """Un punto a 'largo' px del hombro, hacia 'direccion' (px de modelo): donde llevar el puno."""
    d = np.array(direccion, float)
    return tuple(_hombro(p, lado) + d / np.linalg.norm(d) * largo)


def dir_a_modelo(guinada, d):
    """Una direccion del mundo al espacio del modelo de Novilis (para apuntar la espada)."""
    m = (vr.Ry(-math.radians(guinada))[:3, :3] @ np.array(d, float)) * np.array([-1.0, -1.0, 1.0])
    return m / np.linalg.norm(m)


def tex_destello(n=128, color=ORO):
    """El destello del filo: una estrella de cuatro puntas (y cuatro mas cortas), el alma blanca."""
    yy, xx = np.mgrid[0:n, 0:n]
    x, y = (xx + 0.5 - n / 2) / (n / 2), (yy + 0.5 - n / 2) / (n / 2)

    def rayo(a, b, largo, ancho):
        w = ancho * np.clip(1 - np.abs(a) / largo, 0, 1) ** 1.6 + 1e-6
        return np.clip(1 - np.abs(b) / w, 0, 1) * np.clip(1 - np.abs(a) / largo, 0, 1)

    u, v = (x + y) / math.sqrt(2), (x - y) / math.sqrt(2)
    a = np.maximum.reduce([rayo(x, y, 1.0, 0.09), rayo(y, x, 1.0, 0.09), rayo(u, v, 0.45, 0.06), rayo(v, u, 0.45, 0.06)])
    r = np.hypot(x, y)
    a = np.clip(a + np.clip(1 - r / 0.32, 0, 1) ** 1.5, 0, 1)
    k = np.clip(1 - r / 0.22, 0, 1)[..., None]
    col = np.array(color) * (1 - k) + np.array([255, 255, 246]) * k
    return _rgba(col, a)


def tex_moteado(colores, semilla, n=16):
    r = random.Random(semilla)
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            t[y, x] = (*r.choice(colores), 255)
    return t


def tex_chispas_huecas(n=128, semilla=9, color=ORO):
    """Chispas que saltan hacia fuera, sin el nucleo blanco (para no tapar lo que golpea)."""
    r = random.Random(semilla)
    im = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(im)
    c = n / 2
    for k in range(14):
        a = TAU * k / 14 + r.uniform(-0.2, 0.2)
        l0, l1 = n * r.uniform(0.16, 0.22), n * r.uniform(0.32, 0.48)
        d.line([(c + math.cos(a) * l0, c + math.sin(a) * l0), (c + math.cos(a) * l1, c + math.sin(a) * l1)],
               fill=255, width=max(2, n // 48))
    for _ in range(12):
        a, l = r.uniform(0, TAU), n * r.uniform(0.22, 0.47)
        q = (c + math.cos(a) * l, c + math.sin(a) * l)
        d.ellipse((q[0] - 1.5, q[1] - 1.5, q[0] + 1.5, q[1] + 1.5), fill=255)
    m = np.array(im.filter(ImageFilter.GaussianBlur(0.7))).astype(float) / 255
    halo = np.array(im.filter(ImageFilter.GaussianBlur(n / 30))).astype(float) / 255
    col = np.ones((n, n, 3)) * np.array(fe._mez(color, (255, 255, 255), 0.45))
    return _rgba(col, np.clip(m + halo * 0.4, 0, 1))


DESTELLO = tex_destello()
DESTELLO_ROJO = tex_destello(color=ROJO)
CHISPAS = tex_chispas()
CHISPAS_HUECAS = tex_chispas_huecas()


def _escudo_tex():
    """Las dos caras del escudo de vanilla (12 x 22 texeles), o unas tablas con el canto de hierro."""
    im = _vanilla_tex('entity/shield/shield_base_nopattern.png')
    if im is None:
        im = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for x0 in (1, 14):
            d.rectangle((x0, 1, x0 + 11, 22), fill=(120, 124, 130, 255))
            d.rectangle((x0 + 1, 2, x0 + 10, 21), fill=(122, 86, 48, 255))
    a = np.array(im)
    return a[1:23, 1:13].copy(), a[1:23, 14:26].copy()


_FRENTE_E, _DORSO_E = _escudo_tex()
fm.registrar('escudo_frente', _FRENTE_E)
fm.registrar('escudo_dorso', _DORSO_E)
fm.registrar('escudo_canto', fe._loseta(61, nm._rampa('5a5c62', '6e7076', '80838a', '94979e', 'a8abb2'), (1, 2, 2, 3)))
nm.ESTIRADOS.update({'escudo_frente', 'escudo_dorso'})
fm.ESTIRA.update({'escudo_frente', 'escudo_dorso'})


def escudo_modelo():
    """El escudo de vanilla (12 x 22 px), el centro en el origen y la cara hacia -Z."""
    return nm.nodo('escudo', (0, 0, 0), (0, 0, 0), [
        ((-6, -11, -0.55, 12, 22, 0.1), 'escudo_frente'),
        ((-6, -11, 0.45, 12, 22, 0.1), 'escudo_dorso'),
        ((-6, -11, -0.45, 12, 22, 0.9), 'escudo_canto'),
        ((-1, -3, 0.55, 2, 6, 2.5), 'escudo_canto')])


ESCUDO_V = escudo_modelo()
BLOQUEO = {'bi': {'rot': (-80, -28, 0)}, 'bd': {'rot': (18, 0, 6)}, 'pi': {'rot': (-20, 0, 0)}, 'pd': {'rot': (20, 0, 0)}}


def escudo_en(lz, cam, c, guinada, inclina, niebla, fase=1):
    """El escudo de vanilla con el centro en c, de cara a 'guinada' e inclinado hacia arriba."""
    fm.dibujar(lz, cam, nm.quads(ESCUDO_V, {}, modelo_en(c[0], c[1], c[2], guinada, inclina)), fe.LUCES, fe.AMB, niebla, 1.0,
               fase)


def mano_izq_local(guinada, p, delante=0.24):
    """Donde cae el centro del escudo (la mano izquierda y un poco delante) de un jugador en el origen."""
    M0 = ne.jugador_a_mundo(0.0, 0.0, guinada)
    return punto_jugador(M0, p, 'bi', (0, 10, 0)) + frente(guinada) * delante


def item_hacia(lz, cam, Mj, pj, tex, objetivo, tam=None, luz=1.1, alcance=1.0):
    """Un objeto en la mano derecha (el mango en la mano) con la cabeza hacia 'objetivo' (en la foto)."""
    mano = punto_jugador(Mj, pj, 'bd', (0, 10.5, 0))
    d = np.array(objetivo, float) - mano
    phi = math.atan2(d @ cam.u, d @ cam.r)
    g = phi - math.pi / 4
    if tam is None:
        dist = math.hypot(d @ cam.u, d @ cam.r)
        tam = min(0.5, max(0.3, dist * alcance / 1.56))
    rr = cam.r * math.cos(g) + cam.u * math.sin(g)
    uu = -cam.r * math.sin(g) + cam.u * math.cos(g)
    sprite(lz, cam, mano + (rr + uu) * tam * 0.5, tam, tex, g, luz)
    return mano


def contador(img, x, y, cifra_txt, texto, color=ORO_CLARO):
    """El contador de la esquina (como el de la Armadura al Rojo): la cifra grande y debajo que cuenta."""
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 64)
    for o in ((3, 3), (2, 2)):
        d.text((x + o[0], y + o[1]), cifra_txt, font=f, fill=(*SOMBRA, 255))
    d.text((x, y), cifra_txt, font=f, fill=(*color, 255))
    f2 = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 26)
    for o in ((2, 2),):
        d.text((x + 2 + o[0], y + 80 + o[1]), texto, font=f2, fill=(*SOMBRA, 255))
    d.text((x + 2, y + 80), texto, font=f2, fill=(*BLANCO, 255))


# ======================================================================
#  9. Choque de Espadas
#
#  En el Barrido, justo antes del tajo, la hoja da un destello de oro. Cerca,
#  un jugador alza el escudo a tiempo: la hoja choca contra el, saltan chispas
#  y sale "PARADA". Detras, otro espera con el escudo listo y otro con la espada.
#  Arriba a la izquierda, las paradas que lleva este Barrido (2/3).
# ======================================================================
ESTOCADA = {'pelvis': {'pos': (0, 14, 0)}, 'tabardo': {'rot': (-36, 0, 0)},
            'pierna_izq': {'rot': (-55, 0, -6)}, 'espinilla_izq': {'rot': (62, 0, 0)}, 'pie_izq': {'rot': (-7, 0, 0)},
            'pierna_der': {'rot': (38, 0, 8)}, 'espinilla_der': {'rot': (16, 0, 0)}, 'pie_der': {'rot': (-46, 0, 0)}}


def _pose_tajo():
    if 'TAJO_BAJO' not in _POSES:
        p = fe._une(ESTOCADA, fe.CAPA_VIENTO, {'torso': {'rot': (30, -18, 0)}, 'cabeza': {'rot': (-10, 14, 0)}})
        p, _ = fm.alcanzar(p, 'der', _alcance(p, 'der', (-0.05, 0.75, -0.66), 42))
        p, _ = fm.alcanzar(p, 'izq', _alcance(p, 'izq', (0.55, 0.7, 0.3), 34))
        _POSES['TAJO_BAJO'] = p
    return {k: dict(v) for k, v in _POSES['TAJO_BAJO'].items()}


def choque(W=1600, H=900, fase=1):
    N = np.array([5.0, 0.0, 8.0])
    hacia = np.array([-0.58, 0.0, -0.81])
    hacia /= np.linalg.norm(hacia)
    g_nov = fe.guinada_hacia(N[0], N[2], N[0] + hacia[0], N[2] + hacia[2])
    M = fm.entidad_a_mundo(N[0], 0, N[2], g_nov, ESCALA)
    p = _pose_tajo()
    # el escudo del que para: a la altura de su mano; la hoja le da en la mitad de arriba
    g0 = fe.guinada_hacia(0, 0, -hacia[0], -hacia[2])
    alto_escudo = mano_izq_local(g0, BLOQUEO)[1]
    alto_choque = alto_escudo + 0.3
    agarre = fe.mundo_de(M, V, p, 'agarre')
    LC = 23 + 0.95 * fm.LARGO_HOJA                        # el punto de la hoja que choca (px de la espada)
    largo = LC * K_NOV
    caida = agarre[1] - alto_choque
    llano = math.sqrt(max(0.1, largo ** 2 - caida ** 2))
    giro = math.radians(10)
    hz = np.array([hacia[0] * math.cos(giro) - hacia[2] * math.sin(giro), 0, hacia[0] * math.sin(giro) + hacia[2] * math.cos(giro)])
    d_w = hz * llano - np.array([0, caida, 0])
    p = fm.apuntar_espada(p, dir_a_modelo(g_nov, d_w))
    C = fe.mundo_de(M, V, p, 'espada', (0, LC, 0))
    # el jugador: de cara a la hoja, con el centro del escudo justo detras del choque
    f_p = np.array([N[0] - C[0], 0, N[2] - C[2]])
    f_p /= np.linalg.norm(f_p)
    g_p = fe.guinada_hacia(0, 0, f_p[0], f_p[2])
    S = C - f_p * 0.08 - np.array([0, 0.3, 0])
    o = mano_izq_local(g_p, BLOQUEO)
    P = np.array([S[0] - o[0], 0.0, S[2] - o[2]])
    izq = np.array([f_p[2], 0.0, -f_p[0]])                # la izquierda del jugador
    ojo = P + izq * 5.4 - f_p * 6.4 + np.array([0, 1.75, 0])
    mira = P + f_p * 6.0 - izq * 0.5 + np.array([0, 4.7, 0])
    cam = vr.Camara(ojo=tuple(ojo), objetivo=tuple(mira), fov=56, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    # los de detras: uno con el escudo listo (espera su destello) y otro con la espada
    Q1 = P + f_p * 0.8 - izq * 3.2
    Q2 = P + f_p * 2.2 - izq * 5.2
    for q, pz in ((Q1, BLOQUEO), (Q2, GUARDIA)):
        gq = fe.guinada_hacia(q[0], q[2], N[0], N[2])
        Mq, pq = jugador(lz, cam, q[0], q[2], (N[0], N[2]), pz, niebla=niebla)
        if pz is BLOQUEO:
            escudo_en(lz, cam, punto_jugador(Mq, pq, 'bi', (0, 10, 0)) + frente(gq) * 0.24, gq, 14, niebla, fase)
        else:
            en_mano(lz, cam, Mq, pq, 'espada', 0.4, giro=math.radians(30), luz=1.1)
    # el que para
    Mj, pj = jugador(lz, cam, P[0], P[2], (N[0], N[2]), BLOQUEO, niebla=niebla)
    en_mano(lz, cam, Mj, pj, 'espada', 0.38, giro=math.radians(-60), luz=1.05)
    escudo_en(lz, cam, S, g_p, 12, niebla, fase)
    # Novilis, con el tajo que baja
    caballero(lz, cam, N[0], N[2], g_nov, p, fase, niebla)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase, espada=False, k=0.8)
    # el destello de oro: la hoja entera se enciende y un brillo corre por el filo
    qs = [q for q in quads_por_pieza(p, M) if q[3] == 'espada_hoja']
    capa_sobre(lz, cam, qs, fe.tex_plano((255, 200, 70)), 'aditivo', brillo=0.6)
    base = fe.mundo_de(M, V, p, 'espada', (0, 14, 0))
    punta = fe.mundo_de(M, V, p, 'espada', (0, fm.PUNTA_ESPADA, 0))
    haz_oro(lz, cam, [base + (punta - base) * t for t in np.linspace(0, 0.9, 12)], 0.2, 0.55, ORO, ORO_CLARO)
    filo = fe.mundo_de(M, V, p, 'espada', (0, 23 + 0.38 * fm.LARGO_HOJA, 0))
    fe.aditivo(lz, cam, [fe.billboard(filo, 2.3, cam, 0.25)], DESTELLO, 2.0)
    resplandor(lz, cam, filo, 2.4, ORO, 0.45)
    # el choque: chispas y el resplandor delante del escudo
    hacia_cam = (cam.ojo - C) / np.linalg.norm(cam.ojo - C)
    imp = C + hacia_cam * 0.25
    resplandor(lz, cam, imp, 1.0, ORO_CLARO, 0.35)
    fe.aditivo(lz, cam, [fe.billboard(imp, 1.0, cam, 0.3)], CHISPAS, 1.15)
    fe.aditivo(lz, cam, [fe.billboard(imp, 0.6, cam, 1.1)], CHISPAS, 0.8)
    img = acabar(lz, cam, W, H, fase, 101)
    cifra(img, cam, imp + np.array([0, 1.5, 0]) - izq * 2.2, '¡PARADA!', 96, (255, 226, 130))
    rotulo(img, cam, filo, 'DESTELLO DE ORO', 90, -150, 50, ORO_CLARO)
    rotulo(img, cam, S - f_p * 0.1 - np.array([0, 0.45, 0]), 'ESCUDO EN ALTO', -160, 90, 44, BLANCO)
    contador(img, 60, 50, '2/3', 'PARADAS EN ESTE BARRIDO')
    guardar(img, 'choque')


# ======================================================================
#  10. Forja del Juramento
#
#  Novilis, de rodillas al fondo con la espada clavada. Delante, tres yunques
#  de piedra con una hoja al rojo encima y un herrero en cada uno. En el de
#  cerca, el golpe en el momento justo: el aro de luz se ha cerrado sobre la
#  hoja, saltan chispas y sale "PERFECTO". Encima de cada yunque, los golpes
#  buenos que lleva (de 6). En los otros dos, el aro aun se esta cerrando.
# ======================================================================
fm.registrar('hoja_roja', tex_moteado(((255, 150, 40), (255, 112, 30), (240, 84, 24), (255, 186, 70), (226, 66, 20)), 71),
             pleno=True)
fm.registrar('hoja_espiga', tex_moteado(((150, 44, 22), (120, 34, 20), (176, 60, 26)), 72),
             tex_moteado(((150, 44, 22), (120, 34, 20), (176, 60, 26)), 72))


def yunque_modelo():
    """Un yunque de piedra como el de vanilla (px de bloque: el pie en y = 0, Y hacia abajo, lo largo en Z),
    con su hoja al rojo encima."""
    hoja = [((-2.2, -16.8, -12, 4.4, 0.8, 22), 'hoja_roja')]
    for i in range(5):                                    # el filo ondulado, como el de su espada
        o = 0.6 if i % 2 == 0 else -0.6
        hoja.append(((-3.0 + o, -16.7, -11 + 4.4 * i, 6.0, 0.7, 4.4), 'hoja_roja'))
    hoja += [((-1.5, -16.8, 10, 3.0, 0.8, 3), 'hoja_roja'), ((-0.7, -16.8, 13, 1.4, 0.8, 2), 'hoja_roja'),
             ((-0.9, -16.7, -18, 1.8, 0.7, 6), 'hoja_espiga')]
    return nm.nodo('yunque', (0, 0, 0), (0, 0, 0), [
        ((-6, -4, -6, 12, 4, 12), 'basalto_j'),
        ((-6.3, -4.6, -6.3, 12.6, 0.8, 12.6), 'oro_bloque'),
        ((-4, -5, -5, 8, 1, 10), 'negra'),
        ((-2, -10, -4, 4, 5, 8), 'basalto_j'),
        ((-5, -16, -8, 10, 6, 16), 'basalto'),
        ((-5.3, -11, -8.3, 10.6, 1.0, 16.6), 'oro_bloque')] + hoja)


YUNQUE = yunque_modelo()
ESC_YUNQUE = 1.25
MARTILLA = {'bd': {'rot': (-58, -12, 0)}, 'bi': {'rot': (-20, 0, -12)}, 'pi': {'rot': (-16, 0, 0)}, 'pd': {'rot': (16, 0, 0)}}
ALZA_MAZA = {'bd': {'rot': (-165, -10, 0)}, 'bi': {'rot': (-24, 0, -14)}, 'pi': {'rot': (-14, 0, 0)}, 'pd': {'rot': (14, 0, 0)}}


def sprite_maza():
    im = _vanilla_tex('item/mace.png')
    if im is None:
        im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.line([(2, 13), (10, 5)], fill=(90, 70, 110, 255), width=2)
        d.rectangle((9, 1, 14, 6), fill=(70, 72, 80, 255))
    return np.array(im)


def yunque(lz, cam, x, z, eje, niebla, fase):
    """Dibuja un yunque en (x, z) con lo largo hacia 'eje' (x, z); devuelve el punto de golpe de la hoja."""
    g = fe.guinada_hacia(x, z, x + eje[0], z + eje[1])
    M = modelo_en(x, 0, z, g, 0, ESC_YUNQUE)
    qs = nm.quads(YUNQUE, {}, M)
    fm.dibujar(lz, cam, qs, fe.LUCES, fe.AMB, niebla, 0.5, fase)
    # la hoja brilla por encima (que se lea entera, no solo el filo)
    fe.aditivo(lz, cam, [(P, UV) for P, UV, mat in qs if mat == 'hoja_roja'], fe.tex_plano((255, 70, 10)), 0.25)
    return (M @ np.array([0, -16.8, -1, 1.0]))[:3], (M @ np.array([0, -16.8, -9, 1.0]))[:3]


def aro_golpe(lz, cam, c, R, k=1.0, fantasmas=(), grueso=0.08, halo=0.1):
    """El aro de luz que se cierra sobre la hoja (de cara a la camara) y, mas grandes y
    apagados, los aros por donde ha pasado."""
    for (Rf, kf) in fantasmas:
        fe.aditivo(lz, cam, [fe.billboard(c, Rf, cam)], fe.tex_aro(ORO, 256, grueso * 0.7), kf)
    fe.aditivo(lz, cam, [fe.billboard(c, R, cam)], fe.tex_aro((255, 226, 130), 256, grueso), k)
    if halo:
        resplandor(lz, cam, c, R * 1.3, ORO, halo * k)


def chevrones(img, cam, c, R, n=4, tam=12, color=ORO_CLARO, giro=0.785):
    """Unos angulos que apuntan al centro, por fuera del aro: el aro se cierra."""
    sx, sy, z = cam.proyectar(c)
    sx, sy = sx / SS, sy / SS
    rp = cam.foco / SS * R / z
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for k in range(n):
        a = giro + TAU * k / n
        u = np.array([math.cos(a), math.sin(a)])
        nrm = np.array([-u[1], u[0]])
        p = np.array([sx, sy]) + u * (rp + tam * 1.4)
        pts = [tuple(p + u * tam + nrm * tam), tuple(p), tuple(p + u * tam - nrm * tam)]
        d.line(pts, fill=(*SOMBRA, 170), width=8, joint='curve')
        d.line(pts, fill=(*color, 255), width=4, joint='curve')
    img.alpha_composite(capa)


def pips(img, cam, p, buenos, total=6, lado=18, dy=0):
    """Los golpes buenos que lleva un yunque: cuadraditos de oro (encendidos) y huecos."""
    sx, sy, z = cam.proyectar(p)
    sx, sy = sx / SS, sy / SS + dy
    paso = lado * 1.35
    x0 = sx - paso * total / 2 + (paso - lado) / 2
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for i in range(total):
        x = x0 + i * paso
        caja = (x, sy - lado / 2, x + lado, sy + lado / 2)
        d.rectangle((caja[0] + 2, caja[1] + 2, caja[2] + 2, caja[3] + 2), fill=(*SOMBRA, 180))
        if i < buenos:
            d.rectangle(caja, fill=(*ORO, 255), outline=(*ORO_CLARO, 255), width=max(1, lado // 8))
        else:
            d.rectangle(caja, fill=(40, 22, 14, 220), outline=(*ORO, 255), width=max(1, lado // 8))
    halo = capa.filter(ImageFilter.GaussianBlur(lado / 4))
    img.alpha_composite(halo)
    img.alpha_composite(capa)
    return x0 + total * paso, sy


def forja(W=1600, H=900, fase=2):
    A1 = np.array([-4.0, 0.0, -8.5])
    D = np.array([0.32, 0.0, 0.95])
    D /= np.linalg.norm(D)
    cam = vr.Camara(ojo=tuple(A1 - D * 5.6 + np.array([0, 4.0, 0])), objetivo=tuple(A1 + D * 5.0 + np.array([0, 2.3, 0])),
                    fov=58, ancho=W * SS, alto=H * SS)
    F, R = marco_camara(cam)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    A2 = A1 + F * 6.0 + R * 5.8
    A3 = A1 + F * 7.5 - R * 6.0
    N = A1 + F * 27.0 + R * 6.0
    # Novilis de rodillas, la espada clavada delante
    p = pose('CASTIGO_CLAVA')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], A1[0], A1[2]), p, fase, niebla, con_espada=False)
    fe.espada_clavada(lz, cam, M, 0, -30, V, fase, niebla, inclina=0.0)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase, espada=False, k=0.6)
    maza = sprite_maza()
    golpes = []
    # los yunques: lo largo de lado a la camara; el herrero, en el lado largo
    for i, (A, pz, buenos) in enumerate(((A1, MARTILLA, 4), (A2, ALZA_MAZA, 2), (A3, MARTILLA, 5))):
        eje = (R[0], R[2])
        golpe, punta = yunque(lz, cam, A[0], A[2], eje, niebla, fase)
        if i == 0:                                       # el de cerca: detras del yunque, de cara a la camara
            q, mira = A + F * 1.05 + R * 0.3, np.array([cam.ojo[0], 0, cam.ojo[2]])
        else:                                            # los otros: detras y a un lado, de cara a la hoja
            q, mira = A + F * 0.95 + R * 0.85, golpe
        Mj, pj = jugador(lz, cam, q[0], q[2], (mira[0], mira[2]), pz, niebla=niebla)
        if pz is MARTILLA:
            item_hacia(lz, cam, Mj, pj, maza, golpe + np.array([0, 0.25, 0]), luz=1.1)
        else:
            arriba = punto_jugador(Mj, pj, 'bd', (0, 10.5, 0)) + np.array([0, 1.0, 0]) - R * 0.3
            item_hacia(lz, cam, Mj, pj, maza, arriba, 0.42, luz=1.1)
        golpes.append((golpe, buenos))
        # el calor de la hoja
        resplandor(lz, cam, golpe + np.array([0, 0.1, 0]), 0.9, BRASA, 0.3)
    # el yunque de cerca: el aro justo encima de la hoja, las chispas del golpe
    g1 = golpes[0][0]
    aro_golpe(lz, cam, g1 + np.array([0, 0.05, 0]), 0.58, 2.4, ((0.86, 0.6), (1.14, 0.35), (1.42, 0.2)), 0.11, halo=0.0)
    aro_golpe(lz, cam, g1 + np.array([0, 0.05, 0]), 0.58, 1.2, (), 0.05, halo=0.0)
    hacia_cam = (cam.ojo - g1) / np.linalg.norm(cam.ojo - g1)
    fe.aditivo(lz, cam, [fe.billboard(g1 + hacia_cam * 0.3 + np.array([0, 0.1, 0]), 0.75, cam, 0.4)], CHISPAS_HUECAS, 1.1)
    # los otros dos: el aro aun grande, cerrandose
    aro_golpe(lz, cam, golpes[1][0] + np.array([0, 0.05, 0]), 1.1, 0.9, ((1.6, 0.3),), 0.07)
    aro_golpe(lz, cam, golpes[2][0] + np.array([0, 0.05, 0]), 0.75, 0.9, ((1.2, 0.3),), 0.07)
    img = acabar(lz, cam, W, H, fase, 102)
    cifra(img, cam, g1 + np.array([0, 1.5, 0]) + R * 0.6, '¡PERFECTO!', 84, (255, 226, 130))
    for (g, b), Ra in zip(golpes[1:], (1.1, 0.75)):
        chevrones(img, cam, g + np.array([0, 0.05, 0]), Ra, 4, 13)
    fin, y = pips(img, cam, golpes[0][0] + np.array([0, 2.35, 0]) - R * 0.5, 4, 6, 22)
    d = ImageDraw.Draw(img)
    for (g, b) in golpes[1:]:
        pips(img, cam, g + np.array([0, 2.6, 0]), b, 6, 14)
    rotulo(img, cam, golpes[0][0] - R * 0.95 + np.array([0, -0.05, 0]), 'HOJA AL ROJO', -60, 80, 44, (255, 190, 120))
    rotulo(img, cam, golpes[1][0] + R * 1.1 + np.array([0, 0.3, 0]), 'EL ARO SE CIERRA', 60, -10, 40, ORO_CLARO)
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 30)
    for o in ((2, 2), (1, 1)):
        d.text((fin + 10 + o[0], y - 20 + o[1]), '4/6', font=f, fill=(*SOMBRA, 255))
    d.text((fin + 10, y - 20), '4/6', font=f, fill=(*ORO_CLARO, 255))
    guardar(img, 'forja')


# ======================================================================
#  11. Justa del Sol
#
#  Un pasillo marcado por dos lineas de llamas. Por el, el retado carga a
#  lomos de un caballo de fuego con la lanza de luz bajo el brazo; de frente,
#  Novilis carga agachado tras un escudo grande con el sol en medio. La punta
#  de la lanza llega al emblema, que se enciende. Fuera de las llamas, los demas.
# ======================================================================
def _tex_caballo(semilla=81):
    """La piel del caballo de fuego: brasa oscura (para que se lea la forma) con grietas de lava que brillan."""
    r = random.Random(semilla)
    t = np.zeros((16, 16, 4), np.uint8)
    e = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            t[y, x] = (*r.choice(((92, 30, 16), (110, 38, 18), (128, 44, 20), (84, 26, 14))), 255)
    for _ in range(3):                                  # las grietas: caminos que bajan en zigzag
        x, y = r.randrange(16), 0
        while y < 16:
            c = (255, 196, 70) if r.random() < 0.5 else (255, 140, 40)
            t[y % 16, x % 16] = (*c, 255)
            e[y % 16, x % 16] = (*c, 255)
            x += r.choice((-1, 0, 1))
            y += 1
    for _ in range(10):
        x, y = r.randrange(16), r.randrange(16)
        t[y, x] = (240, 110, 30, 255)
        e[y, x] = (240, 110, 30, 160)
    return t, e


_tc, _ec = _tex_caballo()
fm.registrar('caballo_fuego', _tc, _ec)
fm.registrar('casco_fuego', tex_moteado(((255, 244, 200), (255, 226, 150)), 82), pleno=True)
fm.registrar('crin_fuego', tex_moteado(((236, 104, 28), (255, 150, 44), (212, 76, 22), (255, 186, 70)), 83), pleno=True)
fm.registrar('ojo_fuego', tex_moteado(((255, 255, 236),), 84), pleno=True)
fm.registrar('lanza_luz', tex_moteado(((255, 246, 210), (255, 232, 160), (255, 252, 236)), 85), pleno=True)


def caballo_modelo():
    """El caballo de vanilla (AbstractHorseModel), en px, con su silla: el pie en y = 24, el frente en -Z."""
    n = nm.nodo

    def pata(nombre, x, z, x0, z0):
        return n(nombre, (x, 14, z), (0, 0, 0), [((x0, -1, z0, 4, 11, 4), 'caballo_fuego'),
                                                ((x0 - 0.2, 7.5, z0 - 0.2, 4.4, 2.6, 4.4), 'casco_fuego')])

    silla = [((-5.5, -8.7, -9, 11, 3, 9), 'cuero'), ((-5.6, -9.4, -9.6, 11.2, 1.4, 1.6), 'oro'),
             ((-5.6, -9.6, -1.4, 11.2, 1.8, 1.8), 'oro'), ((-5.7, -6, -6, 0.6, 8, 2), 'cuero'), ((5.1, -6, -6, 0.6, 8, 2), 'cuero'),
             ((-6.0, 1.5, -6.5, 1.0, 1.6, 3), 'oro'), ((5.0, 1.5, -6.5, 1.0, 1.6, 3), 'oro')]
    return n('raiz', (0, 0, 0), (0, 0, 0), [], [
        n('cuerpo', (0, 11, 5), (0, 0, 0), [((-5, -8, -17, 10, 10, 22), 'caballo_fuego')] + silla, [
            n('cola', (0, -5, 2), (30, 0, 0), [((-1.5, 0, 0, 3, 14, 4), 'crin_fuego')])]),
        n('cuello', (0, 4, -12), (30, 0, 0), [((-2.05, -6, -2, 4, 12, 7), 'caballo_fuego')], [
            n('cabeza_c', (0, 0, 0), (0, 0, 0), [
                ((-3, -11, -2, 6, 5, 7), 'caballo_fuego'), ((-2, -11, -7, 4, 5, 5), 'caballo_fuego'),
                ((0.55, -13, 4, 2, 3, 1), 'caballo_fuego'), ((-2.55, -13, 4, 2, 3, 1), 'caballo_fuego'),
                ((-3.3, -10, -0.5, 0.5, 1.4, 1.4), 'ojo_fuego'), ((2.8, -10, -0.5, 0.5, 1.4, 1.4), 'ojo_fuego')]),
            n('crin', (0, 0, 0), (0, 0, 0), [((-1, -11, 5.01, 2, 16, 2), 'crin_fuego')])]),
        pata('pata_ti', 4, 7, -3, -1), pata('pata_td', -4, 7, -1, -1),
        pata('pata_di', 4, -10, -3, -1.9), pata('pata_dd', -4, -10, -1, -1.9)])


CABALLO = caballo_modelo()
ESC_CABALLO = 1.4
GALOPE = {'pata_di': {'rot': (-52, 0, 0)}, 'pata_dd': {'rot': (-18, 0, 0)}, 'pata_ti': {'rot': (40, 0, 0)},
          'pata_td': {'rot': (14, 0, 0)}, 'cuello': {'rot': (-14, 0, 0)}, 'cola': {'rot': (46, 0, 0)}}
JINETE = {'pi': {'rot': (-81, -18, -4.5)}, 'pd': {'rot': (-81, 18, 4.5)}, 'bd': {'rot': (-24, 0, 6)},
          'bi': {'rot': (-58, 0, -8)}, 'cabeza': {'rot': (6, 0, 0)}}


def caballo(lz, cam, x, z, guinada, p, niebla, fase):
    """Dibuja el caballo de fuego (con llamas en la crin, la cola y los cascos); devuelve su matriz."""
    M = vr.entidad_a_mundo(x, 0, z, guinada, ESC_CABALLO)
    fm.dibujar(lz, cam, nm.quads(CABALLO, p, M), fe.LUCES, fe.AMB, niebla, 1.0, fase)
    for i, t in enumerate(np.linspace(-10, 4, 6)):          # la crin, de la nuca a la cruz
        fe.llamas_en(lz, cam, punto_de(CABALLO, M, p, 'crin', (0, t, 6)), 0.55, 1, 2, 120 + i, 0.9)
    for i, t in enumerate((2, 6, 10, 14)):                   # la cola
        fe.llamas_en(lz, cam, punto_de(CABALLO, M, p, 'cola', (0, t, 2)), 0.5, 1, 2, 130 + i, 0.9)
    for i, t in enumerate(np.linspace(-15, 3, 5)):           # el lomo arde
        fe.llamas_en(lz, cam, punto_de(CABALLO, M, p, 'cuerpo', (0, -8, t)), 0.4, 1, 2, 150 + i, 0.6)
    resplandor(lz, cam, punto_de(CABALLO, M, p, 'cuerpo', (0, -3, -6)), 2.4, BRASA, 0.18)
    return M


def eje_a_mundo(a, b):
    """La matriz que lleva px de un modelo con Y a lo largo (0 en a) al tramo a -> b; y lo largo en px."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = float(np.linalg.norm(d))
    y = d / L
    x = np.cross(y, [0.0, 1.0, 0.0])
    if np.linalg.norm(x) < 1e-6:
        x = np.array([1.0, 0, 0])
    x /= np.linalg.norm(x)
    z = np.cross(x, y)
    R = np.eye(4)
    R[:3, 0], R[:3, 1], R[:3, 2] = x, y, z
    return vr.T(*a) @ R @ vr.S(1 / 16), L * 16


def lanza(lz, cam, culata, punta, niebla, fase):
    """La lanza de luz: la empunadura de cuero, la arandela de oro y el asta de luz que se afina."""
    M, L = eje_a_mundo(culata, punta)
    cajas = [((-1.3, 0, -1.3, 2.6, 22, 2.6), 'cuero')]
    for i, (w, h) in enumerate(((9, 1.6), (7, 1.6), (5, 1.6))):
        cajas.append(((-w / 2, 22 + 1.6 * i, -w / 2, w, h, w), 'oro'))
    y0, n = 26.8, 6
    for i in range(n):
        w = 3.2 - 2.2 * i / n
        cajas.append(((-w / 2, y0 + (L - y0) * i / n, -w / 2, w, (L - y0) / n + 0.2, w), 'lanza_luz'))
    fm.dibujar(lz, cam, nm.quads(nm.nodo('lanza', (0, 0, 0), (0, 0, 0), cajas), {}, M), fe.LUCES, fe.AMB, niebla, 0.8, fase)
    a = (M @ np.array([0, y0, 0, 1.0]))[:3]
    haz_oro(lz, cam, [a + (np.array(punta) - a) * t for t in np.linspace(0, 1, 10)], lambda t: 0.16 - 0.08 * t, 0.6, ORO,
            ORO_CLARO)
    return a


def escudo_sol_modelo():
    """El escudo de Novilis (px de su modelo): acero quemado en forma de blason, el canto de oro y el sol
    en medio. El centro en el origen, la cara hacia -Z."""
    n = nm.nodo
    cajas = [((-22, -30, -1.5, 44, 38, 3), 'placa'), ((-19, 8, -1.5, 38, 8, 3), 'placa'),
             ((-14, 16, -1.5, 28, 7, 3), 'placa'), ((-8, 23, -1.5, 16, 6, 3), 'placa'), ((-3, 29, -1.5, 6, 4, 3), 'placa'),
             ((-23.5, -31.5, -2.4, 47, 3, 4.5), 'oro'), ((-23.5, -31.5, -2.4, 3, 41, 4.5), 'oro'),
             ((20.5, -31.5, -2.4, 3, 41, 4.5), 'oro')]
    for (x, y) in ((-20.5, 8), (17.5, 8), (-15.5, 15), (12.5, 15), (-9.5, 22), (6.5, 22), (-4.5, 28), (1.5, 28)):
        cajas.append(((x, y, -2.4, 3, 9, 4.5), 'oro'))
    cajas += [((-3, 31, -2.4, 6, 3, 4.5), 'oro'), ((-1.5, -28, -2.0, 3, 56, 1), 'oro')]
    sol = [((-7, -7, -4.4, 14, 14, 2.4), 'nucleo')]
    for a in range(12):
        ang = TAU * a / 12
        sol.append(((math.cos(ang) * 10.5 - 1.6, math.sin(ang) * 10.5 - 1.6, -3.8, 3.2, 3.2, 1.6), 'oro'))
    return n('escudo_sol', (0, 0, 0), (0, 0, 0), cajas, [
        n('emblema', (0, -6, 0), (0, 0, 0), sol, [fm.rayos_pecho(14, 8, -3.6, 12, 2.6)[k] for k in range(12)])])


ESCUDO_SOL = escudo_sol_modelo()
CARGA = {'pelvis': {'pos': (0, 22, 0)}, 'tabardo': {'rot': (-56, 0, 0)},
         'pierna_izq': {'rot': (-74, 0, -8)}, 'espinilla_izq': {'rot': (80, 0, 0)}, 'pie_izq': {'rot': (-6, 0, 0)},
         'pierna_der': {'rot': (46, 0, 10)}, 'espinilla_der': {'rot': (36, 0, 0)}, 'pie_der': {'rot': (-30, 0, 0)}}


def _pose_carga():
    if 'CARGA' not in _POSES:
        p = fe._une(CARGA, fe.CAPA_VIENTO, {'torso': {'rot': (38, 8, 0)}, 'cabeza': {'rot': (-30, -6, 0)},
                                            'capa_1': {'rot': (46, 0, 0)}, 'capa_2': {'rot': (16, 0, 0)}})
        p, _ = fm.alcanzar(p, 'izq', _alcance(p, 'izq', (-0.2, 0.86, -0.46), 42))
        p, _ = fm.alcanzar(p, 'der', _alcance(p, 'der', (-0.45, -0.25, 0.5), 36))
        p = fm.apuntar_espada(p, (-0.35, -0.7, 0.62))
        _POSES['CARGA'] = p
    return {k: dict(v) for k, v in _POSES['CARGA'].items()}


def pared_recta(a, b, alto, n=24, rep=8.0):
    """Una pared de llamas en linea recta de a a b (por el suelo), u a lo largo."""
    a, b = np.array(a, float), np.array(b, float)
    out = []
    for i in range(n):
        p0, p1 = a + (b - a) * i / n, a + (b - a) * (i + 1) / n
        P = [(p0[0], 0.0, p0[2]), (p1[0], 0.0, p1[2]), (p1[0], alto, p1[2]), (p0[0], alto, p0[2])]
        u0, u1 = i / n * rep, (i + 1) / n * rep
        out.append((P, [(u0, 1), (u1, 1), (u1, 0), (u0, 0)]))
    return out


def linea_llamas(lz, cam, a, b, fase, semilla=0):
    """Una linea de fuego de vanilla (un fuego por bloque) por el suelo de a a b, y el suelo que arde debajo."""
    r = random.Random(semilla)
    a, b = np.array(a, float), np.array(b, float)
    L = np.linalg.norm(b - a)
    d = (b - a) / L
    lado = np.array([-d[2], 0, d[0]]) * 0.28
    P = [tuple(a - lado + [0, 0.06, 0]), tuple(b - lado + [0, 0.06, 0]), tuple(b + lado + [0, 0.06, 0]), tuple(a + lado + [0, 0.06, 0])]
    fe.aditivo(lz, cam, [(P, [(0, 1), (1, 1), (1, 0), (0, 0)])], tex_banda(BRASA), 0.5)
    fuegos = sprites_fuego(2)
    for i in range(int(L)):
        q = a + d * (i + 0.5)
        llama_plana(lz, cam, q, 0.5, 0.95 + 0.25 * r.random(), fuegos[i % 2], 0.45)


def justa_geo(giro_nov=-0.6, alcance=7.0):
    """Donde va cada cosa de la Justa: el pasillo (D), Novilis y su escudo, el emblema y el caballo."""
    D = np.array([0.9, 0.0, 0.44])
    D /= np.linalg.norm(D)
    der = np.array([-D[2], 0.0, D[0]])                       # la derecha del jinete
    N = np.array([6.0, 0.0, 4.0])
    gira = -D + der * giro_nov                              # carga por el pasillo, con el escudo vuelto hacia la lanza
    g_nov = fe.guinada_hacia(N[0], N[2], N[0] + gira[0], N[2] + gira[2])
    Mn = fm.entidad_a_mundo(N[0], 0, N[2], g_nov, ESCALA)
    p = _pose_carga()
    mano = fe.mundo_de(Mn, V, p, 'mano_izq', (0, 6, 0))
    # la mano agarra el escudo por arriba (por detras): el escudo cuelga por delante de las piernas
    asa = (modelo_en(0, 0, 0, g_nov, -4, ESCALA) @ np.array([0, -16, 3.5, 1.0]))[:3]
    C = mano - asa
    Ms = modelo_en(C[0], C[1], C[2], g_nov, -4, ESCALA)
    E = (Ms @ np.array([0, -6, -4.4, 1.0]))[:3]              # el centro del emblema
    # el caballo: la mano del jinete (con la lanza) a 'alcance' del emblema
    g_c = fe.guinada_hacia(0, 0, D[0], D[2])
    M0 = vr.entidad_a_mundo(0, 0, 0, g_c, ESC_CABALLO)
    silla0 = (M0 @ np.array([0, 2.3, 0.5, 1.0]))[:3]
    Mj0 = vr.T(0, silla0[1] - 0.75, 0) @ ne.jugador_a_mundo(silla0[0], silla0[2], g_c)
    agarre0 = punto_jugador(Mj0, JINETE, 'bd', (0, 10.5, 0))
    Hc = np.array([E[0], 0, E[2]]) - D * alcance - np.array([agarre0[0], 0, agarre0[2]])
    return dict(D=D, der=der, N=N, g_nov=g_nov, Mn=Mn, p=p, Ms=Ms, E=E, g_c=g_c, Hc=Hc)


JUSTA_CAM = ((-3.0, -7.0, 2.6), (4.6, 0.0, 4.2), 64)         # (ojo, mira) en (D, der, alto) desde el caballo; fov


def justa(W=1600, H=900, fase=3):
    G = justa_geo()
    D, der, N, g_nov, Mn, p, Ms, E, g_c, Hc = (G[k] for k in ('D', 'der', 'N', 'g_nov', 'Mn', 'p', 'Ms', 'E', 'g_c', 'Hc'))
    (oa, ob, oc), (ma, mb, mc), fov = JUSTA_CAM
    ojo = Hc + D * oa + der * ob + np.array([0, oc, 0])
    mira = Hc + D * ma + der * mb + np.array([0, mc, 0])
    cam = vr.Camara(ojo=tuple(ojo), objetivo=tuple(mira), fov=fov, ancho=W * SS, alto=H * SS)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    # los de fuera del pasillo
    for q, pz in ((Hc - D * 1.6 + der * 10.0, MIRAR), (Hc - D * 2.8 + der * 11.5, QUIETO), (Hc + D * 10.5 + der * 10.5, MIRAR)):
        jugador(lz, cam, q[0], q[2], (Hc[0] + D[0] * 4, Hc[2] + D[2] * 4), pz, niebla=niebla)
    # Novilis y su escudo
    caballero(lz, cam, N[0], N[2], g_nov, p, fase, niebla)
    fe.fuego_cuerpo(lz, cam, Mn, V, p, fase, k=0.7)
    fm.dibujar(lz, cam, nm.quads(ESCUDO_SOL, {}, Ms), fe.LUCES, fe.AMB, niebla, 1.4, fase)
    # el caballo, el jinete y la lanza
    Mh = caballo(lz, cam, Hc[0], Hc[2], g_c, GALOPE, niebla, fase)
    silla = (Mh @ np.array([0, 2.3, 0.5, 1.0]))[:3]
    Mj, pj = jugador(lz, cam, silla[0], silla[2], (silla[0] + D[0], silla[2] + D[2]), JINETE, y=silla[1] - 0.75, niebla=niebla)
    agarre = punto_jugador(Mj, pj, 'bd', (0, 10.5, 0))
    d = (E - agarre) / np.linalg.norm(E - agarre)
    mitad = lanza(lz, cam, agarre - d * 1.3, E - d * 0.1, niebla, fase)
    # el pasillo: dos lineas de llamas
    for s_, sem in ((-1, 1), (1, 2)):
        a = Hc - D * 8.0 + der * 8.0 * s_
        b = N + D * 9.0 + der * 8.0 * s_
        linea_llamas(lz, cam, a, b, fase, sem)
    # el choque: el emblema se enciende
    hacia_cam = (cam.ojo - E) / np.linalg.norm(cam.ojo - E)
    resplandor(lz, cam, E + hacia_cam * 0.3, 3.0, ORO_CLARO, 0.8)
    fe.aditivo(lz, cam, [fe.billboard(E + hacia_cam * 0.4, 1.6, cam, 0.2)], DESTELLO, 1.6)
    fe.aditivo(lz, cam, [fe.billboard(E + hacia_cam * 0.4, 1.3, cam)], CHISPAS_HUECAS, 1.2)
    img = acabar(lz, cam, W, H, fase, 103)
    rotulo(img, cam, E + hacia_cam * 0.4, '¡CLIC EN EL EMBLEMA!', -120, -200, 50, ORO_CLARO)
    rotulo(img, cam, punto_de(CABALLO, Mh, GALOPE, 'cuerpo', (0, 0, -8)), 'CABALLO DE FUEGO', -240, 100, 44, (255, 190, 120))
    rotulo(img, cam, mitad + (E - mitad) * 0.45, 'LANZA DE LUZ', 30, -110, 40, BLANCO)
    q = Hc - D * 1.2 + der * 8.0 + np.array([0, 0.6, 0])
    rotulo(img, cam, q, 'PASILLO DE LLAMAS', 0, -190, 40, (255, 200, 150))
    cola = punto_de(CABALLO, Mh, GALOPE, 'cuerpo', (0, -3, 4))
    estelas(img, cam, cola, cola - D * 3.0, 4, (255, 226, 170))
    guardar(img, 'justa')


# ======================================================================
#  12. Lluvia de Brasas
#
#  Al fondo, Novilis ruge y su sol se agita (crece y echa rayos). Del cielo caen
#  brasas con estela: doradas y rojas, cada una con su marca en el suelo (un
#  aro de oro donde caera la dorada, el sello rojo donde caera la roja). Dos
#  jugadores corren a ponerse debajo de una dorada; otro salta para apartarse
#  de una roja que acaba de estallar en llamas. Arriba, la barra del jefe con
#  la Corona del Sol al 60 %.
# ======================================================================
ROJA = (236, 52, 32)
ROJA_CLARA = (255, 160, 120)
fm.registrar('brasa_oro', tex_moteado(((255, 236, 150), (255, 214, 90), (255, 250, 210)), 91), pleno=True)
fm.registrar('brasa_roja', tex_moteado(((226, 40, 24), (186, 24, 16), (255, 96, 44)), 92), pleno=True)


def brasa(lz, cam, p, dorada, cola, tam=0.5, k=1.0):
    """Una brasa que cae: un cubo encendido, su resplandor y la estela (de p hacia p + cola)."""
    p = np.array(p, float)
    color, claro, mat = (ORO, ORO_CLARO, 'brasa_oro') if dorada else (ROJA, ROJA_CLARA, 'brasa_roja')
    pts = [p + np.array(cola, float) * t for t in np.linspace(0, 1, 14)]
    haz_oro(lz, cam, pts, lambda t: tam * 0.5 * (1 - 0.85 * t), 0.85 * k, color, claro)
    h = tam / 2
    fm.dibujar(lz, cam, fe.caja_mundo(p[0] - h, p[1] - h, p[2] - h, tam, tam, tam, mat), fe.LUCES, fe.AMB, None, 0.7, 2)
    resplandor(lz, cam, p, tam * 2.6, color, 0.55 * k)


def marca(lz, cam, x, z, dorada, R=1.25):
    """Donde va a caer: un aro de oro (ponte debajo) o el sello rojo (apartate)."""
    if dorada:
        aro_suelo(lz, cam, x, z, R, ORO, 0.9, 0.7, 0.09, 12, 70)
    else:
        fe.trans(lz, cam, fe.suelo_cuad(x, z, R, 0.08), fe.tex_sello(ROJA, relleno=80), 0.85, None, 0.6)


def rayos_sol(img, cam, p, R, n=18, largo=2.2, color=ORO_CLARO, semilla=0):
    """Los rayos del sol que se agita: rayas que salen del disco (sobre la foto)."""
    sx, sy, z = cam.proyectar(p)
    sx, sy = sx / SS, sy / SS
    rp = cam.foco / SS * R / z
    r = random.Random(semilla)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for k in range(n):
        a = TAU * k / n + r.uniform(-0.08, 0.08)
        l = rp * (1.0 + largo * r.uniform(0.5, 1.0) * (1.0 if k % 2 == 0 else 0.55))
        d.line([(sx + math.cos(a) * rp * 0.95, sy + math.sin(a) * rp * 0.95), (sx + math.cos(a) * l, sy + math.sin(a) * l)],
               fill=(*color, 200), width=max(3, int(rp * 0.14)))
    halo = capa.filter(ImageFilter.GaussianBlur(max(2, rp * 0.12)))
    img.alpha_composite(halo)
    img.alpha_composite(halo)
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(1)))


def barra_jefe(img, cx, y0, esc=2, vida=0.62, corona=0.6):
    """La barra de Novilis del juego (las texturas de textures/gui, como las monta NovilisBarraHud,
    fase II) y debajo, en la fila de las vistas, la Corona del Sol llenandose de oro."""
    gui = os.path.join(fe.TEX, 'gui')

    def t(nombre):
        return Image.open(os.path.join(gui, nombre + '.png')).convert('RGBA')

    base = Image.new('RGBA', (240, 58), (0, 0, 0, 0))
    base.alpha_composite(t('novilis_barra_marco_2'), (0, 0))
    rell = t('novilis_barra_relleno_2')
    lleno, x = round(190 * vida), 0
    while x < lleno:
        w = min(64, lleno - x)
        base.alpha_composite(rell.crop((0, 0, w, 9)), (40 + x, 22))
        x += w
    for corte in (0.75, 0.5, 0.25):
        base.alpha_composite(t('novilis_barra_rayo_roto' if vida < corte else 'novilis_barra_rayo_2'),
                             (40 + round(190 * corte) - 3, 17))
    base.alpha_composite(t('novilis_barra_nucleo_2'), (7, 14))
    base.alpha_composite(t('novilis_barra_nombre'), (92, 9))
    rot = np.array(t('novilis_barra_fase_2')).astype(float)
    rot[..., :3] = rot[..., :3] * np.array([0xFF, 0xC2, 0x3A]) / 255.0
    base.alpha_composite(Image.fromarray(np.clip(rot, 0, 255).astype(np.uint8)), (167, 8))
    base.alpha_composite(t('novilis_barra_ofrenda_sol'), (40, 35))
    base.alpha_composite(t('novilis_barra_carga_losa'), (84, 42))
    w = round(132 * corona)
    oro = np.zeros((5, w, 4), np.uint8)
    for fila, c in enumerate(((255, 246, 200), (255, 226, 120), (255, 200, 70), (240, 168, 46), (206, 130, 34))):
        oro[fila, :] = (*c, 255)
    oro[:, -1] = (255, 252, 236, 255)
    base.alpha_composite(Image.fromarray(oro), (85, 43))
    grande = base.resize((240 * esc, 58 * esc), Image.NEAREST)
    x0 = int(cx - 120 * esc)
    img.alpha_composite(grande, (x0, y0))
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 11 * esc)
    d = ImageDraw.Draw(img)
    tx, ty = x0 + (84 + 134 + 5) * esc, y0 + 37 * esc
    texto = 'Corona del Sol 60 %'
    d.text((tx + esc, ty + esc), texto, font=f, fill=(40, 24, 10, 255))
    d.text((tx, ty), texto, font=f, fill=(255, 224, 122, 255))


def brasas_escena(W=1600, H=900, fase=2):
    cam = vr.Camara(ojo=(-7.0, 3.0, -21.0), objetivo=(-1.0, 5.6, -7.0), fov=60, ancho=W * SS, alto=H * SS)
    F, R = marco_camara(cam)
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = fe.Niebla(30, 70)
    fe.suelo(lz, cam, niebla, fase)
    fe.braseros(lz, cam, niebla, fase)
    base = np.array([cam.ojo[0], 0.0, cam.ojo[2]])
    G = base + F * 9.5 - R * 1.6                       # donde cae la dorada que van a coger
    G2 = base + F * 17.0 - R * 7.5                     # otra dorada, mas lejos
    Rj = base + F * 10.5 + R * 4.6                     # la roja que acaba de estallar
    Rj2 = base + F * 16.0 + R * 1.5                    # otra roja que llega
    N = base + F * 34.0 + R * 9.0
    # Novilis ruge al fondo
    p = pose('GRITO')
    M = caballero(lz, cam, N[0], N[2], fe.guinada_hacia(N[0], N[2], G[0], G[2]), p, fase, niebla)
    fe.fuego_cuerpo(lz, cam, M, V, p, fase, k=0.8)
    sol = fe.mundo_de(M, V, p, 'halo')
    # los jugadores: dos corren a la dorada, otro salta lejos de la roja
    for q, mira in ((G - R * 2.6 - F * 1.2, G), (G + R * 2.2 + F * 1.6, G)):
        jugador(lz, cam, q[0], q[2], (mira[0], mira[2]), CORRER, niebla=niebla)
    salta = Rj - R * 2.4 - F * 1.6
    jugador_inclinado(lz, cam, salta + np.array([0, 0.7, 0]), fe.guinada_hacia(salta[0], salta[2], Rj[0], Rj[2]), -28, SALTO,
                      niebla)
    # las marcas del suelo
    marca(lz, cam, G[0], G[2], True)
    marca(lz, cam, G2[0], G2[2], True, 1.1)
    marca(lz, cam, Rj2[0], Rj2[2], False, 1.2)
    # la roja que ha caido: estalla en llamas
    fe.explosion(lz, cam, Rj + np.array([0, 0.05, 0]), 1.5, 4, 7, lava=False, k=0.9)
    fuegos = sprites_fuego(2)
    for i, (a, b) in enumerate(((-0.6, 0.2), (0.5, -0.3), (0.1, 0.6), (-0.2, -0.7))):
        llama_plana(lz, cam, Rj + R * a + F * b, 0.45, 1.0 + 0.3 * (i % 2), fuegos[i % 2], 0.55)
    # el sol se agita: crece, arde y escupe brasas
    resplandor(lz, cam, sol, 9.0, BRASA, 0.5)
    fe.sol_mini(lz, cam, sol, 2.4, fase, 5, 1.0)
    # las brasas: la estela apunta de vuelta hacia su sol
    r = random.Random(12)
    caen = [(G + np.array([0, 2.3, 0]), True, 0.6), (G2 + np.array([0, 6.5, 0]), True, 0.5), (Rj2 + np.array([0, 5.0, 0]), False, 0.5)]
    # la guia: un hilo de luz de cada brasa a su marca
    for q, c, cc in ((G + np.array([0, 2.3, 0]), ORO, ORO_CLARO), (G2 + np.array([0, 6.5, 0]), ORO, ORO_CLARO),
                     (Rj2 + np.array([0, 5.0, 0]), ROJA, ROJA_CLARA)):
        haz_oro(lz, cam, [q + (np.array([q[0], 0.1, q[2]]) - q) * t for t in np.linspace(0, 1, 8)], 0.035, 0.6, c, cc)
    for _ in range(9):
        q = base + F * r.uniform(10, 28) + R * r.uniform(-12, 12) + np.array([0, r.uniform(7, 15), 0])
        caen.append((q, r.random() < 0.5, 0.45))
    for k in range(4):                                  # recien salidas del sol, subiendo
        a = TAU * k / 4 + 0.4
        q = sol + np.array([math.cos(a) * 3.2, 2.0 + 1.5 * abs(math.sin(a)), math.sin(a) * 1.5])
        caen.append((q, k % 2 == 0, 0.45))
    for q, dorada, tam in caen:
        hacia = (sol - q) * 0.25 + np.array([0, 2.2, 0])
        brasa(lz, cam, q, dorada, hacia / np.linalg.norm(hacia) * 2.8, tam)
    img = acabar(lz, cam, W, H, fase, 104)
    rayos_sol(img, cam, sol, 2.6, 20, 2.0, ORO_CLARO, 3)
    barra_jefe(img, W / 2, 8, 2, 0.62, 0.6)
    rotulo(img, cam, G + np.array([0, 2.3, 0]), 'DORADA: ¡CÓGELA!', -60, -150, 48, ORO_CLARO)
    rotulo(img, cam, Rj + np.array([0, 0.8, 0]), 'ROJA: ¡APÁRTATE!', 80, -120, 48, ROJA_CLARA)
    rotulo(img, cam, sol, 'SU SOL SE AGITA', -120, 40, 40, (255, 200, 150))
    guardar(img, 'brasas')


ESCENAS = {'duelo': duelo, 'armadura': armadura, 'espejos': espejos, 'llama': llama,
           'sombra': sombra, 'estandarte': estandarte, 'escuderos': escuderos, 'sol_caido': sol_caido,
           'choque': choque, 'forja': forja, 'justa': justa, 'brasas': brasas_escena}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()

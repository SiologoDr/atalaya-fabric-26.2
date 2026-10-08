"""
Poster promocional de Novilis, el Caballero Solar, en el Altar del Sol, con
el Dios de la Guerra en marcha. Presenta al jefe: el grande a la derecha, su
nombre a la izquierda y nada mas (ni jugadores ni lista de ataques).

Novilis en la fase IV (Dios de la Guerra), casi de frente y con la camara
baja: la espada clavada a su lado, los brazos abiertos en alto y la cabeza
baja, mirando a quien mira, con el halo de rayos detras del yelmo. Le arde el
fuego carmesi del Dios de la Guerra (yelmo, hombreras, punos, espalda y la
hoja clavada) y sobre el halo flota su sol, carmesi, que echa haces por el
humo. Ya ha lanzado dos soles: cada uno vuela en arco con su estela hacia su
sello carmesi del suelo; el tercer sello espera. Detras, el altar de basalto
con el sol de oro en el suelo, los braseros, los volcanes y un cielo que arde.
Arriba, su barra de jefe tal cual sale en el juego.

Todo lo que sale esta hecho para el mod: la malla del juego con su atlas y su
capa de brillo de la fase IV (novilis_juego.py) en la pose del Dios de la
Guerra (novilis_juego_anim.py), las lenguas de fuego de NovilisLlamasLayer,
su sol, los sellos y los soles lanzados como NovilisDibujo, SelloSolRenderer
y SolNovilisRenderer (con sus texturas, de novilis_extras.py), el altar y los
braseros de la ficha (fuego_escenas.py), los volcanes en bloques, las
particulas propias y la barra. Las fuentes son las del sistema.

Uso: python novilis_poster.py <raiz del proyecto> <salida.png> [escala]
"""
import math, os, sys, random, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ, SALIDA = sys.argv[1], sys.argv[2]
ESCALA = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# los __pycache__ de los generadores estan en git: importarlos no los reescribe
sys.dont_write_bytecode = True
_argv = sys.argv
sys.argv = [_argv[0], RAIZ, tempfile.mkdtemp()]
import vigia_render as vr
import fuego_escenas as fe
import novilis_juego as nj
import novilis_juego_anim as na
sys.argv = _argv

A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
P = os.path.join(A, 'particle')
GUI = os.path.join(A, 'gui')
ENT = os.path.join(A, 'entity/novilis')
FUENTES = 'C:/Windows/Fonts/'
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
SS = 2
FASE = 4
TAU = math.tau

CARMESI = (0xFF, 0x2A, 0x3A)          # el fuego de la fase IV y del Dios (NovilisDibujo.COLOR_FASE)
ASCUA = (255, 150, 84, 255)
LLAMA = (255, 184, 72, 255)
BLANCO = (252, 244, 236, 255)
GRIS = (214, 188, 176, 255)


def fuente(nombre, tam):
    return ImageFont.truetype(FUENTES + nombre, int(tam * ESCALA))


def px(n):
    return int(round(n * ESCALA))


def claro(c, k):
    """NereaDibujo.claro: el color, k hacia el blanco."""
    return tuple(int(v + (255 - v) * k) for v in c)


def _vec(nombre, defecto):
    return tuple(float(v) for v in os.environ.get(nombre, defecto).split(','))


# ----------------------------------------------------------------------
#  La pose: el Dios de la Guerra abierto de brazos (T_DIOS_MARCA), antes
#  del primer lanzamiento, con la espada ya clavada a su derecha. La cabeza,
#  baja hacia quien mira (en la animacion mira al cielo): asi el halo le
#  rodea el yelmo de frente.
# ----------------------------------------------------------------------
T_POSE = 0.9
GIRO_CABEZA = {'cabeza': (40.0, -6.0, 0.0), 'cuello': (10.0, 0.0, 0.0)}


def hornear():
    # la espada clavada se coloca con la de la Ofrenda, como al exportar el juego
    for nombre in ('OFRENDA', 'DIOS'):
        na.hornear(nombre)
    na.ajustar_espada_suelta()


def pose_poster():
    pose = na.pose_hoja('DIOS', T_POSE)
    for pieza, rot in GIRO_CABEZA.items():
        d = pose.setdefault(pieza, {})
        d['rot'] = tuple(a + b for a, b in zip(d.get('rot', (0, 0, 0)), rot))
    return pose


# ----------------------------------------------------------------------
#  Escena: camara baja (a la altura de los ojos de un jugador) y bastante
#  cerca, mirando hacia arriba: se le ve entero, de los pies a su sol.
# ----------------------------------------------------------------------
NOVILIS_EN = (0.0, 0.0, 0.0)
GUINADA = float(os.environ.get('GUINADA', '-16'))
CAM = vr.Camara(ojo=_vec('CAM_OJO', '12.0,4,-33'), objetivo=_vec('CAM_OBJ', '11.5,10.8,-3.8'),
                fov=float(os.environ.get('CAM_FOV', '44')), ancho=W * SS, alto=H * SS)


def hacia(derecha, arriba, fondo):
    """Una direccion del mundo dada en la base de la camara (derecha, arriba y
    hacia el fondo de la imagen)."""
    d = CAM.r * derecha + np.array([0.0, 1.0, 0.0]) * arriba + np.array([CAM.f[0], 0.0, CAM.f[2]]) * fondo
    return tuple(d / np.linalg.norm(d))


LUCES = [
    (hacia(-0.45, 0.45, -0.75), (1.0, 0.72, 0.56), 0.85, 'llave'),   # las brasas del altar, por delante: la armadura se lee
    (hacia(0.1, 1.0, 0.25), (1.0, 0.34, 0.32), 0.7, 'llave'),        # su sol, encima
    (hacia(0.6, 0.35, 0.75), (1.0, 0.52, 0.2), 1.5, 'contra'),       # el horizonte que arde, detras
    (hacia(-0.85, 0.25, 0.45), (1.0, 0.18, 0.24), 1.1, 'contra'),    # el carmesi del Dios, por la izquierda
]
AMBIENTE = (0.2, 0.1, 0.1)


class Niebla:
    """El humo rojizo del altar: lo lejano se funde con el horizonte que arde."""
    color = (0.34, 0.09, 0.06)

    def __init__(self, ini=30.0, largo=110.0, tope=0.9):
        self.ini, self.largo, self.tope = ini, largo, tope

    def __call__(self, z):
        return np.clip((z - self.ini) / self.largo, 0, self.tope)


def sumar(base, capa, k=1.0):
    f = np.array(base).astype(float)
    f[..., :3] = np.clip(f[..., :3] + np.array(capa).astype(float)[..., :3] * k, 0, 255)
    return Image.fromarray(f.astype(np.uint8))


def sprite(nombre, ancho, alto=None):
    return Image.open(os.path.join(P, nombre)).convert('RGBA').resize((max(1, ancho), max(1, alto or ancho)), Image.NEAREST)


def pantalla(p):
    """Del mundo al poster: (x, y) en pixeles de la imagen final y la profundidad."""
    sx, sy, z = CAM.proyectar(np.asarray(p, float))
    return sx / SS, sy / SS, z


def tam_px(bloques, prof):
    """Cuantos pixeles del poster mide algo de 'bloques' a 'prof' de la camara."""
    return max(2, int(bloques * CAM.foco / SS / max(prof, 0.5)))


def desproyectar(sx, sy, prof):
    """El punto del mundo que cae en (sx, sy) del poster (medido en 1920x1080) a "prof" bloques de la camara."""
    x = (sx * ESCALA * SS - CAM.W / 2) * prof / CAM.foco
    y = (CAM.H / 2 - sy * ESCALA * SS) * prof / CAM.foco
    return CAM.ojo + CAM.f * prof + CAM.r * x + CAM.u * y


def en_suelo(sx, sy):
    """El punto del suelo (y=0) que cae en (sx, sy) del poster (medido en 1920x1080)."""
    d = desproyectar(sx, sy, 1.0) - CAM.ojo
    return CAM.ojo + d * (-CAM.ojo[1] / d[1])


def a_imagen(arr):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    return im.resize((W, H), Image.LANCZOS)


def flotante(im):
    return np.array(im).astype(float) / 255.0


def textura(nombre):
    return vr.cargar(os.path.join(ENT, nombre + '.png'))


def tenir(t, rgb, k=1.0):
    """Una textura en grises, del color rgb (como el color de vertice del juego)."""
    t = t.astype(float).copy()
    t[..., :3] *= np.array(rgb, float) / 255.0 * k
    return np.clip(t, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------
#  El fuego del Dios de la Guerra (NovilisLlamasLayer): lenguas pegadas a
#  cada hueso, siempre de cara a quien mira y hacia arriba del mundo. La
#  llama es una fila de 8 cuadros; cada lengua, en el suyo.
# ----------------------------------------------------------------------
LENGUAS = [   # hueso, punto (px del hueso), alto y ancho (px)
    ('cabeza', (0, -28, 0), 54, 26), ('cabeza', (9, -22, 3), 32, 16), ('cabeza', (-9, -22, 3), 32, 16),
    ('hombro_izq', (5, -12, 0), 44, 24), ('hombro_der', (-5, -12, 0), 44, 24),
    ('hombro_izq', (11, -8, 9), 30, 16), ('hombro_der', (-11, -8, 9), 30, 16),
    ('hombro_izq', (2, -10, -9), 26, 14), ('hombro_der', (-2, -10, -9), 26, 14),
    ('mano_izq', (0, 5, -2), 28, 17),
    ('torso', (0, -44, 14), 34, 28), ('torso', (12, -40, 13), 26, 18), ('torso', (-12, -40, 13), 26, 18),
]
HOJA = (28, 38, 48, 58, 68, 78)     # lo largo de la hoja clavada (px desde el agarre)
K_DIOS = 1.15                       # el Dios de la Guerra arde mas que la Furia
EDAD = 37.0                         # el tick del fotograma (los cuadros de la llama y su latido)

_LLAMA = textura('llama_sprite')


def cuadro_llama(i, rgb, k=1.0):
    return tenir(_LLAMA[:, i * 32:(i + 1) * 32], rgb, k)


def lenguas(punto):
    """Los cuadrilateros de cada lengua: (puntos, uv, cuadro, alma)."""
    out = []
    lista = [(h, c, al * K_DIOS, an * K_DIOS) for h, c, al, an in LENGUAS]
    lista += [('espada_suelta', (0, y, 0), 22 * K_DIOS, 13 * K_DIOS) for y in HOJA]
    arriba = np.array([0.0, 1.0, 0.0])
    for i, (hueso, local, alto, ancho) in enumerate(lista, start=1):
        c = punto(hueso, local)
        h = alto / 16 * nj.ESCALA * (0.9 + 0.12 * math.sin(EDAD * 0.37 + i * 1.7))
        w = ancho / 16 * nj.ESCALA
        ojo = CAM.ojo - c
        lado = np.cross(arriba, ojo)
        lado = lado / np.linalg.norm(lado)
        n = int(EDAD / 1.4 + i * 3) % 8
        for k_ancho, k_alto, alma in ((1.0, 1.0, False), (0.55, 0.6, True)):
            b = c - arriba * h * k_alto * 0.14
            a = c + arriba * h * k_alto * 0.86
            l = lado * w * 0.5 * k_ancho
            out.append(([b - l, b + l, a + l, a - l], [(0, 1), (1, 1), (1, 0), (0, 0)], n, alma))
    return out


# ----------------------------------------------------------------------
#  Los soles del Dios (SolNovilisRenderer): vuelan en arco desde la mano
#  hasta su zona, con la estela detras; la zona lleva el sello carmesi
#  (SelloSolRenderer). Las zonas se dan en el poster (x, y del suelo).
# ----------------------------------------------------------------------
ZONAS = [(_vec('ZONA_A', '820,1012')), (_vec('ZONA_B', '1745,968')), (_vec('ZONA_C', '470,915'))]
RADIO_ZONA = 6.0
# los braseros del altar que salen (fuego_escenas.BRASEROS): sin el de delante a la izquierda, que tapa el texto
BRASEROS = (0, 1, 2, 3, 4, 5)
ARCO = 7.0
R_SOL_DIOS = 0.9
R_SOL = 2.2                         # su sol, sobre el halo
# (mano de la que sale, zona, cuanto lleva del vuelo)
LANZADOS = [('mano_der', 0, 0.58), ('mano_izq', 1, 0.8)]

TEX_SOL = textura('sol')
TEX_SELLO = textura('sello')
TEX_ESTELA = np.ascontiguousarray(np.transpose(textura('estela'), (1, 0, 2)))   # la cabeza en u = 0


def vuelo(desde, hasta, k):
    """SolNovilisEntity.enVuelo: la recta y el arco encima."""
    return desde + (hasta - desde) * k + np.array([0.0, ARCO * 4 * k * (1 - k), 0.0])


def sol_3d(lz, p, r, giro=0.0, k=1.0):
    """NovilisDibujo.sol, sumado a la luz: el resplandor, la corona y el nucleo."""
    for tam, col, al, g in ((2.2, CARMESI, 0.55, 1.0), (1.3, claro(CARMESI, 0.35), 1.0, -2.5), (0.8, claro(CARMESI, 0.75), 1.0, 4.0)):
        fe.aditivo(lz, CAM, [fe.billboard(p, r * tam, CAM, giro * g)], tenir(TEX_SOL, col, al), 0.85 * k)


# ----------------------------------------------------------------------
#  Fondo: el cielo que arde, el humo y los volcanes en bloques
# ----------------------------------------------------------------------
def ruido(w, h, celdas, semilla):
    g = np.random.default_rng(semilla).random((celdas[1] + 1, celdas[0] + 1))
    return flotante(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC))


def cielo(horiz, sol):
    yy, xx = np.mgrid[0:H, 0:W]
    t = np.clip(yy / max(horiz, 1), 0, 1)
    arriba, medio, abajo = np.array([0.03, 0.008, 0.012]), np.array([0.2, 0.025, 0.035]), np.array([0.78, 0.22, 0.07])
    t1, t2 = np.clip(t / 0.62, 0, 1), np.clip((t - 0.62) / 0.38, 0, 1)
    col = np.where((t < 0.62)[..., None], arriba + (medio - arriba) * t1[..., None] ** 1.2,
                   medio + (abajo - medio) * t2[..., None] ** 1.6)
    # el humo: bancos que suben del horizonte, encendidos por abajo
    n1 = ruido(W, H, (12, 7), 4) * 0.6 + ruido(W, H, (38, 20), 5) * 0.4
    bancos = np.clip(n1 * 1.3 - 0.45, 0, 1) * np.clip(t * 1.2 - 0.15, 0, 1)
    col += bancos[..., None] * np.array([0.32, 0.07, 0.04]) * 0.9
    oscuro = np.clip(ruido(W, H, (9, 5), 6) - 0.55, 0, 1) * (1 - t)
    col *= (1 - oscuro[..., None] * 0.7)
    # su sol tine el aire: un resplandor carmesi grande alrededor
    sx, sy = sol
    d = np.hypot((xx - sx) / W, (yy - sy) / W)
    col += np.exp(-(d / 0.16) ** 2)[..., None] * np.array([0.5, 0.06, 0.08]) * 0.35
    col += np.exp(-(d / 0.45) ** 2)[..., None] * np.array([0.12, 0.02, 0.025])
    return col


def haces(sol, n=18, semilla=3):
    """Haces de luz que bajan de su sol abriendose en abanico por el humo."""
    r = random.Random(semilla)
    capa = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(capa)
    gx, gy = sol
    for _ in range(n):
        a = r.uniform(math.pi * 0.08, math.pi * 0.92)
        abre = r.uniform(0.012, 0.04)
        L = W * 1.4
        d.polygon([(gx, gy), (gx + math.cos(a - abre) * L, gy + math.sin(a - abre) * L),
                   (gx + math.cos(a + abre) * L, gy + math.sin(a + abre) * L)], fill=r.randint(24, 64))
    capa = flotante(capa.filter(ImageFilter.GaussianBlur(px(22))))
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.hypot(xx - gx, yy - gy) / W
    return capa * np.exp(-dd * 1.6)


def volcanes(horiz, semilla=12):
    """Los volcanes del horizonte, en bloques: tres capas que se oscurecen
    hacia delante; los del fondo tienen el crater encendido. Devuelve
    [(mascara, tono, lava)] de atras a delante."""
    r = random.Random(semilla)
    capas = []
    for alto, bloque_, tono, n_lava in ((px(230), px(18), 0.95, 3), (px(150), px(26), 0.7, 0), (px(85), px(36), 0.5, 0)):
        m = Image.new('L', (W, H), 0)
        lava = Image.new('L', (W, H), 0)
        d, dl = ImageDraw.Draw(m), ImageDraw.Draw(lava)
        x = -px(80)
        conos = []
        while x < W + px(80):
            ancho = r.randint(9, 18) * bloque_
            cima = horiz - alto * r.uniform(0.35, 1.0)
            cx = x + ancho / 2
            boca = r.randint(1, 2) * bloque_
            # escalones: cada uno un bloque mas ancho por lado, hasta el horizonte
            y, medio = cima, boca
            while y < horiz + px(20):
                d.rectangle((cx - medio, y, cx + medio, horiz + px(20)), fill=255)
                y += bloque_ * r.choice((0.5, 0.75, 1.0))
                medio += bloque_ * r.choice((0.5, 1.0, 1.0, 1.5))
            conos.append((cx, cima, boca))
            x += ancho * r.uniform(0.5, 0.9)
        for cx, cima, boca in r.sample(conos, min(n_lava, len(conos))):
            # el crater: la boca encendida y el humo que alumbra por encima
            dl.rectangle((cx - boca, cima - bloque_ * 0.4, cx + boca, cima + bloque_ * 0.3), fill=255)
        capas.append((flotante(m.filter(ImageFilter.GaussianBlur(max(1, px(1.5))))), tono,
                      flotante(lava.filter(ImageFilter.GaussianBlur(max(1, px(6)))))))
    return capas


# ----------------------------------------------------------------------
#  La barra de jefe
# ----------------------------------------------------------------------
def barra_jefe(escala, vida=0.2, rastro=0.235):
    """La barra de jefe de Novilis (novilis_hud.py, 240x44), compuesta igual
    que en NovilisBarraHud en la fase IV: el marco de acero quemado con las
    lenguas de fuego, la lava carmesi con su frente encendido y la chispa, el
    rastro claro del ultimo golpe, los rayos de sol de las muescas (rotos los
    que ya paso), el yelmo ante su sol y los rotulos de pixel."""
    def tex(n):
        return Image.open(os.path.join(GUI, n + '.png')).convert('RGBA')

    def tinte(im, rgb):
        return Image.fromarray(tenir(np.array(im), rgb))
    hx, hy, ancho, alto = 40, 22, 190, 9                    # el hueco (HUECO_X, HUECO_Y...)
    medio, claro_, fuego = (0xFF, 0x9A, 0x84), (0xFF, 0xE4, 0xD8), CARMESI    # MEDIO, CLARO y FUEGO de la IV
    lienzo = tex(f'novilis_barra_marco_{FASE}').copy()
    d = ImageDraw.Draw(lienzo, 'RGBA')
    lleno, hasta = round(ancho * vida), round(ancho * rastro)
    if hasta > lleno:
        d.rectangle((hx + lleno, hy, hx + hasta - 1, hy + alto - 1), fill=(0xFF, 0xF2, 0xD8, 0xD8))
    relleno = tex(f'novilis_barra_relleno_{FASE}')
    for x in range(0, lleno, 64):
        lienzo.alpha_composite(relleno.crop((0, 0, min(64, lleno - x), alto)), (hx + x, hy))
    d = ImageDraw.Draw(lienzo, 'RGBA')
    x = hx + lleno
    if lleno >= 3:                                          # el frente (NovilisBarraHud.frente)
        d.rectangle((x - 3, hy, x - 3, hy + 2), fill=(*medio, 255))
        d.rectangle((x - 2, hy, x - 2, hy + 4), fill=(*claro_, 255))
        d.rectangle((x - 2, hy + 5, x - 2, hy + alto - 1), fill=(*medio, 255))
        d.rectangle((x - 1, hy, x - 1, hy + alto - 1), fill=(*claro_, 255))
        d.point((x - 1, hy - 1), fill=(*medio, 255))
        d.point((x - 2, hy - 3), fill=(*fuego, 255))        # la chispa que salta
    for corte in (0.75, 0.5, 0.25):
        nombre = 'novilis_barra_rayo_roto' if vida < corte else f'novilis_barra_rayo_{FASE}'
        lienzo.alpha_composite(tex(nombre), (hx + round(ancho * corte) - 3, hy - 5))
    lienzo.alpha_composite(tex(f'novilis_barra_nucleo_{FASE}'), (19 - 12, 26 - 12))
    lienzo.alpha_composite(tex('novilis_barra_nombre'), (92, 9))
    lienzo.alpha_composite(tinte(tex(f'novilis_barra_fase_{FASE}'), CARMESI), (167, 8))
    return lienzo.resize((lienzo.width * escala, lienzo.height * escala), Image.NEAREST)


# ----------------------------------------------------------------------
#  Composicion (todo medido en el poster de 1920x1080)
# ----------------------------------------------------------------------
def main():
    hornear()
    lz = fe.Lienzo(W * SS, H * SS)
    niebla = Niebla()
    r = random.Random(9)

    # el altar: el suelo de basalto con el sol de oro, y los braseros con su fuego naranja
    fe.suelo(lz, CAM, niebla, fase=FASE, ext=96, desde=int(CAM.ojo[2]) - 2, prof=170, bloque_lejos=4)
    fe.braseros(lz, CAM, niebla, fase=1, cuales=BRASEROS)

    # Novilis: la malla del juego con su atlas y su capa de brillo de la fase IV
    uv, alto_atlas = nj.empaquetar()
    tex = textura(f'novilis_f{FASE}')
    brillo = textura(f'novilis_brillo_f{FASE}')
    pose = pose_poster()
    M = vr.entidad_a_mundo(*NOVILIS_EN, GUINADA, nj.ESCALA)
    cuerpo = nj.quads(pose, uv, alto_atlas, M)
    for Pq, UVq, _ in cuerpo:
        luz = vr.iluminar(vr.normal(Pq), CAM, np.mean(Pq, axis=0), LUCES, AMBIENTE)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, luz, brillo, None)

    Ms = nj.matrices(pose)

    def punto(pieza, local=(0, 0, 0)):
        return (M @ Ms[pieza] @ np.array([*local, 1.0]))[:3]
    k_px = nj.ESCALA / 16
    sol = (M @ np.array([0.0, 24.016 - 24.5 / k_px, 1.5 / k_px, 1.0]))[:3]     # SOL_PROPIO: 24,5 arriba, 1,5 detras
    yelmo = punto('cabeza', (0, -8, -6))

    # la silueta de Novilis: lo que pasa por detras se recorta con ella
    solo = fe.Lienzo(W * SS, H * SS)
    for Pq, UVq, _ in cuerpo:
        for tri in ((0, 1, 2), (0, 2, 3)):
            solo.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, np.ones(3))
    figura = flotante(a_imagen(solo.alfa))

    # --- la luz: lo que solo brilla, tapado por lo opaco ---
    luz = fe.Lienzo(W * SS, H * SS)
    luz.z = lz.z.copy()
    # el fuego del Dios de la Guerra
    for pts, uvs, n, alma in lenguas(punto):
        t = cuadro_llama(n, claro(CARMESI, 0.4), 0.75) if alma else cuadro_llama(n, CARMESI)
        fe.aditivo(luz, CAM, [(pts, uvs)], t, 0.85)
    # los sellos de las tres zonas: el de fuera y el de dentro, que giran al reves
    zonas = [en_suelo(*z) for z in ZONAS]
    for i, q in enumerate(zonas):
        giro = 0.7 + i * 1.3
        m = RADIO_ZONA * 1.08
        fe.aditivo(luz, CAM, fe.suelo_cuad(q[0], q[2], m, 0.06, giro), tenir(TEX_SELLO, claro(CARMESI, 0.1)), 1.4)
        fe.aditivo(luz, CAM, fe.suelo_cuad(q[0], q[2], m * 0.55, 0.08, -giro * 1.6), tenir(TEX_SELLO, claro(CARMESI, 0.5)), 1.1)
    # los soles lanzados: la estela del arco y el sol
    volando = []
    for mano, z, k in LANZADOS:
        desde, hasta = punto(mano, (0, 4, -2)), zonas[z]
        p = vuelo(desde, hasta, k)
        cola = [vuelo(desde, hasta, max(0.0, k - 0.32 * j / 10)) for j in range(11)]
        fe.aditivo(luz, CAM, fe.cinta3d(cola, lambda s: R_SOL_DIOS * 0.75 * (1 - 0.6 * s), CAM), tenir(TEX_ESTELA, CARMESI), 1.1)
        sol_3d(luz, p, R_SOL_DIOS * 1.1, giro=k * 3, k=0.6)
        volando.append((p, cola, desde, hasta))

    # --- a resolucion final ---
    color = flotante(a_imagen(lz.color))
    alfa = flotante(a_imagen(lz.alfa))[..., None]
    emis = a_imagen(lz.emis)
    llamas = a_imagen(luz.emis)

    lejos = np.array([CAM.ojo[0] + CAM.f[0] * 400, 0.0, CAM.ojo[2] + CAM.f[2] * 400])
    horiz = CAM.proyectar(lejos)[1] / SS
    sx_sol, sy_sol, z_sol = pantalla(sol)
    fondo = cielo(horiz, (sx_sol, sy_sol))
    fondo += haces((sx_sol, sy_sol))[..., None] * np.array([1.0, 0.3, 0.26]) * 0.45
    # los volcanes del horizonte, recortados contra el cielo; la lava encendida
    for m, tono, lava in volcanes(horiz):
        fondo = fondo * (1 - m[..., None]) + m[..., None] * np.array(Niebla.color) * tono * 0.55
        fondo += lava[..., None] * np.array([1.0, 0.42, 0.12]) * 0.9 * tono
    yy, xx = np.mgrid[0:H, 0:W]
    # el contraluz: el aire brilla justo detras de su silueta
    halo = flotante(Image.fromarray((figura * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(px(50))))
    fondo += halo[..., None] * np.array([0.45, 0.1, 0.08]) * 0.3

    # su sol, sobre el halo (NovilisDibujo.sol): el resplandor, la corona y el nucleo
    fondo_img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    rp = tam_px(R_SOL, z_sol)
    for tam, col, al, giro in ((2.2, CARMESI, 0.55, 8), (1.3, claro(CARMESI, 0.35), 1.0, -21), (0.8, claro(CARMESI, 0.75), 1.0, 33)):
        lado = max(2, int(rp * tam * 2))
        s = Image.fromarray(tenir(TEX_SOL, col)).resize((lado, lado), Image.NEAREST).rotate(giro, Image.NEAREST)
        s.putalpha(s.getchannel('A').point(lambda v: int(v * al * 235 / 255)))
        fondo_img.alpha_composite(s, (int(sx_sol - s.width / 2), int(sy_sol - s.height / 2)))
    f = flotante(fondo_img)[..., :3]

    f = color * alfa + f * (1 - alfa)
    # humo bajo que corre por el altar
    bruma = np.exp(-((yy - horiz + px(14)) / px(60)) ** 2) * (0.55 + 0.45 * ruido(W, H, (24, 6), 6))
    f += np.array([0.3, 0.08, 0.05])[None, None] * bruma[..., None] * 0.6 * (1 - figura[..., None])
    img = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

    e = emis.convert('RGB')
    for radio, k in ((px(5), 0.8), (px(18), 0.6), (px(60), 0.45)):
        img = sumar(img, e.filter(ImageFilter.GaussianBlur(radio)), k)
    img = sumar(img, e, 0.6)
    ll = llamas.convert('RGB')
    for radio, k in ((px(4), 0.6), (px(16), 0.45), (px(48), 0.35)):
        img = sumar(img, ll.filter(ImageFilter.GaussianBlur(radio)), k)
    img = sumar(img, ll, 0.9).convert('RGBA')

    # contraluces: el borde de la derecha, en naranja (el horizonte); el de la izquierda, en carmesi
    f = np.array(img).astype(float)
    for (dx_, dy_), rgb, k in (((1, -1), (255, 150, 80), 0.75), ((-1, 0), (255, 50, 70), 0.6)):
        n_ = max(1, px(3))
        vecino = np.roll(figura, (-dy_ * n_, -dx_ * n_), axis=(0, 1))
        borde = np.clip(figura - vecino, 0, 1)
        borde = flotante(Image.fromarray((borde * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(1, px(1.5)))))
        f[..., :3] += borde[..., None] * np.array(rgb) * k
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))

    # la luz de su sol se derrama por encima del halo y del yelmo
    d_sol = np.hypot(xx - sx_sol, yy - sy_sol)
    glow = np.exp(-(d_sol / (rp * 2.4)) ** 2)[..., None] * np.array([255, 60, 70]) * 0.5
    glow += np.exp(-(d_sol / (rp * 0.9)) ** 2)[..., None] * np.array([255, 200, 190]) * 0.15
    img = sumar(img, Image.fromarray(np.clip(glow, 0, 255).astype(np.uint8)), 1.0).convert('RGBA')

    # --- particulas propias, en 2D ---
    zbuf = np.array(Image.fromarray(np.minimum(lz.z, 1e4).astype(np.float32)).resize((W, H), Image.NEAREST))

    def detras(p, holgura=0.0):
        sx, sy, z = pantalla(p)
        ix, iy = int(min(W - 1, max(0, sx))), int(min(H - 1, max(0, sy)))
        return z > zbuf[iy, ix] + holgura

    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    # las brasas carmesi que suben de donde arde
    fuegos = [punto(h, c) for h, c, _, _ in LENGUAS] + [punto('espada_suelta', (0, y, 0)) for y in HOJA]
    puestas = intentos = 0
    while puestas < 70 and intentos < 4000:
        intentos += 1
        c = fuegos[r.randrange(len(fuegos))]
        p = c + np.array([r.uniform(-2.5, 2.5), r.uniform(1.0, 9.0), r.uniform(-2.5, 2.5)])
        sx, sy, z = pantalla(p)
        if not (0 <= sx < W and 0 <= sy < H) or detras(p, 0.5):
            continue
        q = r.random()
        nombre = (f'novilis_carmesi_{r.randint(0, 3)}.png' if q < 0.45 else f'novilis_chispa_{r.randint(0, 2)}.png' if q < 0.75
                  else f'novilis_brasa_{r.randint(0, 2)}.png')
        s = sprite(nombre, tam_px(r.choice([0.3, 0.4, 0.5]), z))
        capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
        puestas += 1
    # las llamas carmesi que dejan los soles al volar (NOVILIS_CARMESI)
    for p, cola, desde, hasta in volando:
        for j in range(9):
            q = cola[r.randrange(1, len(cola))] + np.array([r.gauss(0, 0.4), r.gauss(0, 0.4), r.gauss(0, 0.4)])
            sx, sy, z = pantalla(q)
            if detras(q):
                continue
            s = sprite(f'novilis_carmesi_{r.randint(0, 3)}.png', tam_px(r.choice([0.35, 0.45, 0.55]), z))
            capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
    # chispas que saltan de los sellos
    for q0 in zonas:
        for _ in range(7):
            a, d = r.uniform(0, TAU), r.uniform(0, RADIO_ZONA)
            q = q0 + np.array([math.cos(a) * d, r.uniform(0.2, 2.5), math.sin(a) * d])
            sx, sy, z = pantalla(q)
            if z < 2 or detras(q):
                continue
            s = sprite(f'novilis_luz_{r.randint(0, 2)}.png' if r.random() < 0.5 else f'novilis_carmesi_{r.randint(0, 3)}.png',
                       tam_px(r.choice([0.25, 0.35]), z))
            capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(px(5))))
    img.alpha_composite(capa)

    # ceniza y brasas sueltas en el aire, con profundidad: lejos pequenas y
    # nitidas, cerca grandes y desenfocadas
    for n_, tams, desenfoque in ((60, (6, 8, 10), 0), (10, (22, 28, 34), 5)):
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        puestas = intentos = 0
        while puestas < n_ and intentos < 4000:
            intentos += 1
            hx_, hy_ = int(r.uniform(px(700), W - px(20))), int(r.uniform(px(110), H - px(30)))
            if figura[min(H - 1, hy_), min(W - 1, hx_)] > 0.1 and not desenfoque:
                continue
            q = r.random()
            nombre = (f'novilis_ceniza_{r.randint(0, 2)}.png' if q < 0.45 else f'novilis_brasa_{r.randint(0, 2)}.png' if q < 0.8
                      else f'novilis_chispa_{r.randint(0, 2)}.png')
            s = sprite(nombre, px(r.choice(tams)))
            capa.alpha_composite(s, (hx_ - s.width // 2, hy_ - s.height // 2))
            puestas += 1
        if desenfoque:
            capa = capa.filter(ImageFilter.GaussianBlur(px(desenfoque)))
            capa.putalpha(capa.getchannel('A').point(lambda v: int(v * 0.8)))
        img.alpha_composite(capa)

    # --- grado y vineta ---
    f = np.array(img).astype(float) / 255.0
    vin = 1 - 0.6 * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.32, 0, 1) ** 1.4
    f[..., :3] *= vin[..., None]
    f[..., :3] = np.clip(f[..., :3] * np.array([1.0, 0.97, 0.95]) + np.random.default_rng(2).normal(0, 0.01, (H, W, 1)), 0, 1)
    img = Image.fromarray((f * 255).astype(np.uint8)).convert('RGBA')

    # --- el anuncio ---
    gr = np.zeros((H, W, 4), np.uint8)
    gr[..., :3] = (12, 3, 4)
    gr[..., 3] = (np.clip(1 - xx / (W * 0.5), 0, 1) ** 1.6 * 215).astype(np.uint8)
    img.alpha_composite(Image.fromarray(gr))
    d_ = ImageDraw.Draw(img)

    x0 = px(110)
    texto_espaciado(d_, (x0, px(300)), 'ATALAYA  ·  JEFE DEL FUEGO', fuente('Montserrat-Bold.ttf', 22), ASCUA, px(5))
    brillo_texto(img, (x0 - px(6), px(320)), 'NOVILIS', fuente('Oswald-Bold.ttf', 196), BLANCO, (255, 70, 50, 210), px(24))
    d_ = ImageDraw.Draw(img)
    d_.text((x0, px(562)), 'El Caballero Solar', font=fuente('Montserrat-SemiBoldItalic.ttf', 34), fill=(240, 220, 208, 255))
    d_.text((x0, px(608)), FRASE, font=fuente('Montserrat-Medium.ttf', 24), fill=GRIS)
    d_.rectangle((x0, px(656), x0 + px(90), px(661)), fill=LLAMA)

    # la barra de jefe, como en el juego, sobre el
    barra = barra_jefe(max(1, px(2)))
    img.alpha_composite(barra, (int(float(os.environ.get('BARRA_X', '960')) * ESCALA) - barra.width // 2, px(36)))
    d_ = ImageDraw.Draw(img)

    fs = fuente('Oswald-Bold.ttf', 26)
    fp = fuente('Montserrat-Medium.ttf', 18)
    tw = d_.textlength('HARDCORE', font=fs)
    bx, by = W - px(110) - tw - px(36), px(60)
    d_.rectangle((bx, by, bx + tw + px(36), by + px(52)), outline=LLAMA, width=max(1, px(3)))
    d_.text((bx + px(18), by + px(6)), 'HARDCORE', font=fs, fill=LLAMA)
    d_.text((W - px(110) - d_.textlength('Minecraft 26.2 · Fabric', font=fp), H - px(70)),
            'Minecraft 26.2 · Fabric', font=fp, fill=(196, 168, 158, 255))
    img.convert('RGB').save(SALIDA)
    print('ok', W, H, 'sol en', int(sx_sol), int(sy_sol), 'horizonte', int(horiz))


FRASE = 'Rompe a sus ángeles. Apaga su sol.'


def texto_espaciado(d, xy, txt, f, color, sep):
    x, y = xy
    for ch in txt:
        d.text((x, y), ch, font=f, fill=color)
        x += d.textlength(ch, font=f) + sep
    return x


def brillo_texto(base, xy, txt, f, color, halo, radio):
    capa = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).text(xy, txt, font=f, fill=halo)
    capa = capa.filter(ImageFilter.GaussianBlur(radio))
    base.alpha_composite(capa)
    base.alpha_composite(capa)
    ImageDraw.Draw(base).text(xy, txt, font=f, fill=color)


main()

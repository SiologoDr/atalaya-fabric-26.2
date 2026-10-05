"""
Poster promocional de Nerea, Guardian de los Mares, en el fondo del mar con
el Remolino en marcha. Presenta al jefe: el gigante grande a la derecha, su
nombre a la izquierda y nada mas (ni jugadores ni lista de ataques).

Nerea, con la camara baja mirandolo desde abajo: el tridente a plomo en la
derecha, los ojos y el corazon maldito encendidos, y la izquierda abierta
hacia un lado, de la que sale el latigazo del Arpon: la cadena sube, da la
vuelta y baja con el gancho volando de perfil hacia quien mira. A su
alrededor, el Remolino: brazos de ola baja que giran por el suelo hacia sus
pies y corrientes que suben en espiral, abriendose como un embudo, por detras
de el (por delante solo le pasan por las piernas). Arriba, su barra de jefe
tal cual sale en el juego.

Todo lo que sale esta hecho para el mod: la malla del juego con su atlas y su
capa de brillo (nerea_juego.py), los eslabones y el gancho con los materiales
del boceto (nerea_modelo.py), el agua del remolino (una textura en pixeles
pintada aqui), el fondo marino, los rayos de luz, las particulas propias y la
barra. Las fuentes son las del sistema.

Uso: python nerea_poster.py <raiz del proyecto> <salida.png> [escala]
"""
import math, os, sys, random, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAIZ, SALIDA = sys.argv[1], sys.argv[2]
ESCALA = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NEREA_SIN_FISICA'] = '1'
_argv = sys.argv
sys.argv = [_argv[0], RAIZ, tempfile.mkdtemp()]
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne
import nerea_juego as nj
import nerea_juego_anim as na
import nerea_fisica as nf
sys.argv = _argv

A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
P = os.path.join(A, 'particle')
GUI = os.path.join(A, 'gui')
FUENTES = 'C:/Windows/Fonts/'
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
SS = 2
FASE = 1

CIAN = (110, 236, 220, 255)
MAGENTA = (255, 70, 140, 255)
BLANCO = (240, 246, 244, 255)
GRIS = (178, 200, 202, 255)


def fuente(nombre, tam):
    return ImageFont.truetype(FUENTES + nombre, int(tam * ESCALA))


def px(n):
    return int(round(n * ESCALA))


# ----------------------------------------------------------------------
#  La pose: acaba de soltar el Arpon. El tridente a plomo en la derecha, la
#  izquierda abierta hacia un lado y alzada (de ella sale la cadena), el
#  torso echado hacia quien mira, la cabeza baja clavando los ojos y la
#  mandibula abierta. Las piernas abiertas y plantadas.
# ----------------------------------------------------------------------
def pose_poster():
    ocultos = {n: {'oculto': True} for n in ('corazon_1', 'corazon_2', 'corazon_3', 'corazon_4', 'corazon_libre',
                                             'molino_izq', 'molino_der') if n != f'corazon_{FASE}'}
    pose = na.mezcla({'pelvis': na.P(0, 3, -1), 'torso': na.r(8, -6, 0), 'cuello': na.r(2, -4, 0),
                      'cabeza': na.r(8, -6, 0), 'mandibula': na.r(30),
                      'ojo_izq': {'esc': (1.35, 1.35, 1.35)}, 'ojo_der': {'esc': (1.35, 1.35, 1.35)},
                      'corazon': {'esc': (1.15, 1.15, 1.15)},
                      # el gancho de la mano va lanzado: lo dibuja la cadena del Arpon
                      'cadena_mano': {'oculto': True}},
                     ocultos, na.brazo('izq', -15, -105, -25), na.brazo('der', -14, 10, -40))
    pose['tridente'] = na.r(*na.tridente_vertical(pose))
    Ms = nj.matrices(pose)
    for lado, obj in (('izq', (8.5, na.SUELO, -8.0)), ('der', (-8.5, na.SUELO, 5.0))):
        (mx, my, mz), rod, pie = nf.ik_pierna(Ms['pelvis'], lado, obj, 0.0, 0.0)
        pose['pierna_' + lado] = {'rot': (mx - nf.REPOSO_PIERNA, my, mz)}
        pose['espinilla_' + lado] = {'rot': (rod - nf.REPOSO_ESPINILLA, 0, 0)}
        pose['pie_' + lado] = {'rot': (pie - nf.REPOSO_PIE, 0, 0)}
    return pose


# ----------------------------------------------------------------------
#  Escena: camara baja, casi a ras de suelo, mirando hacia arriba
# ----------------------------------------------------------------------
NEREA_EN = (2.8, 0.0, 1.5)
GUINADA = float(os.environ.get('GUINADA', '22'))
CAM = vr.Camara(ojo=(-5.2, 0.9, -11.0), objetivo=(float(os.environ.get('OBJ_X', '6.8')), 6.0, 1.0),
                fov=46, ancho=W * SS, alto=H * SS)
LUCES = [
    ((-0.3, 1.0, -0.5), (0.66, 0.95, 1.0), 1.2, 'llave'),      # la luz que baja de la superficie
    ((0.8, 0.3, 0.7), (1.0, 0.25, 0.55), 1.15, 'contra'),      # el corazon maldito tine la espalda
    ((-0.9, 0.25, 0.5), (0.25, 0.95, 1.0), 1.2, 'contra'),     # el remolino lo recorta en cian
]
AMBIENTE = (0.15, 0.25, 0.31)


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


def desproyectar(sx, sy, prof):
    """El punto del mundo que cae en (sx, sy) del poster (medido en 1920x1080) a "prof" bloques de la camara."""
    x = (sx * ESCALA * SS - CAM.W / 2) * prof / CAM.foco
    y = (CAM.H / 2 - sy * ESCALA * SS) * prof / CAM.foco
    return CAM.ojo + CAM.f * prof + CAM.r * x + CAM.u * y


def delante_del_eje(p):
    """Si un punto queda entre la camara y el eje de Nerea (a su misma altura)."""
    eje = np.array([NEREA_EN[0], p[1], NEREA_EN[2]])
    return (np.asarray(p) - eje) @ CAM.f < 0


# ----------------------------------------------------------------------
#  El Arpon: una cadena de eslabones que sigue una curva y el gancho al final
# ----------------------------------------------------------------------
def curva(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


def orientar(d):
    """Angulos (x, y) que llevan +Y local a la direccion d (como nm.cadena_nodo)."""
    d = np.asarray(d, float) / np.linalg.norm(d)
    return math.degrees(math.acos(max(-1.0, min(1.0, d[1])))), math.degrees(math.atan2(d[0], d[2]))


def cadena_curva(pts, grosor, mat='oxido'):
    """Eslabones alternos a lo largo de la curva (en bloques), cada uno con la
    direccion de su tramo: la cadena se dobla con la curva sin romperse."""
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    acum = np.concatenate([[0.0], np.cumsum(seg)])
    paso = 3.2 * grosor / 16
    qs, s, k = [], 0.0, 0
    g = grosor
    while s < acum[-1] - paso * 0.5:
        i = min(int(np.searchsorted(acum, s, side='right')) - 1, len(seg) - 1)
        p = pts[i] + (pts[i + 1] - pts[i]) * (s - acum[i]) / seg[i]
        a, b = orientar(pts[i + 1] - pts[i])
        caja = (-1.5 * g, 0, -0.5 * g, 3 * g, 4 * g, g) if k % 2 == 0 else (-0.5 * g, 0, -1.5 * g, g, 4 * g, 3 * g)
        qs += nm.quads(nm.nodo('eslabon', (0, 0, 0), (a, b, k * 23.0 % 40 - 20), [(caja, mat)]), {},
                       vr.T(*p) @ vr.S(1 / 16))
        s += paso
        k += 1
    return qs


def gancho(p, d, k):
    """El gancho del Arpon (las cajas de GANCHO en nerea_juego.py), con las
    puas por delante en la direccion de vuelo d."""
    a, b = orientar(d)
    cajas = [((c[0], c[1], c[2], c[3], c[4], c[5]), c[6]) for c in nj.GANCHO]
    return nm.quads(nm.nodo('gancho', (0, 0, 0), (a, b, 0), cajas), {}, vr.T(*p) @ vr.S(k / 16))


# El latigazo del Arpon: la cadena sale de la mano, sube, da la vuelta por la
# derecha y baja con el gancho por delante, de perfil, hacia quien mira. Cada
# punto de control es (x, y del poster, profundidad en bloques).
LATIGO = [(1800, 110, 11.0), (1990, 540, 9.6), (1600, 770, 8.8)]
GROSOR_CADENA = 1.8
TAM_GANCHO = 2.5


def arpon(mano):
    """La cadena y el gancho del Arpon. Devuelve los quads y, para los
    efectos, la curva, el gancho y hacia donde vuela."""
    p1, p2, fin = [desproyectar(*q) for q in LATIGO]
    pts = curva(mano, p1, p2, fin, 90)
    vuelo = pts[-1] - pts[-4]
    qs = cadena_curva(pts, GROSOR_CADENA) + gancho(fin, vuelo, TAM_GANCHO)
    return qs, (pts, fin, vuelo / np.linalg.norm(vuelo))


def latigazo(capa, info, r):
    """La estela del latigazo: el agua que arrastra la cadena (rayas que se
    abren hacia el gancho) y el remolino de burbujas y gotas que deja el gancho."""
    pts, fin, d = info
    lapiz = ImageDraw.Draw(capa)
    proy = [pantalla(p) for p in pts]
    n = len(proy)
    for hebra in range(9):
        o = (hebra / 8 - 0.5) * 2
        for i in range(n - 1):
            t = i / (n - 1)
            (ax, ay, az), (bx, by, bz) = proy[i], proy[i + 1]
            tx, ty = bx - ax, by - ay
            lt = math.hypot(tx, ty) + 1e-6
            ancho = px(1000) / az * (0.1 + 0.75 * t ** 1.3)
            ox, oy = -ty / lt * o * ancho, tx / lt * o * ancho
            al = int(150 * t ** 1.4 * (1 - abs(o)) ** 0.7 * (0.6 + 0.4 * math.sin(t * 31 + hebra * 2.1)))
            lapiz.line([(ax + ox, ay + oy), (bx + ox, by + oy)], fill=(205, 245, 255, max(0, al)),
                       width=max(1, int(px(14) / az)))
    gx, gy, gz = pantalla(fin)
    escala = px(1000) / gz
    atras = pantalla(fin - d * 2.5)
    ux, uy = atras[0] - gx, atras[1] - gy
    l = math.hypot(ux, uy) + 1e-6
    ux, uy = ux / l, uy / l
    for k in range(14):
        s = sprite(f'nerea_{"gota_" + str(r.randint(0, 1)) if k % 2 else "burbuja_" + str(r.randint(0, 1))}.png',
                   max(4, int(escala * r.uniform(0.06, 0.13))))
        t = r.uniform(0.2, 2.2)
        o = r.uniform(-0.5, 0.5) * escala * 0.7
        capa.alpha_composite(s, (int(gx + ux * escala * t - uy * o - s.width / 2), int(gy + uy * escala * t + ux * o - s.height / 2)))


# ----------------------------------------------------------------------
#  El Remolino, hecho malla: bandas de agua en pixeles con la cresta de
#  espuma arriba. Por el suelo, seis brazos de ola baja que giran en espiral
#  hacia sus pies (como NereaEfectosCliente.remolinoGigante); alrededor de el,
#  corrientes que suben en espiral y se abren como un embudo.
# ----------------------------------------------------------------------
def _tex_corriente(semilla, w=64, h=14):
    """La fila 0 es la cresta: espuma blanca. Debajo, lineas de flujo a lo
    largo de la banda, cada vez mas raras hacia la base, que casi no se ve."""
    r = random.Random(semilla)
    t = np.zeros((h, w, 4), np.uint8)
    for y in range(h):
        k = 1 - y / (h - 1)
        x = 0
        while x < w:
            largo = r.randint(3, 11)
            if y <= 1:
                col, a = (236, 252, 255), r.randint(205, 250) if r.random() < 0.88 else 0
            elif y == 2:
                col, a = (196, 244, 252), r.randint(130, 190) if r.random() < 0.6 else 0
            elif r.random() < 0.25 + 0.5 * k:
                col, a = (150, 232, 242), int(r.randint(80, 160) * (0.25 + 0.75 * k))
            else:
                col, a = (60, 180, 200), int(r.randint(20, 60) * (0.2 + 0.8 * k))
            for xx in range(x, min(w, x + largo)):
                t[y, xx] = (*col, a)
            x += largo + (0 if y <= 1 else r.randint(0, 4))
    return t


TEX_CORRIENTE = _tex_corriente(3)
TEX_CRESTA = TEX_CORRIENTE.copy()          # solo la espuma brilla
TEX_CRESTA[3:, :, 3] = 0

# Lo que esta a menos de esto de la camara (bloques) no se pinta: saldria enorme.
CERCA = 4.5
# Altura (bloques) hasta la que el agua puede pasar por delante de el: por
# encima se esconde, para no taparle el corazon ni la cara.
FRENTE_MAX = 3.2
# Las corrientes que suben: (angulo de salida, vueltas, altura de salida y de
# llegada, radio abajo y arriba, alto de la banda abajo y arriba).
CORRIENTES = [
    (0.3, 0.62, 0.3, 7.2, 3.3, 5.8, 0.7, 1.6),
    (1.6, 0.58, 1.2, 8.0, 3.6, 6.2, 0.6, 1.4),
    (2.9, 0.66, 0.4, 8.2, 3.1, 6.2, 0.7, 1.7),
    (4.3, 0.55, 2.2, 8.4, 3.8, 6.4, 0.5, 1.2),
    (5.4, 0.6, 0.6, 6.4, 3.4, 5.4, 0.6, 1.4),
]


def banda(filas, largo_tex=2.6):
    """filas: [(base, cresta, opacidad)] a lo largo de la banda -> quads (P, UV, k)."""
    qs, s = [], 0.0
    for (a0, a1, ka), (b0, b1, kb) in zip(filas, filas[1:]):
        ds = float(np.linalg.norm(b0 - a0))
        ua, ub = s / largo_tex, (s + ds) / largo_tex
        qs.append(([a0, b0, b1, a1], [(ua, 0.999), (ub, 0.999), (ub, 0.0), (ua, 0.0)], (ka + kb) / 2))
        s += ds
    return qs


def bandas_remolino():
    cx, cz = NEREA_EN[0], NEREA_EN[2]
    qs = []
    crestas = []
    for brazo in range(6):                       # los brazos del suelo
        base = brazo * math.tau / 6 + 0.4
        filas = []
        rad = 2.4
        while rad < 30:
            a = base + math.log(rad) * 2.4
            p = np.array([cx + math.cos(a) * rad, 0.02, cz + math.sin(a) * rad])
            alto = 0.25 + 0.035 * rad                # la ola crece hacia fuera
            t = (rad - 2.4) / 27.6
            filas.append((p, p + np.array([0, alto, 0]), 0.9 * math.sin(math.pi * min(1.0, t * 1.15)) ** 0.5))
            rad += 0.2 + rad * 0.025
        qs += banda(filas, 2.0)
        crestas += [f[1] for f in filas[2::4]]
    for th0, vueltas, y0, y1, r0, r1, b0, b1 in CORRIENTES:     # las que suben
        filas = []
        for i in range(120):
            t = i / 119
            th = th0 + t * vueltas * math.tau
            rad = r0 + (r1 - r0) * t ** 1.4
            p = np.array([cx + math.cos(th) * rad, y0 + (y1 - y0) * t, cz + math.sin(th) * rad])
            filas.append((p, p + np.array([0, b0 + (b1 - b0) * t, 0]), 0.95 * math.sin(math.pi * t) ** 0.6))
        qs += banda(filas)
        crestas += [f[1] for f in filas[3::7]]
    return qs, crestas


def dibujar_agua(lz, niebla):
    """Pinta el agua en su propio lienzo, con la profundidad de la escena (asi
    queda detras de el cuando pasa por detras), de atras a delante."""
    agua = vr.Lienzo(lz.W, lz.H)
    agua.z = lz.z.copy()
    qs, crestas = bandas_remolino()
    qs = [q for q in qs if min(CAM.proyectar(p)[2] for p in q[0]) > CERCA]
    qs.sort(key=lambda q: -CAM.proyectar(np.mean(q[0], axis=0))[2])
    for Pq, UVq, k in qs:
        # arriba se disuelve en el agua: la franja de la barra queda limpia
        alto_pantalla = min(CAM.proyectar(p)[1] for p in Pq) / SS / ESCALA
        k *= min(1.0, max(0.0, (alto_pantalla - 110) / 90))
        if k < 0.02:
            continue
        for tri in ((0, 1, 2), (0, 2, 3)):
            agua.triangulo(CAM, [Pq[i] for i in tri], [UVq[i] for i in tri], TEX_CORRIENTE, np.ones(3), None, niebla,
                           envolver=True, translucido=k)
            agua.triangulo(CAM, [Pq[i] for i in tri], [UVq[i] for i in tri], TEX_CRESTA, np.ones(3), None, None,
                           aditivo=True, brillo=0.35 * k, envolver=True)
    return agua, crestas


def espuma_crestas(tras, frente, crestas, r):
    """Espuma, crestas de ola y gotas que saltan del agua (las particulas del
    juego), salpicadas por las crestas."""
    for p in crestas:
        if r.random() > 0.45:
            continue
        sx, sy, prof = pantalla(p)
        if prof < CERCA:
            continue
        tira = r.random()
        nombre = (f'nerea_ola_{r.randint(0, 2)}.png' if tira < 0.35 else
                  f'nerea_espuma_{r.randint(0, 2)}.png' if tira < 0.75 else f'nerea_gota_{r.randint(0, 1)}.png')
        s = sprite(nombre, max(3, int(px(300) / prof * r.uniform(0.6, 1.1))))
        delante = delante_del_eje(p) and p[1] < FRENTE_MAX
        (frente if delante else tras).alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height * 0.8)))


def ojo_remolino(tras, frente):
    """El ojo del remolino: el agua que se hunde en espiral a sus pies."""
    cx, cz = NEREA_EN[0], NEREA_EN[2]
    for k in range(10):
        ang = k * math.tau / 10
        p = np.array([cx + math.cos(ang) * 2.2, 0.1, cz + math.sin(ang) * 2.2])
        sx, sy, prof = pantalla(p)
        lado = int(px(1300) / prof)
        s = sprite(f'nerea_remolino_{k % 3}.png', lado, int(lado * 0.5))
        (frente if delante_del_eje(p) else tras).alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))


def barra_jefe(escala, vida=0.86, rastro=0.93):
    """La barra de jefe de Nerea, compuesta igual que en NereaBarraHud: el agua
    de la fase, el rastro blanco del ultimo golpe y los tres eslabones."""
    def tex(n):
        return Image.open(os.path.join(GUI, n + '.png')).convert('RGBA')

    def tenir(im, rgb):
        a = np.array(im).astype(float)
        a[..., :3] *= np.array(rgb)[None, None] / 255.0
        return Image.fromarray(a.astype(np.uint8))
    color = [(0x3F, 0xE0, 0xCC), (0x9A, 0x6B, 0xFF), (0xD4, 0x3C, 0xFF), (0xFF, 0x20, 0x50)][FASE - 1]
    lienzo = Image.new('RGBA', (208, 26 + 7), (0, 0, 0, 0))
    y0 = 7
    lienzo.alpha_composite(tex('nerea_barra_marco'), (0, y0))
    lleno, hasta = round(172 * vida), round(172 * rastro)
    if hasta > lleno:
        ImageDraw.Draw(lienzo).rectangle((28 + lleno, y0 + 9, 28 + hasta - 1, y0 + 9 + 7), fill=(0xF4, 0xFF, 0xFF, 0xD8))
    agua = tenir(tex('nerea_barra_agua'), color)
    for x in range(0, lleno, 64):
        lienzo.alpha_composite(agua.crop((0, 0, min(64, lleno - x), 8)), (28 + x, y0 + 9))
    for corte in (0.75, 0.5, 0.25):
        nombre = 'nerea_barra_eslabon_roto' if vida < corte else 'nerea_barra_eslabon'
        lienzo.alpha_composite(tex(nombre), (28 + round(172 * corte) - 3, y0 + 7))
    lienzo.alpha_composite(tex(f'nerea_barra_corazon_{FASE}'), (13 - 8, y0 + 13 - 8))
    lienzo.alpha_composite(tex('nerea_barra_nombre'), (28, y0 + 7 - 10))
    lienzo.alpha_composite(tenir(tex(f'nerea_barra_fase_{FASE}'), color), (28 + 172 - 64 + 1, y0 + 7 - 10))
    return lienzo.resize((lienzo.width * escala, lienzo.height * escala), Image.NEAREST)


def a_imagen(arr):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    return im.resize((W, H), Image.LANCZOS)


def main():
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(ini=12.0, largo=34.0)

    # suelo de arena y prismarina, y ruinas sumergidas al fondo, en la niebla
    ne.suelo(lz, CAM, ext=26, prof=46, niebla=niebla)
    for x, z, alto in ((-14.0, 15.0, 6), (17.0, 15.0, 9), (-19.0, 4.0, 4), (23.0, 26.0, 7), (4.0, 30.0, 8)):
        ruina = [(Pq, UVq, 'prisma_osc' if m == 'sello' else m) for Pq, UVq, m in ne.pilar(x, z, alto)]
        nm.dibujar(lz, CAM, ruina, ne.LUCES_MAR, ne.AMB_MAR, niebla)

    # Nerea: la malla del juego con su atlas y su capa de brillo
    uv, alto = nj.empaquetar()
    tex = vr.cargar(os.path.join(A, f'entity/nerea/nerea_f{FASE}.png'))
    brillo = vr.cargar(os.path.join(A, f'entity/nerea/nerea_brillo_f{FASE}.png'))
    pose = pose_poster()
    M = vr.entidad_a_mundo(*NEREA_EN, GUINADA, nj.ESCALA)
    cuerpo = nj.quads(pose, uv, alto, M)
    for Pq, UVq, _ in cuerpo:
        luz = vr.iluminar(vr.normal(Pq), CAM, np.mean(Pq, axis=0), LUCES, AMBIENTE)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, luz, brillo, niebla, brillo=1.0)

    # la cadena del Arpon, de la mano al gancho
    mano = (M @ np.array([*nj.punto(pose, 'mano_izq', (0, 5, 0)), 1.0]))[:3]
    hierro, info_arpon = arpon(mano)
    nm.dibujar(lz, CAM, hierro, LUCES, AMBIENTE, niebla)
    # el agua del remolino, despues de todo lo opaco
    agua, crestas = dibujar_agua(lz, niebla)

    pecho = (M @ np.array([*nj.punto(pose, 'corazon'), 1.0]))[:3]
    puntas = (M @ np.array([*nj.punto(pose, 'tridente', (0, 62, 0)), 1.0]))[:3]

    # la silueta de lo que esta delante (el, la cadena y el gancho): lo que
    # pasa por detras se recorta con ella
    solo = vr.Lienzo(W * SS, H * SS)
    for Pq, UVq, _ in cuerpo:
        for tri in ((0, 1, 2), (0, 2, 3)):
            solo.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, np.ones(3))
    nm.dibujar(solo, CAM, hierro, [], (1, 1, 1))
    figura = np.array(a_imagen(solo.alfa)).astype(float) / 255.0

    # --- a resolucion final ---
    color = a_imagen(lz.color)
    alfa = a_imagen(lz.alfa)
    emis = a_imagen(lz.emis)

    lejos = np.array([CAM.ojo[0] + CAM.f[0] * 400, 0.0, CAM.ojo[2] + CAM.f[2] * 400])
    horiz = CAM.proyectar(lejos)[1] / SS
    fondo = ne.fondo_mar(W, H, horiz)
    yy, xx = np.mgrid[0:H, 0:W]
    # el corazon maldito tine el agua detras de el; el remolino la enciende en cian
    for punto, rgb, k, ax_, ay_ in ((pecho, (0.55, 0.06, 0.32), 0.45, 0.22, 0.3), (pecho, (0.08, 0.5, 0.55), 0.42, 0.42, 0.55),
                                    (puntas, (0.2, 0.7, 0.75), 0.35, 0.12, 0.18)):
        cx, cy, _ = pantalla(punto)
        dd = np.hypot((xx - cx) / (W * ax_), (yy - cy) / (H * ay_))
        fondo = fondo + np.array(rgb)[None, None] * np.exp(-dd ** 2 * 1.4)[..., None] * k
    fondo += ne.rayos(W, H, 5, n=9)[..., None] * np.array([0.45, 0.85, 0.9]) * 0.8
    # el contraluz: el agua brilla justo detras de su silueta
    halo = np.array(Image.fromarray((figura * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(px(40)))).astype(float) / 255
    fondo += halo[..., None] * np.array([0.1, 0.4, 0.42]) * 0.75
    fondo_img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

    escena = color.convert('RGBA')
    escena.putalpha(alfa)
    fondo_img.alpha_composite(escena)

    # el agua del remolino: ya viene recortada por detras de el; por delante
    # solo se deja pasar por sus piernas, no por el pecho ni la cara
    _, cintura, _ = pantalla((NEREA_EN[0], FRENTE_MAX, NEREA_EN[2]))
    arriba = np.clip((cintura + px(40) - yy) / px(80), 0, 1)
    deja = 1 - figura * arriba
    a_agua = np.array(a_imagen(agua.alfa)).astype(float)[..., None] / 255 * deja[..., None]
    c_agua = np.array(a_imagen(agua.color)).astype(float) * deja[..., None]
    f = np.array(fondo_img).astype(float)
    f[..., :3] = f[..., :3] * (1 - a_agua) + c_agua
    fondo_img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
    # la espuma de las crestas brilla (con el mismo recorte)
    e_agua = np.array(a_imagen(agua.emis)).astype(float) * deja[..., None]
    emis = Image.fromarray(np.clip(np.array(emis).astype(float) + e_agua, 0, 255).astype(np.uint8))

    # espuma del remolino y estela del latigazo: lo de detras, recortado con su silueta
    tras = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    frente = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    r = random.Random(9)
    ojo_remolino(tras, frente)
    espuma_crestas(tras, frente, crestas, r)
    latigazo(tras, info_arpon, r)
    hueco = 1 - figura
    tras.putalpha(Image.fromarray((np.array(tras.getchannel('A')).astype(float) * hueco).astype(np.uint8)))
    fondo_img.alpha_composite(tras)

    # rayos de luz tambien POR DELANTE: agua entre la camara y el
    rayos_frente = ne.rayos(W, H, 41, n=5)[..., None] * np.array([0.5, 0.9, 1.0]) * 0.18
    fondo_img = sumar(fondo_img, Image.fromarray((np.clip(rayos_frente, 0, 1) * 255).astype(np.uint8)), 1.0)

    e = emis.convert('RGB')
    for radio, k in ((px(5), 0.8), (px(18), 0.6), (px(60), 0.45)):
        fondo_img = sumar(fondo_img, e.filter(ImageFilter.GaussianBlur(radio)), k)
    img = sumar(fondo_img, e, 1.0).convert('RGBA')

    # contraluces: el borde de la silueta que mira a la superficie, en blanco
    # azulado, y el que mira al remolino, en cian
    f = np.array(img).astype(float)
    for (dx, dy), rgb, k in (((-1, -1), (200, 250, 255), 0.75), ((1, 0), (60, 230, 230), 0.55)):
        n_ = max(1, px(3))
        vecino = np.roll(figura, (-dy * n_, -dx * n_), axis=(0, 1))
        borde = np.clip(figura - vecino, 0, 1)
        borde = np.array(Image.fromarray((borde * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(1, px(1.5))))).astype(float) / 255
        f[..., :3] += borde[..., None] * np.array(rgb) * k
    img = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))

    # --- particulas propias, en 2D ---
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for nombre_pt in ('ojo_izq', 'ojo_der'):
        ojo = (M @ np.array([*nj.punto(pose, nombre_pt), 1.0]))[:3]
        ox, oy, _ = pantalla(ojo)
        for _ in range(3):                       # destellos en los ojos, hacia fuera y arriba
            a = r.uniform(-math.pi * 0.95, -math.pi * 0.05)
            d = r.uniform(px(45), px(110))
            s = sprite(f'nerea_ojo_{r.randint(0, 2)}.png', px(r.choice([10, 14, 18])))
            capa.alpha_composite(s, (int(ox + math.cos(a) * d - s.width / 2), int(oy + math.sin(a) * d - s.height / 2)))
    cx, cy, _ = pantalla(pecho)
    for _ in range(6):                           # el latido del corazon
        s = sprite(f'nerea_corazon_{r.randint(0, 2)}.png', px(r.choice([18, 24, 30])))
        capa.alpha_composite(s, (int(cx + r.uniform(-px(120), px(120))), int(cy + r.uniform(-px(110), px(80)))))
    tx, ty, _ = pantalla(puntas)
    for _ in range(4):                           # destellos en las puntas del tridente
        s = sprite(f'nerea_ojo_{r.randint(1, 2)}.png', px(r.choice([10, 14])))
        a = r.uniform(-math.pi, 0)
        d = r.uniform(px(50), px(100))
        capa.alpha_composite(s, (int(tx + math.cos(a) * d - s.width / 2), int(ty + math.sin(a) * d - s.height / 2)))
    puestas = 0
    while puestas < 46:                          # burbujas que suben, sin taparle la cara ni el pecho
        bx_, by_ = int(r.uniform(px(860), W - px(40))), int(r.uniform(px(130), H - px(60)))
        if figura[min(H - 1, by_), min(W - 1, bx_)] > 0.1 and by_ < cintura:
            continue
        s = sprite(f'nerea_burbuja_{r.randint(0, 1)}.png', px(r.choice([12, 16, 20, 28])))
        capa.alpha_composite(s, (bx_ - s.width // 2, by_ - s.height // 2))
        puestas += 1
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(px(6))))
    img.alpha_composite(capa)
    con = img.copy()
    ne.burbujas(con, int(50 * ESCALA), 17, zona=((px(860), W - px(30)), (px(120), H - px(40))))
    img = Image.composite(img, con, Image.fromarray((figura * arriba * 255).astype(np.uint8)))
    # lo del remolino que pasa por delante de el, encima de todo
    img.alpha_composite(frente)

    # --- grado y vineta ---
    f = np.array(img).astype(float) / 255.0
    vin = 1 - 0.6 * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.32, 0, 1) ** 1.4
    f[..., :3] *= vin[..., None]
    f[..., :3] = np.clip(f[..., :3] * np.array([0.94, 1.0, 1.04]) + np.random.default_rng(2).normal(0, 0.01, (H, W, 1)), 0, 1)
    img = Image.fromarray((f * 255).astype(np.uint8)).convert('RGBA')

    # --- el anuncio ---
    gr = np.zeros((H, W, 4), np.uint8)
    gr[..., :3] = (2, 10, 16)
    gr[..., 3] = (np.clip(1 - xx / (W * 0.5), 0, 1) ** 1.6 * 215).astype(np.uint8)
    img.alpha_composite(Image.fromarray(gr))
    d = ImageDraw.Draw(img)

    x0 = px(110)
    texto_espaciado(d, (x0, px(300)), 'ATALAYA  ·  JEFE DEL MAR', fuente('Montserrat-Bold.ttf', 22), CIAN, px(5))
    brillo_texto(img, (x0 - px(6), px(320)), 'NEREA', fuente('Oswald-Bold.ttf', 196), BLANCO, (40, 220, 210, 210), px(24))
    d = ImageDraw.Draw(img)
    d.text((x0, px(562)), 'Guardián de los Mares', font=fuente('Montserrat-SemiBoldItalic.ttf', 34), fill=(205, 228, 230, 255))
    d.text((x0, px(608)), 'Rompe sus cadenas. Libera su corazón.', font=fuente('Montserrat-Medium.ttf', 24), fill=GRIS)
    d.rectangle((x0, px(656), x0 + px(90), px(661)), fill=MAGENTA)

    # la barra de jefe, como en el juego, sobre el
    barra = barra_jefe(max(1, px(2)))
    img.alpha_composite(barra, (int(float(os.environ.get('BARRA_X', '1270')) * ESCALA) - barra.width // 2, px(36)))
    d = ImageDraw.Draw(img)

    fs = fuente('Oswald-Bold.ttf', 26)
    fp = fuente('Montserrat-Medium.ttf', 18)
    tw = d.textlength('HARDCORE', font=fs)
    bx, by = W - px(110) - tw - px(36), px(60)
    d.rectangle((bx, by, bx + tw + px(36), by + px(52)), outline=MAGENTA, width=max(1, px(3)))
    d.text((bx + px(18), by + px(6)), 'HARDCORE', font=fs, fill=MAGENTA)
    d.text((W - px(110) - d.textlength('Minecraft 26.2 · Fabric', font=fp), H - px(70)),
           'Minecraft 26.2 · Fabric', font=fp, fill=(160, 186, 190, 255))
    img.convert('RGB').save(SALIDA)
    print('ok', W, H)


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

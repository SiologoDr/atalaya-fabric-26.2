"""
Poster promocional de Nerea: el mismo formato que el del Vigia (bicho en el
tercio derecho, anuncio a la izquierda, franja de datos abajo), bajo el mar.

Nerea invoca su Remolino: el tridente clavado, la otra mano en alto
removiendo el agua y los brazos de espuma girando hacia ella por el fondo.
Arriba, su barra de jefe tal cual sale en el juego (letras en pixel).

Todo lo que sale esta hecho para el mod: la malla del juego con su atlas y su
capa de brillo (nerea_juego.py), la pose de la animacion del Remolino con los
pies plantados por cinematica inversa, el fondo marino, los rayos de luz, las
particulas propias, los iconos y la barra. Las fuentes son las del sistema.

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

CIAN = (110, 236, 220, 255)
MAGENTA = (255, 70, 140, 255)
BLANCO = (240, 246, 244, 255)
GRIS = (178, 200, 202, 255)


def fuente(nombre, tam):
    return ImageFont.truetype(FUENTES + nombre, int(tam * ESCALA))


def px(n):
    return int(round(n * ESCALA))


# ----------------------------------------------------------------------
#  La pose: el Remolino en su punto alto. Tridente clavado, la mano
#  izquierda arriba removiendo el agua, la mandibula abierta y la cabeza
#  alzada; las piernas abiertas y plantadas.
# ----------------------------------------------------------------------
def pose_poster():
    pose = na.pose_autor('REMOLINO', 0.75)
    pose = na.mezcla(pose, {'mandibula': na.r(30), 'cabeza': na.r(-2, -22, 0), 'cuello': na.r(4, -8, 0),
                            'ojo_izq': {'esc': (1.35, 1.35, 1.35)}, 'ojo_der': {'esc': (1.35, 1.35, 1.35)},
                            'corazon': {'esc': (1.15, 1.15, 1.15)},
                            'corazon_2': {'oculto': True}, 'corazon_3': {'oculto': True},
                            'corazon_4': {'oculto': True}, 'corazon_libre': {'oculto': True},
                            'molino_izq': {'oculto': True}, 'molino_der': {'oculto': True}})
    Ms = nj.matrices(pose)
    for lado, obj in (('izq', (8.0, 20.9, -9.0)), ('der', (-8.0, 20.9, 4.0))):
        (mx, my, mz), rod, pie = nf.ik_pierna(Ms['pelvis'], lado, obj, 0.0, 0.0)
        pose['pierna_' + lado] = {'rot': (mx - nf.REPOSO_PIERNA, my, mz)}
        pose['espinilla_' + lado] = {'rot': (rod - nf.REPOSO_ESPINILLA, 0, 0)}
        pose['pie_' + lado] = {'rot': (pie - nf.REPOSO_PIE, 0, 0)}
    # la cadena de la mano, colgando por su peso
    Ms = nj.matrices(pose)
    p = nj.PARTES['cadena_mano']
    Rp = Ms[p.padre][:3, :3]
    Rp = Rp / np.linalg.norm(Rp, axis=0)
    d = Rp.T @ np.array([0.1, 1.0, 0.2])
    x, z = nf._dir_xz(d)
    pose['cadena_mano'] = {'rot': (x - p.rot[0], 0, z - p.rot[2])}
    return pose


# ----------------------------------------------------------------------
#  Escena: camara baja, que la haga enorme
# ----------------------------------------------------------------------
NEREA_EN = (2.8, 0.0, 1.5)
GUINADA = float(os.environ.get('GUINADA', '20'))
CAM = vr.Camara(ojo=(-8.0, 2.1, -14.5), objetivo=(9.0, 4.9, 0.5), fov=45, ancho=W * SS, alto=H * SS)
LUCES = [
    ((-0.3, 1.0, -0.5), (0.66, 0.95, 1.0), 1.25, 'llave'),     # la luz que baja de la superficie
    ((0.8, 0.3, 0.7), (1.0, 0.25, 0.55), 1.1, 'contra'),       # el corazon maldito tine la espalda
    ((-0.9, 0.2, 0.5), (0.25, 0.95, 1.0), 1.0, 'contra'),      # el remolino la recorta en cian
]
AMBIENTE = (0.16, 0.26, 0.32)


def sumar(base, capa, k=1.0):
    f = np.array(base).astype(float)
    f[..., :3] = np.clip(f[..., :3] + np.array(capa).astype(float)[..., :3] * k, 0, 255)
    return Image.fromarray(f.astype(np.uint8))


def sprite(nombre, ancho, alto=None):
    return Image.open(os.path.join(P, nombre)).convert('RGBA').resize((max(1, ancho), max(1, alto or ancho)), Image.NEAREST)


def remolino(img, niebla):
    """El gran remolino por el fondo: seis brazos de espuma en espiral que
    giran hacia ella, con crestas de ola, aplastados por la perspectiva."""
    r = random.Random(4)
    puntos = []
    cx, cz = NEREA_EN[0], NEREA_EN[2]
    for brazo in range(6):
        base = brazo * math.tau / 6 + 0.4
        rad = 2.4
        while rad < 34:
            a = base + math.log(rad) * 2.4
            for _ in range(3):
                x = cx + math.cos(a) * rad + r.uniform(-0.6, 0.6)
                z = cz + math.sin(a) * rad + r.uniform(-0.6, 0.6)
                sx, sy, prof = CAM.proyectar(np.array([x, 0.06, z]))
                if prof > 0.5:
                    puntos.append((prof, sx / SS, sy / SS, rad))
            rad += 0.45 + rad * 0.05
    puntos.sort(reverse=True)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for prof, sx, sy, rad in puntos:
        lado = int(px(1150) / prof * r.uniform(0.7, 1.2))
        if lado < 3:
            continue
        cresta = r.random() < 0.3
        nombre = f'nerea_ola_{r.randint(0, 2)}.png' if cresta else f'nerea_espuma_{r.randint(1, 3)}.png'
        s = sprite(nombre, lado, max(2, int(lado * 0.42)))
        a = (1 - float(niebla(prof))) * (0.95 if rad < 20 else 0.95 * (34 - rad) / 14)
        s.putalpha(s.getchannel('A').point(lambda v, k=a: int(v * k)))
        capa.alpha_composite(s, (int(sx - s.width / 2), int(sy - s.height / 2)))
    # el ojo del remolino: el agua que se hunde en espiral a sus pies
    for k in range(10):
        ang = k * math.tau / 10
        x = cx + math.cos(ang) * 2.0
        z = cz + math.sin(ang) * 2.0
        sx, sy, prof = CAM.proyectar(np.array([x, 0.1, z]))
        lado = int(px(1400) / prof)
        s = sprite(f'nerea_remolino_{k % 3}.png', lado, int(lado * 0.5))
        capa.alpha_composite(s, (int(sx / SS - s.width / 2), int(sy / SS - s.height / 2)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(px(5))))
    img.alpha_composite(capa)


def barra_jefe(escala):
    """La barra de jefe de Nerea, compuesta igual que en NereaBarraHud: fase I, llena."""
    def tex(n):
        return Image.open(os.path.join(GUI, n + '.png')).convert('RGBA')

    def tenir(im, rgb):
        a = np.array(im).astype(float)
        a[..., :3] *= np.array(rgb)[None, None] / 255.0
        return Image.fromarray(a.astype(np.uint8))
    color = (0x3F, 0xE0, 0xCC)
    lienzo = Image.new('RGBA', (208, 26 + 7), (0, 0, 0, 0))
    y0 = 7
    lienzo.alpha_composite(tex('nerea_barra_marco'), (0, y0))
    agua = tenir(tex('nerea_barra_agua'), color)
    for x in range(0, 172, 64):
        trozo = agua.crop((0, 0, min(64, 172 - x), 8))
        lienzo.alpha_composite(trozo, (28 + x, y0 + 9))
    for corte in (0.75, 0.5, 0.25):
        lienzo.alpha_composite(tex('nerea_barra_eslabon'), (28 + round(172 * corte) - 3, y0 + 7))
    lienzo.alpha_composite(tex('nerea_barra_corazon_1'), (13 - 8, y0 + 13 - 8))
    lienzo.alpha_composite(tex('nerea_barra_nombre'), (28, y0 + 7 - 10 + 3 - 3))
    lienzo.alpha_composite(tenir(tex('nerea_barra_fase_1'), color), (28 + 172 - 64 + 1, y0 + 7 - 10))
    return lienzo.resize((lienzo.width * escala, lienzo.height * escala), Image.NEAREST)


def main():
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(ini=12.0, largo=36.0)

    # suelo de arena y prismarina, y ruinas sumergidas al fondo
    ne.suelo(lz, CAM, ext=20, prof=44, niebla=niebla)
    for x, z, alto in ((-12.5, 14.0, 6), (15.5, 13.0, 9), (-17.0, 5.0, 4), (21.0, 24.0, 7)):
        ruina = [(Pq, UVq, 'prisma_osc' if m == 'sello' else m) for Pq, UVq, m in ne.pilar(x, z, alto)]
        nm.dibujar(lz, CAM, ruina, ne.LUCES_MAR, ne.AMB_MAR, niebla)

    uv, alto = nj.empaquetar()
    tex = vr.cargar(os.path.join(A, 'entity/nerea/nerea_f1.png'))
    brillo = vr.cargar(os.path.join(A, 'entity/nerea/nerea_brillo_f1.png'))
    pose = pose_poster()
    M = vr.entidad_a_mundo(*NEREA_EN, GUINADA, nj.ESCALA)
    for Pq, UVq, _ in nj.quads(pose, uv, alto, M):
        n = vr.normal(Pq)
        luz = vr.iluminar(n, CAM, np.mean(Pq, axis=0), LUCES, AMBIENTE)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, luz, brillo, niebla, brillo=1.25)

    pecho = (M @ np.array([*nj.punto(pose, 'torso', (0, -17, -9)), 1.0]))[:3]
    mano = (M @ np.array([*nj.punto(pose, 'mano_izq', (0, 4, 0)), 1.0]))[:3]

    # --- a resolucion final ---
    color = Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    emis = Image.fromarray((np.clip(lz.emis, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)

    lejos = np.array([CAM.ojo[0] + CAM.f[0] * 400, 0.0, CAM.ojo[2] + CAM.f[2] * 400])
    horiz = CAM.proyectar(lejos)[1] / SS
    fondo = ne.fondo_mar(W, H, horiz)
    yy, xx = np.mgrid[0:H, 0:W]
    # el corazon maldito ilumina el agua detras de ella, y la mano alzada el remolino
    for punto, rgb, k in ((pecho, (0.55, 0.06, 0.32), 0.5), (mano, (0.1, 0.6, 0.62), 0.45)):
        cx, cy, _ = CAM.proyectar(punto)
        dd = np.hypot((xx - cx / SS) / (W * 0.26), (yy - cy / SS) / (H * 0.36))
        fondo = fondo + np.array(rgb)[None, None] * np.exp(-dd ** 2 * 1.4)[..., None] * k
    fondo += ne.rayos(W, H, 5, n=9)[..., None] * np.array([0.45, 0.85, 0.9]) * 0.75
    fondo_img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')

    # el remolino por el fondo, DETRAS de ella (el suelo ya esta en el render)
    suelo_y_bicho = color.convert('RGBA')
    suelo_y_bicho.putalpha(alfa)
    fondo_img.alpha_composite(suelo_y_bicho)
    capa_rem = Image.new('RGBA', fondo_img.size, (0, 0, 0, 0))
    remolino(capa_rem, niebla)
    # lo que queda delante de su cuerpo no tapa a Nerea: se recorta con su silueta
    bicho = Image.new('L', (W * SS, H * SS), 0)
    solo = vr.Lienzo(W * SS, H * SS)
    for Pq, UVq, _ in nj.quads(pose, uv, alto, M):
        for tri in ((0, 1, 2), (0, 2, 3)):
            solo.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, np.ones(3), None, None)
    bicho = Image.fromarray((solo.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    hueco = Image.fromarray(255 - np.array(bicho))
    capa_rem.putalpha(Image.fromarray((np.array(capa_rem.getchannel('A')).astype(float) * np.array(hueco) / 255).astype(np.uint8)))
    fondo_img.alpha_composite(capa_rem)

    # rayos de luz tambien POR DELANTE: agua entre camara y bicho
    rayos_frente = ne.rayos(W, H, 41, n=5)[..., None] * np.array([0.5, 0.9, 1.0]) * 0.2
    fondo_img = sumar(fondo_img, Image.fromarray((np.clip(rayos_frente, 0, 1) * 255).astype(np.uint8)), 1.0)

    e = emis.convert('RGB')
    for radio, k in ((px(5), 0.9), (px(18), 0.7), (px(60), 0.5)):
        fondo_img = sumar(fondo_img, e.filter(ImageFilter.GaussianBlur(radio)), k)
    img = sumar(fondo_img, e, 1.0).convert('RGBA')

    # --- particulas propias, en 2D ---
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    r = random.Random(9)
    for nombre_pt in ('ojo_izq', 'ojo_der'):
        ojo = (M @ np.array([*nj.punto(pose, nombre_pt), 1.0]))[:3]
        ox, oy, _ = CAM.proyectar(ojo)
        for _ in range(3):                       # destellos en los ojos
            a = r.uniform(0, math.tau)
            d = r.uniform(px(20), px(90))
            s = sprite(f'nerea_ojo_{r.randint(0, 2)}.png', px(r.choice([10, 14, 18])))
            capa.alpha_composite(s, (int(ox / SS + math.cos(a) * d), int(oy / SS + math.sin(a) * d)))
    cx, cy, _ = CAM.proyectar(pecho)
    for _ in range(8):                           # el latido del corazon
        s = sprite(f'nerea_corazon_{r.randint(0, 2)}.png', px(r.choice([22, 30, 38])))
        capa.alpha_composite(s, (int(cx / SS + r.uniform(-px(110), px(110))), int(cy / SS + r.uniform(-px(120), px(70)))))
    mx_, my_, _ = CAM.proyectar(mano)
    for k in range(26):                          # el agua que gira alrededor de la mano alzada
        a = k * 0.55
        d = px(30) + k * px(5)
        s = sprite(f'nerea_{"burbuja_" + str(r.randint(0, 1)) if k % 3 else "gota_" + str(r.randint(0, 1))}.png',
                   px(r.choice([14, 18, 24])))
        capa.alpha_composite(s, (int(mx_ / SS + math.cos(a) * d), int(my_ / SS + math.sin(a) * d * 0.6 - k * px(4))))
    for _ in range(46):                          # burbujas que suben
        s = sprite(f'nerea_burbuja_{r.randint(0, 1)}.png', px(r.choice([14, 18, 24, 32])))
        capa.alpha_composite(s, (int(r.uniform(px(940), W - px(60))), int(r.uniform(px(150), H - px(230)))))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(px(6))))
    img.alpha_composite(capa)
    ne.burbujas(img, int(46 * ESCALA), 17, zona=((px(940), W - px(40)), (px(150), H - px(200))))

    # --- grado y vineta ---
    f = np.array(img).astype(float) / 255.0
    vin = 1 - 0.6 * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.32, 0, 1) ** 1.4
    f[..., :3] *= vin[..., None]
    f[..., :3] = np.clip(f[..., :3] * np.array([0.94, 1.0, 1.04]) + np.random.default_rng(2).normal(0, 0.01, (H, W, 1)), 0, 1)
    img = Image.fromarray((f * 255).astype(np.uint8)).convert('RGBA')

    # --- el anuncio ---
    gr = np.zeros((H, W, 4), np.uint8)
    gr[..., :3] = (2, 10, 16)
    gr[..., 3] = (np.clip(1 - xx / (W * 0.55), 0, 1) ** 1.5 * 220).astype(np.uint8)
    img.alpha_composite(Image.fromarray(gr))
    d = ImageDraw.Draw(img)

    x0 = px(110)
    texto_espaciado(d, (x0, px(96)), 'ATALAYA  ·  JEFE DEL MAR', fuente('Montserrat-Bold.ttf', 22), CIAN, px(5))
    brillo_texto(img, (x0 - px(6), px(116)), 'NEREA', fuente('Oswald-Bold.ttf', 210), BLANCO, (40, 220, 210, 210), px(24))
    d = ImageDraw.Draw(img)
    d.text((x0, px(382)), 'Rompe sus cadenas. Libera su corazón.', font=fuente('Montserrat-SemiBoldItalic.ttf', 34), fill=GRIS)
    d.rectangle((x0, px(440), x0 + px(90), px(445)), fill=MAGENTA)

    def icono(ruta, lado):
        im = Image.open(ruta).convert('RGBA')
        bb = im.getbbox()
        if bb:
            im = im.crop(bb)
        k = max(1, int(lado / max(im.size)))
        return im.resize((im.width * k, im.height * k), Image.NEAREST)

    filas = [
        (icono(os.path.join(P, 'nerea_remolino_1.png'), px(62)), 'EL REMOLINO',
         'Te arrastra desde 64 bloques y te ahoga. Solo la luz te suelta.'),
        (icono(os.path.join(GUI, 'nerea_barra_eslabon.png'), px(60)), 'EL ARPÓN',
         'Te engancha de lejos, te arrastra a sus pies y te ensarta.'),
        (icono(os.path.join(P, 'nerea_ojo_0.png'), px(56)), 'LA MIRADA DEL ABISMO',
         'Rómpele los ojos a flechazos o cae.'),
        (icono(os.path.join(GUI, 'nerea_barra_corazon_3.png'), px(56)), 'EL CORAZÓN MALDITO',
         'Se raja en cada fase, y cada fase pega más.'),
    ]
    y = px(478)
    for ic, titulo, linea in filas:
        img.alpha_composite(Image.new('RGBA', (px(76), px(76)), (180, 255, 245, 22)), (x0, y))
        img.alpha_composite(ic, (x0 + (px(76) - ic.width) // 2, y + (px(76) - ic.height) // 2))
        d.text((x0 + px(98), y + px(2)), titulo, font=fuente('Oswald-Bold.ttf', 32), fill=BLANCO)
        d.text((x0 + px(98), y + px(44)), linea, font=fuente('Montserrat-Medium.ttf', 21), fill=GRIS)
        y += px(98)

    # la barra de jefe, como en el juego, sobre ella
    barra = barra_jefe(max(1, px(2)))
    img.alpha_composite(barra, (px(1150) - barra.width // 2, px(40)))

    # franja inferior
    banda_y = px(902)
    img.alpha_composite(Image.new('RGBA', (W, H - banda_y), (3, 14, 20, 215)), (0, banda_y))
    d = ImageDraw.Draw(img)
    d.rectangle((0, banda_y, W, banda_y + px(3)), fill=CIAN)
    cy2 = banda_y + px(80)
    fx = fuente('Montserrat-Bold.ttf', 24)
    fp = fuente('Montserrat-Medium.ttf', 18)

    def bloque(x, ic, titulo, sub):
        img.alpha_composite(ic, (x, cy2 - ic.height // 2))
        dd = ImageDraw.Draw(img)
        dd.text((x + ic.width + px(18), cy2 - px(30)), titulo, font=fx, fill=BLANCO)
        dd.text((x + ic.width + px(18), cy2 + px(4)), sub, font=fp, fill=GRIS)

    bloque(px(110), icono(os.path.join(GUI, 'nerea_barra_corazon_1.png'), px(48)), '11.250 DE VIDA', 'para 30-40 jugadores')
    bloque(px(500), icono(os.path.join(P, 'nerea_corazon_0.png'), px(48)), '4 FASES', '+7 de daño en cada una')
    bloque(px(880), icono(os.path.join(A, 'mob_effect/corriente_abismal.png'), px(54)), 'CORRIENTE ABISMAL', 'te frena y te arrastra')
    bloque(px(1290), icono(os.path.join(A, 'item/lagrima_nerea.png'), px(56)), 'LÁGRIMA DE NEREA', 'su botín')
    bloque(px(1620), icono(os.path.join(A, 'item/huevo_nerea.png'), px(56)), 'HUEVO', 'generador')

    fs = fuente('Oswald-Bold.ttf', 26)
    tw = d.textlength('HARDCORE', font=fs)
    bx, by = W - px(110) - tw - px(36), px(60)
    d.rectangle((bx, by, bx + tw + px(36), by + px(52)), outline=MAGENTA, width=max(1, px(3)))
    d.text((bx + px(18), by + px(6)), 'HARDCORE', font=fs, fill=MAGENTA)
    d.text((W - px(110) - d.textlength('Minecraft 26.2 · Fabric', font=fp), banda_y - px(36)),
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

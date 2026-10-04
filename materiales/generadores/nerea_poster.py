"""
Poster promocional de Nerea, Guardian de los Mares: el mismo formato que el del
Vigia (bicho en el tercio derecho, anuncio a la izquierda, franja de datos
abajo), pero bajo el mar.

Todo lo que sale esta hecho para el mod: la malla del juego con su atlas y su
capa de brillo (nerea_juego.py), la pose del Rompeolas en lo alto (las mismas
poses que las animaciones, con los pies plantados por cinematica inversa), las
cadenas tendidas a los pilares-ancla, el fondo marino, los rayos de luz y las
particulas propias. Las fuentes son las del sistema.

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
FUENTES = 'C:/Windows/Fonts/'
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
SS = 2
rnd = random.Random(23)


def fuente(nombre, tam):
    return ImageFont.truetype(FUENTES + nombre, int(tam * ESCALA))


def px(n):
    return int(round(n * ESCALA))


# ----------------------------------------------------------------------
#  La pose: el Rompeolas en lo alto. El tridente arriba, la mandibula abierta,
#  un paso al frente y la cadena de la mano colgando por su peso.
# ----------------------------------------------------------------------
def pose_poster():
    pose = na.pose_autor('ROMPEOLAS', 0.38)
    pose = na.mezcla(pose, {'mandibula': na.r(30), 'cabeza': na.r(-16, -18, 4), 'cuello': na.r(-8),
                            'ojo_izq': {'esc': (1.35, 1.35, 1.35)}, 'ojo_der': {'esc': (1.35, 1.35, 1.35)},
                            'corazon': {'esc': (1.15, 1.15, 1.15)},
                            'corazon_1': {'oculto': True}, 'corazon_2': {'oculto': True},
                            'corazon_4': {'oculto': True}, 'corazon_libre': {'oculto': True},
                            'cadena_1': {'oculto': True},
                            'molino_izq': {'oculto': True}, 'molino_der': {'oculto': True}})
    # piernas por cinematica inversa: el pie izquierdo adelantado
    Ms = nj.matrices(pose)
    for lado, obj in (('izq', (7.5, 20.9, -13.0)), ('der', (-6.5, 20.9, 3.0))):
        (mx, my, mz), rod, pie = nf.ik_pierna(Ms['pelvis'], lado, obj, 0.0, 0.0)
        pose['pierna_' + lado] = {'rot': (mx - nf.REPOSO_PIERNA, my, mz)}
        pose['espinilla_' + lado] = {'rot': (rod - nf.REPOSO_ESPINILLA, 0, 0)}
        pose['pie_' + lado] = {'rot': (pie - nf.REPOSO_PIE, 0, 0)}
    # la cadena de la mano, a plomo
    Ms = nj.matrices(pose)
    p = nj.PARTES['cadena_mano']
    Rp = Ms[p.padre][:3, :3]
    Rp = Rp / np.linalg.norm(Rp, axis=0)
    d = Rp.T @ np.array([0.15, 1.0, 0.25])
    x, z = nf._dir_xz(d)
    pose['cadena_mano'] = {'rot': (x - p.rot[0], 0, z - p.rot[2])}
    return pose


# ----------------------------------------------------------------------
#  Escena
# ----------------------------------------------------------------------
NEREA_EN = (2.6, 0.0, 1.0)
GUINADA = float(os.environ.get('GUINADA', '24'))
CAM = vr.Camara(ojo=(-6.6, 1.2, -18.6), objetivo=(2.1, 5.5, 0.0), fov=44, ancho=W * SS, alto=H * SS)
LUCES = [
    ((-0.3, 1.0, -0.5), (0.62, 0.92, 1.0), 1.05, 'llave'),     # la luz que baja de la superficie
    ((0.8, 0.25, 0.7), (1.0, 0.22, 0.55), 1.3, 'contra'),      # el corazon maldito tine la espalda
    ((-0.9, 0.15, 0.4), (0.2, 0.8, 0.95), 0.6, 'contra'),
]
AMBIENTE = (0.13, 0.22, 0.28)


def sumar(base, capa, k=1.0):
    f = np.array(base).astype(float)
    f[..., :3] = np.clip(f[..., :3] + np.array(capa).astype(float)[..., :3] * k, 0, 255)
    return Image.fromarray(f.astype(np.uint8))


def main():
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(ini=10.0, largo=34.0)

    # suelo de arena y prismarina
    ne.suelo(lz, CAM, ext=18, prof=40, niebla=niebla)
    # ruinas sumergidas al fondo: columnas rotas cubiertas de coral
    for x, z, alto in ((-10.5, 12.0, 6), (13.5, 10.0, 8), (-14.0, 2.0, 4)):
        ruina = [(Pq, UVq, 'prisma_osc' if m == 'sello' else m) for Pq, UVq, m in ne.pilar(x, z, alto)]
        nm.dibujar(lz, CAM, ruina, ne.LUCES_MAR, ne.AMB_MAR, niebla)

    uv, alto = nj.empaquetar()
    # La fase III: venas de la maldicion, ojos violeta, el coral muriendose.
    tex = vr.cargar(os.path.join(A, 'entity/nerea/nerea_f3.png'))
    brillo = vr.cargar(os.path.join(A, 'entity/nerea/nerea_brillo_f3.png'))
    pose = pose_poster()
    M = vr.entidad_a_mundo(*NEREA_EN, GUINADA, nj.ESCALA)
    qs = nj.quads(pose, uv, alto, M)
    for Pq, UVq, _ in qs:
        n = vr.normal(Pq)
        luz = vr.iluminar(n, CAM, np.mean(Pq, axis=0), LUCES, AMBIENTE)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [Pq[k] for k in tri], [UVq[k] for k in tri], tex, luz, brillo, niebla, brillo=1.15)

    pecho = (M @ np.array([*nj.punto(pose, 'torso', (0, -17, -9)), 1.0]))[:3]

    # --- a resolucion final ---
    color = Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    emis = Image.fromarray((np.clip(lz.emis, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)

    lejos = np.array([CAM.ojo[0] + CAM.f[0] * 400, 0.0, CAM.ojo[2] + CAM.f[2] * 400])
    horiz = CAM.proyectar(lejos)[1] / SS
    fondo = ne.fondo_mar(W, H, horiz)
    # resplandor magenta detras: el corazon maldito ilumina el agua
    cx, cy, _ = CAM.proyectar(pecho)
    cx, cy = cx / SS, cy / SS
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.hypot((xx - cx) / (W * 0.28), (yy - cy) / (H * 0.38))
    fondo = fondo + np.array([0.55, 0.06, 0.32])[None, None] * np.exp(-dd ** 2 * 1.4)[..., None] * 0.55
    fondo += ne.rayos(W, H, 5, n=9)[..., None] * np.array([0.45, 0.85, 0.9]) * 0.7
    fondo_img = Image.fromarray((np.clip(fondo, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    color = color.convert('RGBA')
    color.putalpha(alfa)
    fondo_img.alpha_composite(color)

    # rayos de luz tambien POR DELANTE: agua entre camara y bicho
    rayos_frente = ne.rayos(W, H, 41, n=5)[..., None] * np.array([0.5, 0.9, 1.0]) * 0.22
    fondo_img = sumar(fondo_img, Image.fromarray((np.clip(rayos_frente, 0, 1) * 255).astype(np.uint8)), 1.0)

    e = emis.convert('RGB')
    for radio, k in ((px(5), 0.9), (px(18), 0.7), (px(60), 0.5)):
        fondo_img = sumar(fondo_img, e.filter(ImageFilter.GaussianBlur(radio)), k)
    img = sumar(fondo_img, e, 1.0).convert('RGBA')

    # --- particulas propias, en 2D ---
    def sprite(nombre, lado):
        return Image.open(os.path.join(P, nombre)).convert('RGBA').resize((lado, lado), Image.NEAREST)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    r = random.Random(9)
    ojo = (M @ np.array([*nj.punto(pose, 'ojo_izq'), 1.0]))[:3]
    ox, oy, _ = CAM.proyectar(ojo)
    for _ in range(14):                          # destellos que van a los ojos
        a = r.uniform(0, math.tau)
        d = r.uniform(px(30), px(130))
        s = sprite(f'nerea_ojo_{r.randint(0, 2)}.png', px(r.choice([16, 22, 28])))
        capa.alpha_composite(s, (int(ox / SS + math.cos(a) * d), int(oy / SS + math.sin(a) * d)))
    for _ in range(10):                          # el latido del corazon
        s = sprite(f'nerea_corazon_{r.randint(0, 2)}.png', px(r.choice([22, 30, 40])))
        capa.alpha_composite(s, (int(cx + r.uniform(-px(120), px(120))), int(cy + r.uniform(-px(140), px(80)))))
    pie_x, pie_y, _ = CAM.proyectar(np.array(NEREA_EN))
    for _ in range(40):                          # burbujas que suben
        s = sprite(f'nerea_burbuja_{r.randint(0, 1)}.png', px(r.choice([14, 18, 24, 32])))
        bx_ = int(r.uniform(px(980), W - px(60)))
        by_ = int(r.uniform(px(130), H - px(220)))
        capa.alpha_composite(s, (bx_, by_))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(px(6))))
    img.alpha_composite(capa)
    espuma = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for _ in range(30):                          # arena y espuma levantadas a los pies
        s = sprite(f'nerea_{r.choice(["espuma", "polvo"])}_{r.randint(1, 3)}.png', px(r.choice([70, 100, 140])))
        s.putalpha(s.getchannel('A').point(lambda v: int(v * 0.6)))
        espuma.alpha_composite(s, (int(pie_x / SS + r.uniform(-px(600), px(380))), int(pie_y / SS - r.uniform(-px(30), px(110)))))
    img.alpha_composite(espuma.filter(ImageFilter.GaussianBlur(px(3))))
    ne.burbujas(img, int(40 * ESCALA), 17, zona=((px(1000), W - px(40)), (px(140), H - px(200))))

    # --- grado y vineta ---
    f = np.array(img).astype(float) / 255.0
    vin = 1 - 0.6 * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.32, 0, 1) ** 1.4
    f[..., :3] *= vin[..., None]
    f[..., :3] = np.clip(f[..., :3] * np.array([0.93, 1.0, 1.04]) + np.random.default_rng(2).normal(0, 0.011, (H, W, 1)), 0, 1)
    img = Image.fromarray((f * 255).astype(np.uint8)).convert('RGBA')

    # --- el anuncio ---
    gr = np.zeros((H, W, 4), np.uint8)
    gr[..., :3] = (2, 10, 16)
    gr[..., 3] = (np.clip(1 - xx / (W * 0.56), 0, 1) ** 1.5 * 215).astype(np.uint8)
    img.alpha_composite(Image.fromarray(gr))
    d = ImageDraw.Draw(img)
    CIAN = (110, 236, 220, 255)
    MAGENTA = (255, 70, 140, 255)
    BLANCO = (240, 246, 244, 255)
    GRIS = (178, 200, 202, 255)

    x0 = px(110)
    texto_espaciado(d, (x0, px(110)), 'ATALAYA  ·  JEFE ELEMENTAL DEL AGUA', fuente('Montserrat-Bold.ttf', 22), CIAN, px(5))
    brillo_texto(img, (x0 - px(6), px(130)), 'NEREA', fuente('Oswald-Bold.ttf', 210), BLANCO, (40, 220, 210, 210), px(24))
    d = ImageDraw.Draw(img)
    texto_espaciado(d, (x0, px(392)), 'GUARDIÁN DE LOS MARES', fuente('Oswald-Bold.ttf', 40), CIAN, px(6))
    d.text((x0, px(452)), 'Rompe sus cadenas. Libera su corazón.', font=fuente('Montserrat-SemiBoldItalic.ttf', 32), fill=GRIS)
    d.rectangle((x0, px(506), x0 + px(90), px(511)), fill=MAGENTA)

    def icono(ruta, lado):
        im = Image.open(ruta).convert('RGBA')
        bb = im.getbbox()
        if bb:
            im = im.crop(bb)
        k = max(1, int(lado / max(im.size)))
        return im.resize((im.width * k, im.height * k), Image.NEAREST)

    filas = [
        (icono(os.path.join(A, 'gui/nerea_barra_corazon_3.png'), px(58)), 'EL CORAZÓN MALDITO', 'Se raja en cada fase. Libéralo.'),
        (icono(os.path.join(P, 'nerea_remolino_1.png'), px(64)), 'EL REMOLINO', 'Te arrastra a sus pies. Solo la luz te suelta.'),
        (icono(os.path.join(P, 'nerea_ojo_0.png'), px(56)), 'LA MIRADA DEL ABISMO', 'Apágale los ojos a flechazos o cae.'),
    ]
    y = px(540)
    for ic, titulo, linea in filas:
        img.alpha_composite(Image.new('RGBA', (px(84), px(84)), (180, 255, 245, 20)), (x0, y))
        img.alpha_composite(ic, (x0 + (px(84) - ic.width) // 2, y + (px(84) - ic.height) // 2))
        d.text((x0 + px(108), y + px(6)), titulo, font=fuente('Oswald-Bold.ttf', 34), fill=BLANCO)
        d.text((x0 + px(108), y + px(48)), linea, font=fuente('Montserrat-Medium.ttf', 22), fill=GRIS)
        y += px(108)

    # franja inferior
    banda_y = px(902)
    img.alpha_composite(Image.new('RGBA', (W, H - banda_y), (3, 14, 20, 210)), (0, banda_y))
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

    bloque(px(110), icono(os.path.join(P, 'nerea_onda_0.png'), px(52)), '30-40 JUGADORES', 'jefe de servidor')
    bloque(px(500), icono(os.path.join(P, 'nerea_corazon_0.png'), px(48)), '4 FASES', 'cada una más feroz')
    bloque(px(840), icono(os.path.join(P, 'nerea_chispa_0.png'), px(48)), '6 ATAQUES', 'todos avisan antes')
    bloque(px(1180), icono(os.path.join(A, 'item/lagrima_nerea.png'), px(56)), 'LÁGRIMA DE NEREA', 'núcleo del agua')
    bloque(px(1560), icono(os.path.join(A, 'item/huevo_nerea.png'), px(56)), 'HUEVO', 'generador')

    fs = fuente('Oswald-Bold.ttf', 26)
    tw = d.textlength('HARDCORE', font=fs)
    bx, by = W - px(110) - tw - px(36), px(60)
    d.rectangle((bx, by, bx + tw + px(36), by + px(52)), outline=MAGENTA, width=px(3))
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

"""
Poster promocional del Vigia, estilo arte de trailer: el bicho en pose de
accion, de noche, con su rayo saliendo del ojo, y la informacion justa.

Todo lo que sale en la imagen esta hecho para el mod: la malla y las texturas
del Vigia (via vigia_render.py), su rayo, sus particulas, sus iconos, el cielo,
el suelo y la atalaya del horizonte. Las fuentes son las del sistema.

Uso: python vigia_poster.py <raiz del proyecto> <salida.png> [escala]
"""
import math, os, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr

RAIZ, SALIDA = sys.argv[1], sys.argv[2]
ESCALA = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
P = os.path.join(A, 'particle')
FUENTES = 'C:/Windows/Fonts/'
W, H = int(1920 * ESCALA), int(1080 * ESCALA)
SS = 2                                    # supermuestreo: se pinta al doble y se reduce
rnd = random.Random(11)

# ----------------------------------------------------------------------
#  La pose: la mirada a punto de disparar. Se yergue, abre los brazos con
#  las garras crispadas, la capa vuela y el ojo, dilatado, apunta a camara.
# ----------------------------------------------------------------------
POSE = {
    'torso':        {'rot': (-16, 14, 3)},
    'cuello':       {'rot': (-4, 0, 0)},
    'cabeza':       {'rot': (8, -14, 8)},
    'ojo':          {'esc': 1.55},
    'capa':         {'rot': (34, 0, 7)},
    'brazo_izq':    {'rot': (18, -10, -82)},
    'antebrazo_izq': {'rot': (-70, 0, 0)},
    'garras_izq':   {'rot': (50, 0, 0)},
    'brazo_der':    {'rot': (10, 15, 100)},
    'antebrazo_der': {'rot': (-55, 0, 0)},
    'garras_der':   {'rot': (45, 0, 0)},
    'pierna_izq':   {'rot': (-24, 0, -7)},
    'espinilla_izq': {'rot': (28, 0, 0)},
    'pie_izq':      {'rot': (-6, 0, 0)},
    'pierna_der':   {'rot': (20, 0, 9)},
    'espinilla_der': {'rot': (12, 0, 0)},
}

GUINADA = float(os.environ.get("GUINADA", "45"))
# Camara baja (heroica), y apuntando a la izquierda del bicho: asi el Vigia
# queda en el tercio derecho y el texto respira a la izquierda.
CAM = vr.Camara(ojo=(-2.4, 0.65, -6.6), objetivo=(2.35, 2.2, 0), fov=40, ancho=W * SS, alto=H * SS)

LUCES = [
    ((-0.6, 0.9, -0.7), (0.62, 0.70, 0.95), 0.95, 'llave'),      # luna, fria
    ((0.9, 0.35, 0.8), (1.0, 0.22, 0.12), 1.25, 'contra'),       # resplandor rojo detras
    ((0.2, -1.0, -0.2), (0.35, 0.12, 0.08), 0.35, 'llave'),      # rebote calido del suelo
]
AMBIENTE = (0.16, 0.16, 0.22)

class Niebla:
    color = (0.09, 0.05, 0.11)
    def __call__(self, z):
        return np.clip((z - 7.0) / 22.0, 0, 0.92)

def suelo_tex():
    """Losas de piedra musgosa oscura, 16x16, pintadas aqui."""
    r = random.Random(3)
    t = np.zeros((16, 16, 4), np.uint8)
    for y in range(16):
        for x in range(16):
            base = r.choice([(46, 48, 56), (52, 54, 62), (40, 42, 50), (58, 60, 68)])
            if r.random() < 0.18:
                base = r.choice([(40, 58, 44), (48, 66, 50)])      # musgo
            if x == 0 or y == 0:
                base = (30, 30, 38)                                 # junta
            t[y, x] = (*base, 255)
    return t

# ----------------------------------------------------------------------
#  Utilidades de composicion
# ----------------------------------------------------------------------
def fuente(nombre, tam):
    return ImageFont.truetype(FUENTES + nombre, int(tam * ESCALA))

def px(n):
    return int(round(n * ESCALA))

def icono(ruta, lado):
    im = Image.open(ruta).convert('RGBA')
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    k = max(1, int(lado / max(im.size)))
    return im.resize((im.width * k, im.height * k), Image.NEAREST)

def dibujo(filas, lado, paleta):
    """Icono de pixel-art desde una lista de cadenas."""
    h, w = len(filas), len(filas[0])
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y, fila in enumerate(filas):
        for x, c in enumerate(fila):
            if c in paleta:
                im.putpixel((x, y), paleta[c])
    k = max(1, int(lado / max(w, h)))
    return im.resize((w * k, h * k), Image.NEAREST)

CORAZON = ["..##.##..", ".#aa#bb#.", "#aaaabbb#", "#aaaaabb#", "#aaaaaab#", ".#aaaaa#.", "..#aaa#..", "...#a#...", "....#...."]
ESCUDO = ["#########", "#bbbabbb#", "#bbbabbb#", "#aaaaaaa#", "#bbbabbb#", ".#bbabb#.", ".#bbabb#.", "..#bab#..", "...###..."]
LUNA = ["...####...", ".##aaaa##.", "#aabaaaaa#", "#aaaaacaa#", "#acaaaaaa#", "#aaaabaaa#", "#aaaaaaca#", ".##aaaa##.", "...####..."]
PAL_LUNA = {'#': (205, 210, 225, 255), 'a': (232, 234, 242, 255), 'b': (196, 200, 214, 255), 'c': (214, 218, 230, 255)}

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

# ----------------------------------------------------------------------
#  Cielo y horizonte: todo pintado aqui
# ----------------------------------------------------------------------
def cielo(horizonte_y, centro_brillo):
    y = np.linspace(0, 1, H)[:, None, None]
    arriba = np.array([10, 9, 24]) / 255.0
    medio = np.array([26, 14, 38]) / 255.0
    abajo = np.array([70, 18, 30]) / 255.0
    t = np.clip(y / (horizonte_y / H), 0, 1)
    col = np.where(t < 0.6, arriba + (medio - arriba) * (t / 0.6), medio + (abajo - medio) * ((t - 0.6) / 0.4))
    col = np.broadcast_to(col, (H, W, 3)).copy()
    # el resplandor rojo detras del Vigia
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = centro_brillo
    d = np.hypot((xx - cx) / (W * 0.30), (yy - cy) / (H * 0.42))
    col += np.array([0.75, 0.10, 0.06])[None, None] * np.exp(-d ** 2 * 1.6)[..., None] * 0.85
    img = Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    d2 = ImageDraw.Draw(img)
    r = random.Random(7)
    for _ in range(int(260 * ESCALA)):
        sx, sy = r.randrange(W), r.randrange(max(1, int(horizonte_y * 0.85)))
        b = r.randint(120, 255)
        tam = px(1.5) if r.random() < 0.85 else px(3)
        d2.rectangle((sx, sy, sx + tam, sy + tam), fill=(b, b, min(255, b + 20), 255))
    luna = dibujo(LUNA, px(150), PAL_LUNA)
    lx, ly = px(840), px(40)
    halo = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse((lx - px(60), ly - px(60), lx + luna.width + px(60), ly + luna.height + px(60)),
                                 fill=(180, 190, 255, 60))
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(px(40))))
    img.alpha_composite(luna, (lx, ly))
    return img

def horizonte(img, y0):
    """Colinas de bloques y, en lo alto de una, la atalaya: el nombre del mod."""
    d = ImageDraw.Draw(img)
    r = random.Random(4)
    bloque = px(14)
    for col, alt, var in (((34, 16, 34), 90, 50), ((22, 12, 26), 55, 35)):
        x = 0
        h = alt
        while x < W:
            h = max(10, min(alt + var, h + r.choice([-14, 0, 0, 14])))
            d.rectangle((x, y0 - px(h), x + bloque, y0 + px(6)), fill=(*col, 255))
            x += bloque
    tx, base = px(760), y0 - px(120)
    sil = (18, 10, 22, 255)
    d.rectangle((tx - px(70), base, tx + px(70), y0), fill=sil)
    d.rectangle((tx - px(18), base - px(150), tx + px(18), base), fill=sil)
    d.rectangle((tx - px(30), base - px(178), tx + px(30), base - px(150)), fill=sil)
    for k in range(-30, 31, 15):
        d.rectangle((tx + px(k) - px(5), base - px(192), tx + px(k) + px(5), base - px(178)), fill=sil)
    # su ventana encendida: la misma luz ambar que el ojo en calma
    d.rectangle((tx - px(5), base - px(170), tx + px(5), base - px(158)), fill=(255, 180, 60, 255))

# ----------------------------------------------------------------------
#  El rayo, en 3D, con la geometria de RayoVigiaModel
# ----------------------------------------------------------------------
def rayo_quads(punta, direccion):
    z = np.array(direccion, float); z /= np.linalg.norm(z)
    x = np.cross([0, 1, 0], z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    R = np.eye(4); R[:3, 0] = x; R[:3, 1] = y; R[:3, 2] = z
    M = vr.T(*punta) @ R @ vr.S(1.2 / 16)
    cajas = [((0, 0), (-1, -1, -24, 2, 2, 28), 0), ((0, 30), (-2.5, -2.5, -20, 5, 5, 22), 0),
             ((0, 30), (-2.5, -2.5, -20, 5, 5, 22), 45), ((64, 0), (-2, -2, 0, 4, 4, 4), 0),
             ((60, 30), (-1.5, -1.5, -48, 3, 3, 30), 0)]
    out = []
    for tex, box, giro in cajas:
        Mg = M @ vr.Rz(giro * vr.D2R)
        for pts, uvs in vr.caja_quads(tex, box, False, 128, 64):
            out.append(([(Mg @ np.array([*q, 1.0]))[:3] for q in pts], uvs))
    return out

def sumar(base, capa_rgb, k=1.0):
    f = np.array(base).astype(float)
    f[..., :3] = np.clip(f[..., :3] + np.array(capa_rgb).astype(float)[..., :3] * k, 0, 255)
    return Image.fromarray(f.astype(np.uint8))

def main():
    lz = vr.Lienzo(W * SS, H * SS)
    tex = vr.cargar(os.path.join(A, 'entity/vigia/vigia.png'))
    brillo = vr.cargar(os.path.join(A, 'entity/vigia/vigia_ojo_caza.png'))
    rayo_tex = vr.cargar(os.path.join(A, 'entity/vigia/rayo.png'))
    niebla = Niebla()

    st = suelo_tex()
    quads = []
    for gx in range(-18, 16):
        for gz in range(-8, 40):
            h = 0.0 if abs(gx) < 4 and gz < 6 else rnd.choice([0, 0, 0, 0.0625, -0.0625])
            P0 = [(gx, h, gz), (gx + 1, h, gz), (gx + 1, h, gz + 1), (gx, h, gz + 1)]
            quads.append((P0, [(0, 0), (1, 0), (1, 1), (0, 1)], 'suelo'))
    vr.dibujar_quads(lz, CAM, quads, st, luces=LUCES[:1], ambiente=(0.2, 0.2, 0.27), niebla=niebla)

    M = vr.entidad_a_mundo(0.55, 0.0, 0.0, GUINADA, 1.0)
    vigia = vr.quads_del_modelo(POSE, modelo_a_mundo=M)
    vr.dibujar_quads(lz, CAM, vigia, tex, emis=brillo, luces=LUCES, ambiente=AMBIENTE, brillo=1.6)

    # El ojo, en mundo: centro de su caja. El rayo sale de ahi y pasa rozando
    # la camara por la izquierda.
    ojo = np.mean([np.mean(q[0], axis=0) for q in vigia if q[2] == 'ojo'], axis=0)
    # Cruza la escena de lado, hacia donde estaria el jugador (fuera de cuadro
    # por la izquierda), un poco hacia la camara y algo hacia abajo: asi se
    # lee como un disparo y no como un fogonazo pegado al objetivo.
    dirr = CAM.r * 10.0 - CAM.f * 8.0 - CAM.u * 1.6
    # La cola mide 48 pixeles de malla: con la punta a esa distancia del ojo,
    # el rayo arranca justo en el y no asoma por detras de la cabeza.
    punta = ojo + dirr / np.linalg.norm(dirr) * (48 * 1.2 / 16)
    for Pq, UVq in rayo_quads(punta, dirr):
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(CAM, [Pq[i] for i in tri], [UVq[i] for i in tri], rayo_tex, None, aditivo=True, brillo=0.9)

    # --- a resolucion final ---
    color = Image.fromarray((np.clip(lz.color, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = Image.fromarray((lz.alfa * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    emis = Image.fromarray((np.clip(lz.emis, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)

    ox, oy, _ = CAM.proyectar(ojo)
    lejos = np.array([CAM.ojo[0] + CAM.f[0] * 400, 0.0, CAM.ojo[2] + CAM.f[2] * 400])
    horiz = CAM.proyectar(lejos)[1] / SS
    fondo = cielo(horiz, (ox / SS, oy / SS + px(120)))
    horizonte(fondo, int(horiz))
    color = color.convert('RGBA'); color.putalpha(alfa)
    fondo.alpha_composite(color)

    # bloom: tres radios; el amplio tine el aire alrededor del ojo
    e = emis.convert('RGB')
    for radio, k in ((px(5), 0.8), (px(18), 0.6), (px(55), 0.45)):
        fondo = sumar(fondo, e.filter(ImageFilter.GaussianBlur(radio)), k)
    fondo = sumar(fondo, e, 1.0).convert('RGBA')

    # --- particulas propias, en 2D sobre la imagen ---
    def sprite(nombre, lado):
        return Image.open(os.path.join(P, nombre)).convert('RGBA').resize((lado, lado), Image.NEAREST)
    capa = Image.new('RGBA', fondo.size, (0, 0, 0, 0))
    r = random.Random(9)
    ex, ey = ox / SS, oy / SS
    for _ in range(16):                        # chispas que convergen al ojo
        a = r.uniform(0, math.tau); dd = r.uniform(px(40), px(150))
        s = sprite(f'vigia_chispa_{r.randint(0, 2)}.png', px(r.choice([18, 24, 30])))
        capa.alpha_composite(s, (int(ex + math.cos(a) * dd), int(ey + math.sin(a) * dd)))
    pie_x, pie_y, _ = CAM.proyectar((0.55, 0.0, 0.0))
    for _ in range(14):                        # almas que suben desde el suelo
        s = sprite(f'vigia_alma_{r.randint(0, 2)}.png', px(r.choice([22, 28, 36])))
        capa.alpha_composite(s, (int(pie_x / SS + r.uniform(-px(320), px(320))), int(pie_y / SS - r.uniform(px(40), px(520)))))
    for _ in range(0):                         # (sin marcas sueltas: distraian)
        s = sprite(f'vigia_marca_{r.randint(0, 1)}.png', px(r.choice([26, 34])))
        capa.alpha_composite(s, (int(r.uniform(px(820), px(1050))), int(r.uniform(px(560), px(820)))))
    fondo.alpha_composite(capa.filter(ImageFilter.GaussianBlur(px(8))))
    fondo.alpha_composite(capa)
    humo = Image.new('RGBA', fondo.size, (0, 0, 0, 0))
    for _ in range(26):                        # niebla baja de humo a los pies
        s = sprite(f'vigia_humo_{r.randint(2, 4)}.png', px(r.choice([90, 120, 160])))
        s.putalpha(s.getchannel('A').point(lambda v: int(v * 0.55)))
        humo.alpha_composite(s, (int(pie_x / SS + r.uniform(-px(700), px(500))), int(pie_y / SS - r.uniform(-px(40), px(90)))))
    fondo.alpha_composite(humo.filter(ImageFilter.GaussianBlur(px(3))))

    # --- grado de color y vineta ---
    f = np.array(fondo).astype(float) / 255.0
    yy, xx = np.mgrid[0:H, 0:W]
    vin = 1 - 0.55 * np.clip(np.hypot((xx - W / 2) / (W * 0.62), (yy - H / 2) / (H * 0.62)) - 0.35, 0, 1) ** 1.4
    f[..., :3] *= vin[..., None]
    grano = np.random.default_rng(2).normal(0, 0.012, (H, W, 1))
    f[..., :3] = np.clip(f[..., :3] + grano, 0, 1)
    img = Image.fromarray((f * 255).astype(np.uint8)).convert('RGBA')

    # --- el anuncio ---
    gr = np.zeros((H, W, 4), np.uint8)
    gr[..., 3] = (np.clip(1 - xx / (W * 0.55), 0, 1) ** 1.6 * 200).astype(np.uint8)
    img.alpha_composite(Image.fromarray(gr))
    d = ImageDraw.Draw(img)
    AMBAR = (255, 180, 58, 255); ROJO = (255, 64, 40, 255); BLANCO = (245, 242, 236, 255); GRIS = (196, 190, 200, 255)

    x0 = px(110)
    texto_espaciado(d, (x0, px(118)), 'ATALAYA  ·  NUEVA AMENAZA', fuente('Montserrat-Bold.ttf', 22), AMBAR, px(5))
    brillo_texto(img, (x0 - px(6), px(140)), 'EL VIGÍA', fuente('Oswald-Bold.ttf', 196), BLANCO, (255, 40, 20, 200), px(22))
    d = ImageDraw.Draw(img)
    d.text((x0, px(400)), 'Lo que mira, lo maldice.', font=fuente('Montserrat-SemiBoldItalic.ttf', 38), fill=GRIS)
    d.rectangle((x0, px(462), x0 + px(90), px(467)), fill=ROJO)

    filas = [
        (icono(os.path.join(A, 'mob_effect/marcado.png'), px(64)), 'LA MIRADA', 'Te marca. Todo viene a por ti.'),
        (icono(os.path.join(P, 'vigia_zarpa_1.png'), px(64)), 'EL CEPO', 'Te atrapa a dos bloques.'),
        (icono(os.path.join(P, 'vigia_esquirla_0.png'), px(56)), 'PUNTO CIEGO', 'Rodéalo: +50 % por la espalda.'),
    ]
    y = px(505)
    for ic, titulo, linea in filas:
        img.alpha_composite(Image.new('RGBA', (px(84), px(84)), (255, 255, 255, 18)), (x0, y))
        img.alpha_composite(ic, (x0 + (px(84) - ic.width) // 2, y + (px(84) - ic.height) // 2))
        d.text((x0 + px(108), y + px(6)), titulo, font=fuente('Oswald-Bold.ttf', 34), fill=BLANCO)
        d.text((x0 + px(108), y + px(48)), linea, font=fuente('Montserrat-Medium.ttf', 22), fill=GRIS)
        y += px(108)

    # franja inferior: donde, cuanto aguanta, que deja
    banda_y = px(902)
    img.alpha_composite(Image.new('RGBA', (W, H - banda_y), (8, 6, 14, 205)), (0, banda_y))
    d.rectangle((0, banda_y, W, banda_y + px(3)), fill=ROJO)
    cy = banda_y + px(80)
    fx = fuente('Montserrat-Bold.ttf', 24); fp = fuente('Montserrat-Medium.ttf', 18)

    def bloque(x, ic, titulo, sub):
        img.alpha_composite(ic, (x, cy - ic.height // 2))
        dd = ImageDraw.Draw(img)
        dd.text((x + ic.width + px(18), cy - px(30)), titulo, font=fx, fill=BLANCO)
        dd.text((x + ic.width + px(18), cy + px(4)), sub, font=fp, fill=GRIS)

    bloque(px(110), dibujo(LUNA, px(52), PAL_LUNA), 'DE NOCHE', 'en todo el mundo')
    bloque(px(470), dibujo(CORAZON, px(48), {'#': (60, 8, 8, 255), 'a': (230, 40, 40, 255), 'b': (255, 120, 120, 255)}), '30 CORAZONES', 'un minijefe')
    bloque(px(830), dibujo(ESCUDO, px(48), {'#': (40, 40, 48, 255), 'a': (150, 155, 170, 255), 'b': (200, 205, 215, 255)}), 'ARMADURA 8', 'aguanta golpes')
    bloque(px(1170), icono(os.path.join(A, 'item/huevo_vigia.png'), px(56)), 'HUEVO', 'generador')
    bloque(px(1460), icono(os.path.join(A, 'item/ojo_vigia.png'), px(56)), 'OJO DEL VIGÍA', 'revela monstruos')

    # sello hardcore y version
    d = ImageDraw.Draw(img)
    fs = fuente('Oswald-Bold.ttf', 26)
    tw = d.textlength('HARDCORE', font=fs)
    bx, by = W - px(110) - tw - px(36), px(60)
    d.rectangle((bx, by, bx + tw + px(36), by + px(52)), outline=ROJO, width=px(3))
    d.text((bx + px(18), by + px(6)), 'HARDCORE', font=fs, fill=ROJO)
    d.text((W - px(110) - d.textlength('Minecraft 26.2 · Fabric', font=fp), banda_y - px(36)),
           'Minecraft 26.2 · Fabric', font=fp, fill=(170, 160, 175, 255))

    img.convert('RGB').save(SALIDA)
    print('ok', W, H)

main()

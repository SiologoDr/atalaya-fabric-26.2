"""
Los rotulos de la presentacion de los jefes: lo que sale en mitad de la
pantalla, entre las bandas negras, cuando un jefe despierta y ruge. Mismo
idioma que los posters de promo (nerea_poster.py, aeralis_poster.py,
rajang_poster.py): el nombre en Oswald Bold casi blanco con el halo del color
del jefe, el antetitulo en Montserrat Bold espaciado y del color de acento, el
epiteto en SemiBoldItalic y el lema en Medium gris. Novilis no tiene poster:
sus colores salen de su HUD (novilis_hud.py, ORO y CARMESI).

El Java anima cada capa por separado (fundido, un poco de desliz vertical,
cortina que se abre desde el centro y un destello que la barre), asi que el
rotulo va partido en capas sobre lienzos identicos que se apilan tal cual.

Las dibuja 1:1 en pixeles de PANTALLA (no de interfaz), centradas en
horizontal, y escoge el ancho mayor que quepa en el 80 % de la pantalla. Por
eso hay cuatro anchos, y los textos pequenos no escalan del todo en
proporcion: en la ventana por defecto (854x480, lienzo de 480) el lema a
escala saldria de 8 px y no se leeria.

Uso: python presentacion_jefes.py <raiz del proyecto> [<carpeta de hoja>]

Escribe en textures/gui/presentacion:
  <jefe>_<W>_nombre.png            el nombre con su halo (sin idioma)
  <jefe>_<W>_linea.png             el adorno entre nombre y epiteto (sin idioma)
  <jefe>_<idioma>_<W>_ante.png     el antetitulo (JEFE DEL MAR...)
  <jefe>_<idioma>_<W>_epiteto.png  el epiteto y, debajo, el lema
  destello.png                     el destello que barre el rotulo (512x64),
                                   en blanco y grises: el Java lo tine
con W en 480, 720, 960 y 1440, alto round(W*0.34), e idioma es o en.

Composicion, igual en todas las capas (centro de la altura de mayusculas, en
fraccion del alto H; la linea, su eje): antetitulo 0.155, nombre 0.455,
linea 0.69, epiteto 0.79, lema 0.905. Fondo transparente y el alfa a cero en
los cuatro bordes.

Con la carpeta de hoja monta ademas las vistas previas: cada jefe a 960 sobre
cielo y sobre cueva, los cuatro a 720 en los dos idiomas, y los cuatro a 480
sobre capturas reales del juego (854x480, la ventana por defecto).
"""
import math, os, sys, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

RAIZ = sys.argv[1]
HOJA = sys.argv[2] if len(sys.argv) > 2 else None
SALIDA = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/presentacion')
CAPTURAS = os.path.join(RAIZ, 'run/screenshots')
FUENTES = 'C:/Windows/Fonts/'
ANCHOS = (480, 720, 960, 1440)
IDIOMAS = ('es', 'en')
SS = 2          # se dibuja al doble y se reduce con LANCZOS


def alto(w):
    return int(round(w * 0.34))


# ----------------------------------------------------------------------
#  Composicion vertical, igual en todas las capas para que se apilen.
#  Cada numero es el centro de la altura de mayusculas (de la linea base a
#  lo alto de la H), en fraccion del alto del lienzo. El de la linea es su eje.
# ----------------------------------------------------------------------
Y_ANTE = 0.155
Y_NOMBRE = 0.455
Y_LINEA = 0.69
Y_EPITETO = 0.79
Y_LEMA = 0.905

# altura de mayusculas del nombre, en fraccion del ancho. Con 0.13 (lo
# pedido) el nombre pisaba la linea: el lienzo solo tiene 0.34 de alto.
CAP_NOMBRE = 0.118
AIRE_NOMBRE = 0.035   # aire extra entre letras del nombre, en fraccion del cuerpo


# tamanos de letra (cuerpo, en px de pantalla) del resto: a + b*W. A 960 son
# casi los del poster en proporcion al nombre; a 480 suben para leerse.
def cuerpo_ante(w):
    return 6.0 + 0.0135 * w


def cuerpo_epiteto(w):
    return 6.5 + 0.0185 * w


def cuerpo_lema(w):
    return 5.5 + 0.0135 * w


JEFES = {
    'nerea': dict(
        nombre='NEREA',
        ante={'es': 'JEFE DEL MAR', 'en': 'SEA BOSS'},
        epiteto={'es': 'Guardián de los Mares', 'en': 'Guardian of the Seas'},
        lema={'es': 'Rompe sus cadenas. Libera su corazón.', 'en': 'Break his chains. Free his heart.'},
        acento=(110, 236, 220), halo=(40, 220, 210), linea=(255, 70, 140), blanco=(240, 246, 244),
        epi=(205, 228, 230), gris=(178, 200, 202), sombra=(2, 14, 18)),
    'aeralis': dict(
        nombre='AERALIS',
        ante={'es': 'JEFE DEL AIRE', 'en': 'AIR BOSS'},
        epiteto={'es': 'La Mariposa del Vendaval', 'en': 'The Gale Moth'},
        lema={'es': 'Calma la tormenta. Apaga el ojo de su pecho.', 'en': 'Calm the storm. Put out the eye in her chest.'},
        acento=(120, 214, 255), halo=(120, 150, 255), linea=(190, 140, 255), blanco=(240, 244, 252),
        epi=(205, 214, 236), gris=(184, 194, 214), sombra=(6, 6, 22)),
    'rajang': dict(
        nombre='RAJANG',
        ante={'es': 'JEFE DE LA TIERRA', 'en': 'EARTH BOSS'},
        epiteto={'es': 'El Jaguar de Jade', 'en': 'The Jade Jaguar'},
        lema={'es': 'Resiste el cataclismo. Arranca la raíz de su pecho.',
              'en': 'Withstand the cataclysm. Tear the root from his chest.'},
        acento=(118, 236, 158), halo=(60, 210, 110), linea=(248, 217, 124), blanco=(244, 248, 236),
        epi=(212, 232, 214), gris=(182, 204, 188), sombra=(3, 12, 8)),
    # sin poster: ORO[4] y CARMESI[3] de novilis_hud.py, y el halo del fuego
    'novilis': dict(
        nombre='NOVILIS',
        ante={'es': 'JEFE DEL FUEGO', 'en': 'FIRE BOSS'},
        epiteto={'es': 'El Caballero Solar', 'en': 'The Solar Knight'},
        lema={'es': 'Rompe sus fuentes. Apaga su sol.', 'en': 'Break his fonts. Put out his sun.'},
        acento=(255, 206, 110), halo=(255, 116, 28), linea=(255, 42, 58), blanco=(252, 246, 234),
        epi=(240, 224, 206), gris=(206, 192, 182), sombra=(20, 6, 4)),
}


def fuente(nombre, tam):
    return ImageFont.truetype(FUENTES + nombre, max(1, int(round(tam))))


def gauss(m, s):
    """Desenfoque gaussiano. Los anchos (halos, velos) se hacen sobre la
    mascara reducida y se vuelven a ampliar: salen igual y diez veces antes."""
    if s <= 0:
        return m
    k = int(s // 4)
    if k < 2:
        return ndimage.gaussian_filter(m, s)
    h, w = m.shape
    hk, wk = h // k, w // k
    peq = m[:hk * k, :wk * k].reshape(hk, k, wk, k).mean(axis=(1, 3))
    peq = ndimage.gaussian_filter(peq, math.sqrt(max(s * s - k * k / 12.0, 1.0)) / k)
    out = ndimage.zoom(peq, k, order=1, grid_mode=True, mode='nearest')
    return np.pad(out, ((0, h - out.shape[0]), (0, w - out.shape[1])), mode='edge')


def mover(m, dy):
    """Desplaza una mascara dy pixeles hacia abajo (dy entero)."""
    if dy == 0:
        return m
    out = np.zeros_like(m)
    out[dy:] = m[:-dy]
    return out


def lienzo(w, h):
    return np.zeros((h, w, 4), float)


def sobre(capa, color, a):
    """Compone un color (rgb 0-255, o array h*w*3) con alfa a (h*w, 0-1) encima
    de la capa, con alfa recto."""
    c = np.asarray(color, float) / 255.0
    a = np.clip(a, 0, 1)
    ad = capa[..., 3]
    ao = a + ad * (1 - a)
    rgb = (c * a[..., None] + capa[..., :3] * (ad * (1 - a))[..., None]) / np.maximum(ao, 1e-6)[..., None]
    capa[..., :3] = rgb
    capa[..., 3] = ao


def a_imagen(capa, w, h, orillas=True):
    """De la capa al doble a la textura final: LANCZOS (Pillow premultiplica).
    Con orillas, el alfa se apaga en los bordes del lienzo: un velo que llegue
    al borde no deja un corte recto sobre el cielo."""
    if orillas:
        H2, W2 = capa.shape[:2]
        fy = np.clip(np.minimum(np.arange(H2), H2 - 1 - np.arange(H2)) / (0.04 * H2), 0, 1)
        fx = np.clip(np.minimum(np.arange(W2), W2 - 1 - np.arange(W2)) / (0.03 * W2), 0, 1)
        capa = capa.copy()
        capa[..., 3] *= (fy * fy * (3 - 2 * fy))[:, None] * (fx * fx * (3 - 2 * fx))[None, :]
    arr = (np.clip(capa, 0, 1) * 255 + 0.5).astype(np.uint8)
    arr[arr[..., 3] == 0, :3] = 0
    return Image.fromarray(arr, 'RGBA').resize((w, h), Image.LANCZOS)


def mascara_texto(W2, H2, txt, f, y_cap, aire=0.0):
    """Mascara (0-1) del texto en un lienzo W2*H2 al doble, centrado en x por
    su tinta y con el centro de las mayusculas en y_cap (px a 1x). La linea
    base cae en un pixel entero a 1x para que el texto salga nitido."""
    cap = -f.getbbox('H', anchor='ls')[1] / SS
    base = int(round(y_cap + cap / 2.0)) * SS
    asc, desc = f.getmetrics()
    margen = int(f.size * 0.6)
    ancho = int(math.ceil(f.getlength(txt) + aire * len(txt))) + 2 * margen
    tmp = Image.new('L', (ancho, asc + desc + 2 * margen), 0)
    d = ImageDraw.Draw(tmp)
    by = margen + asc
    if aire:
        for i, ch in enumerate(txt):
            d.text((margen + f.getlength(txt[:i]) + aire * i, by), ch, font=f, fill=255, anchor='ls')
    else:
        d.text((margen, by), txt, font=f, fill=255, anchor='ls')
    x0, y0, x1, y1 = tmp.getbbox()
    ox = int(round((W2 / 2.0 - (x0 + x1) / 2.0) / SS)) * SS
    oy = base - by
    out = Image.new('L', (W2, H2), 0)
    out.paste(tmp, (ox, oy))
    return np.asarray(out, float) / 255.0, (x0 + ox, x1 + ox)


def sombra_texto(capa, m, color, cuerpo2, fuerza=1.0):
    """La sombra que deja leer un texto claro sobre cielo y sobre cueva: un
    contorno oscuro apretado, un poco caido, y un velo ancho y suave."""
    velo = gauss(m, 0.45 * cuerpo2)
    sobre(capa, color, np.clip(velo * 1.7, 0, 1) * 0.50 * fuerza)
    apretada = mover(gauss(m, 0.07 * cuerpo2), max(1, int(round(0.05 * cuerpo2))))
    sobre(capa, color, np.clip(apretada * 1.9, 0, 1) * 0.70 * fuerza)


# ----------------------------------------------------------------------
#  Las capas
# ----------------------------------------------------------------------
def capa_nombre(j, w):
    h = alto(w)
    W2, H2 = w * SS, h * SS
    cuerpo2 = CAP_NOMBRE * w / 0.81 * SS          # Oswald: mayuscula = 0.81 del cuerpo
    f = fuente('Oswald-Bold.ttf', cuerpo2)
    m, (x0, x1) = mascara_texto(W2, H2, j['nombre'], f, Y_NOMBRE * h, aire=AIRE_NOMBRE * f.size)
    capa = lienzo(W2, H2)
    s = f.size
    # velo oscuro debajo: sobre cielo claro, el halo y el blanco necesitan fondo
    velo = mover(gauss(m, 0.07 * s), int(0.02 * s))
    sobre(capa, j['sombra'], np.clip(velo * 1.5, 0, 1) * 0.28)
    # el halo de los posters: el texto en el color del halo, desenfocado y
    # puesto dos veces (brillo_texto: radio 24 a cuerpo 196)
    halo = gauss(m, 0.122 * s) * (210 / 255.0)
    sobre(capa, j['halo'], halo)
    sobre(capa, j['halo'], halo)
    # contorno oscuro fino pegado a la letra, para que el blanco recorte
    borde = mover(gauss(m, 0.018 * s), max(1, int(round(0.012 * s))))
    sobre(capa, j['sombra'], np.clip(borde * 2.2, 0, 1) * 0.62)
    # el relleno: casi blanco arriba, tirando al halo abajo
    yy = np.arange(H2, dtype=float)[:, None]
    cap2 = CAP_NOMBRE * w * SS
    top = Y_NOMBRE * H2 - cap2 / 2
    t = np.clip((yy - top) / cap2, 0, 1)[..., None]
    b = np.asarray(j['blanco'], float)
    fondo_ = b * 0.80 + np.asarray(j['halo'], float) * 0.20
    rgb = np.broadcast_to(b * (1 - t ** 1.5) + fondo_ * t ** 1.5, (H2, W2, 3))
    sobre(capa, rgb, m)
    return a_imagen(capa, w, h), ((x1 - x0) / SS)


def capa_ante(j, w, idioma):
    h = alto(w)
    W2, H2 = w * SS, h * SS
    f = fuente('Montserrat-Bold.ttf', cuerpo_ante(w) * SS)
    s = f.size
    m, (x0, x1) = mascara_texto(W2, H2, j['ante'][idioma], f, Y_ANTE * h, aire=0.30 * s)
    # dos trazos a los lados que se apagan hacia fuera
    cap2 = 0.70 * s
    yc = (int(round(Y_ANTE * h + cap2 / SS / 2)) * SS) - cap2 / 2
    hueco, largo, grosor = 0.9 * s, 0.07 * W2, max(SS * 1.0, 0.085 * s)
    xx = np.arange(W2, dtype=float)[None, :]
    yy = np.arange(H2, dtype=float)[:, None]
    fila = np.clip(grosor / 2 - np.abs(yy - yc) + 0.5, 0, 1)
    trazo = np.zeros((H2, W2))
    for lado, borde in ((-1, x0 - hueco), (1, x1 + hueco)):
        u = (xx - borde) * lado / largo                   # 0 junto al texto, 1 fuera
        trazo = np.maximum(trazo, fila * np.clip(1 - u, 0, 1) ** 1.3 * (u >= 0))
    todo = np.maximum(m, trazo)
    capa = lienzo(W2, H2)
    sombra_texto(capa, todo, j['sombra'], s)
    sobre(capa, j['acento'], gauss(m, 0.25 * s) * 0.35)   # un poco de brillo propio
    sobre(capa, j['acento'], todo)
    return a_imagen(capa, w, h)


def capa_epiteto(j, w, idioma):
    h = alto(w)
    W2, H2 = w * SS, h * SS
    fe = fuente('Montserrat-SemiBoldItalic.ttf', cuerpo_epiteto(w) * SS)
    fl = fuente('Montserrat-Medium.ttf', cuerpo_lema(w) * SS)
    me, _ = mascara_texto(W2, H2, j['epiteto'][idioma], fe, Y_EPITETO * h)
    ml, _ = mascara_texto(W2, H2, j['lema'][idioma], fl, Y_LEMA * h)
    capa = lienzo(W2, H2)
    sombra_texto(capa, me, j['sombra'], fe.size)
    sombra_texto(capa, ml, j['sombra'], fl.size)
    sobre(capa, j['epi'], me)
    sobre(capa, j['gris'], ml)
    return a_imagen(capa, w, h)


def rombo(xx, yy, cx, cy, rx, ry):
    """Cobertura con antialias de un rombo de semiejes rx, ry."""
    k = rx * ry / math.hypot(rx, ry)
    dist = (np.abs(xx - cx) / rx + np.abs(yy - cy) / ry - 1) * k
    return np.clip(0.5 - dist, 0, 1)


def capa_linea(j, w):
    h = alto(w)
    W2, H2 = w * SS, h * SS
    xx = np.arange(W2, dtype=float)[None, :]
    yy = np.arange(H2, dtype=float)[:, None]
    cx = W2 / 2.0
    cy = round(Y_LINEA * h) * SS + SS / 2.0 - 0.5
    semi = 0.35 * W2
    u = np.abs(xx - cx) / semi
    # el rombo del centro y dos pequenos a sus lados
    rx, ry = 0.0095 * W2, 0.0125 * W2
    gr = rombo(xx, yy, cx, cy, rx, ry)
    nucleo = rombo(xx, yy, cx, cy, rx * 0.48, ry * 0.48)
    sep = rx * 2.25
    chicos = np.maximum(rombo(xx, yy, cx - sep, cy, rx * 0.36, ry * 0.36),
                        rombo(xx, yy, cx + sep, cy, rx * 0.36, ry * 0.36))
    # la linea: arranca pasado el rombo pequeno, se afina y se apaga hacia fuera
    arranque = (sep + rx * 0.7) / semi
    v = np.clip((u - arranque) / (1 - arranque), 0, 1)
    grosor = max(SS * 1.5, 0.0034 * W2) * (1 - 0.5 * v)
    fila = np.clip(grosor / 2 - np.abs(yy - cy) + 0.5, 0, 1)
    apaga = np.clip(1 - v, 0, 1) ** 1.25 * np.clip((u - arranque) * semi / (SS * 2), 0, 1)
    linea = fila * apaga
    forma = np.maximum(np.maximum(linea, gr), chicos)
    capa = lienzo(W2, H2)
    # sombra para el cielo claro y brillo del color de la linea
    sobre(capa, j['sombra'], np.clip(mover(gauss(forma, 0.004 * W2), SS) * 2.0, 0, 1) * 0.55)
    sobre(capa, j['linea'], np.clip(gauss(forma, 0.006 * W2) * 1.4, 0, 1) * 0.8)
    sobre(capa, j['linea'], gauss(gr, 0.014 * W2) * 0.7)
    # la linea se calienta (hacia blanco) cerca del centro
    calor = (np.clip(1 - u, 0, 1) ** 4 * 0.45)[..., None]
    col = np.asarray(j['linea'], float) * (1 - calor) + 255.0 * calor
    sobre(capa, np.broadcast_to(col, (H2, W2, 3)), np.maximum(linea, chicos))
    sobre(capa, j['linea'], gr)
    nuc = np.asarray(j['acento'], float) * 0.45 + 255.0 * 0.55
    sobre(capa, nuc, nucleo)
    return a_imagen(capa, w, h)


def destello():
    """Un trazo de luz horizontal, 512x64, en blanco y grises: el Java lo tine
    y lo pasa por encima del rotulo."""
    w, h = 512, 64
    W2, H2 = w * SS, h * SS
    x = (np.arange(W2, dtype=float) + 0.5) / W2 * 2 - 1          # -1 .. 1
    y = (np.arange(H2, dtype=float) + 0.5 - H2 / 2) / SS          # px a 1x
    X, Y = np.meshgrid(x, y)
    vent = np.clip(1 - (Y / (h / 2)) ** 2, 0, 1) ** 2
    nucleo = np.exp(-0.5 * (Y / 1.3) ** 2) * np.clip(1 - X ** 2, 0, 1) ** 3
    medio = np.exp(-0.5 * (Y / 5.0) ** 2) * np.clip(1 - X ** 2, 0, 1) ** 2 * 0.55
    bruma = np.exp(-0.5 * (Y / 14.0) ** 2) * np.clip(1 - X ** 2, 0, 1) ** 1.4 * 0.22
    a = 1 - (1 - nucleo) * (1 - medio) * (1 - bruma)
    a *= vent
    gris = 0.84 + 0.16 * np.clip(nucleo / np.maximum(a, 1e-6), 0, 1)
    capa = np.zeros((H2, W2, 4))
    capa[..., :3] = gris[..., None]
    capa[..., 3] = a
    return a_imagen(capa, w, h, orillas=False)


# ----------------------------------------------------------------------
#  Vistas previas
# ----------------------------------------------------------------------
def fondo_cielo(w, h, semilla=1):
    """Cielo de Minecraft: degradado azul y nubes de bloques."""
    yy = np.linspace(0, 1, h)[:, None, None]
    arriba, abajo = np.array([118, 162, 238]), np.array([178, 206, 248])
    img = np.broadcast_to(arriba * (1 - yy) + abajo * yy, (h, w, 3)).copy()
    r = np.random.default_rng(semilla)
    bloque = max(8, w // 60)
    gw, gh = w // bloque + 2, h // bloque + 2
    nube = ndimage.gaussian_filter(r.random((gh, gw)), 1.6)
    nube = (nube > np.quantile(nube, 0.62)).astype(float)
    nube = np.kron(nube, np.ones((bloque, bloque)))[:h, :w]
    img = img * (1 - 0.85 * nube[..., None]) + 250 * 0.85 * nube[..., None]
    return Image.fromarray(img.astype(np.uint8)).convert('RGBA')


def fondo_cueva(w, h, semilla=2):
    """Pared de cueva oscura: bloques de 16 de pizarra profunda casi negra."""
    r = np.random.default_rng(semilla)
    bloque = max(16, w // 40)
    gw, gh = w // bloque + 2, h // bloque + 2
    base = r.uniform(14, 34, (gh, gw))
    img = np.kron(base, np.ones((bloque, bloque)))[:h, :w]
    img = img + r.normal(0, 4, (h, w))
    luz = np.exp(-((np.linspace(-1, 1, w)[None, :] - 0.4) ** 2 / 0.5 + (np.linspace(-1, 1, h)[:, None] + 0.2) ** 2 / 0.8))
    img = img * (1 + 0.8 * luz)
    rgb = np.stack([img * 0.95, img * 0.97, img * 1.08], -1)
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert('RGBA')


def montar(fondo, capas, xy=(0, 0)):
    out = fondo.copy()
    for c in capas:
        out.alpha_composite(c, xy)
    return out


def vistas(carpeta, texturas):
    os.makedirs(carpeta, exist_ok=True)
    # cada jefe a 960 sobre cielo y sobre cueva, en los dos idiomas
    w, h = 960, alto(960)
    for jefe in JEFES:
        hoja = Image.new('RGBA', (w * 2, h * 2), (0, 0, 0, 255))
        for fila, idioma in enumerate(IDIOMAS):
            capas = [texturas[f'{jefe}_{w}_linea'], texturas[f'{jefe}_{w}_nombre'],
                     texturas[f'{jefe}_{idioma}_{w}_ante'], texturas[f'{jefe}_{idioma}_{w}_epiteto']]
            hoja.paste(montar(fondo_cielo(w, h, 3 + fila), capas), (0, fila * h))
            hoja.paste(montar(fondo_cueva(w, h, 5 + fila), capas), (w, fila * h))
        hoja.convert('RGB').save(os.path.join(carpeta, f'{jefe}_960.png'))
        # y a 1:1 sobre cielo, solo la mitad izquierda, para juzgar el detalle
        capas = [texturas[f'{jefe}_{w}_linea'], texturas[f'{jefe}_{w}_nombre'],
                 texturas[f'{jefe}_es_{w}_ante'], texturas[f'{jefe}_es_{w}_epiteto']]
        montar(fondo_cielo(w, h, 3), capas).crop((120, 0, 600, h)).convert('RGB').save(
            os.path.join(carpeta, f'{jefe}_960_detalle.png'))
    # los cuatro a 720, es y en, sobre gris medio
    w, h = 720, alto(720)
    hoja = Image.new('RGBA', (w * 2, h * 4), (0, 0, 0, 255))
    for fila, jefe in enumerate(JEFES):
        for col, idioma in enumerate(IDIOMAS):
            fondo = fondo_cielo(w, h, 9 + fila) if (fila + col) % 2 == 0 else fondo_cueva(w, h, 9 + fila)
            capas = [texturas[f'{jefe}_{w}_linea'], texturas[f'{jefe}_{w}_nombre'],
                     texturas[f'{jefe}_{idioma}_{w}_ante'], texturas[f'{jefe}_{idioma}_{w}_epiteto']]
            hoja.paste(montar(fondo, capas), (col * w, fila * h))
    hoja.convert('RGB').save(os.path.join(carpeta, 'los_cuatro_720.png'))
    # los cuatro a 480 sobre capturas del juego (ventana por defecto, 854x480),
    # con las bandas de cine
    capturas = {
        'nerea': 'nerea_ronda2/nerea_fase1.png',
        'aeralis': 'aeralis_prueba4/aeralis_picado_cielo.png',
        'rajang': 'ronda3/rajang_terremoto.png',
        'novilis': 'novilis_trompetas_estrado.png',
    }
    w, h = 480, alto(480)
    hoja = Image.new('RGBA', (854 * 2, 480 * 2), (0, 0, 0, 255))
    for k, jefe in enumerate(JEFES):
        ruta = os.path.join(CAPTURAS, capturas[jefe])
        if not os.path.exists(ruta):
            ruta = sorted(glob.glob(os.path.join(CAPTURAS, '*.png')))[0]
        fondo = Image.open(ruta).convert('RGBA').resize((854, 480))
        banda = int(480 * 0.12)
        ImageDraw.Draw(fondo).rectangle((0, 0, 853, banda - 1), fill=(0, 0, 0, 255))
        ImageDraw.Draw(fondo).rectangle((0, 480 - banda, 853, 479), fill=(0, 0, 0, 255))
        capas = [texturas[f'{jefe}_{w}_linea'], texturas[f'{jefe}_{w}_nombre'],
                 texturas[f'{jefe}_es_{w}_ante'], texturas[f'{jefe}_es_{w}_epiteto']]
        hoja.paste(montar(fondo, capas, ((854 - w) // 2, (480 - h) // 2)), ((k % 2) * 854, (k // 2) * 480))
    hoja.convert('RGB').save(os.path.join(carpeta, 'juego_480.png'))
    # el destello, sobre negro y tenido
    d = texturas['destello']
    hoja = Image.new('RGBA', (512, 64 * 3), (16, 16, 20, 255))
    hoja.alpha_composite(d, (0, 0))
    for k, col in enumerate(((110, 236, 220), (255, 160, 60))):
        t = np.asarray(d, float)
        t[..., :3] *= np.asarray(col, float) / 255.0
        hoja.alpha_composite(Image.fromarray(t.astype(np.uint8), 'RGBA'), (0, 64 * (k + 1)))
    hoja.convert('RGB').save(os.path.join(carpeta, 'destello.png'))


def main():
    os.makedirs(SALIDA, exist_ok=True)
    texturas = {}
    escritos = 0

    def guardar(nombre, im):
        nonlocal escritos
        im.save(os.path.join(SALIDA, nombre + '.png'))
        texturas[nombre] = im
        escritos += 1

    for jefe, j in JEFES.items():
        for w in ANCHOS:
            im, ancho = capa_nombre(j, w)
            guardar(f'{jefe}_{w}_nombre', im)
            if w == 960:
                print(f'{jefe}: nombre de {ancho:.0f} px de tinta a 960 ({ancho / w:.3f} del ancho)')
            guardar(f'{jefe}_{w}_linea', capa_linea(j, w))
            for idioma in IDIOMAS:
                guardar(f'{jefe}_{idioma}_{w}_ante', capa_ante(j, w, idioma))
                guardar(f'{jefe}_{idioma}_{w}_epiteto', capa_epiteto(j, w, idioma))
    guardar('destello', destello())
    print(escritos, 'texturas en', SALIDA)
    if HOJA:
        vistas(HOJA, texturas)
        print('hojas en', HOJA)


main()

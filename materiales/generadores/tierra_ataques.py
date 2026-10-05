"""
Los ataques de Rajang, hechos a mano para el mod: nada de bloques de
Minecraft. Mallas facetadas con texturas propias y calcos en el suelo.

- Pico de tierra (Garra Terrestre): un cumulo de esquirlas de roca parda en
  estratos, inclinadas hacia fuera, con la roca rota y los terrones a su
  pie; una veta verde apenas asoma.
- Rocas en bloque: los terrones que saltan, cajas irregulares giradas.
- Pilares de tierra (Terremoto Ancestral): torres de roca en bloques que
  revientan el suelo, cada bloque algo torcido y la punta en esquirla.
- Totems del Sello y sus plataformas: columna de piedra verde en tres
  tramos con glifos que brillan (numeros mayas, el ojo, la espiral y la
  mascara del jaguar), encima de una plataforma de tierra alta; alrededor,
  piedras flotando en espiral para subir saltando.
- Columnas ancestrales (Terremoto Ancestral): haces de columnas de basalto
  con jade, hexagonales y cortadas en bisel, que revientan el suelo.
- Losas: placas del suelo arrancadas e inclinadas (la onda del Terremoto y
  los bordes de los crateres).
- Estela del sello (Sello de la Tierra): monolito octogonal tallado con la
  mascara del jaguar y numeros mayas; encima flota un aro de jade con su
  cristal. Encendida, la talla brilla y sube un haz.
- Fragmento de jade (Cataclismo de Jade): cristal bipiramidal que cae envuelto
  en llama verde, con su estela.
- Escombros: piedras irregulares que saltan.
- Calcos: la grieta del suelo, la marca del Cataclismo (con la cuenta atras),
  el aviso del Terremoto, el circulo del Sello, la onda de choque y el crater.

Todo en bloques de mundo (Y hacia arriba). Cada malla es una lista de
triangulos (P, UV, material).
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import vigia_render as vr
import nerea_modelo as nm

_hex = nm._hex
TAU = math.tau


# ----------------------------------------------------------------------
#  Ruido 2D para las texturas
# ----------------------------------------------------------------------
def _ruido2(w, h, celdas, semilla):
    rng = np.random.default_rng(semilla)
    gx, gy = celdas
    g = rng.random((gy + 1, gx + 1))
    g[:, -1] = g[:, 0]
    g[-1, :] = g[0, :]
    return np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(float) / 255


def _fbm2(w, h, celdas, semilla, octavas=3):
    s, a, tot = 0.0, 1.0, 0.0
    for o in range(octavas):
        s = s + a * _ruido2(w, h, (celdas[0] * 2 ** o, celdas[1] * 2 ** o), semilla + o * 13)
        tot += a
        a *= 0.5
    return s / tot


def _mezcla(R, t):
    R = np.asarray([_hex(x) if isinstance(x, str) else x for x in R], float)
    t = np.clip(t, 0, 1) * (len(R) - 1)
    i = np.minimum(np.floor(t).astype(int), len(R) - 2)
    f = (t - i)[..., None]
    return R[i] * (1 - f) + R[i + 1] * f


def _rgba(col, alfa=255):
    t = np.zeros((*col.shape[:2], 4), np.uint8)
    t[..., :3] = np.clip(col, 0, 255)
    t[..., 3] = alfa if np.isscalar(alfa) else np.clip(alfa, 0, 255)
    return t


ROCA = ('1e1a14', '2c261e', '3c3428', '4e4634', '645a44', '7a6e54')
JADE = ('0c2a1a', '154030', '1f5a40', '2c7452', '3e9066', '62b088')
GLOW = (156, 255, 122)
GLOW_BLANCO = (226, 255, 200)
TIERRA = ('2a1e14', '3a2a1c', '4c3824', '5e4830', '725a3c')
PIEDRA = ('34342a', '444436', '565644', '6a6a54', '808066')


# ----------------------------------------------------------------------
#  Texturas
# ----------------------------------------------------------------------
def _vetas(w, h, n, semilla, vertical=True, paso=1.6, largo=(10, 30)):
    """Vetas dibujadas como lineas finas que serpentean (mascara booleana)."""
    r = random.Random(semilla)
    img = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h)
        a = (math.pi / 2 if vertical else 0) + r.uniform(-0.5, 0.5)
        for k in range(r.randint(*largo)):
            a += r.uniform(-0.35, 0.35)
            x1, y1 = x + math.cos(a) * paso, y + math.sin(a) * paso
            d.line((x, y, x1, y1), fill=255, width=1)
            x, y = x1, y1
            if r.random() < 0.06:
                a += r.choice([-1, 1]) * 0.9
    return np.array(img) > 0


def _tex_pico(w=32, h=96, s=1):
    """La esquirla, cara por cara (u de canto a canto, v de la base a la
    punta): jade que se aclara y se enciende hacia la punta, la tierra que se
    le queda pegada abajo, los cantos brillantes y grietas por dentro."""
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    u = np.ones((h, 1)) * np.linspace(0, 1, w)[None]
    n1 = _fbm2(w, h, (2, 6), s)
    n2 = _fbm2(w, h, (5, 15), s + 5)
    col = _mezcla(JADE, 0.12 + 0.7 * v + 0.22 * (n2 - 0.5))
    col *= (0.88 + 0.22 * (0.5 + 0.5 * np.sin(u * TAU * 1.5 + n1 * 5)))[..., None]
    em = np.zeros((h, w, 4))
    em[..., :3] = GLOW
    em[..., 3] = 12 + 150 * v ** 2.2
    grietas = _vetas(w, h, 5, s + 9) & (v > 0.3)
    col[grietas] = col[grietas] * 0.45 + np.array(GLOW) * 0.4
    em[grietas] = (*GLOW_BLANCO, 200)
    canto = (u < 0.06) | (u > 0.94)
    col[canto] = col[canto] * 0.5 + np.array(GLOW_BLANCO) * 0.35
    em[canto, 3] = np.maximum(em[canto, 3], 60 + 140 * v[canto])
    tierra = v < 0.1 + 0.14 * n1
    col[tierra] = _mezcla(TIERRA, 0.3 + 0.6 * n2[tierra])
    em[tierra, 3] = 0
    punta = v > 0.9
    em[punta] = (*GLOW_BLANCO, 230)
    return _rgba(col), _premul(em)


def _premul(em):
    k = em[..., 3:4] / 255.0
    out = np.zeros(em.shape, np.uint8)
    out[..., :3] = np.clip(em[..., :3] * k, 0, 255)
    out[..., 3] = np.where(em[..., 3] > 0, 255, 0)
    return out


def _tex_basalto(w=32, h=64, s=2):
    """El costado de una columna: piedra verde negruzca, juntas horizontales
    y vetas de jade que suben y brillan."""
    n1 = _fbm2(w, h, (3, 6), s)
    n2 = _fbm2(w, h, (6, 12), s + 3)
    x = np.ones((h, 1)) * np.arange(w)[None]
    y = np.arange(h)[:, None] * np.ones((1, w))
    col = _mezcla(('121812', '1a221a', '243024', '304030', '3e523e'), 0.45 + 0.45 * (n2 - 0.5) + 0.2 * (n1 - 0.5))
    junta = np.abs(np.mod(y + n1 * 5, 24) - 12) > 11.3
    col[junta] *= 0.35
    canto = (x < 1) | (x > w - 2)
    col[canto] = col[canto] * 0.7 + 22
    vena = _vetas(w, h, 2, s + 7, paso=1.4, largo=(8, 22))
    col[vena] = _mezcla(JADE, np.full(vena.sum(), 0.8))
    em = np.zeros((h, w, 4))
    em[vena] = (*GLOW, 110)
    return _rgba(col), _premul(em)


def _tex_tapa(n=48, s=4):
    """La cara de arriba de la columna, recien partida: grietas que brillan."""
    n1 = _fbm2(n, n, (4, 4), s)
    col = _mezcla(('1a201a', '263026', '344034', '445244'), 0.5 + 0.6 * (n1 - 0.5))
    yy, xx = np.mgrid[0:n, 0:n]
    em = np.zeros((n, n, 4))
    r = random.Random(s)
    img = Image.new('L', (n, n), 0)
    d = ImageDraw.Draw(img)
    for _ in range(4):
        a = r.uniform(0, TAU)
        x0, y0 = n / 2, n / 2
        for k in range(6):
            a += r.uniform(-0.6, 0.6)
            x1, y1 = x0 + math.cos(a) * n * 0.1, y0 + math.sin(a) * n * 0.1
            d.line((x0, y0, x1, y1), fill=255, width=1)
            x0, y0 = x1, y1
    m = np.array(img) > 0
    col[m] = col[m] * 0.3 + np.array(GLOW) * 0.4
    em[m] = (*GLOW, 200)
    return _rgba(col), _premul(em)


def _tex_losa(n=32, s=6):
    """Losa del templo arrancada: piedra con un canto tallado y musgo."""
    n1 = _fbm2(n, n, (3, 3), s)
    n2 = _fbm2(n, n, (8, 8), s + 1)
    col = _mezcla(PIEDRA, 0.5 + 0.5 * (n2 - 0.5) + 0.2 * (n1 - 0.5))
    yy, xx = np.mgrid[0:n, 0:n]
    talla = (np.abs(xx - n / 2) + np.abs(yy - n / 2)).astype(int) % 9 == 0
    col[talla] *= 0.6
    musgo = n1 > 0.62
    col[musgo] = _mezcla(('2c4a1c', '3a5e22', '4c742a'), n2[musgo])
    return _rgba(col), None


def _tex_tierra(n=32, s=7):
    n1 = _fbm2(n, n, (4, 4), s)
    n2 = _fbm2(n, n, (10, 10), s + 2)
    col = _mezcla(TIERRA, 0.5 + 0.6 * (n2 - 0.5) + 0.2 * (n1 - 0.5))
    piedra = n2 > 0.7
    col[piedra] = _mezcla(ROCA, n1[piedra])
    return _rgba(col), None


def _tex_roca(n=32, s=8):
    n1 = _fbm2(n, n, (4, 4), s)
    col = _mezcla(ROCA, 0.4 + 0.6 * (n1 - 0.5) + 0.2 * _fbm2(n, n, (12, 12), s + 1))
    return _rgba(col), None


def _tex_fragmento(n=32, s=9):
    """Jade de la maldicion, encendido por dentro: facetas y brillo."""
    yy, xx = np.mgrid[0:n, 0:n]
    n1 = _fbm2(n, n, (3, 3), s)
    col = _mezcla(('1c6a3c', '2e8a50', '4cae6a', '7ad08e', 'b8f0c0'), 0.4 + 0.6 * (n1 - 0.5) + 0.3 * (yy / n))
    faceta = np.abs(np.mod(xx * 0.7 + yy * 0.4, 9) - 4.5) < 0.6
    col[faceta] = col[faceta] * 0.6 + np.array(GLOW_BLANCO) * 0.4
    em = np.zeros((n, n, 4))
    em[..., :3] = GLOW
    em[..., 3] = 90 + 80 * (yy / n)
    em[faceta] = (*GLOW_BLANCO, 230)
    return _rgba(col), _premul(em)


def _jaguar_glifo(w, h):
    """La mascara del jaguar tallada (mascara booleana de w x h)."""
    m = np.zeros((h, w), bool)
    sx, sy = w / 28.0, h / 30.0
    yy, xx = np.mgrid[0:h, 0:w]
    X, Y = xx / sx, yy / sy

    def caja(x0, y0, x1, y1, hueca=True, g=1.6):
        dentro = (X >= x0) & (X < x1) & (Y >= y0) & (Y < y1)
        if not hueca:
            return dentro
        return dentro & ~((X >= x0 + g) & (X < x1 - g) & (Y >= y0 + g) & (Y < y1 - g))
    m |= caja(3, 6, 25, 29)                                   # la cabeza
    m |= caja(3, 1, 9, 8) | caja(19, 1, 25, 8)                # las orejas
    m |= caja(7, 11, 12, 14, False) & (Y - 11 < (X - 7) * 0.6 + 2)     # ojos rasgados
    m |= caja(16, 11, 21, 14, False) & (Y - 11 < (21 - X) * 0.6 + 2)
    m |= (np.abs(X - 14) <= (20 - Y) / 1.4) & (Y >= 15) & (Y < 20)      # la nariz
    m |= caja(7, 21, 21, 22.6, False)                         # la boca
    m |= caja(9, 21, 11, 27.5, False) | caja(17, 21, 19, 27.5, False)   # los sables
    for cx, cy in ((6, 18), (22, 18), (6.5, 24), (21.5, 24)):  # rosetas de las mejillas
        m |= (np.hypot(X - cx, Y - cy) < 1.2)
    return m


def _greca_banda(w, h):
    yy, xx = np.mgrid[0:h, 0:w]
    periodo = 2 * h
    tri = h - np.abs(np.mod(xx, periodo) - h)
    arriba = yy < np.floor(tri / 2) * 2 - 1
    tri2 = h - np.abs(np.mod(xx + h, periodo) - h)
    abajo = yy >= h - np.floor(tri2 / 2) * 2 + 1
    return arriba | abajo


def _numero_maya(w, h, valor):
    """Puntos y barras (un 5 es una barra)."""
    m = np.zeros((h, w), bool)
    barras, puntos = valor // 5, valor % 5
    y = h - 3
    for _ in range(barras):
        m[y - 2:y, 2:w - 2] = True
        y -= 4
    if puntos:
        paso = (w - 4) / puntos
        for k in range(puntos):
            cx = int(2 + paso * (k + 0.5))
            m[y - 2:y, cx - 1:cx + 1] = True
    return m


def _tex_estela(cara=True, w=32, h=112, s=11):
    """El costado de la estela. La de delante lleva la mascara del jaguar, la
    greca y tres numeros mayas; las otras, solo greca y numeros. Lo tallado
    va hundido (oscuro con el canto de abajo claro) y es lo que se enciende."""
    n1 = _fbm2(w, h, (3, 10), s)
    n2 = _fbm2(w, h, (8, 28), s + 1)
    col = _mezcla(('2a3026', '3a4234', '4c5644', '5e6a54', '76846a'), 0.5 + 0.5 * (n2 - 0.5) + 0.2 * (n1 - 0.5))
    talla = np.zeros((h, w), bool)
    talla[1:3, :] = True
    talla[h - 3:h - 1, :] = True
    talla[:, 1:3] = True
    talla[:, w - 3:w - 1] = True
    y0 = 6
    if cara:
        talla[y0:y0 + 30, 2:30] |= _jaguar_glifo(28, 30)
        y0 += 34
    talla[y0:y0 + 8, 4:w - 4] |= _greca_banda(w - 8, 8)
    y0 += 12
    for val in ((13, 7, 9) if cara else (4, 11, 6, 18)):
        if y0 + 14 > h - 4:
            break
        talla[y0:y0 + 14, 6:w - 6] |= _numero_maya(w - 12, 14, val)
        y0 += 17
    col[talla] *= 0.42
    bajo = np.roll(talla, 1, axis=0) & ~talla
    col[bajo] = col[bajo] * 1.25 + 10
    musgo = (n1 > 0.64) & (np.arange(h)[:, None] > h * 0.6)
    col[musgo & ~talla] = _mezcla(('2c4a1c', '3a5e22', '4c742a'), n2[musgo & ~talla])
    em = np.zeros((h, w, 4))
    em[talla] = (*GLOW, 230)
    return _rgba(col), _premul(em), talla


def _tex_oro(w=32, h=8, s=12):
    n1 = _fbm2(w, h, (8, 2), s)
    col = _mezcla(('5e400e', '8f6418', 'c28d28', 'e2b443', 'f8d97c'), 0.55 + 0.4 * (n1 - 0.5))
    g = _greca_banda(w, h - 2)
    col[1:h - 1][g] *= 0.6
    col[0] = col[0] * 1.15
    col[h - 1] *= 0.6
    return _rgba(col), None


def _tex_aro(n=32, s=13):
    n1 = _fbm2(n, n, (4, 4), s)
    col = _mezcla(JADE, 0.45 + 0.6 * (n1 - 0.5))
    return _rgba(col), None


def _tex_halo(n=64, color=GLOW, nucleo=GLOW_BLANCO, duro=2.2):
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    a = np.clip(1 - d, 0, 1) ** duro
    k = np.clip(1 - d * 3, 0, 1)[..., None]
    col = np.array(color) * (1 - k) + np.array(nucleo) * k
    return _rgba(col, a * 255)


def _tex_llama(w=32, h=128, s=14):
    """La estela del fragmento: cabeza blanca, cuerpo verde, cola que se
    deshilacha (v=0 en la cabeza)."""
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    u = np.ones((h, 1)) * np.linspace(-1, 1, w)[None]
    n1 = _fbm2(w, h, (3, 10), s)
    ancho = (1 - v) ** 0.6 * (0.75 + 0.5 * (n1 - 0.5))
    a = np.clip(1 - np.abs(u) / np.maximum(ancho, 1e-3), 0, 1) ** 1.3 * (1 - v) ** 1.2
    k = np.clip(1 - v * 4, 0, 1)[..., None]
    col = np.array([90, 230, 110]) * (1 - k) + np.array(GLOW_BLANCO) * k
    return _rgba(col, a * 255)


def _tex_haz(w=32, h=64):
    v = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    u = np.ones((h, 1)) * np.linspace(-1, 1, w)[None]
    a = np.clip(1 - np.abs(u), 0, 1) ** 2 * np.clip(1 - v, 0, 1) ** 0.8
    return _rgba(np.ones((h, w, 3)) * np.array(GLOW), a * 200)


# --- calcos del suelo
def _lienzo_calco(n):
    return Image.new('RGBA', (n, n), (0, 0, 0, 0))


def _tex_marca_cataclismo(n=256, cuenta=0.65, color=GLOW):
    """Donde va a caer un fragmento: aro doble con dientes escalonados, la
    cuenta atras (arco que se va cerrando) y el rombo de jade en el centro."""
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = xx + 0.5 - n / 2, yy + 0.5 - n / 2
    d = np.hypot(dx, dy) / (n / 2)
    ang = (np.arctan2(dx, -dy) / TAU) % 1.0
    a = np.zeros((n, n))
    a[(d > 0.92) & (d < 0.98)] = 0.95
    a[(d > 0.78) & (d < 0.81)] = 0.7
    dientes = (np.floor(ang * 24) % 2 == 0) & (d > 0.83) & (d < 0.9 - 0.03 * (np.floor(ang * 48) % 2))
    a[dientes] = 0.55
    arco = (d > 0.62) & (d < 0.72) & (ang < cuenta)
    a[arco] = 0.85
    rombo = (np.abs(dx) + np.abs(dy)) / (n / 2)
    a[(rombo > 0.26) & (rombo < 0.32)] = 0.9
    a[rombo < 0.14] = 0.75
    a += np.clip(1 - d, 0, 1) ** 2 * 0.2
    return _rgba(np.ones((n, n, 3)) * np.array(color), np.clip(a, 0, 1) * 255)


def _tex_aviso(n=128, color=GLOW, semilla=3):
    """Donde va a reventar una columna: el hexagono y la estrella de grietas."""
    img = _lienzo_calco(n)
    d = ImageDraw.Draw(img)
    c = n / 2
    pts = [(c + math.cos(TAU * k / 6) * n * 0.44, c + math.sin(TAU * k / 6) * n * 0.44) for k in range(7)]
    d.line(pts, fill=(*color, 220), width=max(2, n // 40))
    r = random.Random(semilla)
    for k in range(7):
        a = TAU * k / 7 + r.uniform(-0.2, 0.2)
        x0, y0 = c, c
        for s in range(5):
            a += r.uniform(-0.5, 0.5)
            x1, y1 = x0 + math.cos(a) * n * 0.08, y0 + math.sin(a) * n * 0.08
            d.line((x0, y0, x1, y1), fill=(*color, 255 - s * 30), width=max(1, n // 60))
            x0, y0 = x1, y1
    return np.array(img.filter(ImageFilter.GaussianBlur(0.6)))


def _tex_sello(n=512, color=(120, 255, 140), cuenta=0.4):
    """El circulo del Sello: aro con greca, cuatro nodos (los totems), las
    lineas que los unen al centro y la mascara del jaguar en medio. El arco de
    fuera es el tiempo que queda."""
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = xx + 0.5 - n / 2, yy + 0.5 - n / 2
    d = np.hypot(dx, dy) / (n / 2)
    ang = (np.arctan2(dx, -dy) / TAU) % 1.0
    a = np.zeros((n, n))
    a[(d > 0.95) & (d < 0.985)] = 0.9
    a[(d > 0.97) & (d < 1.0) & (ang < cuenta)] = 1.0
    banda = (d > 0.84) & (d < 0.92)
    hb = 12
    gx = (ang * TAU * n * 0.44).astype(int)
    gy = ((d - 0.84) / 0.08 * hb).astype(int)
    a[banda & _greca_banda(int(TAU * n * 0.44) + 2 * hb, hb)[np.clip(gy, 0, hb - 1), np.clip(gx, 0, int(TAU * n * 0.44) + 2 * hb - 1)]] = 0.7
    a[(d > 0.82) & (d < 0.84)] = 0.8
    for k in range(4):
        th = TAU * k / 4 + TAU / 8
        cx, cy = math.sin(th) * 0.72 * n / 2, -math.cos(th) * 0.72 * n / 2
        dn = np.hypot(dx - cx, dy - cy) / (n / 2)
        a[(dn > 0.075) & (dn < 0.095)] = 0.95
        a[dn < 0.04] = 0.8
        # la linea hasta el centro
        t = np.clip((dx * cx + dy * cy) / (cx * cx + cy * cy), 0, 1)
        dl = np.hypot(dx - t * cx, dy - t * cy) / (n / 2)
        a[(dl < 0.008) & (t > 0.32) & (t < 0.86)] = 0.6
    g = _jaguar_glifo(int(n * 0.26), int(n * 0.28))
    oy, ox = int(n / 2 - n * 0.14), int(n / 2 - n * 0.13)
    a[oy:oy + g.shape[0], ox:ox + g.shape[1]][g] = 0.95
    a[(d > 0.3) & (d < 0.32)] = 0.75
    a += np.clip(1 - d, 0, 1) ** 3 * 0.15
    return _rgba(np.ones((n, n, 3)) * np.array(color), np.clip(a, 0, 1) * 255)


def _tex_onda(n=256, color=(200, 255, 170)):
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot(xx + 0.5 - n / 2, yy + 0.5 - n / 2) / (n / 2)
    a = np.exp(-((d - 0.93) / 0.04) ** 2) + 0.35 * np.exp(-((d - 0.82) / 0.06) ** 2)
    return _rgba(np.ones((n, n, 3)) * np.array(color), np.clip(a, 0, 1) * 220)


def _tex_grieta(w=64, h=512, semilla=5, ancho=3.0):
    """Grieta larga en el suelo (v a lo largo). Devuelve (oscura, brillo): la
    oscura se pinta opaca (los bordes rotos y el fondo negro) y el brillo,
    sumado."""
    r = random.Random(semilla)
    xs = []
    x = w / 2
    for y in range(h):
        x += r.uniform(-1.0, 1.0)
        x += (w / 2 - x) * 0.04
        xs.append(x)
    yy, xx = np.mgrid[0:h, 0:w]
    centro = np.array(xs)[:, None]
    an = ancho * (0.6 + 0.8 * _ruido2(w, h, (2, 16), semilla)) * (1 - 0.6 * np.abs(yy / h - 0.5) * 2)
    dist = np.abs(xx - centro)
    oscura = np.zeros((h, w, 4), np.uint8)
    hueco = dist < an
    labio = (dist < an + 2.2) & ~hueco
    oscura[hueco] = (8, 12, 8, 255)
    oscura[labio] = (40, 34, 24, 255)
    # ramitas
    img = Image.fromarray(oscura)
    d = ImageDraw.Draw(img)
    for _ in range(14):
        y0 = r.uniform(0.1, 0.9) * h
        x0 = xs[int(y0)]
        a = r.choice([-1, 1]) * r.uniform(0.4, 1.2)
        for s in range(4):
            x1, y1 = x0 + math.sin(a) * 9, y0 + math.cos(a) * 9 * r.choice([-1, 1])
            d.line((x0, y0, x1, y1), fill=(10, 14, 10, 255), width=2)
            x0, y0 = x1, y1
            a += r.uniform(-0.5, 0.5)
    oscura = np.array(img)
    brillo = np.zeros((h, w, 4))
    brillo[..., :3] = GLOW
    brillo[..., 3] = np.clip(1 - dist / (an + 0.01), 0, 1) ** 0.7 * 255 + np.clip(1 - dist / (an + 9), 0, 1) ** 2 * 80
    return oscura, _rgba(brillo[..., :3], np.clip(brillo[..., 3], 0, 255))


def _tex_crater(n=128, semilla=6):
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = xx + 0.5 - n / 2, yy + 0.5 - n / 2
    ang = np.arctan2(dy, dx)
    d = np.hypot(dx, dy) / (n / 2)
    borde = 0.85 + 0.12 * np.sin(ang * 5 + semilla) * np.cos(ang * 3)
    t = np.zeros((n, n, 4), np.uint8)
    dentro = d < borde
    k = (d / borde)[dentro]
    col = _mezcla(('0a0c08', '1a1810', '2c261a', '4a3e2a'), k)
    t[dentro] = np.c_[np.clip(col, 0, 255), np.full(dentro.sum(), 255)].astype(np.uint8)
    return t


def _teselas(w, h, T, semilla, var=0.16):
    """Tono por tesela de T texeles y su bisel (para que la piedra parezca
    tallada en bloques). Devuelve (tono -0.5..0.5, factor de bisel)."""
    rng = np.random.default_rng(semilla)
    yy, xx = np.mgrid[0:h, 0:w]
    tu, tv = xx // T, yy // T
    tabla = rng.random((h // T + 2, w // T + 2))
    tono = (tabla[tv, tu] - 0.5) * var * 2
    lu, lv = xx - tu * T, yy - tv * T
    k = np.ones((h, w))
    k[lv == 0] *= 1.15
    k[(lu == 0) & (lv > 0)] *= 1.07
    k[lv == T - 1] *= 0.75
    k[(lu == T - 1) & (lv < T - 1)] *= 0.86
    return tono, k


def _tex_estrato(w=32, h=64, s=21):
    """Roca de tierra (los picos, los pilares, las plataformas): capas que
    ondulan y cambian de grosor, tierra y piedra gris mezcladas, guijarros,
    grietas oscuras sueltas, bisel suave por bloques y alguna veta verde."""
    yy, xx = np.mgrid[0:h, 0:w]
    n1 = _fbm2(w, h, (3, 6), s)
    n2 = _fbm2(w, h, (5, 10), s + 2)
    n3 = _fbm2(w, h, (10, 20), s + 4)
    pos = yy + n1 * 12 + 3 * np.sin(xx * 0.22 + s)
    capa = np.floor(pos / (5 + 5 * n2))
    tono_capa = np.abs(np.modf(np.sin(capa * 12.9898 + s) * 43758.5)[0])
    tono, k = _teselas(w, h, 4, s + 1, 0.06)
    col = _mezcla(('2a2218', '3c3226', '524536', '695a46', '80725a', '978a70'),
                  0.48 + 0.28 * (tono_capa - 0.5) + 0.3 * (n3 - 0.5) + tono)
    col *= (0.93 + 0.07 * (k - 1) * 3)[..., None]
    guijarro = n3 > 0.7
    col[guijarro] = _mezcla(('5a564c', '726d62', '8c877a'), (n2[guijarro] - 0.2) * 1.5)
    grieta = _vetas(w, h, 3, s + 5, paso=1.3, largo=(5, 12))
    col[grieta] *= 0.45
    vena = _vetas(w, h, 1, s + 3, paso=1.4, largo=(6, 14))
    col[vena] = col[vena] * 0.4 + np.array(GLOW) * 0.35
    em = np.zeros((h, w, 4))
    em[vena] = (*GLOW, 110)
    return _rgba(col), _premul(em)


def _tex_cesped(n=32, s=23):
    """La cara de arriba de las plataformas y las piedras flotantes: hierba y
    musgo de selva."""
    tono, k = _teselas(n, n, 4, s, 0.1)
    n1 = _fbm2(n, n, (4, 4), s + 1)
    col = _mezcla(('1e3a14', '2a4e1a', '386424', '4a7a2e', '5e9038'), 0.5 + tono + 0.4 * (n1 - 0.5)) * k[..., None]
    tierra = n1 < 0.32
    col[tierra] = _mezcla(TIERRA, 0.5 + tono[tierra])
    return _rgba(col), None


def _glifo(cual, w, h):
    """Glifos de los totems: 0 numero maya, 1 el ojo, 2 la espiral, 3 el jaguar."""
    if cual == 0:
        return _numero_maya(w, h, 13)
    if cual == 3:
        return _jaguar_glifo(w, h)
    m = np.zeros((h, w), bool)
    yy, xx = np.mgrid[0:h, 0:w]
    if cual == 1:
        cx, cy = (w - 1) / 2, (h - 1) / 2
        d = np.maximum(np.abs(xx - cx), np.abs(yy - cy) * w / h)
        m |= (d > w * 0.38) & (d < w * 0.48)
        m |= (d > w * 0.16) & (d < w * 0.26)
        m |= d < w * 0.07
        return m
    # la espiral cuadrada
    x, y, k = 1, h - 2, 0
    largos = [h - 3, w - 3, h - 3]
    while True:
        k += 1
        largos += [w - 3 - 3 * k, h - 3 - 3 * k]
        if largos[-1] <= 0 or largos[-2] <= 0:
            break
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    for i, L in enumerate(largos):
        if L <= 0:
            break
        dx, dy = dirs[i % 4]
        for t in range(L + 1):
            if 0 <= y + dy * t < h and 0 <= x + dx * t < w:
                m[y + dy * t, x + dx * t] = True
        x, y = x + dx * L, y + dy * L
    return m


def _tex_totem(cual, estado, w=24, h=40, s=31):
    """Un tramo del totem: piedra verde oscura en bloques, marco tallado y el
    glifo en medio. estado: 'on' (brilla), 'off' o 'roto' (rajado y apagado)."""
    tono, k = _teselas(w, h, 4, s + cual, 0.1)
    n1 = _fbm2(w, h, (3, 5), s + 7)
    col = _mezcla(('0e1a12', '16261a', '1e3424', '28442e', '345838'), 0.5 + tono + 0.3 * (n1 - 0.5)) * k[..., None]
    marco = np.zeros((h, w), bool)
    marco[1, 1:w - 1] = marco[h - 2, 1:w - 1] = True
    marco[1:h - 1, 1] = marco[1:h - 1, w - 2] = True
    g = np.zeros((h, w), bool)
    gw, gh = w - 8, h - 10
    g[5:5 + gh, 4:4 + gw] = _glifo(cual, gw, gh)
    talla = marco | g
    col[talla] *= 0.45
    em = np.zeros((h, w, 4))
    if estado == 'on':
        col[talla] = col[talla] * 0.4 + np.array(GLOW) * 0.55
        em[talla] = (*GLOW, 235)
        em[marco] = (*GLOW, 150)
    if estado == 'roto':
        r = random.Random(s + cual)
        img = Image.new('L', (w, h), 0)
        d = ImageDraw.Draw(img)
        for _ in range(4):
            x0, y0 = r.uniform(0, w), r.uniform(0, h)
            for _ in range(6):
                x1, y1 = x0 + r.uniform(-4, 4), y0 + r.uniform(2, 6)
                d.line((x0, y0, x1, y1), fill=255)
                x0, y0 = x1, y1
        col[np.array(img) > 0] *= 0.25
    return _rgba(col), (_premul(em) if estado == 'on' else None)


_TEX = {}


def tex(nombre):
    if nombre not in _TEX and nombre.startswith('totem_'):
        _, cual, estado = nombre.split('_')
        _TEX[nombre] = _tex_totem(int(cual), estado)
    if nombre not in _TEX:
        f = {
            'pico': _tex_pico, 'basalto': _tex_basalto, 'tapa': _tex_tapa, 'losa': _tex_losa, 'tierra_c': _tex_tierra,
            'roca': _tex_roca, 'fragmento': _tex_fragmento, 'oro_b': _tex_oro, 'aro': _tex_aro,
            'estrato': _tex_estrato, 'cesped': _tex_cesped, 'tapa_totem': lambda: (_tex_totem(1, 'off')[0], None),
            'estela_cara': lambda: (_tex_estela(True)[0], None), 'estela_lisa': lambda: (_tex_estela(False)[0], None),
            'estela_cara_on': lambda: _tex_estela(True)[:2], 'estela_lisa_on': lambda: _tex_estela(False)[:2],
        }[nombre]
        _TEX[nombre] = f()
    return _TEX[nombre]


# ----------------------------------------------------------------------
#  Mallas
# ----------------------------------------------------------------------
def _tri(a, b, c, ua, ub, uc, mat):
    return (np.array([a, b, c], float), [ua, ub, uc], mat)


def _cuad(a, b, c, d, uva, uvb, uvc, uvd, mat):
    return [_tri(a, b, c, uva, uvb, uvc, mat), _tri(a, c, d, uva, uvc, uvd, mat)]


def pico(x, z, alto, radio, inclina=(0.0, 0.0), semilla=0, lados=6, extras=True, mat='estrato'):
    """Esquirla de jade que revienta el suelo: prisma irregular con su punta
    piramidal, inclinado; a su pie, cristales menores y la roca rota."""
    r = random.Random(semilla)
    e = np.array([inclina[0], 1.0, inclina[1]])
    e /= np.linalg.norm(e)
    a = np.cross(e, [0.0, 0.0, 1.0]); a /= np.linalg.norm(a)
    b = np.cross(e, a)
    largo = alto / e[1]
    base = np.array([x, 0.0, z])
    giro = r.uniform(0, TAU)
    def anillo(t, k):
        out = []
        for i_ in range(lados):
            ang = giro + (i_ + r.uniform(-0.2, 0.2)) / lados * TAU
            rr = radio * k * r.uniform(0.85, 1.12)
            out.append(base + e * largo * t + (a * math.cos(ang) + b * math.sin(ang)) * rr)
        return out
    A, B = anillo(-0.15, 1.0), anillo(r.uniform(0.6, 0.72), r.uniform(0.75, 0.9))
    apice = base + e * largo + (a * r.uniform(-0.12, 0.12) + b * r.uniform(-0.12, 0.12)) * radio
    tb = 0.66
    out = []
    for i_ in range(lados):
        j_ = (i_ + 1) % lados
        alto_uv = largo / 2.0
        out += _cuad(A[i_], A[j_], B[j_], B[i_], (0, 0), (1, 0), (1, tb * alto_uv), (0, tb * alto_uv), mat)
        out.append(_tri(B[i_], B[j_], apice, (0, tb * alto_uv), (1, tb * alto_uv), (0.5, alto_uv), mat))
    if extras:
        # las esquirlas menores, abiertas hacia fuera como en una flor de roca
        for k in range(r.randint(3, 5)):
            ang = r.uniform(0, TAU)
            d = radio * r.uniform(0.7, 1.2)
            out += pico(x + math.cos(ang) * d, z + math.sin(ang) * d, alto * r.uniform(0.35, 0.7), radio * r.uniform(0.4, 0.6),
                        (math.cos(ang) * r.uniform(0.3, 0.6), math.sin(ang) * r.uniform(0.3, 0.6)), semilla * 7 + k + 1, 5, False, mat)
        # la roca rota y los terrones al pie
        for k in range(r.randint(5, 8)):
            ang = TAU * k / 6 + r.uniform(-0.3, 0.3)
            d = radio * r.uniform(1.1, 1.9)
            out += roca_cubica(x + math.cos(ang) * d, 0.12, z + math.sin(ang) * d, radio * r.uniform(0.28, 0.5), semilla * 13 + k)
    return out


def roca_cubica(x, y, z, tam, semilla=0, mat='estrato', aplanar=1.0, giro=None):
    """Una roca en bloque: caja irregular, girada al azar."""
    r = random.Random(semilla)
    hx, hy, hz = tam * r.uniform(0.75, 1.2), tam * r.uniform(0.6, 1.0) * aplanar, tam * r.uniform(0.75, 1.2)
    g = giro if giro is not None else (r.uniform(-40, 40), r.uniform(0, 360), r.uniform(-40, 40))
    R = (vr.Ry(g[1] * vr.D2R) @ vr.Rx(g[0] * vr.D2R) @ vr.Rz(g[2] * vr.D2R))[:3, :3]
    v = []
    for i in range(8):
        sx, sy, sz = (1 if i & 1 else -1), (1 if i & 2 else -1), (1 if i & 4 else -1)
        q = np.array([sx * hx * r.uniform(0.85, 1.1), sy * hy * r.uniform(0.85, 1.1), sz * hz * r.uniform(0.85, 1.1)])
        v.append(np.array([x, y, z]) + R @ q)
    caras = [(0, 4, 6, 2), (1, 3, 7, 5), (0, 1, 5, 4), (2, 6, 7, 3), (0, 2, 3, 1), (4, 5, 7, 6)]
    out = []
    for a_, b_, c_, d_ in caras:
        out += _cuad(v[a_], v[b_], v[c_], v[d_], (0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5), mat)
    return out


def pilar_tierra(x, z, alto, ancho, semilla=0):
    """Pilar de roca en bloques que revienta el suelo: cada bloque un poco
    torcido y mas estrecho, la punta en esquirla."""
    r = random.Random(semilla)
    out = []
    y = -0.4
    i = 0
    while y < alto - ancho * 0.6:
        w = ancho * (1 - 0.1 * i) * r.uniform(0.92, 1.05)
        h = w * r.uniform(0.7, 1.0)
        cx, cz = x + r.uniform(-0.12, 0.12) * ancho, z + r.uniform(-0.12, 0.12) * ancho
        out += roca_cubica(cx, y + h / 2, cz, w / 2, semilla * 17 + i, 'estrato', 1.0,
                           (r.uniform(-7, 7), r.uniform(0, 90), r.uniform(-7, 7)))
        y += h * 0.9
        i += 1
    tope = pico(0, 0, ancho * 1.2, ancho * 0.36, (r.uniform(-0.2, 0.2), r.uniform(-0.2, 0.2)), semilla + 5, 5, False)
    out += [(P + np.array([x, y - 0.2, z]), UV, m) for P, UV, m in tope]
    return out


def plataforma(x, z, alto, ancho, semilla=0):
    """La plataforma de tierra del totem: una mesa de roca arrancada del suelo,
    irregular, que se ensancha hacia arriba, con la hierba encima, terrones
    clavados en los costados y escombro al pie."""
    r = random.Random(semilla)
    n = 9
    giro = r.uniform(0, TAU)
    anillos = []
    for t, k in ((-0.06, 0.64), (0.3, 0.72), (0.62, 0.86), (0.9, 1.0), (1.0, 0.97)):
        anillo = []
        for i in range(n):
            a = giro + TAU * (i + r.uniform(-0.2, 0.2)) / n
            rr = ancho / 2 * k * r.uniform(0.86, 1.08)
            anillo.append((x + math.cos(a) * rr, alto * t, z + math.sin(a) * rr))
        anillos.append(anillo)
    out = []
    for A, B in zip(anillos[:-2], anillos[1:-1]):
        out += prisma(A, B, 'estrato', 'cesped', uv_alto=2.0, tapa=False)
    out += prisma(anillos[-2], anillos[-1], 'tierra_c', 'cesped', uv_alto=1.0)
    for k in range(7):
        a = r.uniform(0, TAU)
        out += roca_cubica(x + math.cos(a) * ancho * r.uniform(0.45, 0.75), 0.2, z + math.sin(a) * ancho * r.uniform(0.45, 0.75),
                           r.uniform(0.3, 0.6), semilla * 23 + k)
    for k in range(4):
        a = r.uniform(0, TAU)
        y = alto * r.uniform(0.3, 0.8)
        out += roca_cubica(x + math.cos(a) * ancho * 0.42, y, z + math.sin(a) * ancho * 0.42, r.uniform(0.3, 0.5), semilla * 31 + k)
    return out


def piedra_flotante(x, y, z, tam, semilla=0):
    """Un escalon: piedra plana arrancada que flota, con su hierba encima y
    terrones colgando debajo."""
    r = random.Random(semilla)
    n = r.randint(5, 7)
    arriba, abajo = [], []
    for k in range(n):
        a = TAU * (k + r.uniform(-0.2, 0.2)) / n
        rr = tam * r.uniform(0.75, 1.0)
        arriba.append((x + math.cos(a) * rr, y, z + math.sin(a) * rr))
        abajo.append((x + math.cos(a) * rr * 0.7, y - tam * 0.55, z + math.sin(a) * rr * 0.7))
    out = prisma(abajo, arriba, 'estrato', 'cesped', uv_alto=1.0, cerrado_abajo=True)
    for k in range(3):
        out += roca_cubica(x + r.uniform(-0.4, 0.4) * tam, y - tam * r.uniform(0.8, 1.4), z + r.uniform(-0.4, 0.4) * tam,
                           tam * r.uniform(0.15, 0.25), semilla * 29 + k)
    return out


def totem(x, y, z, estado='on', ancho=1.5, giro=0.0, semilla=0, roto=False):
    """El totem del Sello: base, tres tramos con glifos (cada cara el suyo) y
    el remate. 'roto': partido, el tramo de arriba en el suelo."""
    r = random.Random(semilla)
    out = []
    g = giro * vr.D2R

    def cuadrado(cx, cy, cz, w):
        return [(cx + math.cos(g + TAU * k / 4 + TAU / 8) * w * 0.7071, cy, cz + math.sin(g + TAU * k / 4 + TAU / 8) * w * 0.7071)
                for k in range(4)]
    out += prisma(cuadrado(x, y, z, ancho * 1.35), cuadrado(x, y + 0.45, z, ancho * 1.35), 'totem_0_off', 'tapa_totem', uv_alto=0.45)
    alto_tramo = 1.3
    tramos = 2 if roto else 3
    yy = y + 0.45
    for t in range(tramos):
        w = ancho * (1.0 - 0.05 * t)
        base, techo = cuadrado(x, yy, z, w), cuadrado(x, yy + alto_tramo, z, w)
        for k in range(4):
            j = (k + 1) % 4
            mat = f'totem_{(k + t) % 4}_{"roto" if roto else estado}'
            out += _cuad(base[k], base[j], techo[j], techo[k], (0, 1), (1, 1), (1, 0), (0, 0), mat)
        yy += alto_tramo
        out += prisma(cuadrado(x, yy - 0.05, z, w * 1.1), cuadrado(x, yy + 0.18, z, w * 1.1), 'oro_b', 'oro_b', uv_alto=0.23)
        yy += 0.18
    if roto:
        out += roca_cubica(x + 1.4, y + 0.5, z - 0.6, ancho * 0.5, semilla + 3, 'totem_2_roto', 0.9, (12, 40, 70))
        for k in range(5):
            out += roca_cubica(x + r.uniform(-1.8, 1.8), y + 0.15, z + r.uniform(-1.8, 1.8), r.uniform(0.15, 0.3), semilla * 7 + k,
                               'totem_1_roto')
    else:
        out += prisma(cuadrado(x, yy, z, ancho * 1.2), cuadrado(x, yy + 0.35, z, ancho * 0.9), 'totem_3_off', 'tapa_totem', uv_alto=0.35)
    return out


def prisma(base, techo, mat_lado, mat_tapa, uv_alto=1.0, tapa=True, cerrado_abajo=False):
    """Prisma entre dos poligonos (listas de puntos del mismo largo)."""
    n = len(base)
    out = []
    for i in range(n):
        j = (i + 1) % n
        alto = max(np.linalg.norm(np.array(techo[i]) - base[i]), 0.01)
        out += _cuad(base[i], base[j], techo[j], techo[i], (0, 0), (1, 0), (1, alto / uv_alto), (0, alto / uv_alto), mat_lado)
    if tapa:
        c = np.mean(np.array(techo), axis=0)
        e0 = np.array(techo[0]) - c
        L = max(np.linalg.norm(e0), 1e-6)
        for i in range(n):
            j = (i + 1) % n
            uvs = [(0.5 + (np.array(p) - c) @ np.array([1, 0, 0]) / (2.4 * L), 0.5 + (np.array(p) - c) @ np.array([0, 0, 1]) / (2.4 * L))
                   for p in (techo[i], techo[j], c)]
            out.append(_tri(techo[i], techo[j], c, *uvs, mat_tapa))
    if cerrado_abajo:
        c = np.mean(np.array(base), axis=0)
        for i in range(n):
            j = (i + 1) % n
            out.append(_tri(base[j], base[i], c, (0, 0), (1, 0), (0.5, 1), mat_lado))
    return out


def columna(x, z, alto, radio, semilla=0, bisel=(0.0, 0.0), hunde=0.6):
    """Columna hexagonal de basalto y jade, cortada en bisel."""
    r = random.Random(semilla)
    giro = r.uniform(0, TAU)
    base, techo = [], []
    for k in range(6):
        a = giro + TAU * k / 6
        rr = radio * r.uniform(0.92, 1.05)
        px, pz = x + math.cos(a) * rr, z + math.sin(a) * rr
        base.append((px, -hunde, pz))
        techo.append((px * 0.97 + x * 0.03, alto + bisel[0] * (px - x) + bisel[1] * (pz - z), pz * 0.97 + z * 0.03))
    return prisma(base, techo, 'basalto', 'tapa', uv_alto=2.0)


def haz_columnas(x, z, n, alto, radio=0.9, semilla=0):
    """Un haz de columnas apretadas: la del centro, la mas alta."""
    r = random.Random(semilla)
    sitios = [(0, 0)]
    d = radio * math.sqrt(3) * 1.02
    for k in range(6):
        a = TAU * k / 6 + TAU / 12
        sitios.append((math.cos(a) * d, math.sin(a) * d))
    for k in range(6):
        a = TAU * k / 6
        sitios.append((math.cos(a) * d * 1.75, math.sin(a) * d * 1.75))
    r.shuffle(sitios[1:])
    out = []
    for i, (dx, dz) in enumerate([sitios[0]] + sitios[1:n]):
        h = alto * (1.0 if i == 0 else r.uniform(0.35, 0.85))
        out += columna(x + dx, z + dz, h, radio * r.uniform(0.85, 1.0), semilla * 31 + i,
                       (r.uniform(-0.35, 0.35), r.uniform(-0.35, 0.35)))
    return out


def losa(x, z, tam, inclina, giro, alza=0.0, grosor=0.35, semilla=0, mat='losa'):
    """Placa irregular del suelo, arrancada e inclinada (inclina en grados)."""
    r = random.Random(semilla)
    n = r.randint(5, 7)
    poli = []
    for k in range(n):
        a = TAU * (k + r.uniform(-0.2, 0.2)) / n
        rr = tam * r.uniform(0.6, 1.0)
        poli.append((math.cos(a) * rr, math.sin(a) * rr))
    M = vr.T(x, alza, z) @ vr.Ry(giro * vr.D2R) @ vr.Rx(inclina * vr.D2R)
    arriba = [(M @ np.array([px, 0, pz, 1.0]))[:3] for px, pz in poli]
    abajo = [(M @ np.array([px * 0.92, -grosor, pz * 0.92, 1.0]))[:3] for px, pz in poli]
    return prisma(abajo, arriba, 'tierra_c', mat, uv_alto=1.0, cerrado_abajo=True)


def escombro(x, y, z, tam, semilla=0, mat='roca'):
    r = random.Random(semilla)
    dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    pts = [np.array([x, y, z]) + np.array(d) * tam * r.uniform(0.6, 1.2) + np.array([r.uniform(-0.3, 0.3) for _ in range(3)]) * tam
           for d in dirs]
    caras = [(0, 2, 4), (4, 2, 1), (1, 2, 5), (5, 2, 0), (4, 3, 0), (1, 3, 4), (5, 3, 1), (0, 3, 5)]
    return [_tri(pts[a], pts[b], pts[c], (0, 0), (1, 0), (0.5, 1), mat) for a, b, c in caras]


def _octogono(x, z, y, r, giro=TAU / 16):
    return [(x + math.cos(giro + TAU * k / 8) * r, y, z + math.sin(giro + TAU * k / 8) * r) for k in range(8)]


def estela(x, z, mira=0.0, encendida=False, alto=5.2):
    """El totem del Sello. 'mira': hacia donde da la cara tallada (grados)."""
    g = mira * vr.D2R + TAU / 16
    out = []
    out += prisma(_octogono(x, z, -0.2, 1.55, g), _octogono(x, z, 0.55, 1.45, g), 'losa', 'losa', uv_alto=1.0)
    base, techo = _octogono(x, z, 0.55, 1.0, g), _octogono(x, z, 0.55 + alto, 0.82, g)
    for i in range(8):
        j = (i + 1) % 8
        mat = ('estela_cara' if i in (1, 2) else 'estela_lisa') + ('_on' if encendida else '')
        out += _cuad(base[i], base[j], techo[j], techo[i], (0, 1), (1, 1), (1, 0), (0, 1 - 1), mat)
    for y in (1.5, 0.55 + alto - 0.9):
        k = 1.0 - 0.18 * (y - 0.55) / alto
        out += prisma(_octogono(x, z, y, k * 1.08, g), _octogono(x, z, y + 0.32, k * 1.08, g), 'oro_b', 'oro_b', uv_alto=0.32)
    out += prisma(_octogono(x, z, 0.55 + alto, 1.05, g), _octogono(x, z, 0.95 + alto, 1.12, g), 'losa', 'losa', uv_alto=1.0)
    # el aro de jade que flota encima, con su cristal
    yc = alto + 2.4
    R, rr, N, n2 = 1.0, 0.16, 18, 6
    inc = 0.35
    def p_aro(i, j):
        a, b = TAU * i / N, TAU * j / n2
        px = (R + rr * math.cos(b)) * math.cos(a)
        py = rr * math.sin(b)
        pz = (R + rr * math.cos(b)) * math.sin(a)
        py, pz = py * math.cos(inc) - pz * math.sin(inc), py * math.sin(inc) + pz * math.cos(inc)
        return (x + px, yc + py, z + pz)
    for i in range(N):
        for j in range(n2):
            out += _cuad(p_aro(i, j), p_aro(i + 1, j), p_aro(i + 1, j + 1), p_aro(i, j + 1),
                         (i / N, j / n2), ((i + 1) / N, j / n2), ((i + 1) / N, (j + 1) / n2), (i / N, (j + 1) / n2), 'aro')
    out += cristal(x, yc, z, 0.75, 'fragmento' if encendida else 'aro')
    return out


def cristal(x, y, z, tam, mat='fragmento', eje=(0, 1, 0), largo=1.6, lados=6, semilla=0):
    """Bipiramide de cristal a lo largo de 'eje'."""
    e = np.array(eje, float)
    e /= np.linalg.norm(e)
    a = np.cross(e, [0.3, 0.1, 1.0]); a /= np.linalg.norm(a)
    b = np.cross(e, a)
    c = np.array([x, y, z], float)
    r = random.Random(semilla)
    anillo = [c + (a * math.cos(TAU * k / lados) + b * math.sin(TAU * k / lados)) * tam * 0.55 * r.uniform(0.85, 1.1)
              for k in range(lados)]
    punta, cola = c + e * tam * largo, c - e * tam * largo * 0.7
    out = []
    for k in range(lados):
        j = (k + 1) % lados
        out.append(_tri(anillo[k], anillo[j], punta, (k / lados, 0.5), ((k + 1) / lados, 0.5), ((k + 0.5) / lados, 0), mat))
        out.append(_tri(anillo[j], anillo[k], cola, ((k + 1) / lados, 0.5), (k / lados, 0.5), ((k + 0.5) / lados, 1), mat))
    return out


# ----------------------------------------------------------------------
#  Dibujo
# ----------------------------------------------------------------------
def dibujar(lz, cam, tris, luces, amb, niebla=None, brillo=1.3):
    for P, UV, mat in tris:
        t, em = tex(mat)
        luz = vr.iluminar(vr.normal(P), cam, P.mean(axis=0), luces, amb)
        lz.triangulo(cam, P, UV, t, luz, em, niebla, brillo=brillo, envolver=True)


def calco(lz, cam, x, z, radio, textura, brillo=1.0, giro=0.0, y=0.04, opaco=False, luz=None, largo=None):
    """Un calco plano en el suelo (sumado o, con opaco, pintado encima). Con
    'largo', es un rectangulo de radio x largo girado 'giro' grados."""
    c, s = math.cos(giro * vr.D2R), math.sin(giro * vr.D2R)
    rx, rz = radio, (radio if largo is None else largo)
    esq = [(-rx, -rz), (rx, -rz), (rx, rz), (-rx, rz)]
    P = [(x + ex * c - ez * s, y, z + ex * s + ez * c) for ex, ez in esq]
    UV = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for tri in ((0, 1, 2), (0, 2, 3)):
        if opaco:
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], textura, np.ones(3) if luz is None else luz, None, None)
        else:
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], textura, np.ones(3), None, None, aditivo=True, brillo=brillo)


def grieta(lz, cam, x0, z0, x1, z1, ancho=0.9, semilla=5, brillo=1.2, luz=None, parte='todo'):
    """Grieta del suelo de (x0, z0) a (x1, z1). parte: 'oscura' (con lo
    opaco), 'brillo' (al final, sobre todo lo demas) o 'todo'."""
    oscura, bri = _GRIETAS.setdefault(semilla, _tex_grieta(semilla=semilla))
    L = math.hypot(x1 - x0, z1 - z0)
    giro = math.degrees(math.atan2(-(x1 - x0), z1 - z0))
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    if parte in ('todo', 'oscura'):
        calco(lz, cam, cx, cz, ancho, oscura, giro=giro, y=0.03, opaco=True,
              luz=np.array([0.7, 0.7, 0.7]) if luz is None else luz, largo=L / 2)
    if parte in ('todo', 'brillo'):
        calco(lz, cam, cx, cz, ancho, bri, brillo=brillo, giro=giro, y=0.05, largo=L / 2)


_GRIETAS = {}


def cartel(lz, cam, centro, tam, textura, brillo=1.0):
    """Sprite plano mirando a la camara (sumado)."""
    c = np.array(centro, float)
    r, u = cam.r * tam, cam.u * tam
    P = [c - r + u, c + r + u, c + r - u, c - r - u]
    UV = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], textura, np.ones(3), None, None, aditivo=True, brillo=brillo)


def cinta(lz, cam, p0, p1, ancho, textura, brillo=1.0):
    """Cinta de p0 (v=0) a p1 (v=1), de cara a la camara (estelas, haces)."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = p1 - p0
    lado = np.cross(d, cam.ojo - (p0 + p1) / 2)
    lado /= max(np.linalg.norm(lado), 1e-9)
    lado *= ancho
    P = [p0 - lado, p0 + lado, p1 + lado, p1 - lado]
    UV = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], textura, np.ones(3), None, None, aditivo=True, brillo=brillo)


HALO = _tex_halo()
HALO_SUAVE = _tex_halo(64, (120, 255, 120), (200, 255, 190), 3.5)
LLAMA = _tex_llama()
HAZ = _tex_haz()
ONDA = _tex_onda()
CRATER = _tex_crater()
AVISO = _tex_aviso()


def marca_cataclismo(cuenta):
    return _MARCAS.setdefault(round(cuenta, 2), _tex_marca_cataclismo(cuenta=cuenta))


_MARCAS = {}


def sello(cuenta):
    return _SELLOS.setdefault(round(cuenta, 2), _tex_sello(cuenta=cuenta))


_SELLOS = {}


def fragmento_cayendo(lz, cam, pos, direccion, tam, luces, amb, semilla=0, largo_estela=9.0, parte='todo'):
    """El fragmento con su llama, su halo y la estela por detras."""
    d = np.array(direccion, float)
    d /= np.linalg.norm(d)
    p = np.array(pos, float)
    if parte in ('todo', 'malla'):
        dibujar(lz, cam, cristal(*p, tam, 'fragmento', d, 1.7, 6, semilla), luces, amb, brillo=1.6)
    if parte == 'malla':
        return
    cinta(lz, cam, p + d * tam * 0.6, p - d * largo_estela * tam, tam * 1.1, LLAMA, 1.4)
    cinta(lz, cam, p, p - d * largo_estela * tam * 0.55, tam * 0.45, LLAMA, 1.6)
    cartel(lz, cam, p, tam * 2.4, HALO, 0.9)


# ----------------------------------------------------------------------
#  Polvo, en 2D sobre la imagen compuesta
# ----------------------------------------------------------------------
def polvo_en(img, cam, puntos, ss=2, color=(120, 100, 70), semilla=0, densidad=1.0):
    """puntos: (x, y, z, radio en bloques). Nubes de polvo que se van
    abriendo, proyectadas y difuminadas."""
    r = random.Random(semilla)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for (x, y, z, rad) in puntos:
        for _ in range(int(7 * densidad)):
            px, py, pz = cam.proyectar((x + r.uniform(-rad, rad) * 0.7, y + r.uniform(0, rad * 0.6), z + r.uniform(-rad, rad) * 0.7))
            if pz < 0.5:
                continue
            rr = rad * r.uniform(0.35, 0.7) * cam.foco / pz / ss
            px, py = px / ss, py / ss
            g = r.uniform(0.8, 1.15)
            d.ellipse((px - rr, py - rr * 0.75, px + rr, py + rr * 0.75),
                      fill=(int(color[0] * g), int(color[1] * g), int(color[2] * g), r.randint(50, 110)))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(max(2, img.size[0] / 300))))

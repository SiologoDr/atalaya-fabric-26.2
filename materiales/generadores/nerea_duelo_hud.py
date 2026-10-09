"""
La pantalla del Duelo de Canto de Nerea (octubre de 2026; Juan: "debe verse mas
como Minecraft, mas interactivo y con diseno"). Todo pixel a pixel, al tamano en
que se pinta (cada texel un pixel de interfaz), con la paleta de la barra de
Nerea (nerea_remake_hud.py): prismarina vieja, hueso, coral y espuma.

  gui/nerea_duelo_panel.png     el panel entero (PANEL_W x PANEL_H): el marco de
                                bloques de prismarina con su junta cada nueve
                                pixeles, coral y percebes, la placa del titulo, el
                                hueco del medidor y los cuatro carriles de agua
                                (cada uno de su color: cian, violeta, magenta y
                                rosa), oscuros arriba y mas claros junto a la cuerda
  gui/nerea_duelo_cuerda.png    la cuerda del arpa (88 x 3), de oro
  gui/nerea_duelo_tecla.png     la tecla de un carril (20 x 20) y, debajo, la
                                misma hundida (20 x 20): prismarina clara
  gui/nerea_duelo_notas.png     las notas que bajan (4 de 12 x 12, en blanco con
                                su contorno: el color lo pone el carril)
  gui/nerea_duelo_halo.png      el halo de una nota y el destello al acertar (16 x 16)
  gui/nerea_duelo_estallido.png el estallido al acertar (24 x 24): aro y chispas
  gui/nerea_duelo_medidor.png   el relleno del medidor (84 x 6), en blanco
  gui/nerea_duelo_nerea.png     la cara de Nerea (11 x 11) al final del medidor

Las medidas las usa DueloCantoHud; si se cambian aqui, alli tambien.

Uso: python nerea_duelo_hud.py <raiz del proyecto> [vista_previa.png]
"""
import math
import os
import random
import sys

from PIL import Image

RAIZ = sys.argv[1]
VISTA = sys.argv[2] if len(sys.argv) > 2 else None
GUI = os.path.join(RAIZ, 'src', 'main', 'resources', 'assets', 'atalaya', 'textures', 'gui')
os.makedirs(GUI, exist_ok=True)


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mezclar(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


PRIS = [hexc(c) for c in ('0b1f21', '173b3c', '22504d', '2f6660', '3f7f76', '5aa596', '8fd0bd')]
HUESO = [hexc(c) for c in ('5c5545', '8a8068', 'b3a98c', 'd3c9aa', 'ece4c8')]
CORAL = [hexc(c) for c in ('7a1636', 'a8204a', 'd8336a', 'f2618f')]
ORO = [hexc(c) for c in ('7a4a08', 'c07a10', 'ffc23a', 'ffe08a', 'fffbe0')]
FONDO = hexc('050e12')
OSCURO = hexc('02080a')
ESPUMA = hexc('eaffff')
# Los carriles: el mismo color que las notas del canto (NereaParticula.COLORES_NOTA).
CARRILES = [hexc(c) for c in ('4fd8f0', '9a7bff', 'd45af0', 'f06aa8')]

# ---------------------------------------------------------------- medidas
CARRIL = 22
N_CARRILES = 4
BORDE = 4
LANES_W = CARRIL * N_CARRILES          # 88
PANEL_W = LANES_W + 2 * BORDE + 4      # 96: 2 de aire a cada lado de los carriles
TITULO_Y, TITULO_H = 4, 12
MEDIDOR_Y, MEDIDOR_H = 19, 10
CARRILES_Y, CARRILES_H = 32, 108
TECLAS_Y, TECLAS_H = 144, 22
PANEL_H = TECLAS_Y + TECLAS_H + BORDE   # 170
CARRILES_X = BORDE + 2
LINEA_Y = CARRILES_Y + CARRILES_H - 12  # la cuerda, en el panel


def lienzo(w, h):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    return im, im.load()


def panel():
    r = random.Random(3)
    im, px = lienzo(PANEL_W, PANEL_H)
    # El marco: bloques de prismarina vieja, junta cada 9, luz arriba y sombra abajo.
    for y in range(PANEL_H):
        for x in range(PANEL_W):
            if x in (0, PANEL_W - 1) or y in (0, PANEL_H - 1):
                px[x, y] = PRIS[0]
                continue
            k = r.choice((3, 3, 4, 3, 2))
            if y == 1 or x == 1:
                k = 5
            elif y == PANEL_H - 2 or x == PANEL_W - 2:
                k = 1
            elif (x - 1) % 9 == 0 or (y - 1) % 9 == 0:
                k = 2
            px[x, y] = PRIS[k]
    # Los huecos: titulo, medidor y carriles, con su canto oscuro.
    def hueco(x0, y0, w, h, fondo):
        for y in range(y0 - 1, y0 + h + 1):
            for x in range(x0 - 1, x0 + w + 1):
                if x0 <= x < x0 + w and y0 <= y < y0 + h:
                    px[x, y] = fondo(x - x0, y - y0, w, h)
                elif y == y0 - 1 or x == x0 - 1:
                    px[x, y] = OSCURO
                else:
                    px[x, y] = PRIS[5]
    hueco(CARRILES_X, TITULO_Y, LANES_W, TITULO_H,
          lambda x, y, w, h: PRIS[1] if y < h - 2 else PRIS[2])
    hueco(CARRILES_X, MEDIDOR_Y, LANES_W, MEDIDOR_H, lambda x, y, w, h: FONDO)

    def agua(x, y, w, h):
        c = CARRILES[x // CARRIL]
        en = x % CARRIL
        # oscuro arriba, el color sube hacia la cuerda; separacion de un pixel entre carriles
        t = (y / h) ** 1.6
        base = mezclar(FONDO, mezclar(FONDO, c, 0.55), t)
        if en == 0 and x > 0:
            return PRIS[0]
        if en in (1, CARRIL - 1):
            base = mezclar(base, c, 0.18)
        # ondas: rayas finas que bajan, de luz en el agua
        if (y + 3 * (x // CARRIL)) % 11 == 0 and 4 <= en <= CARRIL - 5:
            base = mezclar(base, c, 0.22)
        # por debajo de la cuerda, el pozo de la tecla
        if y > h - 12:
            base = mezclar(base, FONDO, 0.35)
        return base
    hueco(CARRILES_X, CARRILES_Y, LANES_W, CARRILES_H, agua)
    hueco(CARRILES_X, TECLAS_Y, LANES_W, TECLAS_H, lambda x, y, w, h: PRIS[1] if y < h - 3 else PRIS[2])
    # Coral y percebes sobre el marco.
    for x, alto, c in ((9, 4, 1), (52, 3, 2), (83, 5, 1)):
        for k in range(alto):
            px[x, PANEL_H - 2 - k] = CORAL[min(3, c + k // 2)]
        px[x - 1, PANEL_H - alto] = CORAL[c]
        px[x + 1, PANEL_H - alto - 1] = CORAL[c]
    for (x, y) in ((2, 40), (2, 77), (PANEL_W - 3, 58), (PANEL_W - 3, 101), (2, 120)):
        px[x, y] = HUESO[3]
        px[x, y + 1] = HUESO[1]
    for (x, y) in ((30, 1), (31, 1), (70, 1), (PANEL_W - 2, 140)):
        px[x, y] = HUESO[4]
    return im


def cuerda():
    im, px = lienzo(LANES_W, 3)
    for x in range(LANES_W):
        px[x, 0] = ORO[3] if x % 4 else ORO[4]
        px[x, 1] = ORO[2]
        px[x, 2] = ORO[0]
    return im


def tecla():
    """La tecla normal (arriba) y hundida (abajo): cara de prismarina clara, filo
    de luz, labio oscuro debajo. La letra la pone el juego con su fuente."""
    im, px = lienzo(20, 40)
    for fila, hundida in ((0, False), (20, True)):
        labio = 1 if hundida else 3
        for y in range(20):
            for x in range(20):
                if x in (0, 19) and y in (0, 19):
                    continue
                if x in (0, 19) or y in (0, 19):
                    c = PRIS[0]
                elif y >= 19 - labio:
                    c = PRIS[1] if y == 18 or x == 18 else PRIS[2]
                elif (y == 1 or x == 1) and not hundida:
                    c = PRIS[6]
                elif x == 18 or y == 18 - labio:
                    c = PRIS[3]
                else:
                    c = PRIS[5] if not hundida else PRIS[4]
                px[x, fila + y] = c
    return im


NOTAS = [
    # corchea
    ["....##......", "....###.....", "....####....", "....##.##...", "....##..#...", "....##......",
     "....##......", "..####......", ".#####......", ".#####......", "..###.......", "............"],
    # dos corcheas unidas
    ["..########..", "..########..", "..##....##..", "..##....##..", "..##....##..", "..##....##..",
     "..##....##..", "####..####..", "####..####..", "####..####..", ".##....##...", "............"],
    # negra
    [".....##.....", ".....##.....", ".....##.....", ".....##.....", ".....##.....", ".....##.....",
     ".....##.....", "...####.....", "..#####.....", "..#####.....", "...###......", "............"],
    # una perla (redonda): la nota de Nerea
    ["............", "....####....", "...######...", "..########..", "..##.#####..", "..#.######..",
     "..########..", "..########..", "...######...", "....####....", "............", "............"],
]


def notas():
    im, px = lienzo(12 * len(NOTAS), 12)
    for i, dib in enumerate(NOTAS):
        pts = {(x, y) for y, fila in enumerate(dib) for x, c in enumerate(fila) if c == '#'}
        for (x, y) in pts:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q not in pts and 0 <= q[0] < 12 and 0 <= q[1] < 12:
                        px[i * 12 + q[0], q[1]] = (20, 12, 40, 230)
        for (x, y) in pts:
            # blanco arriba y algo mas apagado abajo: al tenirlo, sale la rampa del color
            v = 255 if y < 5 else 232 if y < 8 else 205
            px[i * 12 + x, y] = (v, v, v, 255)
        # el brillo de la cabeza
        if i == 3:
            px[i * 12 + 4, 4] = (255, 255, 255, 255)
    return im


def halo():
    im, px = lienzo(16, 16)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5) / 8.0
            if d < 1:
                a = int(200 * (1 - d) ** 1.8)
                px[x, y] = (255, 255, 255, a)
    return im


def estallido():
    im, px = lienzo(24, 24)
    for y in range(24):
        for x in range(24):
            d = math.hypot(x - 11.5, y - 11.5)
            if 8.6 <= d <= 10.4:
                px[x, y] = (255, 255, 255, 255 if 9.2 <= d <= 9.8 else 170)
    for k in range(8):
        a = k * math.pi / 4
        for j in range(3):
            x = int(round(11.5 + math.cos(a) * (4 + j)))
            y = int(round(11.5 + math.sin(a) * (4 + j)))
            px[x, y] = (255, 255, 255, 255 - j * 60)
    return im


def medidor():
    im, px = lienzo(LANES_W - 4, 6)
    for y in range(6):
        for x in range(LANES_W - 4):
            v = 255 if y == 0 else 236 if y < 3 else 210 if y < 5 else 178
            if x % 6 == 0 and 1 <= y <= 4:
                v -= 25
            px[x, y] = (v, v, v, 255)
    return im


def cara_nerea():
    """La cara de Nerea, 11 x 11: el craneo de hueso con la corona de coral y los
    ojos cian."""
    im, px = lienzo(11, 11)
    for y in range(11):
        for x in range(11):
            if y < 3:
                if (x in (1, 4, 6, 9) and y >= 0) or (x in (2, 5, 8) and y >= 1):
                    px[x, y] = CORAL[2] if y == 0 else CORAL[1]
                continue
            if 1 <= x <= 9 and 3 <= y <= 9 and not (y == 9 and x in (1, 9)):
                px[x, y] = HUESO[3] if y < 6 else HUESO[2]
            if x in (0, 10) and 4 <= y <= 8:
                px[x, y] = HUESO[0]
    for (x, y) in ((3, 5), (7, 5)):
        px[x, y] = hexc('3fe0ff')
        px[x, y + 1] = hexc('1b8aa6')
    for x in range(3, 8):
        px[x, 8] = HUESO[0] if x % 2 else HUESO[4]
    px[5, 7] = HUESO[0]
    return im


PIEZAS = {
    'nerea_duelo_panel': panel(),
    'nerea_duelo_cuerda': cuerda(),
    'nerea_duelo_tecla': tecla(),
    'nerea_duelo_notas': notas(),
    'nerea_duelo_halo': halo(),
    'nerea_duelo_estallido': estallido(),
    'nerea_duelo_medidor': medidor(),
    'nerea_duelo_nerea': cara_nerea(),
}
for nombre, im in PIEZAS.items():
    im.save(os.path.join(GUI, nombre + '.png'))
    print('ok', nombre, im.size)
print('PANEL', PANEL_W, PANEL_H, 'CARRILES_Y', CARRILES_Y, 'LINEA_Y', LINEA_Y, 'TECLAS_Y', TECLAS_Y)

if VISTA:
    # Un montaje como lo veria el juego, ampliado: el panel con notas, la cuerda y las teclas.
    fondo = Image.new('RGBA', (PANEL_W + 60, PANEL_H + 20), (120, 150, 190, 255))
    p = PIEZAS['nerea_duelo_panel']
    fondo.alpha_composite(p, (10, 10))
    fondo.alpha_composite(PIEZAS['nerea_duelo_cuerda'], (10 + CARRILES_X, 10 + LINEA_Y - 1))
    for i in range(4):
        t = PIEZAS['nerea_duelo_tecla'].crop((0, 20 if i == 1 else 0, 20, 40 if i == 1 else 20))
        fondo.alpha_composite(t, (10 + CARRILES_X + i * CARRIL + 1, 10 + TECLAS_Y + 1))
        n = PIEZAS['nerea_duelo_notas'].crop((12 * (i % 4), 0, 12 * (i % 4) + 12, 12))
        c = CARRILES[i]
        n = Image.merge('RGBA', [b.point(lambda v, k=k: v * c[k] // 255) if k < 3 else b for k, b in enumerate(n.split())])
        fondo.alpha_composite(n, (10 + CARRILES_X + i * CARRIL + 5, 10 + CARRILES_Y + 20 + i * 18))
    fondo.alpha_composite(PIEZAS['nerea_duelo_nerea'], (10 + CARRILES_X + LANES_W - 12, 10 + MEDIDOR_Y - 1))
    fondo.resize((fondo.width * 4, fondo.height * 4), Image.NEAREST).save(VISTA)

"""
Renders de la ficha de las mecanicas nuevas de Nerea (octubre de 2026: "que cada
jefe haga que los jugadores cooperen con mecanicas suyas"). Cada propuesta en el
fondo del mar de su ficha, con la Nerea del juego y jugadores; usa las ayudas de
nerea_remake_escenas (camara, luz, niebla, texturas de efectos).

  canto       Canto de Sirena: los hechizados caminan hacia ella; un companero
              los despierta de un golpe
  naufragio   Ancla del Naufragio: el dano del ancla se reparte entre los que
              esten dentro del circulo
  marea_alta  Marea Alta: la arena se inunda; burbujas de aire que compartir
  tira        Tira y afloja: los companeros sujetan la cadena del Arpon
  cadenas     Encadenados: parejas atadas por una cadena de agua
  corazon     Corazon a la deriva: su corazon flota y se lleva a golpes al remolino

Uso: python nerea_mecanicas_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nerea_remake_escenas as R  # lee la raiz y la carpeta de salida de sys.argv
from nerea_remake_escenas import (vr, ne, nm, nj, nr, pose, nerea, jugador, fondo, acabar, dibujar_trans, suelo_cuad,
                                  billboard, cinta3d, linea_suelo, ancla, tex_aro, tex_burbuja, tex_haz, tex_galon,
                                  tex_plano, tex_ola, tex_espiral, COLOR, AGUA, LUCES, AMB, SS, OUT, RAIZ, FUENTE)

ROSA = (255, 118, 196)
ORO = (255, 194, 58)
VERDE = (120, 255, 150)
ROJO = (255, 70, 70)
BLANCO = (245, 250, 255)


def lienzo(ojo, objetivo, W, H, fov=58, cerca=20, lejos=48):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ne.NieblaMar(cerca, lejos)
    fondo(lz, cam, niebla)
    return cam, lz, niebla


def puntos_nerea(p, x, z, nombres):
    """Donde caen en el mundo unos huesos de la Nerea dibujada en (x, z)."""
    nr.usar('despues')
    M = vr.entidad_a_mundo(x, 0, z, 0, nr.ESCALA['despues'])
    Ms = nj.matrices(p)
    return [(M @ Ms[n] @ np.array([0, 0, 0, 1.0]))[:3] for n in nombres]


def curva(a, b, alto, n=10):
    a, b = np.array(a, float), np.array(b, float)
    return [tuple(a + (b - a) * k + np.array([0, alto * math.sin(math.pi * k), 0])) for k in np.linspace(0, 1, n)]


def chispa(n=48):
    """Una estrella de golpe: cuatro puntas blancas con el centro encendido."""
    t = np.zeros((n, n, 4), np.uint8)
    c = (n - 1) / 2
    for y in range(n):
        for x in range(n):
            dx, dy = abs(x - c) / c, abs(y - c) / c
            v = max(0.0, 1.0 - (dx * 6 + dy) if dx < dy else 1.0 - (dy * 6 + dx))
            r = math.hypot(dx, dy)
            v = max(v, max(0.0, 1.0 - r * 3.0))
            if v > 0:
                t[y, x] = (255, 252, 230, int(255 * min(1.0, v * 1.4)))
    return t


def nota(color, n=48):
    """Una nota musical de pixel (la del Canto): cabeza redonda, palo y bandera."""
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            cab = math.hypot((x - 16) / 9.0, (y - 36) / 7.0) <= 1.0
            palo = 23 <= x <= 26 and 8 <= y <= 36
            bandera = 26 <= x <= 36 and 8 <= y <= 16 + (x - 26) * 0.6
            if cab or palo or bandera:
                t[y, x] = (*color, 255)
    return t


def png(ruta, escala=1.0):
    im = Image.open(ruta).convert('RGBA')
    if escala != 1.0:
        im = im.resize((int(im.width * escala), int(im.height * escala)), Image.NEAREST)
    return np.array(im)


def rotular(nombre, textos):
    """Rotulos encima de la foto ya guardada: (texto, x, y, tam, color)."""
    ruta = os.path.join(OUT, nombre + '.jpg')
    img = Image.open(ruta).convert('RGB')
    d = ImageDraw.Draw(img)
    for texto, x, y, tam, color in textos:
        f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', tam)
        d.text((x + 2, y + 2), texto, font=f, fill=(6, 14, 24))
        d.text((x, y), texto, font=f, fill=color)
    img.save(ruta, quality=90)


# ----------------------------------------------------------------------
#  1. Canto de Sirena
# ----------------------------------------------------------------------
def canto(W=1600, H=900, fase=2):
    cam, lz, niebla = lienzo((15.0, 6.5, -23.0), (-1.0, 5.0, -2.0), W, H)
    p = pose('MIRADA', 0.35, fase=fase)
    nerea(lz, cam, 'despues', 0, 8, 0, p=p, fase=fase, niebla=niebla, luces=LUCES, amb=AMB, brillo=1.5)
    ojos = puntos_nerea(p, 0, 8, ('ojo_izq', 'ojo_der'))
    boca = (ojos[0] + ojos[1]) / 2 + np.array([0, -1.3, -0.6])
    hechizado = np.array([-2.6, 0.0, -5.5])
    # el camino que haria hasta ella, en el suelo
    dibujar_trans(lz, cam, linea_suelo(hechizado[0], hechizado[2], -0.6, 3.2, 0.7), tex_galon(ROSA), 0.7, niebla, 0.4)
    dibujar_trans(lz, cam, suelo_cuad(hechizado[0], hechizado[2], 1.7, giro=0.3),
                  tex_aro(ROSA, grueso=0.12, marcas=10, relleno=70), 0.9, niebla, 0.7)
    jugador(lz, cam, hechizado[0], hechizado[2], 10, niebla=niebla)
    rescate = np.array([-5.4, 0.0, -8.6])
    jugador(lz, cam, rescate[0], rescate[2], -40, niebla=niebla)
    for (x, z, g) in ((6.0, -12.0, 15), (2.5, -15.5, 0), (9.5, -7.5, 30)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    # el canto: ondas y notas que van de su boca al hechizado
    camino = curva(boca, hechizado + np.array([0, 1.7, 0]), 1.6, 9)
    dibujar_trans(lz, cam, cinta3d(camino, 0.35, cam), tex_haz(ROSA), 0.55, niebla, 0.6)
    ta = tex_aro(ROSA, 64, 0.1, 0)
    tn = nota((255, 170, 220))
    for i, q in enumerate(camino[1:-1]):
        k = (i + 1) / len(camino)
        dibujar_trans(lz, cam, [billboard(q, 0.9 - 0.4 * k, cam)], ta, 0.85, niebla, 0.7)
        if i % 2 == 0:
            dibujar_trans(lz, cam, [billboard(np.array(q) + np.array([0.6, 0.8, 0]), 0.5, cam, giro=0.2 * i)], tn, 1.0,
                          niebla, 0.6)
    # corazones sobre el hechizado y el golpe del companero que lo despierta
    tb = tex_burbuja(ROSA)
    for d in ((0, 2.5, 0), (0.5, 2.9, 0.2), (-0.4, 3.2, -0.1)):
        dibujar_trans(lz, cam, [billboard(hechizado + np.array(d), 0.22, cam)], tb, 1.0, niebla, 0.8)
    medio = (hechizado + rescate) / 2 + np.array([0.3, 1.3, 0.3])
    dibujar_trans(lz, cam, [billboard(medio, 0.9, cam, giro=0.4)], chispa(), 1.0, None, 1.0)
    acabar(lz, cam, W, H, 'canto', 71)
    rotular('canto', [('HECHIZADO', 800, 625, 30, ROSA), ('¡UN GOLPE LO DESPIERTA!', 990, 520, 28, BLANCO)])


# ----------------------------------------------------------------------
#  2. Ancla del Naufragio
# ----------------------------------------------------------------------
def naufragio(W=1600, H=900, fase=2):
    cam, lz, niebla = lienzo((11.0, 9.5, -27.0), (1.0, 4.5, -6.0), W, H, fov=56)
    nerea(lz, cam, 'despues', -3, 12, -20, p=pose('GEISER', 0.32, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    c = np.array([1.5, 0.0, -8.0])
    dibujar_trans(lz, cam, suelo_cuad(c[0], c[2], 4.4, giro=0.2), tex_aro(ORO, grueso=0.07, marcas=12, relleno=80),
                  0.9, niebla, 0.8)
    for (x, z, g) in ((0.4, -8.4, 10), (2.6, -7.0, -20), (1.8, -9.9, 30)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    jugador(lz, cam, 9.0, -13.0, -30, niebla=niebla)
    jugador(lz, cam, -7.5, -12.5, 20, niebla=niebla)
    arriba = c + np.array([0.0, 10.5, 0.0])
    dibujar_trans(lz, cam, cinta3d([tuple(arriba), tuple(c + np.array([0, 0.2, 0]))], 1.4, cam), tex_haz(ORO), 0.35,
                  niebla, 0.4)
    nm.dibujar(lz, cam, ancla(tuple(arriba), rumbo=30, escala=2.2, inclina=180), LUCES, AMB, niebla)
    acabar(lz, cam, W, H, 'naufragio', 72)
    rotular('naufragio', [('÷ 3', 860, 600, 64, ORO), ('53 CADA UNO', 640, 700, 30, ORO)])


# ----------------------------------------------------------------------
#  3. Marea Alta
# ----------------------------------------------------------------------
def marea_alta(W=1600, H=900, fase=3):
    cam, lz, niebla = lienzo((14.0, 5.6, -24.0), (0.0, 3.6, -3.0), W, H, fov=58)
    nerea(lz, cam, 'despues', 0, 10, 0, p=pose('MAREA', 1.2, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    burbujas = [(np.array([-5.0, 2.3, -8.0]), 1.9, [(-5.0, -8.0)]),
                (np.array([4.0, 2.4, -11.0]), 2.3, [(3.4, -11.3), (4.7, -10.6)]),
                (np.array([-11.0, 3.4, -15.0]), 1.5, [])]
    dentro = [q for _, _, js in burbujas for q in js]
    for (x, z) in dentro:
        jugador(lz, cam, x, z, 0, niebla=niebla)
    ahogado = (8.5, -6.0)
    jugador(lz, cam, ahogado[0], ahogado[1], -20, niebla=niebla)
    # el agua: un plano a 3,4 bloques, con la superficie rizada
    nivel = 3.4
    # en baldosas de 4 bloques, todas delante de la camara (un plano entero con
    # esquinas detras de ella no se proyecta)
    plano, rizo = [], []
    for x0 in range(-28, 28, 4):
        for z0 in range(-23, 41, 4):
            P = [(x0, nivel, z0), (x0 + 4, nivel, z0), (x0 + 4, nivel, z0 + 4), (x0, nivel, z0 + 4)]
            plano.append((P, [(0, 0), (1, 0), (1, 1), (0, 1)]))
            rizo.append(([(q[0], nivel + 0.02, q[2]) for q in P], [(0, 0), (1, 0), (1, 1), (0, 1)]))
    dibujar_trans(lz, cam, plano, tex_plano((50, 150, 210), 140), 0.75, niebla, 0.05)
    dibujar_trans(lz, cam, rizo, tex_ola(AGUA), 0.25, niebla, 0.08)
    tb = tex_burbuja((230, 250, 255))
    for c, r, _ in burbujas:
        dibujar_trans(lz, cam, [billboard(c, r, cam)], tb, 0.75, niebla, 0.45)
        for k in range(4):
            q = c + np.array([0.3 * math.sin(k * 2.1), r + 0.6 + k * 0.7, 0])
            dibujar_trans(lz, cam, [billboard(q, 0.18 + 0.05 * k, cam)], tb, 0.9, niebla, 0.4)
    for k in range(5):
        q = np.array([ahogado[0] + 0.2 * math.sin(k), 2.2 + k * 0.45, ahogado[1]])
        dibujar_trans(lz, cam, [billboard(q, 0.12, cam)], tb, 0.9, niebla, 0.4)
    acabar(lz, cam, W, H, 'marea_alta', 73)
    rotular('marea_alta', [('SIN AIRE', 470, 520, 30, (255, 150, 150)), ('BURBUJAS DE AIRE', 760, 380, 30, BLANCO)])


# ----------------------------------------------------------------------
#  4. Tira y afloja
# ----------------------------------------------------------------------
def tira(W=1600, H=900, fase=2):
    cam, lz, niebla = lienzo((22.0, 7.5, -12.0), (0.0, 4.0, -4.0), W, H, fov=60)
    p = pose('ARPON_TIRAR', 0.25, fase=fase)
    nerea(lz, cam, 'despues', 0, 8, 0, p=p, fase=fase, niebla=niebla, luces=LUCES, amb=AMB, brillo=1.5)
    mano = puntos_nerea(p, 0, 8, ('mano_izq',))[0] if 'mano_izq' in nj.matrices(p) else np.array([-2.5, 8.0, 6.0])
    presa = np.array([0.8, 0.6, -14.0])
    jugador(lz, cam, presa[0], presa[2], 180, y=0.6, niebla=niebla)
    pts = curva(mano, presa + np.array([0, 1.2, 0]), -1.2, 12)
    for i in range(len(pts) - 1):
        nm.dibujar(lz, cam, nm.cadena_mundo(pts[i], pts[i + 1], 2.0), LUCES, AMB, niebla)
    # los que la sujetan: un aro verde bajo cada uno y la cadena encendida donde la agarran
    for (x, z) in ((-1.4, -9.2), (2.4, -6.0)):
        dibujar_trans(lz, cam, suelo_cuad(x, z, 1.3), tex_aro(VERDE, grueso=0.14, marcas=6, relleno=60), 0.9, niebla, 0.7)
        jugador(lz, cam, x, z, 180, niebla=niebla)
    dibujar_trans(lz, cam, cinta3d(pts[6:11], 0.45, cam), tex_haz(VERDE), 0.6, niebla, 0.7)
    jugador(lz, cam, -7.0, -14.0, 120, niebla=niebla)
    acabar(lz, cam, W, H, 'tira', 74)
    rotular('tira', [('SUJETANDO 2/2', 640, 700, 34, VERDE), ('¡SE ROMPE: SE TAMBALEA!', 120, 120, 30, BLANCO)])


# ----------------------------------------------------------------------
#  5. Encadenados
# ----------------------------------------------------------------------
def cadenas(W=1600, H=900, fase=2):
    cam, lz, niebla = lienzo((12.0, 8.5, -26.0), (0.0, 2.5, -6.0), W, H, fov=58)
    nerea(lz, cam, 'despues', 0, 13, 0, p=pose('BURBUJAS', 0.4, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    parejas = [((-6.5, -5.5), (-3.2, -8.6), AGUA, 1.0), ((3.0, -3.5), (5.6, -7.8), AGUA, 1.0),
               ((-10.0, -14.5), (3.5, -16.0), ROJO, 0.0)]
    for a, b, color, comba in parejas:
        jugador(lz, cam, a[0], a[1], 0, niebla=niebla)
        jugador(lz, cam, b[0], b[1], 0, niebla=niebla)
        pa, pb = np.array([a[0], 1.1, a[1]]), np.array([b[0], 1.1, b[1]])
        pts = curva(pa, pb, -0.7 * comba, 10)
        for i in range(len(pts) - 1):
            nm.dibujar(lz, cam, nm.cadena_mundo(pts[i], pts[i + 1], 1.4), LUCES, AMB, niebla)
        dibujar_trans(lz, cam, cinta3d(pts, 0.28, cam), tex_haz(color), 0.6, niebla, 0.8)
        if comba == 0.0:
            medio = (pa + pb) / 2 + np.array([0, 0.3, 0])
            dibujar_trans(lz, cam, [billboard(medio, 0.8, cam)], chispa(), 1.0, None, 1.0)
    acabar(lz, cam, W, H, 'cadenas', 75)
    rotular('cadenas', [('DEMASIADO LEJOS: ¡TIRÓN!', 300, 760, 30, (255, 150, 150))])


# ----------------------------------------------------------------------
#  6. Corazon a la deriva
# ----------------------------------------------------------------------
def corazon(W=1600, H=900, fase=4):
    cam, lz, niebla = lienzo((-15.0, 6.5, -21.0), (3.0, 3.5, -5.0), W, H, fov=58)
    nerea(lz, cam, 'despues', -2, 9, 20, p=pose('AGOTADO', 2.0, fase=fase), fase=fase, niebla=niebla, luces=LUCES,
          amb=AMB, brillo=1.5)
    meta = np.array([13.0, 0.0, -13.0])
    dibujar_trans(lz, cam, suelo_cuad(meta[0], meta[2], 3.4, giro=0.5), tex_espiral(AGUA), 0.85, niebla, 0.6)
    dibujar_trans(lz, cam, suelo_cuad(meta[0], meta[2], 3.8), tex_aro(ORO, grueso=0.06, marcas=16, relleno=0), 0.9,
                  niebla, 0.7)
    cor = np.array([3.0, 4.2, -6.5])
    dibujar_trans(lz, cam, linea_suelo(cor[0], cor[2], meta[0] - 2.6, meta[2] + 1.8, 0.6), tex_galon(ORO), 0.7, niebla,
                  0.4)
    for (x, z, g) in ((0.6, -9.0, -30), (6.5, -10.5, 20), (-3.5, -11.0, -10)):
        jugador(lz, cam, x, z, g, niebla=niebla)
    tc = png(os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/nerea/corazon_burbuja.png'))
    dibujar_trans(lz, cam, [billboard(cor, 1.5, cam)], tex_burbuja((255, 140, 170)), 0.8, niebla, 0.6)
    dibujar_trans(lz, cam, [billboard(cor, 0.9, cam)], tc, 1.0, niebla, 0.5)
    golpe = (cor + np.array([0.6, 1.2, -9.0])) / 2 + np.array([0, -0.4, 0])
    dibujar_trans(lz, cam, [billboard(golpe, 0.8, cam, giro=0.3)], chispa(), 1.0, None, 1.0)
    acabar(lz, cam, W, H, 'corazon', 76)
    rotular('corazon', [('SU REMOLINO', 330, 470, 30, ORO), ('¡A GOLPES HASTA AQUÍ!', 250, 600, 26, BLANCO)])


ESCENAS = {'canto': canto, 'naufragio': naufragio, 'marea_alta': marea_alta, 'tira': tira, 'cadenas': cadenas,
           'corazon': corazon}

if __name__ == '__main__':
    solo = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in solo:
        ESCENAS[k]()
        print(k, flush=True)

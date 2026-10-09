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

Segunda ficha (minijuegos, octubre de 2026: "a la gente le gustaron los
minijuegos de los jefes"). La camara va cerca de los jugadores; Nerea queda
grande al fondo:

  pesca         Pesca del Abismo: pozas negras con el borde cian; uno pesca con
                la Cana del Abismo (el corcho brilla: recoge) y otro lanza una
                Perla del Abismo al corazon de Nerea
  canones       Canones del Naufragio: canones de bronce medio enterrados; uno
                mete la bala por la boca, otro prende la mecha; el disparo vuela
                hacia Nerea, que se tambalea
  morenas       Morenas de las Pozas: un anillo de agujeros; las morenas asoman y
                un jugador le da a una; encima, la cuenta de aciertos
  duelo_canto   Duelo de Canto: Nerea canta (notas cian) a un jugador; encima,
                el panel de ritmo de su pantalla (carriles A S D F)

Uso: python nerea_mecanicas_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import itertools, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
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


# ======================================================================
#  Segunda ficha: minijuegos (octubre de 2026)
# ======================================================================
CIAN = (96, 232, 255)
NEGRO = (6, 14, 24)
NARANJA = (255, 150, 50)
# los colores de las cuatro fases (los de la barra del jefe), para los carriles
CARRIL = [(63, 224, 255), (154, 107, 255), (212, 60, 255), (255, 118, 196)]


def _plano(c1, c2, semilla, p=0.7):
    a, b = nm._hex(c1), nm._hex(c2)
    return nm._loseta(semilla, lambda x, y, r: a if r.random() < p else b)


def _bronce(x, y, r):
    """Bronce de barco hundido: vetas doradas y manchas de verdin."""
    if (x * 5 + y * 3) % 13 == 0 and r.random() < 0.7:
        return nm._hex(r.choice(['4fa58a', '62b89a']))
    if y in (0, 15):
        return nm._hex('6a4618')
    return nm._hex(r.choice(['a8782c', 'b8873a', 'c99a48', 'c99a48', 'e0b864']))


def _tabla(x, y, r):
    """Madera podrida del afuste: tablas oscuras con juntas y musgo."""
    if y % 4 == 0:
        return nm._hex('22180f')
    if r.random() < 0.2:
        return nm._hex(r.choice(['3f5a2a', '4c6a30']))
    return nm._hex(r.choice(['4a3322', '553b27', '5e4430', '42301f']))


def _morena(x, y, r):
    """La piel de la morena: verde azulado con manchas oscuras y motas claras."""
    if ((x // 3) + (y // 3) * 2) % 5 == 0 and r.random() < 0.85:
        return nm._hex(r.choice(['15392d', '1b4436']))
    if r.random() < 0.08:
        return nm._hex('9cc870')
    return nm._hex(r.choice(['2e7a62', '358a6e', '2a6e58', '3d957a']))


nm.MAT.update({
    'mj_cana': _plano('9a6a38', '7e5228', 401),
    'mj_mango': _plano('3e2a18', '32220f', 402),
    'mj_hoja': _plano('6eeee2', '4fd8cf', 403),
    'mj_filo': _plano('c8fff8', 'a8f8ee', 404),
    'mj_guarda': _plano('2fb8c8', '24a0ae', 405),
    'mj_bronce': nm._loseta(406, _bronce),
    'mj_tabla': nm._loseta(407, _tabla),
    'mj_hierro': _plano('3a3c42', '2c2e33', 408),
    'mj_bala': _plano('1c1f24', '262a30', 409),
    'mj_morena': nm._loseta(410, _morena),
    'mj_vientre': _plano('a8c46c', '93b25a', 411),
    'mj_aleta': _plano('1d5a48', '174a3b', 412),
    'mj_diente': _plano('f6f3ea', 'e2ddd0', 413),
    'mj_boca': _plano('7a1f30', '5e1424', 414),
    'mj_ojo': nm._loseta(415, nm.emisivo('fff6b0', 'f0b818')),
    'mj_brasa': nm._loseta(416, nm.emisivo('fff2b0', 'ff6a10')),
    'mj_perla': nm._loseta(417, nm.emisivo('ffffff', 'b8f4ff')),
})
nm.EMISIVOS.update({'mj_ojo', 'mj_brasa', 'mj_perla'})


# ----------------------------------------------------------------------
#  Jugadores con pose y lo que llevan en la mano
# ----------------------------------------------------------------------
def buscar(n, nombre):
    if n[0] == nombre:
        return n
    for h in n[4]:
        q = buscar(h, nombre)
        if q is not None:
            return q
    return None


def jugador2(lz, cam, x, z, guinada, pose=None, y=0.0, mano=(), niebla=None, dibujar=True):
    """El jugador de las fichas con pose y, si se dan, nodos en la mano derecha
    (la espada). Devuelve (raiz, pose, matriz) para buscar sus puntos luego;
    con dibujar=False solo los calcula."""
    raiz = ne.jugador()
    buscar(raiz, 'bd')[4].extend(mano)
    pose = pose or {}
    M = vr.T(x, y, z) @ vr.Ry(guinada * vr.D2R) @ vr.T(0, 1.5, 0) @ np.diag([-1 / 16, -1 / 16, 1 / 16, 1])
    if dibujar:
        nm.dibujar(lz, cam, nm.quads(raiz, pose, M), LUCES, AMB, niebla)
    return raiz, pose, M


def punto_en(fig, nombre, punto=(0, 0, 0)):
    """Donde cae en el mundo un punto (pixeles de modelo) del nodo 'nombre'."""
    raiz, pose, M = fig
    hallado = []

    def visitar(n, Mp):
        nom, off, rot, cajas, hijos = n
        ex = pose.get(nom, {})
        r = [rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        p = [off[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        Mn = Mp @ vr.T(*p) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R)
        if nom == nombre:
            hallado.append(Mn)
        for h in hijos:
            visitar(h, Mn)

    visitar(raiz, np.eye(4))
    return (M @ hallado[0] @ np.array([*punto, 1.0]))[:3]


def mano_de(fig, lado='bd'):
    return punto_en(fig, lado, (0, 10, 0))


def nodo_espada(rot=(0, 0, 0)):
    """Una espada de diamante: la hoja hacia -Z, el puno en el origen del nodo."""
    return nm.nodo('espada', (0, 10, -1), rot, [
        ((-0.8, -0.8, -1.0, 1.6, 1.6, 5.0), 'mj_mango'),
        ((-0.9, -0.9, 3.6, 1.8, 1.8, 1.4), 'mj_guarda'),
        ((-3.0, -1.2, -2.4, 6.0, 2.4, 1.4), 'mj_guarda'),
        ((-0.6, -1.4, -16.0, 1.2, 2.8, 13.6), 'mj_hoja'),
        ((-0.5, -0.9, -18.0, 1.0, 1.8, 2.0), 'mj_filo'),
    ])


def guinada_hacia(dx, dz):
    """La guinada (grados) para que algo con el frente en -Z mire hacia (dx, dz)."""
    return math.degrees(math.atan2(-dx, -dz))


# poses del jugador (grados sobre el reposo)
P_CANA = {'bd': {'rot': (-62, 0, 4)}, 'bi': {'rot': (-30, 0, -6)}, 'pi': {'rot': (-10, 0, 0)}, 'pd': {'rot': (12, 0, 0)}}
P_LANZA = {'bd': {'rot': (-150, 0, 8)}, 'bi': {'rot': (36, 0, -12)}, 'pi': {'rot': (-28, 0, 0)}, 'pd': {'rot': (24, 0, 0)},
           'cabeza': {'rot': (-12, 0, 0)}}
P_EMPUJA = {'bd': {'rot': (-96, 0, 12)}, 'bi': {'rot': (-96, 0, -12)}, 'pi': {'rot': (-26, 0, 0)}, 'pd': {'rot': (22, 0, 0)},
            'cuerpo': {'rot': (12, 0, 0)}}
P_MECHA = {'bd': {'rot': (-70, 0, 0)}, 'bi': {'rot': (-20, 0, -14)}, 'pi': {'rot': (-12, 0, 0)}, 'pd': {'rot': (14, 0, 0)}}
P_GOLPE = {'bd': {'rot': (-125, -20, 0)}, 'bi': {'rot': (30, 0, -10)}, 'pi': {'rot': (-28, 0, 0)}, 'pd': {'rot': (24, 0, 0)}}
P_CORRE = {'bi': {'rot': (40, 0, 0)}, 'bd': {'rot': (-50, 0, 0)}, 'pi': {'rot': (-40, 0, 0)}, 'pd': {'rot': (38, 0, 0)}}
P_QUIETO = {'bi': {'rot': (-12, 0, 0)}, 'bd': {'rot': (14, 0, 0)}}
P_ESCUCHA = {'cabeza': {'rot': (-16, 0, 0)}, 'bi': {'rot': (-10, 0, -10)}, 'bd': {'rot': (-10, 0, 10)}}


# ----------------------------------------------------------------------
#  Geometria suelta en el mundo (cajas orientadas, palos, sprites)
# ----------------------------------------------------------------------
def caja_or(c, ex, ey, ez, mat):
    """Una caja orientada en el mundo: el centro y los tres semiejes (vectores);
    los quads van en mosaico (1 bloque = 1 loseta de 16 px)."""
    c = np.asarray(c, float)
    E = [np.asarray(e, float) for e in (ex, ey, ez)]
    out = []
    for a in range(3):
        b, d = [i for i in range(3) if i != a]
        La, Lb = 2 * np.linalg.norm(E[b]), 2 * np.linalg.norm(E[d])
        for s in (-1, 1):
            f = c + s * E[a]
            P = [f - E[b] - E[d], f + E[b] - E[d], f + E[b] + E[d], f - E[b] + E[d]]
            out.append(([tuple(q) for q in P], [(0, 0), (La, 0), (La, Lb), (0, Lb)], mat))
    return out


def ejes(d, arriba=(0.0, 1.0, 0.0)):
    """Tres ejes unitarios con el tercero en d: (lado, arriba, d)."""
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    lado = np.cross(arriba, d)
    if np.linalg.norm(lado) < 1e-6:
        lado = np.array([1.0, 0, 0])
    lado = lado / np.linalg.norm(lado)
    return lado, np.cross(d, lado), d


def palo(a, b, grueso, mat):
    """Una barra de seccion cuadrada de a a b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    lado, up, d = ejes(b - a)
    return caja_or((a + b) / 2, lado * grueso, up * grueso, d * np.linalg.norm(b - a) / 2, mat)


def dibujar_qs(lz, cam, qs, niebla, brillo=1.4):
    nm.dibujar(lz, cam, qs, LUCES, AMB, niebla, brillo)


def sprite(lz, cam, p, tam, tex, niebla=None, luz=1.0, giro=0.0, tapa_brillo=False):
    """Un billboard opaco (recortado) que tapa en profundidad, como una bala;
    con tapa_brillo borra el resplandor que ya hubiera debajo (el corcho)."""
    P, UV = billboard(p, tam, cam, giro)
    antes = lz.z.copy() if tapa_brillo else None
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3) * luz, None, niebla)
    if tapa_brillo:
        lz.emis[lz.z != antes] = 0


def humo_en(lz, cam, p, tam, tex, k=0.9, niebla=None, giro=0.0):
    """Una bocanada translucida que ademas apaga el resplandor que tenga detras
    (si no, el bloom del fogonazo se la come)."""
    antes = lz.color.copy()
    dibujar_trans(lz, cam, [billboard(p, tam, cam, giro=giro)], tex, k, niebla)
    cambio = np.any(lz.color != antes, axis=2)
    lz.emis[cambio] *= 0.25


def luz_en(lz, cam, p, tam, color, k=1.0, dura=1.6):
    """Un resplandor aditivo redondo en p."""
    P, UV = billboard(p, tam, cam)
    tex = tex_luz(color, dura=dura)
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), None, None, aditivo=True, brillo=k)


def punto_nerea(p, x, z, guinada, hueso, local=(0, 0, 0)):
    """Un punto (pixeles de modelo) de un hueso de la Nerea dibujada en (x, z)."""
    nr.usar('despues')
    M = vr.entidad_a_mundo(x, 0, z, guinada, nr.ESCALA['despues'])
    return (M @ nj.matrices(p)[hueso] @ np.array([*local, 1.0]))[:3]


# ----------------------------------------------------------------------
#  Texturas de la segunda ficha (RGBA uint8)
# ----------------------------------------------------------------------
_TEX = {}


def _disco(n):
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    return np.hypot(xx - n / 2, yy - n / 2) / (n / 2), xx, yy


def tex_luz(color, n=96, dura=1.6):
    """Un resplandor redondo: blanco en el centro y el color hacia el borde."""
    clave = ('luz', color, n, dura)
    if clave not in _TEX:
        d, _, _ = _disco(n)
        a = np.clip(1 - d, 0, 1) ** dura
        k = np.clip(1 - d / 0.3, 0, 1)[..., None]
        t = np.zeros((n, n, 4), np.uint8)
        t[..., :3] = (np.array(color, float) * (1 - k) + 255 * k).clip(0, 255)
        t[..., 3] = a * 255
        _TEX[clave] = t
    return _TEX[clave]


def tex_halo(color, n=96, r0=0.45):
    """Un resplandor en anillo: hueco en el centro (lo de dentro se sigue viendo)."""
    clave = ('halo', color, n, r0)
    if clave not in _TEX:
        d, _, _ = _disco(n)
        a = np.where(d < r0, (d / r0) ** 2, np.clip(1 - (d - r0) / (1 - r0), 0, 1) ** 1.4)
        t = np.zeros((n, n, 4), np.uint8)
        t[..., :3] = color
        t[..., 3] = (a * 255).clip(0, 255)
        _TEX[clave] = t
    return _TEX[clave]


def tex_poza(color, n=160):
    """Una poza del abismo vista desde arriba: negra por dentro (algo mas clara
    hacia el borde) y un borde de luz del color, con su halo."""
    d, xx, yy = _disco(n)
    t = np.zeros((n, n, 4), np.uint8)
    k = (np.clip(d / 0.8, 0, 1) ** 3)[..., None]
    t[..., :3] = np.array([1, 3, 8], float) * (1 - k) + np.array([10, 46, 74], float) * k
    t[..., 3] = np.where(d < 0.8, 253, 0)
    # remolinos tenues dentro
    a = np.arctan2(yy - n / 2, xx - n / 2)
    s = (a * 2 / (2 * math.pi) + np.log(d + 1e-6) * 1.3) % 1.0
    m = (d < 0.7) & (d > 0.15) & (s < 0.08)
    t[m] = (*R.mezclar(color, (0, 0, 0), 0.65), 253)
    t[(d >= 0.8) & (d < 0.9)] = (*R.mezclar(color, (255, 255, 255), 0.35), 255)
    halo = (d >= 0.9) & (d < 1.0)
    t[halo, :3] = color
    t[halo, 3] = ((1 - (d[halo] - 0.9) / 0.1) * 210).astype(np.uint8)
    return t


def tex_agujero(n=160):
    """Un agujero de agua en la arena: agua oscura, el borde de espuma rota."""
    d, xx, yy = _disco(n)
    r = np.random.RandomState(4)
    t = np.zeros((n, n, 4), np.uint8)
    k = (np.clip(d / 0.82, 0, 1) ** 2)[..., None]
    t[..., :3] = np.array([4, 18, 30], float) * (1 - k) + np.array([30, 96, 120], float) * k
    t[..., 3] = np.where(d < 0.84, 250, 0)
    a = np.arctan2(yy - n / 2, xx - n / 2)
    rot = 0.5 + 0.5 * np.sin(a * 9 + 1.3) * np.sin(a * 4)
    espuma = (d > 0.74) & (d < 0.84 + 0.12 * rot) & (r.rand(n, n) < 0.85)
    t[espuma] = (236, 252, 255, 240)
    return t


def tex_anillo(color, grueso=0.12, n=128, alfa=235):
    d, _, _ = _disco(n)
    t = np.zeros((n, n, 4), np.uint8)
    t[(d > 1 - grueso) & (d < 1)] = (*color, alfa)
    return t


def tex_corcho():
    """El corcho de la cana (el de Minecraft): rojo arriba, blanco abajo."""
    n = 16
    t = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            d = math.hypot(x + 0.5 - 8, y + 0.5 - 8)
            if d < 6.6:
                t[y, x] = (40, 12, 12, 255)
            if d < 5.6:
                t[y, x] = (226, 44, 40, 255) if y < 8 else (246, 246, 240, 255)
    t[4:6, 5:7] = (255, 190, 180, 255)
    return t


def tex_bala(n=40):
    """Una bala de canon: hierro negro, la luz de arriba y un brillo."""
    d, xx, yy = _disco(n)
    t = np.zeros((n, n, 4), np.uint8)
    nx, ny = (xx - n / 2) / (n / 2), (yy - n / 2) / (n / 2)
    nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1))
    luz = np.clip(-0.45 * nx - 0.65 * ny + 0.6 * nz, 0, 1)
    borde = np.clip((d - 0.7) / 0.3, 0, 1) * np.clip(nx * 0.6 + ny * 0.5 + 0.4, 0, 1)
    col = np.array([22, 25, 31], float)[None, None] * (0.6 + 1.6 * luz[..., None])
    col += np.array([60, 150, 170], float)[None, None] * borde[..., None] * 0.7
    spec = np.clip(1 - np.hypot(nx + 0.38, ny + 0.42) / 0.22, 0, 1) ** 1.5
    col += 200 * spec[..., None]
    t[..., :3] = col.clip(0, 255)
    t[..., 3] = np.where(d < 1, 255, 0)
    return t


def nota_borde(color, n=48):
    """La nota del Canto con un borde oscuro (para que se lea sobre el haz)."""
    base = nota(color, n)
    a = Image.fromarray(base[..., 3]).filter(ImageFilter.MaxFilter(7))
    t = np.zeros((n, n, 4), np.uint8)
    t[np.array(a) > 0] = (*NEGRO, 255)
    t[base[..., 3] > 0] = base[base[..., 3] > 0]
    return t


def tex_estrella(color, n=64, puntas=8):
    """Un fogonazo: estrella de puntas del color con el centro blanco."""
    d, xx, yy = _disco(n)
    a = np.arctan2(yy - n / 2, xx - n / 2)
    radio = 0.45 + 0.55 * np.abs(np.cos(a * puntas / 2)) ** 6
    v = np.clip(1 - d / radio, 0, 1)
    t = np.zeros((n, n, 4), np.uint8)
    k = np.clip(1 - d / 0.35, 0, 1)[..., None]
    t[..., :3] = (np.array(color, float) * (1 - k) + 255 * k).clip(0, 255)
    t[..., 3] = (np.clip(v * 1.6, 0, 1) * 255)
    return t


def tex_humo(semilla, n=64, color=(226, 236, 240)):
    """Una bocanada de humo blando."""
    d, xx, yy = _disco(n)
    r = np.random.RandomState(semilla)
    g = Image.fromarray((r.rand(6, 6) * 255).astype(np.uint8)).resize((n, n), Image.BICUBIC)
    ruido = np.array(g).astype(float) / 255
    a = np.clip(1 - d, 0, 1) ** 1.1 * (0.55 + 0.45 * ruido)
    t = np.zeros((n, n, 4), np.uint8)
    t[..., :3] = np.array(color, float) * (0.82 + 0.18 * ruido[..., None])
    t[..., 3] = (a * 235).clip(0, 255)
    return t


# ----------------------------------------------------------------------
#  Rotulos sobre la foto (pixeles de 1600 de ancho)
# ----------------------------------------------------------------------
def componer2(lz, cam, W, H, semilla, rayos=1.0):
    horiz = cam.proyectar(np.array([cam.ojo[0] + cam.f[0] * 300, 0.0, cam.ojo[2] + cam.f[2] * 300]))[1] / SS
    return ne.componer(lz, W, H, horiz, semilla, rayos).convert('RGBA')


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=90)


def pantalla(cam, p):
    sx, sy, z = cam.proyectar(p)
    return sx / SS, sy / SS, z


def texto_sombra(img, xy, texto, f, color):
    d = ImageDraw.Draw(img)
    tx, ty = xy
    for o in ((3, 3), (2, 2), (-1, 1), (1, -1)):
        d.text((tx + o[0], ty + o[1]), texto, font=f, fill=(*NEGRO, 255))
    d.text((tx, ty), texto, font=f, fill=(*color, 255))


def rotulo(img, cam, p, texto, dx, dy, tam=30, color=BLANCO, linea=True, centro=False):
    """Un rotulo en mayusculas junto al punto p del mundo, desplazado (dx, dy),
    con su sombra y, si se pide, una linea fina hasta el punto."""
    sx, sy, z = pantalla(cam, p)
    if z < 0.5:
        return
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
        dc.line([(sx, sy), (ax, ay)], fill=(*NEGRO, 170), width=5)
        dc.line([(sx, sy), (ax, ay)], fill=(*color, 235), width=2)
        dc.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=(*color, 255))
        img.alpha_composite(capa)
    texto_sombra(img, (tx, ty), texto, f, color)
    return tx, ty, w


def cifra(img, xy, texto, tam, color, centro=True):
    """Un texto grande que brilla (la cuenta), con su halo y su sombra."""
    x, y = xy
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', tam)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    w = d.textlength(texto, font=f)
    if centro:
        x -= w / 2
    d.text((x, y), texto, font=f, fill=(*color, 255))
    halo = capa.filter(ImageFilter.GaussianBlur(tam / 7))
    img.alpha_composite(halo)
    img.alpha_composite(halo)
    sombra = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).text((x + 3, y + 3), texto, font=f, fill=(*NEGRO, 255))
    img.alpha_composite(sombra)
    img.alpha_composite(capa)
    return x, w


# ----------------------------------------------------------------------
#  La morena (Morenas de las Pozas; y la que muerde al que falla en la Pesca)
# ----------------------------------------------------------------------
def morena(base, hacia, alto=2.3, adelante=1.0, abre=44, escala=1.0, onda=1.0):
    """Una morena que asoma de un agujero en base (x, z): el cuerpo sube del
    agua en S y se curva hacia 'hacia' (x, z), con la boca abierta y los
    dientes. Devuelve (quads, punta de la boca)."""
    bx, bz = base
    h = np.array([hacia[0] - bx, 0.0, hacia[1] - bz])
    h /= np.linalg.norm(h)
    up = np.array([0.0, 1.0, 0.0])
    lado = np.cross(h, up)
    s = escala

    def pos(t):
        a = t * math.pi / 2
        return (np.array([bx, -0.5, bz]) + up * (alto * math.sin(a)) + h * (adelante * (1 - math.cos(a)))
                + lado * (0.22 * onda * s * math.sin(2 * math.pi * t)))

    n = 10
    pts = [pos(i / n) for i in range(n + 1)]
    qs = []
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        d = b - a
        L = np.linalg.norm(d)
        d /= L
        dors = np.cross(lado, d)
        dors /= np.linalg.norm(dors)
        g = s * (1.05 - 0.12 * i / n)
        c = (a + b) / 2
        qs += caja_or(c, lado * 0.17 * g, dors * 0.24 * g, d * L * 0.62, 'mj_morena')
        qs += caja_or(c - dors * 0.2 * g, lado * 0.135 * g, dors * 0.06 * g, d * L * 0.62, 'mj_vientre')
        qs += caja_or(c + dors * 0.29 * g, lado * 0.03 * g, dors * 0.07 * g, d * L * 0.55, 'mj_aleta')
    top = pts[-1]
    # la cabeza: el craneo y las dos mandibulas abiertas, con dientes
    qs += caja_or(top + h * 0.1 * s + up * 0.02 * s, lado * 0.2 * s, up * 0.27 * s, h * 0.2 * s, 'mj_morena')
    gozne = top + h * 0.26 * s
    ang = math.radians(abre / 2)
    for sg in (1, -1):
        jd = h * math.cos(ang) + up * math.sin(ang) * sg
        jn = up * math.cos(ang) - h * math.sin(ang) * sg
        L = 0.66 * s
        qs += caja_or(gozne + jd * L / 2 + jn * 0.1 * s * sg, lado * 0.19 * s, jn * 0.11 * s, jd * L / 2,
                      'mj_morena' if sg > 0 else 'mj_vientre')
        for k in range(4):
            for e in (-1, 1):
                c = gozne + jd * (0.16 + 0.14 * k) * s + lado * e * 0.13 * s - jn * sg * 0.07 * s
                qs += caja_or(c, lado * 0.03 * s, jn * 0.07 * s, jd * 0.03 * s, 'mj_diente')
    qs += caja_or(gozne + h * 0.06 * s, lado * 0.16 * s, up * 0.16 * s, h * 0.08 * s, 'mj_boca')
    for e in (-1, 1):
        qs += caja_or(top + h * 0.2 * s + up * 0.2 * s + lado * e * 0.2 * s, lado * 0.03 * s, up * 0.055 * s,
                      h * 0.055 * s, 'mj_ojo')
    return qs, gozne + h * 0.6 * s


def asoma(lz, cam, base, hacia, niebla, **kw):
    """Una morena entera: el cuerpo, la espuma donde sale y unas burbujas."""
    qs, boca = morena(base, hacia, **kw)
    dibujar_qs(lz, cam, qs, niebla)
    dibujar_trans(lz, cam, suelo_cuad(base[0], base[1], 0.75, y=0.09), tex_anillo(R.ESPUMA, 0.3), 0.9, niebla, 0.3)
    tb = tex_burbuja(R.ESPUMA)
    for k in range(5):
        q = (base[0] + 0.5 * math.cos(k * 1.9), 0.3 + 0.35 * k, base[1] + 0.5 * math.sin(k * 1.9))
        dibujar_trans(lz, cam, [billboard(q, 0.07 + 0.02 * (k % 3), cam)], tb, 0.85, niebla, 0.3)
    return boca


# ----------------------------------------------------------------------
#  7. Pesca del Abismo
#
#  Nerea ha clavado el tridente; por la arena, pozas negras con el borde cian.
#  Uno pesca con la Cana del Abismo: el hilo tenso y el corcho brillando (es el
#  momento de recoger). Otro lanza una Perla del Abismo a su corazon, que
#  brilla en el pecho.
# ----------------------------------------------------------------------
def pesca(W=1600, H=900, fase=2):
    cam, lz, niebla = lienzo((1.5, 6.8, -19.5), (0.0, 3.6, 2.0), W, H, fov=54, cerca=22, lejos=50)
    nx, nz, ng = 0.0, 15.0, -6
    p = pose('GEISER', 1.15, fase=fase)
    nerea(lz, cam, 'despues', nx, nz, ng, p=p, fase=fase, niebla=niebla, luces=LUCES, amb=AMB, brillo=1.5)
    cor = punto_nerea(p, nx, nz, ng, 'corazon_%d' % fase)
    # las pozas
    tp = tex_poza(CIAN)
    pozas = [(1.6, -7.4), (-6.5, -2.0), (7.5, 1.0), (-2.0, 4.0), (4.0, 8.5)]
    for (x, z) in pozas:
        dibujar_trans(lz, cam, suelo_cuad(x, z, 1.35, y=0.07), tp, 0.96, niebla, 0.7)
    # el que fallo: le sale una morena de la poza y le muerde
    mx, mz = 10.8, 2.2
    jugador2(lz, cam, mx, mz, guinada_hacia(pozas[2][0] - mx, pozas[2][1] - mz),
             {'bi': {'rot': (-100, 0, -30)}, 'bd': {'rot': (-90, 0, 30)}, 'cabeza': {'rot': (10, 0, 0)}}, niebla=niebla)
    mordisco = asoma(lz, cam, pozas[2], (mx, mz), niebla, alto=2.2, adelante=1.1, escala=1.1)
    # el pescador: cana, hilo tenso y el corcho que brilla
    fx, fz = 5.6, -8.6
    pz = pozas[0]
    fig = jugador2(lz, cam, fx, fz, guinada_hacia(pz[0] - fx, pz[1] - fz), P_CANA, niebla=niebla)
    mano = mano_de(fig)
    rumbo = np.array([pz[0] - fx, 0, pz[1] - fz])
    rumbo /= np.linalg.norm(rumbo)
    punta = mano + rumbo * 1.5 + np.array([0, 1.7, 0])
    dibujar_qs(lz, cam, palo(mano - (punta - mano) * 0.08, mano + (punta - mano) * 0.1, 0.07, 'mj_mango'), niebla)
    dibujar_qs(lz, cam, palo(mano, punta, 0.04, 'mj_cana'), niebla)
    corcho = np.array([pz[0], 0.16, pz[1]])
    dibujar_trans(lz, cam, cinta3d([punta, corcho], 0.012, cam), tex_plano((235, 240, 240)), 1.0, niebla, 0.2)
    for r_, k in ((0.5, 0.8), (0.9, 0.45)):
        dibujar_trans(lz, cam, suelo_cuad(corcho[0], corcho[2], r_, y=0.09), tex_anillo((220, 255, 255), 0.1), k,
                      niebla, 0.25)
    P, UV = billboard(corcho + np.array([0, 0.36, 0]), 0.75, cam)
    for tri in ((0, 1, 2), (0, 2, 3)):
        lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex_halo(ORO, r0=0.6), np.ones(3), None, None,
                     aditivo=True, brillo=0.35)
    sprite(lz, cam, corcho + np.array([0, 0.36, 0]), 0.3, tex_corcho(), None, 1.1, tapa_brillo=True)
    tb = tex_burbuja(R.ESPUMA)
    for k in range(7):
        a = k * 0.9
        q = corcho + np.array([0.35 * math.cos(a), 0.25 + 0.12 * (k % 3), 0.35 * math.sin(a)])
        dibujar_trans(lz, cam, [billboard(q, 0.05, cam)], tb, 0.9, niebla, 0.4)
    # otro pescando al fondo, con el hilo flojo
    gx, gz = -9.0, -4.2
    pz2 = pozas[1]
    fig2 = jugador2(lz, cam, gx, gz, guinada_hacia(pz2[0] - gx, pz2[1] - gz), P_CANA, niebla=niebla)
    m2 = mano_de(fig2)
    r2 = np.array([pz2[0] - gx, 0, pz2[1] - gz])
    r2 /= np.linalg.norm(r2)
    pu2 = m2 + r2 * 1.5 + np.array([0, 1.6, 0])
    dibujar_qs(lz, cam, palo(m2, pu2, 0.04, 'mj_cana'), niebla)
    c2 = np.array([pz2[0], 0.12, pz2[1]])
    dibujar_trans(lz, cam, cinta3d(curva(pu2, c2, -0.5, 8), 0.012, cam), tex_plano((235, 240, 240)), 1.0, niebla)
    sprite(lz, cam, c2 + np.array([0, 0.06, 0]), 0.16, tex_corcho(), niebla)
    # el que lanza la perla al corazon
    lx, lz_ = -3.2, -9.8
    fig3 = jugador2(lz, cam, lx, lz_, guinada_hacia(cor[0] - lx, cor[2] - lz_), P_LANZA, niebla=niebla)
    m3 = mano_de(fig3)
    arco = curva(m3, cor, 1.6, 30)
    ip = 8
    perla = np.array(arco[ip])
    for i in range(1, ip):
        k = (i - 1) / (ip - 1)
        dibujar_trans(lz, cam, cinta3d(arco[i:i + 2], 0.03 + 0.07 * k, cam), tex_haz((200, 245, 255)), 0.3 + 0.5 * k,
                      niebla, 0.3 + 0.7 * k)
    luz_en(lz, cam, perla, 1.1, (170, 240, 255), 1.3)
    dibujar_qs(lz, cam, caja_or(perla, cam.r * 0.14, cam.u * 0.14, cam.f * 0.14, 'mj_perla'), None, 1.3)
    # el corazon: brilla, con la diana alrededor
    luz_en(lz, cam, cor, 4.0, (255, 70, 130), 1.0)
    dibujar_trans(lz, cam, [billboard(cor, 1.7, cam)], tex_anillo((255, 200, 220), 0.1), 0.9, None, 0.8)
    img = componer2(lz, cam, W, H, 91)
    rotulo(img, cam, corcho + np.array([-0.5, 0.42, 0]), '¡RECOGE!', 60, -70, 50, ORO)
    rotulo(img, cam, punta, 'CAÑA DEL ABISMO', 40, -75, 30, BLANCO)
    rotulo(img, cam, perla, 'PERLA DEL ABISMO', 80, 40, 32, (190, 245, 255))
    rotulo(img, cam, cor, 'SU CORAZÓN  1/3', 150, -60, 34, (255, 150, 190))
    rotulo(img, cam, mordisco, 'SI FALLAS: ¡MORENA!', -90, 30, 28, (255, 150, 150))
    rotulo(img, cam, np.array([pozas[4][0], 0.1, pozas[4][1]]), 'POZAS DEL ABISMO', -260, -150, 28, CIAN)
    guardar(img, 'pesca')


# ----------------------------------------------------------------------
#  8. Canones del Naufragio
#
#  Del suelo han salido canones de un barco hundido (bronce con verdin, el
#  afuste de madera podrida medio enterrado) y una pila de balas. Uno mete la
#  bala por la boca de un canon; otro prende la mecha del suyo: el disparo sale
#  entre humo y burbujas y vuela a su pecho, que se tambalea. Al fondo, su
#  Rompeolas va a por el tercer canon.
# ----------------------------------------------------------------------
def canon(base, hacia, elev=12.0, hundido=0.3):
    """Un canon de barco hundido en base (x, z), apuntando hacia (x, z).
    Devuelve (quads, boca, oido, eje del tubo, horizontal)."""
    bx, bz = base
    d = np.array([hacia[0] - bx, 0.0, hacia[1] - bz])
    d /= np.linalg.norm(d)
    up = np.array([0.0, 1.0, 0.0])
    lado = np.cross(up, d)
    c0 = np.array([bx, -hundido, bz])
    qs = []
    # el afuste: la cama, las gualderas escalonadas y las ruedas
    qs += caja_or(c0 + up * 0.35, lado * 0.62, up * 0.22, d * 1.15, 'mj_tabla')
    for e in (-1, 1):
        for (dz, alto) in ((-0.8, 0.62), (-0.3, 0.78), (0.25, 0.62), (0.75, 0.42)):
            qs += caja_or(c0 + lado * e * 0.5 + d * dz + up * (0.5 + alto / 2), lado * 0.1, up * alto / 2, d * 0.26,
                          'mj_tabla')
        for dz in (-0.75, 0.75):
            qs += caja_or(c0 + lado * e * 0.72 + d * dz + up * 0.32, lado * 0.09, up * 0.32, d * 0.32, 'mj_tabla')
            qs += caja_or(c0 + lado * e * 0.82 + d * dz + up * 0.32, lado * 0.02, up * 0.12, d * 0.12, 'mj_hierro')
    # el tubo de bronce
    a = math.radians(elev)
    t = d * math.cos(a) + up * math.sin(a)
    n = up * math.cos(a) - d * math.sin(a)
    eje0 = c0 + up * 1.08 - d * 0.95

    def seg(u0, u1, r, mat='mj_bronce'):
        return caja_or(eje0 + t * (u0 + u1) / 2, lado * r, n * r, t * (u1 - u0) / 2, mat)

    qs += seg(-0.3, -0.14, 0.1) + seg(-0.14, 0.0, 0.22) + seg(0.0, 0.75, 0.37) + seg(0.75, 0.86, 0.4)
    qs += seg(0.86, 2.3, 0.31) + seg(1.5, 1.58, 0.34) + seg(2.3, 2.52, 0.37)
    qs += caja_or(eje0 + t * 0.98, lado * 0.52, n * 0.1, t * 0.1, 'mj_bronce')
    boca = eje0 + t * 2.52
    qs += caja_or(boca + t * 0.006, lado * 0.2, n * 0.2, t * 0.01, 'mj_bala')
    oido = eje0 + t * 0.3 + n * 0.37
    qs += caja_or(oido, lado * 0.05, n * 0.025, t * 0.05, 'mj_bala')
    # arena amontonada alrededor (sale del suelo)
    r = np.random.RandomState(int(abs(bx * 7 + bz * 13)) % 1000)
    for k in range(9):
        ang = k / 9 * 2 * math.pi + r.uniform(-0.2, 0.2)
        rr = r.uniform(1.1, 1.6)
        p = np.array([bx + math.cos(ang) * rr * 0.8, 0.06, bz + math.sin(ang) * rr * 1.1])
        qs += caja_or(p, np.array([r.uniform(0.25, 0.45), 0, 0]), up * r.uniform(0.05, 0.14), np.array([0, 0, 0.3]),
                      'arena')
    return qs, boca, oido, t, d


def canones(W=1600, H=900, fase=3):
    cam, lz, niebla = lienzo((0.8, 6.2, -19.0), (0.0, 4.0, 3.0), W, H, fov=54, cerca=22, lejos=50)
    nx, nz, ng = 1.5, 16.0, -4
    p = pose('TAMBALEO', 0.14, fase=fase)
    nerea(lz, cam, 'despues', nx, nz, ng, p=p, fase=fase, niebla=niebla, luces=LUCES, amb=AMB, brillo=1.5)
    pecho = punto_nerea(p, nx, nz, ng, 'torso', (0, -17, -9))
    # tercer canon, al fondo, y la ola del Rompeolas que va a por el
    qc, bc, _, _, _ = canon((-9.0, 4.5), (pecho[0], pecho[2]), elev=14)
    dibujar_qs(lz, cam, qc, niebla)
    # la pila de balas
    tb_ = tex_bala()
    pila = (0.6, -8.4)
    for capa, (nfil, y) in enumerate(((3, 0.2), (2, 0.52), (1, 0.84))):
        for i in range(nfil):
            for j in range(nfil):
                q = (pila[0] + (i - (nfil - 1) / 2) * 0.42, y, pila[1] + (j - (nfil - 1) / 2) * 0.42)
                sprite(lz, cam, q, 0.22, tb_, niebla)
    # canon A: el artillero prende la mecha y sale el disparo
    qa, ba, oa, ta, da = canon((4.6, -6.4), (pecho[0], pecho[2]))
    dibujar_qs(lz, cam, qa, niebla)
    lado_a = np.cross([0.0, 1.0, 0.0], da)
    gpos = np.array([4.6, 0, -6.4]) + lado_a * 1.35 - da * 0.75
    fig_g = jugador2(lz, cam, gpos[0], gpos[2], guinada_hacia(-lado_a[0] + 0.4 * da[0], -lado_a[2] + 0.4 * da[2]),
                     P_MECHA, niebla=niebla)
    mg = mano_de(fig_g)
    punta_m = oa + np.array([0, 0.12, 0])
    dibujar_qs(lz, cam, palo(mg - (punta_m - mg) * 0.15, punta_m, 0.045, 'mj_mango'), niebla)
    dibujar_qs(lz, cam, caja_or(punta_m, cam.r * 0.06, cam.u * 0.06, cam.f * 0.06, 'mj_brasa'), niebla)
    luz_en(lz, cam, punta_m, 0.9, NARANJA, 1.1)
    for k in range(6):
        ang = k * 1.05
        q = punta_m + np.array([0.25 * math.cos(ang), 0.15 + 0.12 * (k % 3), 0.25 * math.sin(ang)])
        dibujar_trans(lz, cam, [billboard(q, 0.09, cam, giro=ang)], chispa(), 1.0, None, 0.9)
    # el disparo: fogonazo, humo y burbujas en la boca; la bala vuela a su pecho
    luz_en(lz, cam, ba + ta * 0.3, 1.0, (255, 200, 120), 0.7)
    humo = [(1.9, 0.1, 0.9, 1.5), (1.3, -0.5, 0.6, 1.2), (1.2, 0.7, 0.8, 1.1), (0.7, 0.0, 0.4, 0.9), (2.5, 0.4, 1.4, 1.3)]
    humo.sort(key=lambda h: -cam.proyectar(ba + ta * h[0])[2])
    for k, (dl, ds, dy, tam) in enumerate(humo):
        q = ba + ta * dl + lado_a * ds + np.array([0, dy, 0])
        humo_en(lz, cam, q, tam, tex_humo(30 + k, color=(250, 252, 252)), 0.97, niebla, giro=k)
    dibujar_trans(lz, cam, [billboard(ba + ta * 0.25 + np.array([0, 0.1, 0]), 0.75, cam, giro=0.4)],
                  tex_estrella((255, 190, 90)), 1.0, None, 1.0)
    for k in range(18):
        ang = k * 2.4
        q = ba + ta * (0.6 + 0.12 * k) + lado_a * 0.7 * math.cos(ang) + np.array([0, 0.5 + 0.6 * math.sin(ang * 1.3), 0])
        dibujar_trans(lz, cam, [billboard(q, 0.08 + 0.05 * (k % 4), cam)], tex_burbuja(R.ESPUMA), 0.9, niebla, 0.35)
    tbur = tex_burbuja(R.ESPUMA)
    camino = [ba + (pecho - ba) * k + np.array([0, 1.2 * math.sin(math.pi * k), 0]) for k in np.linspace(0, 1, 40)]
    ib = 8
    bala = camino[ib]
    for i in range(3, ib):
        k = (i - 3) / (ib - 3)
        dibujar_trans(lz, cam, cinta3d(camino[i:i + 2], 0.03 + 0.1 * k, cam), tex_haz((220, 240, 255)), 0.2 + 0.4 * k,
                      niebla, 0.1 + 0.2 * k)
        for j in range(2):
            q = camino[i] + np.array([0.25 * math.sin(i * 2.3 + j), 0.25 * math.cos(i * 1.7 + j * 2), 0])
            dibujar_trans(lz, cam, [billboard(q, 0.07 + 0.03 * ((i + j) % 3), cam)], tbur, 0.85, niebla, 0.3)
    sprite(lz, cam, bala, 0.32, tb_, None, 1.15)
    # las siguientes balas: el camino que seguiria (punteado tenue)
    for i in range(ib + 3, 37, 3):
        dibujar_trans(lz, cam, [billboard(camino[i], 0.07, cam)], tex_luz((220, 240, 255)), 0.6, None, 0.2)
    # el impacto en el pecho
    luz_en(lz, cam, pecho, 4.5, (255, 214, 150), 1.1)
    dibujar_trans(lz, cam, [billboard(pecho, 1.6, cam, giro=0.3)], chispa(), 1.0, None, 1.0)
    for k in range(10):
        ang = k * 0.63
        q = pecho + np.array([1.4 * math.cos(ang), 1.4 * math.sin(ang), -0.8])
        dibujar_trans(lz, cam, [billboard(q, 0.18, cam)], tbur, 0.85, None, 0.4)
    # canon B: el cargador mete la bala por la boca
    qb, bb, ob, tb2, db = canon((-3.6, -6.6), (-3.6 - 1.0, -6.6 + 0.35))
    dibujar_qs(lz, cam, qb, niebla)
    bola = bb + tb2 * 0.32 + np.array([0, 0.3, 0])
    g_c = guinada_hacia(-db[0], -db[2])
    prueba = jugador2(lz, cam, 0, 0, g_c, P_EMPUJA, dibujar=False)
    manos = (mano_de(prueba, 'bd') + mano_de(prueba, 'bi')) / 2 - db * 0.24
    cpos = bola - manos
    jugador2(lz, cam, cpos[0], cpos[2], g_c, P_EMPUJA, y=cpos[1], niebla=niebla)
    sprite(lz, cam, bola, 0.3, tb_, niebla, 1.15)
    img = componer2(lz, cam, W, H, 93)
    rotulo(img, cam, cpos + np.array([0, 1.95, 0]), 'CARGADOR: METE LA BALA', 40, -90, 34, BLANCO)
    rotulo(img, cam, gpos + np.array([0, 2.0, 0]), 'ARTILLERO: DISPARA', -40, -110, 34, BLANCO)
    rotulo(img, cam, punta_m, 'MECHA', 70, 30, 28, NARANJA)
    rotulo(img, cam, np.array([pila[0], 1.0, pila[1]]), 'BALAS', 40, 60, 28, BLANCO)
    rotulo(img, cam, pecho, '−3 % · ¡SE TAMBALEA!', 170, -60, 36, ORO)
    rotulo(img, cam, pecho, 'TRES SEGUIDAS: ATURDIDA', 170, -10, 26, BLANCO, linea=False)
    guardar(img, 'canones')


# ----------------------------------------------------------------------
#  9. Morenas de las Pozas
#
#  Ocho agujeros de agua en anillo alrededor de Nerea. Las morenas asoman de
#  una en una (o de dos en dos) y hay que darles antes de que se escondan: uno
#  acierta (chispas), otro corre a la siguiente; encima, la cuenta 12/20.
# ----------------------------------------------------------------------
def morenas(W=1600, H=900, fase=2):
    cam, lz, niebla = lienzo((1.6, 5.0, -5.0), (0.0, 4.7, 10.0), W, H, fov=60, cerca=20, lejos=46)
    nx, nz = 0.0, 15.5
    p = pose('BURBUJAS', 0.25, fase=fase)
    nerea(lz, cam, 'despues', nx, nz, 0, p=p, fase=fase, niebla=niebla, luces=LUCES, amb=AMB, brillo=1.5)
    ta = tex_agujero()
    agujeros = []
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        agujeros.append((nx + 11.0 * math.cos(a), nz + 11.0 * math.sin(a)))
    for (x, z) in agujeros:
        dibujar_trans(lz, cam, suelo_cuad(x, z, 1.25, y=0.07), ta, 0.95, niebla, 0.1)
    # la que se lleva el golpe (delante, a la derecha)
    h1 = agujeros[5]
    p1 = (h1[0] + 2.3, h1[1] - 0.9)
    boca1 = asoma(lz, cam, h1, p1, niebla, alto=2.1, adelante=0.9, abre=50, escala=1.2)
    fig1 = jugador2(lz, cam, p1[0], p1[1], guinada_hacia(boca1[0] - p1[0], boca1[2] - p1[1]), P_GOLPE,
                    mano=[nodo_espada((0, 0, 0))], niebla=niebla)
    golpe = (boca1 + mano_de(fig1)) / 2 + np.array([0, 0.35, 0])
    dibujar_trans(lz, cam, [billboard(golpe, 1.2, cam, giro=0.2)], tex_estrella((255, 240, 180)), 0.9, None, 0.6)
    dibujar_trans(lz, cam, [billboard(golpe, 0.7, cam, giro=0.3)], chispa(), 1.0, None, 0.8)
    for k in range(7):
        ang = k * 0.9
        q = golpe + 0.6 * (math.cos(ang) * cam.r + math.sin(ang) * cam.u)
        dibujar_trans(lz, cam, [billboard(q, 0.12, cam, giro=ang)], chispa(), 1.0, None, 0.9)
    # otra asoma a la izquierda: uno corre a por ella
    h2 = agujeros[7]
    boca2 = asoma(lz, cam, h2, (h2[0] - 2.5, h2[1] - 3.0), niebla, alto=2.2, adelante=1.0, abre=44, escala=1.15)
    p2 = (h2[0] - 3.4, h2[1] - 4.8)
    jugador2(lz, cam, p2[0], p2[1], guinada_hacia(h2[0] - p2[0], h2[1] - p2[1]), P_CORRE,
             mano=[nodo_espada((-60, 0, 0))], niebla=niebla)
    # y otra a la derecha, sin nadie cerca: si se esconde, muerde y Nerea se cura
    h3 = agujeros[4]
    boca3 = asoma(lz, cam, h3, (h3[0] + 2.0, h3[1] - 2.6), niebla, alto=2.3, adelante=1.0, abre=40, escala=1.15)
    # una que espera al fondo, junto a otro agujero
    h4 = agujeros[0]
    jugador2(lz, cam, h4[0] - 1.2, h4[1] - 1.6, guinada_hacia(-0.4, 1.0), P_QUIETO, mano=[nodo_espada((-30, 0, 0))],
             niebla=niebla)
    img = componer2(lz, cam, W, H, 95)
    rotulo(img, cam, golpe, '¡ACIERTO!', -60, -150, 46, ORO)
    rotulo(img, cam, boca2, '¡OTRA!', -60, -100, 38, BLANCO)
    rotulo(img, cam, boca3, 'SI SE ESCONDE: MUERDE', -40, -120, 26, (255, 150, 150))
    rotulo(img, cam, boca3, 'Y NEREA SE CURA', -40, -88, 26, (255, 150, 150), linea=False)
    rotulo(img, cam, np.array([agujeros[6][0], 0.1, agujeros[6][1]]), '8 AGUJEROS', 90, -10, 30, CIAN)
    cifra(img, (190, 30), '12/20', 84, ORO)
    texto_sombra(img, (122, 130), 'ACIERTOS EN 20 S', ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 24), BLANCO)
    guardar(img, 'morenas')


# ----------------------------------------------------------------------
#  10. Duelo de Canto
#
#  Elige a uno y le canta: notas cian de su boca al elegido. Encima, lo que ve
#  el elegido en su pantalla: cuatro carriles (A S D F) con notas que bajan a
#  la linea; arriba, la barra que ven todos. Los demas le pegan para frenar
#  el canto.
# ----------------------------------------------------------------------
def panel_ritmo(img, x0, y0, w, h):
    """El panel de ritmo de la pantalla del elegido: cuatro carriles con sus
    teclas, notas que bajan y la linea donde hay que pulsar."""
    f = lambda t: ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', t)
    fondo_ = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fondo_)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=16, fill=(4, 14, 26, 228), outline=(*CIAN, 255), width=3)
    lx0, lx1 = x0 + 22, x0 + w - 22
    ly0, linea = y0 + 112, y0 + h - 118
    lw = (lx1 - lx0) / 4
    for i, c in enumerate(CARRIL):
        d.rectangle((lx0 + i * lw + 3, ly0, lx0 + (i + 1) * lw - 3, linea + 6), fill=(*c, 30))
    img.alpha_composite(fondo_)
    texto_sombra(img, (x0 + 22, y0 + 14), 'DUELO DE CANTO', f(34), BLANCO)
    texto_sombra(img, (x0 + 22, y0 + 60), 'ACIERTOS 9/16 · GANA CON 12', f(22), CIAN)
    # las notas (y la que esta en la linea ahora mismo)
    notas = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dn = ImageDraw.Draw(notas)
    for (carril, dy) in ((0, 70), (2, 140), (3, 205), (1, 270), (0, 330), (3, 390), (2, 450), (1, 505)):
        y = linea - dy
        if y < ly0 + 8:
            continue
        c = CARRIL[carril]
        x = lx0 + carril * lw
        dn.rounded_rectangle((x + 9, y - 13, x + lw - 9, y + 13), radius=7, fill=(*c, 255))
        dn.rounded_rectangle((x + 14, y - 10, x + lw - 14, y - 4), radius=3, fill=(255, 255, 255, 170))
    # la linea de pulsar
    dn.rectangle((lx0, linea - 3, lx1, linea + 3), fill=(255, 255, 255, 255))
    # la nota acertada: un destello en la linea del carril S
    cx = lx0 + 1.5 * lw
    dn.ellipse((cx - 44, linea - 30, cx + 44, linea + 30), fill=(*CARRIL[1], 120))
    dn.rounded_rectangle((cx - lw / 2 + 6, linea - 15, cx + lw / 2 - 6, linea + 15), radius=8, fill=(255, 255, 255, 255))
    halo = notas.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(halo)
    img.alpha_composite(notas)
    # las teclas
    teclas = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dt = ImageDraw.Draw(teclas)
    for i, (letra, c) in enumerate(zip('ASDF', CARRIL)):
        x = lx0 + i * lw
        pulsada = i == 1
        dt.rounded_rectangle((x + 7, linea + 22, x + lw - 7, linea + 22 + 66), radius=10,
                             fill=(*c, 255) if pulsada else (*R.mezclar(c, (0, 0, 0), 0.65), 255), outline=(*c, 255),
                             width=3)
    img.alpha_composite(teclas)
    dl = ImageDraw.Draw(img)
    for i, letra in enumerate('ASDF'):
        x = lx0 + i * lw
        wl = dl.textlength(letra, font=f(40))
        texto_sombra(img, (x + lw / 2 - wl / 2, linea + 25), letra, f(40), BLANCO if i != 1 else NEGRO)
    cifra(img, (cx + 70, linea - 98), '¡PERFECTO!', 44, ORO)
    return linea


def barra_duelo(img, cx, y, w, hechas=9, total=16):
    """La barra del jefe durante el duelo: las 16 notas, las acertadas encendidas."""
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 24)
    d = ImageDraw.Draw(img)
    t = 'NEREA · DUELO DE CANTO  9/16'
    wt = d.textlength(t, font=f)
    texto_sombra(img, (cx - wt / 2, y), t, f, BLANCO)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    x0, y0 = cx - w / 2, y + 38
    dc.rounded_rectangle((x0 - 4, y0 - 4, x0 + w + 4, y0 + 18), radius=6, fill=(4, 14, 26, 220))
    paso = w / total
    for i in range(total):
        c = CIAN if i < hechas else (40, 70, 90)
        if i == 11:
            c = ORO if i < hechas else (120, 100, 40)
        dc.rectangle((x0 + i * paso + 2, y0, x0 + (i + 1) * paso - 2, y0 + 14), fill=(*c, 255))
    img.alpha_composite(capa.filter(ImageFilter.GaussianBlur(3)))
    img.alpha_composite(capa)
    return x0 + 11.5 * paso, y0 + 14


def duelo_canto(W=1600, H=900, fase=3):
    cam, lz, niebla = lienzo((1.0, 4.4, -10.0), (-2.0, 4.0, 8.0), W, H, fov=56, cerca=22, lejos=48)
    nx, nz = -6.0, 13.0
    ele = (0.6, -0.4)
    ng = guinada_hacia(ele[0] - nx, ele[1] - nz)
    p = pose('CANTO', 1.4, fase=fase)
    nerea(lz, cam, 'despues', nx, nz, ng, p=p, fase=fase, niebla=niebla, luces=LUCES, amb=AMB, brillo=1.5)
    boca = punto_nerea(p, nx, nz, ng, 'mandibula', (0, 2, -9))
    # el elegido, en su aro, quieto escuchando
    dibujar_trans(lz, cam, suelo_cuad(ele[0], ele[1], 1.5), tex_aro(CIAN, grueso=0.1, marcas=12, relleno=60), 0.9, niebla,
                  0.8)
    fig = jugador2(lz, cam, ele[0], ele[1], guinada_hacia(nx - ele[0], nz - ele[1]), P_ESCUCHA, niebla=niebla)
    cabeza = punto_en(fig, 'cabeza', (0, -4, 0))
    # los que le pegan en las piernas para frenar el canto
    golpes = []
    for (dx, dz) in ((2.4, -3.0), (-2.6, -2.6)):
        x, z = nx + dx, nz + dz
        f_ = jugador2(lz, cam, x, z, guinada_hacia(nx - x, nz - z), P_GOLPE, mano=[nodo_espada()], niebla=niebla)
        golpes.append(mano_de(f_) + (np.array([nx, 1.6, nz]) - mano_de(f_)) * 0.35)
    for g in golpes:
        dibujar_trans(lz, cam, [billboard(g, 0.55, cam, giro=0.4)], chispa(), 1.0, None, 0.9)
    # el canto: una cinta ondulada de la boca a su cabeza, aros y notas
    lado = np.cross(cabeza - boca, [0, 1.0, 0])
    lado /= np.linalg.norm(lado)
    camino = [np.array(q) + lado * 0.5 * math.sin(k * math.pi * 3) for k, q in
              zip(np.linspace(0, 1, 24), curva(boca, cabeza, 1.2, 24))]
    dibujar_trans(lz, cam, cinta3d(camino, 0.14, cam), tex_haz(CIAN), 0.45, niebla, 0.4)
    ta = tex_aro(CIAN, 64, 0.1, 0)
    for i in range(2, 22, 3):
        k = i / 23
        dibujar_trans(lz, cam, [billboard(camino[i], 0.8 - 0.4 * k, cam)], ta, 0.7, niebla, 0.35)
    for i, j in enumerate(range(2, 22, 3)):
        c = CARRIL[i % 4]
        hacia_cam = cam.ojo - camino[j]
        hacia_cam /= np.linalg.norm(hacia_cam)
        q = camino[j] + hacia_cam * 1.2 + np.array([0, 0.7 + 0.25 * math.sin(j), 0]) + cam.r * 0.5 * (-1) ** i
        sprite(lz, cam, q, 0.6 - 0.012 * j, nota_borde(c), None, 1.15, giro=0.25 * math.sin(j), tapa_brillo=True)
    img = componer2(lz, cam, W, H, 97)
    # el panel de la pantalla del elegido y su linea hasta el
    x0, y0, w, h = 36, 96, 380, 700
    linea = panel_ritmo(img, x0, y0, w, h)
    sx, sy, _ = pantalla(cam, cabeza)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    for (a_, b_) in (((x0 + w, y0 + 40), (sx - 24, sy - 20)),):
        dc.line([a_, b_], fill=(*NEGRO, 170), width=6)
        dc.line([a_, b_], fill=(*CIAN, 235), width=2)
    dc.ellipse((sx - 28, sy - 24, sx - 20, sy - 16), fill=(*CIAN, 255))
    img.alpha_composite(capa)
    texto_sombra(img, (x0 + 4, y0 - 44), 'LO QUE VE EL ELEGIDO', ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 28), CIAN)
    bx, by = barra_duelo(img, 1250, 18, 440)
    fc = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 22)
    tc = 'LOS DEMÁS VEN EN LA BARRA CÓMO VA'
    texto_sombra(img, (1250 - ImageDraw.Draw(img).textlength(tc, font=fc) / 2, by + 10), tc, fc, (190, 230, 240))
    rotulo(img, cam, cabeza + np.array([0, -0.9, 0]), 'EL ELEGIDO', 90, 40, 34, CIAN)
    rotulo(img, cam, camino[10] + np.array([0, 1.2, 0]), 'SU CANTO', -20, -110, 34, BLANCO)
    rotulo(img, cam, golpes[0], 'PEGÁNDOLE FRENAN EL CANTO', 60, 110, 28, BLANCO)
    guardar(img, 'duelo_canto')


ESCENAS = {'canto': canto, 'naufragio': naufragio, 'marea_alta': marea_alta, 'tira': tira, 'cadenas': cadenas,
           'corazon': corazon, 'pesca': pesca, 'canones': canones, 'morenas': morenas, 'duelo_canto': duelo_canto}

if __name__ == '__main__':
    solo = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in solo:
        ESCENAS[k]()
        print(k, flush=True)

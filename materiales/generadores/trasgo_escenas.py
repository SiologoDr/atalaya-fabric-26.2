"""
Renders del Trasgo (15-10-2026), el mob que se te aferra al cuerpo: en una mina abandonada (la galeria de piedra con
sus vigas de madera, los railes, los faroles y alguna veta de mineral), a la escala de Minecraft; la cara (de cerca); la
foto de lo que hace, agarrado a un jugador (el Colgon a la espalda, el Jinete en los hombros tapandole los ojos y el
Ladron colgado del brazo); los tres juntos con un jugador; y la lamina de materiales.

Las fotos salen sin letras y con el contorno blanco.

Uso: python trasgo_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
     (con RAPIDO=1 en el entorno, a media resolucion para probar)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vigia_render as vr
import nerea_modelo as nm
import nerea_escenas as ne            # el jugador
import quimeras_modelo as qm
import quimeras_escenas as qe         # el lienzo, la niebla y el revelado
import bestias_modelo as bm
import trasgo_modelo as tg

RAIZ, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
RAPIDO = os.environ.get('RAPIDO') == '1'
SS = 1 if RAPIDO else 2
K = 0.5 if RAPIDO else 1.0
TAU = math.tau
D = vr.D2R
_r = bm._r


def _c(h):
    return tuple(c / 255 for c in nm._hex(h))


def sitio(v):
    """La misma mina para los tres: oscura, con la luz calida de los faroles y un poco de luz fria de fuera."""
    return dict(
        luces=[((-0.4, 0.6, 0.7), (1.0, 0.72, 0.42), 0.75, 'llave'), ((0.5, 0.4, -1.0), (0.5, 0.6, 0.8), 0.7, 'contra'),
               ((0.7, 0.3, 0.5), (1.0, 0.6, 0.3), 0.3, 'llave')],
        amb=(0.2, 0.18, 0.17), niebla=(0.03, 0.025, 0.025), niebla_d=(6, 30), fondo=(0.02, 0.016, 0.016),
        motas=(255, 200, 140),
    )


# ----------------------------------------------------------------------
#  La mina: el suelo, las paredes y el techo de piedra, las vigas, los railes, los faroles y las vetas
# ----------------------------------------------------------------------
PIEDRA = _r('1e1c1c', '2a2826', '363432', '44403c', '54504a')
GRAVA = _r('221e1c', '2e2a26', '3a3530', '48423c', '58514a')
MADERA = _r('2a1a0e', '3e2814', '58381c', '6e4a26', '8a5e32')
HIERRO = _r('1a1c20', '2a2e34', '40464e', '5a626c', '7a848e')


def _piedra(semilla, rampa):
    rng = random.Random(semilla)
    n = 16
    idx = np.full((n, n), 2)
    for _ in range(9):                                                                   # manchas limpias de 2 x 2
        x, y = rng.randrange(0, n, 2), rng.randrange(0, n, 2)
        idx[y:y + 2, x:x + 2] = rng.choice((1, 3))
    return bm._imagen(idx, rampa)


qm._reg('grava_tg', _piedra(5, GRAVA))
qm._reg('piedra_tg', _piedra(9, PIEDRA))


def p_piedra(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    idx = np.where((((xs // 2) * 5 + (ys // 2) * 3 + s) % 7) == 0, 1, np.where((((xs // 2) * 3 + (ys // 2) * 7 + s) % 11) == 0, 3, 2))
    return bm._imagen(idx, PIEDRA), None


def p_madera(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    if cara in ('arriba', 'abajo'):
        idx = np.where((xs + ys) % 4 == 0, 3, 2)
    else:
        idx = np.where((xs % 4) == 0, 1, 2)
        idx[(ys % 7) == 3] = 3
    return bm._imagen(idx, MADERA), None


def p_hierro(tw, th, cara, s):
    ys, xs = np.mgrid[0:th, 0:tw]
    return bm._imagen(np.where(xs == 0, 3, 2), HIERRO), None


def p_farol(tw, th, cara, s):
    """El farol: el cristal calido que brilla con el marco de hierro oscuro."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t = np.zeros((th, tw, 4), np.uint8)
    t[...] = (255, 190, 90, 255)
    t[(np.abs(xs - (tw - 1) / 2) < tw / 4) & (np.abs(ys - (th - 1) / 2) < th / 4)] = (255, 236, 180, 255)
    t[(xs == 0) | (xs == tw - 1) | (ys == 0) | (ys == th - 1)] = (40, 34, 30, 255)
    return t, None


def p_veta(tw, th, cara, s):
    """Una veta de mineral en la piedra (de oro viejo): la piedra con las pepitas de 2 x 2."""
    ys, xs = np.mgrid[0:th, 0:tw]
    t = bm._imagen(np.full((th, tw), 2), PIEDRA)
    m = (((xs // 2) * 3 + (ys // 2) * 5 + s) % 4) == 0
    t[m] = (232, 180, 60, 255)
    return t, None


for _n, _f in (('piedra', p_piedra), ('madera', p_madera), ('hierro', p_hierro), ('farol', p_farol), ('veta', p_veta)):
    _f.__name__ = 'tgE_' + _n
bm.PLENOS.add(p_farol)

ANCHO, ALTO = 4.0, 4.0           # media anchura y altura de la galeria (bloques)


def mina(lz, cam, niebla, S, largo=40.0, giro=0.0, centro=(0.0, 0.0), vetas=True, semilla=3):
    """La galeria a lo largo de z (girada 'giro'): el suelo de grava, las paredes y el techo de piedra (que no tapan la
    camara), las vigas cada cuatro bloques (dos postes y el travesano), los railes, los faroles en los postes y alguna
    veta de mineral."""
    qs = []
    r = random.Random(semilla)
    M0 = vr.T(centro[0], 0.0, centro[1]) @ vr.Ry(giro)
    paso = 2.0
    for z in np.arange(-largo, largo, paso):                                              # el suelo, por losas
        for x in np.arange(-ANCHO, ANCHO, paso):
            P = [pt_(M0, (x + paso, 0.0, z)), pt_(M0, (x, 0.0, z)), pt_(M0, (x, 0.0, z + paso)), pt_(M0, (x + paso, 0.0, z + paso))]
            qs.append((P, [(paso, 0), (0, 0), (0, paso), (paso, paso)], 'grava_tg'))
    for z in np.arange(-largo, largo, paso):                                              # las paredes y el techo
        for lado in (-1, 1):
            x = lado * ANCHO
            P = [pt_(M0, (x, ALTO, z)), pt_(M0, (x, ALTO, z + paso)), pt_(M0, (x, 0.0, z + paso)), pt_(M0, (x, 0.0, z))]
            qs.append((P, [(0, 0), (paso, 0), (paso, ALTO), (0, ALTO)], 'piedra_tg'))
        for x in np.arange(-ANCHO, ANCHO, paso):
            P = [pt_(M0, (x, ALTO, z)), pt_(M0, (x + paso, ALTO, z)), pt_(M0, (x + paso, ALTO, z + paso)), pt_(M0, (x, ALTO, z + paso))]
            qs.append((P, [(0, 0), (paso, 0), (paso, paso), (0, paso)], 'piedra_tg'))
    for k, z in enumerate(np.arange(-largo, largo, 4.0)):                                  # las vigas
        M = M0 @ vr.T(0.0, 0.0, z)
        for lado in (-1, 1):
            bm.cubo(qs, M, lado * (ANCHO - 0.5) - 0.25, 0.0, -0.25, 0.5, ALTO, 0.5, p_madera, semilla=k)
        bm.cubo(qs, M, -ANCHO, ALTO - 0.5, -0.25, 2 * ANCHO, 0.5, 0.5, p_madera, semilla=k + 1)
        if k % 2 == 0:                                                                     # el farol, colgado del poste
            lado = 1 if k % 4 == 0 else -1
            bm.cubo(qs, M, lado * (ANCHO - 0.85) - 0.18, 2.3, 0.3, 0.36, 0.46, 0.36, p_farol, semilla=k)
    for lado in (-0.6, 0.6):                                                               # los railes
        bm.cubo(qs, M0, lado - 0.06, 0.0, -largo, 0.12, 0.08, 2 * largo, p_hierro, semilla=1)
    for z in np.arange(-largo, largo, 0.6):                                                # las traviesas
        bm.cubo(qs, M0 @ vr.T(0.0, 0.0, z), -0.9, 0.0, -0.1, 1.8, 0.05, 0.2, p_madera, semilla=2)
    if vetas:
        for k in range(10):
            lado = r.choice((-1, 1))
            z = r.uniform(-largo * 0.5, largo * 0.5)
            y = r.uniform(0.6, ALTO - 1.0)
            bm.cubo(qs, M0 @ vr.T(lado * (ANCHO - 0.02), y, z), -0.02, 0.0, 0.0, 0.04, 0.6, 0.8, p_veta, semilla=k)
    qm.dibujar(lz, cam, qs, S['luces'], S['amb'], niebla)
    return [pt_(M0, (lado * (ANCHO - 0.67), 2.5, z + 0.48)) for k, z in enumerate(np.arange(-largo, largo, 4.0))
            if k % 2 == 0 for lado in ([1] if k % 4 == 0 else [-1])]


def pt_(M, p):
    return np.array(tg.pt(M, p), float)


def luces_faroles(faroles, cam, n=3):
    """Las luces de los faroles mas cercanos a la camara."""
    cerca = sorted(faroles, key=lambda f: np.linalg.norm(f - cam.ojo))[:n]
    return [(tuple(f) + (5.0,), (1.0, 0.68, 0.36), 0.9, 'punto') for f in cerca]


def revelar(lz, cam, W, H, S, n_motas=30, semilla=3, fuerza_vineta=0.45, brillo=0.9):
    def a_img(x):
        return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    alfa = np.array(a_img(lz.alfa)).astype(float)[..., None] / 255
    col = np.array(a_img(lz.color)).astype(float) / 255
    emis = np.array(a_img(qe.tono(lz.emis))).astype(float) / 255
    fondo = np.broadcast_to(np.array(S['fondo']), (H, W, 3))
    arr = col * alfa + fondo * (1 - alfa)
    arr = qe.tono(qe.bloom(arr, emis * brillo, radios=((2 * K, 0.5), (10 * K, 0.4), (40 * K, 0.35))))
    arr = qe.vineta(arr, fuerza_vineta)
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    if n_motas > 0:                                                                       # el polvo de la mina
        capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        r = random.Random(semilla)
        for _ in range(int(n_motas * W / 1600)):
            x, y = r.uniform(0, W), r.uniform(0, H)
            g = max(1, int(W / 1600))
            d.rectangle((x, y, x + g, y + g), fill=(*S['motas'], r.randint(60, 140)))
        img = Image.alpha_composite(img.convert('RGBA'), capa)
    return img


def guardar(img, nombre):
    img.convert('RGB').save(os.path.join(OUT, nombre + '.jpg'), quality=92)
    print('ok', nombre, flush=True)
    return img


def perfilar(lz, mascara, grosor, color=(1.0, 0.97, 1.0)):
    """El contorno blanco: los pixeles de fuera que tocan al monstruo y quedan detras de el."""
    zc = np.where(mascara, lz.z, np.inf)
    for _ in range(grosor):
        e = zc.copy()
        e[1:] = np.minimum(e[1:], zc[:-1])
        e[:-1] = np.minimum(e[:-1], zc[1:])
        e[:, 1:] = np.minimum(e[:, 1:], zc[:, :-1])
        e[:, :-1] = np.minimum(e[:, :-1], zc[:, 1:])
        zc = np.where(mascara, zc, e)
    borde = ~mascara & np.isfinite(zc) & (lz.z > zc)
    lz.color[borde] = color
    lz.alfa[borde] = 1.0
    lz.emis[borde] = np.array(color) * 0.15


# las posturas del jugador en la foto de accion (los brazos: 'bi' el izquierdo, 'bd' el derecho)
JUGADOR = {
    'A': {'bi': {'rot': (-55, 0, -30)}, 'bd': {'rot': (-55, 0, 30)}, 'cabeza': {'rot': (10, 0, 0)}},
    'B': {'bi': {'rot': (-160, 0, -35)}, 'bd': {'rot': (-160, 0, 35)}},
    'C': {'bd': {'rot': (-90, 0, 0)}, 'bi': {'rot': (-20, 0, -15)}},
}
MANO_JUGADOR = (-6.0, 22.0, 11.0)          # la mano derecha del jugador, estirada (pixeles, el jugador mira a +z)


def postura_accion(cual):
    if cual == 'A':
        return tg.postura_espalda()
    if cual == 'B':
        return tg.postura_hombros()
    return tg.postura_brazo(MANO_JUGADOR)


def camara(cual, vista, info):
    c = np.asarray(info['cabeza'], float)
    if vista == 'heroe':
        return (1.3, 0.75, 2.7), (0.0, 0.62, 0.15), 50
    if vista == 'cabeza':
        return tuple(c + np.array((0.32, 0.05, 0.95))), tuple(c + np.array((0.0, -0.02, 0.0))), 50
    obj = {'A': (-0.15, 1.35, 0.0), 'B': (0.0, 1.6, 0.0), 'C': (-0.3, 1.0, 0.45)}[cual]
    ojo = {'A': (-1.7, 1.7, 2.3), 'B': (0.9, 1.7, 2.7), 'C': (-3.4, 1.2, 1.3)}[cual]
    return ojo, obj, 50


def escena(cual, vista, n_motas=30, brillo=0.9):
    """Una foto: la mina; el Trasgo (y, en la de accion, agarrado a un jugador); el contorno blanco; y sin letras."""
    W, H = int(1600 * K), int(1000 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio(cual)
    niebla = qe.Niebla(S['niebla'], *S['niebla_d'])
    accion = vista == 'accion'
    qs, info = tg.trasgo(cual, postura_accion(cual) if accion else 'acecho')
    ojo, obj, fov = camara(cual, vista, info)
    cam = vr.Camara(ojo, obj, fov, W * SS, H * SS)
    faroles = mina(lz, cam, niebla, S, giro=1.3 if (accion and cual == 'C') else 0.35)   # la camara, dentro de la galeria
    luces = S['luces'] + luces_faroles(faroles, cam) + [(tuple(info['ojos']) + (1.2,), _c(info['luz']), 0.5, 'punto')]
    z0 = lz.z.copy()
    if accion:
        nm.dibujar(lz, cam, nm.quads(ne.jugador(), JUGADOR[cual], ne.jugador_a_mundo(0.0, 0.0, 180)), luces, S['amb'],
                   niebla)
    tg.dibujar(lz, cam, qs, luces, S['amb'], niebla)
    perfilar(lz, lz.z < z0, max(1, int(round(3 * SS * K))))
    return revelar(lz, cam, W, H, S, n_motas=n_motas, brillo=brillo)


def heroe(cual):
    guardar(escena(cual, 'heroe'), 'heroe_' + cual)


def cabeza(cual):
    guardar(escena(cual, 'cabeza', 15), 'cabeza_' + cual)


def accion(cual):
    guardar(escena(cual, 'accion', 25, brillo=1.0), 'accion_' + cual)


def tres(formas='ABC', nombre='tres'):
    """Los tres juntos, agazapados en la galeria, con un jugador de pie al lado."""
    W, H = int(1800 * K), int(860 * K)
    lz = qe.Lienzo(W * SS, H * SS)
    S = sitio('A')
    niebla = qe.Niebla(S['niebla'], 8, 34)
    cam = vr.Camara((0.0, 1.3, 6.4), (0.0, 0.9, 0.0), 40, W * SS, H * SS)
    faroles = mina(lz, cam, niebla, S, giro=0.0)
    luces = S['luces'] + luces_faroles(faroles, cam, 4)
    figura = np.zeros(lz.z.shape, bool)
    for cual, x in (('A', -1.0), ('B', 0.9), ('C', 2.8)):
        qs, info = tg.trasgo(cual, 'acecho')
        qs = qm.transformar(qs, vr.T(x, 0, 0) @ vr.Ry(-0.15))
        z0 = lz.z.copy()
        tg.dibujar(lz, cam, qs, luces, S['amb'], niebla)
        figura |= lz.z < z0
    perfilar(lz, figura, max(1, int(round(2 * SS * K))))
    nm.dibujar(lz, cam, nm.quads(ne.jugador(), {}, ne.jugador_a_mundo(-2.8, 0.0, 180)), luces, S['amb'], niebla)
    guardar(revelar(lz, cam, W, H, S, n_motas=30), nombre)


def materiales(formas='ABC', nombre='materiales'):
    """La lamina de materiales, sin letras: una fila por tipo, con la piel, el ojo, la boca, el diente, el gorro y la
    oreja."""
    W = 1240
    filas = []
    for c in 'ABC':
        P = tg.pintores(tg.VARIANTES[c])
        filas.append([(P['piel'], 'frente', 10, 10), (P['ojo'], 'frente', 4, 2), (P['boca'], 'frente', 10, 2),
                      (P['diente'], 'frente', 1, 2), (P['gorro'], 'frente', 9, 4), (P['oreja'], 'frente', 8, 4)])
    celda = 150
    H = 40 + len(filas) * (celda + 30) + 10
    img = Image.new('RGB', (W, H), (20, 18, 18))
    d = ImageDraw.Draw(img)
    for fi, fila in enumerate(filas):
        y0 = 40 + fi * (celda + 30)
        for k, (pintor, cara, tw, th) in enumerate(fila):
            t, _ = pintor(tw, th, cara, 7)
            fondo = Image.new('RGBA', (tw, th), (44, 40, 40, 255))
            fondo.alpha_composite(Image.fromarray(t))
            esc = min(celda / tw, celda / th)
            im = fondo.resize((max(1, int(tw * esc)), max(1, int(th * esc))), Image.NEAREST)
            cx = 40 + k * 192
            img.paste(im.convert('RGB'), (cx + (celda - im.width) // 2, y0 + (celda - im.height) // 2))
            d.rectangle((cx - 1, y0 - 1, cx + celda, y0 + celda), outline=(70, 64, 62))
    guardar(img, nombre)


ESCENAS = {'heroe_' + c: (lambda c=c: heroe(c)) for c in 'ABC'}
ESCENAS.update({'cabeza_' + c: (lambda c=c: cabeza(c)) for c in 'ABC'})
ESCENAS.update({'accion_' + c: (lambda c=c: accion(c)) for c in 'ABC'})
ESCENAS.update({'tres': tres, 'materiales': materiales})
PRUEBAS = {}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for k in pedidas:
        (ESCENAS.get(k) or PRUEBAS[k])()

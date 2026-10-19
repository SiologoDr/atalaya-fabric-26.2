"""
Las hormigas del bestiario (18-10-2026): las cinco hormigas del DEDsafío 2 (Cantimplo, Bombermant, Parapona, Compona y
Solvetus), con nuestro diseño. Todas comparten el cuerpo de hormiga (la cabeza con sus antenas acodadas y sus mandíbulas,
el tórax, la cintura fina y el gáster, y seis patas de dos tramos) y cada una tiene lo suyo:

  lancera     (Cantimplo)  parda, con un casco de cáscara de semilla y una lanza de madera con punta de pedernal
                           sujeta en las mandíbulas: la hormiga soldado de siempre
  polvorin    (Bombermant) gris oscura, con una bomba de barro atada al gáster con cuerdas y la mecha encendida:
                           revienta (y deja alucinando a todo el que pilla cerca)
  cabezona    (Parapona)   parda, con una cabeza enorme y unas mandíbulas como tenazas: su mordisco te deja lentísimo
  radiactiva  (Compona)    negra, con las marcas verdes que brillan y los ojos encendidos: su mordisco deja radiación
  brasa       (Solvetus)   roja, con grietas de brasa que brillan y el gáster encendido: tocarla te prende un fuego que
                           solo se apaga con agua

Uso: python bestiario_hormigas.py <raíz> [carpeta de las vistas] [ids separados por comas]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
from bestiario import rampa

CARPETA = None
LADOS = ((1, 'i'), (-1, 'd'))


def juntar(*rampas):
    return np.vstack(rampas)


def hormiga(m, P, h=4.6, cabeza=(2.2, 2.0, 2.0), torax=(1.7, 1.5, 2.4), gaster=(2.5, 2.3, 3.1), muslo=4.4, ojo=None,
            mandibula=None, antena=None):
    """El cuerpo de hormiga. P: los pintores ('cuerpo', 'cabeza', 'gaster', 'pata'). Devuelve los dos trípodes de patas
    (para el paso alterno) y los centros de la cabeza y del gáster."""
    tx, ty, tz = torax
    m.parte('cuerpo', None, (0, h, 0))
    m.ovalo('cuerpo', (0, h, 0), (tx, ty, tz), P['cuerpo'])
    # La cabeza, delante y algo más alta, con sus ojos a los lados, las mandíbulas y las antenas acodadas.
    cx, cy, cz = cabeza
    c_cab = np.array((0, h + 0.8, tz + cz * 0.9))
    m.parte('cabeza', 'cuerpo', (0, h + 0.5, tz))
    m.ovalo('cabeza', tuple(c_cab), (cx, cy, cz), P['cabeza'])
    if ojo is not None:
        for lado in (-1, 1):
            m.caja('cabeza', (lado * cx * 0.92, c_cab[1] + cy * 0.25, c_cab[2] + cz * 0.2), (0.9, cy * 0.7, cz * 0.7), ojo)
    if mandibula is not None:
        for lado, ld in LADOS:
            piv = c_cab + np.array((lado * cx * 0.45, -cy * 0.45, cz * 0.85))
            n = m.parte(f'mandibula_{ld}', 'cabeza', tuple(piv))
            a = piv
            b = a + np.array((lado * cx * 0.15, -0.3, cz * 0.7))
            c = b + np.array((-lado * cx * 0.45, -0.1, cz * 0.35))
            m.viga(n, a, b, 0.9, mandibula)
            m.viga(n, b, c, 0.7, mandibula)
    if antena is not None:
        for lado, ld in LADOS:
            piv = c_cab + np.array((lado * cx * 0.35, cy * 0.75, cz * 0.6))
            n = m.parte(f'antena_{ld}', 'cabeza', tuple(piv))
            codo = piv + np.array((lado * 0.6, 3.2, 0.6))
            m.viga(n, piv, codo, 0.6, antena)
            n2 = m.parte(f'antena_{ld}b', n, tuple(codo))
            m.viga(n2, codo, codo + np.array((lado * 0.8, 0.6, 3.4)), 0.5, antena)
    # La cintura (el pecíolo) y el gáster, detrás, levantado.
    gx, gy, gz = gaster
    m.caja('cuerpo', (0, h - 0.1, -tz - 0.6), (1.0, 1.0, 1.6), P['cuerpo'])
    c_gas = np.array((0, h + 0.7, -tz - 1.2 - gz))
    m.parte('gaster', 'cuerpo', (0, h, -tz - 1.0))
    m.ovalo('gaster', tuple(c_gas), (gx, gy, gz), P['gaster'], rot=(-14, 0, 0))
    # Las seis patas: el muslo sube hasta la rodilla y la tibia baja al suelo, abiertas.
    tripodes = ([], [])
    zs = (tz * 0.55, 0.0, -tz * 0.55)
    angulos = (40, 2, -38)
    for lado, ld in LADOS:
        for i in range(3):
            phi = math.radians(angulos[i])
            d = np.array((lado * math.cos(phi), 0.0, math.sin(phi)))
            cadera = np.array((lado * tx * 0.8, h - 0.4, zs[i]))
            rodilla = cadera + d * muslo * math.cos(math.radians(18)) + np.array((0, muslo * math.sin(math.radians(18)), 0))
            pie = rodilla + d * muslo * 0.8 + np.array((0, -rodilla[1] + 0.15, 0))
            theta = math.degrees(math.atan2(d[0], d[2]))
            n = m.parte(f'pata_{ld}{i}', 'cuerpo', tuple(cadera), rot=(0, theta, 0))
            m.viga(n, cadera, rodilla, 0.9, P['pata'])
            n2 = m.parte(f'pata_{ld}{i}b', n, tuple(rodilla), rot=(0, theta, 0))
            m.viga(n2, rodilla, pie, 0.7, P['pata'])
            tripodes[(i + (0 if lado > 0 else 1)) % 2].append((f'pata_{ld}{i}', f'pata_{ld}{i}b', lado, i))
    m.mirar(('cabeza', 0.7))
    return tripodes, c_cab, c_gas


def anims_hormiga(m, tripodes, paso=0.4, swing=22, alza=14):
    """andar: el paso de trípode (tres patas apoyadas, tres que se adelantan levantadas); siempre: las antenas tantean y
    las mandíbulas se abren y cierran; ataque: la cabeza se lanza y las mandíbulas muerden; muerte: patas arriba, con
    las patas encogidas."""
    a = m.anim('andar', paso, bucle=True)
    for g, tri in enumerate(tripodes):
        for muslo, tib, lado, i in tri:
            fase = 0.5 * g
            a.onda(muslo, 'r', 1, swing, fase=fase)
            a.onda(muslo, 'r', 0, -alza, fase=fase + 0.25, forma=lambda v: max(0.0, v))
            a.onda(tib, 'r', 0, alza * 0.7, fase=fase + 0.25, forma=lambda v: max(0.0, v))
    a.onda('gaster', 'r', 1, 5, periodo=paso)
    m.anim('reposo', 3.0, bucle=True).onda('gaster', 'r', 0, 4, periodo=1.5)
    s = m.anim('siempre', 2.0, bucle=True)
    for lado, ld in LADOS:
        if f'antena_{ld}' in m.partes:
            s.onda(f'antena_{ld}', 'r', 0, 12, periodo=1.0, fase=0.25 if lado > 0 else 0.0)
            s.onda(f'antena_{ld}b', 'r', 1, 14, periodo=0.7, fase=0.4 if lado > 0 else 0.1)
        if f'mandibula_{ld}' in m.partes:
            s.onda(f'mandibula_{ld}', 'r', 1, lado * 10, periodo=1.0, forma=lambda v: max(0.0, v))
    at = m.anim('ataque', 0.5)
    at.rot('cabeza', [(0, 0, 0, 0), (0.12, -14, 0, 0), (0.24, 12, 0, 0), (0.5, 0, 0, 0)])
    at.mov('cabeza', [(0, 0, 0, 0), (0.12, 0, 0, -0.6), (0.24, 0, 0, 1.0), (0.5, 0, 0, 0)])
    for lado, ld in LADOS:
        if f'mandibula_{ld}' in m.partes:
            at.rot(f'mandibula_{ld}', [(0, 0, 0, 0), (0.12, 0, lado * 30, 0), (0.24, 0, lado * -14, 0), (0.5, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.35, 0, 0, 90), (0.7, 0, 0, 178), (1.0, 0, 0, 180)])
    d.mov('cuerpo', [(0, 0, 0, 0), (0.5, 0, 2.6, 0), (1.0, 0, 1.4, 0)])
    for tri in tripodes:
        for muslo, tib, lado, i in tri:
            d.rot(muslo, [(0, 0, 0, 0), (0.6, 35, 0, 0), (1.0, 50, 0, 0)])
            d.rot(tib, [(0, 0, 0, 0), (0.6, 40, 0, 0), (1.0, 70, 0, 0)])


def terminar(m, raiz, nombre_es, nombre_en, huevo, retrato, particulas=(), poses=None):
    m.exportar(raiz)
    if CARPETA:
        m.hoja_vistas(os.path.join(CARPETA, f'{m.id}.png'),
                      poses=poses or [('andar', 0.1), ('andar', 0.3), ('ataque', 0.24), ('muerte', 1.0)])
    piel, contorno, dib = huevo
    B.huevo(m.id, piel, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    ojo, obj = retrato
    B.retrato(m, ojo=ojo, objetivo=obj, fov=34)
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)
    return m


def chispa(color, n=8):
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            d = np.hypot(x - 0.5, y - 0.5)
            centro = d < 0.16
            return (np.where(centro, 255, color[0]), np.where(centro, 240, color[1]), np.where(centro, 210, color[2]),
                    (d < 0.42 - k * 0.1) * 255)
        cuadros.append(B.sprite(n, f))
    return cuadros


def esquirla(color, n=8):
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            a = (np.abs(x - 0.5) + np.abs(y - 0.5) * (0.7 + 0.3 * k) < 0.38) * 255
            sombra = (x + y > 1.05)
            return (np.where(sombra, color[0] * 0.6, color[0]), np.where(sombra, color[1] * 0.6, color[1]),
                    np.where(sombra, color[2] * 0.6, color[2]), a)
        cuadros.append(B.sprite(n, f))
    return cuadros


def nube(color, n=16):
    cuadros = []
    for k in range(4):
        def f(x, y, k=k):
            d = np.hypot(x - 0.5, y - 0.5)
            r0 = 0.22 + 0.06 * k
            bulto = (d < r0) | (np.hypot(x - 0.32, y - 0.42) < r0 * 0.7) | (np.hypot(x - 0.66, y - 0.4) < r0 * 0.65)
            return color[0], color[1], color[2], bulto * (235 - 30 * k)
        cuadros.append(B.sprite(n, f))
    return cuadros


def quitina_fn(R, veta=True, marca=None):
    """La quitina de hormiga: lisa y brillante (una veta de luz en diagonal), con los cantos un tono más oscuros; con
    marca (fn(xs, ys, tw, th, cara, s) -> máscara), lo marcado va en el color de la segunda rampa (y brilla)."""
    def fn(xs, ys, tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if veta:
            diag = (xs + ys * 0.8) % max(6, tw)
            idx[(diag >= 1) & (diag < 2)] = 4
            idx[(diag >= 2) & (diag < 3)] = 3
        idx[(xs == 0) | (xs == tw - 1)] = 1
        if cara == 'abajo':
            idx[...] = 1
        if marca is None:
            return idx
        mk = marca(xs, ys, tw, th, cara, s)
        idx = np.where(mk, 7, idx)
        return idx, mk
    return fn


# ======================================================================================================================
#  Las cinco hormigas
# ======================================================================================================================
PARDA = rampa('2a1406', '4a240c', '6e3a16', '965424', 'c07a3e')
GRIS = rampa('121214', '1e1e22', '2c2c32', '3e3e46', '56565e')
NEGRA = rampa('040406', '0a0a0e', '121218', '1c1c24', '2a2a34')
ROJA = rampa('3a0604', '6a0e08', '9e1a0e', 'd0321a', 'f06a40')
VERDE = rampa('0a3a0a', '127012', '2ab82a', '7aff5a', 'd8ffc8')
BRASA = rampa('6a1604', 'c04a0a', 'f08a1a', 'ffc84a', 'fff2b0')
MADERA = rampa('3a2410', '5a3a1c', '7e5428', '9e7038', 'c09050')
PEDERNAL = rampa('2a2a30', '44444c', '62626c', '84848e', 'a8a8b2')
OJO_NEGRO = rampa('000000', '080808', '141414', '262626', 'd0d0d0')


def ojo_brillante(nombre):
    """El ojo compuesto: negro brillante, con su reflejo."""
    def fn(tw, th, cara, s):
        ys, xs = np.mgrid[0:th, 0:tw]
        idx = np.full((th, tw), 2)
        idx[((xs + ys) % 2) == 0] = 3
        idx[(xs < tw * 0.4) & (ys < th * 0.35)] = 4
        return B._img(idx, OJO_NEGRO), None
    return B.Pintor(nombre, fn)


def lancera(raiz):
    """La Hormiga Lancera: parda y lustrosa, con un casco de cáscara de semilla (con su borde) y una lanza de madera
    con la punta de pedernal atada, en alto como un soldado (la baja de golpe al atacar)."""
    m = B.Modelo('lancera', K=2, ancho=128)
    m.escala = 1.1
    q = B.trazo('quitina_parda', quitina_fn(PARDA), PARDA)
    P = {'cuerpo': q, 'cabeza': q, 'gaster': q, 'pata': B.anillos('pata_parda', PARDA, paso=3)}
    tri, c_cab, c_gas = hormiga(m, P, ojo=ojo_brillante('ojo_hormiga'), mandibula=B.liso('mandibula_parda', PARDA, base=1),
                                antena=B.anillos('antena_parda', PARDA, paso=2))
    casco = B.trazo('casco_semilla', lambda xs, ys, tw, th, c, s: np.where((ys % 3) == 0, 1, np.where((xs % 5) == 2, 3, 2)),
                    MADERA)
    m.caja('cabeza', tuple(c_cab + np.array((0, 1.6, -0.3))), (4.0, 1.2, 4.0), casco)
    m.caja('cabeza', tuple(c_cab + np.array((0, 2.4, -0.4))), (2.6, 0.9, 2.6), casco)
    # La lanza: en alto, apoyada en el hombro izquierdo y sujeta con la mandíbula, con la punta arriba y delante.
    m.parte('lanza', 'cabeza', tuple(c_cab + np.array((0, -0.9, 2.2))))
    a = c_cab + np.array((2.0, -2.4, 0.4))
    b = c_cab + np.array((3.0, 6.5, 5.4))
    m.viga('lanza', a, b, 0.9, B.anillos('asta', MADERA, paso=4))
    dir_ = (b - a) / np.linalg.norm(b - a)
    pedernal = B.trazo('pedernal', lambda xs, ys, tw, th, c, s: np.where((xs + ys) % 3 == 0, 3, 2), PEDERNAL)
    m.viga('lanza', b, b + dir_ * 2.0, 1.0, pedernal, ancho=2.2)
    m.viga('lanza', b + dir_ * 2.0, b + dir_ * 3.4, 0.6, pedernal, ancho=1.2)
    m.viga('lanza', b - dir_ * 0.4, b + dir_ * 0.3, 1.3, B.liso('atadura', MADERA, base=3))
    anims_hormiga(m, tri)
    at = m.anims['ataque']
    at.rot('lanza', [(0, 0, 0, 0), (0.12, -15, 0, 0), (0.24, 55, 0, 0), (0.5, 0, 0, 0)])
    m.paso = 4.0

    def dib(px, filas, c):
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c('000000')
        for x, f in ((3, 13), (5, 11), (7, 9), (9, 7), (11, 5)):
            px[x, f] = c('9e7038')
        px[12, 4] = c('84848e')
    return terminar(m, raiz, 'Hormiga Lancera', 'Spear Ant', (('c07a3e', '965424', '6e3a16'), ('2a1406', '140a02'), dib),
                    ((1.4, 1.1, 1.9), (0, 0.4, 0)),
                    particulas=(('astilla', esquirla((158, 112, 56))),))


def polvorin(raiz):
    """La Hormiga Polvorín: gris oscura, con una bomba de barro cocido atada al gáster con dos vueltas de cuerda y la
    mecha encendida (chisporrotea siempre); cuando te tiene cerca, se le enciende de verdad."""
    m = B.Modelo('polvorin', K=2, ancho=128)
    m.escala = 1.0
    q = B.trazo('quitina_gris', quitina_fn(GRIS), GRIS)
    P = {'cuerpo': q, 'cabeza': q, 'gaster': q, 'pata': B.anillos('pata_gris', GRIS, paso=3)}
    tri, c_cab, c_gas = hormiga(m, P, ojo=ojo_brillante('ojo_hormiga'), mandibula=B.liso('mandibula_gris', GRIS, base=1),
                                antena=B.anillos('antena_gris', GRIS, paso=2))
    barro = rampa('3a1a0c', '5e2c14', '84421e', 'a8602e', 'c8844a')
    bomba = B.trazo('barro_cocido', lambda xs, ys, tw, th, c, s: np.where(((xs * 3 + ys * 5 + s) % 11) == 0, 1,
                                                                        np.where(ys < 2, 3, 2)), barro)
    cb = c_gas + np.array((0, 3.2, 0.4))
    m.parte('bomba', 'gaster', tuple(cb))
    m.ovalo('bomba', tuple(cb), (2.6, 2.4, 2.6), bomba)
    cuerda = B.anillos('cuerda_bomba', rampa('3a2a14', '5a4424', '7e6236', '9e824a', 'c0a468'), paso=2)
    for dz in (-0.9, 0.9):
        m.caja('bomba', tuple(cb + np.array((0, -0.4, dz))), (5.6, 0.5, 0.5), cuerda)
    m.caja_desde('bomba', tuple(cb + np.array((0, 2.2, 0))), (1.2, 0.8, 1.2), B.liso('boca_bomba', barro, base=1))
    m.parte('chispa', 'bomba', tuple(cb + np.array((0.5, 4.2, -0.3))))
    m.viga('chispa', cb + np.array((0, 2.8, 0)), cb + np.array((0.5, 4.2, -0.3)), 0.5,
           B.anillos('mecha_p', rampa('2a1c0c', '4a3418', '6a4c24', '8a6a38', 'a8885a'), paso=2))
    fuego = B.luz('chispa_p', BRASA)
    m.caja('chispa', tuple(cb + np.array((0.5, 4.4, -0.3))), (0.9, 0.9, 0.9), fuego)
    anims_hormiga(m, tri, paso=0.45)
    s = m.anims['siempre']
    s.esc('chispa', [(0, 1, 1, 1), (0.1, 1.5, 1.5, 1.5), (0.2, 0.8, 0.8, 0.8), (0.35, 1.3, 1.3, 1.3), (0.5, 1, 1, 1),
                     (2.0, 1, 1, 1)])
    e = m.anim('especial', 1.0)
    e.esc('bomba', [(0, 1, 1, 1), (0.15, 1.1, 1.1, 1.1), (0.3, 1, 1, 1), (0.45, 1.15, 1.15, 1.15), (0.6, 1, 1, 1),
                    (0.75, 1.2, 1.2, 1.2), (1.0, 1.25, 1.25, 1.25)])
    e.esc('chispa', [(0, 1, 1, 1), (1.0, 2.2, 2.2, 2.2)])
    m.paso = 3.6

    def dib(px, filas, c):
        for x, f in ((6, 8), (9, 8)):
            px[x, f] = c('000000')
        for f in range(3, 7):
            for x in range(6, 10):
                px[x, f] = c('84421e')
        px[8, 2] = c('ffc84a')
    return terminar(m, raiz, 'Hormiga Polvorín', 'Powder Ant', (('56565e', '3e3e46', '2c2c32'), ('121214', '000000'), dib),
                    ((1.4, 1.2, 1.9), (0, 0.45, 0)),
                    particulas=(('chispa', chispa((255, 200, 74))), ('barro', esquirla((132, 66, 30))),
                                ('humo', nube((80, 80, 88)))),
                    poses=[('andar', 0.1), ('andar', 0.3), ('especial', 0.75), ('muerte', 1.0)])


def cabezona(raiz):
    """La Hormiga Cabezona: parda, con una cabeza que dobla la del resto, con la frente lisa y brillante, y unas
    mandíbulas largas como tenazas, dentadas por dentro."""
    m = B.Modelo('cabezona', K=2, ancho=128)
    m.escala = 1.15
    q = B.trazo('quitina_cabezona', quitina_fn(PARDA), PARDA)
    P = {'cuerpo': q, 'cabeza': q, 'gaster': q, 'pata': B.anillos('pata_cabezona', PARDA, paso=3)}
    tri, c_cab, c_gas = hormiga(m, P, cabeza=(3.4, 3.0, 2.8), ojo=ojo_brillante('ojo_hormiga'),
                                mandibula=B.trazo('tenaza', lambda xs, ys, tw, th, c, s: np.where((ys % 3) == 0, 0, 1), PARDA),
                                antena=B.anillos('antena_cabezona', PARDA, paso=2))
    # Los dientes de dentro de las tenazas.
    for lado, ld in LADOS:
        m.dientes(f'mandibula_{ld}', tuple(c_cab + np.array((lado * 1.5, -1.6, 3.4))),
                  tuple(c_cab + np.array((lado * 0.6, -1.6, 4.4))), 3, 0.8, (-lado, 0, 0.3), B.diente('diente_tenaza'))
    anims_hormiga(m, tri, paso=0.5)
    m.paso = 3.2

    def dib(px, filas, c):
        for f in range(3, 9):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('965424')
        for x, f in ((5, 6), (10, 6)):
            px[x, f] = c('000000')
        for x, f in ((5, 10), (6, 11), (9, 11), (10, 10)):
            px[x, f] = c('2a1406')
    return terminar(m, raiz, 'Hormiga Cabezona', 'Bighead Ant', (('c07a3e', '965424', '6e3a16'), ('2a1406', '140a02'), dib),
                    ((1.5, 1.2, 2.0), (0, 0.45, 0)),
                    particulas=(('astilla', esquirla((150, 84, 36))),))


def radiactiva(raiz):
    """La Hormiga Radiactiva: negra como el carbón, con marcas verdes que brillan en el tórax y en el gáster (el trébol
    del peligro, a su manera) y los ojos encendidos de verde."""
    m = B.Modelo('radiactiva', K=2, ancho=128)
    m.escala = 1.0
    R = juntar(NEGRA, VERDE)

    def marcas(xs, ys, tw, th, cara, s):
        if cara not in ('arriba', 'izq', 'der'):
            return np.zeros((th, tw), bool)
        u, v = (xs + 0.5) / tw - 0.5, (ys + 0.5) / th - 0.5
        a = np.arctan2(v, u)
        rr = np.hypot(u, v)
        return ((np.cos(3 * a) > 0.55) & (rr > 0.12) & (rr < 0.36)) | (rr < 0.06)
    q = B.trazo('quitina_radiactiva', quitina_fn(R, marca=marcas), R)
    P = {'cuerpo': q, 'cabeza': B.trazo('quitina_negra', quitina_fn(NEGRA), NEGRA), 'gaster': q,
         'pata': B.anillos('pata_negra', NEGRA, paso=3)}
    tri, c_cab, c_gas = hormiga(m, P, ojo=B.luz('ojo_radiactivo', VERDE), mandibula=B.liso('mandibula_negra', NEGRA, base=1),
                                antena=B.anillos('antena_negra', NEGRA, paso=2))
    anims_hormiga(m, tri)
    m.paso = 4.0

    def dib(px, filas, c):
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c('7aff5a')
        for x, f in ((7, 10), (8, 10), (6, 11), (9, 11), (7, 12), (8, 12)):
            px[x, f] = c('2ab82a')
    return terminar(m, raiz, 'Hormiga Radiactiva', 'Radiant Ant', (('2a2a34', '1c1c24', '121218'), ('040406', '000000'), dib),
                    ((1.4, 1.1, 1.9), (0, 0.4, 0)),
                    particulas=(('radiacion', chispa((122, 255, 90))),))


def brasa(raiz):
    """La Hormiga Brasa: roja, con las grietas de brasa que brillan por todo el cuerpo y el gáster encendido por dentro
    (como un carbón al rojo); va soltando chispas."""
    m = B.Modelo('brasa', K=2, ancho=128)
    m.escala = 1.0
    R = juntar(ROJA, BRASA)

    def grietas(xs, ys, tw, th, cara, s):
        return B.grietas(tw, th, s, cara, cuantas=max(1, (tw * th) // 60), giro=0.6, ramas=0.1)
    q = B.trazo('quitina_brasa', quitina_fn(R, marca=grietas), R)

    def ascua(xs, ys, tw, th, cara, s):
        idx = np.full((th, tw), 7)
        idx[((xs // 2 + ys // 2) % 3) == 0] = 8
        idx[((xs + ys * 3 + s) % 7) == 0] = 9
        return idx, np.ones((th, tw), bool)
    P = {'cuerpo': q, 'cabeza': q, 'gaster': B.trazo('ascua', ascua, R), 'pata': B.anillos('pata_roja', ROJA, paso=3)}
    tri, c_cab, c_gas = hormiga(m, P, ojo=ojo_brillante('ojo_hormiga'), mandibula=B.liso('mandibula_roja', ROJA, base=1),
                                antena=B.anillos('antena_roja', ROJA, paso=2))
    anims_hormiga(m, tri)
    m.paso = 4.0

    def dib(px, filas, c):
        for x, f in ((6, 6), (9, 6)):
            px[x, f] = c('000000')
        for x, f in ((4, 9), (5, 10), (10, 9), (11, 11), (7, 12), (8, 13)):
            px[x, f] = c('ffc84a')
    return terminar(m, raiz, 'Hormiga Brasa', 'Ember Ant', (('f06a40', 'd0321a', '9e1a0e'), ('3a0604', '1a0202'), dib),
                    ((1.4, 1.1, 1.9), (0, 0.4, 0)),
                    particulas=(('brasa', chispa((255, 150, 40))),))


MOBS = {'lancera': lancera, 'polvorin': polvorin, 'cabezona': cabezona, 'radiactiva': radiactiva, 'brasa': brasa}


def main():
    global CARPETA
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    CARPETA = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
    if CARPETA:
        os.makedirs(CARPETA, exist_ok=True)
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(MOBS)
    for p in pedidos:
        MOBS[p](raiz)


if __name__ == '__main__':
    main()

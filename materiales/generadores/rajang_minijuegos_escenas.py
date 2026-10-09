"""
Renders de la tercera ficha de Rajang (octubre de 2026). Juan, de la segunda:
"lo unico que me gusto fueron Suelo que se Hunde y Glifos del Templo; haz mas
propuestas para completar el ciclo de 4". Cuatro minijuegos mas para elegir dos,
en la plaza del Templo del Jaguar y con las ayudas de rajang_mecanicas_escenas
(la camara, Rajang del juego, los jugadores, los rotulos):

  pelota      Juego de Pelota: la cancha de los muros escalonados con el aro de
              piedra en lo alto; un jugador acaba de golpear la pelota de hule
              (el arco de puntos hasta el aro) y Rajang, al fondo, la devuelve
  roca        La Roca del Templo: una roca enorme baja rodando por la escalera de
              la piramide; un jugador la golpea de lado y el camino se tuerce
              hacia Rajang; otro se aparta de la linea
  calendario  La Piedra del Sol: el disco del calendario de piedra en pie detras
              de Rajang, con tres anillos de glifos que giran y la flecha de oro;
              tres jugadores, cada uno en su peana, paran su anillo
  crias       Las Crias de Jade: crias de jaguar de jade que corren por la plaza;
              una atrapada en su jaula de oro, dos jugadores persiguiendo a otras
              y una que llega a Rajang

Uso: python rajang_minijuegos_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rajang_mecanicas_escenas as me  # lee la raiz y la carpeta de salida de sys.argv
from rajang_mecanicas_escenas import (rm, ts, ta, ra, vr, SS, TAU, JADE, JADE_CLARO, ORO, ORO_CLARO, BLANCO, rotulo,
                                      pildora, guardar, jugador2, matriz_jugador, rajang_en, tex_halo, tex_aro,
                                      contorno, icono_glifo, capa_fina, texto_sombra, CORRER, GOLPE, SALTO)

AMBAR = (255, 186, 90)
ROJO = (255, 96, 80)
MIRAR = {'cabeza': {'rot': (-12, 0, 0)}, 'bi': {'rot': (-24, 0, -8)}, 'bd': {'rot': (-30, 0, 8)}}
AGARRAR = {'cabeza': {'rot': (14, 0, 0)}, 'bi': {'rot': (-80, 0, -14)}, 'bd': {'rot': (-80, 0, 14)},
           'pi': {'rot': (-36, 0, 0)}, 'pd': {'rot': (30, 0, 0)}}


# ----------------------------------------------------------------------
#  Ayudas: cajas giradas, bolas de pixeles y lineas de puntos
# ----------------------------------------------------------------------
def caja_mundo(c, hx, hy, hz, mat, cuadros=False):
    """Una caja con centro c y medios ejes hx, hy, hz (vectores): triangulos para
    ta.dibujar o, con cuadros, caras de cuatro puntos para ts.dibujar_mundo."""
    c = np.array(c, float)
    v = []
    for i in range(8):
        sx, sy, sz = (1 if i & 1 else -1), (1 if i & 2 else -1), (1 if i & 4 else -1)
        v.append(c + sx * np.array(hx) + sy * np.array(hy) + sz * np.array(hz))
    caras = [(0, 4, 6, 2), (1, 3, 7, 5), (0, 1, 5, 4), (2, 6, 7, 3), (0, 2, 3, 1), (4, 5, 7, 6)]
    out = []
    for a, b, cc, d in caras:
        if cuadros:
            out.append((np.array([v[a], v[b], v[cc], v[d]]), [(0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5)], mat))
        else:
            out += ta._cuad(v[a], v[b], v[cc], v[d], (0, 0), (0.5, 0), (0.5, 0.5), (0, 0.5), mat)
    return out


def bola_pixeles(c, r, mat, giro=0.0):
    """Lo redondo, a lo Minecraft: tres cajas cruzadas."""
    R = vr.Ry(giro)[:3, :3]
    ex, ey, ez = R @ np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), R @ np.array([0, 0, 1.0])
    out = []
    for kx, ky, kz in ((1.0, 0.75, 0.75), (0.75, 1.0, 0.75), (0.75, 0.75, 1.0)):
        out += caja_mundo(c, ex * r * kx, ey * r * ky, ez * r * kz, mat)
    return out


def a_mundo(qs):
    """Quads de ta (array, uv, mat) al formato de ts.dibujar_mundo (lista de puntos)."""
    return [([tuple(p) for p in P], UV, m) for P, UV, m in qs]


def puntos(lz, cam, camino, paso, halo, tam=0.16, k=0.9):
    """Una linea de puntos de luz por un camino de puntos del mundo."""
    resto = 0.0
    for a, b in zip(camino[:-1], camino[1:]):
        a, b = np.array(a, float), np.array(b, float)
        largo = np.linalg.norm(b - a)
        t = resto
        while t < largo:
            ta.cartel(lz, cam, a + (b - a) * (t / largo), tam, halo, k)
            t += paso
        resto = t - largo


def parabola(p0, p1, alto, n=24):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    return [p0 + (p1 - p0) * (i / n) + np.array([0, alto * 4 * (i / n) * (1 - i / n), 0]) for i in range(n + 1)]


def escenario(cam, lz, niebla, fase, piramide_z=50.0, arboles=True):
    escena = rm.plaza_templo(26, 70, 44) + ts.piramide(-4, piramide_z)
    if arboles:
        escena += ts._arboles((-32, 30, 17, 10), (32, 34, 18, 11), (-36, 4, 15, 9), (36, 8, 15, 9))
    ts.dibujar_mundo(lz, cam, escena, niebla, fase)


# ----------------------------------------------------------------------
#  1. Juego de Pelota
# ----------------------------------------------------------------------
def aro_piedra(cx, cy, cz, radio=1.6, grueso=0.45, n=14):
    """El aro de piedra de la cancha, en pie (su hueco mira a lo largo de la
    cancha, +z): un anillo de bloques, con una cenefa de oro."""
    qs = []
    for i in range(n):
        a = TAU * i / n
        c = np.array([cx + math.cos(a) * radio, cy + math.sin(a) * radio, cz])
        t = np.array([-math.sin(a), math.cos(a), 0.0])
        rad = np.array([math.cos(a), math.sin(a), 0.0])
        qs += caja_mundo(c, t * (radio * math.pi / n + 0.05), rad * grueso, np.array([0, 0, 0.32]), 'templo', True)
    for i in range(n):
        a = TAU * (i + 0.5) / n
        c = np.array([cx + math.cos(a) * (radio + grueso * 0.9), cy + math.sin(a) * (radio + grueso * 0.9), cz])
        qs += caja_mundo(c, np.array([0.12, 0, 0]), np.array([0, 0.12, 0]), np.array([0, 0, 0.36]), 'oro', True)
    return qs


def muro_cancha(x, z0, z1, lado):
    """El muro de la cancha: banqueta en talud (escalones) y el paramento alto."""
    qs = []
    largo = z1 - z0
    for k, (dentro, alto) in enumerate(((2.6, 0.8), (1.8, 1.6), (1.0, 2.4))):
        x0 = x - lado * dentro
        qs += ts.caja(min(x0, x0 + lado * 0.8), 0, z0, 0.8, alto, largo, 'templo')
    qs += ts.caja(x if lado > 0 else x - 1.2, 0, z0, 1.2, 6.0, largo, 'templo')
    qs += ts.caja(x if lado > 0 else x - 1.2, 6.0, z0 - 0.2, 1.2, 0.35, largo + 0.4, 'oro')
    return qs


def pelota(W=1600, H=900, fase=1, ojo=(-1.0, 6.2, -9.0), objetivo=(1.0, 3.0, 12.0), fov=62, nombre='pelota'):
    # la camara mira hacia +z: en la foto, +x queda a la izquierda
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 90)
    escenario(cam, lz, niebla, fase)
    # la cancha: dos muros a lo largo, con un aro de piedra en lo alto de cada uno
    mundo = muro_cancha(10.0, 0.0, 26.0, 1) + muro_cancha(-8.0, 0.0, 26.0, -1)
    ts.dibujar_mundo(lz, cam, mundo, niebla, fase)
    aro_c = np.array([8.2, 4.4, 13.0])
    ts.dibujar_mundo(lz, cam, aro_piedra(*aro_c), niebla, fase)
    aro2 = np.array([-6.2, 4.4, 13.0])
    ts.dibujar_mundo(lz, cam, aro_piedra(*aro2), niebla, fase)
    # Rajang al fondo de la cancha, de zarpazo: te la devuelve
    pose = ra.sumar(ra.pose_en('GARRA', 0.45), ra.cabeza(y=-18))
    rajang_en(lz, cam, 0.5, 0.0, 22.0, rm.guinada_hacia(0.2, -1), pose, fase, niebla=niebla)
    # el que acaba de golpearla, el que espera y el que corre a por ella
    golpea = np.array([2.6, 3.2])
    jugador2(lz, cam, matriz_jugador(golpea[0], golpea[1], rm.guinada_hacia(0.55, 1)), pose=GOLPE, espada=True,
             rot_espada=(-30, 0, 0), niebla=niebla)
    espera = np.array([-3.4, 5.5])
    jugador2(lz, cam, matriz_jugador(espera[0], espera[1], rm.guinada_hacia(0.6, 0.8)), pose=MIRAR, niebla=niebla)
    corre = np.array([5.8, 9.5])
    jugador2(lz, cam, matriz_jugador(corre[0], corre[1], rm.guinada_hacia(0.2, 1)), pose=CORRER, niebla=niebla)
    # la pelota de hule, en el aire, camino del aro
    camino = parabola((golpea[0], 1.6, golpea[1] + 0.6), aro_c, 4.2)
    bola = camino[6]
    ta.dibujar(lz, cam, bola_pixeles(bola, 0.95, 'basalto', giro=0.5), ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    ta.dibujar(lz, cam, bola_pixeles(bola, 0.97, 'fragmento', giro=0.5)[:12], ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    halo_o = tex_halo(ORO, ORO_CLARO)
    halo_j = tex_halo(JADE, JADE_CLARO)
    puntos(lz, cam, camino[8:], 0.6, halo_o, 0.2, 1.3)
    ta.cartel(lz, cam, aro_c, 3.4, halo_j, 0.55)
    ta.cartel(lz, cam, aro2, 3.0, halo_j, 0.3)
    # los botes que lleva (marcas en el suelo) y el golpe
    for (x, z) in ((1.0, 8.0), (3.5, 5.0)):
        ta.calco(lz, cam, x, z, 1.1, tex_aro(AMBAR, grueso=0.12, marcas=8), 1.0)
    ta.cartel(lz, cam, (golpea[0] + 0.3, 1.7, golpea[1] + 0.9), 1.0, me.CHISPA, 1.2)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 121, oscuro=0.2, rayos=False)
    rm.lineas_movimiento(img, cam, bola, camino[4] - camino[6], 10, 2.4, 122)
    rm.lineas_movimiento(img, cam, (corre[0], 1.1, corre[1] - 0.9), (0.1, 0, -1), 8, 2.0, 123)
    rotulo(img, cam, aro_c + np.array([0, 2.0, 0]), '¡POR EL ARO!', 10, -150, 52, ORO_CLARO, centro=True)
    rotulo(img, cam, bola, 'GOLPÉALA: SALE HACIA DONDE MIRAS', 120, 40, 30, BLANCO)
    rotulo(img, cam, (2.2, 0.0, 6.6), 'SI BOTA 3 VECES, REVIENTA', -160, 70, 30, (255, 214, 150))
    rotulo(img, cam, (0.5, 7.0, 22.0), 'RAJANG TE LA DEVUELVE', 90, -30, 30, JADE_CLARO)
    pildora(img, 300, 52, 'BOTES 2/3', 30, (255, 214, 150))
    pildora(img, W - 110, 52, '30 S', 34, ORO_CLARO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  2. La Roca del Templo
# ----------------------------------------------------------------------
def roca_grande(c, r, semilla, giro=0.0):
    """La roca del templo: una bola de pixeles de piedra con bloques sueltos encima."""
    qs = bola_pixeles(c, r, 'estrato', giro)
    rr = random.Random(semilla)
    for k in range(7):
        a, b = rr.uniform(0, TAU), rr.uniform(-1.0, 1.0)
        d = np.array([math.cos(a) * math.sqrt(1 - b * b), b, math.sin(a) * math.sqrt(1 - b * b)])
        qs += ta.roca_cubica(*(np.array(c) + d * r * 0.95), r * rr.uniform(0.22, 0.32), semilla=semilla + k, mat='roca')
    return qs


def roca(W=1600, H=900, fase=2, ojo=(3.0, 10.0, -15.0), objetivo=(0.5, 2.5, 14.0), fov=60, nombre='roca'):
    # la camara mira hacia +z: en la foto, +x queda a la izquierda
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(40, 100)
    escenario(cam, lz, niebla, fase, piramide_z=36.0)
    # el camino: baja recto de la escalera; donde la golpean, tuerce hacia Rajang
    golpe = np.array([-4.0, 10.0])
    rajang_p = np.array([8.0, 4.0])
    recta = [(-4.0, 0.2, 24.0), (-4.0, 0.2, golpe[1])]
    tuerce = [(golpe[0], 0.2, golpe[1]), (rajang_p[0] - 1.5, 0.2, rajang_p[1] + 1.0)]
    sigue = [(golpe[0], 0.2, golpe[1]), (-4.0, 0.2, -6.0)]
    roca_c = np.array([-4.0, 2.4, 19.0])
    r = random.Random(41)
    # Rajang, de espaldas a la roca, rugiendo a los jugadores
    pose = ra.sumar(ra.pose_en('RUGIDO', 0.7), ra.cabeza(y=14))
    rajang_en(lz, cam, rajang_p[0], 0.0, rajang_p[1], rm.guinada_hacia(0.3, -1), pose, fase, niebla=niebla)
    ta.dibujar(lz, cam, roca_grande(roca_c, 2.3, 51, giro=0.4), ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    piedras = []
    for k in range(10):
        piedras += ta.roca_cubica(-4.0 + r.uniform(-2.5, 2.5), r.uniform(0.2, 2.5), roca_c[2] + r.uniform(1.5, 5.0),
                                  r.uniform(0.15, 0.4), semilla=900 + k, mat='roca')
    ta.dibujar(lz, cam, piedras, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    # el que la golpea de lado y el que se aparta de la linea
    jugador2(lz, cam, matriz_jugador(golpe[0] - 1.6, golpe[1] - 0.6, rm.guinada_hacia(1, 0.5)), pose=GOLPE, espada=True,
             rot_espada=(-30, 0, 0), niebla=niebla)
    jugador2(lz, cam, matriz_jugador(-1.2, 2.0, rm.guinada_hacia(1, -0.3)), pose=CORRER, niebla=niebla)
    halo_o = tex_halo(ORO, ORO_CLARO)
    halo_r = tex_halo(ROJO, (255, 210, 200))
    puntos(lz, cam, recta, 0.9, halo_r, 0.18, 1.0)
    puntos(lz, cam, sigue, 0.9, halo_r, 0.12, 0.35)
    puntos(lz, cam, tuerce, 0.8, halo_o, 0.24, 1.3)
    ta.cartel(lz, cam, (golpe[0] - 0.6, 1.0, golpe[1]), 1.6, me.CHISPA, 1.0)
    ta.calco(lz, cam, rajang_p[0], rajang_p[1], 3.6, tex_aro(ORO, grueso=0.06, marcas=12, relleno=0.15), 1.0)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 131, oscuro=0.2, rayos=False)
    ta.polvo_en(img, cam, [(roca_c[0], 0.4, roca_c[2] + 2.0, 3.0), (-4.0, 0.0, 24.0, 2.5)], SS, (128, 110, 80), 132)
    rm.lineas_movimiento(img, cam, roca_c, (0, 0.3, 1), 12, 4.0, 133, (230, 220, 190), 4)
    rotulo(img, cam, roca_c + np.array([0, 2.6, 0]), '¡RUEDA LA ROCA!', 0, -80, 50, ORO_CLARO, centro=True)
    rotulo(img, cam, (golpe[0] - 1.6, 2.0, golpe[1] - 0.6), 'GOLPÉALA DE LADO: SE DESVÍA', 60, 90, 30, BLANCO)
    rotulo(img, cam, (rajang_p[0], 6.5, rajang_p[1]), 'SI LE DA A ÉL: ATURDIDO', -60, -110, 32, ORO_CLARO)
    rotulo(img, cam, (-4.0, 0.2, -2.0), 'A TI TE APLASTA', 40, 40, 30, (255, 170, 160))
    pildora(img, W - 110, 52, '20 S', 34, ORO_CLARO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  3. La Piedra del Sol
# ----------------------------------------------------------------------
ANILLOS = (('jaguar', 'sol', 'luna', 'espiral', 'ojo', 'piramide'),
           ('sol', 'jaguar', 'ojo', 'luna', 'piramide', 'espiral'),
           ('luna', 'ojo', 'jaguar', 'piramide', 'espiral', 'sol'))
RADIOS = (2.7, 4.8, 6.9)


def disco(cx, cy, cz, radio=8.0, paso=0.8):
    """El calendario de piedra: un disco de bloques en pie (mira a -z), con la
    cenefa de oro entre anillo y anillo."""
    qs = []
    n = int(radio / paso) + 1
    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            x, y = i * paso, j * paso
            d = math.hypot(x, y)
            if d > radio:
                continue
            mat = 'oro' if any(abs(d - r_ - 0.85) < 0.35 for r_ in RADIOS[:2]) or radio - d < 0.5 else 'templo'
            hond = 0.4 if mat == 'templo' else 0.5
            qs += ts.caja(cx + x - paso / 2, cy + y - paso / 2, cz, paso, paso, hond, mat)
    return qs


def calendario(W=1600, H=900, fase=3, ojo=(0.0, 5.0, -9.0), objetivo=(0.0, 6.5, 14.0), fov=62, nombre='calendario'):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(36, 95)
    escenario(cam, lz, niebla, fase)
    centro = np.array([0.0, 9.4, 24.0])
    ts.dibujar_mundo(lz, cam, disco(*centro) + ts.caja(-2.5, 0, 23.6, 5.0, 1.6, 1.8, 'templo'), niebla, fase)
    # las tres peanas, una por anillo, cada una con su jugador
    peanas = [(-5.5, 8.0), (0.0, 7.0), (5.5, 8.0)]
    mundo = []
    for (x, z) in peanas:
        mundo += ts.caja(x - 0.8, 0, z - 0.8, 1.6, 1.0, 1.6, 'templo') + ts.caja(x - 0.5, 1.0, z - 0.5, 1.0, 0.25, 1.0, 'oro')
    ts.dibujar_mundo(lz, cam, mundo, niebla, fase)
    pose = ra.sumar(ra.pose_en('RUGIDO', 0.3), ra.cabeza(y=-6))
    rajang_en(lz, cam, 11.5, 0.0, 17.0, rm.guinada_hacia(-0.6, -1), pose, fase, niebla=niebla)
    halo_j = tex_halo(JADE, JADE_CLARO)
    halo_o = tex_halo(ORO, ORO_CLARO)
    qs_jug = []
    for k, (x, z) in enumerate(peanas):
        g = GOLPE if k != 2 else MIRAR
        qs_jug.append(jugador2(lz, cam, matriz_jugador(x, z - 1.6, rm.guinada_hacia(0, 1)), pose=g, espada=(k != 2),
                               rot_espada=(-30, 0, 0), niebla=niebla))
        ta.cartel(lz, cam, (x, 1.4, z), 1.2, halo_o if k < 2 else halo_j, 0.9)
    # la flecha de oro arriba del disco
    flecha = centro + np.array([0, 8.7, -0.6])
    ta.cartel(lz, cam, flecha, 1.2, halo_o, 1.2)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 141, oscuro=0.25, rayos=False)
    # los glifos de cada anillo (pegados al disco, en pantalla) y la flecha
    for a_i, (radio, glifos) in enumerate(zip(RADIOS, ANILLOS)):
        giro = (0.0, 0.35, -0.9)[a_i]
        for g_i, g in enumerate(glifos):
            ang = math.pi / 2 + giro + TAU * g_i / len(glifos)
            p = centro + np.array([math.cos(ang) * radio, math.sin(ang) * radio, -0.5])
            sx, sy, _ = cam.proyectar(p)
            arriba = abs(((ang - math.pi / 2) + math.pi) % TAU - math.pi) < 0.2
            col = ORO_CLARO if (g == 'jaguar' and arriba) else (JADE_CLARO if a_i < 2 else (160, 190, 170))
            ic = icono_glifo(g, 46, col)
            img.alpha_composite(ic, (int(sx / SS - 23), int(sy / SS - 23)))
    fx, fy, _ = cam.proyectar(flecha)
    fx, fy = fx / SS, fy / SS

    def dib(d, k):
        d.polygon([((fx - 26) * k, (fy - 20) * k), ((fx + 26) * k, (fy - 20) * k), (fx * k, (fy + 22) * k)],
                  fill=(*ORO, 255), outline=(60, 40, 6, 255))
    capa_fina(img, dib)
    for a_i, radio in enumerate(RADIOS):
        me.arcos(img, cam, centro + np.array([0, 0, -0.6]), radio + 0.55, (0.4, 2.0, 3.6)[a_i], 2,
                 ORO_CLARO if a_i < 2 else JADE_CLARO)
    rotulo(img, cam, flecha + np.array([0, 0.8, 0]), 'EL JAGUAR, BAJO LA FLECHA', 0, -60, 40, ORO_CLARO, linea=False,
           centro=True)
    rotulo(img, cam, (-5.5, 2.4, 6.4), 'PARADO', 90, -60, 30, ORO_CLARO)
    rotulo(img, cam, (0.0, 2.4, 5.4), 'PARADO', 60, -40, 30, ORO_CLARO)
    rotulo(img, cam, (5.5, 2.4, 6.4), 'AÚN GIRA: ¡AHORA!', -150, -60, 30, JADE_CLARO)
    rotulo(img, cam, (11.5, 8.0, 17.0), 'INMUNE MIENTRAS GIRA', -30, -60, 28, JADE_CLARO)
    rotulo(img, cam, (0.0, 0.4, 7.0), 'UNO POR ANILLO: GOLPEA TU PEANA PARA PARARLO', 0, 90, 30, BLANCO)
    pildora(img, W - 110, 52, '20 S', 34, ORO_CLARO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  4. Las Crias de Jade
# ----------------------------------------------------------------------
def cria(lz, cam, x, z, guinada, pose, fase, escala=0.16, niebla=None):
    """Una cria de jade: Rajang del juego, pequeno."""
    M = vr.entidad_a_mundo(x, 0, z, guinada) @ vr.S(escala)
    tex, brillo = rm.piel(fase)
    qs = me.rj.quads(rm.con_fase(pose, fase), rm.UV_ATLAS, rm.ALTO_ATLAS, M)
    for Pq, UVq, _, mat in qs:
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), ts.LUCES_SELVA, ts.AMB_SELVA)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[i] for i in tri], [UVq[i] for i in tri], tex, luz, brillo, niebla, brillo=1.2)
    return qs


def jaula(x, z, lado=1.3, alto=1.4):
    qs = ts.caja(x - lado / 2, 0, z - lado / 2, lado, 0.15, lado, 'oro') + ts.caja(x - lado / 2, alto, z - lado / 2, lado, 0.15, lado, 'oro')
    for i in range(4):
        for j in range(4):
            if 0 < i < 3 and 0 < j < 3:
                continue
            bx, bz = x - lado / 2 + i * lado / 3, z - lado / 2 + j * lado / 3
            qs += ts.caja(bx - 0.04, 0.15, bz - 0.04, 0.08, alto - 0.15, 0.08, 'oro')
    return qs


def crias(W=1600, H=900, fase=2, ojo=(1.5, 6.0, -8.0), objetivo=(-0.5, 1.0, 12.0), fov=60, nombre='crias'):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 90)
    escenario(cam, lz, niebla, fase)
    # Rajang al fondo, llamandolas
    pose = ra.sumar(ra.pose_en('RUGIDO', 0.6), ra.cabeza(y=10))
    rajang_en(lz, cam, -2.0, 0.0, 22.0, rm.guinada_hacia(0.1, -1), pose, fase, niebla=niebla)
    r = random.Random(61)
    corre = ra.pose_en('CORRER', 0.25)
    sitios = [(3.0, 6.0, 0.8, -0.6), (-4.5, 8.0, -0.5, 1.0), (6.0, 12.0, -1.0, 0.4), (-1.0, 12.5, 0.2, 1.0),
              (-7.0, 14.0, 0.6, 0.8), (-2.0, 18.0, 0.1, 1.0)]
    for (x, z, gx, gz) in sitios:
        cria(lz, cam, x, z, rm.guinada_hacia(gx, gz), ra.pose_en('CORRER', r.uniform(0, 0.8)), fase, niebla=niebla)
    # una atrapada en su jaula de oro
    cria(lz, cam, 5.0, 3.0, rm.guinada_hacia(-1, -0.2), ra.pose_en('REPOSO', 1.0), fase, niebla=niebla)
    ts.dibujar_mundo(lz, cam, jaula(5.0, 3.0), niebla, fase)
    # dos que las persiguen
    qs_a = jugador2(lz, cam, matriz_jugador(1.6, 4.0, rm.guinada_hacia(0.6, 0.8)), pose=AGARRAR, niebla=niebla)
    jugador2(lz, cam, matriz_jugador(-5.5, 5.0, rm.guinada_hacia(0.4, 1)), pose=CORRER, niebla=niebla)
    halo_j = tex_halo(JADE, JADE_CLARO)
    halo_o = tex_halo(ORO, ORO_CLARO)
    halo_r = tex_halo(ROJO, (255, 210, 200))
    for (x, z, gx, gz) in sitios:
        ta.cartel(lz, cam, (x, 0.5, z), 1.0, halo_j, 0.55)
    ta.cartel(lz, cam, (5.0, 0.8, 3.0), 1.6, halo_o, 0.6)
    puntos(lz, cam, [(-2.0, 0.3, 18.0), (-2.0, 0.3, 20.5)], 0.5, halo_r, 0.16, 1.0)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 151, oscuro=0.2, rayos=False)
    for k, (x, z, gx, gz) in enumerate(sitios[:4]):
        rm.lineas_movimiento(img, cam, (x, 0.5, z), (-gx, 0, -gz), 5, 1.2, 152 + k)
    contorno(img, cam, qs_a, ORO_CLARO, grosor=3, halo=0.6, lz=lz)
    rotulo(img, cam, (3.0, 1.0, 6.0), '¡ATRÁPALA! CLIC DERECHO', 170, -40, 34, ORO_CLARO)
    rotulo(img, cam, (5.0, 1.6, 3.0), 'ATRAPADA', -120, -60, 30, ORO_CLARO)
    rotulo(img, cam, (-7.0, 0.6, 14.0), 'CORREN Y ESQUIVAN', -40, -150, 28, JADE_CLARO)
    rotulo(img, cam, (-2.0, 1.0, 19.5), 'SI LLEGA A ÉL: FURIA', 170, -170, 30, (255, 170, 160))
    pildora(img, 330, 52, 'CRÍAS 1/7', 30, ORO_CLARO)
    pildora(img, W - 110, 52, '20 S', 34, ORO_CLARO)
    guardar(img, nombre)


ESCENAS = {'pelota': pelota, 'roca': roca, 'calendario': calendario, 'crias': crias}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
        print('ok', nombre, flush=True)

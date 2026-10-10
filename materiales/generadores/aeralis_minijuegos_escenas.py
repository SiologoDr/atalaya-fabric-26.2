"""
Renders de la ficha del cuarto minijuego de Aeralis (10-10-2026). De la
tercera ficha de mecanicas Juan se queda con Ocelos, Pararrayos y Veletas del
Vendaval, y falta uno. Cuatro juegos que conoce todo el mundo, distintos de lo
que ya tienen los cuatro jefes y de lo descartado:

  comba    La Comba del Vendaval (saltar a la comba): dos tornados en los
           extremos hacen girar una cuerda de rayo; una fila de jugadores salta
           cuando pasa por debajo y uno tropieza (Paralisis)
  volante  El Volante (badminton): le lanza un volante gigante hecho de una
           escama con plumas; donde va a caer sale un aro en el suelo y el que
           esta dentro se lo devuelve de un golpe
  chispa   La Chispa (patata caliente): una chispa de tormenta le cae a uno
           encima con su cuenta atras; la pasa de un golpe a un companero
  lobo     ¿Vendaval, estas? ("juguemos en el bosque mientras el lobo no
           esta"): posada con las alas cerradas, se viste; mientras, a pegarle;
           cuando dice "¡SI!", todos fuera del circulo

Usa las ayudas de aeralis_mecanicas_escenas (la Aeralis del juego, los
jugadores, los rayos, los rotulos y la composicion con el cielo de tormenta).

Uso: python aeralis_minijuegos_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aeralis_mecanicas_escenas as am  # lee la raiz y la carpeta de salida de sys.argv
from aeralis_mecanicas_escenas import (vr, nm, ne, ve, rm, aeralis, cinta3d, billboard, cuadrado_suelo, rayo,
                                       tex_plano, tex_aro, tex_halo, trans, brillo, componer, pantalla, rotulo,
                                       titular, pildora, leyenda, leyenda_columna, jugador3, guinada_hacia,
                                       relampago, chispazo, chispas_cuerpo, tornado_color, en, claro, oscuro,
                                       COLOR_FASE, BLANCO, SOMBRA, ROJO, LUCES, AMB, SS, FUENTE, Y_VUELO_NUEVA,
                                       MIRAR_ARRIBA, GOLPE_ALTO, SACUDIDO, guardar)

TAU = math.tau

# Poses de los jugadores
SALTO = {'cabeza': {'rot': (-12, 0, 0)}, 'bi': {'rot': (-140, 0, -24)}, 'bd': {'rot': (-140, 0, 24)},
         'pi': {'rot': (-40, 0, 0)}, 'pd': {'rot': (-30, 0, 0)}}
SALTO_ALTO = {'cabeza': {'rot': (-6, 0, 0)}, 'bi': {'rot': (-30, 0, -40)}, 'bd': {'rot': (-30, 0, 40)},
              'pi': {'rot': (-56, 0, 0)}, 'pd': {'rot': (-44, 0, 0)}}
ESPERA = {'cabeza': {'rot': (-4, 0, 0)}, 'bi': {'rot': (-14, 0, -10)}, 'bd': {'rot': (-20, 0, 10)},
          'pi': {'rot': (-10, 0, 0)}, 'pd': {'rot': (10, 0, 0)}}
CORRE = {'cabeza': {'rot': (-6, 0, 0)}, 'bi': {'rot': (50, 0, -6)}, 'bd': {'rot': (-60, 0, 6)},
         'pi': {'rot': (-50, 0, 0)}, 'pd': {'rot': (44, 0, 0)}}
PASA = {'cabeza': {'rot': (-10, 0, 0)}, 'bi': {'rot': (-20, 0, -10)}, 'bd': {'rot': (-112, 0, -10)},
        'pi': {'rot': (-18, 0, 0)}, 'pd': {'rot': (16, 0, 0)}}
EN_ALTO = {'cabeza': {'rot': (-30, 0, 0)}, 'bi': {'rot': (-170, 0, -12)}, 'bd': {'rot': (-170, 0, 12)},
           'pi': {'rot': (-4, 0, 0)}, 'pd': {'rot': (4, 0, 0)}}
TAJO = {'cabeza': {'rot': (-14, 0, 0)}, 'bi': {'rot': (-30, 0, -12)}, 'bd': {'rot': (-150, 0, 30)},
        'pi': {'rot': (-24, 0, 0)}, 'pd': {'rot': (20, 0, 0)}}


def cuerda(lz, cam, pts, col, ancho, glow=1.0, alfa=1.0, niebla=None):
    """Una cuerda de rayo por los puntos: el velo ancho del color, el cuerpo claro y el alma casi blanca."""
    trans(lz, cam, cinta3d(pts, ancho * 4.0, cam), tex_plano(col, 60), 0.5 * alfa, niebla, 0.45 * glow)
    trans(lz, cam, cinta3d(pts, ancho * 1.7, cam), tex_plano(claro(col, 0.45)), 0.85 * alfa, niebla, 0.8 * glow)
    trans(lz, cam, cinta3d(pts, ancho * 0.6, cam), tex_plano(claro(col, 0.92)), 1.0 * alfa, niebla, 1.3 * glow)


def mancha(lz, cam, x, z, r=0.6):
    trans(lz, cam, cuadrado_suelo(x, z, r, y=0.06), am.tex_mancha(), 1.0, None, 0.0)


def escena_base(cam_ojo, cam_obj, W, H, fov=64, columnas=True):
    cam = vr.Camara(ojo=cam_ojo, objetivo=cam_obj, fov=fov, ancho=W * SS, alto=H * SS)
    lz = vr.Lienzo(W * SS, H * SS)
    niebla = ve.NieblaCielo(26, 64)
    ve.suelo(lz, cam, niebla=niebla)
    if columnas:
        for i, (x, z, alto, rota) in enumerate(((-19, 24, 5, True), (19, 26, 3, True))):
            nm.dibujar(lz, cam, ve.columna(x, z, alto, rota, i), LUCES, AMB, niebla)
    return cam, lz, niebla


# ----------------------------------------------------------------------
#  1. La Comba del Vendaval
#
#  Dos tornados en los extremos de la cima hacen girar una cuerda de rayo,
#  como dos ninas con la comba. Una fila de jugadores en medio salta cuando la
#  cuerda pasa barriendo el suelo; uno no ha saltado: tropieza, Paralisis. Ella,
#  detras y en alto, marca el ritmo. Arriba, la vuelta que va.
# ----------------------------------------------------------------------
def comba(W=1600, H=900, fase=4):
    col = COLOR_FASE[fase]
    rayo_c = claro(col, 0.25)
    # la camara, baja y de frente a la fila: en la foto, +x queda a la izquierda
    cam, lz, niebla = escena_base((0.4, 1.1, 0.5), (0.0, 3.4, 14.0), W, H, fov=72)
    ZF = 9.0
    EJE_Y = 2.3
    XT = 10.5
    # los dos tornados que dan a la comba
    for k, x in enumerate((XT, -XT)):
        tornado_color(lz, cam, x, ZF, 9.0, col, niebla, giro=k * 1.3, r1=2.2, semilla=k + 3)
    # ella, detras y en alto, de cara: marca el ritmo
    ax_, ay_, az_ = 0.0, Y_VUELO_NUEVA + 4.5, ZF + 17.0
    g_ae = guinada_hacia(cam.ojo[0] - ax_, cam.ojo[2] - az_)
    aeralis(lz, cam, 'despues', ax_, ay_, az_, g_ae, pose=rm.HEROICA, fase=fase, niebla=ve.NieblaCielo(40, 120))
    # la fila que salta (la cuerda pasa por debajo) y el que ha tropezado
    saltan = [(-6.6, 0.95, SALTO_ALTO), (-3.9, 0.75, SALTO), (-1.2, 1.05, SALTO_ALTO), (1.4, 0.8, SALTO),
              (6.6, 0.9, SALTO_ALTO)]
    for x, y, pose in saltan:
        mancha(lz, cam, x, ZF)
        jugador3(lz, cam, x, ZF, guinada_hacia(cam.ojo[0] - x, cam.ojo[2] - ZF), y=y, pose=pose, niebla=niebla)
    trope = (4.0, ZF)
    jugador3(lz, cam, trope[0], trope[1], guinada_hacia(cam.ojo[0] - trope[0], cam.ojo[2] - trope[1]) + 14,
             pose=SACUDIDO, niebla=niebla)

    # la cuerda: gira alrededor del eje entre los tornados; ahora barre el suelo, y detras sus estelas
    def cuerda_en(theta, jitter, semilla):
        r = random.Random(semilla)
        pts = []
        for s in np.linspace(0, 1, 48):
            x = XT - 2 * XT * s
            f = 4 * s * (1 - s)
            rad = (EJE_Y - 0.15) * f ** 0.7
            p = np.array([x, EJE_Y - rad * math.cos(theta), ZF - rad * math.sin(theta)])
            if 0.03 < s < 0.97:
                p += np.array([0, r.uniform(-1, 1), r.uniform(-1, 1)]) * jitter
            pts.append(p)
        return pts
    for k, th in enumerate((1.15, 0.75, 0.42)):
        cuerda(lz, cam, cuerda_en(th, 0.05, 30 + k), col, 0.07, glow=0.5, alfa=0.25 + 0.15 * k, niebla=None)
    pts = cuerda_en(0.08, 0.09, 7)
    cuerda(lz, cam, pts, rayo_c, 0.085, glow=1.2)
    # donde toca al que tropieza: chispazo y arcos
    toca = min(pts, key=lambda p: abs(p[0] - trope[0]))
    chispazo(lz, cam, toca + np.array([0, 0.2, 0]), claro(col, 0.3), 0.8)
    chispas_cuerpo(lz, cam, np.array([trope[0], 0.95, trope[1]]), col, 9, n=12, radio=0.7)
    img = componer(lz, cam, W, H, 211, fase, rayos=0.9, estelas=40)
    titular(img, W / 2, 92, '¡SALTAD!', 108, BLANCO, borde=col)
    rotulo(img, cam, pts[30], 'LA CUERDA DE RAYO BARRE EL SUELO', -60, 150, 38, claro(col, 0.45))
    rotulo(img, cam, np.array([trope[0] - 0.2, 1.7, trope[1]]), 'NO SALTÓ: PARÁLISIS', 120, -120, 38, claro(ROJO, 0.4))
    rotulo(img, cam, np.array([XT, 6.0, ZF]), 'SUS TORNADOS DAN A LA COMBA', 40, -90, 34, BLANCO)
    pildora(img, W - 200, 60, 'VUELTA 7/12', 40, BLANCO, borde=(*claro(col, 0.2), 230))
    leyenda(img, W / 2, H - 70, [('CADA VUELTA, MÁS DEPRISA', col), ('MÁS DE LA MITAD SIN TROPEZAR: ATURDIDA', (110, 230, 130))],
            28)
    guardar(img, 'comba')


# ----------------------------------------------------------------------
#  2. El Volante (badminton)
#
#  Le pega con el ala a un volante gigante (una escama con su corona de
#  plumas) y lo manda en arco al grupo. Donde va a caer se enciende un aro en
#  el suelo; el que esta dentro lo devuelve de un golpe en el momento justo.
#  Cada devolucion, ella lo manda mas deprisa. Arriba, el peloteo.
# ----------------------------------------------------------------------
def tex_pluma(color, n=64):
    """Una pluma del volante: el canon claro en medio y las barbas con su veta."""
    yy, xx = np.mgrid[0:n, 0:n]
    u, v = (xx + 0.5) / n, (yy + 0.5) / n
    ancho = 0.5 * np.sin(np.clip(v, 0, 1) * math.pi) ** 0.6
    dentro = np.abs(u - 0.5) < ancho * 0.92
    canon = np.abs(u - 0.5) < 0.035
    veta = (np.abs(((u - 0.5) * 9 + v * 6) % 1.0 - 0.5) < 0.12)
    col = np.ones((n, n, 3)) * np.array(color, float)
    col[veta & dentro] = claro(color, 0.35)
    col[canon] = claro(color, 0.85)
    borde = dentro & (np.abs(u - 0.5) > ancho * 0.8)
    col[borde] = oscuro(color, 0.25)
    return am._rgba(col, dentro * 0.95)


def tex_corcho(n=64):
    """La base del volante: una bola de oro con su brillo arriba a la izquierda."""
    yy, xx = np.mgrid[0:n, 0:n]
    u, v = (xx + 0.5) / n * 2 - 1, (yy + 0.5) / n * 2 - 1
    d = np.hypot(u, v)
    luz = np.clip(1 - np.hypot(u + 0.35, v + 0.35) / 1.2, 0, 1)
    col = np.array((176, 120, 40), float)[None, None, :] * (0.55 + 0.45 * luz[..., None]) + \
        np.array((255, 240, 200), float)[None, None, :] * (luz[..., None] ** 4) * 0.8
    col = np.clip(col, 0, 255)
    return am._rgba(col, (d < 1.0) * 1.0)


def volante_mundo(lz, cam, base, dirc, col, niebla, escala=1.0):
    """El volante: la base de oro delante (hacia 'dirc', por donde vuela) y la corona de plumas detras."""
    dirc = dirc / np.linalg.norm(dirc)
    a = np.cross(dirc, [0, 1, 0])
    if np.linalg.norm(a) < 1e-3:
        a = np.array([1.0, 0, 0])
    a /= np.linalg.norm(a)
    b = np.cross(dirc, a)
    plumas = []
    n = 10
    for i in range(n):
        t = TAU * i / n
        e = a * math.cos(t) + b * math.sin(t)
        raiz = base - dirc * 0.25 * escala + e * 0.32 * escala
        punta = base - dirc * 1.9 * escala + e * 1.05 * escala
        lado = np.cross(punta - raiz, e)
        lado /= np.linalg.norm(lado)
        P = [raiz - lado * 0.12 * escala, raiz + lado * 0.12 * escala, punta + lado * 0.36 * escala,
             punta - lado * 0.36 * escala]
        plumas.append(([tuple(q) for q in P], [(0.3, 0), (0.7, 0), (1, 1), (0, 1)]))
    plumas.sort(key=lambda q: -cam.proyectar(np.mean(q[0], axis=0))[2])
    trans(lz, cam, plumas, tex_pluma(claro(col, 0.55)), 0.95, niebla, 0.25)
    trans(lz, cam, [billboard(base, 0.42 * escala, cam)], tex_corcho(), 1.0, niebla, 0.2)


def volante(W=1600, H=900, fase=3):
    col = COLOR_FASE[fase]
    oro = (255, 214, 120)
    # la camara, detras del grupo, mira hacia ella: en la foto, +x queda a la izquierda
    cam, lz, niebla = escena_base((-2.0, 2.4, -5.0), (1.5, 6.0, 16.0), W, H, fov=66)
    ax_, ay_, az_ = 4.0, Y_VUELO_NUEVA + 2.5, 25.0
    g_ae = guinada_hacia(cam.ojo[0] - ax_, cam.ojo[2] - az_) - 20
    aeralis(lz, cam, 'despues', ax_, ay_, az_, g_ae, pose=rm.HEROICA, fase=fase, niebla=ve.NieblaCielo(40, 120))
    M_ae = vr.T(0, ay_, 0) @ vr.entidad_a_mundo(ax_, 0, az_, g_ae)
    pecho = (M_ae @ rm.matrices(rm.HEROICA)['nucleo'] @ np.array([0, 0, 0, 1.0]))[:3]
    salida = pecho + np.array([-3.0, -1.0, -1.5])
    # donde va a caer: el aro del suelo, y el que esta dentro, con la espada atras para devolverlo
    caida = np.array([-2.6, 0.0, 6.5])
    trans(lz, cam, cuadrado_suelo(caida[0], caida[2], 2.0), tex_aro(oro, 128, 0.08, 16, 60), 0.95, None, 1.0)
    brillo(lz, cam, cuadrado_suelo(caida[0], caida[2], 1.9, y=0.09), tex_halo(oro, 128, 1.4), 0.55)
    golpea = (caida[0] + 0.3, caida[2] - 0.4)
    jugador3(lz, cam, golpea[0], golpea[1], guinada_hacia(salida[0] - golpea[0], salida[2] - golpea[1]), pose=TAJO,
             espada=True, niebla=niebla)
    # los demas, repartidos y atentos al volante
    for x, z in ((2.8, 4.0), (5.6, 9.0), (-6.0, 10.5)):
        jugador3(lz, cam, x, z, guinada_hacia(salida[0] - x, salida[2] - z), pose=MIRAR_ARRIBA, espada=True,
                 niebla=niebla)
    # la trayectoria: de su ala al aro, en arco, con el volante bajando
    def arco(t):
        p = salida + (caida + np.array([0, 1.6, 0]) - salida) * t
        return p + np.array([0, 3.5 * 4 * t * (1 - t), 0])
    ts = np.linspace(0, 1, 60)
    motas = [billboard(arco(t), 0.13, cam) for t in ts[2:-4:2]]
    brillo(lz, cam, motas, tex_halo(claro(oro, 0.4), 16, 1.0), 1.4)
    t0 = 0.8
    p0 = arco(t0)
    volante_mundo(lz, cam, p0, arco(t0 + 0.02) - p0, col, niebla, escala=1.7)
    # su estela de viento
    est = [arco(t) for t in np.linspace(t0 - 0.16, t0 - 0.02, 12)]
    trans(lz, cam, cinta3d(est, 0.32, cam), tex_plano(claro(col, 0.5), 90), 0.6, None, 0.4)
    # la vuelta que se le devolvera (punteado verde, hacia ella)
    vuelta = [caida + np.array([0, 1.6, 0]) + (salida - caida - np.array([0, 1.6, 0])) * t + np.array([0, 5.0 * 4 * t * (1 - t), 0])
              for t in np.linspace(0.12, 0.85, 22)]
    brillo(lz, cam, [billboard(q, 0.06, cam) for q in vuelta[::2]], tex_halo((120, 235, 140), 16, 1.0), 1.0)
    img = componer(lz, cam, W, H, 221, fase, rayos=0.6, estelas=40)
    titular(img, W / 2, 92, '¡DEVUÉLVESELO!', 100, BLANCO, borde=col)
    rotulo(img, cam, p0, 'SU VOLANTE: UNA ESCAMA CON PLUMAS', -330, -40, 38, claro(col, 0.5))
    rotulo(img, cam, caida, 'AQUÍ CAE: EL QUE ESTÁ DENTRO, ¡GOLPE!', 140, -30, 38, oro)
    pildora(img, W - 210, 60, 'PELOTEO 6/10', 40, BLANCO, borde=(*claro(col, 0.2), 230))
    leyenda(img, W / 2, H - 70, [('CADA VUELTA, MÁS DEPRISA', col), ('10 SEGUIDAS: SE LE ESCAPA Y LE DA', (110, 230, 130))],
            28)
    guardar(img, 'volante')


# ----------------------------------------------------------------------
#  3. La Chispa (patata caliente)
#
#  Una chispa de tormenta le cae a uno encima con su cuenta atras. Antes de
#  que reviente, la pasa de un golpe a un companero: salta de uno a otro y
#  cada pase la carga. Cargada, el que la lleva se la devuelve a ella.
# ----------------------------------------------------------------------
def chispa_mundo(lz, cam, c, col, semilla, tam=0.7):
    """La chispa: una bola de rayos que chisporrotea."""
    brillo(lz, cam, [billboard(c, tam * 2.6, cam)], tex_halo(col, 64, 1.6), 0.5)
    brillo(lz, cam, [billboard(c, tam * 1.2, cam)], tex_halo(claro(col, 0.6), 64, 1.2), 1.0)
    brillo(lz, cam, [billboard(c, tam * 0.5, cam)], tex_halo((255, 255, 255), 32, 1.0), 1.4)
    r = random.Random(semilla)
    for k in range(9):
        a = r.uniform(0, TAU)
        e = r.uniform(-1, 1)
        d = np.array([math.cos(a) * math.sqrt(1 - e * e), e, math.sin(a) * math.sqrt(1 - e * e)])
        pts = rayo(c, c + d * tam * r.uniform(1.4, 2.2), semilla * 11 + k, 5, 0.18)
        trans(lz, cam, cinta3d(pts, 0.05, cam), tex_plano(claro(col, 0.4), 170), 0.85, None, 0.7)
        trans(lz, cam, cinta3d(pts, 0.018, cam), tex_plano(claro(col, 0.92)), 1.0, None, 1.2)


def chispa(W=1600, H=900, fase=3):
    col = COLOR_FASE[fase]
    amarillo = (255, 236, 140)
    cam, lz, niebla = escena_base((1.0, 2.3, -4.0), (-0.5, 3.0, 12.0), W, H, fov=64)
    ax_, ay_, az_ = -5.0, Y_VUELO_NUEVA + 4.0, 26.0
    g_ae = guinada_hacia(cam.ojo[0] - ax_, cam.ojo[2] - az_) + 15
    aeralis(lz, cam, 'despues', ax_, ay_, az_, g_ae, pose=rm.HEROICA, fase=fase, niebla=ve.NieblaCielo(40, 120))
    # el que la pasa (acaba de dar el golpe) y el que la recibe
    da = (2.4, 5.0)
    recibe = (-2.4, 7.0)
    jugador3(lz, cam, da[0], da[1], guinada_hacia(recibe[0] - da[0], recibe[1] - da[1]), pose=PASA, espada=True,
             niebla=niebla)
    jugador3(lz, cam, recibe[0], recibe[1], guinada_hacia(da[0] - recibe[0], da[1] - recibe[1]), pose=EN_ALTO,
             niebla=niebla)
    # los demas, apartandose
    for x, z, g, pose in ((5.8, 9.5, 40, CORRE), (-6.0, 4.0, -60, CORRE), (0.4, 11.5, 180, ESPERA)):
        jugador3(lz, cam, x, z, g, pose=pose, espada=True, niebla=niebla)
    # la chispa salta de uno a otro: su estela en arco y ella, a punto de caerle encima
    a = np.array([da[0], 2.2, da[1]])
    b = np.array([recibe[0], 2.6, recibe[1]])

    def arco(t):
        return a + (b - a) * t + np.array([0, 1.6 * 4 * t * (1 - t), 0])
    est = [arco(t) for t in np.linspace(0.05, 0.78, 16)]
    trans(lz, cam, cinta3d(est, 0.35, cam), tex_plano(claro(col, 0.4), 70), 0.6, None, 0.6)
    trans(lz, cam, cinta3d(est, 0.12, cam), tex_plano(claro(col, 0.85)), 0.9, None, 1.0)
    pc = arco(0.84)
    chispa_mundo(lz, cam, pc, col, 5, tam=0.62)
    chispas_cuerpo(lz, cam, np.array([da[0], 1.0, da[1]]), col, 4, n=5, radio=0.6)
    img = componer(lz, cam, W, H, 231, fase, rayos=0.7, estelas=40)
    titular(img, W / 2, 92, '¡LA LLEVAS!', 104, BLANCO, borde=col)
    # la cuenta atras, grande, encima de la chispa
    sx, sy = pantalla(cam, pc + np.array([0, 1.4, 0]))[:2]
    titular(img, sx, sy, '2', 92, amarillo, borde=(255, 120, 60))
    rotulo(img, cam, np.array([da[0], 1.9, da[1]]), 'UN GOLPE A UN COMPAÑERO: SE LA PASAS', -420, 90, 36, BLANCO)
    rotulo(img, cam, np.array([recibe[0], 2.0, recibe[1]]), 'SI TE REVIENTA: PARÁLISIS Y GOLPE', 90, 120, 36,
           claro(ROJO, 0.4))
    pildora(img, W - 190, 60, 'PASES 5/8', 40, BLANCO, borde=(*claro(col, 0.2), 230))
    leyenda(img, W / 2, H - 70, [('CADA PASE LA CARGA', col), ('CARGADA: ¡A ELLA! ATURDIDA', (110, 230, 130))], 28)
    guardar(img, 'chispa')


# ----------------------------------------------------------------------
#  4. ¿Vendaval, estas?
#
#  "Juguemos en el bosque mientras el lobo no esta": se posa en el centro con
#  las alas cerradas y se va vistiendo. Mientras, dentro del circulo se le
#  puede pegar (dano doble). Cuando contesta "¡SI!", todos fuera del circulo.
# ----------------------------------------------------------------------
def lobo(W=1600, H=900, fase=2):
    col = COLOR_FASE[fase]
    luz = claro(col, 0.35)
    cam, lz, niebla = escena_base((7.0, 3.4, -6.5), (-0.5, 4.2, 12.0), W, H, fov=64)
    ax_, ay_, az_ = 0.0, -3.9, 12.0
    g_ae = guinada_hacia(cam.ojo[0] - ax_, cam.ojo[2] - az_)
    # el circulo del bosque, en el suelo
    R_ = 8.5
    aro = [(ax_ + R_ * math.cos(a), 0.12, az_ + R_ * math.sin(a)) for a in np.linspace(0, TAU, 90)]
    for k in range(0, 88, 3):
        trans(lz, cam, cinta3d(aro[k:k + 2], 0.12, cam), tex_plano(claro(col, 0.5)), 1.0, None, 0.8)
    brillo(lz, cam, cuadrado_suelo(ax_, az_, R_ + 0.8, y=0.08), tex_halo(col, 128, 3.0), 0.18)
    aeralis(lz, cam, 'despues', ax_, ay_, az_, g_ae, pose=rm.POSADA, fase=fase, niebla=niebla)
    # dentro, le pegan; fuera, uno sale corriendo y otro espera
    for x, z in ((2.6, 8.8), (-2.8, 9.0), (3.4, 12.6)):
        jugador3(lz, cam, x, z, guinada_hacia(ax_ - x, az_ - z), pose=TAJO, espada=True, niebla=niebla)
    jugador3(lz, cam, 6.4, 4.6, guinada_hacia(10.0, -8.0), pose=CORRE, espada=True, niebla=niebla)
    jugador3(lz, cam, -9.0, 3.2, guinada_hacia(ax_ + 9.0, az_ - 3.2), pose=ESPERA, espada=True, niebla=niebla)
    # los golpes que le entran
    for x, z in ((1.4, 10.0), (-1.6, 10.2), (1.9, 12.0)):
        chispazo(lz, cam, np.array([x, 2.4, z]), (255, 236, 180), 0.35)
    img = componer(lz, cam, W, H, 241, fase, rayos=0.4, estelas=30)
    titular(img, W / 2, 86, '¿VENDAVAL, ESTÁS?', 92, BLANCO, borde=col)
    # lo que contesta, como un bocadillo
    sx, sy = pantalla(cam, np.array([ax_, 9.5, az_]))[:2]
    f = ImageFont.truetype(FUENTE + 'Oswald-Bold.ttf', 40)
    texto = '«ME ESTOY PONIENDO LAS ALAS...»'
    d = ImageDraw.Draw(img)
    w = d.textlength(texto, font=f)
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    x0, y0 = sx - w / 2 - 26, sy - 40
    dc.rounded_rectangle((x0, y0, x0 + w + 52, y0 + 72), 26, fill=(238, 242, 255, 235), outline=(*col, 255), width=4)
    dc.polygon([(sx - 18, y0 + 70), (sx + 18, y0 + 70), (sx + 4, y0 + 100)], fill=(238, 242, 255, 235))
    img.alpha_composite(capa)
    ImageDraw.Draw(img).text((x0 + 26, y0 + 10), texto, font=f, fill=(40, 30, 80, 255))
    rotulo(img, cam, np.array([2.6, 1.6, 8.8]), 'MIENTRAS SE VISTE: ¡A PEGARLE! DAÑO DOBLE', 120, 120, 36, BLANCO)
    rotulo(img, cam, np.array([6.4, 1.8, 4.6]), 'AL «¡SÍ!»: ¡FUERA DEL CÍRCULO!', 60, -110, 36, claro(ROJO, 0.45))
    leyenda(img, W / 2, H - 70, [('«¡SÍ! ¡Y OS VOY A SOPLAR!»', col), ('QUIEN SIGA DENTRO SALE VOLANDO', (255, 110, 120))],
            28)
    guardar(img, 'lobo')


ESCENAS = {'comba': comba, 'volante': volante, 'chispa': chispa, 'lobo': lobo}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
        print('ok', nombre, flush=True)

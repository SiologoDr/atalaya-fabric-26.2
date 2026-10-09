"""
Renders de la quinta ficha de Rajang (octubre de 2026). Juan ya tiene tres
minijuegos (Suelo que se Hunde, Glifos del Templo y El Rayo del Prisma) y falta
"uno mas". Cuatro para elegir uno, en la plaza del Templo del Jaguar:

  trilero  El Trilero de Jade: Rajang esconde su corazon de jade bajo una de
           tres vasijas y las cambia de sitio con las zarpas; los jugadores
           miran y uno golpea la que cree
  pinata   La Pinata del Jaguar: una pinata de oro con forma de jaguar colgada
           de una horca de jade; un jugador le pega, salen dulces, y Rajang corre
           a defenderla
  impostor El Impostor de Jade: Rajang se ha encogido en la copia de un jugador;
           cinco iguales y uno deja huellas de jade y le brillan los ojos
  espejo   El Espejo de Obsidiana: un espejo enorme de obsidiana con marco de oro;
           Rajang bufa a su reflejo; dos jugadores lo giran golpeando el marco

Uso: python rajang_cuarto_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
"""
import math
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rajang_mecanicas_escenas as me  # lee la raiz y la carpeta de salida de sys.argv
import rajang_minijuegos_escenas as mj
from rajang_mecanicas_escenas import (rm, ts, ta, ra, vr, SS, TAU, JADE, JADE_CLARO, ORO, ORO_CLARO, BLANCO, rotulo,
                                      pildora, guardar, jugador2, matriz_jugador, rajang_en, tex_halo, tex_aro,
                                      contorno, capa_fina, texto_sombra, CORRER, GOLPE)

ROJO = (255, 96, 80)
ROJO_CLARO = (255, 180, 170)
MIRAR = {'cabeza': {'rot': (10, 0, 0)}, 'bi': {'rot': (-20, 0, -8)}, 'bd': {'rot': (-24, 0, 8)}}
SENALAR = {'cabeza': {'rot': (10, 0, 0)}, 'bd': {'rot': (-100, 0, 6)}, 'bi': {'rot': (-20, 0, -10)}}
QUIETO = {'bi': {'rot': (-8, 0, -4)}, 'bd': {'rot': (6, 0, 4)}}


# ----------------------------------------------------------------------
#  1. El Trilero de Jade
# ----------------------------------------------------------------------
def vasija(x, z, k=1.5):
    """Una vasija del templo, de bloques: panza ancha, cuello y boca, con cenefas de oro."""
    capas = ((1.4, 0.3), (1.8, 0.5), (1.9, 0.5), (1.6, 0.4), (1.0, 0.3), (1.2, 0.2))
    qs = []
    y = 0.0
    for i, (w, h) in enumerate(capas):
        qs += ts.caja(x - w * k / 2, y, z - w * k / 2, w * k, h * k, w * k, 'oro' if i in (2, 5) else 'templo')
        y += h * k
    return qs


def trilero(W=1600, H=900, fase=2, ojo=(0.0, 5.2, -7.5), objetivo=(0.0, 2.6, 12.0), fov=58, nombre='trilero'):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 90)
    mj.escenario(cam, lz, niebla, fase)
    # Rajang agazapado detras, con las zarpas sobre dos vasijas (las esta cambiando)
    pose = ra.sumar(ra.pose_en('TERREMOTO', 1.15), ra.cabeza(y=-14))
    rajang_en(lz, cam, 0.0, 0.0, 15.5, rm.guinada_hacia(0, -1), pose, fase, niebla=niebla)
    sitios = [(-4.8, 8.5), (0.0, 7.5), (4.8, 8.5)]
    mundo = []
    for k, (x, z) in enumerate(sitios):
        mundo += vasija(x, z)
    ts.dibujar_mundo(lz, cam, mundo, niebla, fase)
    halo_j = tex_halo(JADE, JADE_CLARO)
    halo_o = tex_halo(ORO, ORO_CLARO)
    # el corazon asoma un instante por una grieta de la de la derecha (en la foto, la de la izquierda)
    ta.cartel(lz, cam, (4.8, 1.6, 7.4), 2.2, halo_j, 0.6)
    # los jugadores: uno senala, otro golpea la del medio, otro mira
    jugador2(lz, cam, matriz_jugador(-3.2, 3.0, rm.guinada_hacia(-0.6, 1)), pose=SENALAR, niebla=niebla)
    jugador2(lz, cam, matriz_jugador(0.7, 4.6, rm.guinada_hacia(-0.1, 1)), pose=GOLPE, espada=True, rot_espada=(-30, 0, 0),
             niebla=niebla)
    jugador2(lz, cam, matriz_jugador(4.4, 3.2, rm.guinada_hacia(0.2, 1)), pose=MIRAR, niebla=niebla)
    ta.cartel(lz, cam, (0.2, 1.8, 6.6), 1.2, me.CHISPA, 1.1)
    for (x, z) in sitios:
        ta.calco(lz, cam, x, z, 1.6, tex_aro(ORO, grueso=0.06, marcas=10), 0.8)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 201, oscuro=0.2, rayos=False)
    # las flechas del cambio: las vasijas se cruzan
    for (a, b) in (((-4.8, 1.6, 8.5), (0.0, 1.6, 7.5)), ((0.0, 1.6, 7.5), (4.8, 1.6, 8.5))):
        rm.lineas_movimiento(img, cam, b, np.array(a) - np.array(b), 8, 2.2, 202, (255, 236, 190), 3)
    me.arcos(img, cam, np.array([0.0, 3.6, 8.0]), 4.0, 0.4, 2, ORO_CLARO)
    rotulo(img, cam, (0.0, 9.0, 15.5), '¿DÓNDE ESTÁ SU CORAZÓN?', 0, -60, 46, ORO_CLARO, linea=False, centro=True)
    rotulo(img, cam, (4.8, 1.6, 7.4), 'UN DESTELLO POR LA GRIETA', 160, -60, 28, JADE_CLARO)
    rotulo(img, cam, (-4.8, 3.4, 8.5), 'LAS CAMBIA CADA VEZ MÁS RÁPIDO', -160, -90, 28, BLANCO)
    rotulo(img, cam, (0.2, 1.8, 6.6), 'GOLPEA LA QUE CREAS', 30, 170, 30, BLANCO)
    pildora(img, 330, 52, 'CAMBIOS 6/8', 30, ORO_CLARO)
    pildora(img, W - 110, 52, '15 S', 34, ORO_CLARO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  2. La Pinata del Jaguar
# ----------------------------------------------------------------------
def pinata(cx, cy, cz, giro=0.0):
    """La pinata: un jaguar de carton dorado, de cajas, con franjas de jade y flecos."""
    qs = []
    R = vr.Ry(giro)[:3, :3]
    ex, ey, ez = R @ np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), R @ np.array([0, 0, 1.0])
    c = np.array([cx, cy, cz])
    partes = [((0, 0, 0), (0.55, 0.45, 0.9), 'oro'), ((0, 0.25, 0.95), (0.42, 0.38, 0.4), 'oro'),
              ((0, 0.05, 1.32), (0.2, 0.16, 0.12), 'jade'), ((0.25, 0.65, 0.95), (0.08, 0.12, 0.06), 'jade'),
              ((-0.25, 0.65, 0.95), (0.08, 0.12, 0.06), 'jade'), ((0, 0.12, -1.05), (0.1, 0.1, 0.35), 'jade'),
              ((0.35, -0.65, 0.5), (0.12, 0.25, 0.12), 'oro'), ((-0.35, -0.65, 0.5), (0.12, 0.25, 0.12), 'oro'),
              ((0.35, -0.65, -0.5), (0.12, 0.25, 0.12), 'oro'), ((-0.35, -0.65, -0.5), (0.12, 0.25, 0.12), 'oro')]
    for (o, h, mat) in partes:
        p = c + ex * o[0] + ey * o[1] + ez * o[2]
        qs += mj.caja_mundo(p, ex * h[0], ey * h[1], ez * h[2], mat, True)
    for k in range(-2, 3):
        p = c + ez * (k * 0.32) + ey * 0.0
        qs += mj.caja_mundo(p, ex * 0.57, ey * 0.47, ez * 0.06, 'jade', True)
    return qs


def pinata_escena(W=1600, H=900, fase=2, ojo=(0.0, 4.5, -4.0), objetivo=(0.5, 3.6, 10.0), fov=60, nombre='pinata'):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 90)
    mj.escenario(cam, lz, niebla, fase)
    # la horca de jade: dos postes y el travesano; la cuerda y la pinata balanceandose
    mundo = (ts.caja(-4.4, 0, 7.6, 0.8, 7.0, 0.8, 'templo') + ts.caja(4.0, 0, 7.6, 0.8, 7.0, 0.8, 'templo') +
             ts.caja(-4.6, 7.0, 7.4, 9.6, 0.7, 1.2, 'templo') + ts.caja(-4.7, 6.8, 7.3, 9.8, 0.25, 1.4, 'oro'))
    ts.dibujar_mundo(lz, cam, mundo, niebla, fase)
    colgado = np.array([0.0, 7.0, 8.0])
    p = np.array([1.6, 3.6, 8.0])
    ts.dibujar_mundo(lz, cam, pinata(*p, giro=0.9), niebla, fase)
    cuerda = mj.caja_mundo((colgado + p + np.array([0, 0.9, 0])) / 2, np.array([0.04, 0, 0]),
                           (colgado - p - np.array([0, 0.9, 0])) / 2, np.array([0, 0, 0.04]), 'templo', True)
    ts.dibujar_mundo(lz, cam, cuerda, niebla, fase)
    # Rajang viene corriendo a defenderla
    rajang_en(lz, cam, -10.0, 0.0, 17.0, rm.guinada_hacia(0.8, -0.6), ra.pose_en('CORRER', 0.3), fase, niebla=niebla)
    # los jugadores: uno le pega, otro espera turno, otro coge dulces
    jugador2(lz, cam, matriz_jugador(0.2, 5.6, rm.guinada_hacia(0.5, 1)), pose=GOLPE, espada=True, rot_espada=(-30, 0, 0),
             niebla=niebla)
    jugador2(lz, cam, matriz_jugador(-3.6, 4.0, rm.guinada_hacia(0.8, 1)), pose=MIRAR, niebla=niebla)
    jugador2(lz, cam, matriz_jugador(3.8, 4.2, rm.guinada_hacia(-0.4, 1)), pose=CORRER, niebla=niebla)
    # los dulces que saltan
    r = random.Random(9)
    dulces = []
    colores = ['oro', 'jade', 'obsidiana', 'cristal']
    for k in range(16):
        d = p + np.array([r.uniform(-1.8, 1.8), r.uniform(-1.4, 1.6), r.uniform(-1.2, 1.2)])
        t = r.uniform(0.09, 0.15)
        dulces += mj.caja_mundo(d, np.array([t, 0, 0]), np.array([0, t, 0]), np.array([0, 0, t]), colores[k % 4], True)
    ts.dibujar_mundo(lz, cam, dulces, niebla, fase)
    ta.cartel(lz, cam, p + np.array([-0.6, -0.2, -0.6]), 1.4, me.CHISPA, 1.2)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 211, oscuro=0.2, rayos=False)
    me.arcos(img, cam, colgado, 4.0, 4.4, 2, ORO_CLARO)
    rm.lineas_movimiento(img, cam, (-10.0, 1.4, 17.0), (-1, 0, 0.8), 10, 3.0, 212)
    rotulo(img, cam, p + np.array([0, 1.4, 0]), '¡DALE A LA PIÑATA!', -60, -150, 46, ORO_CLARO)
    rotulo(img, cam, colgado + np.array([2.0, -0.4, 0]), 'CADA GOLPE LA BALANCEA MÁS', 60, -60, 28, BLANCO)
    rotulo(img, cam, (-10.0, 5.0, 17.0), 'RAJANG CORRE A DEFENDERLA', -60, -80, 30, JADE_CLARO)
    rotulo(img, cam, p + np.array([-1.5, -1.0, 0]), 'DULCES: FUERZA Y VELOCIDAD', -300, 160, 28, ORO_CLARO)
    pildora(img, 330, 52, 'GOLPES 9/15', 30, ORO_CLARO)
    pildora(img, W - 110, 52, '20 S', 34, ORO_CLARO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  3. El Impostor de Jade
# ----------------------------------------------------------------------
def impostor(W=1600, H=900, fase=2, ojo=(1.0, 4.0, -7.5), objetivo=(0.0, 1.4, 8.0), fov=58, nombre='impostor'):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(30, 85)
    mj.escenario(cam, lz, niebla, fase)
    # cinco jugadores iguales en corro; el falso es el segundo por la izquierda
    sitios = [(4.6, 6.0, -0.5), (2.2, 5.0, -0.2), (-0.4, 4.6, 0.1), (-3.0, 5.2, 0.4), (-5.2, 6.6, 0.6)]
    falso = 1
    qs_f = None
    for k, (x, z, g) in enumerate(sitios):
        M = matriz_jugador(x, z, rm.guinada_hacia(g, -1) if k != falso else rm.guinada_hacia(-0.6, -1))
        qs = jugador2(lz, cam, M, pose=QUIETO if k != 0 else MIRAR, niebla=niebla)
        if k == falso:
            qs_f = qs
    halo_j = tex_halo(JADE, JADE_CLARO)
    # las huellas de jade del falso (de donde ha venido) y el destello de sus ojos
    x, z, _ = sitios[falso]
    for i, (hx, hz) in enumerate(((x + 1.0, z + 2.2), (x + 0.5, z + 1.5), (x + 0.9, z + 0.8), (x + 0.4, z + 0.2))):
        ta.calco(lz, cam, hx, hz, 0.35, halo_j, 1.2 - 0.2 * i)
    for lado in (-0.13, 0.13):
        ta.cartel(lz, cam, (x + lado, 1.72, z - 0.3), 0.32, halo_j, 1.6)
    # el que ya sospecha, senalandole
    jugador2(lz, cam, matriz_jugador(0.5, 1.8, rm.guinada_hacia(0.6, 1)), pose=SENALAR, espada=True, rot_espada=(-60, 0, 0),
             niebla=niebla)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 221, oscuro=0.25, rayos=False)
    rotulo(img, cam, (0.0, 3.4, 5.4), 'RAJANG ES UNO DE VOSOTROS', 0, -150, 46, ORO_CLARO, linea=False, centro=True)
    rotulo(img, cam, (x, 1.75, z), 'OJOS DE JADE UN INSTANTE', 200, -100, 30, JADE_CLARO)
    rotulo(img, cam, (x + 0.9, 0.0, z + 0.8), 'DEJA HUELLAS DE JADE', 200, 40, 30, JADE_CLARO)
    rotulo(img, cam, (0.5, 1.6, 1.8), '¡ES ESE! PÉGALE AL FALSO', -260, 40, 30, BLANCO)
    pildora(img, W - 110, 52, '20 S', 34, ORO_CLARO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  4. El Espejo de Obsidiana
# ----------------------------------------------------------------------
def espejo(W=1600, H=900, fase=3, ojo=(15.0, 14.0, -5.0), objetivo=(0.0, 4.0, 13.5), fov=60, nombre='espejo'):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 90)
    mj.escenario(cam, lz, niebla, fase)
    # el espejo de cara a Rajang (mira a -z), sobre su peana que gira
    ex, ez = 0.0, 13.0
    pose = ra.sumar(ra.pose_en('RUGIDO', 0.4), ra.cabeza(y=-6, boca=10))
    # el reflejo, al otro lado del cristal y de frente, oscurecido por la obsidiana
    rajang_en(lz, cam, -1.0, 0.0, 21.0, rm.guinada_hacia(0, -1), pose, fase, niebla=ts.NieblaSelva(4, 22), k_cristal=0.2)
    marco = (ts.caja(-5.4, 0.0, -0.4, 10.8, 0.8, 0.8, 'templo') + ts.caja(-5.2, 0.8, -0.2, 0.6, 9.4, 0.4, 'oro') +
             ts.caja(4.6, 0.8, -0.2, 0.6, 9.4, 0.4, 'oro') + ts.caja(-5.2, 10.2, -0.2, 10.4, 0.6, 0.4, 'oro'))
    ts.dibujar_mundo(lz, cam, me._girar(marco, 0.0, ex, 0.0, ez), niebla, fase)
    # Rajang, de espaldas a la camara, bufando a su reflejo
    rajang_en(lz, cam, -1.0, 0.0, 5.0, rm.guinada_hacia(0, 1), pose, fase, niebla=niebla)
    # dos jugadores giran el espejo golpeando el marco
    jugador2(lz, cam, matriz_jugador(6.6, 11.5, rm.guinada_hacia(-1, 0.4)), pose=GOLPE, espada=True, rot_espada=(-30, 0, 0),
             niebla=niebla)
    jugador2(lz, cam, matriz_jugador(-6.8, 11.0, rm.guinada_hacia(1, 0.4)), pose=MIRAR, niebla=niebla)
    halo_o = tex_halo(ORO, ORO_CLARO)
    ta.calco(lz, cam, ex, ez, 6.2, tex_aro(ORO, grueso=0.04, marcas=16), 1.0)
    ta.cartel(lz, cam, (5.0, 3.0, 12.6), 1.4, me.CHISPA, 1.0)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 231, oscuro=0.25, rayos=False)
    me.arcos(img, cam, np.array([ex, 0.4, ez]), 6.0, 4.4, 2, ORO_CLARO)
    rotulo(img, cam, (-1.0, 9.0, 21.0), 'SE VE A SÍ MISMO Y SE PICA', 0, -110, 40, ORO_CLARO, linea=False, centro=True)
    rotulo(img, cam, (5.0, 3.0, 12.6), 'GÍRALO GOLPEANDO EL MARCO', -380, 90, 30, BLANCO)
    rotulo(img, cam, (-1.0, 1.0, 9.5), 'CUANDO CARGUE CONTRA SU REFLEJO: SE ESTAMPA', 40, 190, 28, JADE_CLARO)
    pildora(img, W - 110, 52, '20 S', 34, ORO_CLARO)
    guardar(img, nombre)


ESCENAS = {'trilero': trilero, 'pinata': pinata_escena, 'impostor': impostor, 'espejo': espejo}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
        print('ok', nombre, flush=True)

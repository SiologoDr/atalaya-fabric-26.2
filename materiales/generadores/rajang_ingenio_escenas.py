"""
Renders de la cuarta ficha de Rajang (octubre de 2026). Juan, de la tercera:
"no me gustaron tampoco; crea 4 mas, se mas ingenioso, sorprendeme". Rajang es
un jaguar, un gato enorme: dos propuestas juegan con eso, y dos con trucos que
no ha hecho ningun jefe. Con las ayudas de rajang_mecanicas_escenas y de
rajang_minijuegos_escenas:

  prisma    El Rayo del Prisma: un jugador apunta un prisma de jade y en el suelo
            se enciende un punto de luz; Rajang, como un gato con un puntero, se
            lanza a por el; delante, la trampa de oro con pinchos
  tragado   Tragado: Rajang se ha tragado a uno (se le ve brillar dentro de la
            panza); dos le pegan en la panza; en el recuadro, el de dentro rompe
            los cristales de su estomago de jade
  domino    Domino de Jade: un arco de losas gigantes de pie hasta Rajang; un
            jugador pone la que falta, otro espera junto a la primera a que el
            pise la marca de oro
  cascabel  El Cascabel al Gato: Rajang duerme en medio de la plaza; uno se le
            acerca agachado con un cascabel de oro enorme, los demas quietos y
            agachados; uno corre y hace ruido; arriba, el medidor de ruido

Uso: python rajang_ingenio_escenas.py <raiz del proyecto> <carpeta de salida> [escena,escena...]
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
AGACHADO = {'cuerpo': {'rot': (40, 0, 0)}, 'cabeza': {'rot': (-34, 0, 0)}, 'pi': {'rot': (-50, 0, 0)},
            'pd': {'rot': (30, 0, 0)}, 'bi': {'rot': (-46, 0, -6)}, 'bd': {'rot': (-46, 0, 6)}}
AGACHADO_ALZA = {'cuerpo': {'rot': (22, 0, 0)}, 'cabeza': {'rot': (-20, 0, 0)}, 'pi': {'rot': (-30, 0, 0)},
                 'pd': {'rot': (22, 0, 0)}, 'bi': {'rot': (-168, 0, -14)}, 'bd': {'rot': (-168, 0, 14)}}
APUNTAR = {'cabeza': {'rot': (14, 0, 0)}, 'bd': {'rot': (-80, 0, 4)}, 'bi': {'rot': (-70, 0, -14)}}
CARGAR = {'bi': {'rot': (-72, 0, -10)}, 'bd': {'rot': (-72, 0, 10)}, 'pi': {'rot': (-22, 0, 0)}, 'pd': {'rot': (18, 0, 0)}}
EMPUJAR = {'cuerpo': {'rot': (10, 0, 0)}, 'bi': {'rot': (-90, 0, -6)}, 'bd': {'rot': (-90, 0, 6)}, 'pi': {'rot': (-24, 0, 0)},
           'pd': {'rot': (26, 0, 0)}}


def mano(M, lado='bd', largo=11.0):
    """Donde cae la mano del jugador (con la pose ya puesta, aproximado)."""
    return (M @ np.array([-6.0 if lado == 'bd' else 6.0, 2.0 + largo, -6.0, 1.0]))[:3]


# ----------------------------------------------------------------------
#  1. El Rayo del Prisma
# ----------------------------------------------------------------------
def trampa(x, z, lado=3.0):
    """La trampa de oro: un hoyo cuadrado con pinchos dentro y el borde de oro."""
    mundo = []
    h = lado / 2
    for (a, b, w, d) in ((x - h - 0.3, z - h - 0.3, lado + 0.6, 0.3), (x - h - 0.3, z + h, lado + 0.6, 0.3),
                         (x - h - 0.3, z - h, 0.3, lado), (x + h, z - h, 0.3, lado)):
        mundo += ts.caja(a, -0.05, b, w, 0.25, d, 'oro')
    mundo += ts.caja(x - h, -0.02, z - h, lado, 0.04, lado, 'obsidiana')
    picos = []
    r = random.Random(int(x * 10 + z))
    for k in range(5):
        picos += ta.pico(x + r.uniform(-h + 0.4, h - 0.4), z + r.uniform(-h + 0.4, h - 0.4), r.uniform(0.9, 1.4),
                         r.uniform(0.18, 0.26), semilla=300 + k, extras=False)
    return mundo, picos


def prisma(W=1600, H=900, fase=1, ojo=(-4.0, 8.0, -12.0), objetivo=(2.0, 2.0, 11.0), fov=62, nombre='prisma'):
    # la camara mira hacia +z: en la foto, +x queda a la izquierda
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 90)
    mj.escenario(cam, lz, niebla, fase)
    # las trampas de oro (una ya usada: rota) y el punto de luz, justo delante de una
    for (tx, tz) in ((2.5, 7.0), (-8.0, 14.0)):
        m, p = trampa(tx, tz)
        ts.dibujar_mundo(lz, cam, m, niebla, fase)
        ta.dibujar(lz, cam, p, ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    luz = np.array([4.2, 0.05, 10.0])
    # Rajang, en el aire, saltando a por la luz
    pose = ra.sumar(ra.pose_en('SALTO', 0.75), ra.cabeza(x=10))
    rajang_en(lz, cam, 8.5, 0.8, 15.0, rm.guinada_hacia(luz[0] - 8.5, luz[2] - 15.0), pose, fase, niebla=niebla)
    # el del prisma, apuntando; otro se aparta
    Mp = matriz_jugador(-4.5, 2.0, rm.guinada_hacia(luz[0] + 4.5, luz[2] - 2.0))
    jugador2(lz, cam, Mp, pose=APUNTAR, niebla=niebla)
    pm = mano(Mp)
    ta.dibujar(lz, cam, mj.bola_pixeles(pm, 0.22, 'fragmento', giro=0.6), ts.LUCES_SELVA, ts.AMB_SELVA, niebla)
    jugador2(lz, cam, matriz_jugador(6.5, 5.0, rm.guinada_hacia(-1, -0.2)), pose=CORRER, niebla=niebla)
    # el rayo y el punto
    halo_j = tex_halo(JADE, JADE_CLARO)
    halo_o = tex_halo(ORO, ORO_CLARO)
    mj.puntos(lz, cam, [pm, luz + np.array([0, 0.1, 0])], 0.12, halo_j, 0.09, 1.2)
    ta.calco(lz, cam, luz[0], luz[2], 2.4, halo_o, 1.4)
    ta.calco(lz, cam, luz[0], luz[2], 1.1, tex_halo((255, 255, 230), (255, 255, 255)), 1.6)
    ta.cartel(lz, cam, pm, 1.0, halo_j, 1.3)
    mj.puntos(lz, cam, [(luz[0], 0.2, luz[2]), (2.5, 0.2, 7.0)], 0.6, halo_o, 0.16, 0.9)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 161, oscuro=0.2, rayos=False)
    rm.lineas_movimiento(img, cam, (8.0, 2.8, 14.0), (0.5, 0.3, 0.6), 12, 3.0, 162, (230, 255, 220), 3)
    rotulo(img, cam, (8.5, 5.5, 15.0), 'COMO UN GATO: NO RESISTE LA LUZ', 40, -110, 34, ORO_CLARO)
    rotulo(img, cam, (-4.5, 2.2, 2.0), 'EL PRISMA: APUNTA Y MANTÉN CLIC DERECHO', -60, 110, 28, JADE_CLARO)
    rotulo(img, cam, (2.5, 0.0, 6.4), 'LLÉVALO A LA TRAMPA', 220, 40, 34, ORO_CLARO)
    rotulo(img, cam, (6.5, 1.6, 5.0), 'DONDE ESTÁ LA LUZ, SALTA: ¡APÁRTATE!', -40, 130, 26, ROJO_CLARO)
    pildora(img, 330, 52, 'TRAMPAS 1/3', 30, ORO_CLARO)
    pildora(img, W - 110, 52, '20 S', 34, ORO_CLARO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  2. Tragado
# ----------------------------------------------------------------------
def dentro(W=620, H=360):
    """Lo que ve el tragado: el estomago de jade, que late, con tres cristales; uno roto."""
    cam = vr.Camara(ojo=(0.0, 1.8, -4.6), objetivo=(0.0, 1.4, 3.0), fov=72, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    paredes = []
    for i in range(-3, 4):
        for j in range(0, 4):
            paredes += ts.caja(i * 1.2 - 0.6, j * 1.2, 3.6, 1.2, 1.2, 0.6, 'jade_osc' if (i + j) % 2 else 'jade')
        paredes += ts.caja(-4.2, 0.0, i * 1.2 - 2.0, 0.6, 4.8, 1.2, 'jade_osc' if i % 2 else 'jade')
        paredes += ts.caja(3.6, 0.0, i * 1.2 - 2.0, 0.6, 4.8, 1.2, 'jade' if i % 2 else 'jade_osc')
    paredes += ts.caja(-4.2, -0.6, -4.0, 8.4, 0.6, 8.4, 'vientre')
    paredes += ts.caja(-4.2, 4.8, -4.0, 8.4, 0.6, 8.4, 'jade_osc')
    ts.dibujar_mundo(lz, cam, paredes, None, 4)
    luces = [((0.0, 1.0, -0.4), (0.5, 1.0, 0.6), 0.9, 'llave')]
    halo_j = tex_halo(JADE, JADE_CLARO)
    cristales = [(-2.2, 1.6, 3.0), (0.4, 2.6, 3.2), (2.6, 1.2, 3.0)]
    for k, c in enumerate(cristales):
        if k == 0:
            for j in range(5):
                ta.dibujar(lz, cam, ta.roca_cubica(c[0] + 0.3 * j - 0.6, 0.15, c[2] - 0.6, 0.15, semilla=70 + j, mat='fragmento'),
                           luces, (0.4, 0.5, 0.42))
            continue
        ta.dibujar(lz, cam, mj.bola_pixeles(c, 0.55, 'fragmento', giro=0.3 * k), luces, (0.45, 0.6, 0.5))
        ta.cartel(lz, cam, c, 2.2, halo_j, 0.8)
    Mj = matriz_jugador(1.2, 1.0, rm.guinada_hacia(-0.6, 1))
    jugador2(lz, cam, Mj, pose=GOLPE, espada=True, rot_espada=(-30, 0, 0), luces=luces, amb=(0.45, 0.6, 0.5))
    ta.cartel(lz, cam, (0.6, 2.4, 2.6), 1.2, me.CHISPA, 1.2)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 171, oscuro=0.4, rayos=False)
    texto_sombra(img, (16, 12), 'DENTRO DEL JAGUAR', 30, JADE_CLARO)
    texto_sombra(img, (16, H - 44), 'ROMPE LOS 3 CRISTALES', 28, ORO_CLARO)
    pildora(img, W - 70, 30, '1/3', 26, ORO_CLARO)
    return img


def tragado(W=1600, H=900, fase=2, ojo=(4.0, 6.0, -6.0), objetivo=(-1.0, 3.0, 12.0), fov=60, nombre='tragado'):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 90)
    mj.escenario(cam, lz, niebla, fase)
    rx, rz = -1.0, 11.0
    pose = ra.sumar(ra.pose_en('TAMBALEO', 0.9), ra.cabeza(y=20, boca=8))
    g = rm.guinada_hacia(0.6, -1)
    rajang_en(lz, cam, rx, 0.0, rz, g, pose, fase, niebla=niebla)
    # el tragado, dentro de la panza (se ve su silueta brillando a traves del jade)
    Mt = matriz_jugador(rx + 0.4, rz - 0.6, g + 180, y=2.4, inclina=70)
    qs_t = me.nm.quads(me.ne.jugador(), AGACHADO, Mt)
    # los que le pegan en la panza
    Ma = matriz_jugador(rx + 3.2, rz - 2.6, rm.guinada_hacia(-1, 0.7))
    jugador2(lz, cam, Ma, pose=GOLPE, espada=True, rot_espada=(-30, 0, 0), niebla=niebla)
    Mb = matriz_jugador(rx - 2.4, rz - 3.6, rm.guinada_hacia(0.6, 1))
    jugador2(lz, cam, Mb, pose=GOLPE, espada=True, rot_espada=(-30, 0, 0), niebla=niebla)
    halo_j = tex_halo(JADE, JADE_CLARO)
    ta.cartel(lz, cam, (rx + 0.4, 3.0, rz - 1.0), 4.0, halo_j, 0.6)
    for p in ((rx + 1.6, 2.6, rz - 1.8), (rx - 1.0, 2.4, rz - 2.4)):
        ta.cartel(lz, cam, p, 1.2, me.CHISPA, 1.1)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 172, oscuro=0.2, rayos=False)
    contorno(img, cam, qs_t, JADE_CLARO, grosor=4, halo=1.2)
    ins = dentro()
    x0, y0 = W - ins.width - 30, 96

    def marco(d, k):
        d.rounded_rectangle(((x0 - 6) * k, (y0 - 6) * k, (x0 + ins.width + 6) * k, (y0 + ins.height + 6) * k), 16 * k,
                            fill=(6, 16, 10, 255), outline=(*JADE_CLARO, 255), width=4 * k)
    capa_fina(img, marco)
    img.alpha_composite(ins.convert('RGBA'), (x0, y0))
    rotulo(img, cam, (rx + 0.4, 5.5, rz - 1.0), '¡SE HA TRAGADO A UNO!', -60, -150, 40, JADE_CLARO)
    rotulo(img, cam, (rx + 1.6, 2.6, rz - 1.8), 'FUERA: PEGADLE EN LA PANZA', -300, 120, 30, BLANCO)
    pildora(img, 330, 52, 'DIGESTIÓN 12 S', 30, ROJO_CLARO, borde=(*ROJO, 230))
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  3. Domino de Jade
# ----------------------------------------------------------------------
def losa_domino(x, z, giro, alto=4.6, ancho=2.4, grueso=0.55):
    qs = (ts.caja(-ancho / 2, 0, -grueso / 2, ancho, alto, grueso, 'templo') +
          ts.caja(-ancho / 2 - 0.05, alto - 0.35, -grueso / 2 - 0.05, ancho + 0.1, 0.35, grueso + 0.1, 'oro') +
          ts.caja(-0.45, alto * 0.45, -grueso / 2 - 0.06, 0.9, 0.9, grueso + 0.12, 'jade'))
    return me._girar(qs, giro, x, 0.0, z)


def domino(W=1600, H=900, fase=3, ojo=(-4.0, 21.0, -11.0), objetivo=(2.5, 0.0, 11.0), fov=60, nombre='domino'):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(36, 95)
    mj.escenario(cam, lz, niebla, fase)
    # el arco de losas, de la primera (abajo a la derecha) hasta donde esta Rajang
    n = 11
    arco = []
    for i in range(n):
        a = math.radians(200 - i * 14)
        arco.append((2.0 + math.cos(a) * 11.0, 10.0 + math.sin(a) * 11.0, a))
    huecos = {4, 7}
    mundo = []
    for i, (x, z, a) in enumerate(arco):
        if i in huecos:
            continue
        mundo += losa_domino(x, z, math.degrees(-a) + 90)
    ts.dibujar_mundo(lz, cam, mundo, niebla, fase)
    final = arco[-1]
    rmarca = np.array([final[0] + math.cos(final[2] - math.pi / 2) * 3.4, final[1] + math.sin(final[2] - math.pi / 2) * 3.4])
    pose = ra.sumar(ra.pose_en('ANDAR', 0.4), ra.cabeza(y=-10))
    rajang_en(lz, cam, rmarca[0], 0.0, rmarca[1] + 1.0, rm.guinada_hacia(0.3, -1), pose, fase, niebla=niebla)
    # el que pone la losa que falta (la lleva en brazos) y el que espera junto a la primera
    hx, hz, ha = arco[4]
    Mc = matriz_jugador(hx - 1.4, hz - 1.4, rm.guinada_hacia(1, 0.8))
    jugador2(lz, cam, Mc, pose=CARGAR, niebla=niebla)
    lleva = mano(Mc, largo=9.0)
    ts.dibujar_mundo(lz, cam, me._girar(ts.caja(-0.6, -0.3, -0.15, 1.2, 1.8, 0.3, 'templo') +
                                        ts.caja(-0.62, 1.3, -0.17, 1.24, 0.2, 0.34, 'oro'),
                                        rm.guinada_hacia(1, 0.8), lleva[0], lleva[1] - 0.6, lleva[2]), niebla, fase)
    px, pz, pa = arco[0]
    jugador2(lz, cam, matriz_jugador(px - 1.6, pz - 0.8, rm.guinada_hacia(1, 0.4)), pose=EMPUJAR, niebla=niebla)
    halo_o = tex_halo(ORO, ORO_CLARO)
    halo_r = tex_halo(ROJO, ROJO_CLARO)
    for i in huecos:
        x, z, a = arco[i]
        ta.cartel(lz, cam, (x, 2.3, z), 3.0, halo_o, 0.45 if i == 4 else 0.3)
        ta.calco(lz, cam, x, z, 1.4, tex_aro(ORO, grueso=0.1, marcas=8), 1.1)
    ta.calco(lz, cam, rmarca[0], rmarca[1], 3.0, tex_aro(ORO, grueso=0.06, marcas=12, relleno=0.18), 1.2)
    mj.puntos(lz, cam, [(x, 0.2, z) for (x, z, a) in arco], 0.8, halo_r, 0.1, 0.6)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 181, oscuro=0.2, rayos=False)
    rotulo(img, cam, (hx, 2.0, hz), 'PON LAS QUE FALTAN', 150, -130, 32, ORO_CLARO)
    rotulo(img, cam, (px, 1.6, pz), 'EMPUJA LA PRIMERA...', 90, 50, 32, BLANCO)
    rotulo(img, cam, (rmarca[0], 0.2, rmarca[1]), '...CUANDO PISE LA MARCA', -200, 40, 32, ORO_CLARO)
    x7, z7, a7 = arco[7]
    rotulo(img, cam, (x7, 2.0, z7), 'CON UN HUECO, LA CADENA SE PARA', 60, -90, 26, ROJO_CLARO)
    pildora(img, 330, 52, 'HUECOS 1/2', 30, ORO_CLARO)
    pildora(img, W - 110, 52, '25 S', 34, ORO_CLARO)
    guardar(img, nombre)


# ----------------------------------------------------------------------
#  4. El Cascabel al Gato
# ----------------------------------------------------------------------
def cascabel(c, k=1.0):
    """Un cascabel de oro enorme, de bloques: la campana, la ranura y la bola."""
    x, y, z = c
    qs = []
    for i, w in enumerate((1.1, 1.2, 1.15, 1.0, 0.75, 0.4)):
        qs += ts.caja(x - w * k / 2, y + i * 0.2 * k, z - w * k / 2, w * k, 0.2 * k, w * k, 'oro')
    qs += ts.caja(x - 0.08 * k, y + 1.2 * k, z - 0.25 * k, 0.16 * k, 0.3 * k, 0.5 * k, 'oro')
    qs += ts.caja(x - 0.6 * k, y + 0.42 * k, z - 0.6 * k, 1.2 * k, 0.08 * k, 1.2 * k, 'obsidiana')
    return qs


def medidor_ruido(img, cx, y, lleno):
    w, h = 520, 30

    def dib(d, k):
        d.rounded_rectangle(((cx - w / 2) * k, y * k, (cx + w / 2) * k, (y + h) * k), 10 * k, fill=(8, 22, 14, 220),
                            outline=(*JADE_CLARO, 230), width=3 * k)
        x1 = cx - w / 2 + 6 + (w - 12) * lleno
        d.rounded_rectangle(((cx - w / 2 + 6) * k, (y + 6) * k, x1 * k, (y + h - 6) * k), 6 * k, fill=(*ROJO, 235))
        for f in (0.25, 0.5, 0.75):
            xx = cx - w / 2 + w * f
            d.line((xx * k, (y + 4) * k, xx * k, (y + h - 4) * k), fill=(6, 18, 10, 200), width=2 * k)
    capa_fina(img, dib)
    texto_sombra(img, (cx - w / 2, y - 40), 'RUIDO', 30, ROJO_CLARO)
    texto_sombra(img, (cx + w / 2 - 210, y - 40), 'SI SE LLENA, SE DESPIERTA', 22, BLANCO)


def cascabel_escena(W=1600, H=900, fase=2, ojo=(4.5, 5.0, -6.5), objetivo=(-1.0, 1.4, 12.0), fov=60, nombre='cascabel'):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W * SS, alto=H * SS)
    lz = rm.Lienzo(W * SS, H * SS)
    niebla = ts.NieblaSelva(34, 90)
    mj.escenario(cam, lz, niebla, fase)
    rx, rz = -1.5, 13.0
    g = rm.guinada_hacia(0.8, -0.6)
    rajang_en(lz, cam, rx, 0.0, rz, g, ra.pose_en('DORMIDO', 1.0), fase, niebla=niebla)
    cabeza = me.matriz_pieza(ra.pose_en('DORMIDO', 1.0), 'cabeza', rx, rz, g, fase) @ np.array([0, 0, 0, 1.0])
    cab = cabeza[:3]
    # el del cascabel, agachado y con el cascabel en alto; los demas, quietos y agachados; uno corre
    Mc = matriz_jugador(cab[0] + 2.2, cab[2] - 2.4, rm.guinada_hacia(-1, 0.9), y=-0.3)
    jugador2(lz, cam, Mc, pose=AGACHADO_ALZA, niebla=niebla)
    arriba = (Mc @ np.array([0, -30, 0, 1.0]))[:3]
    ts.dibujar_mundo(lz, cam, cascabel(arriba - np.array([0, 0.1, 0]), 1.3), niebla, fase)
    for (x, z, gx, gz) in ((2.0, 3.0, -0.6, 1), (-7.0, 6.0, 0.6, 1)):
        jugador2(lz, cam, matriz_jugador(x, z, rm.guinada_hacia(gx, gz), y=-0.35), pose=AGACHADO, niebla=niebla)
    jugador2(lz, cam, matriz_jugador(7.5, 7.0, rm.guinada_hacia(-0.4, 1)), pose=CORRER, niebla=niebla)
    halo_o = tex_halo(ORO, ORO_CLARO)
    for k, rr in enumerate((1.4, 2.4, 3.4)):
        ta.calco(lz, cam, 7.5, 7.0, rr, tex_aro(ROJO, grueso=0.05, marcas=0), 1.0 - 0.25 * k)
    ta.cartel(lz, cam, arriba + np.array([0, 0.6, 0]), 2.0, halo_o, 0.5)
    ta.calco(lz, cam, cab[0], cab[2], 1.8, tex_aro(ORO, grueso=0.08, marcas=10, relleno=0.15), 1.0)
    img = ts.componer(lz, W, H, ts.horizonte(cam), 191, oscuro=0.25, rayos=False)
    medidor_ruido(img, W / 2, 96, 0.58)
    for k, (dx, dy, t) in enumerate(((40, -150, 34), (90, -200, 44), (150, -260, 56))):
        rotulo(img, cam, cab + np.array([0, 1.4, 0]), 'Z', dx, dy, t, JADE_CLARO, linea=False)
    rotulo(img, cam, arriba + np.array([0, 1.8, 0]), '¿QUIÉN LE PONE EL CASCABEL AL GATO?', -300, -90, 38, ORO_CLARO)
    rotulo(img, cam, (cab[0], 0.4, cab[2]), 'EN EL CUELLO: CLIC DERECHO', -320, 60, 28, ORO_CLARO)
    rotulo(img, cam, (2.0, 1.0, 3.0), 'AGACHADOS NO HACEN RUIDO', 40, 90, 28, BLANCO)
    rotulo(img, cam, (7.5, 1.6, 7.0), '¡CORRER HACE RUIDO!', 60, -110, 30, ROJO_CLARO)
    pildora(img, W - 110, 52, '30 S', 34, ORO_CLARO)
    guardar(img, nombre)


ESCENAS = {'prisma': prisma, 'tragado': tragado, 'domino': domino, 'cascabel': cascabel_escena}

if __name__ == '__main__':
    pedidas = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ESCENAS)
    for nombre in pedidas:
        ESCENAS[nombre]()
        print('ok', nombre, flush=True)

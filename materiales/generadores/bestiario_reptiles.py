"""
Los reptiles del bestiario (DEDsafío 4, los carteles del día 2, 22-09, y del día 4, 24-09-2026), recreados primero tal
cual de sus iconos (Juan, 19-10-2026: «hagamos los reptiles entonces»; y la regla: primero la copia fiel, luego mejorar):

  reptisaurio_salvaje   (día 2) «Ataca cuerpo a cuerpo. Aparece en las cuevas del Centro de Quiu.» Verde oliva oscuro,
                        encorvado, con los brazos largos que le llegan a las rodillas y garras de hueso; la cabeza ancha
                        con los ojos amarillos de ranura y la boca abierta con dientes; una cresta de musgo verde y dos
                        cuernos de hueso
  reptisaurio_guerrero  (día 2) «Ataca cuerpo a cuerpo. Aparece en los Asentamientos Reptisaurios. Cuidado: aplica Veneno
                        Primitivo.» El mismo cuerpo, pardo y más erguido, con la cresta naranja, una calavera con cuernos
                        en cada hombro, la faja amarilla y verde, el taparrabos de hojas y brazales de hueso
  dromoraptor_rojo      (día 2) «Depredador que posee una fuerza brutal. Se desplaza en manada.» Un raptor naranja rojizo
                        con abanicos de plumas azules de cañón naranja en el lomo y bajo los brazos, dos cuernecillos y
                        un cubo amarillo sobre el hocico
  dromoraptor_azul      (día 4) «Depredador extremadamente veloz que se desplaza en manada.» El mismo raptor, turquesa
                        con las plumas rojas
  plumosaurio           (día 2) «Coloso pacífico, pero si lo golpeas te hará mucho daño.» Un coloso de cuello largo: el
                        cuerpo de plumón morado, el cuello gris con placas y crin morada, la cabeza oscura con un
                        penacho y la cola gris acabada en un penacho
  molusco_rocoso        (día 4, que el cartel llama también «Reptisaurio Salvaje»; su nombre sale en el libro del juego)
                        «Criatura pequeña y lenta que ataca directamente a quien se le acerque. Si te alejas demasiado,
                        se entierra y te acecha hasta encontrarte, saliendo de nuevo para atacar.» Un cuerpo plano color
                        arena con cara y colmillos, sobre cuatro pilares pardos, y un manojo de prismas pardos en el lomo

Al píxel de Minecraft (escala 1, B.TEXEL = 1); las caras, los dientes, las garras y las plumas, a 32 por bloque (B.fino).

Uso: python bestiario_reptiles.py <raíz> [carpeta de las vistas] [ids]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
import bestiario_creepers as bc
import bestiario_limpio as L
from bestiario import T
from bestiario_fantasmas_v2 import con_mapa, degradado, picos_capa
from bestiario_hormigas import _azar1, redondo
from bestiario_plantas import dientes_capa
from bestiario_limpio import rampa

CARPETA = None
LADOS = ((1, 'i'), (-1, 'd'))          # +X es la izquierda del mob (mira hacia +Z)
# Lo que se agranda cada uno (Juan, 20-10-2026): el Plumosaurio, a unos seis bloques; los Dromoraptores, a tres; el
# Cavador, a uno; los Reptisaurios, un poco más grandes. El píxel no cambia (sigue a 16 por bloque): se agrandan las
# piezas y la textura sale con más (o menos) píxeles (agrandar).
TAM = {'reptisaurio_salvaje': 1.0, 'reptisaurio_guerrero': 1.0, 'dromoraptor_rojo': 1.28, 'dromoraptor_azul': 1.28,
       'plumosaurio': 2.5, 'molusco_rocoso': 0.54}
FINO = 0.5                             # el píxel fino: 32 por bloque


def H(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), float)


def P(M, p):
    """El punto p (del marco M) en el boceto."""
    return (M @ np.array((p[0], p[1], p[2], 1.0)))[:3]


def agrandar(m, k):
    """Lo hace k veces más grande sin cambiar el píxel (sigue a 16 por bloque): las cajas, los pivotes y lo que se
    mueven las animaciones, por k; la textura sale con más (o menos) píxeles. El paso se alarga con las piernas."""
    if k == 1.0:
        return m
    S, Si = np.diag([k, k, k, 1.0]), np.diag([1 / k, 1 / k, 1 / k, 1.0])
    for p in m.partes.values():
        p.marco = S @ p.marco @ Si
        p.cajas = [(S @ M @ Si, x0 * k, y0 * k, z0 * k, w * k, h * k, d * k, *resto)
                   for (M, x0, y0, z0, w, h, d, *resto) in p.cajas]
    for a in m.anims.values():
        a.canales = [(parte, tipo, [(t, x * k, y * k, z * k, su) for (t, x, y, z, su) in ks] if tipo == 'm' else ks)
                     for parte, tipo, ks in a.canales]
    m.paso = m.paso / k
    return m


def caja_en(m, parte, M, centro, tam, pint, caras=None):
    """Una caja centrada en 'centro' del marco M (girada con él)."""
    w, h, d = tam
    m._caja(parte, M @ T(*centro), -w / 2, -h / 2, -d / 2, w, h, d, pint, caras)


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def _v(tw, th, c, base, luz):
    """El tono de una pieza, limpio: más claro arriba y más oscuro abajo, con el canto de arriba de cada lado claro."""
    xs, ys = L._malla(tw, th)
    if c == 'arriba':
        v = np.full((th, tw), base + luz * 0.55)
    elif c == 'abajo':
        v = np.full((th, tw), base - luz * 0.8)
    else:
        v = base + luz * (0.4 - (ys + 0.5) / th * 0.8) + (ys == 0) * 0.35
    return xs, ys, v


def escamas(nombre, R, base=2.2, luz=0.8, ancho=3, alto=2, manchas=0.0, fino=False):
    """Escamas limpias en hileras al tresbolillo: la fila de arriba de cada escama, más clara, y su esquina de abajo, en
    sombra. 'manchas': la parte de las escamas que van un tono más oscuras (el moteado de los raptores)."""
    def fn(tw, th, c, s):
        xs, ys, v = _v(tw, th, c, base, luz)
        fila = ys // alto
        x = xs + (fila % 2) * (ancho // 2 + 1)
        col = x // ancho
        u, r = x % ancho, ys % alto
        v = v + (r == 0) * 0.3 - ((u == ancho - 1) & (r == alto - 1)) * 0.45
        if manchas:
            v = v - (_azar1(col, fila, s) < manchas) * 0.55
        return L._rgba(L.color_continuo(R, v)), None
    p = B.Pintor(nombre, fn)
    return B.fino(p, FINO) if fino else p


def bandas(nombre, R, base=1.8, luz=0.6, paso=3, oscuro=0.75, fino=False):
    """Anillos a lo largo (las rayas de las patas): una fila oscura cada 'paso'."""
    def fn(tw, th, c, s):
        xs, ys, v = _v(tw, th, c, base, luz)
        if c not in ('arriba', 'abajo'):
            v = v - ((ys % paso) == paso - 1) * oscuro
        return L._rgba(L.color_continuo(R, v)), None
    p = B.Pintor(nombre, fn)
    return B.fino(p, FINO) if fino else p


def liso(nombre, R, base=2.2, luz=0.8, fino=False):
    def fn(tw, th, c, s):
        xs, ys, v = _v(tw, th, c, base, luz)
        return L._rgba(L.color_continuo(R, v)), None
    p = B.Pintor(nombre, fn)
    return B.fino(p, FINO) if fino else p


def hueso(nombre, R, base=2.6, juntas=0):
    """Hueso limpio; con 'juntas', una junta oscura cada tantos píxeles a lo largo."""
    def fn(tw, th, c, s):
        xs, ys, v = _v(tw, th, c, base, 0.7)
        if juntas and c not in ('arriba', 'abajo'):
            v = v - ((ys % juntas) == juntas - 1) * 0.6
        return L._rgba(L.color_continuo(R, v)), None
    return B.fino(B.Pintor(nombre, fn), FINO)


def pelaje(nombre, R, base=2.2, luz=0.7):
    """Plumón: mechones a lo largo de cada columna (tres píxeles, el de arriba claro y el de abajo en sombra),
    desfasados de una columna a la siguiente."""
    def fn(tw, th, c, s):
        xs, ys, v = _v(tw, th, c, base, luz)
        desf = (xs * 5 + (xs // 3) * 2) % 3
        k = (ys + desf) % 3
        v = v + (k == 0) * 0.4 - (k == 2) * 0.35
        return L._rgba(L.color_continuo(R, v)), None
    return B.Pintor(nombre, fn)


def abanico(nombre, R, RQ, n=5, abre=(-55, 55), largos=None, hacia='arriba', ancho=4.0, base=2.0, punta=0.5):
    """Un abanico de plumas que salen de un punto (abajo en medio, o arriba en medio si 'hacia' es 'abajo'), en una
    lámina: cada pluma es una hoja que se afila hasta la punta, de R, con el cañón del medio y un canto fino de RQ. Se
    pintan de fuera adentro, una encima de otra (la del medio, delante). Lo de alrededor, vacío."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        dx = x - tw / 2.0
        dy = (th - y) if hacia == 'arriba' else y
        tex = np.zeros((th, tw, 4), np.uint8)
        a0, a1 = abre
        ls = largos or [1.0] * n
        dentro = np.zeros((th, tw), bool)
        canto = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        orden = sorted(range(n), key=lambda k: -abs(k - (n - 1) / 2))
        for k in orden:
            a = math.radians(a0 + (a1 - a0) * (k + 0.5) / n if n > 1 else 0.0)
            largo = ls[k % len(ls)] * th * 0.98
            ax, ay = math.sin(a), math.cos(a)
            t = dx * ax + dy * ay
            e = dx * ay - dy * ax
            d = np.abs(e)
            w = ancho * np.clip(1.0 - t / largo, 0, 1) ** punta + 0.4
            mk = (t > 0) & (t < largo) & (d < w)
            borde = mk & ((d > w - 0.7) | ((d < 0.5) & (t < largo - 1.5)))
            canto = np.where(mk, borde, canto)
            v = np.where(mk, base - 0.4 + 1.0 * t / largo, v)
            dentro |= mk
        rgb = np.where(canto[..., None], L.color_continuo(RQ, np.full((th, tw), 2.6)), L.color_continuo(R, v))
        tex[..., :3] = np.round(rgb)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def pix(nombre, R, base=2.0, luz=0.7, ruido=1.0, patron=None, paso=None, claro=0.0, fino=False, semilla=0):
    """La piel de los originales, al píxel: cada píxel, uno de los tonos de la rampa (sin mezclas), más claro arriba y
    más oscuro abajo, con el grano de Minecraft (algún píxel un tono más claro u oscuro) y un dibujo:
      'piel'     piel de reptil, no de bloques (Juan, 20-10-2026): manchas suaves de varios tamaños que se funden, sin
                 cuadrícula ni cantos marcados, con algún pliegue corto y alguna escama clara suelta; 'paso' > 0 le
                 añade anillos suaves a lo largo (los brazos y las patas)
      'escamas'  escamas de 3 x 2 al tresbolillo, con su píxel de luz y su píxel de sombra
      'anillos'  un anillo oscuro cada 'paso' filas a lo largo (los brazos y las patas); 'claro', uno claro detrás
      'manchas'  manchas oscuras de 2 x 2 a 3 x 3 (el moteado)
      'mechones' mechones de tres píxeles a lo largo (el plumón)"""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s * 7 + semilla)
        if c == 'arriba':
            v = np.full((th, tw), base + luz)
        elif c == 'abajo':
            v = np.full((th, tw), base - luz)
        else:
            v = base + luz * (0.5 - (ys + 0.5) / th)
            if patron in ('piel', 'manchas_grandes'):
                v = v + (ys == 0) * 0.25
            else:
                v = v + (ys == 0) * 0.5
                if tw > 2 and th > 2:
                    v = v + (xs == 0) * 0.25 - (xs == tw - 1) * 0.35 - (ys == th - 1) * 0.4
        v = v + np.where(a < 0.1, -1.0, np.where(a > 0.9, 1.0, 0.0)) * ruido
        if patron == 'piel' and c != 'abajo':
            # Manchas de tres tamaños, desplazadas entre sí para que no se vea la rejilla, que se suman en una mancha
            # blanda; algún pliegue corto (dos o tres píxeles oscuros en fila) y alguna escama clara suelta.
            n1 = _azar1((xs + 1) // 3, (ys + 2) // 3, s + 31)
            n2 = _azar1(xs // 2, (ys + 1) // 2, s + 37)
            n3 = _azar1((xs + 3) // 5, (ys + 1) // 4, s + 43)
            v = v + ((n1 * 0.4 + n2 * 0.25 + n3 * 0.35) - 0.5) * 1.35
            pliegue = (_azar1(xs // 3, ys, s + 47) < 0.06) & (c != 'arriba')
            clara = _azar1(xs, ys, s + 53) > 0.95
            v = v - pliegue * 0.8 + clara * 0.6
            if paso and c not in ('arriba', 'abajo'):
                v = v - ((ys % paso) == paso - 1) * 0.55
        elif patron == 'manchas_grandes' and c != 'abajo':
            # Como la piel de los raptores del cartel: el tono de fondo con manchas oscuras grandes e irregulares (de 2
            # a 5 píxeles, de tres rejillas desplazadas que se suman) y alguna mancha clara; sin cuadrícula.
            n1 = _azar1((xs + 1) // 3, (ys + 1) // 3, s + 61)
            n2 = _azar1((xs + 2) // 2, ys // 2, s + 67)
            n3 = _azar1(xs // 4, (ys + 2) // 4, s + 71)
            mancha = n1 * 0.45 + n2 * 0.2 + n3 * 0.35
            v = v - (mancha < 0.34) * 1.1 + (mancha > 0.74) * 0.6
        elif patron == 'escamas' and c != 'abajo':
            # Escamas de 4 x 3 al tresbolillo: cada una con su tono, la luz arriba a la izquierda y el contorno oscuro
            # abajo y a la derecha.
            fila = ys // 3
            x = xs + (fila % 2) * 2
            u, r = x % 4, ys % 3
            tono = (_azar1(x // 4, fila, s + 41) - 0.5) * 0.9
            v = v + tono + ((u == 0) & (r == 0)) * 0.8 - ((u == 3) | (r == 2)) * 0.7
        elif patron == 'vientre' and c not in ('arriba', 'abajo'):
            # Las placas del vientre: bandas de 2 de alto, más claras, con la junta oscura.
            v = v + 0.7 - ((ys % 3) == 2) * 1.0 + ((ys % 3) == 0) * 0.3
        elif patron == 'anillos' and c not in ('arriba', 'abajo'):
            k = ys % (paso or 4)
            v = v - (k == (paso or 4) - 1) * 1.0 + (k == 0) * claro
        elif patron == 'moteado' and c != 'abajo':
            # Escamas de 3 x 2 con su luz y su sombra, y manchas oscuras de 3 x 3 por encima (los raptores).
            fila = ys // 2
            x = xs + (fila % 2) * 1
            u, r = x % 3, ys % 2
            v = v + ((u == 0) & (r == 0)) * 0.6 - ((u == 2) & (r == 1)) * 0.5
            b = _azar1(xs // 3, ys // 3, s + 11 + semilla)
            v = v - (b < 0.28) * 1.1 + (b > 0.85) * 0.5
        elif patron == 'manchas':
            b = _azar1(xs // 3, ys // 3, s + 11 + semilla)
            v = v - (b < 0.3) * 1.0
        elif patron == 'vetas' and c not in ('arriba', 'abajo'):
            col = _azar1(xs, np.zeros_like(xs), s + 13)
            corta = _azar1(xs, ys // 3, s + 17)
            v = v - ((col < 0.28) & (corta > 0.2)) * 0.9 + ((col > 0.85) & (corta > 0.4)) * 0.5
        elif patron == 'hebras' and c not in ('arriba', 'abajo'):
            # Hebras largas a lo largo, una por columna, cada una con su tono, cortadas de tarde en tarde.
            tono = (_azar1(xs, np.zeros_like(xs), s + 21) - 0.5) * 2.0
            corte = _azar1(xs, ys // 6, s + 23) < 0.2
            v = v + tono * 0.9 - corte * 0.6
        elif patron == 'mechones':
            desf = (_azar1(xs, np.zeros_like(xs), s + 5) * 5).astype(int)
            k = (ys + desf) % 5
            v = v + (k == 0) * 1.0 + (k == 1) * 0.6 + (k == 2) * 0.2 - (k == 4) * 0.9
        idx = np.clip(np.round(v), 0, len(R) - 1)
        return L._rgba(L.color_continuo(R, idx)), None
    p = B.Pintor(nombre, fn)
    return B.fino(p, FINO) if fino else p


def penacho(m, parte, M, x, z, n, alto, grueso, pints, hacia=(0, 1, 0), abre=25, semilla=1, y0=0.0):
    """Un manojo de púas sueltas (la cresta de musgo, la de pelo): 'n' vigas de varios gruesos y largos que salen de
    puntos al azar del rectángulo x × z (del marco M, a la altura y0) hacia 'hacia', abiertas hasta 'abre' grados, cada
    una de uno de los pintores de 'pints' (para que haya varios tonos, como en los dibujos)."""
    rng = np.random.default_rng(semilla)
    hacia = B._u(np.asarray(hacia, float))
    for k in range(n):
        px = rng.uniform(*x)
        pz = rng.uniform(*z)
        largo = rng.uniform(*alto)
        g = rng.choice(grueso)
        ang = math.radians(rng.uniform(-abre, abre))
        ang2 = math.radians(rng.uniform(-abre, abre))
        d = B._u(hacia + np.array((math.sin(ang), 0, math.sin(ang2))))
        a = np.array((px, y0, pz))
        b = a + d * largo
        m.viga(parte, P(M, a), P(M, b), g, pints[k % len(pints)], extra=0.0)


def garras(m, parte, base, hacia, n, largo, sep, pint, grueso=0.7, curva=(0, -1, 0)):
    """'n' garras en fila (separadas 'sep' a lo ancho, en X) que salen de 'base' hacia 'hacia' y se curvan."""
    hacia = B._u(np.asarray(hacia, float))
    curva = B._u(np.asarray(curva, float))
    for k in range(n):
        p = np.asarray(base, float) + np.array(((k - (n - 1) / 2) * sep, 0, 0))
        q = p + hacia * largo * 0.6
        r = q + B._u(hacia + curva) * largo * 0.5
        m.viga(parte, p, q, grueso, pint, extra=0.2)
        m.viga(parte, q, r, grueso * 0.7, pint, extra=0.1)


# ======================================================================================================================
#  Las láminas: lo fino, dibujado y recortado (Juan, 20-10-2026: el musgo, las garras, los dientes y las crestas «no son
#  bloques»). Una lámina es una cara sin grosor que el render de las bestias ve por los dos lados; dos cruzadas (como las
#  plantas de Minecraft) dan volumen desde cualquier lado.
# ======================================================================================================================
def lamina(m, parte, M, ancho, alto, pint, abajo=False, x0=None):
    """Una lámina en el plano XY del marco M, de 'ancho' x 'alto', que sale de su origen hacia arriba (o hacia abajo,
    con 'abajo'), centrada en X (o desde x0)."""
    y0 = -alto if abajo else 0.0
    xa = -ancho / 2 if x0 is None else x0
    m._caja(parte, M, xa, y0, 0.0, ancho, alto, 0.0, None, {c: (pint if c == 'frente' else None) for c in B.CARAS})


def cruz(m, parte, M, ancho, alto, pint, abajo=False, giro=0.0):
    """Dos láminas cruzadas desde el origen del marco M (hacia su Y)."""
    for g in (45.0, 135.0):
        lamina(m, parte, M @ B.girar((0, giro + g, 0)), ancho, alto, pint, abajo)


def mata(nombre, R, hojas=6, base=0.8, ancho=1.2):
    """Un manojo (musgo, pelo, llamas): briznas que salen de abajo, de largos distintos y algo torcidas, que se afilan
    hasta la punta, oscuras en la base y claras arriba, con el canto de la izquierda más claro; lo demás, vacío."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        h = th - y
        rng = np.random.default_rng(int(s) * 17 + tw * 3 + th)
        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        orden = rng.permutation(hojas)
        for k in orden:
            x0 = (k + 0.5) / hojas * tw + rng.uniform(-0.5, 0.5)
            largo = rng.uniform(0.5, 1.0) * th
            tuerce = rng.uniform(-0.35, 0.35)
            w0 = ancho * rng.choice([0.9, 1.2, 1.5])
            cx = x0 + tuerce * h
            w = w0 * np.clip(1.0 - h / largo, 0, 1) ** 0.7 + 0.35
            mk = (h < largo) & (np.abs(x - cx) < w)
            tono = base + 3.0 * np.clip(h / largo, 0, 1) + rng.uniform(-0.3, 0.3) + ((x - cx) < -w * 0.3) * 0.5
            v = np.where(mk, tono, v)
            dentro |= mk
        rgb = L.color_continuo(R, np.clip(np.round(v), 0, 4))
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def garras_lamina(nombre, R, n=3, curva=0.0, adelante=False):
    """Garras dibujadas: 'n' garras que cuelgan de la raíz (arriba), anchas arriba y en punta abajo, que se curvan hacia
    la derecha al final ('curva'); con 'adelante', salen de la izquierda y apuntan a la derecha, curvándose hacia abajo
    (las de los pies, vistas de lado). Claras a un lado y en sombra al otro, con la punta más clara."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        if adelante:
            a_, b_, la, lb = y, x, th, tw          # a: a lo ancho de la fila de garras; b: a lo largo de cada garra
        else:
            a_, b_, la, lb = x, y, tw, th
        t = b_ / lb
        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        for k in range(n):
            c0 = (k + 0.5) / n * la
            cc = c0 + curva * (t ** 2) * la / n * (1.0 if not adelante else 1.4)
            w = la / n * 0.36 * np.clip(1.0 - t, 0, 1) ** 0.8 + 0.3
            mk = (np.abs(a_ - cc) < w) & (t < 0.97)
            tono = 2.6 + ((a_ - cc) < 0) * 0.7 - ((a_ - cc) > w * 0.4) * 0.6 + (t > 0.7) * 0.5
            v = np.where(mk, tono, v)
            dentro |= mk
        rgb = L.color_continuo(R, np.clip(np.round(v), 0, 4))
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def aleta(nombre, R, RQ=None, puntas=1, base=2.0, translucida=False, recta=False):
    """Una cresta en aleta (las de la cabeza de los raptores): ancha abajo y en punta arriba (o con varias puntas), echada
    hacia atrás, con el canto de RQ (o un tono más claro) y la raíz más oscura; lo de alrededor, vacío. 'translucida':
    el centro más claro y verdoso, como el vidrio del dibujo."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        u = x / tw
        h = 1.0 - y / th                                   # 0 abajo, 1 arriba
        # El perfil: de la base (todo el ancho) a la punta, echada hacia la izquierda (atrás).
        f = (u * puntas) % 1.0
        techo = 0.55 + 0.45 * (1.0 - np.abs(2 * f - 1)) ** 1.2 - (1.0 - u) * 0.15
        dentro = h < techo
        borde = dentro & ((h > techo - 0.12) | (xs == 0) | (xs == tw - 1) | (ys == th - 1))
        if recta:
            # Una vela con las esquinas de arriba bien redondas (que no se lea como un bloque) y el canto marcado.
            r = 0.36 * min(tw, th)
            dd = np.hypot(np.maximum(0.0, np.abs(x - tw / 2) - (tw / 2 - r)), np.maximum(0.0, r - y))
            dentro = dd < r
            borde = dentro & ((dd > r - 1.6) | (ys == th - 1))
        v = base + h * 1.2
        if translucida:
            v = np.where(borde, 3.6, 1.8 + ((xs + ys) % 4 == 0) * 0.6)
        rgb = L.color_continuo(R, np.clip(np.round(v), 0, 4))
        if RQ is not None:
            rgb = np.where(borde[..., None], L.color_continuo(RQ, np.full((th, tw), 2.8)), rgb)
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def garras_mano(m, parte, punto, pint_frente, pint_perfil, largo=4.0, ancho=3.4):
    """Las garras de una mano, dibujadas y no en bloques: una lámina de frente con tres garras que cuelgan y otra de
    perfil con una que cuelga y se curva hacia delante, desde 'punto' (bajo la mano) hacia abajo."""
    lamina(m, parte, T(*punto), ancho, largo, pint_frente, abajo=True)
    lamina(m, parte, T(*punto) @ B.girar((0, -90, 0)), ancho * 0.9, largo, pint_perfil, abajo=True)


def garras_pie(m, parte, punto, pint, n=3, sep=1.3, largo=3.0, alto=2.0):
    """Las garras de un pie: una lámina de perfil por dedo, que sale de la punta del pie ('punto') hacia delante."""
    for k in range(n):
        p = np.asarray(punto, float) + np.array(((k - (n - 1) / 2) * sep, 0, 0))
        lamina(m, parte, T(*p) @ B.girar((0, -90, 0)), largo, alto, pint, abajo=False, x0=0.0)


# ======================================================================================================================
#  Los reptisaurios (el de las cuevas y el guerrero): el mismo cuerpo
# ======================================================================================================================
# Las medidas, contadas en los iconos del cartel (4 píxeles del cartel por píxel de la textura): unos 2,3 bloques de
# alto encorvados, los brazos y las piernas de 4 a 5 de grueso, los brazos largos hasta las rodillas, la cabeza de 9 a 11.
# Lo fino (las garras, los dientes, el musgo, las llamas de la espalda) va dibujado en láminas o en una 2.ª capa, no en
# bloques (Juan, 20-10-2026).
#
# La cara de delante de la cabeza, a 32 por bloque, como la pintó Juan (20-10-2026): los dos ojos amarillos,
# rectángulos (como en el cartel: «no tienen que ser redondos»), a los costados y con poco hueco entre ellos, cada uno
# con una franja negra gruesa de arriba abajo en medio; justo debajo, en la piel, los dos agujeros de la nariz,
# juntos; y por debajo, la piel sigue hasta la boca (sin la encía roja a la vista).
def cara_reptil(ancho, ojo, k):
    """La cara de delante de un reptisaurio agrandado k veces (a 32 por bloque): ancho y ojo, los de su tamaño de
    siempre."""
    return cara_ojos(int(round(ancho * k)), int(round(ojo * k)), alto=int(round(12 * k)), fila0=int(round(4 * k)),
                     filas=int(round(5 * k)))


def cara_ojos(ancho, ojo, alto=12, fila0=4, filas=5, rendija=2):
    """El mapa de la cara (ancho x alto): los ojos de 'ojo' de ancho, uno en cada costado, de las filas fila0 a
    fila0 + filas - 1, con la rendija de 'rendija' de ancho en medio; y la nariz, debajo, en el centro."""
    g = [['.'] * ancho for _ in range(alto)]
    for c0 in (0, ancho - ojo):
        for f in range(fila0, fila0 + filas):
            for c in range(c0, c0 + ojo):
                g[f][c] = 'y'
            r0 = c0 + (ojo - rendija) // 2
            for c in range(r0, r0 + rendija):
                g[f][c] = 'k'
    n0 = ancho // 2 - 2
    for f in (fila0 + filas, fila0 + filas + 1):
        g[f][n0] = g[f][ancho - 1 - n0] = 'n'
    return [''.join(f) for f in g]


CARA_REPTISAURIO = cara_ojos(18, 8)


def lado_ojo(ancho, alto, k=1.0):
    """La cara del lado de la cabeza (ancho x alto, a 32 por bloque; el frente a la derecha): el ojo, que dobla la
    esquina desde la cara de delante."""
    filas = ['.' * ancho for _ in range(alto)]
    f0, n, w = int(round(4 * k)), int(round(5 * k)), int(round(2 * k))
    for f in range(f0, f0 + n):
        filas[f] = '.' * (ancho - w) + 'y' * w
    return filas


def cuatro_dientes(nombre, R, encia=2, largo=0.85, corto=0.36):
    """Los dientes de los reptisaurios en una 2.ª capa, como los pintó Juan (20-10-2026: «solo 4, 2 en el centro
    pequeños y 2 más largos a cada extremo»; y la segunda vez, los colmillos más anchos, bajo cada ojo): cuelgan del
    borde de la mandíbula de arriba, en la cara de delante; los colmillos, de dos píxeles de ancho y largos, con la
    punta de uno; los dos del medio, de uno y cortos. Claros a la izquierda y en sombra a la derecha. Las filas de
    arriba de la capa, las que montan sobre la cara, quedan vacías: ahí sigue la piel, con la nariz."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        tex = np.zeros((th, tw, 4), np.uint8)
        if cara != 'frente':
            return tex, None
        r = y - encia
        alto = th - encia
        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        for fx, fl, dos in ((0.17, largo, True), (0.4, corto, False), (0.6, corto, False), (0.83, largo, True)):
            lk = max(2.0, round(fl * alto))
            cx = round(fx * tw) if dos else np.floor(fx * tw) + 0.5
            w = 1.0 if dos else 0.5
            mk = (r >= 0) & (r < lk) & (np.abs(x - cx) < w)
            v = np.where(mk, 3.3 - (x > cx) * 0.8, v)
            dentro |= mk
        tex = L._rgba(L.color_continuo(R, np.clip(np.round(v), 0, 4)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


# La calavera de vaca de los hombros del guerrero: el frente del cráneo (6 x 5), con las cuencas; el frente del hocico
# (4 x 3), con los agujeros de la nariz y los dientes; y su lado (4 x 3), con la fila de dientes.
CALAVERA_CRANEO = [
    '......',
    'kk..kk',
    'kk..kk',
    '.k..k.',
    '......',
]
CALAVERA_HOCICO = [
    '.kk.',
    '....',
    'w.ww',
]
CALAVERA_LADO = [
    '....',
    '....',
    'w.w.',
]


def _con_cara(nombre, piel, mapas, colores, fino=False):
    """El pintor de la piel con un mapa encima en las caras de 'mapas'. Con 'fino', el mapa va a 32 por bloque (los ojos
    con su ranura fina) y la piel sigue al píxel de siempre (se pinta a la mitad y se dobla)."""
    def fondo(tw, th, c, s):
        if fino:
            base = piel.fn(max(1, (tw + 1) // 2), max(1, (th + 1) // 2), c, s)[0][..., :3].astype(float)
            return np.repeat(np.repeat(base, 2, 0), 2, 1)[:th, :tw]
        return piel.fn(tw, th, c, s)[0][..., :3].astype(float)
    return con_mapa(nombre, fondo, mapas, colores, fino=fino)


def manojos(m, parte, M, puntos, pints, ancho, alto, inclina=-25.0):
    """Manojos de láminas cruzadas (el musgo, las llamas) en los puntos (x, y, z) del marco M, cada uno echado hacia atrás
    'inclina' grados y del largo que le toque de 'alto' (mín, máx)."""
    rng = np.random.default_rng(len(puntos) * 7 + int(ancho * 10))
    for k, p in enumerate(puntos):
        al = rng.uniform(*alto)
        giro = rng.uniform(0, 90)
        cruz(m, parte, M @ T(*p) @ B.girar((inclina + rng.uniform(-10, 10), 0, rng.uniform(-12, 12))), ancho, al,
             pints[k % len(pints)], giro=giro)


def reptisaurio(m, piel, anillos, R, RH, encorvado, y_cadera=19.0, grueso=1.0, cabeza=(9, 6, 8), cuello_y=14.4,
                abre_boca=14, cuello_z=3.4, cara=None, cabeza_giro=4, muslo=None, vientre=None, k=1.0, ojos_lado=True):
    """El cuerpo de los reptisaurios. piel: el pintor del tronco y la cabeza; anillos: el de los brazos y las piernas;
    R: la rampa de la piel (para la ceja); RH: la del hueso (garras, dientes); encorvado: lo que se echa hacia delante el
    tronco (grados). Devuelve los marcos del tronco y de la cabeza, los hombros y los pintores de hueso."""
    h = pix(f'hueso_{m.id}', RH, base=2.6, luz=0.6, ruido=0.4)
    garra_recta = garras_lamina(f'garra_mano_{m.id}', RH, n=1)
    garra_der = garras_lamina(f'garra_curva_{m.id}', RH, n=1, curva=1.2)
    garra_izq = garras_lamina(f'garra_curva_i_{m.id}', RH, n=1, curva=-1.2)
    garra_pie = garras_lamina(f'garra_pie_{m.id}', RH, n=1, curva=0.9, adelante=True)
    # Las piernas: el muslo grueso hacia delante, la espinilla hacia atrás y el pie largo; las garras, dibujadas.
    for lado, ld in LADOS:
        cad = np.array((lado * 3.6, y_cadera, 0.0))
        rod = np.array((lado * 4.2, y_cadera * 0.56, 4.6))
        tob = np.array((lado * 4.2, 3.0, -0.8))
        n = m.parte(f'pierna_{ld}', 'cuerpo', tuple(cad))
        m.viga(n, rod, cad, 3.8 * grueso, muslo or anillos, extra=1.4)
        # Lo de debajo de la rodilla, aparte (para que la rodilla se doble al andar).
        r_ = m.parte(f'espinilla_{ld}', n, tuple(rod))
        m.viga(r_, tob, rod, 3.0 * grueso, anillos, extra=1.0)
        m.caja(r_, (lado * 4.2, 1.0, 1.6), (4, 2, 5), piel)
        garras_pie(m, r_, (lado * 4.2, 0.0, 4.0), garra_pie, n=3, sep=1.3, largo=3.0, alto=2.2)
    # El tronco, aparte de la cadera (para que se balancee sin mover los pies): echado hacia delante; la pelvis y el
    # pecho ancho.
    m.parte('tronco', 'cuerpo', (0, y_cadera, 0))
    Mt = T(0, y_cadera, 0) @ B.girar((encorvado, 0, 0))
    caras_v = {'frente': vientre} if vientre is not None else None
    caja_en(m, 'tronco', Mt, (0, 3.5, 0), (8, 7, 6), piel, caras=caras_v)
    caja_en(m, 'tronco', Mt, (0, 11.0, 0.4), (10, 9, 7.4), piel, caras=caras_v)
    # La cabeza, sobre el pecho: el cráneo con los ojos, la ceja que los hunde y la mandíbula abierta.
    cuello = P(Mt, (0, cuello_y, cuello_z))
    Mh = T(*cuello) @ B.girar((cabeza_giro, 0, 0))
    m.parte('cabeza', 'tronco', tuple(cuello))
    colores = {'y': H('e6d21c'), 'k': H('0a0804'), 'n': H('0a0804'),
               'd': L.color_continuo(R, np.array([0.0]))[0]}
    cw, ch, cd = cabeza
    lado = lado_ojo(int(round(cd * 2 * k)), int(round(ch * 2 * k)), k) if ojos_lado else None
    craneo = _con_cara(f'cara_{m.id}', piel, {'frente': cara or CARA_REPTISAURIO, 'izq': lado, 'der': lado}, colores,
                       fino=True)
    caja_en(m, 'cabeza', Mh, (0, ch / 2 - 1.4, cd / 2), (cw, ch, cd), piel,
            caras={'frente': craneo, 'izq': craneo, 'der': craneo})
    ceja = pix(f'ceja_{m.id}', R, base=1.2, luz=0.5, ruido=0.4)
    caja_en(m, 'cabeza', Mh, (0, ch - 1.4 - 1.5, cd + 0.4), (cw - 0.2, 1.0, 1.0), ceja)
    # La boca: el paladar rojo oscuro y los cuatro dientes en una 2.ª capa, que cuelgan de la encía de arriba.
    boca = pix(f'boca_{m.id}', rampa('1a0202', '3a0606', '5e0c0c', '861414', 'a82020'), base=1.4, luz=0.3, ruido=0.6)
    caja_en(m, 'cabeza', Mh, (0, -1.5, cd * 0.6), (cw - 3.4, 0.4, cd * 0.7), boca)
    # Los colmillos, del largo que cabe en la boca abierta (hasta el labio de abajo), para que no se vean sobre la
    # mandíbula como si estuvieran partidos.
    a_ = math.radians(abre_boca)
    labio = 1.4 * math.cos(a_) - (cd - 2.4) * math.sin(a_)
    largo_c = min(0.85, max(0.4, -labio * 2.0 / 6.0))
    caja_en(m, 'cabeza', Mh, (0, -2.4, cd - 0.25), (cw - 1.2, 4.0, 1.0),
            cuatro_dientes(f'dientes_{m.id}', RH, largo=largo_c))
    gozne = P(Mh, (0, -1.4, 1.4))
    Mj = T(*gozne) @ B.girar((abre_boca, 0, 0))
    m.parte('mandibula', 'cabeza', tuple(gozne))
    caja_en(m, 'mandibula', Mj, (0, -1.0, cd / 2 - 0.2), (cw - 1.4, 2.0, cd - 1.6), piel, caras={'arriba': boca})
    hombros = []
    for lado, ld in LADOS:
        hombros.append((lado, ld, P(Mt, (lado * 6.2, 13.0, 0.6))))
    return Mt, Mh, hombros, h, (garra_recta, garra_der, garra_izq)


# Los brazos de todos los reptisaurios, como los dibujó Juan (20-10-2026, de frente: «el cuerpo y los brazos como
# deberían estar en todos los reptisaurios que hagamos»): salen del hombro hacia fuera, bajan en arco por fuera del
# cuerpo y vuelven hacia dentro a la altura de la cadera, con la mano y las garras mirando al cuerpo.
# (tramo del hombro al codo, tramo del codo a la muñeca), con +X hacia fuera.
BRAZO_REPTISAURIO = ((6.2, -2.6, 0.6), (-3.4, -10.4, 1.4))


def brazo_reptisaurio(m, lado, ld, hombro, anillos, piel, garras, grueso=1.0):
    """Un brazo de reptisaurio con la forma de siempre (BRAZO_REPTISAURIO), escalada con el grueso."""
    (cx, cy, cz), (mx, my, mz) = BRAZO_REPTISAURIO
    k = 0.85 + 0.15 * grueso
    return brazo(m, lado, ld, hombro, anillos, piel, garras, (lado * cx * k, cy * k, cz), (lado * mx * k, my * k, mz),
                 grueso)


def brazo(m, lado, ld, hombro, anillos, piel, garras, codo_d, mano_d, grueso=1.0):
    """Un brazo largo y grueso: el brazo hasta el codo, el antebrazo hasta la muñeca y, al final, la mano (Juan,
    20-10-2026: «debería ser manos al final y de ahí sus garras»): la palma, más ancha que la muñeca, y tres dedos que
    bajan por delante, cada uno con su garra de hueso dibujada que cuelga y se curva. codo_d y mano_d: los tramos (del
    hombro al codo y del codo a la muñeca)."""
    n = m.parte(f'brazo_{ld}', 'tronco', tuple(hombro))
    codo = hombro + np.asarray(codo_d, float)
    mano = codo + np.asarray(mano_d, float)
    m.viga(n, codo, hombro, 3.8 * grueso, anillos, extra=1.4)
    # Del codo para abajo, aparte (para que el codo se doble).
    n = m.parte(f'antebrazo_{ld}', n, tuple(codo))
    m.viga(n, mano, codo, 3.2 * grueso, anillos, extra=1.0)
    eje = B._u(mano - codo)
    pm = mano + eje * 1.8
    # La mano, normal (Juan, 20-10-2026: «sus manos están raras, hazlas normales»): un puño ancho al final del brazo,
    # con tres dedos que salen por abajo y por el lado de dentro, en fila de delante atrás, y de cada uno su garra,
    # que se curva hacia el cuerpo (de frente, las garras apuntan hacia dentro, como en su dibujo).
    m.caja(n, pm, (3.2 * grueso, 3.2, 3.8 * grueso), piel)
    hacia_dentro = garras[1] if lado < 0 else garras[2]
    for k in (-1, 0, 1):
        dedo = pm + np.array((-lado * 0.9 * grueso, -2.2, k * 1.25 * grueso))
        m.caja(n, dedo, (1.4, 1.4, 1.1), piel)
        punta = dedo + np.array((-lado * 0.3, -0.6, 0))
        Mg = T(*punta) @ B.girar((0, 0, -lado * 30))
        lamina(m, n, Mg, 2.0, 4.0, hacia_dentro, abajo=True)
        lamina(m, n, Mg @ B.girar((0, -90, 0)), 1.6, 4.0, garras[0], abajo=True)
    return f'brazo_{ld}', n, codo, mano


def anims_reptisaurio(m):
    """reposo: respira, mira a un lado y a otro y mece los brazos; siempre: la boca, que se mueve un poco; andar y
    correr: las piernas con la rodilla que se dobla, los brazos a contrapaso con el codo, el tronco que se balancea y la
    cabeza que cabecea (al correr, más deprisa y echado hacia delante); ataque: levanta los dos brazos y descarga el
    zarpazo, con el tronco y la cabeza; especial: el rugido al verte (la cabeza atrás, la boca abierta del todo y los
    brazos abiertos); muerte: se desploma de lado."""
    r = m.anim('reposo', 4.0, bucle=True)
    r.onda('tronco', 'r', 0, 2.0, periodo=4.0)
    r.rot('cabeza', [(0, 0, 0, 0), (0.6, 0, 16, 0), (1.5, 2, 16, 0), (2.0, 0, 0, 0), (2.6, 0, -16, 0),
                     (3.5, 2, -16, 0), (4.0, 0, 0, 0)])
    for k, (lado, ld) in enumerate(LADOS):
        r.onda(f'brazo_{ld}', 'r', 2, lado * 3.0, periodo=4.0, fase=0.5 * k)
        r.onda(f'antebrazo_{ld}', 'r', 0, 4.0, periodo=4.0, fase=0.25 + 0.5 * k)
    s_ = m.anim('siempre', 2.5, bucle=True)
    s_.onda('mandibula', 'r', 0, 3, periodo=2.5)
    for nombre, largo, amp, inclina in (('andar', 1.2, 1.0, 0.0), ('correr', 0.7, 1.45, 9.0)):
        a = m.anim(nombre, largo, bucle=True)
        for k, (lado, ld) in enumerate(LADOS):
            f = 0.5 * k
            a.onda(f'pierna_{ld}', 'r', 0, 24 * amp, periodo=largo, fase=f)
            # La rodilla solo se dobla al adelantar la pierna (a mitad del paso al aire); apoyada, recta.
            a.onda(f'espinilla_{ld}', 'r', 0, 22 * amp, periodo=largo, fase=f - 0.25, forma=lambda v: max(0.0, v))
            a.onda(f'brazo_{ld}', 'r', 0, 16 * amp, periodo=largo, fase=f + 0.5)
            a.onda(f'antebrazo_{ld}', 'r', 0, 10 * amp, periodo=largo, fase=f + 0.75, base=-8 * amp)
        a.onda('tronco', 'r', 2, 3.5 * amp, periodo=largo)
        a.onda('tronco', 'r', 1, 5.0 * amp, periodo=largo, fase=0.25)
        a.onda('tronco', 'r', 0, 2.0 * amp, periodo=largo / 2, base=inclina)
        a.onda('tronco', 'm', 1, 0.45 * amp, periodo=largo / 2)
        a.onda('cabeza', 'r', 0, 3.5 * amp, periodo=largo / 2, fase=0.25, base=-inclina * 0.6)
    at = m.anim('ataque', 0.6)
    for lado, ld in LADOS:
        at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.18, -65, 0, lado * 18), (0.32, -2, 0, -lado * 10), (0.6, 0, 0, 0)])
        at.rot(f'antebrazo_{ld}', [(0, 0, 0, 0), (0.18, -35, 0, 0), (0.32, 8, 0, 0), (0.6, 0, 0, 0)])
    at.rot('tronco', [(0, 0, 0, 0), (0.18, -9, 0, 0), (0.32, 12, 0, 0), (0.6, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.18, -12, 0, 0), (0.32, 10, 0, 0), (0.6, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.2, 16, 0, 0), (0.6, 0, 0, 0)])
    e = m.anim('especial', 1.4)
    e.rot('tronco', [(0, 0, 0, 0), (0.3, -14, 0, 0), (1.0, -14, 0, 0), (1.4, 0, 0, 0)])
    e.rot('cabeza', [(0, 0, 0, 0), (0.3, -24, 0, 0), (0.6, -24, 6, 0), (0.8, -24, -6, 0), (1.0, -24, 0, 0),
                     (1.4, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.3, 22, 0, 0), (1.0, 22, 0, 0), (1.4, 0, 0, 0)])
    for lado, ld in LADOS:
        e.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.3, -20, 0, lado * 30), (1.0, -20, 0, lado * 30), (1.4, 0, 0, 0)])
        e.rot(f'antebrazo_{ld}', [(0, 0, 0, 0), (0.3, -20, 0, lado * 15), (1.0, -20, 0, lado * 15), (1.4, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.3, 6, 0, 0), (1.0, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -9, 0)])
    d.rot('cabeza', [(0, 0, 0, 0), (0.4, -15, 0, 0), (1.0, 10, 0, 0)])


# Las rampas, de los iconos: el verde del Salvaje casi negro (101306 a 303721, con luz 454d30), el musgo (3f4a06 a
# 5c7013, con brillo a8c42a), el pardo del Guerrero (2b160f a 4b281d, con luz 6e3c26), la cresta naranja (5a3209 a
# 8b5207, con brillo d08a14), el amarillo de la faja (7f790e a 8f8a15, con luz d0c624), el verde del cinturón (194612 a
# 156e26) y el hueso (8e887c a d6d0c4).
VERDE_OLIVA = rampa('0c0f05', '161b08', '22280e', '30381c', '465030')
MUSGO_A = rampa('3a4a06', '5a7010', '7e9a14', 'a2c020', 'c8e040')
MUSGO_B = rampa('4a5a08', '6e8a10', '92b41a', 'b4d426', 'dcf060')
HUESO = rampa('5e5a50', '8e887c', 'b2ac9e', 'd0cabc', 'ece8dc')
PARDO = rampa('1e0e08', '2e170e', '45251a', '5e3424', '784630')
PARDO_PECHO = rampa('2e170e', '45251a', '603626', '7a4a34', '946048')
NARANJA_A = rampa('3a1c04', '5a3206', '84500a', 'aa680e', 'c8821a')
NARANJA_B = rampa('4a2606', '6e4008', '965c0c', 'b87410', 'd68e1e')
# Las llamas de la cabeza y la espalda: el naranja vivo del cartel, que siga vivo con la sombra de las láminas.
LLAMA = rampa('5a3206', '965c0c', 'c87a12', 'e8961c', 'f8b030')
FAJA = rampa('6e600e', 'a49a16', 'cec424', 'e6dc30', 'f6ee70')
CINTO = rampa('0e2e0c', '194612', '1e6a20', '28902e', '44b448')
# Las calaveras de los hombros del Guerrero: gris medio, apagado (Juan, 20-10-2026: «medio grises, tonos apagados, no
# fuertes»).
GRIS_CALAVERA = rampa('3a3834', '524f4a', '6a6660', '7f7b74', '948f87')


def construir_reptisaurio_salvaje():
    from quiu.reptisaurio_salvaje import construir as c_salvaje
    return c_salvaje()


# La cara del Guerrero (11 x 6, a 32 por bloque: 22 x 12), como la del Salvaje.
CARA_GUERRERO = cara_ojos(22, 10)


def rayas_diag(nombre, R1, R2, ancho=2, paso=5, base=2.4):
    """Tela a rayas en diagonal: rayas de R2 (de 'ancho' píxeles cada 'paso') sobre R1, al píxel y con grano."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s + 3)
        v = base + 0.5 * (0.5 - (ys + 0.5) / th) + np.where(a < 0.1, -1.0, np.where(a > 0.9, 1.0, 0.0)) * 0.6
        v = v + (c == 'arriba') * 0.5 - (c == 'abajo') * 0.6
        raya = ((xs + ys) % paso) < ancho
        idx = np.clip(np.round(v), 0, 4)
        rgb = np.where(raya[..., None], L.color_continuo(R2, np.clip(idx + 1, 2, 4)),
                       L.color_continuo(R1, np.clip(idx - 1, 0, 2)))
        return L._rgba(rgb), None
    return B.Pintor(nombre, fn)


def calavera_vaca(m, parte, c, lado, hueso, craneo_p, hocico_p, lado_p):
    """Una calavera de vaca sentada en el hombro, con el hocico hacia delante y hacia fuera: el cráneo y el hocico en
    bloques, con las cuencas, la nariz y los dientes pintados; y los dos cuernos, que salen de los lados del cráneo
    hacia fuera, se curvan hacia arriba y acaban en punta."""
    S = T(*c) @ B.girar((0, lado * 35, 0))
    caja_en(m, parte, S, (0, 0, 0), (5.4, 4.8, 5.2), hueso, caras={'frente': craneo_p})
    caja_en(m, parte, S, (0, -0.8, 4.0), (3.8, 3.2, 3.2), hueso, caras={'frente': hocico_p, 'izq': lado_p,
                                                                           'der': lado_p})
    for s_ in (1, -1):
        a = P(S, (s_ * 2.4, 1.4, 0.4))
        b = P(S, (s_ * 4.8, 1.0, 0.2))
        c2 = P(S, (s_ * 5.6, 3.4, 0.8))
        d = P(S, (s_ * 5.2, 5.0, 1.6))
        m.viga(parte, a, b, 2.0, hueso, extra=0.8)
        m.viga(parte, b, c2, 1.6, hueso, extra=0.6)
        m.viga(parte, c2, d, 1.1, hueso, extra=0.3)


def construir_reptisaurio_guerrero():
    from quiu.reptisaurio_guerrero import construir as c_guerrero
    return c_guerrero()


# ======================================================================================================================
#  Los dromoraptores (el rojo y el azul): el mismo raptor
# ======================================================================================================================
# Las medidas, contadas en el icono del Rojo (4 píxeles del cartel por píxel): unos 45 de largo y 37 de alto con las
# plumas. El cuerpo, de 18 de largo y 16 de alto; la cola sale de atrás a la altura del cuerpo; la cabeza, una caja larga
# de techo plano (13 x 7,5), con el ojo pequeño atrás, la mitad de abajo más oscura y la boca con los dientes; las
# crestas, aletas finas en la línea del medio (las dos naranjas una detrás de otra y la amarilla delante, translúcida);
# las patas y los brazos, de velocirraptor (Juan, 20-10-2026).
#
# El lado de la cabeza (13 de largo x 7,5: 13 x 7, el frente a la derecha): el ojo amarillo pequeño atrás, el agujero de
# la nariz delante y la mitad de abajo, la de la boca, más oscura.
# El lado de la cabeza (13 de largo x 7,5: 13 x 7, el frente a la derecha): la ceja oscura y, debajo, el ojo amarillo
# con el centro negro, atrás; el agujero de la nariz delante; y la mitad de abajo, la de la boca, más oscura.
LADO_CABEZA_RAPTOR = [
    '.............',
    '............n',
    '.bbbb........',
    '..yky........',
    '.............',
    'qqqqqqqqqqqqq',
    'mmmmmmmmmmmmm',
]
FRENTE_CABEZA_RAPTOR = [
    '........',
    '.n....n.',
    '........',
    '........',
    '........',
    'qqqqqqqq',
    'mmmmmmmm',
]
LADO_CRANEO_RAPTOR = [
    '.......',
    '.......',
    '.bbbb..',
    '..yky..',
    '.......',
    '.......',
    'qqqqqqq',
    'mmmmmmm',
]
LADO_HOCICO_RAPTOR = [
    '.......',
    '.....n.',
    '.......',
    '.......',
    'qqqqqqq',
    'mmmmmmm',
]
FRENTE_HOCICO_RAPTOR = [
    '.......',
    '.n...n.',
    '.......',
    '.......',
    'qqqqqqq',
    'mmmmmmm',
]
# Las garras de los raptores: gris medio negro (Juan, 20-10-2026).
GARRA_OSCURA = rampa('121214', '232327', '38383e', '505058', '6c6c76')


def gajos(nombre, R, RQ, n=6, abre=(-50, 50), largos=None, base=1.6, hacia='arriba', ancho=None):
    """Las plumas de los dromoraptores, en aleta: un abanico (que sale de abajo en medio, o de arriba con 'hacia'
    'abajo') de 'n' púas anchas en la base y en punta, de R; las de cada lado, con el canto de fuera de RQ, y la del
    medio con su cañón. Se pintan de fuera adentro (la del medio, delante)."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        ls = largos or [1.0] * n
        W = ancho or (tw / n) * 0.95
        dentro = np.zeros((th, tw), bool)
        linea = np.zeros((th, tw), bool)
        oscuro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        orden = sorted(range(n), key=lambda k: -abs(k - (n - 1) / 2))
        for k in orden:
            largo = ls[k % len(ls)] * th * 0.97
            a = math.radians(abre[0] + (abre[1] - abre[0]) * (k + 0.5) / n if n > 1 else 0.0)
            ax, ay = math.sin(a), math.cos(a)
            dx, dy = x - tw / 2.0, (th - y) if hacia == 'arriba' else y
            t = dx * ax + dy * ay
            e = dx * ay - dy * ax
            d = np.abs(e)
            f = np.clip(t / largo, 0, 1)
            dt = math.radians((abre[1] - abre[0]) / n)
            w = 0.62 * np.maximum(t, 1.5) * dt * np.clip((1.0 - f) / 0.32, 0, 1) ** 0.8 + 0.4
            mk = (t > -1.0) & (t < largo) & (d < w)
            borde = mk & (d > w - 0.9)
            medio = (n - 1) / 2
            fuera = borde & (((k < medio) & (e < 0)) | ((k > medio) & (e > 0))) & (f > 0.15)
            cana = mk & (d < 0.5) & (t < largo - 1.2) & (abs(k - medio) < 0.6)
            linea = np.where(mk, cana | fuera, linea)
            oscuro = np.where(mk, borde & ~fuera, oscuro)
            v = np.where(mk, base + 1.6 * f, v)
            dentro |= mk
        v = v - oscuro * 1.2 + (_azar1(xs, ys, s) > 0.92) * 0.6
        rgb = np.where(linea[..., None], L.color_continuo(RQ, np.full((th, tw), 2.6)),
                       L.color_continuo(R, np.clip(np.round(v), 0, 4)))
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def puas(nombre, R, RQ, n=6, abre=(-50, 50), largos=None, curva=-14.0, hacia='arriba', memb=0.8):
    """Los abanicos de los dromoraptores, en aleta de púas (Juan, 20-10-2026: «aletas mejoradas», con su dibujo): las
    púas de RQ salen de la base (abajo en medio, o arriba con 'hacia' 'abajo'), largas y finas, y se curvan hacia la
    punta ('curva', en grados); entre ellas, la membrana de R, que llega a 'memb' del largo de las púas y se mete en
    curva entre una y otra, así que las púas asoman sueltas. La membrana, oscura en la raíz y clara hacia fuera, con
    una veta en medio de cada gajo."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        dx = x - tw / 2.0
        dy = (th - y) if hacia == 'arriba' else y
        r = np.hypot(dx, dy) + 1e-6
        phi = np.degrees(np.arctan2(dx, dy))
        ls = largos or [1.0] * n
        Ls = [ls[k % len(ls)] * th * 0.97 for k in range(n)]
        ang = [abre[0] + (abre[1] - abre[0]) * k / max(1, n - 1) for k in range(n)]

        def eje(k):
            return ang[k] + curva * np.clip(r / Ls[k], 0, 1) ** 2
        memb_ = np.zeros((th, tw), bool)
        vm = np.zeros((th, tw))
        for k in range(n - 1):
            a0, a1 = eje(k), eje(k + 1)
            f = (phi - a0) / (a1 - a0)
            borde = memb * (Ls[k] * (1 - f) + Ls[k + 1] * f) * (1 - 0.2 * np.sin(np.pi * np.clip(f, 0, 1)))
            mk = (f >= 0) & (f <= 1) & (r < borde)
            vm = np.where(mk, 1.1 + 2.1 * r / np.maximum(borde, 1) - 0.5 * f - (np.abs(f - 0.5) < 0.05) * 0.5, vm)
            memb_ |= mk
        pua = np.zeros((th, tw), bool)
        vq = np.zeros((th, tw))
        for k in range(n):
            t = np.clip(r / Ls[k], 0, 1)
            d = np.radians(phi - eje(k)) * r
            w = 0.5 * (1 - t) + 0.45
            mk = (r < Ls[k]) & (r > 0.22 * Ls[k]) & (np.abs(d) < w)
            vq = np.where(mk, 2.7 + 1.1 * t + (d < 0) * 0.3, vq)
            pua |= mk
        rgb = L.color_continuo(R, np.clip(np.round(vm), 0, 4))
        rgb = np.where(pua[..., None], L.color_continuo(RQ, np.clip(np.round(vq), 0, 4)), rgb)
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(memb_ | pua, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def cresta_curva(nombre, R, RQ=None, curva=0.4, base=1.6):
    """Una cresta de la cabeza de los raptores, como la dibujó Juan (20-10-2026: «cresta mejorada»): una púa alta y
    estrecha, ancha en la raíz, que se curva hacia atrás (la izquierda de la textura) y acaba en punta; el canto de
    delante, claro (de RQ), y el de atrás, en sombra."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        t = 1.0 - y / th
        cx = tw * 0.6 - curva * tw * t ** 1.6
        w = tw * 0.34 * (1 - t) ** 0.85 + 0.45
        dentro = np.abs(x - cx) < w
        canto = dentro & (x > cx + w - 1.3)
        v = base + 1.6 * t - (x < cx - w + 1.2) * 0.6 + (_azar1(xs, ys, s) > 0.9) * 0.5
        rgb = L.color_continuo(R, np.clip(np.round(v), 0, 4))
        rgb = np.where(canto[..., None], L.color_continuo(RQ if RQ is not None else R, np.full((th, tw), 3.4)), rgb)
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def cresta_raptor(m, parte, z0, y0, largo, alto, pint):
    """Una cresta sobre la línea del medio de la cabeza: una lámina de perfil (de z0 hacia delante)."""
    lamina(m, parte, T(0, y0, z0) @ B.girar((0, -90, 0)), largo, alto, pint, x0=0.0)


def dromoraptor(m, piel, patas, R, plumas, crestas, RH):
    """El raptor. piel: el cuerpo, el cuello, la cabeza, las piernas, los brazos y la cola; patas: las cañas y los pies
    (con anillos); R: la rampa de la piel (la boca); plumas: (rampa de la membrana, rampa de las púas); crestas: (la de
    la cabeza, la amarilla); RH: el hueso de los dientes y las garras. Como lo dibujó Juan encima del nuestro y con la
    anatomía de un raptor (20-10-2026, con dos raptores de referencia): el cuerpo horizontal, hondo en el pecho, que se
    afina hacia la cadera y sigue en una cola larga que adelgaza; el cuello grande detrás de la cabeza; la pierna en
    zigzag (el muslo grande, la espinilla hacia atrás y la caña oscura, casi derecha, detrás, con el pie hacia delante);
    el brazo en L con las garras en gancho; las aletas de púas (las dos de atrás, echadas hacia la cola) y las crestas
    curvas."""
    m.parte('cuerpo', None, (0, 16, 0))
    # El cuerpo: el pecho, hondo, y la cadera, más alta por abajo (la tripa sube hacia atrás), con el lomo recto.
    redondo(m, 'cuerpo', (0, 16.6, 3.0), (10, 15, 11), piel, bisel=2)
    redondo(m, 'cuerpo', (0, 17.8, -5.2), (9.4, 12.4, 9.6), piel, bisel=2)
    # El cuello, grande: un bloque ancho que sigue el techo de la cabeza hacia atrás y baja en cuesta hasta el lomo, así
    # que detrás de la cabeza no queda hueco («la cabeza no tiene que estar vacía; atrás va su cuello grande»).
    m.viga('cuerpo', (0, 19.7, 2.6), (0, 26.1, 10.6), 10.0, piel, ancho=7.6)
    # La cabeza: una caja larga de techo plano, con la mitad de abajo más oscura, y la mandíbula algo abierta.
    m.parte('cabeza', 'cuerpo', (0, 26.0, 10.0))
    hy = 2.5
    colores = {'k': H('120a06'), 'y': H('f0d020'), 'n': H('1a0a06'), 'b': L.color_continuo(R, np.array([0.4]))[0],
               'q': L.color_continuo(R, np.array([1.0]))[0], 'm': L.color_continuo(R, np.array([0.0]))[0]}

    def con(nombre, mapas):
        return _con_cara(nombre, piel, mapas, colores)
    m.caja('cabeza', (0, 23.8 + hy, 15.6), (8, 7.4, 13), piel,
           caras={'izq': con(f'cabeza_{m.id}', {'izq': LADO_CABEZA_RAPTOR}),
                  'der': con(f'cabeza_d_{m.id}', {'der': LADO_CABEZA_RAPTOR}),
                  'frente': con(f'cabeza_f_{m.id}', {'frente': FRENTE_CABEZA_RAPTOR})})
    m.caja('cabeza', (0, 19.6 + hy, 17.0), (7.4, 3.0, 10.0),
           dientes_capa(f'dientes_arriba_{m.id}', RH, arriba=True, encia=2, largo=3, paso=3))
    m.parte('mandibula', 'cabeza', (0, 20.2 + hy, 10.4))
    mandibula = pix(f'mandibula_{m.id}', R, base=1.4, luz=0.4, ruido=0.4)
    m.caja('mandibula', (0, 19.0 + hy, 16.2), (6.8, 2.4, 11.4), mandibula)
    m.caja('mandibula', (0, 20.3 + hy, 16.6), (6.2, 2.2, 9.4),
           dientes_capa(f'dientes_abajo_{m.id}', RH, arriba=False, encia=2, largo=2, paso=4))
    # Las crestas: dos púas altas y curvas, una detrás de otra, y la vela amarilla delante, translúcida.
    cresta_raptor(m, 'cabeza', 9.2, 26.9 + hy, 3.6, 7.2, crestas[0])
    cresta_raptor(m, 'cabeza', 12.2, 26.9 + hy, 3.4, 6.2, crestas[0])
    cresta_raptor(m, 'cabeza', 16.4, 27.2 + hy, 5.6, 5.6, crestas[1])
    # La cola: larga, a la altura del lomo, que adelgaza en cuatro tramos hasta la punta.
    m.parte('cola', 'cuerpo', (0, 20.0, -9.5))
    m.parte('cola2', 'cola', (0, 21.0, -22.5))
    for parte, (z, y, g, largo) in (('cola', (-13.0, 20.2, 6.6, 7.4)), ('cola', (-19.6, 20.8, 5.0, 6.6)),
                                    ('cola2', (-25.6, 21.2, 3.6, 6.2)), ('cola2', (-31.0, 21.4, 2.4, 5.4))):
        m.caja(parte, (0, y, z), (g * 0.9, g, largo), piel)
    # Las piernas, en zigzag como las de un raptor y como las dibujó Juan: el muslo grande, que baja hacia delante desde
    # la cadera hasta la rodilla; la espinilla, que vuelve hacia atrás hasta el talón alto; la caña oscura, casi
    # derecha, detrás del muslo; y el pie, largo hacia delante, con las garras dibujadas y la garra en hoz levantada.
    garra_pie = garras_lamina(f'garra_pie_{m.id}', GARRA_OSCURA, n=1, curva=0.9, adelante=True)
    hoz = garras_lamina(f'hoz_{m.id}', GARRA_OSCURA, n=1, curva=1.4, adelante=True)
    for lado, ld in LADOS:
        dz = -1.0 if lado > 0 else 1.0
        cad = np.array((lado * 5.4, 16.8, -6.6 + dz))
        rod = np.array((lado * 5.6, 10.6, -2.6 + dz))
        tal = np.array((lado * 5.6, 5.8, -8.0 + dz))
        dedos = np.array((lado * 5.6, 1.4, -7.2 + dz))
        n = m.parte(f'pierna_{ld}', 'cuerpo', tuple(cad))
        m.viga(n, rod, cad, 7.0, piel, ancho=4.6, extra=2.4)
        # De la rodilla para abajo, aparte (para que se doble al correr).
        n = m.parte(f'cana_{ld}', n, tuple(rod))
        m.viga(n, tal, rod, 3.6, piel, ancho=3.4, extra=1.6)
        m.viga(n, dedos, tal, 3.2, patas, extra=1.4)
        m.caja(n, (lado * 5.6, 1.0, -5.2 + dz), (3.8, 2.0, 7.6), patas)
        garras_pie(m, n, (lado * 5.6, 0.0, -1.4 + dz), garra_pie, n=3, sep=1.2, largo=2.8, alto=2.0)
        lamina(m, n, T(lado * 4.4, 2.0, -3.8 + dz) @ B.girar((0, -90, 0)) @ B.girar((0, 0, 55)), 3.2, 2.2, hoz,
               x0=0.0)
    # Los brazos, en L como los dibujó Juan: el brazo baja recto del hombro al codo y el antebrazo va recto hacia
    # delante, bajo la cabeza; al final, las garras en gancho, hacia delante y curvadas hacia abajo; del antebrazo
    # cuelga el abanico de púas.
    cortina = puas(f'cortina_{m.id}', plumas[0], plumas[1], n=7, abre=(-56, 56), hacia='abajo', curva=10.0,
                   largos=[0.9, 0.96, 1.0, 1.0, 1.0, 0.96, 0.9], memb=0.86)
    gancho = garras_lamina(f'gancho_{m.id}', GARRA_OSCURA, n=1, curva=1.7, adelante=True)
    for lado, ld in LADOS:
        hombro = np.array((lado * 5.0, 16.4, 4.5))
        codo = np.array((lado * 5.6, 9.0, 4.5))
        muneca = np.array((lado * 5.6, 9.0, 16.4))
        n = m.parte(f'brazo_{ld}', 'cuerpo', tuple(hombro))
        m.viga(n, codo, hombro, 3.4, piel, extra=1.6)
        m.viga(n, codo, muneca, 3.0, piel, extra=1.4)
        garras_pie(m, n, muneca + np.array((0, -0.5, 0.6)), gancho, n=2, sep=1.3, largo=3.8, alto=3.2)
        m.hoja(n, (lado * 5.6, 4.3, 10.8), 16.0, 9.0, cortina, rot=(0, 90, 0), dos_caras=False)
    # Los abanicos del lomo, en aleta de púas: el de la cola (el más alto) y el de la cadera, echados hacia la cola
    # como los dibujó Juan, con las púas curvadas hacia atrás; y el de los hombros, recto («neutral en cualquier
    # sentido»): derecho, simétrico y con las púas sin curvar. Las garras, gris medio negro: dos en la mano y tres en
    # el pie.
    m.parte('plumas', 'cuerpo', (0, 24.0, 0))
    for (z, y0, ancho, alto, n, largos, abre, inclina, curva) in (
            (-16.8, 21.6, 17.0, 15.0, 6, [0.72, 0.92, 1.0, 0.9, 0.8, 0.62], (-40, 40), -38, 18.0),
            (-8.2, 22.6, 12.0, 10.5, 5, [0.75, 0.95, 1.0, 0.85, 0.7], (-40, 40), -34, 16.0),
            (0.0, 23.0, 15.0, 13.6, 6, [0.66, 0.86, 1.0, 1.0, 0.86, 0.66], (-48, 48), 0, 0.0)):
        a = puas(f'abanico_{m.id}_{z}', plumas[0], plumas[1], n=n, abre=abre, largos=largos, curva=curva, memb=0.86)
        M = T(0, y0, z) @ B.girar((inclina, 0, 0)) @ B.girar((0, 90, 0))
        m._caja('plumas', M, -ancho / 2, 0.0, 0.0, ancho, alto, 0.0, None,
                {c: (a if c == 'frente' else None) for c in B.CARAS})
    m.mirar(('cabeza', 0.7))
    anims_dromoraptor(m)
    return m


def anims_dromoraptor(m):
    """reposo: la cabeza a tirones, como un pájaro (mira a un lado, se queda, mira al otro), la cola que se mece en dos
    tramos y las aletas que respiran; andar y correr: la pierna con la rodilla que se dobla, el cuerpo que sube y baja,
    la cola que ondula al contrapaso y la cabeza firme (al correr, más largo y echado hacia delante, con la cola en
    alto); ataque: echa la cabeza atrás y lanza el mordisco con la boca abierta y las garras por delante; especial: la
    llamada a la manada (la cabeza arriba, la boca abierta y las aletas que se abren); muerte: cae de lado."""
    r = m.anim('reposo', 3.2, bucle=True)
    r.rot('cabeza', [(0, 0, 0, 0), (0.12, 4, 22, 0), (1.0, 4, 22, 0), (1.12, -6, 0, 0), (1.6, -6, 0, 0),
                     (1.72, 2, -20, 0), (2.7, 2, -20, 0), (2.85, 0, 0, 0), (3.2, 0, 0, 0)])
    r.onda('cola', 'r', 1, 6, periodo=3.2)
    r.onda('cola2', 'r', 1, 9, periodo=3.2, fase=0.15)
    r.onda('cuerpo', 'm', 1, 0.3, periodo=1.6)
    s_ = m.anim('siempre', 1.6, bucle=True)
    s_.onda('plumas', 'e', 1, 0.04, periodo=1.6, base=1.0)
    for nombre, largo, amp, inclina in (('andar', 0.8, 1.0, 0.0), ('correr', 0.5, 1.4, 7.0)):
        a = m.anim(nombre, largo, bucle=True)
        for k, (lado, ld) in enumerate(LADOS):
            f = 0.5 * k
            a.onda(f'pierna_{ld}', 'r', 0, 28 * amp, periodo=largo, fase=f)
            a.onda(f'cana_{ld}', 'r', 0, 22 * amp, periodo=largo, fase=f + 0.25, base=-10 * amp)
            a.onda(f'brazo_{ld}', 'r', 0, 6 * amp, periodo=largo, fase=f + 0.5)
        a.onda('cuerpo', 'm', 1, 0.7 * amp, periodo=largo / 2, base=0.5 * amp)
        a.onda('cuerpo', 'r', 0, 1.5 * amp, periodo=largo / 2, base=inclina)
        a.onda('cola', 'r', 1, 7 * amp, periodo=largo, fase=0.5)
        a.onda('cola2', 'r', 1, 10 * amp, periodo=largo, fase=0.65)
        a.onda('cola', 'r', 0, 2 * amp, periodo=largo / 2, base=-inclina * 0.8)
        a.onda('cabeza', 'r', 0, 2 * amp, periodo=largo / 2, fase=0.5, base=inclina * 0.5)
        a.onda('plumas', 'r', 0, 2.5 * amp, periodo=largo / 2)
    at = m.anim('ataque', 0.5)
    at.rot('cabeza', [(0, 0, 0, 0), (0.15, -18, 0, 0), (0.28, 22, 0, 0), (0.5, 0, 0, 0)])
    at.mov('cabeza', [(0, 0, 0, 0), (0.15, 0, 0.5, -1.0), (0.28, 0, -0.5, 3.0), (0.5, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.15, 28, 0, 0), (0.28, 2, 0, 0), (0.5, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.15, -4, 0, 0), (0.28, 5, 0, 0), (0.5, 0, 0, 0)])
    for lado, ld in LADOS:
        at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.15, -35, 0, 0), (0.28, 25, 0, 0), (0.5, 0, 0, 0)])
    e = m.anim('especial', 1.2)
    e.rot('cabeza', [(0, 0, 0, 0), (0.25, -32, 0, 0), (0.9, -32, 0, 0), (1.2, 0, 0, 0)])
    e.rot('mandibula', [(0, 0, 0, 0), (0.25, 26, 0, 0), (0.45, 12, 0, 0), (0.6, 26, 0, 0), (0.9, 20, 0, 0),
                        (1.2, 0, 0, 0)])
    e.esc('plumas', [(0, 1, 1, 1), (0.25, 1.06, 1.12, 1.06), (0.9, 1.06, 1.12, 1.06), (1.2, 1, 1, 1)])
    e.rot('cola', [(0, 0, 0, 0), (0.25, -8, 0, 0), (0.9, -8, 0, 0), (1.2, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.3, 5, 0, 0), (1.0, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -9, 0)])
    d.rot('cola', [(0, 0, 0, 0), (1.0, 0, 15, 0)])


# Las rampas, de los iconos: el Rojo, naranja rojizo (6e2a1f a 8b3517, con luz b25a2e) con manchas granates (3b1820 a
# 552228); las patas casi negras (140e13 a 2e1b24) con anillos rojos; las plumas azul marino (091b40 a 072a75) con el
# cañón naranja (903b1a); el Azul, turquesa (04495c a 147da8) con manchas de verde mar (063535), las patas (0a161b a
# 043340) y las plumas rojas (72110b) con el cañón turquesa. La cresta amarilla, amarillo verdoso (6c6105 a bca508).
ROJIZO = rampa('3a0e18', '5c1c26', '8a2e1e', 'b04620', 'd0682e')
PATA_ROJA = rampa('0a060a', '140e13', '2e1b24', '5a2026', '7e2c22')
PLUMA_AZUL = rampa('06123a', '0c2266', '14348e', '1e48b4', '2c5ccc')
CANON_NARANJA = rampa('5a2410', '903b1a', 'b0501e', 'c86a28', 'e08a3a')
TURQUESA = rampa('04262a', '063a40', '04495c', '0a6a8a', '1a8cb0')
PATA_AZUL = rampa('060e12', '0a161b', '0c2a32', '0e4250', '186070')
PLUMA_ROJA = rampa('400808', '6a100c', '92160e', 'ba2014', 'dc3a22')
CANON_TURQUESA = rampa('06343e', '0c5664', '187e8e', '2aa2b0', '5ac8d2')
CRESTA_AMARILLA = rampa('3a5404', '5a7a08', '86a010', 'c8c418', 'f0e040')


def construir_dromoraptor_rojo():
    from quiu.dromoraptor_rojo import construir as c_rojo
    return c_rojo()


def construir_dromoraptor_azul():
    from quiu.dromoraptor_azul import construir as c_azul
    return c_azul()


# ======================================================================================================================
#  El Plumosaurio
# ======================================================================================================================
# Como en su icono (y como lo corrigió Juan, 20-10-2026): un cuerpo largo y bajo de piel gris oscura, con el plumón
# morado que le cae en dos masas (la de los hombros y la de las caderas) y, entre ellas, el hueco donde se ve el cuerpo;
# el cuello adelantado, gris plateado por delante, con anillos, y una fila de púas negras cortas detrás; la cabeza y el
# hocico de una pieza (la cabeza oscura, alta y corta, con el hocico gris rayado pintado delante, las orejas arriba y
# el ojo de tres rayitas blancas), y detrás la cresta en escalera invertida, más grande, que baja hasta el cuello y
# acaba atrás en la punta morada, que se dobla hacia abajo; y la cola, no muy larga, con el penacho morado colgando.
MORADO = rampa('1a0628', '2d0942', '3d0b5a', '521378', '6e22a0')
GRIS_CUELLO = rampa('121118', '201f2c', '302e41', '43475b', '5a6074')
PLATA = rampa('2e3240', '4a5062', '6c7486', '9098aa', 'b4bccb')
OSCURO = rampa('0c0c12', '181822', '232230', '2e2d3f', '403f54')
# El lado de la cabeza (10,4 de largo x 5,8: 21 x 12 a 32 por bloque, el frente a la derecha), como en el cartel
# (Juan, 20-10-2026: «no es tomar todo sino un poco para hacer la boca»): el ojo, tres rayitas blancas en diagonal; el
# hocico, con rayas grises de arriba abajo en la parte de arriba; y la boca, una raya oscura corta abajo, en la punta,
# que sube un poco en la comisura.
def mapas_plumosaurio(k):
    """El lado y el frente de la cabeza (a 32 por bloque) del Plumosaurio agrandado k veces: en el lado, el ojo (tres
    rayitas blancas en diagonal), el hocico con las rayas grises de arriba abajo (de un píxel de Minecraft cada una)
    y la boca, una raya oscura corta abajo, en la punta, que sube un poco en la comisura; en el frente, las rayas y la
    boca."""
    def r(v):
        return int(round(v * k))

    def rejilla(ancho, alto):
        return [['.'] * ancho for _ in range(alto)]

    def rayas(g, c0, c1, f0, f1):
        for f in range(f0, f1):
            for c in range(c0, c1):
                g[f][c] = 'g' if ((c - c0) // 2) % 2 == 0 else 'h'

    W, Hh = r(21), r(12)
    lado = rejilla(W, Hh)
    rayas(lado, r(13), W, r(2), r(7))
    for i in range(3):
        for f in range(r(3 + i), max(r(3 + i) + 1, r(4 + i))):
            for c in range(r(10 - i), r(12 - i)):
                lado[f][c] = 'w'
    alto_boca = max(1, r(1))
    for f in range(r(9), r(9) + alto_boca):
        for c in range(r(16), W):
            lado[f][c] = 'q'
    for f in range(r(8), r(9)):
        for c in range(r(15), r(16)):
            lado[f][c] = 'q'
    Wf = r(11)
    frente = rejilla(Wf, Hh)
    rayas(frente, 0, Wf, r(2), r(7))
    for f in range(r(9), r(9) + alto_boca):
        for c in range(r(1), Wf - r(1)):
            frente[f][c] = 'q'
    return [''.join(f) for f in lado], [''.join(f) for f in frente]


def aleta_oreja(nombre, R):
    """Las aletas moradas de los lados de la cabeza del Plumosaurio (Juan, 20-10-2026: «le faltan las aletas como orejas
    moradas en los lados de su cabeza»): anchas arriba, en la parte de atrás de la cabeza, y en punta hacia abajo, por
    el cuello (la punta, atrás: a la izquierda); con radios más oscuros que bajan hacia la punta y el canto de delante
    en sombra."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        u, v = x / tw, y / th
        delante = 0.16 + 0.84 * (1 - v) ** 1.25
        dentro = (u > 0.04) & (u < delante) & (v < 0.97)
        radio = np.zeros((th, tw), bool)
        for k in (0.35, 0.6, 0.85):
            cu = 0.12 + (k - 0.12) * (1 - v) ** 1.25
            radio |= np.abs(u - cu) * tw < 0.55
        canto = dentro & ((u > delante - 1.2 / tw) | (u < 0.04 + 1.2 / tw))
        a = _azar1(xs, ys, s)
        val = 2.8 + 0.6 * (1 - v) - radio * 0.9 - canto * 1.2 + (a > 0.93) * 0.5
        tex = L._rgba(L.color_continuo(R, np.clip(np.round(val), 0, 4)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def construir_plumosaurio():
    """El Plumosaurio (día 2)."""
    from quiu.plumosaurio import construir as c_plumosaurio
    return c_plumosaurio()


# ======================================================================================================================
#  El Molusco Rocoso (el «Cavador» hasta el 20-10-2026)
# ======================================================================================================================
# Como en su icono (y como lo corrigió Juan, 20-10-2026): un cuerpo color arena en el medio; de él salen cuatro patas
# finas, también de arena, hasta los cuatro pilares pardos que lo sostienen; la cara delante, con los ojos, las cejas y
# los colmillos dibujados (no en bloques); y el manojo de prismas pardos en el lomo, el del medio el más alto.
ARENA = rampa('5a3e30', '7f604a', 'a08676', 'be957f', 'd8b8a0')
TERRACOTA = rampa('3a1e18', '54302a', '74443a', '945a4c', 'b47a68')
COLMILLO = rampa('6a4a38', '9a8470', 'c4b49e', 'ddd2c0', 'f0eadc')
# La cara (7 x 5, a 32 por bloque: 14 x 10), como en el cartel (Juan, 20-10-2026: «sus ojos y cejas deberían ser así
# como en la foto»): arriba, las cejas, dos cuadritos oscuros bien separados; abajo, los ojos, dos manchas negras
# separadas, cada una con su brillo blanco arriba, hacia dentro.
CARA_CAVADOR = [
    '..............',
    '..............',
    '...kk....kk...',
    '...kk....kk...',
    '..............',
    '..............',
    '.kkwwk..kwwkk.',
    '.kkwwk..kwwkk.',
    '.kkkkk..kkkkk.',
    '.kkkkk..kkkkk.',
]


# La cara del Cavador de un bloque (7 x 5 a la mitad: 8 x 5 a 32 por bloque): las cejas, un píxel oscuro cada una;
# debajo, los ojos, dos manchas negras con el brillo blanco arriba.
CARA_CAVADOR_CHICO = [
    '........',
    '.k....k.',
    '........',
    'kwk..kwk',
    'kkk..kkk',
]


def colmillos(nombre, R, banda=0, delante=(0.27, 0.73), largo=0.95, lado=0.8, corto=0.45):
    """Los colmillos del Cavador en una 2.ª capa (Juan, 20-10-2026: «solo 4 colmillos, 2 delanteros largos y 1 en cada
    cara del lado pequeños»; y luego: «muy delgados y no están conectados a su cabeza»): de dos píxeles de ancho, con
    la punta de uno, que salen de la cara (la capa monta sobre su borde de abajo) y cuelgan; los dos de delante, largos,
    y uno corto en cada lado, cerca de la cara."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        tex = np.zeros((th, tw, 4), np.uint8)
        if cara == 'frente':
            dientes = [(f, largo) for f in delante]
        elif cara == 'izq':
            dientes = [(lado, corto)]
        elif cara == 'der':
            dientes = [(1 - lado, corto)]
        else:
            return tex, None
        r = y - banda
        dentro = np.zeros((th, tw), bool)
        v = np.zeros((th, tw))
        for fx, fl in dientes:
            lk = max(2.0, fl * (th - banda))
            t = np.clip(r / lk, 0, 1)
            cx = fx * tw
            w = np.where(t < 0.75, 1.05, 0.5)
            mk = (r >= 0) & (r < lk) & (np.abs(x - cx) < w)
            v = np.where(mk, 3.0 - (x > cx) * 0.7 + (t > 0.6) * 0.5, v)
            dentro |= mk
        rgb = L.color_continuo(R, np.clip(np.round(v), 0, 4))
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def prisma(nombre, R):
    """Los prismas y los pilares: pardos, al píxel, con la veta a lo largo, como la madera de los dibujos (Juan,
    20-10-2026: que no parezcan ladrillos): cada columna con su tono, que corre de arriba abajo sin cortes, alguna veta
    oscura larga y algún nudo; la tapa, más clara, con sus anillos."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        if c in ('arriba', 'abajo'):
            d = np.maximum(np.abs(xs - (tw - 1) / 2), np.abs(ys - (th - 1) / 2))
            v = np.full((th, tw), 3.0 if c == 'arriba' else 1.2) - (np.round(d) % 2 == 1) * 0.5 + (a > 0.9) * 0.4
        else:
            col = _azar1(xs, np.zeros_like(xs), s + 9)
            veta = (col < 0.22) & (_azar1(xs, ys // 7, s + 5) > 0.15)
            nudo = _azar1(xs // 2, ys // 3, s + 13) < 0.04
            v = 2.3 + 0.6 * (0.5 - (ys + 0.5) / th) + (col - 0.5) * 0.9 + (ys == 0) * 0.4 - veta * 0.7 \
                - nudo * 0.8 + (a > 0.94) * 0.4 - (a < 0.04) * 0.4
        return L._rgba(L.color_continuo(R, np.clip(np.round(v), 0, 4))), None
    return B.Pintor(nombre, fn)


def construir_molusco_rocoso():
    """El Molusco Rocoso / Reptisaurio Cavador."""
    from quiu.cavador import construir as c_cavador
    return c_cavador()


# ======================================================================================================================
#  Todos
# ======================================================================================================================
# ======================================================================================================================
#  En el juego (Juan, 20-10-2026: «mételos al juego»)
# ======================================================================================================================
def _puntos(lista):
    """El dibujo del huevo: unos píxeles sueltos ((x, y), color)."""
    def dib(px, filas, c):
        for (x, y), col in lista:
            px[x, y] = c(col)
    return dib


# Por mob: el nombre (es, en), el huevo (los tres tonos de la piel, los dos del contorno y sus señas) y sus partículas.
EN_JUEGO = {
    'reptisaurio_salvaje': (
        'Reptisaurio Salvaje', 'Wild Reptisaur',
        (('165222', '0c3214', '061c0a'), ('42a42a', '0a2a08'),
         _puntos([((5, 6), 'd4c440'), ((6, 6), '050403'), ((9, 6), 'd4c440'), ((10, 6), '050403'),
                  ((7, 2), '6acd46'), ((8, 3), '42a42a'), ((6, 9), '420410'), ((9, 9), '420410'),
                  ((4, 4), 'ded6c2'), ((11, 4), 'ded6c2')])),
        (('musgo', bc.esquirla((162, 192, 32))), ('hueso', bc.esquirla((208, 202, 188))))),
    'reptisaurio_guerrero': (
        'Reptisaurio Guerrero', 'Reptisaur Warrior',
        (('844824', '5c3018', '1c0e06'), ('e45c12', '7c2006'),
         _puntos([((5, 6), 'd4c440'), ((6, 6), '050403'), ((9, 6), 'd4c440'), ((10, 6), '050403'),
                  ((7, 2), 'f88e22'), ((8, 3), 'e45c12'), ((6, 9), '420410'), ((9, 9), '420410'),
                  ((4, 4), 'ded6c2'), ((11, 4), 'ded6c2'), ((7, 10), 'e6dc30')])),
        (('veneno', bc.gota((120, 200, 60))), ('llama', bc.chispa((232, 150, 28))))),
    'dromoraptor_rojo': (
        'Dromoraptor Rojo', 'Red Dromoraptor',
        (('c63e20', '6e1a12', '3e0e0a'), ('263c8a', '0a122e'),
         _puntos([((9, 6), 'f0c818'), ((10, 6), '120a06'), ((5, 4), '263c8a'), ((6, 3), '3852b4'),
                  ((7, 4), '263c8a'), ((10, 3), 'c8c418'), ((11, 3), 'f0e040')])),
        (('pluma', bc.esquirla((38, 82, 180))), ('escama', bc.esquirla((200, 62, 28))))),
    'dromoraptor_azul': (
        'Dromoraptor Azul', 'Blue Dromoraptor',
        (('1882a0', '0e5c74', '04222c'), ('ac1a22', '3a060a'),
         _puntos([((9, 6), 'f0c818'), ((10, 6), '120a06'), ((5, 4), 'ac1a22'), ((6, 3), 'd62a34'),
                  ((7, 4), 'ac1a22'), ((10, 3), 'c8c418'), ((11, 3), 'f0e040')])),
        (('pluma', bc.esquirla((214, 42, 52))), ('escama', bc.esquirla((24, 130, 160))))),
    'plumosaurio': (
        'Plumosaurio', 'Plumosaur',
        (('403f54', '232230', '0c0c12'), ('6e22a0', '2d0942'),
         _puntos([((9, 5), 'e8e6f0'), ((10, 4), 'e8e6f0'), ((4, 9), '6e22a0'), ((5, 10), '521378'),
                  ((7, 9), '6e22a0'), ((8, 10), '521378'), ((10, 9), '6e22a0'), ((11, 10), '521378')])),
        (('plumon', bc.esquirla((110, 34, 160))), ('polvo', bc.esquirla((120, 110, 96))))),
    'molusco_rocoso': (
        'Molusco Rocoso', 'Rocky Mollusk',
        (('d8b8a0', 'a08676', '5a3e30'), ('b47a68', '54302a'),
         _puntos([((6, 3), '945a4c'), ((7, 2), 'b47a68'), ((9, 3), '945a4c'), ((5, 7), '0c0806'),
                  ((10, 7), '0c0806'), ((5, 9), '0c0806'), ((10, 9), '0c0806'), ((6, 11), 'f0eadc'),
                  ((9, 11), 'f0eadc')])),
        (('tierra', bc.esquirla((120, 88, 60))), ('astilla', bc.esquirla((148, 90, 76))))),
}


def al_juego(m, raiz):
    """Lo escribe en el mod: el modelo y su textura, el huevo, los nombres, el retrato del menú y las partículas."""
    m.exportar(raiz)
    nombre_es, nombre_en, (piel, contorno, dib), particulas = EN_JUEGO[m.id]
    B.huevo(m.id, piel, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    alto = max(1.0, m.altura() / 16.0)
    B.retrato(m, ojo=(alto * 1.0, alto * 0.85, alto * 1.7), objetivo=(0, alto * 0.45, 0), fov=36)
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)


def _a_su_tamano(ident, construir):
    return lambda: agrandar(construir(), TAM[ident])


MOBS = {
    'reptisaurio_salvaje': _a_su_tamano('reptisaurio_salvaje', construir_reptisaurio_salvaje),
    'reptisaurio_guerrero': _a_su_tamano('reptisaurio_guerrero', construir_reptisaurio_guerrero),
    'dromoraptor_rojo': _a_su_tamano('dromoraptor_rojo', construir_dromoraptor_rojo),
    'dromoraptor_azul': _a_su_tamano('dromoraptor_azul', construir_dromoraptor_azul),
    'plumosaurio': _a_su_tamano('plumosaurio', construir_plumosaurio),
    'molusco_rocoso': _a_su_tamano('molusco_rocoso', construir_molusco_rocoso),
}


def main():
    global CARPETA
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    CARPETA = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] not in ('-', '') else None
    if CARPETA:
        os.makedirs(CARPETA, exist_ok=True)
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(MOBS)
    B.TEXEL = 1.0
    for p in pedidos:
        m = MOBS[p]()
        al_juego(m, raiz)
        if CARPETA:
            m.hoja_vistas(os.path.join(CARPETA, f'{m.id}.png'),
                          poses=[('siempre', 0.25), ('andar', 0.3), ('ataque', 0.2), ('muerte', 0.8)])
    B.TEXEL = None


if __name__ == '__main__':
    main()

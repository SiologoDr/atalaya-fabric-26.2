"""
Los phantoms del bestiario (DEDsafío 4, el cartel del 07-10-2026). Primero se recrearon de sus iconos del cartel
(19-10-2026), y Juan pidió mejorarlos: «creo que no debería tener la TNT, y en el caso del otro debería ser mejor su
diseño y otro tipo de color; te lo dejo a tu criterio, mejora el diseño en general y también su textura».

Los dos siguen siendo el phantom de Minecraft (el cuerpo plano, la cabeza ancha con sus ojos que brillan, las alas de
dos tramos y la cola de dos), mejor hechos: el cuerpo y la cabeza redondeados al píxel, una fila de púas por el
espinazo, la ceja de hueso, una uña en la muñeca de cada ala y la membrana en bandas limpias con sus venas. Y lo de cada
uno, de lo que hace:

  phantom_oscuro     te hace soltar un hueco entero del inventario: la pesadilla. Añil profundo, con los huesos de
                     marfil y los ojos violeta pálido que brillan; las alas desgarradas (con agujeros y el borde en
                     jirones), garras curvas debajo del cuerpo para arrancarte lo que llevas, colmillos y la cola
                     acabada en un garfio de dos puntas
  phantom_explosivo  te deja una explosión donde estás. Sin la TNT del cartel: el cuerpo carbonizado con grietas de
                     brasa encendidas, las alas de ceniza con el borde ardiendo como papel quemado, un buche de fuego
                     bajo la panza que late y la cola acabada en una mecha encendida que chisporrotea

Van a escala 1 (16 por bloque, como el phantom); la membrana, los ojos, el buche y la llama de la mecha, a 32 por bloque
(B.fino).

Uso: python bestiario_phantoms.py <raíz> [carpeta de las vistas] [ids]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
import bestiario_creepers as bc
import bestiario_limpio as L
from bestiario import T
from bestiario_hormigas import llama, redondo
from bestiario_limpio import rampa

CARPETA = None
LADOS = ((1, 'i'), (-1, 'd'))          # +X es la izquierda del mob (mira hacia +Z)
FINO = 0.5


def H(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), float)


def _encendido(tex, mk, R, v):
    """Pinta 'mk' con la rampa encendida R (en v) y lo devuelve también como brillo."""
    if not mk.any():
        return tex, None
    tex = tex.copy()
    tex[mk, :3] = np.round(L.color_continuo(R, np.broadcast_to(np.asarray(v, float), mk.shape)[mk]))
    emis = np.zeros_like(tex)
    emis[mk] = tex[mk]
    return tex, emis


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def _tono(tw, th, c, base, luz=0.9):
    """El tono de una pieza: más claro arriba, más oscuro abajo, los cantos de los lados algo más oscuros y la fila de
    arriba de cada lado, el canto, más clara. Sin motas."""
    xs, ys = L._malla(tw, th)
    if c == 'arriba':
        v = np.full((th, tw), base + luz * 0.55)
    elif c == 'abajo':
        v = np.full((th, tw), base - luz * 0.9)
    else:
        v = base + luz * (0.45 - (ys + 0.5) / th) + (ys == 0) * 0.4
    if tw > 3:
        v = v - ((xs == 0) | (xs == tw - 1)) * 0.3
    return xs, ys, v


def placas(nombre, R, base=2.2, brasa=None):
    """La piel del cuerpo en placas que se solapan a lo largo (cada una con su canto claro y la junta oscura de la
    siguiente). Con 'brasa' (una rampa encendida), las juntas son grietas de brasa que brillan y alguna grieta más
    cruza las placas."""
    def fn(tw, th, c, s):
        xs, ys, v = _tono(tw, th, c, base)
        if c in ('izq', 'der'):
            k = xs
        elif c in ('arriba', 'abajo'):
            k = ys
        else:
            k = None
        junta = np.zeros((th, tw), bool)
        if k is not None:
            junta = (k % 3) == 0
            v = v + ((k % 3) == 1) * 0.35
        tex = L._rgba(L.color_continuo(R, v - junta * (0.0 if brasa is not None else 0.7)))
        if brasa is None:
            return tex, None
        grieta = junta & (((xs + ys) % 4) != 0)
        if c in ('izq', 'der', 'arriba'):
            grieta |= (((xs * 2 + ys * 3) % 11) == 0) & ~junta
        return _encendido(tex, grieta, brasa, 2.6 + (((xs + ys) % 3) == 0) * 0.8)
    return B.Pintor(nombre, fn)


def cabeza_pint(nombre, R, ojo, centro, base=2.2, boca=None):
    """La cabeza: su tono, los ojos que brillan (en las esquinas de arriba de delante, con el centro más claro, y que
    asoman por los lados) y la boca, una raya oscura (o encendida, con 'boca', una rampa)."""
    def fn(tw, th, c, s):
        xs, ys, v = _tono(tw, th, c, base)
        tex = L._rgba(L.color_continuo(R, v))
        ojo_m = np.zeros((th, tw), bool)
        nino = np.zeros((th, tw), bool)
        if c == 'frente':
            for x0 in (1, tw - 5):
                ojo_m |= (ys >= 1) & (ys <= 2) & (xs >= x0) & (xs <= x0 + 3)
                nino |= (ys == 1) & (xs >= x0 + 1) & (xs <= x0 + 2)
            fila = th - 2
            raya = (ys == fila) & (xs >= 4) & (xs <= tw - 5)
            if boca is None:
                tex[raya, :3] = np.round(L.color_continuo(R, np.full(raya.sum(), 0.2)))
        elif c in ('izq', 'der'):
            delante = (xs >= tw - 2) if c == 'izq' else (xs <= 1)
            ojo_m = (ys >= 1) & (ys <= 2) & delante
            raya = np.zeros((th, tw), bool)
        else:
            raya = np.zeros((th, tw), bool)
        tex[ojo_m, :3] = ojo
        tex[nino, :3] = centro
        emis = np.zeros_like(tex)
        emis[ojo_m] = tex[ojo_m]
        if boca is not None and raya.any():
            tex, e2 = _encendido(tex, raya, boca, 3.0)
            emis[raya] = e2[raya]
        return tex, (emis if emis[..., 3].any() else None)
    return B.fino(B.Pintor(nombre, fn), FINO)


def hueso(nombre, R, base=2.6, juntas=3, puntas=None):
    """Hueso en vértebras: su tono y una junta oscura cada 'juntas' píxeles a lo largo. Con 'puntas' (una rampa
    encendida), la cara de arriba de cada pieza brilla (las púas y las uñas de brasa)."""
    def fn(tw, th, c, s):
        xs, ys, v = _tono(tw, th, c, base, 0.7)
        if c in ('izq', 'der'):
            v = v - ((xs % juntas) == 0) * 0.7
        elif c in ('arriba', 'abajo'):
            v = v - ((ys % juntas) == 0) * 0.7
        tex = L._rgba(L.color_continuo(R, v))
        if puntas is not None and c == 'arriba':
            return _encendido(tex, np.ones((th, tw), bool), puntas, 3.0)
        return tex, None
    return B.Pintor(nombre, fn)


def membrana(nombre, R, RH, tramo, espejo, rotas=False, brasa=None):
    """Un tramo de ala de phantom (la raíz a la izquierda y el canto arriba, y del revés al final: en las caras de
    arriba y de abajo de un ala plana la fila de arriba de la textura cae en el canto de atrás).

    El brazo: el hueso del canto (dos filas) y la membrana debajo hasta el borde, en arco. La mano: un triángulo que
    acaba en punta, con las dos varillas de hueso que salen de la muñeca hasta el borde, festoneado en arcos entre
    varilla y varilla. La membrana, en tres bandas limpias que se apagan hacia el borde, con venas finas que salen de los
    huesos. 'rotas': agujeros de bordes limpios y el borde en jirones (el Oscuro). 'brasa': el borde ardiendo, como
    papel quemado, y las venas encendidas (el Explosivo)."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        xx = tw - 1 - xs if espejo else xs
        x, y = xx + 0.5, ys + 0.5
        u = x / tw
        hueso_m = ys < 2

        def linea(a, b, grueso):
            """Lo que está a menos de 'grueso' del segmento de a a b."""
            (ax, ay), (bx, by) = a, b
            dx, dy = bx - ax, by - ay
            k = np.clip(((x - ax) * dx + (y - ay) * dy) / max(1e-6, dx * dx + dy * dy), 0, 1)
            return np.hypot(x - ax - k * dx, y - ay - k * dy) < grueso

        if tramo == 'brazo':
            borde = th - 0.6 - 2.6 * np.sin(np.clip(u, 0, 1) * math.pi)
            dist = (y - 2.0) / np.maximum(borde - 2.0, 1.0)
            vena = np.zeros((th, tw), bool)
            for f in (0.3, 0.68):
                vena |= linea((f * tw, 2.0), (f * tw - 2.5, th - 1.0), 1.0)
        else:
            base_ = th - th * 0.86 * u
            puntas = (0.0, 0.4, 0.74, 1.0)
            borde = base_.copy()
            hondo = 0.24 if rotas else 0.15
            for a, b in zip(puntas, puntas[1:]):
                f = np.clip((u - a) / (b - a), 0, 1)
                borde = np.where((u >= a) & (u <= b), base_ - th * hondo * (1.0 - 0.6 * u) * np.sin(f * math.pi), borde)
            for t in puntas[1:3]:
                px, py = t * tw, th - th * 0.86 * t
                k = np.clip(((x - 0.5) * (px - 0.5) + (y - 0.5) * (py - 0.5)) / ((px - 0.5) ** 2 + (py - 0.5) ** 2), 0, 1)
                hueso_m = hueso_m | (np.hypot(x - 0.5 - k * (px - 0.5), y - 0.5 - k * (py - 0.5)) < 0.75)
            dist = np.clip(np.hypot(x, y) / np.maximum(np.hypot(x, borde), 1.0), 0, 1)
            vena = np.zeros((th, tw), bool)
            for t in (0.2, 0.57, 0.87):
                vena |= linea((0.5, 0.5), (t * tw, th - th * 0.86 * t), 1.0)
        memb = y <= borde + 0.3
        if rotas:
            # El borde en jirones: tiras que faltan, de dos píxeles de ancho y largo distinto.
            jiron = ((xx // 2 + s) % 3 == 0) & (y > borde - 1.0 - ((xx // 2 * 7 + s) % 3))
            memb &= ~jiron
            # Agujeros redondos de borde limpio, cerca del borde.
            # (a tres cuartos del camino del canto al borde).
            for (hx, hr) in ((0.3, 1.7), (0.62, 1.4), (0.82, 1.1)):
                cx = hx * tw
                cy = 0.72 * float(np.interp(cx, x[0], borde[0]))
                memb &= np.hypot(x - cx, y - cy) > hr
        hueso_m &= memb | (ys < 2)
        banda = np.floor(np.clip(dist, 0, 0.999) * 3)
        vena &= ~hueso_m
        v = 2.1 - banda * 0.45 - vena * 0.4
        rgb = np.where(hueso_m[..., None], L.color_continuo(RH, np.full((th, tw), 2.8) + (ys == 0) * 0.5),
                       L.color_continuo(R, v))
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(memb | hueso_m, 255, 0)
        emis = None
        if brasa is not None:
            rim = memb & ~hueso_m & (y > borde - 2.6)
            venas = memb & vena & (dist > 0.5)
            tex, emis = _encendido(tex, rim | venas, brasa, np.where(rim, 3.2, 1.9))
        tex = tex[::-1].copy()
        return tex, (None if emis is None else emis[::-1].copy())
    return B.fino(B.Pintor(nombre, fn), FINO)


def buche(nombre, R):
    """El buche de fuego del Explosivo: encendido entero, casi blanco en el centro y rojo en el borde, con tres
    costillas carbonizadas que lo cruzan."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        d = np.hypot((xs + 0.5) / tw - 0.5, (ys + 0.5) / th - 0.5)
        v = np.round((3.9 - d * 4.2) / 0.5) * 0.5
        tex = L._rgba(L.color_continuo(R, v))
        costilla = (xs % max(3, tw // 3)) == 1 if c in ('izq', 'der', 'abajo') else np.zeros((th, tw), bool)
        e = tex.copy()
        tex[costilla, :3] = (30, 22, 16)
        e[costilla] = 0
        return tex, e
    return B.fino(B.Pintor(nombre, fn), FINO)


# ======================================================================================================================
#  El phantom
# ======================================================================================================================
def phantom(m, piel_p, R, RH, h, cabeza_p, rotas=False, brasa=None):
    """El phantom de Minecraft, a su tamaño y mejor hecho: el cuerpo plano redondeado (6 x 3 x 10) con una fila de púas
    por el espinazo, la cabeza ancha redondeada (7 x 3 x 5) un poco agachada con la ceja de hueso, las alas de dos
    tramos (el brazo de 6 y la mano de 13, de 9 de cuerda) echadas hacia atrás y algo levantadas, con el canto de hueso
    y una uña en la muñeca, y la cola de dos tramos. R: la membrana; RH: los huesos del ala; h: las púas y la cola."""
    y = 6.0
    m.parte('cuerpo', None, (0, y, 0))
    redondo(m, 'cuerpo', (0, y, 0), (6, 3, 10), piel_p)
    # Las púas del espinazo: echadas hacia atrás y en punta, más altas en medio.
    for k, z in enumerate((3.6, 1.6, -0.4, -2.4, -4.2)):
        alto = 1.3 if k in (0, 4) else 2.0
        base = np.array((0.0, y + 1.3, z))
        medio = base + np.array((0.0, alto * 0.6, -alto * 0.35))
        m.viga('cuerpo', base, medio, 1.1, h, extra=0.3)
        m.viga('cuerpo', medio, medio + np.array((0.0, alto * 0.5, -alto * 0.45)), 0.6, h, extra=0.2)
    m.parte('cabeza', 'cuerpo', (0, y, 5.0), rot=(10, 0, 0))
    redondo(m, 'cabeza', (0, y - 0.2, 7.5), (7, 3, 5), cabeza_p)
    # La ceja de hueso: un arco sobre cada ojo.
    for lado in (1, -1):
        m.viga('cabeza', (lado * 0.8, y + 1.15, 9.9), (lado * 3.4, y + 1.45, 9.6), 0.6, h, ancho=0.7, extra=0.2)
    # La membrana, una sola cara (la de arriba): el render de las bestias no oculta las caras de atrás, así que se
    # ve también desde abajo, y con dos caras en el mismo plano se pisarían a trozos.
    for lado, ld in LADOS:
        espejo = lado < 0
        hombro = np.array((lado * 3.0, y + 1.0, 0.0))
        r0 = (0, lado * 10, lado * 6)
        n0 = m.parte(f'ala_{ld}0', 'cuerpo', tuple(hombro), rot=r0)
        M0 = T(*hombro) @ B.girar(r0)
        caras = {c: (membrana(f'ala_brazo_{ld}_{m.id}', R, RH, 'brazo', espejo, rotas, brasa)
                     if c == 'arriba' else None) for c in B.CARAS}
        x0 = 0.0 if lado > 0 else -6.0
        m._caja(n0, M0, x0, 0.0, -4.5, 6.0, 0.0, 9.0, None, caras)
        m._caja(n0, M0, x0, -0.4, 3.9, 6.0, 0.8, 0.8, h)
        # La uña de la muñeca: pequeña, asoma hacia delante.
        m._caja(n0, M0 @ T(lado * 6.0, 0.0, 4.6) @ B.girar((-10, 0, 0)), -0.3, -0.3, 0.0, 0.6, 0.6, 1.2, h)
        r1 = (0, lado * 10, lado * 4)
        M1 = M0 @ T(lado * 6.0, 0.0, 0.0) @ B.girar(r1)
        n1 = m.parte(f'ala_{ld}1', n0, tuple((M1 @ np.array((0.0, 0.0, 0.0, 1.0)))[:3]), rot=r1)
        caras = {c: (membrana(f'ala_mano_{ld}_{m.id}', R, RH, 'mano', espejo, rotas, brasa)
                     if c == 'arriba' else None) for c in B.CARAS}
        # Monta un poco sobre el brazo (sin la cuña vacía en la junta) y una pizca más alta (que no se pisen).
        x1 = -1.0 if lado > 0 else -13.0
        m._caja(n1, M1, x1, 0.1, -4.5, 14.0, 0.0, 9.0, None, caras)
        m._caja(n1, M1, x1, -0.3, 4.0, 13.0, 0.6, 0.6, h)
    m.parte('cola0', 'cuerpo', (0, y, -5.0))
    redondo(m, 'cola0', (0, y + 0.1, -8.0), (3, 2, 6), h)
    m.parte('cola1', 'cola0', (0, y, -11.0))
    m.caja('cola1', (0, y + 0.1, -14.0), (2, 1.4, 6), h)
    return y


def anims_phantom(m):
    """siempre: bate las alas (el brazo y, un poco después, la mano), la cola ondea y el cuerpo sube y baja con cada
    aletazo; lo que late, late y la llama se aviva; andar: lo mismo, más deprisa; ataque: se lanza en picado (el morro
    abajo y las alas recogidas atrás) y remonta; muerte: se ladea y cae dando vueltas mientras se encoge."""
    for nombre, largo, amp in (('siempre', 1.0, 1.0), ('andar', 0.6, 1.2)):
        a = m.anim(nombre, largo, bucle=True)
        for lado, ld in LADOS:
            a.onda(f'ala_{ld}0', 'r', 2, lado * 24 * amp, periodo=largo)
            a.onda(f'ala_{ld}1', 'r', 2, lado * 18 * amp, periodo=largo, fase=0.08)
        a.onda('cola0', 'r', 0, 6, periodo=largo, fase=0.25)
        a.onda('cola1', 'r', 0, 9, periodo=largo, fase=0.35)
        a.onda('cuerpo', 'm', 1, 0.7, periodo=largo, fase=0.5)
        if 'buche' in m.partes:
            a.onda('buche', 'e', 1, 0.08, periodo=largo / 2, base=1.0)
        if 'mecha' in m.partes:
            a.onda('mecha', 'e', 1, 0.25, periodo=largo / 3, base=1.0)
    at = m.anim('ataque', 0.6)
    at.rot('cuerpo', [(0, 0, 0, 0), (0.2, 28, 0, 0), (0.4, -12, 0, 0), (0.6, 0, 0, 0)])
    for lado, ld in LADOS:
        at.rot(f'ala_{ld}0', [(0, 0, 0, 0), (0.2, 0, lado * 30, lado * 30), (0.4, 0, 0, -lado * 10), (0.6, 0, 0, 0)])
    if 'garras' in m.partes:
        at.rot('garras', [(0, 0, 0, 0), (0.2, -40, 0, 0), (0.35, 20, 0, 0), (0.6, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (1.0, 20, 0, 160)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -6, 0)])
    d.esc('cuerpo', [(0, 1, 1, 1), (0.7, 0.8, 0.8, 0.8), (1.0, 0.1, 0.1, 0.1)])


def terminar(m, raiz, nombre_es, nombre_en, huevo, retrato, particulas=()):
    m.exportar(raiz)
    if CARPETA:
        m.hoja_vistas(os.path.join(CARPETA, f'{m.id}.png'),
                      poses=[('siempre', 0.25), ('andar', 0.3), ('ataque', 0.2), ('muerte', 0.8)])
    piel_h, contorno, dib = huevo
    B.huevo(m.id, piel_h, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    ojo, obj = retrato
    B.retrato(m, ojo=ojo, objetivo=obj, fov=34)
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)
    return m


# ======================================================================================================================
#  Los dos
# ======================================================================================================================
ANIL = rampa('07061a', '110e2e', '1c174a', '2c2470', '453a9c')
MEMBRANA_ANIL = rampa('090818', '14112e', '221c4c', '332a6e', '4c3f98')
MARFIL = rampa('4e4840', '7e7666', 'aea48c', 'd6ceb4', 'f0eada')
CARBON = rampa('0a0806', '17110c', '261c14', '382a1e', '4e3a2a')
CENIZA = rampa('2a2624', '4a4440', '6e6660', '948a82', 'bab0a6')
BRASA = rampa('5a1004', 'a8300a', 'f0700e', 'ffb42e', 'fff0a0')


def phantom_oscuro(raiz):
    """El Phantom Oscuro: añil, con los huesos de marfil y los ojos violeta pálido; las alas desgarradas, garras debajo
    del cuerpo para arrancarte lo que llevas, colmillos y la cola acabada en un garfio de dos puntas."""
    m = B.Modelo('phantom_oscuro', K=2, ancho=128)
    m.escala = 1.0
    h = hueso('hueso_oscuro', MARFIL)
    y = phantom(m, placas('piel_oscuro', ANIL), MEMBRANA_ANIL, MARFIL, h,
                cabeza_pint('cabeza_oscuro', ANIL, H('c8a0ff'), H('f4ecff')), rotas=True)
    # Los colmillos, que asoman por debajo de la boca.
    for lado in (1, -1):
        m.viga('cabeza', (lado * 1.4, y - 1.6, 9.7), (lado * 1.2, y - 2.7, 9.9), 0.6, h, extra=0.1)
    # Las garras: dos patas cortas bajo el cuerpo con las uñas curvas hacia delante.
    m.parte('garras', 'cuerpo', (0, y - 1.5, 1.5))
    for lado in (1, -1):
        p = np.array((lado * 1.7, y - 1.3, 1.5))
        for d, largo, w in (((0, -1.0, 0.25), 1.4, 1.2), ((0, -0.6, 1.0), 1.2, 0.9), ((0, 0.25, 1.0), 1.0, 0.6)):
            q = p + B._u(np.asarray(d, float)) * largo
            m.viga('garras', p, q, w, h, extra=0.3)
            p = q
    # El garfio de la cola: dos puntas abiertas.
    for lado in (1, -1):
        m.viga('cola1', (0, y + 0.1, -16.6), (lado * 1.5, y + 0.1, -19.0), 0.9, h, extra=0.3)
        m.viga('cola1', (lado * 1.5, y + 0.1, -19.0), (lado * 0.9, y + 0.1, -20.2), 0.6, h, extra=0.2)
    anims_phantom(m)

    def dib(px, filas, c):
        for f in range(3, 12):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('1c174a')
        for x, f in ((5, 6), (6, 6), (9, 6), (10, 6)):
            px[x, f] = c('c8a0ff')
        for x in range(4, 12, 2):
            px[x, 9] = c('d6ceb4')
    return terminar(m, raiz, 'Phantom Oscuro', 'Dark Phantom', (('453a9c', '1c174a', '07061a'), ('d6ceb4', '4e4840'), dib),
                    ((1.6, 1.5, 2.4), (0, 0.3, 0)),
                    particulas=(('humo', bc.esquirla((40, 34, 80))), ('hueso', bc.esquirla((214, 206, 180)))))


def phantom_explosivo(raiz):
    """El Phantom Explosivo: carbonizado, con grietas de brasa; las alas de ceniza con el borde ardiendo, el buche de
    fuego bajo la panza y la cola acabada en una mecha encendida."""
    m = B.Modelo('phantom_explosivo', K=2, ancho=128)
    m.escala = 1.0
    h = hueso('hueso_explosivo', CENIZA, base=2.2)
    y = phantom(m, placas('piel_explosivo', CARBON, base=2.3, brasa=BRASA), CARBON, CENIZA, h,
                cabeza_pint('cabeza_explosivo', CARBON, H('ffb42e'), H('fff0a0'), boca=BRASA), brasa=BRASA)
    # El buche de fuego, que asoma bajo la panza y late.
    m.parte('buche', 'cuerpo', (0, y - 1.6, -0.5))
    redondo(m, 'buche', (0, y - 1.7, -0.5), (4.4, 2.4, 5.6), buche('buche_explosivo', BRASA))
    # La mecha de la cola: un cordón carbonizado y la punta encendida con su llama.
    m.viga('cola1', (0, y + 0.1, -16.6), (0, y + 0.8, -18.6), 0.7, h, extra=0.2)
    m.parte('mecha', 'cola1', (0, y + 0.9, -18.8))
    m.caja('mecha', (0, y + 0.9, -18.8), (1.0, 1.0, 1.0), buche('ascua_mecha', BRASA))
    fuego = llama('llama_mecha', BRASA)
    for giro in (45, 135):
        m.hoja('mecha', (0, y + 2.4, -18.8), 1.8, 2.4, fuego, rot=(0, giro, 0))
    anims_phantom(m)

    def dib(px, filas, c):
        for f in range(3, 12):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('261c14')
        for x, f in ((5, 6), (6, 6), (9, 6), (10, 6), (7, 9), (8, 9), (6, 10), (9, 10)):
            px[x, f] = c('ffb42e')
    return terminar(m, raiz, 'Phantom Explosivo', 'Explosive Phantom',
                    (('4e3a2a', '261c14', '0a0806'), ('f0700e', '5a1004'), dib),
                    ((1.6, 1.4, 2.4), (0, 0.2, 0)),
                    particulas=(('chispa', bc.chispa((255, 180, 46))), ('humo', bc.esquirla((70, 62, 56)))))


MOBS = {'phantom_oscuro': phantom_oscuro, 'phantom_explosivo': phantom_explosivo}


def main():
    global CARPETA
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    CARPETA = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] not in ('-', '') else None
    if CARPETA:
        os.makedirs(CARPETA, exist_ok=True)
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(MOBS)
    # El píxel de Minecraft (16 por bloque): van a escala 1, así que es de 1 píxel del modelo.
    B.TEXEL = 1.0
    for p in pedidos:
        MOBS[p](raiz)
    B.TEXEL = None


if __name__ == '__main__':
    main()

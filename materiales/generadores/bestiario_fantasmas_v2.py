"""
Los fantasmas, recreados de sus ilustraciones (19-10-2026). Juan: «solo hagamos los 4 fantasmas, fantasma farola y la
parca… debes de hacer primero recrear los fantasmas de las imágenes y luego mejorarlas»; y, al ver la primera
recreación: «se parecen pero no como las ilustraciones, más que todo las caras, las manos y su cola de fantasma… te
dije que le pongas más píxeles en estos casos»; y después: «las manos de los fantasmas no son igual».

Por eso las caras no se dibujan a ojo: están calcadas de las ilustraciones (cada cara enderezada y pasada a píxeles de
32 por bloque, en fantasmas_mapas.py), y las colas y las manos se pintan también a 32 por bloque (B.fino). El resto, al
píxel de Minecraft. Las proporciones salen de medir los dibujos.

Los cuatro llevan el mismo cuerpo y solo cambian el color y la cara (Juan, 19-10-2026: «los brazos tienen que ser
igual y su falda igual entre todos, así lo que cambiaría es el color y la cara»). Los brazos y la cola son los que Juan
marcó sobre el Blanco: los brazos en «¡bu!» de su dibujo y, como vuelan, una cola en vez de piernas.

  espectro_blanco    (Fantasma Blanco, D4)   blanco, con la máscara triste de su dibujo
  espectro_negro     (Fantasma Negro, D4)    de carbón, con la cara negra y el humo de los lados de su dibujo
  espectro_amarillo  (Fantasma Amarillo, D4) amarillo que baja al naranja, con la cara y los lados de su dibujo
  espectro_rojo      (los fantas rojos, D3)  rojo, con la cara de su sábana

La Parca y el Farolero no se hacen (Juan, 19-10-2026: «solo los 4 fantasmas»).

Se probó a mejorarlos (19-10-2026): primero las caras limpias con pupilas de neón («sus caras déjalas como antes»),
luego una pieza por fantasma (alas de hielo, la jaula del corazón, la corona de llamas, los grilletes) y después un
muestrario de tres ideas por fantasma. Ninguna le gustó: «mejor déjalo como está». Se quedan como la recreación, con las
texturas del cuerpo limpias (sin motas).

Uso: python bestiario_fantasmas_v2.py <raíz> [carpeta de las vistas] [ids separados por comas]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
import bestiario_limpio as L
import fantasmas_mapas as FM
from bestiario import rampa
from bestiario_hormigas import _azar1, chispa, esquirla, llama, nube

CARPETA = None
LADOS = ((1, 'i'), (-1, 'd'))          # +X es la izquierda del mob (mira hacia +Z)
FINO = 0.5                             # el píxel fino: 32 por bloque


def terminar(m, raiz, nombre_es, nombre_en, huevo, retrato, particulas=(), poses=None):
    m.exportar(raiz)
    if CARPETA:
        m.hoja_vistas(os.path.join(CARPETA, f'{m.id}.png'),
                      poses=poses or [('siempre', 0.5), ('andar', 0.3), ('ataque', 0.2), ('muerte', 0.8)])
    piel, contorno, dib = huevo
    B.huevo(m.id, piel, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    ojo, obj = retrato
    B.retrato(m, ojo=ojo, objetivo=obj, fov=34)
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)
    return m


def H(h):
    return np.array((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), float)


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def a_tam(mp, th, tw):
    """El mapa (lista de cadenas) a th x tw, por el vecino más cercano."""
    a = np.array([list(f) for f in mp])
    ys = np.minimum((np.arange(th) * a.shape[0] / th).astype(int), a.shape[0] - 1)
    xs = np.minimum((np.arange(tw) * a.shape[1] / tw).astype(int), a.shape[1] - 1)
    return a[np.ix_(ys, xs)]


def con_mapa(nombre, fondo, mapas, colores, emis='', transparente='', fino=True, jirones=0):
    """Un pintor que pinta el 'fondo' (fn(tw, th, cara, s) -> rgb) y, en las caras de 'mapas' ({cara: mapa}), encima
    cada letra con su color (las letras de 'emis' brillan; las de 'transparente' quedan vacías). Las letras que no
    están en 'colores' dejan el fondo."""
    def fn(tw, th, c, s):
        rgb = fondo(tw, th, c, s)
        tex = L._rgba(rgb)
        brilla = np.zeros((th, tw), bool)
        if c in mapas and mapas[c] is not None:
            m = a_tam(mapas[c], th, tw)
            if c in ('der',):
                m = m[:, ::-1]
            a = _azar1(*L._malla(tw, th), s + 31)
            for letra, col in colores.items():
                sel = m == letra
                if sel.any():
                    v = np.clip(np.asarray(col, float)[None, :] * (0.97 + 0.06 * a[sel][:, None]), 0, 255)
                    tex[sel, :3] = np.round(v)
                    if letra in emis:
                        brilla |= sel
            for letra in transparente:
                tex[m == letra, 3] = 0
        if jirones and c not in ('arriba', 'abajo'):
            xs, ys = L._malla(tw, th)
            col = _azar1(xs // 2, np.zeros_like(xs), s + 7)
            corte = np.floor(col * jirones + (xs % 2) * 1.5).astype(int)
            tex[ys >= th - corte, 3] = 0
        if brilla.any():
            e = np.zeros_like(tex)
            e[brilla] = tex[brilla]
            return tex, e
        return tex, None
    p = B.Pintor(nombre, fn)
    return B.fino(p, FINO) if fino else p


def degradado(R, base=2.2, luz=1.0, franja=(0.0, 1.0), escalon=0.35, canto=0.45):
    """El fondo de un material, limpio (sin motas): el tono que corre por la rampa, más claro arriba ('franja', la parte
    del alto de la pieza que es esta caja), en escalones de 'escalon' (bandas, como el sombreado de Minecraft), y el
    canto de arriba de cada cara de los lados 'canto' más claro."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        f0, f1 = franja
        if c == 'arriba':
            t = np.full((th, tw), f0 - 0.15)
        elif c == 'abajo':
            t = np.full((th, tw), f1 + 0.1)
        else:
            t = f0 + (ys + 0.5) / th * (f1 - f0)
        v = base + luz * (0.5 - t)
        if escalon:
            v = np.round(v / escalon) * escalon
        if c not in ('arriba', 'abajo'):
            v = v + (ys == 0) * canto
        return L.color_continuo(R, v)
    return fn


def _vecinos(mk):
    """Cuántos de los 8 vecinos de cada píxel están en la máscara."""
    p = np.pad(mk, 1)
    h, w = mk.shape
    return sum(p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w].astype(int)
               for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)


def _manchas(mk):
    """Las manchas de la máscara (de cuatro vecinos), numeradas desde 1."""
    lab = np.zeros(mk.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(mk)):
        if lab[y, x]:
            continue
        n += 1
        lab[y, x] = n
        pila = [(y, x)]
        while pila:
            cy, cx = pila.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = cy + dy, cx + dx
                if 0 <= yy < mk.shape[0] and 0 <= xx < mk.shape[1] and mk[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    pila.append((yy, xx))
    return lab, n


def _moda(a, sel):
    """Cambia cada píxel de 'sel' por la letra que más se repite a su alrededor fuera de 'sel'."""
    out = a.copy()
    h, w = a.shape
    for y, x in zip(*np.nonzero(sel)):
        cuenta = {}
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w and not sel[yy, xx]:
                    cuenta[a[yy, xx]] = cuenta.get(a[yy, xx], 0) + 1
        if cuenta:
            out[y, x] = max(cuenta, key=cuenta.get)
    return out


def limpiar(mapa, oscuras='k', quitar='', alisar=True):
    """Un calco, limpio: lo oscuro (las letras de 'oscuras', que pasan a ser 'k') con el borde alisado, sin manchas
    sueltas ni agujeros pequeños; y en el fondo, cada píxel suelto (sin otro igual al lado) y las letras de 'quitar'
    cambiados por lo que tienen alrededor. Las manchas quedan grandes y de borde limpio. Sin 'alisar', el borde de lo
    oscuro se queda como está (para no perder los trazos finos, como las arrugas del entrecejo del Blanco)."""
    a = np.array([list(f) for f in mapa])
    d = np.isin(a, list(oscuras))
    for _ in range(2 if alisar else 0):
        d = (_vecinos(d) + d) >= 5
    for mk in (d, ~d):
        lab, n = _manchas(mk)
        for i in range(1, n + 1):
            if (lab == i).sum() < 4:
                d[lab == i] = not d[lab == i][0]
    igual = np.zeros(a.shape, int)
    p = np.pad(a, 1, constant_values='#')
    h, w = a.shape
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                igual += p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w] == a
    malo = ~d & (np.isin(a, list(oscuras + quitar)) | (igual == 0))
    a = _moda(np.where(d, 'k', a), malo | d)
    a[d] = 'k'
    return [''.join(f) for f in a]


def picos_capa(nombre, R, colgando=True, banda=2, largo=5, paso=4, v0=2.6):
    """Los picos en una 2.ª capa, como los dientes de las Fauces (bestiario_plantas.dientes_capa): la caja algo mayor
    que la pieza, transparente salvo una banda que monta sobre ella (las 'banda' filas, un tono más oscura) y una fila de
    picos triangulares de largo distinto, macizos, claros a la izquierda y en sombra a la derecha, con la punta más clara.
    'colgando': los picos cuelgan (la falda); si no, se levantan (el hombro). A 32 por bloque, para que salgan en punta.
    En las cuatro caras de los lados; arriba y abajo, nada."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if cara in ('arriba', 'abajo'):
            return tex, None
        y = ys if colgando else (th - 1 - ys)           # filas desde la banda hacia la punta
        r = y - banda                                   # fila dentro del pico (0, la raíz)
        rng = np.random.default_rng(int(s) * 31 + tw * 7 + th + len(cara))
        n = max(1, tw // paso)
        inicio = (tw - n * paso) // 2
        k = np.clip((xs - inicio) // paso, 0, n - 1)
        u = (xs - inicio) - k * paso                    # columna dentro del hueco de cada pico (0..paso-1)
        L_ = rng.integers(max(2, largo - 2), largo + 1, n)[k]
        c = (paso - 2) / 2.0                            # el centro del pico (la última columna es el hueco)
        ancho = (paso - 1) / 2.0 * (1 - r / np.maximum(L_, 1))
        dentro = (r >= 0) & (r < L_) & (np.abs(u - c) <= ancho + 0.01) & (u <= paso - 2)
        en_banda = y < banda
        v = v0 + (u < c) * 0.5 - (u > c) * 0.5 + (r >= L_ - 2) * 0.5 - (r == 0) * 0.4 - en_banda * 0.7
        tex = L._rgba(L.color_continuo(R, v))
        tex[..., 3] = np.where(dentro | en_banda, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


def macizo(nombre, R, **kw):
    f = degradado(R, **kw)
    return B.fino(B.Pintor(nombre, lambda tw, th, c, s: (L._rgba(f(tw, th, c, s)), None)), FINO)


def anims_fantasma(m):
    """siempre: flota (sube y baja), la cabeza se mece y lo de abajo ondea; andar: se inclina hacia delante y lo de abajo
    queda atrás; ataque: se echa atrás y se lanza (con los brazos, si los tiene); muerte: se deshace bajando y
    encogiéndose mientras gira."""
    s = m.anim('siempre', 3.0, bucle=True)
    s.onda('cuerpo', 'm', 1, 1.2, periodo=3.0)
    s.onda('cabeza', 'r', 2, 3, periodo=3.0, fase=0.25)
    for k, (lado, ld) in enumerate(LADOS):
        for n in (f'pierna_{ld}', f'brazo_{ld}', f'ala_{ld}', f'llama_{ld}'):
            if n in m.partes:
                s.onda(n, 'r', 0, 6, periodo=1.5, fase=0.5 * k)
    for n in ('falda', 'cola'):
        if n in m.partes:
            s.onda(n, 'r', 0, 6, periodo=1.5)
            s.onda(n, 'r', 2, 4, periodo=3.0, fase=0.4)
    a = m.anim('andar', 1.0, bucle=True)
    a.onda('cuerpo', 'r', 0, 2, periodo=1.0, base=10)
    for k, (lado, ld) in enumerate(LADOS):
        if f'pierna_{ld}' in m.partes:
            a.onda(f'pierna_{ld}', 'r', 0, 12, periodo=1.0, fase=0.5 * k, base=-14)
    for n in ('falda', 'cola'):
        if n in m.partes:
            a.onda(n, 'r', 0, 5, periodo=0.5, base=-16)
    at = m.anim('ataque', 0.6)
    at.rot('cuerpo', [(0, 0, 0, 0), (0.18, -8, 0, 0), (0.3, 10, 0, 0), (0.6, 0, 0, 0)])
    at.mov('cuerpo', [(0, 0, 0, 0), (0.18, 0, 1, -2), (0.3, 0, -1, 4), (0.6, 0, 0, 0)])
    # Los brazos se echan atrás y se lanzan hacia delante (el «¡bu!») y vuelven.
    for lado, ld in LADOS:
        if f'brazo_{ld}' in m.partes:
            at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.18, 25, 0, lado * 10), (0.3, -40, 0, -lado * 10), (0.6, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -10, 0)])
    d.rot('cuerpo', [(0, 0, 0, 0), (1.0, 0, 200, 0)])
    d.esc('cuerpo', [(0, 1, 1, 1), (0.6, 0.8, 0.8, 0.8), (1.0, 0.1, 0.1, 0.1)])


# ======================================================================================================================
#  El cuerpo común de los cuatro fantasmas (Juan, 19-10-2026: «los brazos tienen que ser igual y su falda igual entre
#  todos, así lo que cambiaría es el color y la cara»; y, dibujando encima del Blanco: «sus manos debería ser así y su
#  cola así, porque estos fantasmas van a volar»; y luego: «el brazo tiene 2 partes, uno que es como un hombro y luego
#  la mano larga; el hombro tiene que ser como una 2.ª capa, y luego su mano normal con el color del fantasma, no tiene
#  que ser transparente; lo mismo con su cuerpo, que sea una 2.ª capa su falda»; y al verlo: «la 2.ª capa me refiero a
#  como los dientes del mob de plantas, así deben ser sus hombros… quita ese transparente»). La cabeza cúbica con su
#  tapa; debajo, el cuerpo macizo de su color con la falda de picos que cuelga; y los brazos, con los picos del hombro.
# ======================================================================================================================
BLANCO = rampa('8e96a2', 'b4bcc6', 'd4dae2', 'eaeef3', 'fbfcfd')
CARBON = rampa('121216', '1e1e24', '2a2a31', '383840', '48484f')
NEGRO_L = rampa('080a10', '10141e', '1a2030', '262e42', '343e56')
AMARILLO = rampa('b04a08', 'd8680c', 'f08c14', 'fab820', 'ffd838')
NARANJA = rampa('5a2406', '8a3a0a', 'b8540e', 'd86c12', 'ec8a1c')
ROJO = rampa('5a0622', '8a0a34', 'b81242', 'd81a4a', 'f84a28')
GRANATE = rampa('1a0208', '3a0614', '5a0a22', '7a1030', '9a1a3e')
HIELO = rampa('6e9cc0', '92c2e0', 'b8e0f4', 'dcf2fc', 'ffffff')
COLORES_A = {'a': H('ffd838'), 'b': H('fab820'), 'o': H('f08c14'), 'n': H('d8680c'), 'r': H('b04a08'),
             'g': H('5a2406'), 'k': H('140604'), 'y': H('ffe060')}
COLORES_R = {'a': H('f84a28'), 'b': H('ec2a30'), 'c': H('d81a4a'), 'd': H('b81242'), 'e': H('8a0a34'),
             'f': H('5a0622'), 'k': H('241418')}
# La cara del Rojo: la de su sábana (lo de arriba del calco, de la franja naranja a la boca).
CARA_ROJO = FM.FRENTE_ROJO[:31]


def fantasma(m, R, cara, lados, colores, llama, emis='', base=2.3, piel=None, picos=None):
    """El cuerpo común. R: la rampa de la cabeza (y del cuerpo, los brazos y los hombros); cara y lados: los mapas
    calcados; llama: la rampa de los picos de la falda; piel: el mapa calcado con el que siguen el cuerpo y los brazos
    (lo de más abajo de su dibujo), para que tengan la misma textura que la cabeza; picos: la rampa de los picos del
    hombro y de la falda (si no, los del hombro van del color de la cabeza y los de la falda, de 'llama')."""
    y_cab = 15.0
    W, Hc = 10, 11
    m.parte('cuerpo', None, (0, 16, 0))
    m.parte('cabeza', 'cuerpo', (0, y_cab, 0))
    fondo = degradado(R, base=base, luz=0.9, franja=(0.0, 0.9))
    pint = con_mapa(f'cabeza_{m.id}', fondo, {'frente': cara, 'izq': lados, 'der': lados, 'atras': lados}, colores,
                    emis=emis)
    m.caja('cabeza', (0, y_cab + Hc / 2, 0), (W, Hc, W), pint)
    m.caja('cabeza', (0, y_cab + Hc + 0.5, 0), (W - 2, 1, W - 2), macizo(f'tapa_{m.id}', R, base=base + 0.6, luz=0.3))
    # El cuerpo (vuelan: nada de piernas), macizo y del color de la cabeza, que sigue oscureciéndose hacia abajo; y la
    # falda, en una 2.ª capa como los dientes de las Fauces: una banda alrededor de lo bajo del cuerpo y los picos que
    # cuelgan de ella.
    n = m.parte('cola', 'cuerpo', (0, y_cab, 0))
    lados4 = ('frente', 'izq', 'der', 'atras')
    m.caja(n, (0, y_cab - 3.0, 0), (W, 6, W),
           con_mapa(f'cola_{m.id}', degradado(R, base=base, luz=0.9, franja=(0.8, 1.0)),
                    {c: piel for c in lados4} if piel else {}, colores, emis=emis), caras={'arriba': None})
    m.caja(n, (0, y_cab - 7.0, 0), (W + 0.5, 4, W + 0.5),
           picos_capa(f'falda_{m.id}', llama if picos is None else picos, colgando=True, banda=2, largo=6, paso=5))
    # Los brazos, como los marcó Juan: el brazo largo, macizo y del color del fantasma, que baja desde junto a lo bajo de
    # la cabeza hacia fuera; y arriba, el hombro, en una 2.ª capa como los dientes de las Fauces: los picos que se
    # levantan de la punta del brazo. Giran desde el hombro.
    piel_brazo = [f[1:1 + len(f) // 2] for f in piel] if piel else None      # sin el borde del dibujo
    brazo = con_mapa(f'brazo_{m.id}', degradado(R, base=base, luz=0.9, franja=(0.5, 0.95)),
                     {c: piel_brazo for c in lados4} if piel else {}, colores, emis=emis)
    hombro = picos_capa(f'hombro_{m.id}', R if picos is None else picos, colgando=False, banda=2, largo=6, paso=3, v0=base + 0.3)
    for lado, ld in LADOS:
        abajo = np.array((lado * 12.2, y_cab - 5.5, 3.0))
        arriba = np.array((lado * 7.6, y_cab + 2.2, 3.0))
        n = m.parte(f'brazo_{ld}', 'cuerpo', tuple(arriba))
        eje = B._u(arriba - abajo)
        m.viga(n, abajo, arriba, 3.5, brazo, ancho=5)
        m.viga(n, arriba - eje * 1.0, arriba + eje * 3.0, 4, hombro, ancho=5.5)
    m.mirar(('cabeza', 0.8))
    anims_fantasma(m)


def espectro_blanco(raiz):
    """El Fantasma Blanco: el cuerpo común, blanco, con la máscara triste calcada de su dibujo."""
    m = B.Modelo('espectro_blanco', K=2, ancho=128)
    m.escala = 1.0
    fantasma(m, BLANCO, FM.CARA_BLANCO, None, {'k': H('0c0c10'), 'g': H('4c505a')}, BLANCO, base=2.6, picos=HIELO)

    def dib(px, filas, c):
        for f in range(3, 10):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('fbfcfd')
        for x, f in ((6, 4), (5, 5), (6, 5), (9, 4), (9, 5), (10, 5), (7, 7), (8, 7), (6, 8), (9, 8)):
            px[x, f] = c('0c0c10')
    return terminar(m, raiz, 'Espectro Blanco', 'White Wraith', (('fbfcfd', 'd4dae2', 'b4bcc6'), ('5a6270', '30363e'), dib),
                    ((1.4, 1.6, 2.3), (0, 1.0, 0)),
                    particulas=(('alma', nube((220, 230, 240))), ('escarcha', chispa((200, 220, 240)))))


def espectro_negro(raiz):
    """El Fantasma Negro: el cuerpo común, de carbón, con la cara negra y el humo de los lados calcados de su dibujo."""
    m = B.Modelo('espectro_negro', K=2, ancho=128)
    m.escala = 1.0
    fantasma(m, CARBON, FM.CARA_NEGRO, FM.LADO_NEGRO,
             {'k': H('040406'), 'g': H('15151a'), 'c': H('4c5568'), 'h': H('707a8e')}, NEGRO_L, base=2.0)

    def dib(px, filas, c):
        for f in range(2, 10):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('383840')
        for x, f in ((5, 4), (6, 4), (5, 5), (9, 4), (10, 4), (10, 5), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (10, 7)):
            px[x, f] = c('040406')
        for f in range(10, 14):
            for x in (5, 6, 9, 10):
                px[x, f] = c('1a2030')
    return terminar(m, raiz, 'Espectro Negro', 'Black Wraith', (('48484f', '2a2a31', '121216'), ('000000', '000000'), dib),
                    ((1.4, 1.6, 2.3), (0, 1.0, 0)),
                    particulas=(('humo', nube((60, 66, 80))), ('corazon', chispa((196, 26, 20)))))


def espectro_amarillo(raiz):
    """El Fantasma Amarillo: el cuerpo común, amarillo que baja en llamas al naranja, con la cara y los lados calcados
    de su dibujo."""
    m = B.Modelo('espectro_amarillo', K=2, ancho=128)
    m.escala = 1.0
    fantasma(m, AMARILLO, FM.CARA_AMARILLO, FM.LADO_AMARILLO, COLORES_A, NARANJA, emis='y',
             piel=limpiar(FM.LADO_AMARILLO[12:], '', quitar='k'))

    def dib(px, filas, c):
        for f in range(2, 10):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c('ffd838' if f < 4 else 'f08c14')
        for x, f in ((5, 4), (6, 4), (9, 4), (10, 4), (7, 6), (8, 6), (6, 7), (7, 7), (8, 7), (9, 7), (7, 8), (8, 8)):
            px[x, f] = c('140604')
        for f in range(10, 14):
            for x in (5, 6, 9, 10):
                px[x, f] = c('b8540e')
    return terminar(m, raiz, 'Espectro Amarillo', 'Yellow Wraith', (('ffd838', 'f08c14', 'b04a08'), ('5a2406', '2a1002'), dib),
                    ((1.4, 1.6, 2.3), (0, 1.0, 0)),
                    particulas=(('chispa', chispa((252, 196, 28))), ('alma', nube((240, 160, 60)))))


def espectro_rojo(raiz):
    """El Fantasma Rojo: el cuerpo común, rojo (del naranja de arriba al granate), con la cara de su sábana calcada."""
    m = B.Modelo('espectro_rojo', K=2, ancho=128)
    m.escala = 1.0
    fantasma(m, ROJO, CARA_ROJO, None, COLORES_R, GRANATE, base=2.6,
             piel=limpiar(FM.FRENTE_ROJO[30:42], '', quitar='k'))

    def dib(px, filas, c):
        for f in range(2, 14):
            a_, b = filas[f]
            for x in range(a_ + 1, b):
                px[x, f] = c('f84a28' if f < 5 else 'd81a4a' if f < 10 else '8a0a34')
        for x, f in ((5, 5), (5, 6), (10, 5), (10, 6), (7, 9), (8, 9), (6, 10), (9, 10)):
            px[x, f] = c('241418')
    return terminar(m, raiz, 'Espectro Rojo', 'Red Wraith', (('f84a28', 'd81a4a', '8a0a34'), ('3a0614', '1a0208'), dib),
                    ((1.4, 1.6, 2.3), (0, 1.0, 0)),
                    particulas=(('brasa', chispa((248, 80, 62))), ('ceniza', esquirla((90, 8, 22)))))


MOBS = {'espectro_blanco': espectro_blanco, 'espectro_negro': espectro_negro, 'espectro_amarillo': espectro_amarillo,
        'espectro_rojo': espectro_rojo}


def main():
    global CARPETA
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    CARPETA = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
    if CARPETA:
        os.makedirs(CARPETA, exist_ok=True)
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(MOBS)
    B.TEXEL = 1.0
    for p in pedidos:
        MOBS[p](raiz)
    B.TEXEL = None


if __name__ == '__main__':
    main()

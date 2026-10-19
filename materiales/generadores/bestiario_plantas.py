"""
Las plantas del bestiario, rehechas (19-10-2026): las del DEDsafío 2 (las Carnivenus de tres colores, la Tramplanta y la
Piña Malibú) y el Zombie Planta del DEDsafío 4, como en sus fichas de la DEDciclopedia pero mejor, y al píxel de
Minecraft (materiales/CONTINUAR.md, regla 1): escala 1 y B.TEXEL = 1, todas las piezas de píxeles enteros y cada
detalle de la textura, un píxel (un estoma, un diente, una escama).

  fauces_verde/carmin/escarcha   el tallo de bloques que sale del suelo, sube y se dobla hacia delante (en J, como el
                                 de su ficha), con sus nudos y dos hojas, y la cabeza de dos mandíbulas cuadradas, rosa
                                 por dentro y con los dientes blancos en el borde. La verde babea veneno, la carmín
                                 tiene espinas en el tallo y la boca encendida, la de escarcha lleva carámbanos y los
                                 dientes de hielo
  trampa                         dos lóbulos de pie unidos por la bisagra, con las pestañas largas en el borde; escondida
                                 se tumba abierta en el suelo, del verde de la hierba de su bioma
  pina                           una piña chica (las escamas en rombo, cada una con su ojo) con la corona de hojas en
                                 punta, dos patas cortas y dos puños de hoja: sin cara, como la de su ficha
  zombi_planta                   un zombi (la anatomía de siempre) comido por la planta: la hiedra y el musgo en 2.ª
                                 capa, una flor que le brota del ojo, los pies que echan raíz y un arbolito a la espalda

Lo que hacen (las mecánicas, los sonidos y los efectos) no cambia: está en Plantas.java.

Uso: python bestiario_plantas.py <raíz> [carpeta de las vistas] [ids separados por comas]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import rampa
from bestiario_hormigas import _azar1, _v, encender, redondo, rotar

CARPETA = None
LADOS = ((1, 'i'), (-1, 'd'))


def terminar(m, raiz, nombre_es, nombre_en, huevo, retrato, particulas=(), poses=None):
    m.exportar(raiz)
    if CARPETA:
        m.hoja_vistas(os.path.join(CARPETA, f'{m.id}.png'),
                      poses=poses or [('siempre', 0.5), ('ataque', 0.2), ('ataque', 0.35), ('muerte', 1.0)])
    piel, contorno, dib = huevo
    B.huevo(m.id, piel, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    ojo, obj = retrato
    B.retrato(m, ojo=ojo, objetivo=obj, fov=34)
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)
    return m


# ======================================================================================================================
#  Las partículas
# ======================================================================================================================
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


def copo(n=8):
    """Un copo de escarcha: una estrella de seis puntas, blanca con el borde celeste; tres tamaños."""
    cuadros = []
    for k in range(3):
        def f(x, y, k=k):
            u, v = x - 0.5, y - 0.5
            rr = np.hypot(u, v)
            ang = np.arctan2(v, u)
            brazo = (np.abs(np.sin(ang * 3)) < 0.28 + 0.1 * k) & (rr < 0.46 - k * 0.1)
            centro = rr < 0.12
            a = (brazo | centro) * 255
            return (np.where(centro, 255, 200), np.where(centro, 255, 240), 255, a)
        cuadros.append(B.sprite(n, f))
    return cuadros


# ======================================================================================================================
#  Los pintores de las plantas, al píxel de Minecraft
# ======================================================================================================================
def tallo(nombre, R, base=2.0, estomas=0.05, nudo=False):
    """La piel del tallo: el tono que corre (más claro arriba), las fibras a lo largo (una columna de cada tres, un
    tono más clara) y estomas de un píxel (más oscuros); con 'nudo', la fila de abajo es el anillo del nudo."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        v = _v(tw, th, cara, s, base, 0.8)
        if cara not in ('arriba', 'abajo'):
            v = v + ((xs % 3) == 1) * 0.35
            if nudo:
                v = np.where(ys == th - 1, v - 0.9, v)
        v = v - (a < estomas) * 0.7
        return L._rgba(L.color_continuo(R, v)), None
    return B.Pintor(nombre, fn)


def hoja_plana(nombre, R, ancho_base=1.0):
    """Una hoja en punta en una lámina (lo de fuera, transparente): el nervio claro en medio, las venas en espiga (un
    píxel más claro cada dos filas) y el borde un tono más oscuro."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        u = (xs + 0.5) / tw - 0.5
        v = (ys + 0.5) / th
        perfil = 0.5 * ancho_base * np.sin(np.clip(v, 0, 1) * math.pi) ** 0.7
        dentro = np.abs(u) < perfil + 0.02
        cx = (tw - 1) / 2
        val = np.full((th, tw), 2.0) + (xs < cx) * 0.3
        val = np.where(np.abs(xs - cx) < 0.6, 3.4, val)
        val = np.where(((ys + np.abs(xs - cx).astype(int)) % 2 == 0) & (np.abs(xs - cx) > 0.6), val + 0.3, val)
        val = np.where(np.abs(u) > perfil - 1.0 / tw, val - 0.8, val)
        tex = L._rgba(L.color_continuo(R, val))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


def boca(nombre, R, brilla=None):
    """Por dentro de la boca: la carne (más clara en el centro, más oscura hacia el canto) con los pliegues a lo largo
    (un píxel más oscuro de cada tres); con 'brilla' (una rampa), el centro encendido."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        d = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        v = 1.6 + np.minimum(d, 3) * 0.55 - ((xs % 3) == 1) * 0.4
        tex = L._rgba(L.color_continuo(R, v))
        if brilla is None:
            return tex, None
        a = np.clip((d - 1) / 2.0, 0, 1)
        return encender(tex, a, brilla, 2.0 + a)
    return B.Pintor(nombre, fn)


def diente(nombre, R):
    """Un diente (una caja de 1 x 2 x 1): blanco, la punta más clara y la raíz un tono más oscura."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), 3.0) - (ys == 0) * 0.8 + (cara == 'frente') * 0.4
        return L._rgba(L.color_continuo(R, v)), None
    return B.Pintor(nombre, fn)


def luz_plana(nombre, R, v=3.0):
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        tex = L._rgba(L.color_continuo(R, np.full((th, tw), v) - ys * 0.3))
        return tex, tex.copy()
    return B.Pintor(nombre, fn, pleno=True)


# ======================================================================================================================
#  Las Fauces (Carnivenus)
# ======================================================================================================================
TIERRA = rampa('24160c', '382412', '503420', '6c4a2c', '8a6640')
CARNE = rampa('4a1018', '7a2232', 'b0485a', 'e07a8a', 'ffb4be')
DIENTE_B = rampa('6a6250', 'a89c80', 'd8ccb0', 'f2ead8', 'fffcf2')
COLORES = {
    # piel, hojas, dientes, (nombre, en), huevo (claro, medio, oscuro), contorno
    'verde': (rampa('0e3006', '1c5a0c', '2e8a16', '4cb826', '7ee048'), rampa('0a2a06', '14480c', '226a16', '3a9022', '5cb836'),
              DIENTE_B, ('Verde', 'Green'), ('7ee048', '4cb826', '2e8a16'), ('0e3006', '061804')),
    'carmin': (rampa('2a0406', '58080e', '8c141c', 'c02a30', 'e8585a'), rampa('2a0a06', '4a140a', '6e2010', '963018', 'be4824'),
               DIENTE_B, ('Carmín', 'Crimson'), ('e8585a', 'c02a30', '8c141c'), ('2a0406', '140202')),
    'escarcha': (rampa('063a3a', '0c6462', '169490', '30c4bc', '7ef0e6'), rampa('0a2e34', '124a54', '1c6a76', '2c8e9a', '4ab4c0'),
                 rampa('3a6a7a', '7ab0c0', 'b0e4ee', 'dcf8fc', 'ffffff'), ('de Escarcha', 'Frost'),
                 ('7ef0e6', '30c4bc', '169490'), ('063a3a', '021c1c')),
}
VENENO = rampa('1a4a04', '3a8a0a', '7ad21a', 'b6ff4a', 'eaffb0')
ASCUA = rampa('6a1604', 'c04a0a', 'f08a1a', 'ffc84a', 'fff2b0')
HIELO = rampa('5a9ab0', '8ac8dc', 'b8ecf6', 'e0fcff', 'ffffff')


def dientes_capa(nombre, R, arriba=True, encia=2, largo=5, paso=4, colmillo=True):
    """Los dientes en una 2.ª capa (la caja algo mayor que la mandíbula, recortada), a 32 por bloque para que salgan en
    punta: una fila de dientes triangulares (cada uno, de 3 píxeles de base y de largo distinto; más largos los de las
    esquinas, los colmillos), claros a la izquierda y en sombra a la derecha, con la punta más clara y la raíz un tono
    más oscura, y encima la encía (una fila rosa oscura). 'arriba': los de la mandíbula de arriba, que cuelgan; si no,
    los de abajo, de pie. 'encia': las filas de la capa que montan sobre la mandíbula (transparentes salvo la encía)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if cara in ('arriba', 'abajo', 'atras'):
            return tex, None
        y = ys if arriba else (th - 1 - ys)             # filas desde la encía hacia la punta
        r = y - encia                                   # fila dentro del diente (0, la raíz)
        rng = np.random.default_rng(int(s) * 31 + tw * 7 + th)
        n = max(1, tw // paso)
        inicio = (tw - n * paso) // 2
        k = np.clip((xs - inicio) // paso, 0, n - 1)
        u = (xs - inicio) - k * paso                    # columna dentro del hueco de cada diente (0..paso-1)
        largos = rng.integers(max(2, largo - 2), largo + 1, n)
        if colmillo and n >= 3:
            largos[0] = largos[-1] = largo + 1
        L_ = largos[k]
        c = (paso - 2) / 2.0                            # el centro del diente (la última columna es el hueco)
        ancho = (paso - 1) / 2.0 * (1 - r / np.maximum(L_, 1))   # medio ancho en cada fila: de la base a la punta
        dentro = (r >= 0) & (r < L_) & (np.abs(u - c) <= ancho + 0.01) & (u <= paso - 2)
        v = 2.9 + (u < c) * 0.6 - (u > c) * 0.5 + (r >= L_ - 2) * 0.5 - (r == 0) * 0.6
        dnt = L.color_continuo(R, v)
        encia_ = (y == encia - 1)
        rgb = np.where(encia_[..., None], L.color_continuo(CARNE, np.full(v.shape, 1.4)), dnt)
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(dentro | encia_, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn))


def fauces(raiz, color):
    """La Fauces (la Carnivenus de su ficha), más grande: el tallo de bloques que sale del suelo, sube y se dobla hacia
    delante en J, con un nudo en cada junta y dos hojas, y la cabeza de dos mandíbulas cuadradas, rosa por dentro, con
    los dientes en una 2.ª capa alrededor del canto (pintados más finos, en punta). Al píxel de Minecraft lo demás."""
    R, RH, RD, (nombre_es, nombre_en), piel_h, cont_h = COLORES[color]
    m = B.Modelo(f'fauces_{color}', K=2, ancho=128)
    m.escala = 1.0
    piel = tallo(f'tallo_{color}', R)
    piel_nudo = tallo(f'nudo_{color}', R, base=1.6, nudo=True)
    hoja = hoja_plana(f'hoja_{color}', RH)
    # La raíz: el bulbo hundido en el suelo y cuatro hojas tendidas, abiertas.
    m.parte('raiz', None, (0, 0, 0))
    redondo(m, 'raiz', (0, 1.5, 0), (8, 3, 8), tallo(f'bulbo_{color}', RH, base=1.6))
    for k, ang in enumerate((40, 130, 220, 310)):
        a = math.radians(ang)
        d = np.array((math.sin(a), 0.0, math.cos(a)))
        m.hoja('raiz', tuple(np.array((0, 0.7, 0)) + d * 6.5), 5, 10, hoja, rot=(-78, ang + 180, 0))
    # El tallo: cuatro tramos de bloques, que sube y se dobla hacia delante (en J), con un nudo en cada junta.
    puntos = [np.array(p) for p in ((0, 2.5, -0.6), (0, 9.5, -1.8), (0, 16.0, -1.6), (0, 21.5, 0.5), (0, 24.0, 4.0))]
    gruesos = (5, 5, 4, 4)
    padre = 'raiz'
    for i in range(4):
        n = m.parte(f'tallo{i}', padre, tuple(puntos[i]))
        m.viga(n, puntos[i], puntos[i + 1], gruesos[i], piel, extra=0.8)
        if i > 0:
            m.caja(n, tuple(puntos[i]), (gruesos[i] + 1, 1, gruesos[i] + 1), piel_nudo)
        padre = n
    # Dos hojas en el tallo, hacia los lados.
    for (i, lado) in ((1, 1), (2, -1)):
        p = puntos[i] + np.array((lado * 4.4, 2.0, 0))
        m.hoja(f'tallo{i - 1}', tuple(p), 4, 8, hoja, rot=(0, 90, lado * -55))

    # La cabeza: la mandíbula de arriba (cuadrada, con la carne por dentro) y la de abajo, que se abre.
    p4 = puntos[4]
    m.parte('cabeza', 'tallo3', tuple(p4))
    z0 = p4[2] - 3.0
    W, D = 11, 13
    fuera = tallo(f'cabeza_{color}', R, base=2.2, estomas=0.07)
    brillo_boca = ASCUA if color == 'carmin' else None
    dentro = B.fino(boca(f'boca_{color}', CARNE, brilla=brillo_boca))
    cy_sup = p4[1] + 3.2
    redondo(m, 'cabeza', (0, cy_sup, z0 + D / 2), (W, 4, D), fuera, caras={'abajo': dentro})
    # La garganta (la bisagra de atrás), con la carne por dentro.
    m.caja('cabeza', (0, p4[1] - 0.2, z0 + 1.2), (W - 2, 5, 2), fuera, caras={'frente': dentro})
    m.parte('mandibula', 'cabeza', (0, p4[1] - 1.2, z0 + 1.2))
    cy_inf = p4[1] - 3.0
    redondo(m, 'mandibula', (0, cy_inf, z0 + D / 2 - 0.5), (W - 1, 3, D - 1), fuera, caras={'arriba': dentro})
    # Los dientes, en una 2.ª capa alrededor del canto de cada mandíbula (delante y a los lados; detrás, la bisagra).
    borde_sup = cy_sup - 2.0
    m.caja('cabeza', (0, borde_sup - 0.75, z0 + D / 2), (W + 0.5, 3.5, D + 0.5),
           dientes_capa(f'dientes_arriba_{color}', RD, arriba=True, encia=2, largo=5))
    borde_inf = cy_inf + 1.5
    m.caja('mandibula', (0, borde_inf + 0.5, z0 + D / 2 - 0.5), (W - 0.5, 3.0, D - 0.5),
           dientes_capa(f'dientes_abajo_{color}', RD, arriba=False, encia=2, largo=4))

    # Lo de cada color.
    if color == 'verde':
        # La baba de veneno que cuelga de la mandíbula de abajo (gotas encendidas).
        gota = luz_plana('baba_veneno', VENENO, v=2.2)
        for (x, largo) in ((-2.5, 2), (1.5, 3)):
            m.caja('mandibula', (x, cy_inf - 1.5 - largo / 2, z0 + D - 3.0), (1, largo, 1), gota)
    elif color == 'carmin':
        # Las espinas del tallo: púas de un píxel, oscuras, hacia fuera y algo hacia arriba.
        espina = tallo('espina_carmin', rampa('0a0202', '1e0606', '360c0c', '501414', '6c1e1e'), base=1.4, estomas=0)
        for i, (lado, z) in enumerate(((1, 0), (-1, 0), (0, -1), (1, 0), (-1, 1), (0, 1))):
            t = i % 4
            base_p = puntos[t] + (puntos[t + 1] - puntos[t]) * (0.3 + 0.15 * (i % 3))
            g = gruesos[t] / 2
            dirv = np.array((lado, 0.6, z if lado == 0 else 0.0))
            dirv = dirv / np.linalg.norm(dirv)
            m.viga(f'tallo{t}', base_p + dirv * (g - 0.3), base_p + dirv * (g + 2.0), 1, espina)
    else:
        # Los carámbanos que cuelgan de la mandíbula de abajo, y escarcha encima de la cabeza (2.ª capa).
        hielo = luz_plana('hielo_escarcha', HIELO, v=2.6)
        for (x, z, largo) in ((-3.5, D - 3.0, 3), (-0.5, D - 2.5, 2), (3.0, D - 3.5, 4), (4.0, 5.0, 2), (-4.0, 6.0, 3)):
            m.caja('mandibula', (x, cy_inf - 1.5 - largo / 2, z0 + z), (1, largo, 1), hielo)

        def escarcha_capa(tw, th, cara, s):
            xs, ys = L._malla(tw, th)
            a = _azar1(xs, ys, s)
            if cara == 'arriba':
                dentro_ = a < 0.45
            elif cara == 'abajo':
                dentro_ = np.zeros((th, tw), bool)
            else:
                dentro_ = (ys == 0) & (a < 0.7) | ((ys == 1) & (a < 0.25))
            v = 2.6 + (a > 0.8) * 0.8
            tex = L._rgba(L.color_continuo(HIELO, np.full((th, tw), 1.0) * v))
            tex[..., 3] = np.where(dentro_, 255, 0)
            return tex, None
        redondo(m, 'cabeza', (0, cy_sup + 0.25, z0 + D / 2), (W + 1, 4, D + 1), B.Pintor('escarcha_capa', escarcha_capa))

    m.mirar(('cabeza', 0.5), ('tallo3', 0.3))
    # siempre: el tallo se mece, la cabeza respira con la boca entreabierta.
    s = m.anim('siempre', 3.0, bucle=True)
    s.onda('tallo1', 'r', 2, 3, periodo=3.0)
    s.onda('tallo2', 'r', 0, 3, periodo=1.5, fase=0.25)
    s.onda('cabeza', 'r', 0, -3, periodo=1.5)
    s.onda('mandibula', 'r', 0, 6, periodo=1.5, forma=lambda v: (v + 1) / 2)
    # ataque: se echa atrás, abre la boca de par en par, se lanza y la cierra de golpe.
    at = m.anim('ataque', 0.6)
    at.rot('tallo2', [(0, 0, 0, 0), (0.16, -16, 0, 0), (0.28, 22, 0, 0), (0.6, 0, 0, 0)])
    at.rot('tallo3', [(0, 0, 0, 0), (0.16, -14, 0, 0), (0.28, 26, 0, 0), (0.6, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.16, -20, 0, 0), (0.28, 10, 0, 0), (0.6, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.16, 38, 0, 0), (0.28, -2, 0, 0), (0.6, 0, 0, 0)])
    # muerte: se marchita y se dobla hasta el suelo.
    d = m.anim('muerte', 1.0)
    d.rot('tallo1', [(0, 0, 0, 0), (1.0, 34, 0, 8)])
    d.rot('tallo2', [(0, 0, 0, 0), (1.0, 40, 0, 0)])
    d.rot('tallo3', [(0, 0, 0, 0), (1.0, 30, 0, 0)])
    d.rot('mandibula', [(0, 0, 0, 0), (0.4, 30, 0, 0), (1.0, 24, 0, 0)])
    d.esc('raiz', [(0, 1, 1, 1), (1.0, 0.9, 0.8, 0.9)])
    m.paso = 0.0

    def dib(px, filas, c_):
        for f in range(4, 8):
            a, b = filas[f]
            for x in range(a + 1, b):
                px[x, f] = c_(piel_h[1])
        for x in range(5, 11):
            px[x, 6] = c_('e07a8a')
        for x in (5, 7, 9):
            px[x, 5] = c_('fffcf2')
        for x in (6, 8, 10):
            px[x, 7] = c_('fffcf2')
        for f in range(9, 14):
            px[7, f] = px[8, f] = c_(piel_h[2])
    return terminar(m, raiz, f'Fauces {nombre_es}', f'{nombre_en} Maw', (piel_h, cont_h, dib),
                    ((1.9, 2.0, 2.8), (0, 1.2, 0.15)),
                    particulas=(('savia', chispa(tuple(int(piel_h[0][i:i + 2], 16) for i in (0, 2, 4)))),
                                ('hoja', esquirla((62, 138, 38))))
                    + ((('escarcha', copo()),) if color == 'escarcha' else ()),
                    poses=[('siempre', 0.5), ('ataque', 0.16), ('ataque', 0.3), ('muerte', 1.0)])


# ======================================================================================================================
#  La Trampa Verde (Tramplanta)
# ======================================================================================================================
# Lo de dentro, en grises, como la hierba de Minecraft: mientras espera, el juego la tiñe del verde de su bioma.
CESPED = rampa('6a6a6a', '808080', '969696', 'acacac', 'c2c2c2')
HOJA_T = rampa('0e2a08', '1a4a10', '2a6a1a', '3e8a26', '5aac36')
ROJO_T = rampa('4a0a14', '7a1424', 'aa2a3a', 'd84a5a', 'f87a88')
# Las pestañas, en grises claros: escondida, el juego las tiñe del verde de la hierba (un poco más claras que ella, como
# briznas); cerrada, son los dientes pálidos de su ficha.
PESTANA = rampa('76766f', '93938a', 'adada3', 'c4c4ba', 'd8d8ce')
# Los cantos de los lóbulos: un gris verdoso que cerrado parece la hoja y teñido se confunde con la hierba.
CANTO_T = rampa('5e6658', '737d6c', '899482', '9faa97', 'b4beab')


def trampa(raiz):
    """La Trampa Verde: dos lóbulos de pie unidos por la bisagra (en escalones, de media luna), con las pestañas largas
    en el borde de arriba. Por fuera, verdes con las venas y el borde enrojecido; por dentro, el césped (en grises, que el
    juego tiñe del verde de la hierba del bioma) con los tres pelillos que la disparan. Escondida, se tumba abierta en el
    suelo, se hunde un píxel y casi no se ve (Juan, 19-10-2026: «solo un poco debe diferenciarse… si un despistado no
    presta la atención mínima, va a caer»): lo que queda a la vista es del gris de la hierba de Minecraft (la misma luz y
    el mismo contraste, a 16 por bloque), que el juego tiñe del verde de su bioma; solo la delatan las pestañas, algo más
    claras, y la línea del labio."""
    m = B.Modelo('trampa', K=2, ancho=128)
    m.escala = 1.0
    m.parte('base', None, (0, 0, 0))
    canto = B.Pintor('canto_trampa', lambda tw, th, c, s_: (L._rgba(L.color_continuo(
        CANTO_T, np.full((th, tw), 2.0) + (_azar1(*L._malla(tw, th), s_) > 0.7) * 0.5)), None))
    m.caja('base', (0, 0.5, 0), (2, 1, 14), canto, caras={'arriba': None})

    def fuera_fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        v = _v(tw, th, cara, s, 2.0, 0.6)
        venas = B.grietas(tw, th, s, cara, cuantas=max(1, tw * th // 24), giro=0.25, ramas=0.1)
        v = np.where(venas, v - 0.7, v)
        tex = L._rgba(L.color_continuo(HOJA_T, v))
        return tex, None

    def borde_fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = 2.4 + ((xs + ys) % 2) * 0.4
        return L._rgba(L.color_continuo(ROJO_T, v)), None

    def dentro_fn(tw, th, cara, s):
        # El césped como la hierba de Minecraft (en grises, que el juego tiñe): un gris de media 147 y desviación 18,
        # de 112 a 195, píxel a píxel a 16 por bloque.
        xs, ys = L._malla(tw, th)
        z = (_azar1(xs, ys, s) + _azar1(xs, ys, s + 3) + _azar1(xs, ys, s + 7) - 1.5) / 0.5
        g = np.clip(147 + z * 18, 112, 195)
        # Los pelillos que la disparan: dos o tres píxeles apenas más oscuros y algo rojizos.
        pelo = _azar1(xs, ys, s + 11) > 0.985
        rgb = np.stack([g, g, g], -1)
        rgb[pelo] = (128, 104, 100)
        return L._rgba(rgb), None
    fuera = B.fino(B.Pintor('fuera_trampa', fuera_fn))
    borde = B.Pintor('borde_trampa', borde_fn)
    dentro = B.Pintor('dentro_trampa', dentro_fn)
    pestana = diente('pestana_trampa', PESTANA)
    # Las filas del lóbulo, de abajo arriba: (alto, largo); la media luna en escalones.
    filas = ((2, 14), (2, 12), (1, 10), (1, 7))
    for lado, ld in LADOS:
        n = m.parte(f'hoja_{ld}', 'base', (lado * 1.0, 1.0, 0))
        ext, inn = ('der', 'izq') if lado > 0 else ('izq', 'der')
        y = 1.0
        for k, (h, largo) in enumerate(filas):
            x = lado * (1.5 + (0.5 if k < 2 else 0.0))
            # Lo que se ve escondida (lo de dentro, los cantos de las puntas y lo de arriba de cada escalón), del gris de la
            # hierba; solo el labio de arriba del todo, rojo.
            caras = {'frente': canto, 'atras': canto, ext: fuera, inn: dentro, 'abajo': canto,
                     'arriba': borde if k == len(filas) - 1 else dentro}
            m.caja(n, (x, y + h / 2, 0), (1, h, largo), None, caras=caras)
            # Las pestañas: en los escalones que deja la fila de encima, una por cada tres píxeles, cortas.
            sig = filas[k + 1][1] if k + 1 < len(filas) else 0
            for z in np.arange(-largo / 2 + 0.5, largo / 2, 3.0):
                if abs(z) < sig / 2 - 0.1:
                    continue
                m.caja(n, (x - lado * 0.5, y + h + 1.0, z), (1, 2, 1), pestana, rot=(0, 0, lado * 25))
            y += h
        # Las pestañas de arriba del todo, más largas, que se cruzan con las del otro lóbulo.
        for z in np.arange(-filas[-1][1] / 2 + 0.5, filas[-1][1] / 2, 2.0):
            m.caja(n, (lado * 1.5 - lado * 0.6, y + 1.4, z + (1.0 if lado > 0 else 0.0)), (1, 3, 1), pestana,
                   rot=(0, 0, lado * 28))
    # estado1: escondida (los lóbulos abiertos y tumbados en el suelo).
    e1 = m.anim('estado1', 1.0, bucle=True)
    for lado, ld in LADOS:
        e1.rot(f'hoja_{ld}', [(0, 0, 0, lado * -90), (1.0, 0, 0, lado * -90)])
    # Hundida un píxel en el suelo: solo asoma la cara de arriba.
    e1.mov('base', [(0, 0, -1.2, 0), (1.0, 0, -1.2, 0)])
    # aparece: salta y se cierra de golpe (de tumbada a cerrada, pasándose un poco y rebotando).
    ap = m.anim('aparece', 0.45)
    for lado, ld in LADOS:
        ap.rot(f'hoja_{ld}', [(0, 0, 0, lado * -90), (0.07, 0, 0, lado * -40), (0.12, 0, 0, lado * 8),
                             (0.2, 0, 0, lado * -4), (0.3, 0, 0, 0)])
    ap.mov('base', [(0, 0, 0, 0), (0.08, 0, 2.0, 0), (0.2, 0, -0.3, 0), (0.3, 0, 0, 0)])
    # reposo (cerrada): mastica, apretando y aflojando.
    r = m.anim('reposo', 1.2, bucle=True)
    for lado, ld in LADOS:
        r.onda(f'hoja_{ld}', 'r', 2, lado * -7, periodo=0.6, forma=lambda v: max(0.0, v))
    r.onda('base', 'e', 1, 0.04, periodo=0.6, base=1.0)
    # ataque: aprieta fuerte.
    at = m.anim('ataque', 0.4)
    for lado, ld in LADOS:
        at.rot(f'hoja_{ld}', [(0, 0, 0, 0), (0.08, 0, 0, lado * 6), (0.4, 0, 0, 0)])
    at.esc('base', [(0, 1, 1, 1), (0.08, 1.06, 0.92, 1.0), (0.4, 1, 1, 1)])
    # especial: se vuelve a abrir despacio y se tumba (sumado a estado1: de cerrada a tumbada).
    es = m.anim('especial', 1.0)
    for lado, ld in LADOS:
        es.rot(f'hoja_{ld}', [(0, 0, 0, lado * 90), (0.25, 0, 0, lado * 75), (0.35, 0, 0, lado * 80),
                             (0.8, 0, 0, lado * 6), (1.0, 0, 0, 0)])
    # muerte: los lóbulos se abren lacios y todo se encoge.
    d = m.anim('muerte', 1.0)
    for lado, ld in LADOS:
        d.rot(f'hoja_{ld}', [(0, 0, 0, 0), (1.0, 0, 0, lado * -65)])
    d.esc('base', [(0, 1, 1, 1), (1.0, 0.85, 0.6, 0.85)])
    m.paso = 0.0

    def dib(px, filas_, c_):
        for f in range(6, 13):
            a, b = filas_[f]
            for x in range(a + 1, b):
                px[x, f] = c_('3e8a26' if (x + f) % 3 else '2a6a1a')
        for x in (4, 6, 8, 10, 12):
            px[x, 5] = c_('f8fff0')
        for x in (5, 7, 9, 11):
            px[x, 6] = c_('d84a5a')
    return terminar(m, raiz, 'Trampa Verde', 'Green Trap', (('5aac36', '3e8a26', '2a6a1a'), ('0e2a08', '061404'), dib),
                    ((1.1, 1.0, 1.5), (0, 0.3, 0)),
                    particulas=(('hoja', esquirla((94, 170, 54))), ('pestana', esquirla((224, 240, 192)))),
                    poses=[('estado1', 0.5), ('aparece', 0.1), ('reposo', 0.15), ('muerte', 1.0)])


# ======================================================================================================================
#  La Piña Brava (Piña Malibú)
# ======================================================================================================================
PINA = rampa('6a3a04', '9a5a0a', 'd08e1a', 'f0bc3a', 'fde27a')
OJO_PINA = rampa('2a1404', '4a2808', '6a3a0e', '8a5418', 'a86e22')
CORONA = rampa('0e3a10', '1a5a16', '2a7e22', '44a432', '6ec84a')
RAIZ_P = rampa('2e1e10', '4a3018', '6a4824', '8e6634', 'b08850')


def escamas_pina(nombre):
    """La piel de la piña, pintada más fina (a 32 por bloque: Juan, 19-10-2026, «en la piña sí deberías aumentar los
    píxeles»): rombos en filas desplazadas, cada uno abombado (más claro arriba, en sombra abajo), con su junta oscura,
    su ojo pardo abajo en el centro y su pincho claro arriba; más clara arriba la piña entera."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = _v(tw, th, cara, s, 2.3, 1.0)
        if cara not in ('arriba', 'abajo') and tw > 4:
            # Lo redondo: las columnas de los cantos, más oscuras.
            v = v - ((xs == 0) | (xs == tw - 1)) * 0.5 - ((xs == 1) | (xs == tw - 2)) * 0.2
        P = 6
        u = (xs + ys) % P
        w = (xs - ys) % P
        # La posición dentro del rombo: de -1 a 1 en las dos diagonales; arriba es donde u + w es pequeño.
        du = (u + 0.5) / P * 2 - 1
        dw = (w + 0.5) / P * 2 - 1
        alto = -(du + dw) / 2                       # 1 arriba del rombo, -1 abajo
        v = v + alto * 0.45
        junta = (u == 0) | (w == 0)
        v = np.where(junta, v - 1.0, v)
        rgb = L.color_continuo(PINA, v)
        if cara not in ('arriba', 'abajo'):
            ojo = (np.abs(du) < 0.36) & (np.abs(dw) < 0.36) & (alto < 0.1)
            ojo_c = (np.abs(du) < 0.2) & (np.abs(dw) < 0.2) & (alto < 0.1)
            punta = (np.abs(du + 0.5) < 0.2) & (np.abs(dw + 0.5) < 0.2)
            rgb = np.where(ojo[..., None], L.color_continuo(OJO_PINA, np.full(ojo.shape, 2.4)), rgb)
            rgb = np.where(ojo_c[..., None], L.color_continuo(OJO_PINA, np.full(ojo.shape, 1.2)), rgb)
            rgb = np.where(punta[..., None], L.color_continuo(PINA, np.full(punta.shape, 4.2)), rgb)
        return L._rgba(rgb), None
    return B.fino(B.Pintor(nombre, fn))


def hoja_corona(nombre):
    """Una hoja de la corona en una lámina, pintada fina: estrecha, en punta, con el nervio claro, el borde un tono más
    oscuro y la punta más clara (lo de fuera, transparente)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        u = (xs + 0.5) / tw - 0.5
        v = (ys + 0.5) / th                      # 0 arriba (la punta), 1 abajo (la base)
        perfil = 0.5 * np.clip(v * 1.15, 0.05, 1.0)
        dentro = np.abs(u) <= perfil
        val = 2.0 + (1 - v) * 1.4 + (u < 0) * 0.3
        val = np.where(np.abs(u) < 0.5 / tw + 0.01, val + 0.6, val)
        val = np.where(np.abs(u) > perfil - 1.0 / tw, val - 0.6, val)
        tex = L._rgba(L.color_continuo(CORONA, val))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn))


def _giro_hacia(d, giro):
    """Los ángulos (x, y, z en radianes, Z·Y·X como ModelPart) que llevan el eje Y a la dirección d, girando además
    'giro' grados alrededor de ella (para cruzar dos láminas)."""
    d = np.asarray(d, float) / np.linalg.norm(d)
    ref = np.array((0.0, 0.0, 1.0)) if abs(d[2]) < 0.9 else np.array((1.0, 0.0, 0.0))
    x = np.cross(d, ref)
    x /= np.linalg.norm(x)
    z = np.cross(x, d)
    g = math.radians(giro)
    x, z = x * math.cos(g) + z * math.sin(g), -x * math.sin(g) + z * math.cos(g)
    R = np.stack([x, d, z], axis=1)
    return np.array(B.euler_zyx(R))


def pina(raiz):
    """La Piña Brava: una piña chica (las escamas en rombo, cada una con su ojo y su pincho) con la corona de hojas en
    punta (las de dentro de pie, las de fuera abiertas), dos patas cortas de raíz y dos puños de hoja: sin cara, como
    la de su ficha. Corre y pega muy deprisa: un uno-dos con los puños."""
    m = B.Modelo('pina', K=2, ancho=128)
    m.escala = 1.0
    m.parte('cuerpo', None, (0, 3.0, 0))
    cyb = 6.5
    esc = escamas_pina('escamas_pina')
    m.caja('cuerpo', (0, cyb, 0), (6, 7, 6), esc)
    # Los hombros y la base, más estrechos: la piña se cierra arriba y abajo.
    m.caja('cuerpo', (0, cyb + 3.5 + 0.5, 0), (4, 1, 4), esc)
    m.caja('cuerpo', (0, cyb - 3.5 - 0.5, 0), (4, 1, 4), esc)
    # La corona: un tocón y las hojas en tres pisos.
    m.parte('corona', 'cuerpo', (0, cyb + 3.5, 0))
    m.caja('corona', (0, cyb + 4.0, 0), (2, 1, 2), tallo('toco_pina', CORONA, base=1.6))
    # Las hojas, en dos láminas cruzadas (para que se vean de todos lados), estrechas y en punta.
    hoja = hoja_corona('hoja_corona')
    base_c = np.array((0, cyb + 4.4, 0))
    for k, (ang, incl, largo) in enumerate(((0, 6, 6), (180, 8, 5), (60, 24, 5), (120, 24, 5), (240, 24, 5), (300, 24, 5),
                                            (30, 46, 4), (90, 46, 4), (150, 46, 4), (210, 46, 4), (270, 46, 4),
                                            (330, 46, 4), (0, 66, 3), (90, 66, 3), (180, 66, 3), (270, 66, 3))):
        a, b = math.radians(ang), math.radians(incl)
        dvec = np.array((math.sin(a) * math.sin(b), math.cos(b), math.cos(a) * math.sin(b)))
        centro = base_c + dvec * (largo / 2 + 0.3)
        for giro in (0, 90):
            m.hoja('corona', tuple(centro), 2, largo, hoja, rot=tuple(np.degrees(_giro_hacia(dvec, giro))))
    # Los bracitos (de tallo) y los puños de hoja.
    brazo = tallo('brazo_pina', CORONA, base=1.8)
    puno = tallo('puno_pina', CORONA, base=2.4, estomas=0.12)
    for lado, ld in LADOS:
        h = np.array((lado * 3.0, cyb - 0.5, 0.5))
        n = m.parte(f'brazo_{ld}', 'cuerpo', tuple(h))
        mano = h + np.array((lado * 1.2, -1.6, 1.4))
        m.viga(n, h, mano, 1, brazo, extra=0.5)
        m.caja(n, tuple(mano + np.array((0, -0.4, 0.5))), (2, 2, 2), puno)
    # Las patas, cortas, de raíz.
    pata = tallo('pata_pina', RAIZ_P, base=1.8)
    for lado, ld in LADOS:
        n = m.parte(f'pata_{ld}', 'cuerpo', (lado * 1.5, 3.0, 0))
        m.caja_desde(n, (lado * 1.5, 0.0, 0.0), (2, 3.4, 2), pata)
        m.caja(n, (lado * 1.5, 0.5, 0.6), (2, 1, 3), pata)
    m.mirar(('cuerpo', 0.3))
    a = m.anim('andar', 0.3, bucle=True)
    a.onda('pata_d', 'r', 0, 42)
    a.onda('pata_i', 'r', 0, 42, fase=0.5)
    a.onda('brazo_d', 'r', 0, -30, fase=0.5)
    a.onda('brazo_i', 'r', 0, -30)
    a.onda('cuerpo', 'r', 2, 6, periodo=0.3)
    a.onda('cuerpo', 'm', 1, 0.6, periodo=0.15, forma=lambda v: abs(v))
    a.onda('corona', 'r', 0, 8, periodo=0.15)
    s = m.anim('siempre', 2.0, bucle=True)
    s.onda('corona', 'r', 2, 4, periodo=2.0)
    rp = m.anim('reposo', 1.2, bucle=True)
    rp.onda('cuerpo', 'm', 1, 0.4, periodo=0.6, forma=lambda v: abs(v))
    for lado, ld in LADOS:
        rp.onda(f'brazo_{ld}', 'r', 0, -10, periodo=0.6, fase=0.5 if lado > 0 else 0.0)
    # ataque: el uno-dos (derecha, izquierda), con el cuerpo que gira en cada golpe.
    at = m.anim('ataque', 0.36)
    at.rot('brazo_d', [(0, 0, 0, 0), (0.07, -80, 0, 0), (0.16, 0, 0, 0)])
    at.rot('brazo_i', [(0, 0, 0, 0), (0.18, 0, 0, 0), (0.25, -80, 0, 0), (0.34, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.07, 0, -14, 0), (0.18, 0, 0, 0), (0.25, 0, 14, 0), (0.36, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.4, 0, 0, 60), (0.7, 0, 0, 92), (1.0, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -2.5, 0)])
    d.rot('corona', [(0, 0, 0, 0), (1.0, 20, 0, 0)])
    m.paso = 2.4

    def dib(px, filas, c_):
        for f in range(1, 4):
            for x in (6, 8, 10):
                px[x, f] = c_('44a432')
        for f in range(5, 14):
            a, b = filas[f]
            for x in range(a + 1, b):
                if (x + f) % 3 == 0:
                    px[x, f] = c_('9a5a0a')
    return terminar(m, raiz, 'Piña Brava', 'Fierce Pineapple', (('fde27a', 'f0bc3a', 'd08e1a'), ('6a3a04', '3a1e02'), dib),
                    ((0.8, 0.7, 1.1), (0, 0.42, 0)),
                    particulas=(('jugo', chispa((246, 194, 74))), ('hoja', esquirla((66, 160, 58)))),
                    poses=[('andar', 0.08), ('andar', 0.22), ('ataque', 0.07), ('ataque', 0.25)])


# ======================================================================================================================
#  El Zombi Planta
# ======================================================================================================================
PIEL_Z = rampa('1e3a1e', '2e5428', '3e6e34', '548a44', '6ea458')
CAMISA = rampa('0e3e3e', '145a5a', '1e7676', '2a9090', '40aaaa')
PANTALON = rampa('1a1a3a', '262658', '343476', '444490', '5656a8')
HIEDRA = rampa('0a2a08', '14440e', '206214', '2e7e1c', '44a02a')
FLOR = rampa('6a1a4a', 'a0306e', 'd04a94', 'f07ab8', 'ffb4dc')
POLEN = rampa('6a4a04', 'a0780a', 'd8aa1a', 'f8d84a', 'fff4a0')
CORTEZA = rampa('2a1a0c', '3e2814', '563a1e', '6e4c28', '886034')


def piel_zombi(nombre, cara=False):
    """La piel del zombi, verde podrida, al píxel: el tono que corre, manchas de musgo (dos píxeles más oscuros) y, en
    la cara, los ojos (el derecho, una cuenca honda; el izquierdo, encendido de polen), la nariz y la boca."""
    def fn(tw, th, cara_, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        v = _v(tw, th, cara_, s, 2.2, 0.7)
        v = v - (a < 0.12) * 0.7 + (a > 0.93) * 0.5
        tex = L._rgba(L.color_continuo(PIEL_Z, v))
        emis = None
        if cara and cara_ == 'frente' and tw >= 8 and th >= 8:
            # La cara de 8 x 8, como la de los zombis: ojos en la fila 4, la nariz y la boca.
            ojo_d = (ys == 4) & ((xs == 1) | (xs == 2))
            ojo_i = (ys == 4) & ((xs == 5) | (xs == 6))
            tex[ojo_d, :3] = (8, 14, 8)
            tex[(ys == 3) & ((xs == 1) | (xs == 2)), :3] = L.color_continuo(PIEL_Z, np.full(2, 0.6))
            tex[ojo_i, :3] = L.color_continuo(POLEN, np.full(int(ojo_i.sum()), 3.2))
            tex[(ys == 5) & ((xs == 3) | (xs == 4)), :3] = L.color_continuo(PIEL_Z, np.full(2, 0.8))
            tex[(ys == 6) & (xs >= 2) & (xs <= 5), :3] = (14, 22, 12)
            emis = np.zeros_like(tex)
            emis[ojo_i] = tex[ojo_i]
        return tex, emis
    return B.Pintor(nombre, fn)


def ropa(nombre, R, rotos=0.12):
    """La ropa desteñida y rota: el tono que corre, las costuras, y los rotos (la piel verde asoma)."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        n = L._ruido(tw, th, s * 3 + 1, 2.5)
        v = _v(tw, th, cara, s, 2.1, 0.7) - (a < 0.08) * 0.6
        rgb = L.color_continuo(R, v)
        roto = n > 1.0 - rotos * 2.5
        rgb = np.where(roto[..., None], L.color_continuo(PIEL_Z, np.full(n.shape, 1.6) + (a > 0.5) * 0.6), rgb)
        return L._rgba(rgb), None
    return B.Pintor(nombre, fn)


def hiedra_capa(nombre, densidad=0.35, flores=0.0, arriba=0.8):
    """La 2.ª capa de hiedra y musgo (recortada): hojitas de un píxel en grupos (lo de arriba más tupido, el musgo), con
    alguna flor rosa con su centro de polen. Lo demás, transparente."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        n = L._ruido(tw, th, s * 5 + 2, 2.0)
        if cara == 'arriba':
            dentro = n + a * 0.4 > 1.0 - arriba
        elif cara == 'abajo':
            dentro = np.zeros((th, tw), bool)
        else:
            dentro = n + a * 0.3 > 1.15 - densidad - (ys < 2) * 0.35
        v = 2.0 + (a > 0.6) * 0.8 - (a < 0.2) * 0.6
        rgb = L.color_continuo(HIEDRA, v)
        flor = dentro & (_azar1(xs, ys, s + 9) < flores)
        rgb = np.where(flor[..., None], L.color_continuo(FLOR, np.full(a.shape, 3.0)), rgb)
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn))


def zombi_planta(raiz):
    """El Zombi Planta: un zombi (la anatomía de siempre: cabeza de 8, cuerpo de 8 x 12, brazos y piernas de 4 x 12)
    al que se ha comido la planta: la piel verde podrida, la camisa turquesa y el pantalón azul desteñidos y rotos, la
    hiedra y el musgo en 2.ª capa (más tupidos en la cabeza y los hombros, con alguna flor), una flor rosa que le brota
    de un ojo (el otro, encendido de polen), raíces en los pies y un arbolito que le crece a la espalda."""
    m = B.Modelo('zombi_planta', K=2, ancho=128)
    m.escala = 1.0
    piel = piel_zombi('piel_zombi')
    camisa = ropa('camisa_zombi', CAMISA)
    pantalon = ropa('pantalon_zombi', PANTALON, rotos=0.08)
    capa = hiedra_capa('hiedra_capa', densidad=0.3, flores=0.03)
    capa_cab = hiedra_capa('musgo_cabeza', densidad=0.5, flores=0.06, arriba=1.2)
    m.parte('cuerpo', None, (0, 12, 0))
    m.caja('cuerpo', (0, 18, 0), (8, 12, 4), camisa)
    m.caja('cuerpo', (0, 18, 0), (9, 13, 5), capa)
    m.parte('cabeza', 'cuerpo', (0, 24, 0))
    m.caja('cabeza', (0, 28, 0), (8, 8, 8), piel, caras={'frente': piel_zombi('cara_zombi', cara=True)})
    m.caja('cabeza', (0, 28.25, 0), (9, 8.5, 9), capa_cab, caras={'abajo': None})
    # La flor que le brota del ojo derecho (a la izquierda de quien lo mira): cuatro pétalos y el centro de polen.
    m.parte('flor', 'cabeza', (-2.0, 28.0, 4.0))
    flor = B.fino(B.Pintor('flor_ojo', lambda tw, th, c, s: _flor(tw, th)))
    m.hoja('flor', (-2.0, 28.5, 4.6), 4, 4, flor, rot=(0, 0, 0), dos_caras=False)
    m.caja('flor', (-2.0, 28.2, 4.3), (1, 1, 1), tallo('tallito_flor', HIEDRA, base=2.0))
    # Los brazos, hacia delante, con la hiedra enroscada.
    for lado, ld in LADOS:
        n = m.parte(f'brazo_{ld}', 'cuerpo', (lado * 6, 22, 0))
        m.caja(n, (lado * 6, 22, 4), (4, 4, 12), camisa if True else piel,
               caras={'frente': piel, 'abajo': piel, 'arriba': camisa})
        m.caja(n, (lado * 6, 22, 4.5), (4.6, 4.6, 11), hiedra_capa('hiedra_brazo', densidad=0.05, arriba=0.25),
               caras={'abajo': None})
        # Los dedos, raíces que cuelgan.
        for dx in (-1.0, 1.0):
            m.caja(n, (lado * 6 + dx, 19.0, 9.5), (1, 2, 1), tallo('raicilla', CORTEZA, base=2.0))
    # Las piernas, con raíces en los pies.
    for lado, ld in LADOS:
        n = m.parte(f'pierna_{ld}', 'cuerpo', (lado * 2, 12, 0))
        m.caja(n, (lado * 2, 6, 0), (4, 12, 4), pantalon)
        for (dx, dz, ang) in ((-1.5, 1.5, 30), (1.5, 1.0, -30), (0.0, -1.5, 0)):
            m.viga(n, (lado * 2 + dx * 0.6, 1.0, dz * 0.6), (lado * 2 + dx * 1.6, 0.2, dz * 1.6), 1,
                   tallo('raiz_pie', CORTEZA, base=1.8))
    # El arbolito de la espalda: el tronco que sale del hombro y la copa.
    m.parte('arbolito', 'cuerpo', (1.5, 22, -2.5))
    m.viga('arbolito', (1.5, 21, -2.5), (2.5, 29, -3.5), 1, tallo('tronco_arbolito', CORTEZA, base=2.0))
    m.viga('arbolito', (2.0, 25, -3.0), (4.0, 27, -3.2), 1, tallo('rama_arbolito', CORTEZA, base=2.0))
    copa = hiedra_capa('copa_arbolito', densidad=0.9, flores=0.04, arriba=1.5)
    redondo(m, 'arbolito', (2.5, 31, -3.5), (5, 4, 5), tallo('hojas_arbolito', HIEDRA, base=2.0, estomas=0.2))
    m.mirar(('cabeza', 1.0))
    a = m.anim('andar', 1.0, bucle=True)
    a.onda('pierna_d', 'r', 0, 30)
    a.onda('pierna_i', 'r', 0, 30, fase=0.5)
    for lado, ld in LADOS:
        a.onda(f'brazo_{ld}', 'r', 0, 4, fase=0.25 if lado > 0 else 0.75)
    a.onda('arbolito', 'r', 2, 5, periodo=0.5)
    a.onda('cuerpo', 'r', 2, 2, periodo=1.0)
    s = m.anim('siempre', 3.0, bucle=True)
    s.onda('arbolito', 'r', 0, 3, periodo=3.0)
    s.onda('flor', 'r', 2, 8, periodo=1.5)
    at = m.anim('ataque', 0.5)
    for lado, ld in LADOS:
        at.rot(f'brazo_{ld}', [(0, 0, 0, 0), (0.15, -25, 0, 0), (0.3, 30, 0, 0), (0.5, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.15, -6, 0, 0), (0.3, 8, 0, 0), (0.5, 0, 0, 0)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.5, -50, 0, 0), (0.85, -92, 0, 0), (1.0, -90, 0, 0)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -10, -2)])
    m.paso = 1.7

    def dib(px, filas, c_):
        for x, f in ((6, 6), (7, 6)):
            px[x, f] = c_('0a120a')
        for x, f in ((9, 6), (10, 6)):
            px[x, f] = c_('f8d84a')
        for x, f in ((5, 3), (8, 2), (11, 4)):
            px[x, f] = c_('d04a94')
        for x in range(5, 11):
            px[x, 9] = c_('1e7676')
    return terminar(m, raiz, 'Zombi Planta', 'Plant Zombie', (('6ea458', '548a44', '3e6e34'), ('1e3a1e', '0a1a0a'), dib),
                    ((1.2, 2.0, 2.1), (0, 1.3, 0)),
                    particulas=(('polen', chispa((232, 196, 26))), ('hoja', esquirla((62, 138, 38))),
                                ('raiz', esquirla((122, 92, 54)))),
                    poses=[('andar', 0.25), ('andar', 0.75), ('ataque', 0.3), ('muerte', 1.0)])


def _flor(tw, th):
    """Una flor de cuatro pétalos al píxel (en una lámina de 4 x 4): los pétalos rosas en cruz, el centro de polen."""
    xs, ys = L._malla(tw, th)
    cx, cy = (tw - 1) / 2, (th - 1) / 2
    dx, dy = np.abs(xs - cx), np.abs(ys - cy)
    petalo = (dx + dy <= max(tw, th) * 0.5) & ~((dx > tw * 0.3) & (dy > th * 0.3))
    centro = (dx < tw * 0.2) & (dy < th * 0.2)
    rgb = L.color_continuo(FLOR, 2.6 + (ys < cy) * 0.6 - (xs > cx) * 0.3)
    rgb = np.where(centro[..., None], L.color_continuo(POLEN, np.full(dx.shape, 3.0)), rgb)
    tex = L._rgba(rgb)
    tex[..., 3] = np.where(petalo, 255, 0)
    return tex, None


MOBS = {}
for _c in COLORES:
    MOBS[f'fauces_{_c}'] = (lambda c: lambda raiz: fauces(raiz, c))(_c)
MOBS['trampa'] = trampa
MOBS['pina'] = pina
MOBS['zombi_planta'] = zombi_planta


def main():
    global CARPETA
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    CARPETA = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
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

"""
Mastodino (DEDsafío 4, la Dungeon de Qumara y el Gulag 1): el gran depredador rojo de dos patas, rehecho desde cero
siguiendo `quiu_ref2/mastodino/ficha.md` (56 imágenes del juego, del libro y de clips). El libro lo describe:
«destruye todo a su paso, impulsando hacia arriba a quienes estén cerca».

Pieza a pieza, como en el juego:
  - cabeza enorme, larga y cuadrada (15 × 12,5 × 27 texels), sin rayas violetas, con reborde de ceja sobre los ojos,
    2 fosas oscuras grandes en la cara delantera, 4 trazos amarillos en 2 filas por costado (con pupilas oscuras entre
    ellos), 2 colmillos de hueso (3 × 5 × 3) colgando en las esquinas delanteras y 2 cuernos blancos en gancho en la
    línea central del techo (poste + barra hacia atrás con hueco debajo y surco gris en marco);
  - mandíbula de hueso en bandeja (13 × 4,5 × 25), suelo granate oscuro con lengua rosa magenta en relieve, dientes de
    arriba cuadrados como teclas de piano (4 delante con hueco doble en el centro y 9 por lado) y dientes de abajo en
    almena;
  - cuello corto y grueso (13 × 13 × 8) y tronco hondo (20 × 23 × 32) con peto crema del mentón al vientre y bandas
    violetas verticales anchas;
  - cola en 3 tramos (14 × 14 × 12, 10 × 10 × 12, 7 × 7 × 11) cortada en cuadrado en la punta, con bandas violetas en
    diagonal y franja crema debajo;
  - fila central de púas planas en escalera curvadas en gancho hacia atrás (base violeta, medio lila y punta blanca);
  - brazos de largo medio en 3 piezas, con 3 ganchos violetas en el canto trasero del antebrazo y 3 garras en bloque
    gris oscuro;
  - patas gruesas en zigzag de 3 tramos con bandas violetas horizontales y 3 dedos con garras en bloque gris oscuro;
  - `construir_montado()` (`mastodino_jinete`): añade la silla de cuero con reborde escalonado, las 2 correas con
    cincha y hebillas grises por costado y el bocado con anillas cuadradas grises en la comisura y riendas.
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import T
from bestiario_hormigas import _azar1
from bestiario_reptiles import caja_en, lamina

ID = 'mastodino'
TAM = 1.25

HUEVO = (
    ('d4703a', 'c05c2c', '8e3a1c'),
    ('5a0cc0', '2e0468'),
    [
        ((7, 2), 'f0e8e4'), ((8, 2), 'dcd2cc'), ((7, 3), 'dcd2cc'),
        ((5, 4), 'ece8f0'), ((6, 4), '9c84c4'), ((5, 5), '5a0cc0'),
        ((9, 6), 'f0b83c'), ((10, 6), '241008'), ((9, 7), 'f0b83c'),
        ((5, 8), '5a0cc0'), ((6, 8), '5a0cc0'), ((5, 9), '5a0cc0'),
        ((8, 9), 'dcd2cc'), ((9, 9), 'dcd2cc'), ((10, 9), 'dcd2cc'),
        ((6, 11), 'd6ccb6'), ((7, 11), 'd6ccb6'), ((8, 11), 'd6ccb6'),
    ],
)


# ======================================================================================================================
#  Colores (paleta.json y apartado 5 de la ficha)
# ======================================================================================================================
def _r(*c):
    return L.rampa(*c)


NARANJA_MASTODINO = _r('7a2c14', 'a0441f', 'b45026', 'c05c2c', 'd4703a')
PARDO_MASTODINO = _r('4e1c0c', '6a2812', '7c3117', '8e3a1c', 'a44a26')
VIOLETA_MASTODINO = _r('2e0468', '40088c', '4e0aa6', '5a0cc0', '6c18d8')
LILA_MASTODINO = _r('584274', '786098', '8a72ae', '9c84c4', 'b89ee0')
PUNTA_MASTODINO = _r('b0a8b8', 'c8c0d0', 'dcd6e2', 'ece8f0', 'faf8fc')
HUESO_MASTODINO = _r('9a8a84', 'b4a8a2', 'c8beb8', 'dcd2cc', 'f0e8e4')
CREMA_MASTODINO = _r('8e826c', 'b0a48a', 'c4b89e', 'd6ccb6', 'e8e0ce')
BOCA_MASTODINO = _r('1c060c', '2a0a14', '441420', '5e1e2c', '742a38')
LENGUA_MASTODINO = _r('602038', '82304e', '9a3c62', 'b04a78', 'c8649a')
GARRA_MASTODINO = _r('1c1815', '2c2622', '3c342e', '4a4038', '625649')
CUERO_MASTODINO = _r('2c1c0e', '3e2a17', '4c351f', '5a4028', '735a36')
CORREA_MASTODINO = _r('160e08', '22160c', '2e1f12', '3a2818', '4c3622')
METAL_MASTODINO = _r('22180f', '5c5655', '746e6d', '8a8484', 'b2acaa')

COLORES_CABEZA_MASTODINO = {
    'n': B.H('c05c2c'),   # naranja base
    'L': B.H('d4703a'),   # naranja claro (canto de ceja y dorso)
    'p': B.H('8e3a1c'),   # rojo pardo de los costados y bajo la ceja
    'o': B.H('6a2812'),   # sombra parda alrededor del ojo y de las fosas
    'f': B.H('1e0c08'),   # hueco de las fosas del hocico
    'b': B.H('4a1a0c'),   # borde de las fosas
    'y': B.H('f0b83c'),   # trazos amarillos del ojo
    'a': B.H('c88e1e'),   # amarillo oscuro del ojo
    'k': B.H('241008'),   # pupila entre los trazos
}

# Cara delantera del hocico (15 de ancho × 12 de alto): dos fosas oscuras grandes (4 × 5) en la mitad de abajo,
# separadas por 3-4 texels de piel, con sombra parda alrededor.
MAPA_FRENTE_MASTODINO = [
    'ppLLLLLLLLLLLpp',
    'pnnnnnnnnnnnnnp',
    'pnnnnnnnnnnnnnp',
    'ppnnnnnnnnnnnpp',
    'ppbbbpnnnppbbbp',
    'pbfffbpoppbfffb',
    'pbfffbpoppbfffb',
    'pbfffbpoppbfffb',
    'pbfffbpoppbfffb',
    'pbfffbpoppbfffb',
    'ppbbbpnnnppbbbp',
    'ppoooonnnoooopp',
]


def _mapa_lado_mastodino():
    """El costado de la cabeza (22 de largo desde la nuca col=0 hasta el hocico col=21, por 12 de alto):
      - arriba y delante, el naranja; en los costados y bajo el reborde de la ceja, zonas de rojo pardo ('p', 'o');
      - a 2/3 del largo desde el hocico (columnas 5 a 11 desde la nuca) y en la mitad de abajo (filas 5 a 9), los
        4 trazos amarillos en 2 filas de 2 con la pupila 'k' entre ellos, la fila de abajo 1 texel más adelantada."""
    W, H_ = 22, 12
    g = [['n'] * W for _ in range(H_)]
    for r in range(H_):
        for c in range(W):
            if r == 0:
                g[r][c] = 'L'
            elif 3 <= r <= 9 and 3 <= c <= 19:
                g[r][c] = 'p'
            if 4 <= r <= 9 and 4 <= c <= 13:
                g[r][c] = 'o'
    # Reborde claro encima de la zona del ojo (fila 3, columnas 4..14)
    for c in range(4, 15):
        g[3][c] = 'L'
        g[4][c] = 'o'
    # Fila superior del ojo (filas 5-6, columnas 5..9): trazo [5,6], pupila [7], trazo [8,9]
    g[5][5] = 'a'
    g[5][9] = 'a'
    g[6][5] = 'y'
    g[6][6] = 'y'
    g[6][7] = 'k'
    g[6][8] = 'y'
    g[6][9] = 'y'
    # Fila inferior del ojo, 1 texel más adelantada (filas 8-9, columnas 6..10): trazo [6,7], pupila [8], trazo [9,10]
    g[8][6] = 'y'
    g[8][7] = 'y'
    g[8][8] = 'k'
    g[8][9] = 'y'
    g[8][10] = 'y'
    g[9][7] = 'a'
    g[9][10] = 'a'
    # Sombra delante hacia las fosas
    for r in range(5, 11):
        for c in range(17, 21):
            g[r][c] = 'p' if c < 19 else 'o'
    return [''.join(f) for f in g]


MAPA_LADO_MASTODINO = _mapa_lado_mastodino()

POSTURA_MASTODINO = dict(
    inc=-22.0,          # tronco inclinado, hombros altos como en el icono del libro y Qumara
    cuello=-18.0,       # cuello corto y grueso que sube del pecho
    cabeza=10.0,        # cabeza ligeramente inclinada hacia abajo
    abre=24.0,          # mandíbula entreabierta mostrando dientes y lengua
    cola1=3.0,          # cola recta hacia atrás
    cola2=2.0,
    cola3=1.0,
    muslo=14.0,         # patas gruesas en zigzag
    espinilla=-34.0,
    metatarso=44.0,
    brazo=34.0,         # brazos de largo medio colgando bajo el pecho hacia delante
    antebrazo=84.0,
    mano=62.0,
    dedos=0.0,
)


# ======================================================================================================================
#  Pintores
# ======================================================================================================================
def _malla(tw, th):
    return L._malla(tw, th)


def _limpiar(mk):
    v = np.zeros(mk.shape, int)
    v[1:, :] += mk[:-1, :]
    v[:-1, :] += mk[1:, :]
    v[:, 1:] += mk[:, :-1]
    v[:, :-1] += mk[:, 1:]
    return mk & (v > 0)


def _manchas_bloque(xs, ys, s, claro=0.68, oscuro=0.30):
    """Manchas de bloque de 2 a 4 píxeles, sin píxeles sueltos."""
    n = (0.5 * _azar1((xs + 1) // 3, (ys + 2) // 3, s + 5)
         + 0.5 * _azar1(xs // 2, ys // 2, s + 11))
    cl = _limpiar(n > claro)
    os_ = _limpiar(n < oscuro)
    return cl.astype(int) - os_.astype(int)


def _z_delante(cara, xs, ys, tw, th):
    if cara == 'izq':
        return tw - 1 - xs
    if cara == 'der':
        return xs
    if cara == 'arriba':
        return th - 1 - ys
    if cara == 'abajo':
        return ys
    return None


def piel_mastodino(nombre, bandas_vert=None, bandas_horiz=None, bandas_diag=False, crema=0.0,
                   crema_caras=('abajo',), peto_diag=False, base=3.0, semilla=0):
    """Piel naranja rojiza en manchas de bloque limpias, con bandas violetas saturadas:
      - bandas_vert: (paso, ancho, alto_frac) verticales desde el lomo hasta media altura del costado;
      - bandas_horiz: (paso, ancho, cuantas) horizontales en muslos, espinillas y brazos;
      - bandas_diag: bandas violetas en diagonal para los 3 tramos de la cola;
      - crema: franja crema inferior con escalones de 1-2 texels y caras enteras en crema_caras."""
    def fn(tw, th, c, s):
        s = s + semilla
        xs, ys = _malla(tw, th)
        v = np.full((th, tw), base) + _manchas_bloque(xs, ys, s) * 0.75
        if c == 'arriba':
            v = v + 0.3
        violeta = np.zeros((th, tw), bool)
        zf = _z_delante(c, xs, ys, tw, th)
        lado = c in ('izq', 'der')
        if bandas_vert is not None and zf is not None and c != 'abajo':
            paso, an, h_frac = bandas_vert
            if lado:
                fin = int(round(th * h_frac))
                for k, z0 in enumerate(range(2, tw - 1, paso)):
                    fin_k = fin + (2 if k % 2 == 0 else -1)
                    b1 = (zf >= z0) & (zf < z0 + an) & (ys < fin_k - 2)
                    # Algunas partidas en cuadros de 2×2 abajo
                    b2 = (zf >= z0 + (k % 2)) & (zf < z0 + (k % 2) + max(2, an - 1)) & (ys >= fin_k - 1) & (ys < fin_k + 2)
                    violeta |= b1 | b2
            elif c == 'arriba':
                for z0 in range(2, th - 1, paso):
                    violeta |= (zf >= z0) & (zf < z0 + an)
        if bandas_diag and zf is not None and c != 'abajo':
            paso, an = 6, 2
            if lado:
                # Bajan en diagonal hacia delante desde el lomo
                d = (zf - ys // 2) % paso
                violeta |= (d < an) & (ys < int(th * 0.78))
            elif c == 'arriba':
                # Vistas desde arriba forman uves que apuntan a la punta
                dx = np.abs(xs - tw // 2)
                d = (zf + dx // 2) % paso
                violeta |= d < an
        if bandas_horiz is not None and c in ('izq', 'der', 'frente', 'atras'):
            paso, an, cuantas = bandas_horiz
            for k, y0 in enumerate(range(3, th - 2, paso)):
                if k >= cuantas:
                    break
                violeta |= (ys >= y0) & (ys < y0 + an) & (xs >= 1) & (xs < tw - 1)
        crema_mk = np.zeros((th, tw), bool)
        if c in crema_caras:
            crema_mk[...] = True
        elif crema > 0 and c in ('izq', 'der', 'frente', 'atras'):
            h0 = int(round(th * (1.0 - crema)))
            escalon = ((xs // 4) % 2)
            crema_mk = ys >= (h0 + escalon)
            if peto_diag and lado and zf is not None:
                crema_mk |= (zf < 7) & (ys >= (h0 - (7 - zf) * 2))
        violeta &= ~crema_mk
        rgb = L.color_continuo(NARANJA_MASTODINO, v)
        vv = 3.0 + _manchas_bloque(xs, ys, s + 41) * 0.45 + 0.25 * (c == 'arriba')
        rgb = np.where(violeta[..., None], L.color_continuo(VIOLETA_MASTODINO, vv), rgb)
        cv = 3.0 + _manchas_bloque(xs, ys, s + 73) * 0.45 - 0.2 * (c == 'abajo')
        rgb = np.where(crema_mk[..., None], L.color_continuo(CREMA_MASTODINO, cv), rgb)
        return L._rgba(rgb), None
    return B.Pintor(nombre, fn)


def cabeza_mastodino(nombre):
    """Piel de la cabeza (sin rayas violetas): naranja rojizo con zonas de rojo pardo en los costados, los 4 trazos
    amarillos del ojo y las 2 fosas oscuras en la cara delantera."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        if c == 'abajo':
            v = 2.8 + _manchas_bloque(xs, ys, s + 3) * 0.35
            return L._rgba(L.color_continuo(BOCA_MASTODINO, v)), None
        v = 3.0 + _manchas_bloque(xs, ys, s + 7) * 0.5 + 0.3 * (c == 'arriba')
        rgb = L.color_continuo(NARANJA_MASTODINO, v)
        if c in ('izq', 'der'):
            mp = MAPA_LADO_MASTODINO
            H_, W_ = len(mp), len(mp[0])
            zt = (xs + 0.5) / tw * W_
            if c == 'der':
                zt = W_ - zt
            ii = np.clip(zt.astype(int), 0, W_ - 1)
            jj = np.clip(((ys + 0.5) / th * H_).astype(int), 0, H_ - 1)
            for j in range(H_):
                for i, ch in enumerate(mp[j]):
                    if ch in COLORES_CABEZA_MASTODINO:
                        rgb[(ii == i) & (jj == j)] = COLORES_CABEZA_MASTODINO[ch]
        elif c == 'frente':
            mp = MAPA_FRENTE_MASTODINO
            H_, W_ = len(mp), len(mp[0])
            ii = np.clip(((xs + 0.5) / tw * W_).astype(int), 0, W_ - 1)
            jj = np.clip(((ys + 0.5) / th * H_).astype(int), 0, H_ - 1)
            for j in range(H_):
                for i, ch in enumerate(mp[j]):
                    if ch in COLORES_CABEZA_MASTODINO:
                        rgb[(ii == i) & (jj == j)] = COLORES_CABEZA_MASTODINO[ch]
        return L._rgba(rgb), None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def hueso_surco_mastodino(nombre):
    """Hueso blanco cálido con el techo más claro y un surco gris de 1 texel en forma de marco por dentro del borde."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        v = np.full((th, tw), 3.1) + _manchas_bloque(xs, ys, s + 9) * 0.25
        if c == 'arriba':
            v[...] = 3.9
        elif c == 'abajo':
            v[...] = 1.8
        else:
            marco = (((xs == 1) | (xs == tw - 2)) & (ys >= 1) & (ys <= th - 2)) | (
                ((ys == 1) | (ys == th - 2)) & (xs >= 1) & (xs <= tw - 2)
            )
            v = np.where(marco, 0.4, v)
        return L._rgba(L.color_continuo(HUESO_MASTODINO, v)), None
    return B.Pintor(nombre, fn)


def mandibula_mastodino(nombre, canto_t, ancho_t, largo_t):
    """Bandeja de hueso blanco: por fuera hueso con surco suave; por arriba, el suelo granate con paredes de hueso."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        if c == 'arriba':
            xt = (xs + 0.5) / tw * ancho_t
            zt = (th - (ys + 0.5)) / th * largo_t
            pared = (xt < canto_t) | (xt > ancho_t - canto_t) | (zt > largo_t - canto_t)
            rgb = L.color_continuo(BOCA_MASTODINO, 2.8 + _manchas_bloque(xs, ys, s + 5) * 0.3)
            rgb = np.where(pared[..., None], L.color_continuo(HUESO_MASTODINO, np.full((th, tw), 3.4)), rgb)
            return L._rgba(rgb), None
        v = 3.0 + _manchas_bloque(xs, ys, s + 13) * 0.3 - 0.4 * (c == 'abajo')
        if c in ('izq', 'der', 'frente'):
            v = np.where(ys == 0, 3.8, v)
        return L._rgba(L.color_continuo(HUESO_MASTODINO, v)), None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def lengua_mastodino(nombre):
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        v = np.where(np.abs((xs + 0.5) - tw / 2) <= 1.0, 3.8, 2.9) if c == 'arriba' else np.full((th, tw), 2.0)
        return L._rgba(L.color_continuo(LENGUA_MASTODINO, v)), None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def dientes_arriba_mastodino(nombre, ancho_t, largo_t, alto_t):
    """Dientes de arriba en 2.ª capa: delante 4 dientes de 1×2 con hueco de 1 y hueco doble en el centro; a cada lado,
    9 cuadrados blancos de 1 texel con huecos de 1 como teclas de piano."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c in ('arriba', 'abajo', 'atras'):
            return tex, None
        yt = (ys + 0.5) / th * alto_t - 0.4
        mk = np.zeros((th, tw), bool)
        if c == 'frente':
            xt = (xs + 0.5) / tw * ancho_t
            # 4 dientes delante: diente, hueco, diente, hueco doble, diente, hueco, diente
            for x0 in (3.2, 5.2, ancho_t - 6.2, ancho_t - 4.2):
                mk |= (xt >= x0) & (xt < x0 + 1.1) & (yt >= 0) & (yt < 2.1)
        else:
            zt = (xs + 0.5) / tw * largo_t
            if c == 'izq':
                zt = largo_t - zt
            for k in range(9):
                z0 = 2.8 + k * 2.0
                mk |= (zt >= z0) & (zt < z0 + 1.05) & (yt >= 0) & (yt < 1.6)
        v = np.where(yt > 1.0, 3.8, 3.2)
        tex[..., :3] = np.round(L.color_continuo(HUESO_MASTODINO, v)).astype(np.uint8)
        tex[..., 3] = np.where(mk, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def dientes_abajo_mastodino(nombre, ancho_t, largo_t, alto_t):
    """Dientes de abajo como almenas de 1 texel con huecos de 1: 6 en la punta y 9 por lado."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        if c in ('arriba', 'abajo', 'atras'):
            return tex, None
        yt = (th - (ys + 0.5)) / th * alto_t
        mk = np.zeros((th, tw), bool)
        if c == 'frente':
            xt = (xs + 0.5) / tw * ancho_t
            for k in range(6):
                x0 = 1.2 + k * 1.9
                mk |= (xt >= x0) & (xt < x0 + 1.0) & (yt < 1.5)
        else:
            zt = (xs + 0.5) / tw * largo_t
            if c == 'izq':
                zt = largo_t - zt
            for k in range(9):
                z0 = 1.5 + k * 2.0
                mk |= (zt >= z0) & (zt < z0 + 1.0) & (yt < 1.5)
        tex[..., :3] = np.round(L.color_continuo(HUESO_MASTODINO, np.full((th, tw), 3.3))).astype(np.uint8)
        tex[..., 3] = np.where(mk, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def pua_lomo_mastodino(nombre):
    """Lámina plana con el borde en escalera que sube del lomo y se curva hacia atrás en gancho, en tres zonas de color:
    base violeta (#5a0cc0), medio lila (#9c84c4) y punta blanca fría (#ece8f0)."""
    mapa = [
        '..bbbbb...',
        '.bbbbbbbb.',
        '.lllbbbbbb',
        'llllllbbb.',
        'llllllll..',
        'vvvlllll..',
        'vvvvvlll..',
        'vvvvvvv...',
        'vvvvvvv...',
        'vvvvvvv...',
    ]

    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        H_, W_ = len(mapa), len(mapa[0])
        ii = np.clip(((xs + 0.5) / tw * W_).astype(int), 0, W_ - 1)
        jj = np.clip(((ys + 0.5) / th * H_).astype(int), 0, H_ - 1)
        for j in range(H_):
            for i, ch in enumerate(mapa[j]):
                if ch == '.':
                    continue
                mk = (ii == i) & (jj == j)
                if ch == 'v':
                    col = L.color_continuo(VIOLETA_MASTODINO, np.array([3.2]))[0]
                elif ch == 'l':
                    col = L.color_continuo(LILA_MASTODINO, np.array([3.1]))[0]
                else:
                    col = L.color_continuo(PUNTA_MASTODINO, np.array([3.3]))[0]
                tex[mk, :3] = np.round(col).astype(np.uint8)
                tex[mk, 3] = 255
        return tex, None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def gancho_brazo_mastodino(nombre):
    """Gancho violeta del canto trasero del antebrazo, con borde lila de 1 texel y sin punta blanca."""
    mapa = [
        '.llll.',
        'lvvvvl',
        'lvvvv.',
        '.lvvv.',
        '..lvv.',
        '...lv.',
    ]

    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        tex = np.zeros((th, tw, 4), np.uint8)
        H_, W_ = len(mapa), len(mapa[0])
        ii = np.clip(((xs + 0.5) / tw * W_).astype(int), 0, W_ - 1)
        jj = np.clip(((ys + 0.5) / th * H_).astype(int), 0, H_ - 1)
        for j in range(H_):
            for i, ch in enumerate(mapa[j]):
                if ch == '.':
                    continue
                mk = (ii == i) & (jj == j)
                col = L.color_continuo(VIOLETA_MASTODINO if ch == 'v' else LILA_MASTODINO, np.array([3.0]))[0]
                tex[mk, :3] = np.round(col).astype(np.uint8)
                tex[mk, 3] = 255
        return tex, None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def garra_mastodino(nombre):
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        v = np.full((th, tw), 2.8)
        if c == 'arriba':
            v[...] = 3.7
        elif c == 'abajo':
            v[...] = 1.5
        else:
            v = v + (ys == 0) * 0.9 - (ys == th - 1) * 0.5
        return L._rgba(L.color_continuo(GARRA_MASTODINO, v)), None
    return B.fino(B.Pintor(nombre, fn), 0.5)


def silla_mastodino(nombre):
    """Asiento de cuero pardo con reborde escalonado más claro (#735a36) y centro hundido (#5a4028)."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        v = np.full((th, tw), 2.8) + _manchas_bloque(xs, ys, s + 19) * 0.25
        if c == 'arriba':
            borde = (xs < 2) | (xs >= tw - 2) | (ys < 2) | (ys >= th - 2)
            v = np.where(borde, 3.9, 2.3)
        elif c in ('izq', 'der', 'frente', 'atras'):
            v = np.where(ys == 0, 3.8, 2.5)
        return L._rgba(L.color_continuo(CUERO_MASTODINO, v)), None
    return B.Pintor(nombre, fn)


def liso_mastodino(nombre, R, base=3.0):
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        v = np.full((th, tw), base) + 0.3 * (c == 'arriba') - 0.3 * (c == 'abajo')
        return L._rgba(L.color_continuo(R, v)), None
    return B.Pintor(nombre, fn)


def anilla_mastodino(nombre):
    """Anilla cuadrada gris de 5×5 con hueco de 3×3 (o hebilla de 4×4 con hueco oscuro)."""
    def fn(tw, th, c, s):
        xs, ys = _malla(tw, th)
        borde = (xs == 0) | (xs == tw - 1) | (ys == 0) | (ys == th - 1)
        v = np.where(borde, 3.2, 0.2)
        return L._rgba(L.color_continuo(METAL_MASTODINO, v)), None
    return B.Pintor(nombre, fn)


# ======================================================================================================================
#  Geometría
# ======================================================================================================================
def _rx(a):
    return B.girar((a, 0, 0))


def _pt(M, p):
    return (M @ np.array((p[0], p[1], p[2], 1.0)))[:3]


def _colgar(m, parte, M, tam, pint, arriba=0.0, caras=None):
    w, h, d = tam
    caja_en(m, parte, M, (0.0, arriba - h / 2.0, 0.0), (w, h, d), pint, caras)


def _sagital(x, y, z, rx=0.0):
    return T(x, y, z) @ B.girar((rx, -90, 0))


def _construir_base(montado=False, con_silla=False):
    m = B.Modelo('mastodino_jinete' if montado else ID, K=2, ancho=256)
    m.escala = 1.0

    # Pintores
    tronco_p = piel_mastodino('tronco_mastodino', bandas_vert=(5, 3, 0.55), crema=0.24,
                              crema_caras=('abajo', 'frente'), peto_diag=True, semilla=1)
    cadera_p = piel_mastodino('cadera_mastodino', bandas_vert=(5, 3, 0.55), crema=0.20,
                              crema_caras=('abajo',), semilla=3)
    cuello_p = piel_mastodino('cuello_mastodino', bandas_vert=(4, 2, 0.45), crema=0.45,
                              crema_caras=('abajo', 'frente'), peto_diag=True, semilla=5)
    cola_p = piel_mastodino('cola_mastodino', bandas_diag=True, crema=0.22, crema_caras=('abajo',), semilla=7)
    muslo_p = piel_mastodino('muslo_mastodino', bandas_horiz=(4, 2, 4), semilla=9)
    espinilla_p = piel_mastodino('espinilla_mastodino', bandas_horiz=(4, 2, 3), semilla=11)
    brazo_p = piel_mastodino('brazo_mastodino', bandas_horiz=(5, 2, 2), semilla=13)
    naranja_p = piel_mastodino('naranja_mastodino', semilla=15)
    cabeza_p = cabeza_mastodino('cabeza_mastodino')
    ceja_p = liso_mastodino('ceja_mastodino', PARDO_MASTODINO, base=3.4)
    hueso_p = hueso_surco_mastodino('hueso_mastodino')
    colmillo_p = liso_mastodino('colmillo_mastodino', HUESO_MASTODINO, base=3.8)
    garra_p = garra_mastodino('garra_mastodino')
    pua_p = pua_lomo_mastodino('pua_mastodino')
    gancho_p = gancho_brazo_mastodino('gancho_brazo_mastodino')

    P = POSTURA_MASTODINO

    def _dir(a):
        return np.array((0.0, -math.cos(math.radians(a)), math.sin(math.radians(a))))

    LM, LE, LT = 16.0, 13.5, 8.0
    caida = -(LM * _dir(P['muslo']) + LE * _dir(P['espinilla']) + LT * _dir(P['metatarso']))[1]
    H0 = np.array((0.0, 2.5 + caida, -1.5))

    # ---------------- Tronco y cadera ----------------
    m.parte('cuerpo', None, tuple(H0))
    Mt = T(*H0) @ _rx(P['inc'])
    caja_en(m, 'cuerpo', Mt, (0, -2.5, 17.5), (20, 23, 29), tronco_p)
    caja_en(m, 'cuerpo', Mt, (0, -3.5, -3.5), (17, 20, 16), cadera_p)

    # ---------------- Cuello corto y grueso ----------------
    N0 = _pt(Mt, (0, 2.0, 29.5))
    m.parte('cuello', 'cuerpo', tuple(N0))
    Mn = T(*N0) @ _rx(P['cuello'])
    caja_en(m, 'cuello', Mn, (0, -0.5, 3.5), (13, 14, 8), cuello_p)

    # ---------------- Cabeza enorme, larga y cuadrada (15 × 12.0 × 22) ----------------
    C0 = _pt(Mn, (0, -4.5, 5.5))
    m.parte('cabeza', 'cuello', tuple(C0))
    Mc = T(*C0) @ _rx(P['cabeza'])
    caja_en(m, 'cabeza', Mc, (0, 6.0, 9.5), (15, 12.0, 22), cabeza_p)
    # Reborde de la ceja encima de los ojos (sobresale a los lados en la mitad de arriba)
    caja_en(m, 'cabeza', Mc, (0, 9.0, 7.5), (16.2, 2.0, 12.0), ceja_p)

    # Los 2 cuernos de hueso en gancho en la línea del medio, uno detrás de otro:
    # Cuerno de delante (mayor, a ~28% desde el hocico -> z=14.5): poste 4×5.5×4 + barra 4×2.2×6.5 hacia atrás
    caja_en(m, 'cabeza', Mc, (0, 12.0 + 2.75, 14.5), (4.0, 5.5, 4.0), hueso_p)
    caja_en(m, 'cabeza', Mc, (0, 12.0 + 5.5 + 1.1, 13.0), (4.0, 2.2, 6.5), hueso_p)
    # Cuerno de detrás (sobre los ojos -> z=6.5): poste 3.4×4.5×3.4 + barra 3.4×1.8×5.5 hacia atrás
    caja_en(m, 'cabeza', Mc, (0, 12.0 + 2.25, 6.5), (3.4, 4.5, 3.4), hueso_p)
    caja_en(m, 'cabeza', Mc, (0, 12.0 + 4.5 + 0.9, 5.2), (3.4, 1.8, 5.5), hueso_p)

    # Los 2 colmillos en las esquinas de delante de la cabeza (3 × 4.8 × 3), colgando por fuera de la mandíbula
    for lado in (1, -1):
        caja_en(m, 'cabeza', Mc @ T(lado * 6.4, -2.0, 18.8) @ _rx(-10.0), (0, 0, 0), (3.0, 4.8, 3.0), colmillo_p)

    # Dientes de arriba (2.ª capa)
    caja_en(m, 'cabeza', Mc, (0, -1.1, 10.5), (15.4, 3.0, 20.0),
            dientes_arriba_mastodino('dientes_arriba_mastodino', 15.4, 20.0, 3.0))

    # ---------------- Mandíbula en bandeja de hueso (13 × 4.5 × 20) ----------------
    G = _pt(Mc, (0, 0.0, 1.0))
    m.parte('mandibula', 'cabeza', tuple(G))
    Mj = T(*G) @ _rx(P['cabeza'] + P['abre'])
    caja_en(m, 'mandibula', Mj, (0, -2.25, 9.5), (13.0, 4.5, 19.5),
            mandibula_mastodino('mandibula_mastodino', 1.2, 13.0, 19.5))
    caja_en(m, 'mandibula', Mj, (0, 0.4, 9.0), (5.5, 1.0, 14.0), lengua_mastodino('lengua_mastodino'))
    caja_en(m, 'mandibula', Mj, (0, 0.9, 9.6), (11.6, 1.8, 17.5),
            dientes_abajo_mastodino('dientes_abajo_mastodino', 11.6, 17.5, 1.8))

    # ---------------- Cola en 3 tramos, cortada en cuadrado ----------------
    C1 = _pt(Mt, (0, -1.0, -11.0))
    m.parte('cola', 'cuerpo', tuple(C1))
    Mk1 = T(*C1) @ _rx(P['cola1'])
    caja_en(m, 'cola', Mk1, (0, 0.0, -6.0), (14.0, 14.0, 12.0), cola_p)

    C2 = _pt(Mk1, (0, -0.5, -11.5))
    m.parte('cola2', 'cola', tuple(C2))
    Mk2 = T(*C2) @ _rx(P['cola2'])
    caja_en(m, 'cola2', Mk2, (0, 0.0, -6.0), (10.0, 10.0, 12.0), cola_p)

    C3 = _pt(Mk2, (0, -0.5, -11.5))
    m.parte('cola3', 'cola2', tuple(C3))
    Mk3 = T(*C3) @ _rx(P['cola3'])
    caja_en(m, 'cola3', Mk3, (0, 0.0, -5.5), (7.0, 7.0, 11.0), cola_p)

    # ---------------- Fila de púas del cuello a la punta de la cola ----------------
    # En el cuello (1)
    lamina(m, 'cuello', Mn @ _sagital(0, 6.5, 4.0), 4.5, 6.5, pua_p)
    # En el tronco y la cadera (5; en el montado se omiten las 2 bajo el asiento)
    puas_tronco = ((26.0, 9.0, 5.0, 8.0), (19.0, 9.0, 5.2, 8.2), (11.5, 9.0, 5.0, 7.8),
                   (4.0, 9.0, 5.0, 7.6), (-4.0, 6.5, 4.8, 7.2))
    for z_p, y_p, w_p, h_p in puas_tronco:
        if montado and 6.0 <= z_p <= 20.0:
            continue
        lamina(m, 'cuerpo', Mt @ _sagital(0, y_p, z_p), w_p, h_p, pua_p)
    # En la cola (6)
    for z_p, w_p, h_p in ((-3.5, 4.5, 6.6), (-9.0, 4.2, 6.0)):
        lamina(m, 'cola', Mk1 @ _sagital(0, 7.0, z_p), w_p, h_p, pua_p)
    for z_p, w_p, h_p in ((-3.5, 3.8, 5.2), (-9.0, 3.5, 4.6)):
        lamina(m, 'cola2', Mk2 @ _sagital(0, 5.0, z_p), w_p, h_p, pua_p)
    for z_p, w_p, h_p in ((-3.0, 3.2, 4.0), (-8.0, 2.8, 3.4)):
        lamina(m, 'cola3', Mk3 @ _sagital(0, 3.5, z_p), w_p, h_p, pua_p)

    # ---------------- Patas gruesas en zigzag ----------------
    for lado, ld in ((1, 'i'), (-1, 'd')):
        x = lado * 8.0
        cad = np.array((x, H0[1], H0[2]))
        rod = cad + LM * _dir(P['muslo'])
        tob = rod + LE * _dir(P['espinilla'])
        bol = tob + LT * _dir(P['metatarso'])
        n = m.parte(f'pierna_{ld}', 'cuerpo', tuple(cad))
        _colgar(m, n, T(*cad) @ _rx(-P['muslo']), (10.5, 19.5, 11.5), muslo_p, arriba=4.0)
        n2 = m.parte(f'cana_{ld}', n, tuple(rod))
        _colgar(m, n2, T(*rod) @ _rx(-P['espinilla']), (8.0, 15.0, 8.0), espinilla_p, arriba=2.4)
        n3 = m.parte(f'pie_{ld}', n2, tuple(tob))
        _colgar(m, n3, T(*tob) @ _rx(-P['metatarso']), (7.0, 10.0, 7.0), naranja_p, arriba=1.5)
        n4 = m.parte(f'dedos_{ld}', n3, (x, 2.4, bol[2]))
        for k, giro in ((-1, -15.0), (0, 0.0), (1, 15.0)):
            Md = T(x + k * 2.2, 1.0, bol[2] - 0.8) @ B.girar((0, giro, 0))
            caja_en(m, n4, Md, (0, 0, 2.6), (2.0, 2.0, 5.6), naranja_p)
            caja_en(m, n4, Md @ T(0, -0.1, 6.2) @ _rx(12.0), (0, 0, 0), (2.0, 2.2, 3.0), garra_p)

    # ---------------- Brazos de largo medio con 3 ganchos en el antebrazo y 3 garras en bloque ----------------
    for lado, ld in ((1, 'i'), (-1, 'd')):
        hom = _pt(Mt, (lado * 10.2, -11.0, 26.5))
        n = m.parte(f'brazo_{ld}', 'cuerpo', tuple(hom))
        Mb = T(*hom) @ _rx(-P['brazo'])
        _colgar(m, n, Mb, (5.0, 12.5, 5.0), brazo_p, arriba=1.4)
        codo = hom + 10.5 * _dir(P['brazo'])
        n2 = m.parte(f'antebrazo_{ld}', n, tuple(codo))
        Ma = T(*codo) @ _rx(-P['antebrazo'])
        _colgar(m, n2, Ma, (4.5, 11.5, 4.5), naranja_p, arriba=1.4)
        # 3 ganchos violetas en el canto de atrás del antebrazo
        for y_g in (-2.5, -5.5, -8.5):
            lamina(m, n2, Ma @ T(0, y_g, -3.6) @ B.girar((0, -90, 0)), 3.4, 3.8, gancho_p)
        mun = codo + 9.8 * _dir(P['antebrazo'])
        n3 = m.parte(f'mano_{ld}', n2, tuple(mun))
        for k in (-1, 0, 1):
            Md = T(mun[0] + k * 1.8, mun[1], mun[2]) @ B.girar((0, 0, -k * 6.0)) @ _rx(-P['mano'])
            _colgar(m, n3, Md, (1.6, 4.2, 2.0), naranja_p, arriba=0.5)
            caja_en(m, n3, Md @ T(0, -3.8, 0.2) @ _rx(32.0), (0, -1.2, 0.2), (1.8, 3.2, 2.4), garra_p)

    # ---------------- Arreos del Mastodino montado ----------------
    if montado or con_silla:
        silla_p = silla_mastodino('silla_mastodino')
        correa_p = liso_mastodino('correa_mastodino', CORREA_MASTODINO, base=2.6)
        anilla_p = anilla_mastodino('anilla_mastodino')
        metal_p = liso_mastodino('metal_mastodino', METAL_MASTODINO, base=3.0)
        parte_silla = 'silla' if con_silla else 'cuerpo'
        if con_silla:
            m.parte('silla', 'cuerpo', tuple(H0))
        # Asiento de cuero (14 × 3 × 12) delante de la cadera
        caja_en(m, parte_silla, Mt, (0, 9.8, 13.0), (14.5, 3.0, 12.5), silla_p)
        # 2 correas verticales por costado + cincha horizontal + 2 hebillas grises por costado
        for z_c in (8.5, 17.5):
            caja_en(m, parte_silla, Mt, (0, -1.5, z_c), (20.6, 21.0, 2.0), correa_p)
        caja_en(m, parte_silla, Mt, (0, 2.5, 13.0), (20.8, 2.0, 13.0), correa_p)
        for lado in (1, -1):
            for z_c in (8.5, 17.5):
                caja_en(m, parte_silla, Mt, (lado * 10.3, 2.5, z_c), (1.0, 4.0, 4.0), anilla_p)
        if montado:
            # Bocado en la comisura: barra corta + anilla cuadrada 5×5 + rienda hacia la silla
            for lado in (1, -1):
                caja_en(m, 'cabeza', Mc, (lado * 8.8, 1.5, 3.0), (3.2, 1.5, 1.5), metal_p)
                caja_en(m, 'cabeza', Mc, (lado * 10.2, 1.5, 3.0), (1.0, 5.0, 5.0), anilla_p)
                caja_en(m, 'cabeza', Mc @ _rx(-12.0), (lado * 9.8, 3.5, -5.0), (1.2, 1.5, 15.0), correa_p)

    m.mirar(('cabeza', 0.6), ('cuello', 0.3))
    anims_mastodino(m)
    return m


def construir(con_silla=False):
    return _construir_base(montado=False, con_silla=con_silla)


def construir_montado():
    return _construir_base(montado=True)


# ======================================================================================================================
#  Animaciones serias de terópodo pesado (con cinemática de patas y apoyo en el suelo)
# ======================================================================================================================
LM_MASTODINO, LE_MASTODINO, LT_MASTODINO = 16.0, 13.5, 8.0
PARTES_POSE_MASTODINO = ('cuerpo', 'cuello', 'cabeza', 'mandibula', 'cola', 'cola2', 'cola3',
                         'pierna_i', 'cana_i', 'pie_i', 'dedos_i', 'pierna_d', 'cana_d', 'pie_d', 'dedos_d',
                         'brazo_i', 'antebrazo_i', 'mano_i', 'brazo_d', 'antebrazo_d', 'mano_d')


def _pierna_mastodino(a1, a2, a3):
    r = math.radians
    y = LM_MASTODINO * math.cos(r(a1)) + LE_MASTODINO * math.cos(r(a2)) + LT_MASTODINO * math.cos(r(a3))
    z = LM_MASTODINO * math.sin(r(a1)) + LE_MASTODINO * math.sin(r(a2)) + LT_MASTODINO * math.sin(r(a3))
    return y, z


def pose_mastodino(destino):
    R = POSTURA_MASTODINO

    def v(k, ld=None):
        if ld and f'{k}_{ld}' in destino:
            return destino[f'{k}_{ld}']
        return destino.get(k, R.get(k, 0.0))
    rot = {}
    dc = v('inc') - R['inc']
    rot['cuerpo'] = dc
    rot['cuello'] = v('cuello') - R['cuello'] - dc
    rot['cabeza'] = (v('cabeza') - R['cabeza']) - (v('cuello') - R['cuello'])
    rot['mandibula'] = v('abre') - R['abre']
    rot['cola'] = v('cola1') - R['cola1'] - dc
    rot['cola2'] = (v('cola2') - R['cola2']) - (v('cola1') - R['cola1'])
    rot['cola3'] = (v('cola3') - R['cola3']) - (v('cola2') - R['cola2'])
    patas = []
    for ld in ('i', 'd'):
        dp = R['muslo'] - v('muslo', ld) - dc
        dk = R['espinilla'] - v('espinilla', ld) - dc - dp
        df = R['metatarso'] - v('metatarso', ld) - dc - dp - dk
        rot[f'pierna_{ld}'], rot[f'cana_{ld}'], rot[f'pie_{ld}'] = dp, dk, df
        rot[f'dedos_{ld}'] = v('metatarso', ld) - R['metatarso'] + v('dedos', ld)
        db = R['brazo'] - v('brazo', ld) - dc
        da = R['antebrazo'] - v('antebrazo', ld) - dc - db
        dm = R['mano'] - v('mano', ld) - dc - db - da
        rot[f'brazo_{ld}'], rot[f'antebrazo_{ld}'], rot[f'mano_{ld}'] = db, da, dm
        patas.append(_pierna_mastodino(v('muslo', ld), v('espinilla', ld), v('metatarso', ld)))
    y0, _ = _pierna_mastodino(R['muslo'], R['espinilla'], R['metatarso'])
    yy, _ = max(patas)
    return rot, (0.0, yy - y0, 0.0)


def claves_pose_mastodino(a, claves):
    canales = {p: [] for p in PARTES_POSE_MASTODINO}
    mov = []
    for c in claves:
        t, destino = c[0], c[1]
        suave = c[2] if len(c) > 2 else 1
        rot, (dx, dy, dz) = pose_mastodino(destino)
        for p in PARTES_POSE_MASTODINO:
            canales[p].append((t, round(rot[p], 2), 0.0, 0.0, suave))
        mov.append((t, dx, round(dy, 3), round(dz, 3), suave))
    for p, ks in canales.items():
        if any(abs(k[1]) > 0.05 for k in ks):
            a.rot(p, ks)
    if any(abs(k[2]) > 0.01 or abs(k[3]) > 0.01 for k in mov):
        a.mov('cuerpo', mov)


def _paso_pose_mastodino(p, amp, rodilla, base):
    p = p % 1.0
    if p < 0.58:
        f = p / 0.58
        a1 = base['muslo'] + amp * math.cos(math.pi * f)
        vuelo = 0.0
    else:
        f = (p - 0.58) / 0.42
        a1 = base['muslo'] - amp * math.cos(math.pi * f)
        vuelo = math.sin(math.pi * f)
    a2 = base['espinilla'] - rodilla * vuelo - 0.25 * (a1 - base['muslo'])
    a3 = base['metatarso'] + rodilla * 0.65 * vuelo + 0.22 * (base['muslo'] - a1)
    return a1, a2, a3


def ciclo_mastodino(a, largo, n, base, amp, rodilla, cuerpo=None):
    claves = []
    for k in range(n + 1):
        ph = k / n
        d = dict(base)
        for ld, f0 in (('i', 0.0), ('d', 0.5)):
            p_ld = (ph + f0) % 1.0
            a1, a2, a3 = _paso_pose_mastodino(p_ld, amp, rodilla, base)
            vuelo = 0.0 if p_ld < 0.58 else math.sin(math.pi * (p_ld - 0.58) / 0.42)
            d[f'muslo_{ld}'], d[f'espinilla_{ld}'], d[f'metatarso_{ld}'] = a1, a2, a3
            d[f'dedos_{ld}'] = 22.0 * vuelo
        if cuerpo:
            d.update(cuerpo(ph))
        claves.append((largo * ph, d))
    claves_pose_mastodino(a, claves)


def _onda(largo, n, amp, fase=0.0, base=0.0, eje=1):
    out = []
    for k in range(n + 1):
        t = largo * k / n
        v = base + amp * math.sin(2 * math.pi * (k / n + fase))
        xyz = [0.0, 0.0, 0.0]
        xyz[eje] = round(v, 2)
        out.append((t, *xyz))
    return out


RUGIDO_MASTODINO = dict(inc=-13.0, cuello=-8.0, cabeza=12.0, abre=46.0, cola1=6.0, cola2=5.0, cola3=4.0,
                        muslo=16.0, espinilla=-36.0, metatarso=45.0, brazo=24.0, antebrazo=82.0, mano=72.0)


def anims_mastodino(m):
    """Animaciones serias de terópodo pesado para el Mastodino:
      siempre   jadeo pesado de la mandíbula y respiración del cuello;
      reposo    respiración con peso, balanceo de la cola en 3 tramos y acecho de la cabeza;
      andar     marcha pesada de dinosaurio: la rodilla se recoge hacia atrás en el vuelo, el pie apoya firme, el
                tronco horizontal baja en cada paso y los brazos van recogidos junto al pecho (sin braceo humanoide);
      correr    embestida pesada con el tronco, cuello y cabeza bajos en horizontal y zancadas largas;
      ataque    mordisco brutal: retrae el cuello abriendo la bandeja de hueso y se abalanza cerrando de golpe;
      especial2 cornada ascendente: baja el cráneo cornudo y embiste hacia delante y arriba levantando a la presa;
      especial  rugido sísmico de terópodo: planta las patas con un pisotón, baja el pecho y proyecta la cabeza al
                frente abriendo las fauces al máximo con los brazos recogidos contra las costillas;
      muerte    se desploma pesadamente de lado;
      aparece   se levanta y ruge."""
    s_ = m.anim('siempre', 2.4, bucle=True)
    s_.rot('mandibula', _onda(2.4, 8, 2.5, eje=0))
    s_.rot('cuello', _onda(2.4, 8, 1.0, fase=0.25, eje=0))

    r = m.anim('reposo', 3.6, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.4, periodo=1.8)
    r.rot('cola', _onda(3.6, 8, 4.5))
    r.rot('cola2', _onda(3.6, 8, 6.5, fase=-0.12))
    r.rot('cola3', _onda(3.6, 8, 8.5, fase=-0.24))
    r.rot('cabeza', [(0, 0, 0, 0), (0.6, 2, 10, -2), (1.5, 2, 10, -2), (1.8, 0, 0, 0),
                     (2.4, 2, -10, 2), (3.2, 2, -10, 2), (3.6, 0, 0, 0)])

    # andar (marcha pesada de terópodo, brazos recogidos junto al pecho)
    a = m.anim('andar', 1.35, bucle=True)
    base_a = dict(POSTURA_MASTODINO, inc=-17.0, cuello=-14.0, cabeza=10.0, brazo=26.0, antebrazo=82.0, mano=70.0)

    def cuerpo_andar(ph):
        pulso = math.sin(4 * math.pi * ph)
        return {'inc': base_a['inc'] + 1.8 * pulso,
                'cuello': base_a['cuello'] - 2.2 * math.sin(4 * math.pi * ph + 0.8),
                'cabeza': base_a['cabeza'] + 2.2 * math.sin(4 * math.pi * ph + 1.4),
                'cola1': base_a['cola1'] + 2.0 * math.sin(4 * math.pi * ph + 0.6),
                'brazo_i': base_a['brazo'] + 1.5 * pulso,
                'brazo_d': base_a['brazo'] + 1.5 * pulso,
                'antebrazo_i': base_a['antebrazo'] + 2.0 * pulso,
                'antebrazo_d': base_a['antebrazo'] + 2.0 * pulso}
    ciclo_mastodino(a, 1.35, 16, base_a, 18.0, 25.0, cuerpo_andar)
    a.rot('cola', _onda(1.35, 16, 5.5, fase=0.5))
    a.rot('cola2', _onda(1.35, 16, 7.5, fase=0.35))
    a.rot('cola3', _onda(1.35, 16, 9.5, fase=0.2))
    a.rot('cuerpo', _onda(1.35, 16, 2.2, fase=0.0, eje=2))

    # correr (carga horizontal pesada de dinosaurio)
    c = m.anim('correr', 0.78, bucle=True)
    base_c = dict(POSTURA_MASTODINO, inc=-11.5, cuello=-8.0, cabeza=12.0, abre=30.0, cola1=4.0, cola2=3.0, cola3=2.0,
                  muslo=18.0, espinilla=-36.0, metatarso=45.0, brazo=22.0, antebrazo=84.0, mano=74.0)

    def cuerpo_correr(ph):
        pulso = math.sin(4 * math.pi * ph)
        return {'inc': base_c['inc'] + 2.5 * pulso,
                'cuello': base_c['cuello'] - 3.0 * math.sin(4 * math.pi * ph + 0.8),
                'cabeza': base_c['cabeza'] + 3.0 * math.sin(4 * math.pi * ph + 1.4),
                'abre': base_c['abre'] + 4.0 * pulso,
                'cola1': base_c['cola1'] + 2.8 * math.sin(4 * math.pi * ph + 0.6),
                'brazo_i': base_c['brazo'] + 2.0 * pulso,
                'brazo_d': base_c['brazo'] + 2.0 * pulso}
    ciclo_mastodino(c, 0.78, 16, base_c, 23.0, 29.0, cuerpo_correr)
    c.rot('cola', _onda(0.78, 16, 6.5, fase=0.5))
    c.rot('cola2', _onda(0.78, 16, 9.0, fase=0.35))
    c.rot('cola3', _onda(0.78, 16, 11.0, fase=0.2))
    c.rot('cuerpo', _onda(0.78, 16, 2.8, fase=0.0, eje=2))

    # ataque: mordisco feroz (retrae el cuello abriendo las fauces al máximo y lanza la cabeza cerrando de golpe)
    at = m.anim('ataque', 0.78)
    prep = dict(inc=-20.0, cuello=-24.0, cabeza=0.0, abre=48.0, cola1=-2.0, cola2=-1.0,
                muslo_i=10.0, espinilla_i=-32.0, metatarso_i=43.0,
                muslo_d=18.0, espinilla_d=-36.0, metatarso_d=45.0,
                brazo=22.0, antebrazo=84.0, mano=74.0)
    mordisco = dict(inc=-10.0, cuello=-2.0, cabeza=18.0, abre=50.0, cola1=6.0, cola2=5.0, cola3=4.0,
                    muslo_i=22.0, espinilla_i=-38.0, metatarso_i=45.0,
                    muslo_d=8.0, espinilla_d=-30.0, metatarso_d=41.0,
                    brazo=24.0, antebrazo=82.0, mano=72.0)
    cierre = dict(mordisco, abre=4.0, cabeza=22.0, cuello=2.0)
    claves_pose_mastodino(at, [(0.0, {}), (0.18, prep), (0.32, mordisco), (0.44, cierre),
                               (0.58, dict(cierre, abre=12.0, cabeza=16.0)), (0.78, {})])
    at.mov('cuerpo', [(0.0, 0, 0, 0), (0.18, 0, 0.4, -1.8), (0.32, 0, -1.0, 4.0), (0.44, 0, -0.8, 3.4),
                      (0.78, 0, 0, 0)])
    at.rot('cabeza', [(0.0, 0, 0, 0), (0.18, 0, 6, -5), (0.32, 0, -4, 4), (0.44, 0, -10, 8), (0.58, 0, 5, -4),
                      (0.78, 0, 0, 0)])

    # especial2: cornada ascendente con los cuernos dorsales del cráneo (lanza a la presa hacia arriba)
    e2 = m.anim('especial2', 0.85)
    baja_cuernos = dict(inc=-8.0, cuello=6.0, cabeza=28.0, abre=14.0, cola1=8.0, cola2=6.0, cola3=4.0,
                        muslo_i=22.0, espinilla_i=-38.0, metatarso_i=45.0,
                        muslo_d=12.0, espinilla_d=-32.0, metatarso_d=43.0,
                        brazo=22.0, antebrazo=84.0, mano=74.0)
    embiste_arriba = dict(inc=-20.0, cuello=-26.0, cabeza=-6.0, abre=38.0, cola1=-4.0, cola2=-3.0, cola3=-2.0,
                          muslo_i=12.0, espinilla_i=-30.0, metatarso_i=43.0,
                          muslo_d=16.0, espinilla_d=-34.0, metatarso_d=44.0,
                          brazo=24.0, antebrazo=82.0, mano=72.0)
    claves_pose_mastodino(e2, [(0.0, {}), (0.24, baja_cuernos), (0.44, embiste_arriba), (0.60, embiste_arriba),
                               (0.85, {})])
    e2.mov('cuerpo', [(0.0, 0, 0, 0), (0.24, 0, -1.5, 1.5), (0.44, 0, 1.0, 4.2), (0.60, 0, 0.5, 2.5),
                      (0.85, 0, 0, 0)])

    # especial: rugido sísmico de terópodo con pisotón (sin ponerse vertical como humanoide ni abrir los brazos)
    e = m.anim('especial', 1.8)
    pisoton = dict(inc=-18.0, cuello=-18.0, cabeza=4.0, abre=16.0,
                   muslo_i=26.0, espinilla_i=-42.0, metatarso_i=46.0,
                   muslo_d=14.0, espinilla_d=-34.0, metatarso_d=44.0,
                   brazo=22.0, antebrazo=84.0, mano=74.0)
    claves_pose_mastodino(e, [(0.0, {}), (0.22, pisoton), (0.42, RUGIDO_MASTODINO), (1.35, RUGIDO_MASTODINO),
                              (1.8, {})])
    e.mov('cuerpo', [(0.0, 0, 0, 0), (0.22, 0, 1.2, -1.0), (0.42, 0, -1.2, 3.0), (1.35, 0, -1.0, 2.8),
                     (1.8, 0, 0, 0)])
    e.rot('cabeza', [(0.0, 0, 0, 0), (0.42, 0, 10, -4), (0.75, 0, -12, 5), (1.08, 0, 10, -4), (1.35, 0, 0, 0),
                     (1.8, 0, 0, 0)])
    e.rot('cola', [(0.0, 0, 0, 0), (0.42, 0, -10, 0), (0.9, 0, 12, 0), (1.35, 0, -8, 0), (1.8, 0, 0, 0)])
    e.rot('cola2', [(0.0, 0, 0, 0), (0.48, 0, -14, 0), (0.95, 0, 16, 0), (1.4, 0, -12, 0), (1.8, 0, 0, 0)])
    e.rot('cola3', [(0.0, 0, 0, 0), (0.54, 0, -18, 0), (1.0, 0, 20, 0), (1.45, 0, -14, 0), (1.8, 0, 0, 0)])

    d = m.anim('muerte', 1.3)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.3, -8, 0, -5), (1.0, 6, 0, 90), (1.3, 6, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (0.3, 0, 1.0, 0), (1.0, 0, -11.0, 0), (1.3, 0, -11.0, 0)])
    d.rot('mandibula', [(0, 0, 0, 0), (0.4, 24, 0, 0), (1.3, 12, 0, 0)])
    d.rot('cola', [(0, 0, 0, 0), (1.0, 0, 14, 0), (1.3, 0, 14, 0)])

    ap = m.anim('aparece', 1.3)
    agachado = dict(inc=-10.0, cuello=4.0, cabeza=18.0, abre=10.0, muslo=32.0, espinilla=-46.0, metatarso=38.0,
                    brazo=24.0, antebrazo=84.0, mano=74.0)
    claves_pose_mastodino(ap, [(0.0, agachado), (0.35, agachado), (0.75, RUGIDO_MASTODINO), (1.05, RUGIDO_MASTODINO),
                               (1.3, {})])

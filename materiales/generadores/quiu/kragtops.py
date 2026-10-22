"""
El Kragtops (DEDsafío 4, Centro de Quiu): «gigante y pacífico; defiende su territorio». Un coloso de piedra a cuatro
patas, bajo y largo (2,4 bloques de alto por 3,9 de largo y 2,1 de ancho), recreado tal cual del icono del libro del
juego y de los carteles (copia fiel; la ficha está en SP/quiu_ref2/kragtops/ficha.md):

  gorguera   lo que más se ve: una corona de placas de piedra casi negra, talladas (marco de 1 px y una greca en
             espiral cuadrada), alrededor del cuello y detrás de la cabeza: abajo, el collar en cuenco de seis paneles
             con su espiral grande; encima, seis placas abiertas en abanico y, en medio, la más alta, una columna casi de
             pie (1,0 H). Diez puntas de hueso blanco en el borde. Va con la cabeza, como la gola del tricerátops
  cabeza     pequeña, baja y de piedra oscura, metida bajo la gorguera, con dos huecos negros juntos en la cara de
             delante; tres cuernos de hueso macizos: el del morro (el más grande, casi de pie) y uno a cada lado de la
             frente, en la unión con la gorguera, abiertos hacia arriba y hacia fuera
  coraza     una losa casi negra de arriba plano sobre la mitad de delante del lomo, con su banda de olas de espirales
             en los costados y dos vetas encima; de ella sale un abanico de seis cristales azules, como los dedos de una
             mano (la base oscura y la punta clara)
  cuerpo     piedra gris parda, cálida; la cadera, un escalón más baja y sin coraza; una losa inclinada en cada hombro y
             en cada muslo, con la arista de arriba clara
  patas      cortas y gruesas, de piedra gris azulada con vetas, y pezuñas casi negras de tres dedos
  cola       corta y recta, parda con bandas, con dos puntas de hueso encima; la maza: dos bloques de hueso escalonados a
             cada lado de la mitad de abajo de la punta (de lado, una barra con muesca; desde arriba, una T)

Es pacífico hasta que lo atacan: entonces embiste de frente con la gorguera por delante (ataque: cabezazo hacia arriba
con los cuernos; correr: la cabeza baja) o barre de lado con la maza (especial: golpe de cola).

Todo al píxel de Minecraft (16 por bloque), también las tallas (líneas de 1 px, como en el juego); los ojos, las
pezuñas y las vetas del hueso, a 32 por bloque (B.fino). El modelo se construye ya a su tamaño (TAM = 1).
"""
import math

import numpy as np

import bestiario as B
import bestiario_limpio as L
from bestiario import T
from bestiario_fantasmas_v2 import con_mapa
from bestiario_hormigas import _azar1
from bestiario_limpio import rampa

ID = 'kragtops'
TAM = 1.0

# ======================================================================================================================
#  Las rampas (de oscuro a claro), de la ficha: el icono del cartel del 02-10 y el juego de día
# ======================================================================================================================
PIEDRA_KRAGTOPS = rampa('2e2820', '3e3830', '4e463c', '625a4c', '7a7262')     # el cuerpo: gris pardo cálido
CORAZA_KRAGTOPS = rampa('121411', '1c1e1b', '272926', '343632', '43453f')     # coraza, gorguera y cara
GRECA_KRAGTOPS = rampa('353733', '3f413d', '4a4c47', '55574f', '62645c')      # las líneas talladas
MARCO_KRAGTOPS = rampa('2e302c', '3c3e3a', '4a4c47', '585a54', '686a63')      # el marco de las placas
HUESO_KRAGTOPS = rampa('8c7a6e', 'ab988b', 'c9b9ad', 'e0d3c8', 'f6ece4')      # blanco hueso, sombra beis rosada
CRISTAL_KRAGTOPS = rampa('14306a', '244c8c', '3e66a8', '6a8ec6', 'a8c2ea')    # la base oscura y la punta clara
PATA_KRAGTOPS = rampa('2e3436', '3c4648', '4c5656', '5e6866', '76807e')       # gris azulado, más frío
PEZUNA_KRAGTOPS = rampa('0e0d0b', '171614', '201f1c', '2b2a27', '3a3935')     # casi negro, algo pardo
COLA_KRAGTOPS = rampa('1c1612', '2a221c', '382f28', '4a4038', '5c5448')       # la piedra del cuerpo, más oscura
OJO_KRAGTOPS = (5, 5, 5)
BARRA_KRAGTOPS = (44, 46, 42)

FINO_KRAGTOPS = 0.5


# ======================================================================================================================
#  Ayudas
# ======================================================================================================================
def _u_kragtops(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def marco_kragtops(o, eje_y, eje_z):
    """El marco con el origen en o, su Y por eje_y y su Z (la cara de delante de las cajas) hacia eje_z."""
    y = _u_kragtops(eje_y)
    z = np.asarray(eje_z, float)
    z = _u_kragtops(z - np.dot(z, y) * y)
    x = np.cross(y, z)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, o
    return M


def caja_kragtops(m, parte, M, x0, y0, z0, w, h, d, pint):
    m._caja(parte, M, x0, y0, z0, w, h, d, pint)


def todas_kragtops(frente, atras, lado, arriba=None, abajo=None):
    """Los pintores de las seis caras."""
    return {'frente': frente, 'atras': atras, 'izq': lado, 'der': lado, 'arriba': arriba or lado,
            'abajo': abajo or lado}


def _tex_kragtops(R_, v, dentro=None):
    tex = L._rgba(L.color_continuo(R_, np.clip(np.round(v), 0, len(R_) - 1)))
    if dentro is not None:
        tex[..., 3] = np.where(dentro, 255, 0)
    return tex


def _luz_kragtops(tw, th, c, base, luz):
    """El tono de una cara: arriba más claro, abajo más oscuro y, en los lados, un poco más claro arriba."""
    xs, ys = L._malla(tw, th)
    if c == 'arriba':
        v = np.full((th, tw), base + luz * 0.6)
    elif c == 'abajo':
        v = np.full((th, tw), base - luz * 0.8)
    else:
        v = base + luz * (0.3 - (ys + 0.5) / max(1, th) * 0.6)
    return xs, ys, v


def _manchas_kragtops(xs, ys, s, k=1.0):
    """Manchas blandas de 2 a 4 px (tres rejillas desplazadas que se suman): -1, 0 o +1 en cada píxel."""
    n1 = _azar1((xs + 1) // 3, (ys + 2) // 3, s + 31)
    n2 = _azar1((xs + 3) // 4, (ys + 1) // 4, s + 43)
    n3 = _azar1(xs // 2, (ys + 1) // 2, s + 37)
    mm = n1 * 0.45 + n2 * 0.4 + n3 * 0.15
    return (np.where(mm < 0.33, -1.0, 0.0) + np.where(mm > 0.69, 0.8, 0.0)) * k


def espiral_kragtops(w, h):
    """Una espiral cuadrada de w x h (líneas de 1 px con 1 px de hueco), de fuera adentro desde la esquina de arriba a
    la izquierda: la greca."""
    a = np.zeros((h, w), bool)
    if w < 1 or h < 1:
        return a
    x, y, dx, dy = 0, 0, 1, 0
    a[0, 0] = True

    def dentro(px, py):
        return 0 <= px < w and 0 <= py < h

    giros = 0
    for _ in range(w * h * 4):
        nx, ny = x + dx, y + dy
        ax, ay = x + 2 * dx, y + 2 * dy
        ok = dentro(nx, ny) and not a[ny, nx] and (not dentro(ax, ay) or not a[ay, ax])
        # que no toque de lado a otra línea (el hueco de 1 px)
        if ok:
            lx, ly = nx - dy, ny + dx
            rx, ry = nx + dy, ny - dx
            if (dentro(lx, ly) and a[ly, lx] and (lx, ly) != (x, y)) or (dentro(rx, ry) and a[ry, rx] and (rx, ry) != (x, y)):
                ok = False
        if ok:
            x, y = nx, ny
            a[y, x] = True
            giros = 0
        else:
            dx, dy = -dy, dx
            giros += 1
            if giros > 1:
                break
    return a


# ======================================================================================================================
#  Los pintores
# ======================================================================================================================
def piedra_kragtops(nombre, R_, base=2.0, luz=0.6, manchas=0.8, arista=0.0, bandas=0, grietas=0.05, semilla=0):
    """Piedra al píxel, limpia: el tono con la luz de arriba, parches grandes y blandos un tono más claros u oscuros
    (de 3 a 5 px, de dos rejillas desplazadas: sin cuadrícula ni motas sueltas), alguna grieta corta de 1 px, la
    arista de arriba más clara ('arista') y bandas transversales oscuras cada 'bandas' px (la cola)."""
    def fn(tw, th, c, s):
        s2 = int(s) + semilla
        xs, ys, v = _luz_kragtops(tw, th, c, base, luz)
        if c != 'abajo' and manchas:
            n1 = _azar1((xs + 2) // 5, (ys + 1) // 4, s2 + 31)
            n2 = _azar1((xs + 4) // 4, (ys + 3) // 5, s2 + 43)
            mm = n1 * 0.55 + n2 * 0.45
            v = v + (mm > 0.72) * 0.7 * manchas - (mm < 0.22) * 0.8 * manchas
        if arista and c not in ('arriba', 'abajo') and th >= 3:
            v = v + (ys == 0) * arista - (ys == th - 1) * arista * 0.7
        if bandas:
            coord = xs if c in ('izq', 'der') else (ys if c in ('arriba', 'abajo') else None)
            if coord is not None:
                v = v - ((coord % bandas) == bandas - 1) * 1.0
        if grietas and c != 'abajo' and tw > 5 and th > 5:
            # Grietas cortas: tramos de 2-3 px en diagonal, de tarde en tarde.
            celda = _azar1(xs // 6, ys // 6, s2 + 71) < grietas * 6
            u, w = xs % 6, ys % 6
            v = v - (celda & (u == w) & (u > 0) & (u < 4)) * 1.0
        idx = L._limpiar(np.clip(np.round(v), 0, len(R_) - 1).astype(int), 1)
        return L._img(idx, R_), None
    return B.Pintor(nombre, fn)


def coraza_kragtops(nombre, base=1.6, luz=0.5, vetas=True):
    """La piedra casi negra de la coraza y de la cara: lisa, con manchas de 1-2 tonos y (arriba) 1-2 vetas talladas."""
    def fn(tw, th, c, s):
        xs, ys, v = _luz_kragtops(tw, th, c, base, luz)
        v = v + _manchas_kragtops(xs, ys, int(s) + 5, 0.5)
        if vetas and c == 'arriba' and tw > 8 and th > 8:
            # Dos vetas talladas a lo largo, con su sombra.
            for f in (0.33, 0.7):
                x0 = int(tw * f)
                ola = ((ys // 4) % 2).astype(int)
                linea = (xs == x0 + ola) & (ys > 1) & (ys < th - 2)
                v = np.where(linea, 2.6, v)
                v = np.where((xs == x0 + ola + 1) & (ys > 1) & (ys < th - 2), v - 0.6, v)
        idx = L._limpiar(np.clip(np.round(v), 0, 4).astype(int), 1)
        return L._img(idx, CORAZA_KRAGTOPS), None
    return B.Pintor(nombre, fn)


def greca_kragtops(tipo, wu, hu):
    """El dibujo de la talla en un hueco de wu x hu (al píxel de Minecraft, líneas de 1 px): 'panel' (una espiral
    cuadrada grande), 'placa' (un gancho: una espiral pequeña arriba y la línea que baja por el medio), 'columna' (una
    ranura a lo largo) o 'banda' (espirales encadenadas como olas, ~@~@~, una al derecho y otra al revés)."""
    g = np.zeros((hu, wu), bool)
    if wu < 3 or hu < 3:
        return g
    if tipo == 'panel':
        n = min(wu, hu, 7)
        y0 = (hu - n) // 2
        x0 = (wu - n) // 2
        g[y0:y0 + n, x0:x0 + n] = espiral_kragtops(n, n)
    elif tipo == 'placa':
        n = min(wu, 5)
        n = n if n % 2 else n - 1
        x0 = (wu - n) // 2
        g[0:n, x0:x0 + n] = espiral_kragtops(n, n)
        g[n - 1:hu, x0] = True
    elif tipo == 'columna':
        g[0:hu, wu // 2] = True
    elif tipo == 'banda':
        # Olas: espirales cuadradas de n x n, una al derecho y la siguiente al revés, unidas por una línea que corre
        # arriba o abajo (~@~@~).
        n = min(hu, 7)
        n = n if n % 2 else n - 1
        paso = n + 2
        gy = (hu - n) // 2
        k = 0
        for gx in range(1, wu - n, paso):
            sp = espiral_kragtops(n, n)
            if k % 2:
                sp = sp[::-1, ::-1]
            g[gy:gy + n, gx:gx + n] |= sp
            fila = gy + n - 1 if k % 2 else gy
            g[fila, max(0, gx - 2):gx] = True
            k += 1
    return g


def placa_kragtops(nombre, tipo='placa', caras_greca=('frente', 'atras'), tapa=None):
    """Una placa tallada, al píxel de Minecraft: el fondo casi negro con manchas de 1-2 tonos, el marco de 1 px gris
    medio (y 1 px de sombra por dentro) y la greca de líneas de 1 px, 1-2 tonos más clara, con su sombra debajo, en las
    caras de 'caras_greca'. Los cantos, de la misma piedra oscura con su arista clara."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), 2.4) + _manchas_kragtops(xs, ys, int(s) + 9, 0.4)
        if c == 'arriba':
            v = v + 0.4
        elif c == 'abajo':
            v = v - 0.4
        tipo_c = tipo if c in caras_greca else (tapa if (c == 'arriba' and tapa) else None)
        if tipo_c is None:
            # Un canto o una cara sin talla: la piedra oscura, con su arista de arriba algo más clara.
            if c not in ('arriba', 'abajo') and th >= 3:
                v = v + (ys == 0) * 0.6
            idx = np.clip(np.round(v), 0, 4).astype(int)
            return L._img(idx, CORAZA_KRAGTOPS), None
        borde = (xs == 0) | (xs == tw - 1) | (ys == 0) | (ys == th - 1)
        greca = np.zeros((th, tw), bool)
        x0, y0, x1, y1 = 2, 2, tw - 2, th - 2          # lo de dentro del marco, con 1 px de hueco
        if tipo_c == 'banda':
            # La banda del costado de la coraza: el marco arriba y abajo, y las olas en todo el alto que queda.
            borde = (ys == 0) | (ys == th - 1)
            x0, y0, x1, y1 = 1, 1, tw - 1, th - 1
        if x1 - x0 >= 3 and y1 - y0 >= 3:
            greca[y0:y1, x0:x1] = greca_kragtops(tipo_c, x1 - x0, y1 - y0)
        sombra_g = np.zeros_like(greca)
        sombra_g[1:, :] = greca[:-1, :] & ~greca[1:, :]
        v = np.where(sombra_g & ~borde, 1.0, v)
        idx = np.clip(np.round(v), 0, 4).astype(int)
        rgb = L.color_continuo(CORAZA_KRAGTOPS, idx)
        rgb = np.where(borde[..., None], L.color_continuo(MARCO_KRAGTOPS, np.full((th, tw), 2.0) + (ys == 0) * 0.8), rgb)
        rgb = np.where(greca[..., None], L.color_continuo(GRECA_KRAGTOPS, np.full((th, tw), 3.2)), rgb)
        return L._rgba(rgb), None
    return B.Pintor(nombre, fn)


def hueso_kragtops(nombre, grietas=True):
    """Hueso blanco cálido: la cara de arriba en #ece2dc-#f4ebe5, los lados algo más oscuros, el canto de abajo de 1 px
    beis rosado y, en las caras grandes, una o dos grietas finas."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), 3.8)
        elif c == 'abajo':
            v = np.full((th, tw), 1.6)
        else:
            v = 3.3 - (ys + 0.5) / th * 0.6
            v = v - (ys >= th - 2) * 1.2 + (ys < 2) * 0.4
        v = v + (_azar1(xs // 4, ys // 4, int(s) + 3) > 0.8) * 0.4 - (_azar1((xs + 2) // 4, (ys + 1) // 4, int(s) + 7) < 0.15) * 0.4
        if c not in ('arriba', 'abajo') and tw >= 6 and th >= 8:
            # Las vetas de lo largo del hueso: líneas finas algo más oscuras, cortadas.
            col = _azar1(xs, np.zeros_like(xs), int(s) + 29)
            v = v - ((col < 0.22) & (_azar1(xs, ys // 5, int(s) + 31) > 0.35) & (ys > 1)) * 0.7
        if grietas and c not in ('abajo',) and tw >= 8 and th >= 8:
            rng = np.random.default_rng(int(s) * 13 + tw)
            gx = rng.integers(2, tw - 2)
            gy = rng.integers(1, th // 2)
            largo = rng.integers(th // 3, th // 2 + 2)
            for k in range(largo):
                yy = gy + k
                xx = gx + (k // 3) * (1 if rng.random() < 0.5 else -1) * 0
                if 0 <= yy < th and 0 <= xx < tw:
                    v[yy, xx] = 1.4
            # una rama corta
            for k in range(3):
                yy, xx = gy + largo // 2 + k, gx + k + 1
                if 0 <= yy < th and 0 <= xx < tw:
                    v[yy, xx] = 1.6
        idx = np.clip(np.round(v), 0, 4).astype(int)
        return L._img(idx, HUESO_KRAGTOPS), None
    return B.fino(B.Pintor(nombre, fn), FINO_KRAGTOPS)


def cristal_kragtops(nombre, arista=True, v0=0.2, v1=3.0):
    """Un cristal (un prisma de 2 x 2): degradado a lo largo, de la base oscura (v0) a la punta clara (v1), con una
    arista de 1 px más clara en una de las caras de lado; sin ruido."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        if c == 'arriba':
            v = np.full((th, tw), v1 + 0.3)
        elif c == 'abajo':
            v = np.full((th, tw), v0)
        else:
            t = 1.0 - (ys + 0.5) / th                   # 0 en la base, 1 en la punta
            v = v0 + (v1 - v0) * t
            if arista and c in ('izq', 'frente'):
                v = v + (xs == 0) * 0.8
            if c in ('der', 'atras'):
                v = v - 0.3
        idx = np.clip(np.round(v), 0, 4).astype(int)
        return L._img(idx, CRISTAL_KRAGTOPS), None
    return B.Pintor(nombre, fn)


def pata_kragtops(nombre):
    """La parte baja de las patas: piedra gris azulada con vetas verticales claras de 1 px y manchas de 2 px; abajo, 1 px
    más oscuro antes de la pezuña."""
    def fn(tw, th, c, s):
        xs, ys, v = _luz_kragtops(tw, th, c, 2.7, 0.5)
        if c not in ('arriba', 'abajo'):
            col = _azar1(xs, np.zeros_like(xs), int(s) + 13)
            corta = _azar1(xs, ys // 3, int(s) + 17)
            v = v + ((col > 0.72) & (corta > 0.3)) * 0.9 - ((col < 0.2) & (corta > 0.4)) * 0.7
            v = v + _manchas_kragtops(xs, ys, int(s) + 19, 0.5)
            v = v - (ys == th - 1) * 0.9
        idx = L._limpiar(np.clip(np.round(v), 0, 4).astype(int), 1)
        return L._img(idx, PATA_KRAGTOPS), None
    return B.Pintor(nombre, fn)


def pezuna_kragtops(nombre):
    """La pezuña (a 32 por bloque): casi negra, tres dedos de unos 2 px separados por una línea más oscura, con la cara
    de arriba de cada dedo 1 px más clara."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        v = np.full((th, tw), 2.0)
        if c == 'arriba':
            v = v + 0.8
        elif c == 'abajo':
            v = v - 1.5
        if c in ('frente', 'arriba', 'izq', 'der'):
            u = xs if c in ('frente', 'arriba') else None
            if u is not None:
                tercio = tw / 3.0
                junta = (np.abs(u + 0.5 - tercio) < 0.6) | (np.abs(u + 0.5 - 2 * tercio) < 0.6)
                v = np.where(junta, 0.3, v)
            if c != 'arriba':
                v = v + (ys < 2) * 0.9 - (ys >= th - 1) * 0.6
        idx = np.clip(np.round(v), 0, 4).astype(int)
        return L._img(idx, PEZUNA_KRAGTOPS), None
    return B.fino(B.Pintor(nombre, fn), FINO_KRAGTOPS)


def cara_kragtops(nombre, ancho, alto, fila0=3, alto_ojo=3, ancho_ojo=4, barra=2):
    """La cara de delante de la cabeza (a 32 por bloque, sin estirar: el mapa es del tamaño de la cara): la piedra
    oscura con los dos huecos negros juntos, justo bajo el cuerno del morro, separados por una barra gris de 1 px."""
    W, Hh = int(round(ancho * 2)), int(round(alto * 2))
    g = [['.'] * W for _ in range(Hh)]
    total = 2 * ancho_ojo + barra
    c0 = (W - total) // 2
    for f in range(fila0, fila0 + alto_ojo):
        for k in range(ancho_ojo):
            g[f][c0 + k] = 'k'
            g[f][c0 + ancho_ojo + barra + k] = 'k'
        for k in range(barra):
            g[f][c0 + ancho_ojo + k] = 'g'
    mapa = [''.join(f) for f in g]
    piel = coraza_kragtops(nombre + '_piel', base=1.7, vetas=False)

    def fondo(tw, th, c, s):
        base = piel.fn(max(1, (tw + 1) // 2), max(1, (th + 1) // 2), c, s)[0][..., :3].astype(float)
        return np.repeat(np.repeat(base, 2, 0), 2, 1)[:th, :tw]
    return con_mapa(nombre, fondo, {'frente': mapa}, {'k': OJO_KRAGTOPS, 'g': BARRA_KRAGTOPS}, fino=True)


# ======================================================================================================================
#  El modelo
# ======================================================================================================================
# Las medidas (px de Minecraft, ya a su tamaño): el suelo en y = 0, el frente en +Z. El cuerno del morro llega a z = 33 y
# la punta de la maza a z = -37 (L = 70); la placa más alta de la gorguera, a y = 37 (H = 37).
Y_VIENTRE_KRAGTOPS = 8.0          # la tripa (0,21 H)
Y_LOMO_KRAGTOPS = 20.0            # lo alto del tronco y de la cadera (0,53 H)
Y_CORAZA_KRAGTOPS = 27.0          # lo alto de la coraza (0,71 H)
Z_CORAZA_KRAGTOPS = (-3.5, 18.0)  # de la cadera a la gorguera
Z_TRONCO_KRAGTOPS = (-11.0, 20.0)
ANCHO_TRONCO_KRAGTOPS = 17.0
N_GORGUERA_KRAGTOPS = np.array((0.0, 12.0, 20.5))   # el centro del cuello, abajo: de ahí sale la corona de placas
EJE_GORGUERA_KRAGTOPS = 3.0                         # grados que se echa hacia atrás el eje de la corona


def _corona_kragtops(psi, tau):
    """Las direcciones de una pieza de la corona: psi, el giro alrededor del cuello (0 delante, + hacia la izquierda,
    +X); tau, lo que se abre hacia fuera desde el eje. Devuelve (hacia fuera, a lo largo de la pieza, su cara de
    fuera)."""
    e = math.radians(EJE_GORGUERA_KRAGTOPS)
    eje = np.array((0.0, math.cos(e), -math.sin(e)))
    frente = np.array((0.0, math.sin(e), math.cos(e)))
    p, t = math.radians(psi), math.radians(tau)
    fuera = math.cos(p) * frente + math.sin(p) * np.array((1.0, 0.0, 0.0))
    largo = math.cos(t) * eje + math.sin(t) * fuera
    cara = -math.sin(t) * eje + math.cos(t) * fuera
    return eje, fuera, largo, cara


def pieza_corona_kragtops(m, parte, psi, tau, radio, alto0, largo, ancho, grueso, caras, punta=None, punta_lado=0.0,
                          de_lado=False):
    """Una placa de la corona: sale del anillo del cuello (radio, a 'alto0' por el eje), abierta 'tau' hacia fuera,
    con la cara tallada hacia fuera (o, con 'de_lado', hacia su costado: así se ve de lado aunque esté detrás); y su
    punta de hueso en el extremo (si se pide), corrida 'punta_lado' de lado."""
    eje, fuera, d, cara = _corona_kragtops(psi, tau)
    if de_lado:
        cara = np.array((math.copysign(1.0, math.sin(math.radians(psi))), 0.0, 0.0))
    o = N_GORGUERA_KRAGTOPS + fuera * radio + eje * alto0
    M = marco_kragtops(o, d, cara)
    caja_kragtops(m, parte, M, -ancho / 2, 0.0, -grueso / 2, ancho, largo, grueso, caras)
    if punta is not None:
        caja_kragtops(m, parte, M, -1.0 + punta_lado, largo - 0.6, -1.0, 2.0, 3.0, 2.0, punta)
    return M


def gorguera_kragtops(m, parte, placa_p, placa_atras, panel_p, panel_atras, hueso, columna_p):
    """La gorguera: una corona de placas talladas alrededor del cuello, abiertas hacia fuera (de frente se ve como un
    cuenco; desde arriba, como un abanico), cada una con su punta de hueso; abajo, el collar de paneles anchos con su
    espiral grande, a los lados de la cabeza."""
    caras_placa = todas_kragtops(placa_p, placa_atras, placa_p)
    caras_panel = todas_kragtops(panel_p, panel_atras, panel_p)
    # El collar: un cuenco ancho de paneles alrededor del cuello, por delante y por los lados, abiertos hacia fuera
    # (de frente es la parte de abajo del abanico, casi tan ancha como toda la gorguera), con la punta de hueso en la
    # esquina de fuera. (psi, tau, radio, alto0, largo, ancho)
    for psi, tau, radio, alto0, largo, ancho, punta in ((55, 28, 7.0, 1.5, 11.0, 9.0, False),
                                                        (95, 30, 7.0, 1.0, 12.0, 11.0, True),
                                                        (135, 25, 6.5, 2.0, 11.0, 8.0, True)):
        for lado in (1, -1):
            pieza_corona_kragtops(m, parte, lado * psi, tau, radio, alto0, largo, ancho, 2.5, caras_panel,
                                  hueso if punta else None, punta_lado=lado * (ancho / 2 - 1.5))
    # La placa más alta: una columna casi de pie en medio, detrás de la cabeza (de lado, justo delante de la coraza; en
    # el icono, detrás del cuerno del morro).
    pieza_corona_kragtops(m, parte, 180, 2, -0.5, 6.0, 18.0, 6.0, 2.5, todas_kragtops(columna_p, panel_atras, panel_atras))
    # Las placas de arriba, abiertas en abanico a los dos lados, más tumbadas cuanto más abajo: (psi, tau, largo)
    for psi, tau, largo, ancho in ((155, 18, 15.0, 6.0), (132, 38, 14.0, 5.5), (110, 56, 12.5, 5.5)):
        for lado in (1, -1):
            pieza_corona_kragtops(m, parte, lado * psi, tau, 5.0, 6.5, largo, ancho, 2.5, caras_placa, hueso,
                                  de_lado=True)


def cristales_kragtops(m, parte, pint, punta):
    """El abanico de cristales del lomo, justo detrás de la gorguera, como los dedos de una mano: seis prismas finos
    (de 1,6 a 2 px), los del medio más largos, los de delante echados hacia la gorguera y los de detrás hacia la cola;
    cada uno se afila en dos escalones hasta la punta, y alguno lleva un brote corto de lado."""
    # (z de la base, x, largo, inclinación hacia delante, inclinación de lado, grueso, brote)
    lista = ((1.8, 0.4, 5.5, -18, 5, 1.8, 0), (3.5, -0.6, 9.5, -12, -5, 2.0, 1), (5.5, 0.5, 11.5, -4, 4, 2.0, 0),
             (7.5, -0.4, 11.0, 5, -4, 2.0, -1), (9.5, 0.6, 8.5, 15, 5, 1.8, 0), (11.5, -0.5, 4.5, 26, -5, 1.6, 0))
    for z, xx, largo, adel, lado, g, brote in lista:
        o = np.array((xx, Y_CORAZA_KRAGTOPS - 1.0, z))
        M = T(*o) @ B.girar((adel, 0, lado))
        caja_kragtops(m, parte, M, -g / 2, 0.0, -g / 2, g, largo, g, pint)
        # La punta, en dos escalones (más fina).
        g2 = g - 0.6
        caja_kragtops(m, parte, M, -g2 / 2, largo, -g2 / 2, g2, 1.4, g2, punta)
        if brote:
            # Un brote corto de lado, a media altura.
            Mb = M @ T(0, largo * 0.45, 0) @ B.girar((0, 0, -brote * 40))
            caja_kragtops(m, parte, Mb, -0.5, 0.0, -0.5, 1.0, 2.4, 1.0, punta)


def construir():
    """El Kragtops a su tamaño (2,3 x 4,4 bloques)."""
    m = B.Modelo('kragtops', K=2, ancho=256)
    m.escala = 1.0

    piedra = piedra_kragtops('piedra_kragtops', PIEDRA_KRAGTOPS, base=2.4, luz=0.7, manchas=0.5)
    losa = piedra_kragtops('losa_kragtops', PIEDRA_KRAGTOPS, base=2.3, luz=0.7, arista=1.2, manchas=0.5, semilla=5)
    coraza = coraza_kragtops('coraza_kragtops')
    banda = placa_kragtops('banda_kragtops', tipo='banda', caras_greca=('izq', 'der'))
    tapa = placa_kragtops('tapa_kragtops', tipo='placa', caras_greca=())
    placa = placa_kragtops('placa_kragtops', tipo='placa')
    placa_det = placa_kragtops('placa_det_kragtops', tipo='placa', caras_greca=())
    columna = placa_kragtops('columna_kragtops', tipo='columna')
    panel = placa_kragtops('panel_kragtops', tipo='panel', caras_greca=('frente',))
    hueso = hueso_kragtops('hueso_kragtops')
    hueso_liso = hueso_kragtops('hueso_liso_kragtops', grietas=False)
    cristal = cristal_kragtops('cristal_kragtops', v0=0.2, v1=2.6)
    punta_cristal = cristal_kragtops('punta_cristal_kragtops', arista=False, v0=2.6, v1=3.1)
    pata = pata_kragtops('pata_kragtops')
    pezuna = pezuna_kragtops('pezuna_kragtops')
    cola_p = piedra_kragtops('cola_kragtops', COLA_KRAGTOPS, base=2.5, luz=0.8, bandas=4, manchas=0.6, semilla=11)
    cara = cara_kragtops('cara_kragtops', 9, 6.5, fila0=3)
    cabeza_p = coraza_kragtops('cabeza_kragtops', base=1.7, vetas=False)

    # ---------------- El cuerpo ----------------
    # La raíz, en el suelo: de ella cuelgan el cuerpo y las patas (así el cuerpo respira y se mece sin hundir las
    # pezuñas, y al morir se tumba entero).
    m.parte('raiz', None, (0, 0, 0))
    m.parte('cuerpo', 'raiz', (0, 15, 0))
    z0, z1 = Z_TRONCO_KRAGTOPS
    yc = (Y_VIENTRE_KRAGTOPS + Y_LOMO_KRAGTOPS) / 2
    hh = Y_LOMO_KRAGTOPS - Y_VIENTRE_KRAGTOPS
    zc, dd = (z0 + z1) / 2, z1 - z0
    # El tronco, con los costados en escalones (cajas cruzadas) y la cadera redondeada por detrás y por abajo: la parte
    # de abajo acaba 3 px antes que la de arriba.
    m.caja('cuerpo', (0, yc, zc + 1.5), (ANCHO_TRONCO_KRAGTOPS, hh - 2, dd - 3), piedra)
    m.caja('cuerpo', (0, yc, zc + 1.5), (ANCHO_TRONCO_KRAGTOPS - 2, hh, dd - 4), piedra)
    m.caja('cuerpo', (0, (Y_VIENTRE_KRAGTOPS + 4 + Y_LOMO_KRAGTOPS) / 2, zc), (ANCHO_TRONCO_KRAGTOPS - 1, Y_LOMO_KRAGTOPS - Y_VIENTRE_KRAGTOPS - 4, dd), piedra)
    # La coraza: una losa casi negra de arriba plano, con su banda de olas en los costados.
    cz0, cz1 = Z_CORAZA_KRAGTOPS
    caras_coraza = {'arriba': coraza, 'abajo': coraza, 'izq': banda, 'der': banda, 'frente': tapa, 'atras': tapa}
    m.caja('cuerpo', (0, (Y_LOMO_KRAGTOPS - 1 + Y_CORAZA_KRAGTOPS) / 2, (cz0 + cz1) / 2),
           (ANCHO_TRONCO_KRAGTOPS + 1, Y_CORAZA_KRAGTOPS - Y_LOMO_KRAGTOPS + 1, cz1 - cz0), caras_coraza)
    # Las losas de los hombros y de los muslos, inclinadas.
    for lado in (1, -1):
        m.caja('cuerpo', (lado * (ANCHO_TRONCO_KRAGTOPS / 2 + 0.8), Y_VIENTRE_KRAGTOPS + 3.5, 12.0), (3.0, 11.0, 11.0), losa,
               rot=(-12, 0, lado * 8))
        m.caja('cuerpo', (lado * (ANCHO_TRONCO_KRAGTOPS / 2 + 0.9), Y_VIENTRE_KRAGTOPS + 6.0, -4.0), (3.5, 9.0, 8.0), losa,
               rot=(-22, 0, lado * 8))
    cristales_kragtops(m, 'cuerpo', cristal, punta_cristal)

    # ---------------- La cabeza, con la gorguera ----------------
    m.parte('cabeza', 'cuerpo', (0, 15, 19))
    # El cuello (casi no se ve) y la cabeza: pequeña, baja y de piedra oscura.
    m.caja('cabeza', (0, 14.0, 20.5), (10, 8, 6), cabeza_p)
    caras_cabeza = {'frente': cara, 'atras': cabeza_p, 'izq': cabeza_p, 'der': cabeza_p, 'arriba': cabeza_p,
                    'abajo': cabeza_p}
    m.caja('cabeza', (0, 11.75, 25.5), (9, 6.5, 8), caras_cabeza)
    # El cuerno del morro: el más grande, casi de pie (16° hacia delante), encima de la cara: los ojos quedan debajo.
    m.caja_desde('cabeza', (0, 15.0, 26.3), (6, 10, 6), hueso, rot=(16, 0, 0))
    # Los cuernos de la frente: detrás del del morro, en la unión con la gorguera, hacia arriba, muy abiertos hacia
    # fuera y algo echados hacia atrás (el cercano se ve en medio de la gorguera; el lejano asoma arriba).
    for lado in (1, -1):
        m.caja_desde('cabeza', (lado * 8.0, 18.5, 19.0), (5, 8.5, 4.5), hueso, rot=(-15, 0, -lado * 50))
    gorguera_kragtops(m, 'cabeza', placa, placa, panel, placa_det, hueso_liso, columna)

    # ---------------- Las patas ----------------
    for lado, ld in ((1, 'i'), (-1, 'd')):
        for nom, x, z, ancho in (('del', 6.5, 14.5, 6.0), ('tra', 6.0, -5.5, 6.5)):
            n = m.parte(f'pata_{nom}_{ld}', 'raiz', (lado * x, Y_VIENTRE_KRAGTOPS + 3.0, z))
            m.caja(n, (lado * x, (3.0 + Y_VIENTRE_KRAGTOPS + 4.0) / 2, z), (ancho, Y_VIENTRE_KRAGTOPS + 1.0, ancho), pata)
            p = m.parte(f'pezuna_{nom}_{ld}', n, (lado * x, 3.0, z))
            m.caja(p, (lado * x, 1.5, z + 0.3), (ancho + 1.0, 3.0, ancho + 0.4), pezuna)
            m.caja(p, (lado * x, 1.25, z + 0.8), (ancho - 0.6, 2.5, ancho + 1.0), pezuna)

    # ---------------- La cola, con la maza ----------------
    # La cola: corta, recta y algo caída. La base, gruesa, sale de lo alto de la cadera; el tramo de la maza es una vara
    # parda más fina que acaba en una punta oscura un poco levantada; la maza va pegada por abajo.
    m.parte('cola', 'cuerpo', (0, 15.0, -10.5))
    m.caja('cola', (0, 14.75, -13.0), (7.0, 7.0, 5.0), cola_p)
    for z in (-12.0, -14.5):
        m.caja_desde('cola', (0, 18.15, z), (2, 2, 2.2), hueso_liso, rot=(-20, 0, 0))
    m.parte('cola2', 'cola', (0, 15.0, -15.5))
    m.caja('cola2', (0, 15.25, -21.0), (5.0, 4.5, 11.0), cola_p, rot=(-3, 0, 0))
    Mp = T(0, 15.6, -26.5) @ B.girar((-22, 0, 0))
    caja_kragtops(m, 'cola2', Mp, -1.75, -1.5, -3.5, 3.5, 3.0, 3.5, cola_p)
    # La maza: a cada lado de la mitad de abajo de la vara, dos bloques de hueso escalonados: el de delante, largo y
    # algo más bajo; el de atrás, más corto, 1 px más alto, que sobresale más por el costado y pasa la punta de la vara
    # (de lado se ve una barra blanca con una muesca; desde arriba, los lóbulos de la maza a los dos lados).
    for lado in (1, -1):
        m.caja('cola2', (lado * 3.4, 12.8, -20.75), (2.0, 3.6, 9.5), hueso)
        m.caja('cola2', (lado * 3.9, 13.1, -28.0), (3.4, 4.6, 5.0), hueso)


    m.mirar(('cabeza', 0.4))
    animaciones_kragtops(m)
    return m


# ======================================================================================================================
#  Las animaciones
# ======================================================================================================================
PATAS_KRAGTOPS = (('pata_del_i', 0.0), ('pata_tra_d', 0.0), ('pata_del_d', 0.5), ('pata_tra_i', 0.5))


def _paso_kragtops(a, largo, amp, alza):
    """Las patas en diagonal: cada una va hacia delante levantada y vuelve apoyada; la pezuña queda plana."""
    for nombre, f in PATAS_KRAGTOPS:
        pez = nombre.replace('pata', 'pezuna')
        claves, claves_p, claves_m = [], [], []
        for i in range(9):
            t = largo * i / 8
            fase = (i / 8 + f) % 1.0
            ang = amp * math.sin(math.tau * fase)                 # + : la pata hacia delante
            sube = alza * max(0.0, math.sin(math.tau * fase + math.pi / 2)) if math.cos(math.tau * fase) > 0 else 0.0
            claves.append((t, -ang, 0, 0))
            claves_p.append((t, ang, 0, 0))
            claves_m.append((t, 0, sube, 0))
        a.rot(nombre, claves)
        a.rot(pez, claves_p)
        a.mov(nombre, claves_m)


def _tumbar_kragtops(theta, qx):
    """El giro de la raíz alrededor del canto del costado (x = qx, en el suelo) en vez de alrededor del centro: lo que
    hay que moverla para que gire 'theta' grados sobre ese canto."""
    t = math.radians(theta)
    return qx * (1 - math.cos(t)), -qx * math.sin(t)


def animaciones_kragtops(m):
    # Reposo: respira despacio (el cuerpo sube y baja 0,25 px sobre las patas) y mira a un lado y a otro con la
    # gorguera; la cola apenas se mece.
    r = m.anim('reposo', 4.0, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.25, periodo=4.0)
    r.rot('cabeza', [(0, 0, 0, 0), (1.0, 3, 7, 0), (2.0, 0, 0, 0), (3.0, 3, -7, 0), (4.0, 0, 0, 0)])
    r.onda('cola', 'r', 1, 3, periodo=4.0, fase=0.25)
    r.onda('cola2', 'r', 1, 1.5, periodo=4.0, fase=0.35)
    # Andar: lento y pesado, las patas en diagonal; el cuerpo apenas sube y baja y se mece; la cola, rígida de la mitad
    # hacia atrás, se balancea poco.
    a = m.anim('andar', 1.4, bucle=True)
    _paso_kragtops(a, 1.4, 16, 1.0)
    a.onda('cuerpo', 'm', 1, 0.4, periodo=0.7, fase=0.25)
    a.onda('cuerpo', 'r', 2, 1.5, periodo=1.4)
    a.onda('cabeza', 'r', 0, 2.5, periodo=0.7)
    a.onda('cola', 'r', 1, 5, periodo=1.4, fase=0.5)
    a.onda('cola2', 'r', 1, 2, periodo=1.4, fase=0.6)
    # Correr (cuando persigue: la embestida, como en el clip de Soarinng): la cabeza baja, con la gorguera de cara,
    # abierta en abanico por delante, y las patas van más rápido.
    c = m.anim('correr', 0.7, bucle=True)
    _paso_kragtops(c, 0.7, 24, 1.6)
    c.rot('cabeza', [(0, 30, 0, 0), (0.35, 26, 0, 0), (0.7, 30, 0, 0)])
    c.onda('cuerpo', 'm', 1, 0.8, periodo=0.35, fase=0.25)
    c.onda('cuerpo', 'r', 0, 1.5, periodo=0.35)
    c.onda('cola', 'r', 1, 7, periodo=0.7, fase=0.5)
    # Ataque (la embestida): baja la cabeza con la gorguera por delante, se lanza hacia delante y da un cabezazo hacia
    # arriba con los cuernos.
    at = m.anim('ataque', 0.8)
    at.rot('cabeza', [(0, 0, 0, 0), (0.25, 36, 0, 0), (0.42, -20, 0, 0), (0.6, -6, 0, 0), (0.8, 0, 0, 0)])
    at.mov('cabeza', [(0, 0, 0, 0), (0.25, 0, -1.0, 0.5), (0.42, 0, 1.0, 2.5), (0.8, 0, 0, 0)])
    at.mov('cuerpo', [(0, 0, 0, 0), (0.25, 0, -0.6, -1.0), (0.42, 0, 0.3, 2.5), (0.8, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.25, 3, 0, 0), (0.42, -3, 0, 0), (0.8, 0, 0, 0)])
    for nombre in ('pata_del_i', 'pata_del_d'):
        # Las patas de delante empujan: se van atrás y luego adelante; la pezuña sigue plana en el suelo.
        at.rot(nombre, [(0, 0, 0, 0), (0.25, 8, 0, 0), (0.42, -10, 0, 0), (0.8, 0, 0, 0)])
        at.rot(nombre.replace('pata', 'pezuna'), [(0, 0, 0, 0), (0.25, -8, 0, 0), (0.42, 10, 0, 0), (0.8, 0, 0, 0)])
        at.mov(nombre, [(0, 0, 0, 0), (0.25, 0, 0.6, 0), (0.42, 0, 0.8, 0), (0.8, 0, 0, 0)])
    # Especial: el golpe de cola, como el anquilosaurio: gira la cola de lado desde la base, con el tramo de la maza
    # recto, y el cuerpo se tuerce un poco al revés.
    e = m.anim('especial', 1.2)
    e.rot('cola', [(0, 0, 0, 0), (0.35, 0, -38, 0), (0.6, 0, 48, 0), (0.85, 0, 20, 0), (1.2, 0, 0, 0)])
    e.rot('cola2', [(0, 0, 0, 0), (0.35, 0, -6, 0), (0.6, 0, 10, 0), (1.2, 0, 0, 0)])
    e.rot('cuerpo', [(0, 0, 0, 0), (0.35, 0, 5, 2), (0.6, 0, -6, -2), (1.2, 0, 0, 0)])
    e.rot('cabeza', [(0, 0, 0, 0), (0.35, 0, -8, 0), (0.6, 0, 8, 0), (1.2, 0, 0, 0)])
    # Muerte: se le doblan las patas de delante, cae sobre el pecho y se tumba de lado sobre el canto de las placas.
    d = m.anim('muerte', 1.6)
    for nombre in ('pata_del_i', 'pata_del_d'):
        d.rot(nombre, [(0, 0, 0, 0), (0.45, 40, 0, 0), (1.6, 30, 0, 0)])
        d.mov(nombre, [(0, 0, 0, 0), (0.2, 0, 1.4, 0), (0.45, 0, 0.6, 0), (1.6, 0, 0.6, 0)])
    for nombre in ('pata_tra_i', 'pata_tra_d'):
        d.rot(nombre, [(0, 0, 0, 0), (0.6, 20, 0, 0), (1.6, 15, 0, 0)])
        d.mov(nombre, [(0, 0, 0, 0), (0.3, 0, 0.9, 0), (0.6, 0, 0.5, 0), (1.6, 0, 0.5, 0)])
    d.mov('cuerpo', [(0, 0, 0, 0), (0.45, 0, -3.0, 0), (1.6, 0, -2.5, 0)])
    d.rot('cuerpo', [(0, 0, 0, 0), (0.45, 7, 0, 0), (1.6, 3, 0, 0)])
    d.rot('cabeza', [(0, 0, 0, 0), (0.45, 12, 0, 0), (1.6, 4, -10, 0)])
    d.rot('cola', [(0, 0, 0, 0), (1.6, 0, 15, 0)])
    claves_r, claves_m = [(0, 0, 0, 0)], [(0, 0, 0, 0)]
    for t, th in ((0.45, 0.0), (0.75, 20.0), (1.0, 45.0), (1.2, 66.0), (1.35, 76.0), (1.45, 72.0), (1.6, 74.0)):
        dx, dy = _tumbar_kragtops(th, -12.5)
        claves_r.append((t, 0, 0, th))
        claves_m.append((t, dx, dy, 0))
    d.rot('raiz', claves_r)
    d.mov('raiz', claves_m)
    # Aparece: sale del suelo, se sacude el polvo y alza la gorguera.
    ap = m.anim('aparece', 1.4)
    ap.mov('raiz', [(0, 0, -14, 0), (0.6, 0, -2, 0), (0.8, 0, 0.5, 0), (1.0, 0, 0, 0)])
    ap.rot('cuerpo', [(0, 0, 0, 0), (0.6, -6, 0, 3), (0.8, 2, 0, -3), (1.0, 0, 0, 2), (1.2, 0, 0, 0)])
    ap.rot('cabeza', [(0, 18, 0, 0), (0.7, 6, 0, 0), (0.9, -14, 0, 0), (1.1, -4, 8, 0), (1.25, -4, -8, 0),
                      (1.4, 0, 0, 0)])


HUEVO = (('7a7262', '4e463c', '2e2820'), ('343632', '121411'),
         [((6, 2), '6a8ec6'), ((7, 2), 'a8c2ea'), ((8, 3), '6a8ec6'), ((5, 3), '3e66a8'),
          ((10, 6), 'f4ebe5'), ((11, 5), 'ddd3cc'), ((10, 7), 'f4ebe5'),
          ((4, 8), '43453f'), ((5, 8), '43453f'), ((6, 9), '43453f'),
          ((3, 10), 'f4ebe5'), ((4, 10), 'ddd3cc')])

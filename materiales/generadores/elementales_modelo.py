"""
Bocetos 3D de tres jefes de otros tipos (ficha de diseno, 12-10-2026), despues
de que a Juan le gustara Espinara (la naturaleza): «ahora crea otros que ya no
sean con forma de serpiente… de otros tipos… creados por ti, no de bloques…
criaturas que no existan, compuestas de varias y con algo nuevo».

Cada uno con su forma de cuerpo y su tipo (el mod ya tiene agua, tierra de
jade, viento, fuego y, con Espinara, la naturaleza):

  A  Boreala, la Zancuda del Norte      HIELO
     seis patas de zancuda + caparazon de glaciar + cuello y lanza de garza +
     barbas de carambano + tres ojos por lado + abanico de plumas de escarcha;
     lo nuevo: la aurora boreal le sale del lomo como una vela de luz
  B  Nocturna, la Bestia sin Cielo      NOCHE / VACIO
     bestia encorvada que anda sobre los nudillos + alas de murcielago plegadas
     como un manto + lunas por espinas (de la llena a la mas fina) + craneo sin
     ojos que se abre de lado como unas pinzas; lo nuevo: se ha comido el cielo,
     lo lleva en la piel con sus constelaciones, y en el pecho una estrella negra
  C  Duneara, la que Nada en la Arena   ARENA / SOL
     aletas de raya + caparazon de escarabajo + cola de escorpion + mandibulas de
     hormiga leon; lo nuevo: la boca es un pozo de arena movediza que gira hacia
     el ambar, y en la punta de la cola lleva un segundo sol

Se construyen en bloques de mundo con las ayudas de quimeras_modelo (cajas,
paneles, prismas), y sus materiales son losetas dibujadas aqui (escarcha en
helecho, glaciar agrietado, cielo con constelaciones, plata, duna rizada,
placas de escarabajo con incrustaciones...), nada de vanilla. Los que van en
ADITIVOS (la aurora, la nebulosa) se pintan como luz: suman, no tapan.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm

TAU = math.tau
D = vr.D2R
caja, panel, hebra, oct_y, oct_z, disco_z, punto = qm.caja, qm.panel, qm.hebra, qm.oct_y, qm.oct_z, qm.disco_z, qm.punto
_r, _vacia, _mezcla, _celdas, _trazo, _linea = qm._r, qm._vacia, qm._mezcla, qm._celdas, qm._trazo, qm._linea

# ----------------------------------------------------------------------
#  Rampas
# ----------------------------------------------------------------------
HIELO = _r('16365a', '2f6a8e', '6aa8c4', 'a8d8ea', 'e2f6ff')
HIELO_C = _r('3a7a9e', '74b2cc', 'a6d6e6', 'd2eef6', 'f6fdff')
HUESO_F = _r('34404e', '5c6e82', '8ea2b4', 'bccad6', 'e4eef4')
NOCHE = _r('04051a', '090b24', '0f1232', '171b42', '222858')
PLATA = _r('545866', '828696', 'aeb2c0', 'd0d4de', 'eef0f6')
BASALTO = _r('07070d', '0d0d17', '151522', '1e1e2e', '2a2a3e')
OCRE = _r('3a2410', '66421e', '966630', 'c4964e', 'e6c278')
DUNA = _r('8a6838', 'ac884c', 'c6a262', 'dcbc7e', 'f0d8a0')
TURQUESA = _r('0a4a44', '167a6e', '26a898', '62d2c2')
LAPIS = _r('0c1448', '16267a', '2238a4', '3654c4', '6484dc')
DIENTE_S = _r('86703e', 'b49854', 'd6ba74', 'ead296', 'fff0c4')


# ----------------------------------------------------------------------
#  Materiales de Boreala
# ----------------------------------------------------------------------
def _hielo(semilla):
    """Glaciar: bloques de hielo con la red de fracturas azul hondo, el canto escarchado
    a la luz y, en algunas grietas, la aurora que asoma (emisivo aparte)."""
    d1, d2, idx, sx, sy = _celdas(semilla, 7)
    r = random.Random(semilla)
    t = _vacia()
    e = _vacia()
    aur = [nm._hex('5affb0'), nm._hex('9a7aff')]
    for y in range(32):
        for x in range(32):
            ed = d2[y, x] - d1[y, x]
            b = 2 if r.random() > 0.2 else 3
            if ed < 0.8:
                b = 0
                if idx[y, x] % 3 == 0:
                    t[y, x] = (*aur[idx[y, x] % 2], 255)
                    e[y, x] = (*aur[idx[y, x] % 2], 190)
                    continue
            elif ed < 1.8:
                b = 4 if sx[y, x] + sy[y, x] < 0 else 1
            elif d1[y, x] > 5 and r.random() < 0.08:
                b = 3
            t[y, x] = (*HIELO[b], 255)
    for _ in range(3):
        _trazo(t, r, r.uniform(0, 32), r.uniform(0, 32), r.randint(5, 9), HIELO[4], giro=0.2)   # el brillo de dentro
    return t, e


def _hielo_claro(semilla):
    """Carambanos y cristal: vetas verticales y un filo de luz."""
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            b = (2, 3, 3, 4, 3, 2, 1, 2)[(x + (y // 11)) % 8]
            if r.random() < 0.06:
                b = 4
            t[y, x] = (*HIELO_C[b], 255)
    return t


def _hueso_frio(semilla):
    t = qm._hueso(semilla, HUESO_F)
    r = random.Random(semilla)
    for _ in range(4):
        x, y = r.randrange(32), r.randrange(32)
        for k in range(r.randint(3, 6)):
            t[(y + k) % 32, x] = (*HIELO_C[4], 255)                          # escarcha pegada
    return t


def _escarcha(semilla):
    """Escarcha: helechos de cristal blanco que crecen sobre azul palido."""
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            t[y, x] = (*HIELO_C[1 if r.random() < 0.7 else 2], 255)

    def helecho(x, y, a, largo, nivel):
        for k in range(largo):
            t[int(y) % 32, int(x) % 32] = (*HIELO_C[4 if k < largo - 2 else 3], 255)
            if nivel < 2 and k % 3 == 1:
                helecho(x, y, a + 0.9, max(2, largo // 2), nivel + 1)
                helecho(x, y, a - 0.9, max(2, largo // 2), nivel + 1)
            x += math.cos(a)
            y += math.sin(a)

    for _ in range(4):
        helecho(r.uniform(0, 32), r.uniform(0, 32), r.uniform(0, TAU), r.randint(7, 11), 0)
    return t


def _aurora():
    """La cortina de aurora (32 x 64, se pinta como luz): abajo un filo verde vivo y
    recortado, y hacia arriba rayos que suben y se apagan en violeta."""
    t = _vacia(32, 64)
    vio, ver, cia = nm._hex('8a5aff'), nm._hex('4affa0'), nm._hex('d8fff2')
    for y in range(64):
        k = 1.0 - y / 63.0                                   # 0 abajo, en el filo; 1 arriba
        for x in range(32):
            rayo = 0.12 + 0.88 * (0.5 + 0.5 * math.sin(x * 0.9 + 2.0 * math.sin(x * 0.37 + k * 1.5))) ** 3
            if k < 0.05:
                c = _mezcla(cia, ver, k / 0.05)
            elif k < 0.42:
                c = ver
            else:
                c = _mezcla(ver, vio, (k - 0.42) / 0.58)
            a = 1.0 if k < 0.03 else rayo * (1.0 - k) ** 0.6
            t[y, x] = (*c, int(max(0, min(255, a * 240))))
    return t


# ----------------------------------------------------------------------
#  Materiales de Nocturna
# ----------------------------------------------------------------------
def _noche(semilla, w=32, h=32):
    """La piel de Nocturna: terciopelo de anil con estrellas (alguna con su cruz) y
    las lineas tenues de una constelacion; las estrellas brillan (emisivo aparte)."""
    r = random.Random(semilla)
    t = _vacia(w, h)
    e = _vacia(w, h)
    for y in range(h):
        for x in range(w):
            b = r.choice((1, 1, 2, 2, 3)) if (x * 7 + y * 3) % 5 else 1
            t[y, x] = (*NOCHE[b], 255)
    estrellas = [(r.randrange(w), r.randrange(h)) for _ in range(int(w * h / 90))]
    for (a, b_) in zip(estrellas[:5], estrellas[1:6]):
        n = int(max(abs(b_[0] - a[0]), abs(b_[1] - a[1]))) + 1
        for k in range(n + 1):
            x = int(round(a[0] + (b_[0] - a[0]) * k / n)) % w
            y = int(round(a[1] + (b_[1] - a[1]) * k / n)) % h
            t[y, x] = (*NOCHE[4], 255)
            e[y, x] = (*nm._hex('6a78c8'), 70)
    for k, (x, y) in enumerate(estrellas):
        c = nm._hex('f2f6ff') if k % 3 else nm._hex('c8d8ff')
        t[y, x] = (*c, 255)
        e[y, x] = (*c, 255)
        if k % 4 == 0:
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                t[(y + dy) % h, (x + dx) % w] = (*nm._hex('8a9ae8'), 255)
                e[(y + dy) % h, (x + dx) % w] = (*nm._hex('8a9ae8'), 150)
    return t, e


def _membrana_noche(semilla):
    """El ala plegada (64 x 128, una imagen por tramo): el cielo de noche con su
    constelacion, nervios de plata que salen de la muneca y el borde libre de
    arriba recortado en arco, como el de un ala de murcielago."""
    t, e = _noche(semilla, 64, 128)
    for x in range(64):
        borde = int(3 + 20 * math.sin(math.pi * (x + 0.5) / 64))
        for y in range(borde):
            t[y, x] = (0, 0, 0, 0)
            e[y, x] = (0, 0, 0, 0)
        t[borde, x] = (*PLATA[3], 255)
        t[borde + 1, x] = (*PLATA[1], 255)
        e[borde, x] = e[borde + 1, x] = (0, 0, 0, 0)
    for k in range(3):                                       # nervios desde abajo en medio
        x1 = 12 + k * 20
        for j in range(100):
            u = j / 99
            x = int(round(32 + (x1 - 32) * u))
            y = int(round(127 - 100 * u))
            if t[y, x, 3] and e[y, x, 3] == 0:
                t[y, x] = (*PLATA[0], 255)
    return t, e


def _plata(semilla):
    """Hueso de plata (costillas, lunas, garras): fino, con lineas de crecimiento."""
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            b = 2 if r.random() > 0.2 else 3
            if (x + int(y * 0.3)) % 9 == 0:
                b = 1
            if (x * 3 + y) % 23 == 0:
                b = 4
            t[y, x] = (*PLATA[b], 255)
    return t


def _vacio(semilla):
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            c = (2, 1, 5) if r.random() > 0.08 else (10, 6, 22)
            t[y, x] = (*c, 255)
    return t


def _nebulosa():
    """Nube de luz (se pinta como luz): un halo suave, teal por dentro y violeta fuera."""
    t = _vacia()
    for y in range(32):
        for x in range(32):
            d = math.hypot(x - 15.5, y - 15.5) / 15.5
            c = _mezcla(nm._hex('9afff0'), nm._hex('7a4aff'), d)
            t[y, x] = (*c, int(max(0, (1 - d)) ** 1.6 * 220))
    return t


def _luna():
    """La cara de Nocturna (64 x 64, una imagen por cara): la luna llena, plata palida con
    sus mares oscuros, crateres con el borde a la luz y el canto que se apaga."""
    r = random.Random(81)
    rng = np.random.default_rng(81)
    LUNA = _r('4a5062', '6e7690', '9aa2b6', 'c2c8d6', 'e4e8f2')
    v = qm._ruido_tile(rng, 64, 4) * 0.6 + qm._ruido_tile(rng, 64, 8) * 0.3 + qm._ruido_tile(rng, 64, 16) * 0.1
    v = (v - v.min()) / (v.max() - v.min())
    t = _vacia(64, 64)
    for y in range(64):
        for x in range(64):
            d = math.hypot(x - 31.5, y - 31.5) / 32.0
            b = 3 if v[y, x] > 0.42 else 2 if v[y, x] > 0.26 else 1
            if d > 0.88:
                b = max(1, b - 1)
            t[y, x] = (*LUNA[b], 255)
    for _ in range(16):
        cx, cy, rr = r.uniform(6, 58), r.uniform(6, 58), r.uniform(1.6, 5.0)
        for y in range(int(cy - rr - 2), int(cy + rr + 2)):
            for x in range(int(cx - rr - 2), int(cx + rr + 2)):
                if not (0 <= x < 64 and 0 <= y < 64):
                    continue
                d = math.hypot(x - cx, y - cy)
                if d < rr - 0.8:
                    t[y, x] = (*LUNA[1], 255)
                elif d < rr + 0.6:
                    t[y, x] = (*(LUNA[4] if (x - cx) + (y - cy) < 0 else LUNA[0]), 255)
    return t


def _basalto(semilla):
    """La roca de la llanura sin cielo: facetas oscuras con polvo de plata."""
    d1, d2, idx, sx, sy = _celdas(semilla, 6)
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            ed = d2[y, x] - d1[y, x]
            b = 1 + idx[y, x] % 2
            if ed < 0.9:
                b = 0
            elif ed < 1.8 and sx[y, x] + sy[y, x] < 0:
                b = 3
            c = BASALTO[b]
            if r.random() < 0.03:
                c = PLATA[1]
            t[y, x] = (*c, 255)
    return t


# ----------------------------------------------------------------------
#  Materiales de Duneara
# ----------------------------------------------------------------------
def _caparazon_sol(semilla):
    """Placas de escarabajo color ocre con el canto de oro y una incrustacion turquesa en
    el centro de cada una (como una joya del desierto)."""
    d1, d2, idx, sx, sy = _celdas(semilla, 7)
    r = random.Random(semilla)
    base = [r.choice((1, 2, 2, 3)) for _ in range(7)]
    t = _vacia()
    for y in range(32):
        for x in range(32):
            ed = d2[y, x] - d1[y, x]
            b = base[idx[y, x]]
            if ed < 0.8:
                c = OCRE[0]
            elif ed < 1.7:
                c = qm.ORO[3] if sx[y, x] + sy[y, x] < 0 else qm.ORO[1]
            elif d1[y, x] < 1.4:
                c = TURQUESA[3]
            elif d1[y, x] < 2.4:
                c = TURQUESA[1]
            else:
                c = OCRE[b] if r.random() > 0.1 else OCRE[max(0, b - 1)]
            t[y, x] = (*c, 255)
    return t


def _duna(semilla, rampa=DUNA):
    """Arena rizada por el viento: ondas paralelas que se tuercen, con su sombra."""
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            ond = (y + 2.2 * math.sin(x / 32 * TAU * 2 + 0.6) + 1.2 * math.sin(x / 32 * TAU * 3)) % 6
            b = 3 if ond < 1.2 else 1 if ond < 2.0 else 2
            if r.random() < 0.05:
                b = 4 if b > 1 else 2
            t[y, x] = (*rampa[b], 255)
    return t


def _ojo_compuesto():
    """El ojo de Duneara: facetas de panal color ambar, cada una con su brillo y el borde
    oscuro (emisivo aparte, a medias)."""
    centros = []
    for fila in range(-1, 10):
        for col in range(-1, 10):
            centros.append((col * 4.0 + (2.0 if fila % 2 else 0.0), fila * 3.46))
    t = _vacia()
    for y in range(32):
        for x in range(32):
            ds = sorted((math.hypot(x + 0.5 - cx, y + 0.5 - cy), cx, cy) for cx, cy in centros)
            (d1, cx, cy), d2 = ds[0], ds[1][0]
            if d2 - d1 < 0.55:
                c = nm._hex('5a2604')
            elif (x + 0.5 - cx) + (y + 0.5 - cy) < -0.8:
                c = nm._hex('fff2b0')
            else:
                c = nm._hex('ffc040') if d1 < 1.2 else nm._hex('e8901a')
            t[y, x] = (*c, 255)
    e = t.copy()
    e[..., 3] = np.where(t[..., 0] > 200, 170, 0).astype(np.uint8)
    return t, e


def _remolino(semilla):
    """La arena que cae al pozo de la boca: vetas en diagonal (en el embudo hacen espiral)."""
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            k = (x + y * 0.9 + 1.5 * math.sin(y / 32 * TAU)) % 8
            b = 3 if k < 1.4 else 1 if k < 3.0 else 2
            if r.random() < 0.06:
                b = max(0, b - 1)
            t[y, x] = (*DUNA[b], 255)
    return t


def _lapis(semilla):
    """El caparazon de Duneara: lapislazuli azul vivo, pulido (cada veta se aclara hacia la
    luz), con vetas palidas y motas de pirita."""
    d1, d2, idx, sx, sy = _celdas(semilla, 5)
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            b = 2 + (1 if sx[y, x] + sy[y, x] < -2.5 else 0) - (1 if sx[y, x] + sy[y, x] > 3.5 else 0)
            if d2[y, x] - d1[y, x] < 0.7:
                b = 1
            c = LAPIS[b]
            if r.random() < 0.04:
                c = LAPIS[min(4, b + 1)]
            if r.random() < 0.022:
                c = qm.ORO[4]
            t[y, x] = (*c, 255)
    for _ in range(2):
        _trazo(t, r, r.uniform(0, 32), r.uniform(0, 32), r.randint(6, 11), LAPIS[4], giro=0.3)
    return t


def _aleta(semilla, punta=False):
    """Un tramo de aleta (32 x 64; la raiz abajo y lo de fuera arriba): bandas de anil,
    radios de oro hacia fuera, ocelos turquesa y, en el ultimo tramo, el borde deshecho en arena."""
    r = random.Random(semilla)
    t = _vacia(32, 64)
    ocelos = [(r.uniform(4, 28), r.uniform(12, 50)) for _ in range(4)]
    for y in range(64):
        for x in range(32):
            banda = int((x * 0.3 + y) / 6) % 3
            c = (LAPIS[1], LAPIS[2], LAPIS[1])[banda] if banda != 2 else LAPIS[0]
            if r.random() < 0.05:
                c = LAPIS[3]
            for (ox, oy) in ocelos:
                d = math.hypot(x - ox, (y - oy) * 0.8)
                if d < 1.5:
                    c = LAPIS[0]
                elif d < 3.0:
                    c = TURQUESA[3]
                elif d < 4.0:
                    c = qm.ORO[3]
            if x % 8 == 3:
                c = qm.ORO[3] if y % 9 else qm.ORO[1]
            elif x % 8 == 4:
                c = qm.ORO[1]
            if punta:
                borde = 8 + int(abs(math.sin(x * 0.55)) * 5 + r.uniform(0, 3))
                if y < borde:
                    continue
                if y < borde + 2:
                    c = DUNA[3]
            t[y, x] = (*c, 255)
    return t


# ----------------------------------------------------------------------
#  Suelos (128 px = 4 bloques, casan por los bordes)
# ----------------------------------------------------------------------
def _suelo_ondas(semilla, rampa, frec, fuerza, tuerce=1.6, chispas=None):
    """Suelo rizado (nieve con sastrugi, arena de duna): ruido de varias escalas y unas
    ondas torcidas con la cara al viento clara y la sombra detras de la cresta."""
    rng = np.random.default_rng(semilla)
    n = 128
    base = qm._ruido_tile(rng, n, 4) * 0.6 + qm._ruido_tile(rng, n, 8) * 0.25 + qm._ruido_tile(rng, n, 32) * 0.15
    base = (base - base.min()) / (base.max() - base.min())
    giro = qm._ruido_tile(rng, n, 4)
    ys, xs = np.mgrid[0:n, 0:n]
    fase = (ys / n * frec + giro * tuerce + xs / n) % 1.0
    onda = np.where(fase < 0.3, 1.0, np.where(fase < 0.42, 0.0, 0.55))
    v = base * (1 - fuerza) + onda * fuerza
    t = np.zeros((n, n, 4), np.uint8)
    b = np.searchsorted((0.25, 0.42, 0.6, 0.8), v)
    for i in range(5):
        t[b == i] = (*rampa[i], 255)
    if chispas:
        r = random.Random(semilla)
        for _ in range(140):
            t[r.randrange(n), r.randrange(n)] = (*chispas, 255)
    return t


# ----------------------------------------------------------------------
#  El registro (en el de quimeras_modelo, que es el que pinta)
# ----------------------------------------------------------------------
ADITIVOS = set()


def _reg(nombre, tex, emis=None, pleno=False, estira=False, aditivo=False):
    qm._reg(nombre, tex, emis, pleno, estira)
    if aditivo:
        ADITIVOS.add(nombre)


_t, _e = _hielo(41)
_reg('hielo', _t, _e)
_reg('hielo_claro', _hielo_claro(42))
_reg('hueso_frio', _hueso_frio(43))
_reg('escarcha', _escarcha(44))
_reg('aurora', _aurora(), estira=True, aditivo=True)
_reg('ojo_aurora', qm._emisivo('f0fffa', '3affd0'), pleno=True)
_reg('aurora_luz', qm._emisivo('d8fff0', '5affb0'), pleno=True)
_t, _e = _noche(51)
_reg('noche', _t, _e)
_t, _e = _membrana_noche(52)
_reg('membrana_noche', _t, _e, estira=True)
_reg('plata', _plata(53))
_reg('vacio', _vacio(54))
_reg('anillo', qm._emisivo('ffffff', '6af0e0'), pleno=True)
_reg('nebulosa', _nebulosa(), estira=True, aditivo=True)
_reg('basalto', _basalto(55))
_reg('caparazon_sol', _caparazon_sol(61))
_reg('duna', _duna(62))
_reg('remolino', _remolino(65))
_reg('lapis', _lapis(67))
_reg('aleta', _aleta(63), estira=True)
_reg('aleta_punta', _aleta(66, punta=True), estira=True)
_reg('nieve', _duna(74, _r('7890b0', '96acc8', 'b4c8dc', 'cfdeec', 'eaf2fa')))
_reg('diente_sol', qm._hueso(64, DIENTE_S))
_t = qm._emisivo('ffe08a', 'ff7a10', oscuro='7a3006', semilla=31)
_e = _t.copy()
_e[..., 3] = 150
_reg('ambar', _t, _e)
_t = _luna()
_e = _t.copy()
_e[..., 3] = 70
_reg('luna', _t, _e, estira=True)
_reg('ojo_sol', qm._emisivo('fffbe0', 'ffc42a'), pleno=True)
_t, _e = _ojo_compuesto()
_reg('ojo_compuesto', _t, _e)
_reg('suelo_nieve', qm._suelo_grande(71, _r('3e5474', '546c8e', '6c86a6', '88a0be', 'a8bed6'), nm._hex('e8f4ff'), grietas=False))
_reg('suelo_noche', qm._suelo_grande(72, BASALTO, PLATA[0]))
_reg('suelo_arena', _suelo_ondas(73, DUNA, 9, 0.45, tuerce=1.1))


# ----------------------------------------------------------------------
#  Ayudas de forma
# ----------------------------------------------------------------------
def _pasos(r, n):
    """Los rectangulos que redondean un circulo de radio r, como en un modelo de Minecraft:
    n escalones por cuarto, el mas ancho llega a r."""
    if n is None:
        n = 2 if r < 0.3 else 3 if r < 1.4 else 4
    k = 1.0 / math.cos(math.radians(90 / (n + 1)))
    return [(r * k * math.cos(math.radians(90 * (i + 1) / (n + 1))), r * k * math.sin(math.radians(90 * (i + 1) / (n + 1))))
            for i in range(n)]


def redondo_z(out, M, r, z0, z1, mat, n=None):
    """Un cilindro de pixel a lo largo de la z local."""
    for w, h in _pasos(r, n):
        caja(out, M, -w, -h, z0, 2 * w, 2 * h, z1 - z0, mat)


def redondo_y_(out, M, y0, y1, r, mat, n=None):
    redondo_y(out, M, y0, y1, r, mat, n)


def redondo_y(out, M, y0, y1, r, mat, n=None):
    """Un cilindro de pixel a lo largo de la y local."""
    for w, h in _pasos(r, n):
        caja(out, M, -w, y0, -h, 2 * w, y1 - y0, 2 * h, mat)


def escala(sx, sy, sz):
    return np.diag([sx, sy, sz, 1.0])


def ejes(p, ex, ey):
    """Marco en p con la x local hacia ex y la y lo mas cerca posible de ey."""
    ex = np.asarray(ex, float)
    ex = ex / np.linalg.norm(ex)
    ey = np.asarray(ey, float)
    ey = ey - ex * (ey @ ex)
    ey = ey / np.linalg.norm(ey)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = ex, ey, np.cross(ex, ey), p
    return M


def cuadro(out, P, UV, mat):
    out.append(([np.asarray(p, float) for p in P], UV, mat))


def segmento(out, p0, p1, r, mat, r1=None, piezas=1):
    """Un tramo octogonal de p0 a p1 (mundo), que puede ir afinando de r a r1."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    if L < 1e-4:
        return
    M = em.marco(p0, p1 - p0)
    r1 = r if r1 is None else r1
    for k in range(piezas):
        z0, z1 = L * k / piezas, L * (k + 1) / piezas
        rr = r + (r1 - r) * (k + 0.5) / piezas
        redondo_z(out, M, rr, z0, z1 + 0.02, mat)


def bola(out, M, r, mat, capas=6):
    for k in range(capas):
        y0 = -r + 2 * r * k / capas
        y1 = y0 + 2 * r / capas
        ym = (y0 + y1) / 2
        redondo_y(out, M, y0, y1, r * math.sqrt(max(0.05, 1 - (ym / r) ** 2)), mat)


def ovoide(out, M, rx, ry, rz, mat, capas=9, lados=8):
    """Un ovoide a lo largo de la z local (cortes de 8 o 16 lados; la y achatada)."""
    Ms = M @ escala(1.0, ry / rx, 1.0)
    for k in range(capas):
        z0 = -rz + 2 * rz * k / capas
        z1 = z0 + 2 * rz / capas
        zm = (z0 + z1) / 2
        r = rx * math.sqrt(max(0.04, 1 - (zm / rz) ** 2))
        redondo_z(out, Ms, r, z0, z1, mat, n=4 if lados == 16 else None)


def cristal(out, M, r, largo, mat):
    """Un cristal (o un carambano, o una pua) a lo largo de la y local, que acaba en punta."""
    redondo_y(out, M, -0.2, largo * 0.6, r, mat, n=2)
    redondo_y(out, M, largo * 0.6 - 0.02, largo * 0.85, r * 0.55, mat, n=2)
    caja(out, M, -r * 0.22, largo * 0.85 - 0.02, -r * 0.22, r * 0.44, largo * 0.15 + 0.02, r * 0.44, mat)


def media_luna(out, M, R, grosor, mat, c=0.25, n=10):
    """Una luna en el plano x-y local, con los cuernos hacia +x: c pequena es la mas
    fina, c grande la mas gorda (c >= 1, la luna llena)."""
    g = grosor / 2
    if c >= 1:
        for k in range(16):
            a0, a1 = k * TAU / 16, (k + 1) * TAU / 16
            for z in (g, -g):
                cuadro(out, [punto(M, (0, 0, z)), punto(M, (R * math.cos(a0), R * math.sin(a0), z)),
                             punto(M, (R * math.cos(a1), R * math.sin(a1), z)), punto(M, (0, 0, z))],
                       [(0.5, 0.5), (0, 0), (1, 0), (0.5, 0.5)], mat)
            cuadro(out, [punto(M, (R * math.cos(a0), R * math.sin(a0), g)), punto(M, (R * math.cos(a1), R * math.sin(a1), g)),
                         punto(M, (R * math.cos(a1), R * math.sin(a1), -g)), punto(M, (R * math.cos(a0), R * math.sin(a0), -g))],
                   [(0, 0), (1, 0), (1, 0.3), (0, 0.3)], mat)
        return
    ri = math.sqrt((0.866 - c) ** 2 + 0.25) * R
    ai = math.degrees(math.atan2(0.5, 0.866 - c))
    O = [(R * math.cos(math.radians(30 + 300 * k / n)), R * math.sin(math.radians(30 + 300 * k / n))) for k in range(n + 1)]
    I = [(c * R + ri * math.cos(math.radians(ai + (360 - 2 * ai) * k / n)), ri * math.sin(math.radians(ai + (360 - 2 * ai) * k / n)))
         for k in range(n + 1)]
    for k in range(n):
        for z in (g, -g):
            cuadro(out, [punto(M, (*O[k], z)), punto(M, (*O[k + 1], z)), punto(M, (*I[k + 1], z)), punto(M, (*I[k], z))],
                   [(0, 0), (1, 0), (1, 0.5), (0, 0.5)], mat)
        for A, B in ((O[k], O[k + 1]), (I[k], I[k + 1])):
            cuadro(out, [punto(M, (*A, g)), punto(M, (*B, g)), punto(M, (*B, -g)), punto(M, (*A, -g))],
                   [(0, 0), (1, 0), (1, 0.3), (0, 0.3)], mat)


def cortina(out, base, alturas, arriba, mat, u_por_bloque=None):
    """Una cortina de luz que sube desde una linea quebrada (el filo de abajo de la imagen
    va en la linea). Con u_por_bloque la imagen corre seguida por toda la cortina."""
    arriba = np.asarray(arriba, float)
    arriba = arriba / np.linalg.norm(arriba)
    u = 0.0
    for k in range(len(base) - 1):
        p, q = base[k], base[k + 1]
        if u_por_bloque:
            du = float(np.linalg.norm(q - p)) * u_por_bloque
            uv = [(u, 0.999), (u + du, 0.999), (u + du, 0.0), (u, 0.0)]
            u += du
        else:
            uv = [(0, 1), (1, 1), (1, 0), (0, 0)]
        cuadro(out, [p, q, q + arriba * alturas[k + 1], p + arriba * alturas[k]], uv, mat)


def losa(out, M, contorno, g, mat, uv=None, mat_canto=None):
    """Una losa de canto g (de z=0 a z=g) con la forma de un contorno convexo del plano
    x-y; uv da el punto de la imagen de cada vertice de la cara."""
    n = len(contorno)
    cx = sum(p[0] for p in contorno) / n
    cy = sum(p[1] for p in contorno) / n
    if uv is None:
        uv = [(p[0], p[1]) for p in contorno]
    cu = (sum(q[0] for q in uv) / n, sum(q[1] for q in uv) / n)
    for k in range(n):
        a, b = contorno[k], contorno[(k + 1) % n]
        ua, ub = uv[k], uv[(k + 1) % n]
        cuadro(out, [punto(M, (cx, cy, g)), punto(M, (*a, g)), punto(M, (*b, g)), punto(M, (cx, cy, g))], [cu, ua, ub, cu], mat)
        cuadro(out, [punto(M, (cx, cy, 0)), punto(M, (*b, 0)), punto(M, (*a, 0)), punto(M, (cx, cy, 0))], [cu, ub, ua, cu], mat)
        cuadro(out, [punto(M, (*a, 0)), punto(M, (*b, 0)), punto(M, (*b, g)), punto(M, (*a, g))], [(0, 0), (1, 0), (1, 0.3), (0, 0.3)],
               mat_canto or mat)


# ======================================================================
#  A · BOREALA, la Zancuda del Norte (hielo)
# ======================================================================
def lomo_boreala(z):
    return 14.0 + 2.6 * math.sqrt(max(0.05, 1 - (z / 5.8) ** 2))


def ancho_boreala(z):
    return 4.0 * math.sqrt(max(0.05, 1 - (z / 5.8) ** 2))


def boreala(boca=24.0, semilla=3):
    rng = random.Random(semilla)
    out = []
    Mc = vr.T(0, 14.0, 0)                                       # el centro del caparazon, mirando a +z
    ovoide(out, Mc, 4.0, 2.6, 5.8, 'hielo', capas=12, lados=16)
    # las placas del glaciar, dos hileras por lado, montadas como tejas
    for s in (1, -1):
        for k in range(6):
            z = -4.6 + k * 1.85
            h = lomo_boreala(z) - 14.0
            w_ = ancho_boreala(z)
            caja(out, vr.T(s * w_ * 0.42, 14.0 + h * 0.84, z) @ vr.Rz(-s * 24 * D) @ vr.Rx(-14 * D), -1.0, -0.25, -0.75, 2.0, 0.5, 1.6, 'hielo')
            caja(out, vr.T(s * w_ * 0.86, 14.0 + h * 0.2, z + 0.9) @ vr.Rz(-s * 64 * D) @ vr.Rx(-10 * D), -0.9, -0.25, -0.7, 1.8, 0.45, 1.5, 'hielo')
    # cristales que le crecen de los costados, hacia fuera y arriba
    for k in range(12):
        s = 1 if k % 2 else -1
        z = -4.6 + (k // 2) * 1.8 + rng.uniform(-0.4, 0.4)
        M = vr.T(s * ancho_boreala(z) * 0.8, 14.5 + rng.uniform(-0.5, 0.8), z) @ vr.Rz(-s * rng.uniform(25, 60) * D) @ vr.Rx(rng.uniform(-25, 15) * D)
        cristal(out, M, rng.uniform(0.22, 0.36), rng.uniform(1.4, 3.0), 'hielo_claro')
    # costras de escarcha
    for k in range(12):
        a = rng.uniform(-50, 40) * D
        z = rng.uniform(-4.4, 4.4)
        s = rng.choice((1, -1))
        Me = Mc @ vr.T(s * ancho_boreala(z) * 0.92 * math.cos(a), 2.4 * math.sin(a), z) @ vr.Rz(-s * 70 * D)
        caja(out, Me, -0.55, -0.1, -0.55, 1.1, 0.3, 1.1, 'escarcha')
    # la lampara de carambanos de debajo
    for k in range(36):
        a = rng.uniform(0, TAU)
        rr = math.sqrt(rng.uniform(0.02, 1.0))
        x, z = math.cos(a) * rr * 3.3, math.sin(a) * rr * 4.8
        y = 14.0 - 2.5 * math.sqrt(max(0.05, 1 - (x / 4.0) ** 2 - (z / 5.8) ** 2)) + 0.3
        largo = rng.uniform(1.5, 5.5) * (1.0 - rr * 0.55)
        cristal(out, vr.T(x, y, z) @ vr.Rx(180 * D) @ vr.Rz(rng.uniform(-8, 8) * D), rng.uniform(0.14, 0.3), largo, 'hielo_claro')
    # la vela: los cristales del espinazo, de donde sube la aurora plegada como una cortina
    base = []
    n = 17
    for k in range(n):
        z = -5.4 + k * 0.68
        x = 0.95 * math.sin(k * 1.9)
        base.append(np.array((x, lomo_boreala(z) - 0.3, z)))
        Mk = vr.T(*base[-1]) @ vr.Ry(rng.uniform(0, 90) * D) @ vr.Rx(rng.uniform(-16, 16) * D)
        cristal(out, Mk, 0.26, 0.9 + 1.4 * math.sin(math.pi * (k + 0.5) / n), 'hielo_claro')
    alturas = [(1.5 + 11.5 * math.sin(math.pi * (k + 0.5) / n) ** 0.45) * (0.86 + 0.14 * math.sin(k * 2.3)) for k in range(n)]
    cortina(out, base, alturas, (0, 1, -0.16), 'aurora', u_por_bloque=0.45)
    cortina(out, [np.array((-p[0] * 1.8 - 0.3, p[1] - 0.2, p[2] - 0.5)) for p in base], [a * 0.78 for a in alturas], (0, 1, -0.4), 'aurora',
            u_por_bloque=0.38)
    cortina(out, [np.array((p[0] * 2.4 + 0.3, p[1] - 0.3, p[2] + 0.2)) for p in base], [a * 0.55 for a in alturas], (0.08, 1, 0.06), 'aurora',
            u_por_bloque=0.6)
    # las seis patas de zancuda: coxa, femur que sube a la rodilla, tibia que baja al suelo
    patas = []
    for s in (1, -1):
        for (za, zk, zf, alto_k, abre_k, abre_f) in ((3.4, 7.2, 12.5, 21.0, 7.6, 13.0), (0.0, 1.0, 1.8, 22.0, 8.8, 15.2),
                                                     (-3.4, -6.6, -12.0, 20.5, 7.6, 13.6)):
            pa = np.array((s * 3.3, 14.3, za))
            pc = pa + np.array((s * 1.6, 1.5, (zk - za) * 0.12))
            pk = np.array((s * abre_k, alto_k, zk))
            pf = np.array((s * abre_f, 0.6, zf))
            segmento(out, pa, pc, 0.78, 'hueso_frio')
            bola(out, vr.T(*pc), 0.72, 'hueso_frio', capas=4)
            segmento(out, pc, pk, 0.62, 'hueso_frio', 0.48, piezas=3)
            segmento(out, pk, pf, 0.5, 'hueso_frio', 0.24, piezas=5)
            for t_ in (0.3, 0.62):                                   # la armadura de hielo del femur
                p = pc + (pk - pc) * t_
                cristal(out, em.marco(p, pk - pc) @ vr.Rx(-60 * D), 0.24, 1.3 - t_ * 0.5, 'hielo_claro')
            Mr = vr.T(*pk)                                           # la rodilla, con su racimo
            bola(out, Mr, 0.75, 'hielo', capas=5)
            for j in range(5):
                cristal(out, Mr @ vr.Ry(j * 72 * D + 0.4) @ vr.Rx(-32 * D), 0.2, rng.uniform(1.0, 2.0), 'hielo_claro')
            for t_ in (0.22, 0.45, 0.68):                            # anillos de escarcha por la tibia
                p = pk + (pf - pk) * t_
                redondo_z(out, em.marco(p, pf - pk), 0.5 - t_ * 0.25, -0.14, 0.14, 'escarcha')
            segmento(out, pf, pf + np.array((s * 0.4, -0.6, (zf - zk) * 0.03)), 0.24, 'hielo_claro', 0.06)   # el pie de cuchilla
            for dz in (-0.6, 0.6):
                segmento(out, pf + np.array((0, 0.4, 0)), pf + np.array((s * 0.7, -0.55, dz)), 0.12, 'hielo_claro', 0.04)
            patas.append((pk, pf))
    # el cuello de garza: sube en ese, con una crin de escarcha detras
    cuello = [np.array((0, 15.0, 4.8)), np.array((0, 17.0, 7.0)), np.array((0, 19.4, 8.0)), np.array((0, 21.4, 8.2)), np.array((0, 22.8, 9.6))]
    radios = (1.35, 1.1, 0.95, 0.86, 0.8)
    for k in range(len(cuello) - 1):
        segmento(out, cuello[k], cuello[k + 1], radios[k], 'hielo', radios[k + 1], piezas=2)
        Mv = em.marco(cuello[k + 1], cuello[k + 1] - cuello[k])
        redondo_z(out, Mv, radios[k + 1] * 1.14, -0.16, 0.16, 'escarcha')
        for j in range(3):
            p = cuello[k] + (cuello[k + 1] - cuello[k]) * (j + 0.5) / 3
            Mf = em.marco(p, cuello[k + 1] - cuello[k]) @ vr.T(0, radios[k] * 0.8, 0) @ vr.Rx(-(25 + j * 8) * D)
            panel(out, Mf, 0.9, 1.4 + 0.3 * j, 'escarcha', g=0.04)
    # la cabeza: craneo de garza, pico que acaba en lanza de hielo, barbas de carambano,
    # tres ojos por lado y el abanico de escarcha
    Mh = em.marco(np.array((0, 22.9, 10.6)), (0, -0.22, 1.0))
    ovoide(out, Mh @ vr.T(0, 0.15, 0.1), 1.3, 1.15, 1.75, 'hueso_frio', capas=7, lados=16)
    for s in (1, -1):                                               # las cejas, de escarcha
        caja(out, Mh @ vr.T(s * 0.55, 0.95, 0.5) @ vr.Ry(s * 14 * D) @ vr.Rz(-s * 18 * D), -0.45, -0.15, -0.9, 0.9, 0.32, 1.9, 'escarcha')
    pico = [(0.0, 0.05, 1.2, 0.8), (0.0, -0.05, 3.2, 0.58), (0.0, -0.15, 5.2, 0.42), (0.0, -0.25, 7.0, 0.28)]
    for (x0, y0, z0, r0), (x1, y1, z1, r1) in zip(pico, pico[1:]):
        segmento(out, punto(Mh, (x0, y0, z0)), punto(Mh, (x1, y1, z1)), r0, 'hueso_frio', r1, piezas=4)
    segmento(out, punto(Mh, (0, -0.25, 6.8)), punto(Mh, (0, -0.32, 9.0)), 0.3, 'hielo_claro', 0.16)       # la lanza
    segmento(out, punto(Mh, (0, -0.32, 9.0)), punto(Mh, (0, -0.4, 11.0)), 0.16, 'hielo_claro', 0.03)
    Mj = Mh @ vr.T(0, -0.55, 0.6) @ vr.Rx(boca * D)                  # la mandibula, abierta
    segmento(out, punto(Mj, (0, 0, 0)), punto(Mj, (0, -0.1, 3.0)), 0.55, 'hueso_frio', 0.4, piezas=2)
    segmento(out, punto(Mj, (0, -0.1, 3.0)), punto(Mj, (0, -0.15, 5.6)), 0.4, 'hueso_frio', 0.08, piezas=2)
    segmento(out, punto(Mh, (0, -0.55, 0.9)), punto(Mh, (0, -0.6, 4.6)), 0.3, 'aurora_luz', 0.12)      # la garganta que brilla
    for s in (1, -1):
        for k in range(3):
            caja(out, Mh @ vr.T(s * 1.22, 0.42 - k * 0.3, 0.65 + k * 0.28) @ vr.Ry(s * 10 * D), -0.06, -0.1, -0.17, 0.12, 0.2, 0.34, 'ojo_aurora')
        for k in range(12):                                         # las barbas de carambano
            z = 1.6 + k * 0.42
            rr = 0.62 - z * 0.05
            largo = rng.uniform(0.5, 1.5) * (1.1 - k / 16)
            cristal(out, Mh @ vr.T(s * rr * 0.75, -0.1 - rr * 0.45, z) @ vr.Rx(180 * D) @ vr.Rz(s * rng.uniform(-10, 4) * D), 0.07, largo, 'hielo_claro')
    for k in range(13):
        a = -78 + k * 13
        largo = 3.0 + 2.2 * math.cos(math.radians(a))
        Mf = Mh @ vr.T(0, 0.75, -1.0) @ vr.Rz(math.radians(a)) @ vr.Rx(-42 * D)
        caja(out, Mf, -0.08, 0, -0.04, 0.16, largo, 0.08, 'hielo_claro')
        panel(out, Mf @ vr.T(0, largo * 0.22, 0.05), 0.5, largo * 0.76, 'escarcha', g=0.03)
    return out, {'patas': patas}


# ======================================================================
#  B · NOCTURNA, la Bestia sin Cielo (noche / vacio)
# ======================================================================
def lomo_nocturna(z):
    return float(np.interp(z, (-7.6, -5.6, -3.0, -0.6, 1.8, 3.4, 4.8), (9.8, 11.6, 13.4, 14.9, 16.0, 15.6, 14.0)))


def nocturna(abre=36.0, semilla=4):
    rng = random.Random(semilla)
    out = []
    # el cuerpo encorvado: alto en la cruz y bajando hasta la grupa
    ovoide(out, vr.T(0, 10.8, -0.8) @ vr.Rx(-18 * D), 4.8, 4.0, 6.2, 'noche', capas=12, lados=16)
    ovoide(out, vr.T(0, 13.2, 1.8) @ vr.Rx(-25 * D), 4.4, 2.8, 3.4, 'noche', capas=8, lados=16)       # la cruz
    ovoide(out, vr.T(0, 8.6, -5.6) @ vr.Rx(10 * D), 3.5, 2.9, 2.7, 'noche', capas=7, lados=16)        # la grupa
    # por el espinazo, las fases de la luna: de la llena en la cruz a la mas fina en la grupa
    for (z, R, c) in ((2.6, 2.0, 0.75), (0.9, 2.3, 0.55), (-0.9, 2.3, 0.42), (-2.6, 2.1, 0.32), (-4.2, 1.8, 0.23),
                      (-5.6, 1.45, 0.16), (-6.8, 1.1, 0.1)):
        y = lomo_nocturna(z) - 0.3
        if c >= 1:
            Mm = vr.T(0, y + R * 0.85, z) @ vr.Ry(90 * D)
        else:
            Mm = vr.T(0, y + R * 0.3, z) @ vr.Ry(90 * D) @ vr.Rz(62 * D)
        media_luna(out, Mm, R, 0.34, 'plata', c=c)
    # la estrella negra del pecho, con su anillo de luz, y las costillas que la agarran como dedos
    pecho = np.array((0, 8.4, 5.6))
    bola(out, vr.T(*pecho), 2.0, 'vacio', capas=8)
    Ma = vr.T(*pecho) @ vr.Rx(74 * D) @ vr.Rz(14 * D)
    for k in range(44):
        a = k * TAU / 44
        caja(out, Ma @ vr.Rz(a) @ vr.T(0, 2.75, 0), -0.22, -0.08, -0.05, 0.44, 0.16 + 0.1 * (k % 2), 0.1, 'anillo')
    for k in range(30):
        a = k * TAU / 30 + 0.1
        caja(out, Ma @ vr.Rz(a) @ vr.T(0, 3.5, 0), -0.2, -0.04, -0.03, 0.4, 0.08, 0.06, 'anillo')
    for k in range(14):
        a = k * TAU / 14 + 0.2
        r_ = rng.uniform(3.9, 4.8)
        p = punto(Ma, (math.cos(a) * r_, math.sin(a) * r_, rng.uniform(-0.4, 0.4)))
        redondo_y_(out, vr.T(*p), -0.09, 0.09, 0.09, 'anillo')
    panel(out, vr.T(*(pecho + np.array((0, -4.6, -0.3)))), 9.4, 9.2, 'nebulosa', g=0.01)
    for k, z in enumerate((3.4, 4.5, 5.6, 6.7)):
        for s in (1, -1):
            pts = [np.array((s * 1.5, 11.8 - k * 0.15, z - 0.8)), np.array((s * 3.3, 10.6, z - 0.2)), np.array((s * 3.6, 8.2, z + 0.3)),
                   np.array((s * 2.9, 6.0, z + 0.8)), np.array((s * 1.3, 5.2, z + 1.0))]
            for j, (p, q) in enumerate(zip(pts, pts[1:])):
                segmento(out, p, q, 0.26 - j * 0.04, 'plata', 0.22 - j * 0.04)
    # los brazos largos, sobre los nudillos, y las alas plegadas encima como un manto
    for s in (1, -1):
        hom = np.array((s * 4.5, 13.6, 2.6))
        cod = np.array((s * 7.4, 8.8, 4.8))
        mun = np.array((s * 7.0, 2.7, 7.6))
        segmento(out, hom, cod, 1.45, 'noche', 1.1, piezas=2)
        segmento(out, cod, mun, 1.1, 'noche', 0.9, piezas=2)
        bola(out, vr.T(*hom), 1.6, 'noche', capas=5)
        bola(out, vr.T(*cod), 1.15, 'noche', capas=4)
        for t_ in (0.62, 0.78):
            p = cod + (mun - cod) * t_
            redondo_z(out, em.marco(p, mun - cod), 1.05, -0.15, 0.15, 'plata')            # brazaletes de plata
        ovoide(out, vr.T(*mun) @ vr.Rx(20 * D), 1.0, 0.75, 1.15, 'noche', capas=5)
        for dx in (-0.65, 0.0, 0.65):
            p1 = mun + np.array((s * 0.3 + dx, -0.8, 1.2))
            p2 = p1 + np.array((dx * 0.3, -1.1, 0.4))
            p3 = p2 + np.array((dx * 0.2, -0.4, 1.0))
            segmento(out, mun + np.array((dx, -0.3, 0.6)), p1, 0.4, 'noche')
            segmento(out, p1, p2, 0.34, 'noche')
            segmento(out, p2, p3, 0.26, 'plata', 0.05)
        # el ala plegada: tres dedos de plata que suben desde la muneca y la membrana entre ellos
        raiz = mun + np.array((s * 0.5, 1.0, -0.4))
        puntas = [np.array((s * 6.4, 19.8, 1.8)), np.array((s * 8.2, 16.8, -2.9)), np.array((s * 7.8, 12.8, -7.0))]
        cadera = np.array((s * 4.6, 9.0, -7.4))
        medios = []
        for tp in puntas:
            md = raiz + (tp - raiz) * 0.42 + np.array((s * 1.1, 0, 0))
            segmento(out, raiz, md, 0.38, 'plata', 0.3)
            segmento(out, md, tp, 0.3, 'plata', 0.1)
            bola(out, vr.T(*md), 0.42, 'plata', capas=3)
            fin = tp + (tp - md) / np.linalg.norm(tp - md) * 1.1 + np.array((0, -0.6, 0))
            segmento(out, tp, fin, 0.12, 'plata', 0.02)                                 # la una del dedo
            medios.append(md)
        medios.append(raiz + (cadera - raiz) * 0.42 + np.array((s * 0.6, 0, 0)))
        bordes = puntas + [cadera]
        for j in range(len(bordes) - 1):
            a, b = bordes[j], bordes[j + 1]
            ma, mb = medios[j], medios[j + 1]
            cuadro(out, [raiz, ma, mb, raiz], [(0.5, 1), (0, 0.58), (1, 0.58), (0.5, 1)], 'membrana_noche')
            cuadro(out, [ma, a, b, mb], [(0, 0.58), (0, 0), (1, 0), (1, 0.58)], 'membrana_noche')
    # las patas de atras, cortas y dobladas
    for s in (1, -1):
        cad = np.array((s * 3.1, 8.2, -5.8))
        rod = np.array((s * 3.7, 4.6, -3.5))
        cor = np.array((s * 4.0, 2.4, -7.2))
        pie = np.array((s * 4.0, 0.4, -6.0))
        segmento(out, cad, rod, 1.3, 'noche', 1.05)
        segmento(out, rod, cor, 0.95, 'noche', 0.72)
        segmento(out, cor, pie, 0.68, 'noche', 0.56)
        for dx in (-0.45, 0.0, 0.45):
            segmento(out, pie, pie + np.array((dx, -0.3, 1.3)), 0.22, 'plata', 0.04)
    # el cuello, corto y gordo, y la cabeza baja, adelantada
    segmento(out, np.array((0, 12.8, 5.0)), np.array((0, 12.0, 8.0)), 1.7, 'noche', 1.35, piezas=2)
    Mh = em.marco(np.array((0, 11.8, 9.8)), (0, -0.12, 1.0))
    R = 2.3
    ovoide(out, Mh @ vr.T(0, 0.1, -1.4), R * 0.86, R * 0.82, 1.7, 'noche', capas=6, lados=16)
    # la cara es la luna llena: se parte en dos por la mitad y cada mitad se abre como una puerta
    for s in (1, -1):
        Mq = Mh @ vr.T(s * R, 0, 0) @ vr.Ry(s * abre * D) @ vr.T(-s * R, 0, 0)
        for (rr, z0, g) in ((R, 0.0, 0.45), (R * 0.8, 0.45, 0.28), (R * 0.52, 0.73, 0.18)):
            angs = [(-90 + 180 * k / 9) if s > 0 else (90 + 180 * k / 9) for k in range(10)]
            cont = [(rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a))) for a in angs]
            uv = [(0.5 + x / (2 * R), 0.5 - y / (2 * R)) for x, y in cont]
            losa(out, Mq @ vr.T(0, 0, z0), cont, g, 'luna', uv, 'plata')
        for k in range(11):
            y = (-0.85 + k * 0.17) * R
            largo = 0.42 if k % 2 else 0.26
            caja(out, Mq @ vr.T(0, y, 0.25), -largo if s > 0 else 0.0, -0.06, -0.06, largo, 0.12, 0.14, 'diente_sol')
    # detras de la cara, el vacio: negro, con su nebulosa y alguna estrella suelta
    caja(out, Mh, -R * 0.72, -R * 0.78, -1.3, R * 1.44, R * 1.56, 1.3, 'vacio')
    panel(out, Mh @ vr.T(0, -R * 0.85, 0.03), R * 1.7, R * 1.7, 'nebulosa', g=0.01)
    for k in range(9):
        redondo_y_(out, Mh @ vr.T(rng.uniform(-0.4, 0.4) * R, rng.uniform(-0.6, 0.6) * R, 0.08), -0.07, 0.07, 0.07, 'anillo')
    # el halo: las fases de la luna alrededor de la cara, con los cuernos hacia fuera
    for k, c in enumerate((0.7, 0.52, 0.38, 0.27, 0.18, 0.12, 0.18, 0.27, 0.38, 0.52)):
        a = 90 + k * 36
        Mm = Mh @ vr.T(math.cos(math.radians(a)) * (R + 1.0), math.sin(math.radians(a)) * (R + 1.0), -0.4) @ vr.Rz(math.radians(a))
        media_luna(out, Mm, 0.9, 0.22, 'plata', c=c)
    return out, {'pecho': pecho}


# ======================================================================
#  C · DUNEARA, la que Nada en la Arena (arena / sol)
# ======================================================================
def duneara(abre=30.0, semilla=5):
    rng = random.Random(semilla)
    out = []
    Mc = vr.T(0, 1.4, 0)
    # el caparazon de lapislazuli: una cupula ancha y plana, medio enterrada, hecha de duelas
    # que dejan ver el oro entre una y otra (los surcos de los elitros)
    ovoide(out, Mc, 6.75, 2.9, 8.1, 'oro', capas=12, lados=16)
    RX, RY, RZ = 7.0, 3.1, 8.4

    def alto(z):
        return RY * math.sqrt(max(0.05, 1 - (z / RZ) ** 2))

    def sobre(th, z):
        f = math.sqrt(max(0.0, 1 - (z / RZ) ** 2))
        return np.array((RX * f * math.sin(th), 1.4 + RY * f * math.cos(th), z))

    for s in (1, -1):
        for i in range(7):
            th0, th1 = s * math.radians(2 + 12.5 * i), s * math.radians(2 + 12.5 * (i + 1))
            thm = (th0 + th1) / 2
            zs = [-RZ * 0.97 + k * (1.94 * RZ / 16) for k in range(17)]
            for k in range(16):
                z0, z1 = zs[k], zs[k + 1]
                p0, p1 = sobre(thm, z0), sobre(thm, z1)
                pm = (p0 + p1) / 2
                nrm = np.array((pm[0] / RX ** 2, (pm[1] - 1.4) / RY ** 2, pm[2] / RZ ** 2))
                w = float(np.linalg.norm(sobre(th1, (z0 + z1) / 2) - sobre(th0, (z0 + z1) / 2))) * 0.86
                L = float(np.linalg.norm(p1 - p0))
                caja(out, em.marco(p0, p1 - p0, up=nrm), -w / 2, -0.5, -0.04, w, 0.5, L + 0.08, 'lapis')

    for k in range(16):
        z = -7.4 + k * 0.98
        caja(out, vr.T(0, 1.4 + alto(z) - 0.12, z) @ vr.Rx(-math.atan2(z, 8.4) * 0.5), -0.28, 0, -0.52, 0.56, 0.32, 1.04, 'oro')
    for s in (1, -1):                                                 # las costuras de oro de cada elitro
        for k in range(12):
            z = -6.6 + k * 1.15
            x = s * 3.4 * math.sqrt(max(0.05, 1 - (z / 8.4) ** 2))
            y = 1.4 + alto(z) * math.sqrt(max(0.05, 1 - (x / 7.0) ** 2)) - 0.05
            caja(out, vr.T(x, y, z) @ vr.Rz(-s * 28 * D), -0.18, 0, -0.45, 0.36, 0.22, 0.9, 'oro')
    # la arena que le resbala por el lomo, solo detras
    for (x, z) in ((-2.2, -5.8), (2.8, -4.6)):
        ovoide(out, vr.T(x, 1.4 + alto(z) * 0.86, z) @ vr.Ry(rng.uniform(60, 120) * D), 0.8, 0.36, 1.6, 'duna', capas=5, lados=16)
    # el canto de oro del caparazon, a ras de arena
    for k in range(32):
        a = k * TAU / 32
        redondo_y_(out, vr.T(math.cos(a) * 6.85, 1.2, math.sin(a) * 8.2), -0.2, 0.4, 0.34, 'oro')
    # las aletas de raya: tres tramos por lado que ondulan, con radios de oro y ocelos
    for s in (1, -1):
        Mx = ejes(np.array((s * 6.2, 1.9, 1.0)), (0, 0, s), (s * math.cos(24 * D), math.sin(24 * D), 0))
        for j, (largo, ancho, ola) in enumerate(((4.4, 12.0, 18), (4.0, 10.0, -26), (3.6, 7.5, 18))):
            panel(out, Mx, ancho, largo, 'aleta_punta' if j == 2 else 'aleta', g=0.08)
            for xr in (-0.44, 0.0, 0.44):
                segmento(out, punto(Mx, (xr * ancho, 0, 0)), punto(Mx, (xr * ancho * 0.92, largo, 0)), 0.13, 'oro', 0.09)
            Mx = Mx @ vr.T(-s * ancho * 0.08, largo, 0) @ vr.Rx(ola * D)
    # la cola de escorpion: cuentas de lapis con anillos de oro, arqueada sobre el lomo
    cola = [np.array((0, 3.0, -7.4)), np.array((0, 5.6, -10.4)), np.array((0, 9.4, -11.2)), np.array((0, 12.4, -9.4)),
            np.array((0, 14.0, -6.2)), np.array((0, 13.6, -3.0))]
    radios = (1.9, 1.6, 1.38, 1.18, 1.0, 0.85)
    for k in range(len(cola) - 1):
        p, q = cola[k], cola[k + 1]
        L = float(np.linalg.norm(q - p))
        M = em.marco((p + q) / 2, q - p)
        r = (radios[k] + radios[k + 1]) / 2
        ovoide(out, M, r, r * 0.9, L * 0.62, 'lapis', capas=6, lados=16)
        redondo_z(out, em.marco(q, q - p), radios[k + 1] * 1.1, -0.18, 0.18, 'oro')
        redondo_z(out, em.marco(q, q - p) @ vr.Rz(22.5 * D), radios[k + 1] * 1.1, -0.18, 0.18, 'oro')
        for s in (1, -1):
            cristal(out, M @ vr.T(s * r * 0.55, r * 0.75, 0) @ vr.Rz(-s * 35 * D) @ vr.Rx(-30 * D), 0.16, 1.0, 'oro')
    sol = cola[-1] + np.array((0, -0.8, 1.7))
    bola(out, vr.T(*sol), 1.8, 'ambar', capas=8)
    Ms = vr.T(*sol) @ vr.Rx(75 * D)
    for k in range(14):
        cristal(out, Ms @ vr.Rz(k * TAU / 14) @ vr.T(0, 1.65, 0), 0.16, 1.0 if k % 2 else 1.8, 'oro')
    segmento(out, sol + np.array((0, -1.2, 0.9)), sol + np.array((0, -3.4, 2.2)), 0.34, 'diente_sol', 0.04)     # el aguijon
    # la cabeza: el escudo de escarabajo es un sol que sale, con sus rayos de oro
    Mh = em.marco(np.array((0, 2.6, 8.6)), (0, 0.1, 1.0))
    ovoide(out, Mh @ vr.T(0, 0.1, -2.5), 2.7, 1.7, 1.6, 'lapis', capas=6, lados=16)
    Mcl = Mh @ vr.T(0, 0.9, -0.2) @ vr.Rx(-15 * D)
    cont = [(3.3 * math.cos(math.radians(a)), 3.3 * math.sin(math.radians(a))) for a in range(0, 181, 15)]
    losa(out, Mcl, cont, 0.42, 'lapis', None, 'oro')
    losa(out, Mcl @ vr.T(0, 0, 0.42), [(x * 0.62, y * 0.62) for x, y in cont], 0.14, 'oro')
    for k in range(9):
        a = 10 + k * 20
        Mr = Mcl @ vr.T(math.cos(math.radians(a)) * 3.15, math.sin(math.radians(a)) * 3.15, 0.21) @ vr.Rz(math.radians(a - 90))
        cristal(out, Mr, 0.2, 1.1 if k % 2 else 2.0, 'oro')
    for s in (1, -1):                                               # los ojos compuestos, de ambar
        ovoide(out, Mh @ vr.T(s * 2.4, 0.25, 0.2) @ vr.Ry(s * 30 * D), 0.55, 0.66, 0.68, 'ojo_compuesto', capas=5, lados=16)
        ant = [punto(Mh, (s * 1.3, 1.2, 0.2)), punto(Mh, (s * 2.4, 3.4, 0.6)), punto(Mh, (s * 3.8, 4.6, -1.0))]
        for p, q in zip(ant, ant[1:]):
            segmento(out, p, q, 0.1, 'oro')
        for j in range(3):                                           # la maza de laminas de la antena
            caja(out, vr.T(*ant[-1]) @ vr.Ry(s * 40 * D) @ vr.Rz(-s * (20 + j * 30) * D), -0.05, 0, -0.35, 0.1, 1.0, 0.7, 'oro')
    # el pozo de la boca, bajo el escudo: un embudo de arena que gira hacia el ambar
    Mb = Mh @ vr.T(0, -0.55, 1.2) @ vr.Rx(-8 * D)
    anillos = ((2.3, 0.0), (1.85, -0.5), (1.35, -0.95), (0.85, -1.35), (0.45, -1.65))
    n = 16
    for j in range(len(anillos) - 1):
        (r0, z0), (r1, z1) = anillos[j], anillos[j + 1]
        for k in range(n):
            a0, a1 = k * TAU / n + j * 0.2, (k + 1) * TAU / n + j * 0.2
            b0, b1 = a0 + 0.25, a1 + 0.25
            cuadro(out, [punto(Mb, (math.cos(a0) * r0, math.sin(a0) * r0, z0)), punto(Mb, (math.cos(a1) * r0, math.sin(a1) * r0, z0)),
                         punto(Mb, (math.cos(b1) * r1, math.sin(b1) * r1, z1)), punto(Mb, (math.cos(b0) * r1, math.sin(b0) * r1, z1))],
                   [(0, 0), (1, 0), (1, 1), (0, 1)], 'remolino')
        m = int(n * r0 / 2.3) + 4
        for k in range(m):
            a = k * TAU / m + j * 0.3
            Md = Mb @ vr.T(math.cos(a) * r0 * 0.95, math.sin(a) * r0 * 0.95, z0 - 0.05) @ vr.Rz(a + TAU / 4) @ vr.Rx(-55 * D)
            cristal(out, Md, 0.08, 0.6 - j * 0.1, 'diente_sol')
    redondo_z(out, Mb, 0.62, -1.72, -1.58, 'ambar', n=3)
    for k in range(20):
        a = k * TAU / 20
        caja(out, Mb @ vr.T(math.cos(a) * 2.5, math.sin(a) * 2.5, 0.05) @ vr.Rz(a), -0.3, -0.2, -0.25, 0.6, 0.4, 0.45, 'oro')
    # las mandibulas de hoz, abiertas a los lados del pozo
    for s in (1, -1):
        Mm = Mh @ vr.T(s * 2.3, -0.9, 1.4) @ vr.Ry(s * (abre - 8) * D)
        pts = [punto(Mm, (0, 0, 0)), punto(Mm, (s * 0.5, 0, 2.4)), punto(Mm, (-s * 0.3, 0, 4.4)), punto(Mm, (-s * 1.7, 0, 5.5))]
        for j, (p, q) in enumerate(zip(pts, pts[1:])):
            segmento(out, p, q, 0.46 - j * 0.13, 'oro' if j < 2 else 'diente_sol', 0.33 - j * 0.11)
    # las patas cortas de cavar, delante, medio enterradas
    for s in (1, -1):
        for z in (5.4, 3.2):
            p0 = np.array((s * 5.4, 1.2, z))
            p1 = p0 + np.array((s * 2.2, 0.3, 0.6))
            p2 = p1 + np.array((s * 0.9, -1.5, 0.8))
            segmento(out, p0, p1, 0.5, 'lapis', 0.42)
            bola(out, vr.T(*p1), 0.48, 'oro', capas=3)
            segmento(out, p1, p2, 0.4, 'oro', 0.12)
    # el reborde de arena que se le amontona contra los costados
    for k in range(26):
        a = k * TAU / 26
        x, z = math.cos(a) * 7.3, math.sin(a) * 8.7
        ovoide(out, vr.T(x, -0.15, z) @ vr.Ry(-a), 1.1, 0.5, 1.6, 'duna', capas=5, lados=16)
    return out, {'sol': sol}


# ----------------------------------------------------------------------
#  Dibujo: lo opaco primero y la luz (aurora, nebulosa) despues, sumando
# ----------------------------------------------------------------------
def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.5, brillo_luz=1.2):
    qm.dibujar(lz, cam, [q for q in qs if q[2] not in ADITIVOS], luces, ambiente, niebla, brillo)
    for P, UV, mat in qs:
        if mat not in ADITIVOS:
            continue
        tex = qm.MAT[mat]
        k = 1.0 if niebla is None else 1.0 - float(niebla(np.array(np.mean([cam.proyectar(p)[2] for p in P]))))
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, np.ones(3), aditivo=True, brillo=brillo_luz * k,
                         envolver=True)

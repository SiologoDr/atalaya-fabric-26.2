"""
Bocetos 3D de tres quimeras para el quinto jefe (ficha de diseno, 12-10-2026).

Juan: «se mas creativo, no te bases en criaturas que existan en la realidad:
crea tus monstruos; Ofidia esta compuesta de varias criaturas y les da algo
nuevo». Ofidia es sierpe marina + pez abisal (los senuelos y la fauce) +
capucha de espectro + aleta de manta + tambores de piedra con cinturones. Estas
tres se inventan igual, cada una con su cosa que no tiene nadie:

  A  Quelvora, la Devoradora de Atalayas
     gusano excavador + craneo de mandibulas en tres + las atalayas que se trago,
     fundidas a su lomo con su caparazon + el ultimo faro como unico ojo
  B  Ixtara, la Hilandera
     sierpe de carretes + brazos de aguja + mascara de porcelana que se parte
     en dos + un telar de luz tendido entre las manos + velo de hilos
  C  Espinara, la Zarza que Florece
     zarza trenzada + una flor carnivora por cabeza con un craneo dentro que
     mira + estambres que muerden + farolillos de semilla + raices

Se construyen en bloques de mundo sobre una curva (la de eclipse_modelo). Los
materiales son losetas de 32 px por bloque dibujadas aqui: placas de quitina con
anillos de crecimiento, hueso poroso, sillares irregulares comidos por el
caparazon, laca con su tela de arana de oro, porcelana cuarteada, hilo devanado,
corteza nudosa, petalos de terciopelo... nada de vanilla ni juntas en
cuadricula. Sirven para decidir forma, tamano y color: no son la textura final.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em

TAU = math.tau
D = vr.D2R


def _r(*hs):
    return [nm._hex(h) for h in hs]


def _mezcla(a, b, t):
    t = min(1.0, max(0.0, t))
    return tuple(int(int(a[i]) + (int(b[i]) - int(a[i])) * t) for i in range(3))


# ----------------------------------------------------------------------
#  Rampas (DISENO.md: cinco tonos, el borde tenido, el nucleo sin blanco puro)
# ----------------------------------------------------------------------
QUITINA = _r('0b0907', '17120e', '241c16', '362a20', '4e3e30')
QUITINA_O = _r('060504', '0e0b09', '17120e', '221a14', '30261c')
VIENTRE_Q = _r('2a241c', '42382c', '5c4e3e', '786652', '96826a')
HUESO = _r('4e463a', '7c7262', 'a89c84', 'cbbfa2', 'e8dec4')
DIENTE = _r('8a8070', 'b4aa94', 'd4cab0', 'e8e0c8', 'fbf6e6')
PIEDRA = _r('24201c', '38322c', '4e4740', '665e55', '82786c')
PIZARRA = _r('0e1016', '181b24', '232836', '30374a', '434c64')
BRONCE = _r('2a1c10', '4a3218', '6e4c24', '92683a', 'b88c56')
VERDIN = _r('1e3a34', '2c5a4e', '3f7a68')
AZUL_E = _r('0a0e22', '121a3a', '1c2852', '28386c', '3a4c88')
ORO = _r('4a3008', '7a5212', 'aa7c20', 'd8a838', 'f6d27a')
LACA = _r('050406', '0b090d', '131016', '1e1a23', '2e2936')
PORCELANA = _r('7e8090', 'a8aab6', 'cdd0d8', 'e6e8ee', 'f8f9fc')
CARMIN = _r('300408', '560810', '86101c', 'b82230', 'e45a5e')
TALLO = _r('050806', '0b120c', '132014', '1d301e', '2b442a')
ESPINA = _r('040304', '0c080a', '180f12', '2a1a1e', '42282c')
PETALO = _r('0c0820', '1a1440', '2a2466', '45429a', '8a8cd8')
HOJA = _r('050a06', '0c160c', '142414', '1e361c', '2c4c28')
VAINA = _r('3a4a2a', '5a6e3e', '7e9456', '9fb672', 'c4d896')


def _vacia(w=32, h=32):
    return np.zeros((h, w, 4), np.uint8)


def _celdas(semilla, n, w=32, h=32, estira=(1.0, 1.0)):
    """Voronoi sobre un toro (para que la loseta case): distancia al centro mas
    cercano y al segundo, cual es, y el vector del centro al pixel."""
    r = random.Random(semilla)
    pts = [(r.uniform(0, w), r.uniform(0, h)) for _ in range(n)]
    ys, xs = np.mgrid[0:h, 0:w].astype(float) + 0.5
    d1 = np.full((h, w), 1e9)
    d2 = np.full((h, w), 1e9)
    idx = np.zeros((h, w), int)
    sx = np.zeros((h, w))
    sy = np.zeros((h, w))
    for k, (px, py) in enumerate(pts):
        dx = xs - px
        dx = dx - w * np.round(dx / w)
        dy = ys - py
        dy = dy - h * np.round(dy / h)
        d = np.sqrt((dx * estira[0]) ** 2 + (dy * estira[1]) ** 2)
        menor = d < d1
        d2 = np.where(menor, d1, np.minimum(d2, d))
        sx = np.where(menor, dx, sx)
        sy = np.where(menor, dy, sy)
        idx = np.where(menor, k, idx)
        d1 = np.where(menor, d, d1)
    return d1, d2, idx, sx, sy


def _linea(t, x0, y0, x1, y1, color):
    """Una linea de un pixel (da la vuelta a la loseta)."""
    h, w = t.shape[:2]
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 1.5) + 1
    for k in range(n + 1):
        u = k / n
        t[int(round(y0 + (y1 - y0) * u)) % h, int(round(x0 + (x1 - x0) * u)) % w] = (*color, 255)


def _trazo(t, r, x, y, pasos, color, angulo=None, giro=0.5, alfa=255):
    """Una grieta o una vena: un camino que tuerce poco a poco (y da la vuelta a la loseta)."""
    h, w = t.shape[:2]
    a = r.uniform(0, TAU) if angulo is None else angulo
    for _ in range(pasos):
        t[int(y) % h, int(x) % w] = (*color, alfa)
        a += r.uniform(-giro, giro)
        x += math.cos(a)
        y += math.sin(a)


# ----------------------------------------------------------------------
#  Materiales de Quelvora
# ----------------------------------------------------------------------
def _quitina(semilla, rampa):
    """Escudos de quitina: placas irregulares abombadas, con el canto a la luz arriba
    a la izquierda, anillos de crecimiento y un brillo aceitoso frio."""
    d1, d2, idx, sx, sy = _celdas(semilla, 7)
    r = random.Random(semilla * 7 + 1)
    base = [r.choice((1, 2, 2, 3)) for _ in range(7)]
    t = _vacia()
    for y in range(32):
        for x in range(32):
            e = d2[y, x] - d1[y, x]
            b = base[idx[y, x]]
            if e < 0.9:
                c = rampa[0]
            elif e < 2.3:
                c = rampa[min(4, b + 1)] if sx[y, x] + sy[y, x] < 0 else rampa[max(0, b - 1)]
            else:
                c = rampa[b]
                if int(d1[y, x] * 1.4) % 3 == 0:
                    c = rampa[max(0, b - 1)]                     # anillos de crecimiento
                if d1[y, x] < 1.5:
                    c = rampa[min(4, b + 1)]
            if r.random() < 0.015:
                c = _mezcla(rampa[4], nm._hex('6a7a9a'), 0.5)    # brillo aceitoso
            t[y, x] = (*c, 255)
    return t


def _vientre_q(semilla):
    d1, d2, idx, sx, sy = _celdas(semilla, 11)
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            e = d2[y, x] - d1[y, x]
            b = 2 if r.random() > 0.15 else 1
            if e < 0.8:
                b = 0
            elif e < 1.8 and sx[y, x] + sy[y, x] < 0:
                b = 3
            t[y, x] = (*VIENTRE_Q[b], 255)
    return t


def _hueso(semilla, rampa=HUESO):
    """Hueso: poroso, con alguna grieta fina y la parte que mira a la luz mas clara."""
    d1, d2, idx, sx, sy = _celdas(semilla, 5)
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            b = 3 if d2[y, x] - d1[y, x] > 2.6 else 2
            if sx[y, x] + sy[y, x] < -3 and b == 3:
                b = 4
            if r.random() < 0.05:
                b = 1                                             # poro
            t[y, x] = (*rampa[b], 255)
    for _ in range(3):
        _trazo(t, r, r.uniform(0, 32), r.uniform(0, 32), r.randint(6, 13), rampa[1])
    return t


def _sillar(semilla):
    """Los muros de las atalayas tragadas: mamposteria de piedras poligonales de
    tamanos distintos (nada de hiladas de ladrillo), gastadas, con hollin, y el
    caparazon de ella trepando por las juntas."""
    d1, d2, idx, sx, sy = _celdas(semilla, 9)
    r = random.Random(semilla)
    tonos = [r.choice((1, 2, 2, 3)) for _ in range(9)]
    t = _vacia()
    for y in range(32):
        for x in range(32):
            e = d2[y, x] - d1[y, x]
            b = tonos[idx[y, x]]
            if e < 1.0:
                c = PIEDRA[0]
            elif e < 2.0:
                c = PIEDRA[min(4, b + 1)] if sx[y, x] + sy[y, x] < 0 else PIEDRA[max(0, b - 1)]
            else:
                c = PIEDRA[b] if r.random() > 0.12 else PIEDRA[max(0, b - 1)]
            t[y, x] = (*c, 255)
    for _ in range(3):
        x0 = r.randrange(32)
        for yy in range(r.randint(8, 20)):
            for k in range(r.randint(1, 3)):
                p = t[yy, (x0 + k) % 32, :3]
                t[yy, (x0 + k) % 32, :3] = _mezcla(p, (14, 11, 9), 0.35)
    for _ in range(3):
        x0 = r.uniform(0, 32)
        _trazo(t, r, x0, 31.0, r.randint(12, 24), QUITINA[1], angulo=-math.pi / 2, giro=0.45)
        _trazo(t, r, x0 + 1, 31.0, r.randint(8, 16), QUITINA[2], angulo=-math.pi / 2, giro=0.45)
    return t


def _bronce(semilla):
    d1, d2, idx, sx, sy = _celdas(semilla, 9)
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            b = r.choice((1, 2, 2, 3))
            if d2[y, x] - d1[y, x] < 0.8:
                b = 0
            c = BRONCE[b]
            if idx[y, x] % 4 == 0 and d1[y, x] > 1.4:
                c = VERDIN[r.choice((0, 1, 1, 2))]               # el cardenillo
            if r.random() < 0.03:
                c = BRONCE[4]
            t[y, x] = (*c, 255)
    return t


def _estandarte(semilla):
    """El estandarte de las atalayas (32 x 64): azul de guardia, cenefa de oro y la
    torre con su faro; el bajo deshilachado."""
    r = random.Random(semilla)
    t = _vacia(32, 64)
    for y in range(64):
        for x in range(32):
            c = AZUL_E[2] if x % 2 else AZUL_E[1]
            if y % 3 == 0:
                c = AZUL_E[1] if x % 2 else AZUL_E[0]
            if r.random() < 0.03:
                c = AZUL_E[3]
            if x < 2 or x > 29 or y < 2:
                c = ORO[3] if (x + y) % 2 else ORO[2]
            t[y, x] = (*c, 255)
    # la torre del escudo
    for y in range(18, 46):
        for x in range(12, 20):
            t[y, x] = (*ORO[3], 255)
    for y in range(14, 18):
        for x in (11, 12, 14, 15, 17, 18, 20):
            if 11 <= x <= 20:
                t[y, x] = (*ORO[3], 255)
    for y in range(44, 47):
        for x in range(10, 22):
            t[y, x] = (*ORO[2], 255)
    for y in range(24, 29):
        for x in (15, 16):
            t[y, x] = (*AZUL_E[0], 255)                           # la ventana
    for (x, y) in ((15, 8), (16, 8), (14, 9), (15, 9), (16, 9), (17, 9), (15, 10), (16, 10), (15, 11), (16, 11)):
        t[y, x] = (*nm._hex('ffe6a0'), 255)                       # el faro, arriba
    # el bajo, deshilachado
    for x in range(32):
        corte = 52 + int(abs((x % 8) - 4) * 2.2 + r.uniform(0, 3))
        for y in range(corte, 64):
            t[y, x] = (0, 0, 0, 0)
    return t


def _pizarra(semilla):
    """Tejas de pizarra solapadas: cada fila tapa la de arriba, el canto de abajo
    redondeado y a la luz, la sombra que echa la teja de encima."""
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        fila, fy = y // 8, y % 8
        off = 4 if fila % 2 else 0
        for x in range(32):
            fx = (x + off) % 8
            if fy <= 1:
                b = 1
            elif fy <= 4:
                b = 2 if r.random() > 0.15 else 3
            elif fy == 5:
                b = 3
            elif fy == 6:
                b = 4 if 1 <= fx <= 6 else 1
            else:
                b = 0
            if fx == 0 and fy < 7:
                b = 0
            if fy >= 6 and fx in (0, 7):
                b = 0
            t[y, x] = (*PIZARRA[b], 255)
    return t


def _emisivo(c1, c2, w=32, h=32, oscuro=None, semilla=0):
    """Un emisivo de centro claro a borde de color; 'oscuro' pinta grietas oscuras (magma)."""
    a, b = nm._hex(c1), nm._hex(c2)
    t = _vacia(w, h)
    for y in range(h):
        for x in range(w):
            d = max(abs(x - (w - 1) / 2) / ((w - 1) / 2), abs(y - (h - 1) / 2) / ((h - 1) / 2))
            t[y, x] = (*_mezcla(a, b, d), 255)
    if oscuro:
        d1, d2, idx, sx, sy = _celdas(semilla, 8, w, h)
        m = (d2 - d1) < 0.9
        t[m, :3] = nm._hex(oscuro)
    return t


def _ventana():
    """Una ventana de las atalayas (16 x 24): el arco, el parteluz y la luz de dentro."""
    t = _vacia(16, 24)
    nuc, borde = nm._hex('fff2c4'), nm._hex('ff8a2a')
    marco = nm._hex('1a140f')
    for y in range(24):
        for x in range(16):
            dx = (x - 7.5) / 7.5
            arco = y < 8 and (dx * dx + ((y - 8) / 8.0) ** 2) > 1.0
            if arco or x in (0, 15) or y == 23:
                c = marco
            elif x in (7, 8) or y == 13:
                c = nm._hex('3a2210')                              # el parteluz
            else:
                c = _mezcla(nuc, borde, min(1.0, abs(dx) * 0.8 + abs(y - 14) / 18))
            t[y, x] = (*c, 255)
    return t


def _vidriera():
    """El cristal de la linterna del faro (16 x 32): luz de ambar con la red de plomo en rombos."""
    t = _vacia(16, 32)
    for y in range(32):
        for x in range(16):
            d = abs(x - 7.5) / 7.5 * 0.6 + abs(y - 15.5) / 15.5 * 0.4
            c = _mezcla(nm._hex('fff4d0'), nm._hex('ffae4a'), d)
            if (x + y) % 8 == 0 or (x - y) % 8 == 0:
                c = nm._hex('3a2614')
            if x in (0, 15) or y in (0, 31):
                c = nm._hex('2a1c10')
            t[y, x] = (*c, 255)
    return t


def _faro():
    """La lente del faro (escalonada, de Fresnel): anillos alternos de luz."""
    t = _vacia()
    for y in range(32):
        for x in range(32):
            d = math.hypot(x - 15.5, y - 15.5)
            if d < 4:
                c = nm._hex('ffffff')
            elif int(d / 2.6) % 2:
                c = nm._hex('ffe8a8')
            else:
                c = nm._hex('fff8e2')
            if d > 14:
                c = nm._hex('ffc864')
            t[y, x] = (*c, 255)
    return t


# ----------------------------------------------------------------------
#  Materiales de Ixtara
# ----------------------------------------------------------------------
def _laca(semilla):
    """Laca negra con veladuras de brillo y su tela de arana de oro (maki-e)."""
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            b = 1 if r.random() < 0.82 else 2
            s = (x * 0.8 + y * 0.35) % 32
            if 4 <= s < 6:
                b = 3
            elif 6 <= s < 7:
                b = 2
            t[y, x] = (*LACA[b], 255)
    cx, cy = 20.5, 12.5
    radios = [k * TAU / 7 + 0.3 for k in range(7)]
    for a in radios:
        _linea(t, cx, cy, cx + math.cos(a) * 10, cy + math.sin(a) * 10, ORO[2])
    for R in (3.2, 6.0, 8.8):
        for k in range(7):
            a0, a1 = radios[k], radios[(k + 1) % 7]
            _linea(t, cx + math.cos(a0) * R, cy + math.sin(a0) * R, cx + math.cos(a1) * R, cy + math.sin(a1) * R, ORO[3])
    for _ in range(12):
        t[r.randrange(32), r.randrange(32)] = (*ORO[4], 255)      # el polvo de oro
    return t


def _porcelana(semilla, rota=False):
    """Porcelana con su craquelado; 'rota': las grietas grandes laten de carmin (emisivo aparte)."""
    d1, d2, idx, sx, sy = _celdas(semilla, 11)
    r = random.Random(semilla)
    t = _vacia()
    e = _vacia()
    for y in range(32):
        for x in range(32):
            b = 3 if r.random() > 0.15 else 2
            if sx[y, x] + sy[y, x] < -3:
                b = 4
            borde = d2[y, x] - d1[y, x]
            if borde < 0.55:
                b = 1
            t[y, x] = (*PORCELANA[b], 255)
            if rota and borde < 0.95 and idx[y, x] % 2 == 0:
                t[y, x] = (*CARMIN[2], 255)
                e[y, x] = (*nm._hex('ff4a5a'), 235)
    return t, e


def _hilo(semilla):
    """Hilo carmesi devanado en diagonal (se lee como una helice desde cualquier cara)."""
    r = random.Random(semilla)
    t = _vacia()
    paso = (0, 1, 3, 2, 1)
    for y in range(32):
        for x in range(32):
            b = paso[(x + y) % 5]
            if (x - y) % 16 == 0:
                b = 2                                              # una vuelta que cruza
            if r.random() < 0.04:
                b = 4                                              # la pelusa
            t[y, x] = (*CARMIN[b], 255)
    return t


def _oro(semilla):
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            b = r.choice((2, 3, 3))
            if int(math.hypot(x - 8, y - 8)) % 6 == 0 or int(math.hypot(x - 24, y - 24)) % 6 == 0:
                b = 1                                              # el grabado
            if (x + y) % 13 == 0 and r.random() < 0.5:
                b = 4
            t[y, x] = (*ORO[b], 255)
    return t


def _tapiz(semilla):
    """Un tapiz de Ixtara (32 x 48): cenefa, campo de laca y el ojo del telar."""
    r = random.Random(semilla)
    t = _vacia(32, 48)
    for y in range(48):
        for x in range(32):
            c = LACA[1] if (x + y) % 2 else LACA[2]
            if x < 2 or x > 29 or y < 2:
                c = ORO[3] if (x // 2 + y // 2) % 2 else CARMIN[2]
            dd = abs(x - 15.5) + abs(y - 21.5)
            if int(dd) in (4, 8, 12):
                c = CARMIN[3] if int(dd) != 8 else ORO[3]
            if abs(x - 15.5) < 6 and abs(y - 21.5) < 2.2 - abs(x - 15.5) * 0.3:
                c = CARMIN[2]
            if abs(x - 15.5) < 1.2 and abs(y - 21.5) < 1.2:
                c = ORO[4]
            t[y, x] = (*c, 255)
    for x in range(32):
        if x % 2 == 0:
            for y in range(43, 48):
                t[y, x] = (0, 0, 0, 0)                             # el fleco
    return t


# ----------------------------------------------------------------------
#  Materiales de Espinara
# ----------------------------------------------------------------------
def _tallo(semilla, venas=True):
    """Corteza de zarza: celdas alargadas, fibras y (solo en algunos tramos) una vena de savia que brilla."""
    d1, d2, idx, sx, sy = _celdas(semilla, 8, estira=(1.0, 0.45))
    r = random.Random(semilla)
    t = _vacia()
    e = _vacia()
    for y in range(32):
        for x in range(32):
            b = r.choice((1, 2, 2, 3))
            ed = d2[y, x] - d1[y, x]
            if ed < 0.7:
                b = 0
            elif ed < 1.6 and sx[y, x] < 0:
                b = min(4, b + 1)
            if (x * 3 + int(y * 0.4)) % 7 == 0:
                b = max(0, b - 1)
            t[y, x] = (*TALLO[b], 255)
    if venas:
        v = _vacia()
        _trazo(v, r, r.uniform(0, 32), r.uniform(0, 32), 26, nm._hex('7aff3a'), giro=0.35)
        m = v[..., 3] > 0
        t[m, :3] = nm._hex('3a8a22')
        e[m] = (*nm._hex('7aff3a'), 120)
    return t, e


def _espina(semilla):
    r = random.Random(semilla)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            b = r.choice((1, 1, 2))
            if (x + y) % 11 in (0, 1):
                b = 3
            if (x + y) % 11 == 0 and r.random() < 0.4:
                b = 4
            t[y, x] = (*ESPINA[b], 255)
    return t


def _petalo(semilla):
    """Un petalo (32 x 96): de la punta (arriba) a la base (abajo), terciopelo de
    anil que se aclara hacia la punta, el canto palido, nervios en abanico y, en
    la base, motas que brillan verdes (por dentro de la flor). La forma va en el alfa."""
    r = random.Random(semilla)
    t = _vacia(32, 96)
    e = _vacia(32, 96)
    canto = nm._hex('e4e2ff')
    for y in range(96):
        k = y / 95.0
        t_ = 1.0 - k                                   # 0 en la base, 1 en la punta
        if t_ < 0.62:
            hw = 0.32 + 0.68 * math.sin(t_ / 0.62 * math.pi / 2)
        else:
            hw = max(0.0, math.cos((t_ - 0.62) / 0.38 * math.pi / 2)) ** 0.75
        for x in range(32):
            dx = (x - 15.5) / 15.5
            if abs(dx) > hw:
                continue
            tono = min(4, 1 + int((1 - k) * 3.4))
            c = PETALO[tono]
            if abs(dx) > hw - 0.13:
                c = _mezcla(c, canto, 0.65) if k < 0.7 else PETALO[max(0, tono - 1)]
            for vena in (-0.62, -0.31, 0.0, 0.31, 0.62):
                xv = 15.5 + vena * hw * 15.5 * (0.35 + 0.65 * (1 - k))
                if abs(x - xv) < 0.6:
                    c = PETALO[max(0, tono - 1)]
            if r.random() < 0.05:
                c = PETALO[min(4, tono + 1)]
            t[y, x] = (*c, 255)
            if k > 0.72:
                e[y, x] = (*nm._hex('7aff3a'), int(min(1.0, (k - 0.72) / 0.28) * 150))   # la base brilla, por dentro
            if k > 0.8 and r.random() < 0.035:
                t[y, x] = (*nm._hex('9aff6a'), 255)
                e[y, x] = (*nm._hex('7aff3a'), 220)
    return t, e


def _hoja(semilla):
    """Una hoja (32 x 48) con su nervio, sus venas y el brillo de la cera; la forma en el alfa."""
    r = random.Random(semilla)
    t = _vacia(32, 48)
    for y in range(48):
        k = y / 47.0
        hw = math.sin(min(1.0, k * 1.15) * math.pi) * 0.95 + 0.05
        for x in range(32):
            dx = (x - 15.5) / 15.5
            if abs(dx) > hw:
                continue
            b = 2 if r.random() > 0.15 else 1
            if abs(dx) > hw - 0.12:
                b = 1
            if abs(x - 15.5) < 0.8:
                b = 3                                              # el nervio
            elif (abs(x - 15.5) * 1.2 + y) % 7 < 1:
                b = 1                                              # las venas
            if dx < -0.2 and 0.3 < k < 0.6 and b == 2:
                b = 3                                              # el brillo de la cera
            t[y, x] = (*HOJA[b], 255)
    return t


def _vaina(semilla):
    """Un farolillo de semilla: piel palida con venas; por dentro brilla (emisivo aparte)."""
    r = random.Random(semilla)
    t = _vacia()
    e = _vacia()
    for y in range(32):
        for x in range(32):
            b = r.choice((2, 3, 3, 4))
            vena = (x + int(math.sin(y * 0.4) * 3)) % 8 == 0
            if vena:
                b = 0
            t[y, x] = (*VAINA[b], 255)
            if not vena:
                e[y, x] = (*nm._hex('b8ff6a'), 150)
    return t, e


def _ruido_tile(rng, n, k):
    """Ruido suave que casa por los bordes: una rejilla k x k interpolada a n x n."""
    g = rng.random((k, k))
    xs = np.arange(n) * k / n
    x0 = np.floor(xs).astype(int)
    f = xs - x0
    f = f * f * (3 - 2 * f)
    x1 = (x0 + 1) % k
    x0 = x0 % k
    A, B, C, Dd = g[np.ix_(x0, x0)], g[np.ix_(x0, x1)], g[np.ix_(x1, x0)], g[np.ix_(x1, x1)]
    fy, fx = f[:, None], f[None, :]
    return (A * (1 - fx) + B * fx) * (1 - fy) + (C * (1 - fx) + Dd * fx) * fy


def _suelo_grande(semilla, rampa, motas=None, grietas=True):
    """El suelo de una escena (128 x 128 = 4 bloques): ruido de varias escalas
    cuantizado a la rampa (pixel, no degradado), grietas grandes y piedrecitas."""
    rng = np.random.default_rng(semilla)
    n = 128
    v = (_ruido_tile(rng, n, 4) * 0.5 + _ruido_tile(rng, n, 8) * 0.28 + _ruido_tile(rng, n, 16) * 0.14
         + _ruido_tile(rng, n, 64) * 0.08)
    v = (v - v.min()) / (v.max() - v.min())
    t = np.zeros((n, n, 4), np.uint8)
    cortes = (0.28, 0.45, 0.62, 0.8)
    b = np.searchsorted(cortes, v)
    for i in range(5):
        t[b == i] = (*rampa[i], 255)
    if grietas:
        d1, d2, idx, sx, sy = _celdas(semilla + 3, 7, n, n)
        t[(d2 - d1) < 1.2] = (*rampa[0], 255)
    if motas:
        r = random.Random(semilla)
        for _ in range(160):
            x, y = r.randrange(n), r.randrange(n)
            t[y, x] = (*motas, 255)
            t[y, (x + 1) % n] = (*rampa[0], 255)
    return t


def _suelo(semilla, rampa, motas=None):
    """Suelo de la escena: ruido de varias escalas, sin cuadricula."""
    r = random.Random(semilla)
    d1, d2, idx, sx, sy = _celdas(semilla, 6)
    t = _vacia()
    for y in range(32):
        for x in range(32):
            b = (idx[y, x] % 3) + 1
            if r.random() < 0.3:
                b = max(0, b - 1)
            if d2[y, x] - d1[y, x] < 0.6 and r.random() < 0.6:
                b = 0
            c = rampa[b]
            if motas and r.random() < 0.035:
                c = motas
            t[y, x] = (*c, 255)
    return t


# ----------------------------------------------------------------------
#  El registro de materiales
# ----------------------------------------------------------------------
MAT = {}
EMIS = {}          # emisivo parcial: lo que brilla dentro de un material que no brilla entero
EMISIVOS = set()   # emisivos enteros
ESTIRA = set()     # una sola imagen por cara (paneles y ventanas), en vez de mosaico por bloque


def _reg(nombre, tex, emis=None, pleno=False, estira=False):
    MAT[nombre] = tex
    if emis is not None:
        EMIS[nombre] = emis
    if pleno:
        EMISIVOS.add(nombre)
    if estira:
        ESTIRA.add(nombre)


_reg('quitina', _quitina(1, QUITINA))
_reg('quitina_o', _quitina(2, QUITINA_O))
_reg('vientre_q', _vientre_q(3))
_reg('hueso', _hueso(4))
_reg('diente', _hueso(5, DIENTE))
_reg('sillar', _sillar(6))
_reg('pizarra', _pizarra(7))
_reg('bronce', _bronce(8))
_reg('estandarte', _estandarte(9), estira=True)
_reg('ventana', _ventana(), pleno=True, estira=True)
_reg('faro', _faro(), pleno=True, estira=True)
_reg('vidriera', _vidriera(), pleno=True, estira=True)
_reg('ascua', _emisivo('ffd08a', 'ff5a1a', oscuro='5a1606', semilla=10), pleno=True)
_reg('laca', _laca(11))
_t, _e = _porcelana(12)
_reg('porcelana', _t)
_t, _e = _porcelana(13, rota=True)
_reg('porcelana_rota', _t, _e)
_reg('hilo', _hilo(14))
_reg('oro', _oro(15))
_reg('tapiz', _tapiz(16), estira=True)
_reg('hilo_luz', _emisivo('ffe0e4', 'ff2a44'), pleno=True)
_t, _e = _tallo(17, venas=False)
_reg('tallo', _t)
_t, _e = _tallo(26)
_reg('tallo_savia', _t, _e)
_reg('espina', _espina(18))
_t, _e = _petalo(19)
_reg('petalo', _t, _e, estira=True)
for _k, _nombre in enumerate(('petalo_punta', 'petalo_medio', 'petalo_base')):
    _reg(_nombre, np.ascontiguousarray(_t[_k * 32:(_k + 1) * 32]), np.ascontiguousarray(_e[_k * 32:(_k + 1) * 32]), estira=True)
    _d = np.ascontiguousarray(_t[_k * 32:(_k + 1) * 32]).copy()
    _d[..., :3] = (_d[..., :3].astype(float) * np.array((0.42, 0.38, 0.5))).astype(np.uint8)
    _reg(_nombre.replace('petalo', 'dorso'), _d, estira=True)
_reg('hoja', _hoja(20), estira=True)
_t, _e = _vaina(21)
_reg('vaina', _t, _e)
_reg('savia', _emisivo('f0ffd0', '7aff3a'), pleno=True)
_reg('polen', _emisivo('fffbc0', 'c8ff4a'), pleno=True)
_reg('fauce', nm._loseta(22, lambda x, y, r: LACA[r.choice((0, 0, 1))]))
_reg('suelo_a', _suelo_grande(23, _r('120f0c', '1c1713', '261f19', '322920', '42372b'), nm._hex('5a544c')))
_reg('suelo_b', _suelo_grande(24, _r('09090e', '0f0f15', '15151d', '1c1c26', '262632'), nm._hex('3a2a34')))
_reg('suelo_c', _suelo_grande(25, _r('050806', '0a100b', '0f1811', '152218', '1e3022'), nm._hex('2e4a2a')))


# ----------------------------------------------------------------------
#  Geometria: cajas, paneles, hebras y prismas en bloques de mundo
# ----------------------------------------------------------------------
def _caja_quads(box):
    x0, y0, z0, w, h, d = box
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    V = {0: (x0, y0, z0), 1: (x1, y0, z0), 2: (x1, y1, z0), 3: (x0, y1, z0),
         4: (x0, y0, z1), 5: (x1, y0, z1), 6: (x1, y1, z1), 7: (x0, y1, z1)}
    caras = [((5, 4, 0, 1), w, d), ((2, 3, 7, 6), w, d), ((0, 4, 7, 3), d, h),
             ((1, 0, 3, 2), w, h), ((5, 1, 2, 6), d, h), ((4, 5, 6, 7), w, h)]
    out = []
    for idx, a, b in caras:
        if a <= 0 or b <= 0:
            continue
        out.append(([V[i] for i in idx], [(a, 0), (0, 0), (0, b), (a, b)]))
    return out


def punto(M, p):
    return (M @ np.array([*p, 1.0]))[:3]


def caja(out, M, x0, y0, z0, w, h, d, mat):
    estira = mat in ESTIRA
    for pts, uv in _caja_quads((x0, y0, z0, w, h, d)):
        if estira:
            uv = [(1, 1), (0, 1), (0, 0), (1, 0)]
        out.append(([punto(M, q) for q in pts], uv, mat))


def panel(out, M, w, h, mat, g=0.04):
    """Una lamina (estandarte, petalo, hoja): x de -w/2 a w/2, y de 0 (la base de la
    imagen) a h (lo alto de la imagen), con la imagen entera en cada cara."""
    a, b = -w / 2, w / 2
    frente = [(a, 0, g / 2), (b, 0, g / 2), (b, h, g / 2), (a, h, g / 2)]
    detras = [(b, 0, -g / 2), (a, 0, -g / 2), (a, h, -g / 2), (b, h, -g / 2)]
    out.append(([punto(M, q) for q in frente], [(0, 1), (1, 1), (1, 0), (0, 0)], mat))
    out.append(([punto(M, q) for q in detras], [(1, 1), (0, 1), (0, 0), (1, 0)], mat))


def hebra(out, p0, p1, g, mat):
    """Una hebra recta de p0 a p1 (mundo)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    if L < 1e-4:
        return
    caja(out, em.marco(p0, p1 - p0), -g / 2, -g / 2, 0, g, g, L, mat)


def oct_y(out, M, y0, y1, r, mat):
    """Prisma octogonal a lo largo de la y local."""
    caja(out, M, -r, y0, -r, 2 * r, y1 - y0, 2 * r, mat)
    q = r * 0.7071 * 1.1
    caja(out, M @ vr.Ry(45 * D), -q, y0, -q, 2 * q, y1 - y0, 2 * q, mat)


def oct_z(out, M, r, z0, z1, mat):
    """Prisma octogonal a lo largo de la z local."""
    caja(out, M, -r, -r, z0, 2 * r, 2 * r, z1 - z0, mat)
    q = r * 0.7071 * 1.1
    caja(out, M @ vr.Rz(45 * D), -q, -q, z0, 2 * q, 2 * q, z1 - z0, mat)


def disco_z(out, M, r, z0, z1, mat):
    """Un disco de 16 lados a lo largo de la z local (las pestanas de los carretes)."""
    oct_z(out, M, r, z0, z1, mat)
    oct_z(out, M @ vr.Rz(22.5 * D), r, z0, z1, mat)


def transformar(qs, M):
    return [([punto(M, p) for p in P], uv, mat) for P, uv, mat in qs]


def _cuerpo(out, camino, R, perfil, deco, paso=1.1, rng=None):
    """El cuerpo sobre la curva: llama a deco(out, M, i, along, r, L, recto) en
    cada segmento y devuelve el marco de la cabeza, el de la cola y los segmentos."""
    largo = sum(float(np.linalg.norm(np.array(camino[i + 1]) - np.array(camino[i]))) for i in range(len(camino) - 1))
    n = max(30, int(largo / paso))
    pts, tg = em.catmull(camino, n)
    segs = []
    for i in range(1, n - 1):
        along = i / (n - 1)
        r = perfil(along, R)
        M = em.marco(pts[i], tg[i])
        L = float(np.linalg.norm(pts[min(i + 1, n - 1)] - pts[i - 1])) * 0.8
        t0 = tg[i - 1] / np.linalg.norm(tg[i - 1])
        t1 = tg[min(i + 1, n - 1)] / np.linalg.norm(tg[min(i + 1, n - 1)])
        recto = float(t0 @ t1) > 0.962
        deco(out, M, i, along, r, L, recto, rng)
        segs.append((i, along, M, r, L))
    return em.marco(pts[n - 1], tg[n - 1]), em.marco(pts[1], -tg[1]), segs, pts


# ======================================================================
#  A · QUELVORA, la Devoradora de Atalayas
# ======================================================================
def _q_perfil(along, R):
    if along < 0.18:
        return R * (0.42 + 0.58 * (along / 0.18) ** 0.8)
    if along > 0.86:
        return R * (1.0 - 0.2 * (along - 0.86) / 0.14)
    return R


def _q_seg(out, M, i, along, r, L, recto, rng):
    mat = 'quitina_o' if (i // 2) % 5 == 4 else 'quitina'
    oct_z(out, M, r, -L / 2, L / 2, mat)
    # el escudo dorsal, solapado hacia atras, y la placa del vientre
    caja(out, M @ vr.Rx(-7 * D), -r * 0.8, r * 0.52, -L / 2 - 0.22, r * 1.6, r * 0.56, L * 0.82, 'quitina')
    caja(out, M @ vr.Rx(5 * D), -r * 0.64, -r * 1.12, -L / 2 - 0.12, r * 1.28, r * 0.3, L * 0.78, 'vientre_q')
    # las costuras de ascua: los faros que se trago arden por dentro
    if i % 3 == 1 and recto and along > 0.08:
        oct_z(out, M, r * 1.035, -0.07, 0.07, 'ascua')
    # los remos: patas de hueso que cavan
    if i % 2 == 0 and 0.08 < along < 0.9:
        for s in (1, -1):
            Mh = M @ vr.T(r * 0.86 * s, -r * 0.2, 0) @ vr.Rz(-112 * s * D) @ vr.Rx(rng.uniform(-14, 14) * D)
            caja(out, Mh, -0.11, 0, -0.14, 0.22, r * 0.8, 0.28, 'quitina_o')
            Mk = Mh @ vr.T(0, r * 0.76, 0) @ vr.Rz(-48 * s * D)
            caja(out, Mk, -0.08, 0, -0.1, 0.16, r * 0.75, 0.2, 'quitina_o')
            caja(out, Mk @ vr.T(0, r * 0.72, 0), -0.05, 0, -0.06, 0.1, 0.42, 0.12, 'hueso')


def _torre(out, M, alto, rng, ruina=False, bandera=True):
    """Una atalaya tragada, fundida al lomo: la base comida por el caparazon, el fuste
    octogonal de sillares, ventanas que arden, matacan, almenas y el chapitel."""
    M = M @ vr.Rx(rng.uniform(-8, 8) * D) @ vr.Rz(rng.uniform(-8, 8) * D)
    rb = 1.0
    oct_y(out, M, -0.5, 0.45, 1.55, 'quitina')
    oct_y(out, M, 0.35, 0.78, 1.28, 'quitina_o')
    for k in range(5):
        a = k * 72 + rng.uniform(-15, 15)
        caja(out, M @ vr.Ry(a * D) @ vr.T(0, 0.5, rb * 0.97) @ vr.Rx(-6 * D),
             -0.13, 0, -0.07, 0.26, rng.uniform(1.0, 2.4), 0.14, 'quitina')
    oct_y(out, M, 0.4, alto, rb, 'sillar')
    yb = 1.7
    while yb < alto - 0.8:
        oct_y(out, M, yb, yb + 0.16, rb * 1.07, 'sillar')
        yb += 1.8
    for k in (0, 1, 3):
        for hv in (alto * 0.36, alto * 0.7):
            if hv < 1.1:
                continue
            Mw = M @ vr.Ry(k * 90 * D) @ vr.T(0, hv, rb)
            caja(out, Mw, -0.17, 0, -0.03, 0.34, 0.62, 0.07, 'ventana')
            caja(out, Mw @ vr.T(0, 0.62, 0), -0.22, 0, -0.05, 0.44, 0.1, 0.1, 'sillar')
    oct_y(out, M, alto, alto + 0.34, rb * 1.3, 'sillar')
    for k in range(8):
        if ruina and k in (1, 2, 5):
            continue
        a = k * 45 + 22.5
        hm = 0.6 if not ruina else rng.uniform(0.25, 0.6)
        inclina = rng.uniform(-14, 6) if ruina else 0.0
        caja(out, M @ vr.Ry(a * D) @ vr.T(0, alto + 0.34, rb * 1.13) @ vr.Rx(inclina * D),
             -0.24, 0, -0.17, 0.48, hm, 0.34, 'sillar')
    if not ruina:
        y = alto + 0.34
        capas = 7
        for j in range(capas):
            rr = 1.22 * (1 - j / capas) + 0.08
            oct_y(out, M, y, y + 0.36, rr, 'pizarra')
            y += 0.34
        caja(out, M @ vr.T(0, y, 0), -0.06, 0, -0.06, 0.12, 0.7, 0.12, 'bronce')
        oct_y(out, M, y + 0.7, y + 0.92, 0.13, 'bronce')
    else:
        for k in range(3):
            caja(out, M @ vr.T(rng.uniform(-0.5, 0.5), alto + 0.34, rng.uniform(-0.5, 0.5)) @ vr.Ry(rng.uniform(0, 90) * D),
                 -0.2, 0, -0.2, 0.4, 0.3, 0.4, 'sillar')
    if bandera:
        Mp = M @ vr.T(rb * 0.92, alto + 0.34, 0)
        caja(out, Mp, -0.05, 0, -0.05, 0.1, 2.35, 0.1, 'bronce')
        panel(out, Mp @ vr.T(0.56, 0.78, 0) @ vr.Ry(rng.uniform(-35, 35) * D), 1.0, 1.5, 'estandarte')


def _muro(out, M, r, L):
    """Un lienzo de muralla almenada sobre el lomo, entre torre y torre."""
    caja(out, M @ vr.T(0, r * 0.95, 0), -0.22, 0, -L * 0.55, 0.44, 1.05, L * 1.1, 'sillar')
    for z in (-L * 0.35, 0.0, L * 0.35):
        caja(out, M @ vr.T(0, r * 0.95 + 1.05, z), -0.25, 0, -0.17, 0.5, 0.42, 0.34, 'sillar')


def _q_cabeza(out, M, boca=24.0, rng=None):
    """La cabeza: craneo de quitina oscura con la cresta y los dientes de hueso,
    mandibulas en tres con dientes de almena y, encima, la linterna entera del
    ultimo faro que se trago (galeria, vidrieras que arden, la lente que mira al
    frente como unico ojo, la cupula de pizarra y su veleta). En la nuca, los
    estandartes de las atalayas."""
    rng = rng or random.Random(3)
    M = M @ vr.T(0, 0.2, 0.9) @ vr.S(1.45)
    # la gorguera de quitina donde entra el cuello
    for (dz, g) in ((-2.0, 1.45), (-1.55, 1.35), (-1.1, 1.25)):
        caja(out, M @ vr.T(0, 0.1, dz) @ vr.Rx(-8 * D), -g, -g * 0.7, -0.22, 2 * g, g * 1.55, 0.44, 'quitina')
    # el craneo y el hocico, de quitina, con la cresta nasal de hueso
    caja(out, M, -1.35, -0.5, -1.25, 2.7, 1.45, 2.4, 'quitina')
    caja(out, M @ vr.Rx(-5 * D), -1.42, 0.85, -1.35, 2.84, 0.32, 2.2, 'quitina_o')
    caja(out, M, -0.95, -0.5, 1.1, 1.9, 0.95, 2.2, 'quitina')
    caja(out, M @ vr.Rx(5 * D), -0.72, -0.45, 3.25, 1.44, 0.75, 1.15, 'quitina')
    caja(out, M @ vr.Rx(-8 * D), -0.15, 0.42, 1.2, 0.3, 0.18, 3.0, 'quitina_o')
    for j in range(3):
        caja(out, M @ vr.T(0, 0.62, 1.7 + j * 0.75) @ vr.Rx(-42 * D), -0.08, 0, -0.08, 0.16, 0.42 - j * 0.08, 0.16, 'hueso')
    for s in (1, -1):
        # la ceja de hueso, el pomulo, el ojillo de brasa y la pua de la sien
        caja(out, M @ vr.T(0.75 * s, 0.72, 1.0) @ vr.Rz(-14 * s * D) @ vr.Rx(10 * D), -0.5, -0.12, -0.35, 1.0, 0.26, 0.75, 'quitina_o')
        caja(out, M @ vr.T(1.3 * s, -0.12, 0.2) @ vr.Rz(10 * s * D), -0.38, -0.5, -1.0, 0.76, 1.0, 2.0, 'quitina_o')
        caja(out, M @ vr.T(1.55 * s, 0.24, 0.8), -0.05, -0.06, -0.24, 0.1, 0.12, 0.48, 'ascua')
        caja(out, M @ vr.T(1.45 * s, 0.2, -0.9) @ vr.Ry(-25 * s * D) @ vr.Rx(-100 * D), -0.1, 0, -0.1, 0.2, 1.3, 0.2, 'hueso')
        # colmillos y dientes almenados de arriba
        Mc = M @ vr.T(0.62 * s, -0.5, 4.05) @ vr.Rx(10 * D)
        caja(out, Mc, -0.14, -0.6, -0.14, 0.28, 0.6, 0.28, 'diente')
        caja(out, Mc @ vr.T(0, -0.55, 0) @ vr.Rx(12 * D), -0.08, -0.55, -0.08, 0.16, 0.55, 0.16, 'diente')
        for j in range(8):
            h = 0.36 if j % 2 == 0 else 0.2
            caja(out, M @ vr.T(0.8 * s, -0.5, 1.25 + j * 0.34), -0.1, -h, -0.1, 0.2, h, 0.2, 'diente')
    # la boca, encendida por dentro
    caja(out, M, -0.72, -0.9, -0.2, 1.44, 0.42, 3.3, 'ascua')
    caja(out, M, -0.5, -0.75, -0.6, 1.0, 0.6, 0.6, 'ascua')
    # las mandibulas en tres
    Mj = M @ vr.T(0, -0.58, -0.45) @ vr.Rx(boca * D)
    caja(out, Mj, -0.7, -0.5, 0.05, 1.4, 0.5, 3.9, 'quitina')
    caja(out, Mj, -0.5, -0.62, 0.8, 1.0, 0.16, 2.6, 'quitina')
    caja(out, Mj, -0.5, 0.0, 0.3, 1.0, 0.06, 3.2, 'ascua')
    for s in (1, -1):
        for j in range(8):
            h = 0.34 if j % 2 else 0.18
            caja(out, Mj @ vr.T(0.52 * s, 0.0, 0.5 + j * 0.42), -0.1, 0, -0.1, 0.2, h, 0.2, 'diente')
        Ms = M @ vr.T(1.25 * s, -0.35, 0.3) @ vr.Ry(-(12 + boca * 0.7) * s * D) @ vr.Rx(boca * 0.3 * D)
        caja(out, Ms, -0.3, -0.36, 0, 0.6, 0.72, 2.9, 'quitina_o')
        caja(out, Ms @ vr.T(0, 0.36, 0.4), -0.22, 0, 0, 0.44, 0.14, 2.2, 'quitina')
        Ms2 = Ms @ vr.T(0, 0, 2.8) @ vr.Ry(30 * s * D)
        caja(out, Ms2, -0.24, -0.3, 0, 0.48, 0.6, 2.1, 'quitina_o')
        Ms3 = Ms2 @ vr.T(0, 0, 2.0) @ vr.Ry(30 * s * D)
        caja(out, Ms3, -0.14, -0.2, 0, 0.28, 0.4, 1.1, 'quitina_o')
        caja(out, Ms3 @ vr.T(0, 0, 1.05) @ vr.Ry(20 * s * D), -0.07, -0.1, 0, 0.14, 0.2, 0.6, 'hueso')
        for (Mx, n, z0) in ((Ms, 5, 0.4), (Ms2, 4, 0.3)):
            for j in range(n):
                h = 0.4 if j % 2 else 0.22
                caja(out, Mx @ vr.T(-0.3 * s, 0, z0 + j * 0.44) @ vr.Rz(90 * s * D), -0.1, 0, -0.1, 0.2, h, 0.2, 'diente')
    # la linterna del faro, sobre el craneo
    Ml = M @ vr.T(0, 1.12, 0.1)
    oct_y(out, Ml, 0.0, 0.2, 1.6, 'bronce')                                   # el suelo de la galeria
    for k in range(16):
        caja(out, Ml @ vr.Ry(k * 22.5 * D) @ vr.T(0, 0.2, 1.5), -0.04, 0, -0.04, 0.08, 0.55, 0.08, 'bronce')
    for k in range(8):
        caja(out, Ml @ vr.Ry((k * 45 + 22.5) * D) @ vr.T(0, 0.72, 1.48), -0.63, 0, -0.04, 1.26, 0.08, 0.08, 'bronce')
    rL, hL = 1.05, 1.7
    oct_y(out, Ml, 0.2, 0.5, rL * 1.04, 'sillar')
    for k in range(1, 8):
        caja(out, Ml @ vr.Ry(k * 45 * D) @ vr.T(0, 0.5, rL * 0.97), -0.43, 0, -0.03, 0.86, hL, 0.06, 'vidriera')
        caja(out, Ml @ vr.Ry((k * 45 + 22.5) * D) @ vr.T(0, 0.5, rL * 1.04), -0.06, 0, -0.06, 0.12, hL, 0.12, 'bronce')
    Mf = Ml @ vr.T(0, 0.5 + hL / 2, 0.3)
    for (rr, dz) in ((0.72, 0.0), (0.56, 0.1), (0.4, 0.2), (0.22, 0.28)):
        oct_z(out, Mf, rr, dz - 0.05, dz + 0.05, 'faro')
    yC = 0.5 + hL
    oct_y(out, Ml, yC, yC + 0.22, rL * 1.2, 'bronce')
    y = yC + 0.22
    for j in range(6):
        oct_y(out, Ml, y, y + 0.34, rL * 1.12 * (1 - j / 6) + 0.12, 'pizarra')
        y += 0.32
    caja(out, Ml @ vr.T(0, y, 0), -0.05, 0, -0.05, 0.1, 0.9, 0.1, 'bronce')
    oct_y(out, Ml, y + 0.9, y + 1.1, 0.14, 'bronce')
    panel(out, Ml @ vr.T(0.4, y + 0.45, 0) @ vr.Ry(25 * D), 0.75, 0.48, 'estandarte')
    # dos torrecillas, a los lados de la nuca, como cuernos
    for s in (1, -1):
        Mt = M @ vr.T(1.2 * s, 0.9, -1.0) @ vr.Rz(-38 * s * D) @ vr.Rx(-25 * D)
        oct_y(out, Mt, 0, 0.6, 0.42, 'sillar')
        for k in range(4):
            caja(out, Mt @ vr.Ry((k * 90 + 45) * D) @ vr.T(0, 0.6, 0.38), -0.12, 0, -0.08, 0.24, 0.22, 0.16, 'sillar')
        yy = 0.6
        for j in range(5):
            oct_y(out, Mt, yy, yy + 0.3, 0.42 * (1 - j / 5) + 0.06, 'pizarra')
            yy += 0.28
    # los estandartes de la nuca, en su travesano de bronce
    Mb = M @ vr.T(0, 0.95, -2.35)
    caja(out, Mb, -2.1, 0, -0.08, 4.2, 0.16, 0.16, 'bronce')
    for s in (1, -1):
        panel(out, Mb @ vr.T(1.25 * s, -2.6, 0) @ vr.Ry(rng.uniform(-12, 12) * D), 1.2, 2.6, 'estandarte')
    faro_p = punto(Mf, (0, 0, 0.4))
    faro_d = np.array(Mf[:3, 2], float)
    return faro_p, faro_d / np.linalg.norm(faro_d)


def camino_quelvora():
    return [(26, -5.0, 16), (21, 1.0, 13.5), (17, 4.8, 11), (12.5, 3.0, 9), (9.0, -1.5, 7.5), (6.0, -3.5, 6.5),
            (2.5, 0.5, 5.0), (-1.0, 4.6, 3.0), (-4.5, 3.2, 0.5), (-7.0, 1.9, -2.5), (-7.5, 2.0, -6.0),
            (-5.0, 3.8, -8.8), (-1.5, 7.6, -9.6), (1.5, 11.4, -8.6), (3.2, 13.6, -6.6), (4.0, 13.4, -3.8)]


def quelvora(camino=None, boca=24.0, R=1.75, semilla=5):
    """Devuelve (quads, info) con info['faro'] = (posicion, direccion) y los cruces con el suelo."""
    rng = random.Random(semilla)
    out = []
    camino = camino or camino_quelvora()
    M_cab, M_cola, segs, pts = _cuerpo(out, camino, R, _q_perfil, _q_seg, rng=rng)
    # las atalayas tragadas: en lo alto de los arcos, separadas
    cand = [s for s in segs if 0.1 < s[1] < 0.74 and s[2][1, 1] > 0.62]
    torres = []
    for s in cand:
        if not torres or s[0] - torres[-1][0] >= 6:
            torres.append(s)
    alturas = (4.8, 6.2, 3.8, 5.6, 4.4)
    for k, (i, along, M, r, L) in enumerate(torres):
        _torre(out, M @ vr.T(0, r * 0.82, 0), alturas[k % 5], rng, ruina=(k % 3 == 1), bandera=(k % 2 == 0))
    usados = {s[0] for s in torres}
    for (i, along, M, r, L) in cand:
        if all(abs(i - j) >= 2 for j in usados):
            _muro(out, M, r, L)
    faro = _q_cabeza(out, M_cab, boca, rng)
    cruces = [pts[i] for i in range(1, len(pts)) if (pts[i - 1][1] - 0.3) * (pts[i][1] - 0.3) < 0]
    return out, {'faro': faro, 'cruces': cruces}


# ======================================================================
#  B · IXTARA, la Hilandera
# ======================================================================
def _i_perfil(along, R):
    if along < 0.2:
        return R * (0.35 + 0.65 * (along / 0.2) ** 0.8)
    if along > 0.9:
        return R * (1.0 - 0.25 * (along - 0.9) / 0.1)
    return R


def _i_seg(out, M, i, along, r, L, recto, rng):
    q = 0.7071 * 1.1
    if i % 3 == 0 and 0.06 < along < 0.97:
        # el carrete: la pestana de laca con el canto de oro
        g = r * 1.38
        disco_z(out, M, g, -0.16, 0.16, 'laca')
        disco_z(out, M, g * 1.05, -0.05, 0.05, 'oro')
        oct_z(out, M, r * 0.92, -L / 2, L / 2, 'laca')
        # los tachones de oro en el canto
        for k in range(16):
            caja(out, M @ vr.Rz(k * 22.5 * D) @ vr.T(0, g * 1.04, 0), -0.06, 0, -0.06, 0.12, 0.1, 0.12, 'oro')
    else:
        # el hilo devanado entre pestana y pestana
        oct_z(out, M, r, -L / 2, L / 2, 'hilo')


def _brazo(out, M, s, largo1, largo2, abre, alza, dobla, palma=0.0):
    """Un brazo de aguja: hombro de oro, brazo y antebrazo de laca con sus anillos,
    y cuatro dedos-aguja de oro en abanico. Devuelve las puntas de los dedos (mundo)."""
    Mh = M @ vr.Rz(-abre * s * D) @ vr.Rx(alza * D)
    oct_y(out, Mh, -0.34, 0.34, 0.36, 'oro')
    oct_y(out, Mh, 0, largo1, 0.2, 'laca')
    for t in (0.3, 0.62):
        oct_y(out, Mh, largo1 * t, largo1 * t + 0.14, 0.26, 'oro')
    caja(out, Mh @ vr.T(0, largo1 * 0.96, -0.1) @ vr.Rx(-150 * D), -0.06, 0, -0.06, 0.12, 0.7, 0.12, 'oro')   # la pua del codo
    Me = Mh @ vr.T(0, largo1, 0) @ vr.Rz(-dobla * s * D) @ vr.Rx(12 * D)
    oct_y(out, Me, -0.26, 0.26, 0.28, 'oro')
    oct_y(out, Me, 0, largo2, 0.16, 'laca')
    oct_y(out, Me, largo2 * 0.5, largo2 * 0.5 + 0.12, 0.21, 'oro')
    Mw = Me @ vr.T(0, largo2, 0) @ vr.Rz(palma * s * D)
    caja(out, Mw, -0.22, 0, -0.06, 0.44, 0.34, 0.12, 'laca')
    puntas = []
    for k, a in enumerate((-33, -11, 11, 33)):
        Mf = Mw @ vr.T(-0.15 + k * 0.1, 0.3, 0) @ vr.Rz(a * D)
        largo = 1.9 if k in (1, 2) else 1.5
        caja(out, Mf, -0.035, 0, -0.035, 0.07, largo, 0.07, 'oro')
        puntas.append(punto(Mf, (0, largo, 0)))
    return puntas


_MASCARA = (1.25, 2.0, 0.9)       # los semiejes del elipsoide de la cara (ancho, alto, fondo)


def _en_cara(M, x, y, dz=0.0):
    """El marco de un punto de la cara: en la superficie del elipsoide, con la z local
    hacia fuera (la normal)."""
    a, b, c = _MASCARA
    k = 1 - (x / a) ** 2 - (y / b) ** 2
    z = c * math.sqrt(max(0.02, k))
    n = np.array((x / a ** 2, y / b ** 2, z / c ** 2))
    n = n / np.linalg.norm(n)
    return M @ em.marco(np.array((x, y, z)) + n * dz, n)


def _i_mascara(out, M, partida=0.0):
    """La mascara de porcelana, facetada como una talla: planos tangentes a un
    elipsoide que se solapan (frente, cejas, pomulos, nariz, menton). Encima, los
    ojos cerrados pintados de oro, las pestanas, las lagrimas de hilo y la marca
    de la frente; dos grietas que laten. 'partida': lo que se separan las dos
    mitades (detras, la boca de agujas)."""
    filas = ((1.7, (0.2, 0.55)), (1.3, (0.22, 0.6, 0.92)), (0.9, (0.22, 0.6, 0.95)), (0.5, (0.22, 0.6, 0.98, 1.12)),
             (0.1, (0.22, 0.6, 0.98, 1.12)), (-0.3, (0.22, 0.6, 0.98)), (-0.7, (0.22, 0.58, 0.92)),
             (-1.1, (0.2, 0.52, 0.78)), (-1.45, (0.18, 0.45)), (-1.78, (0.14,)))
    rotas = {(1, 0.6, 2), (-1, 0.98, 5)}
    for j, (y, xs) in enumerate(filas):
        for s_ in (1, -1):
            for x in xs:
                mat = 'porcelana_rota' if (s_, x, j) in rotas else 'porcelana'
                Mf = vr.T(s_ * partida / 2, 0, 0) @ _en_cara(np.eye(4), s_ * x, y)
                caja(out, M @ Mf, -0.24, -0.24, -0.6, 0.48, 0.48, 0.6, mat)
    # la nariz: una arista que sobresale
    for s_ in (1, -1):
        Mn = M @ vr.T(s_ * partida / 2, 0, 0) @ _en_cara(np.eye(4), s_ * 0.06, 0.1, 0.06) @ vr.Rx(-4 * D)
        caja(out, Mn, -0.1 if s_ > 0 else -0.02, -0.55, -0.2, 0.12, 1.1, 0.22, 'porcelana')

    def pinta(x, y, w, h, mat, dz=0.03, giro=0.0):
        s_ = 1 if x >= 0 else -1
        Mp = M @ vr.T(s_ * partida / 2, 0, 0) @ _en_cara(np.eye(4), x, y, dz) @ vr.Rz(giro * D)
        caja(out, Mp, -w / 2, -h / 2, 0, w, h, 0.03, mat)

    for s_ in (1, -1):
        cx = s_ * 0.55
        for k in range(7):
            t = k / 6
            x = cx + (t - 0.5) * 0.7
            y = 0.42 - math.sin(t * math.pi) * 0.14
            pinta(x, y, 0.14, 0.11, 'laca', giro=(t - 0.5) * 50 * s_)             # el ojo cerrado, de laca
            pinta(x, y - 0.07, 0.14, 0.04, 'oro', dz=0.05, giro=(t - 0.5) * 50 * s_)
        for k in range(3):
            x = cx + (k - 1) * 0.2
            pinta(x, 0.2, 0.035, 0.14, 'oro')                                    # las pestanas
        for k in range(5):
            t = k / 4
            x = cx + (t - 0.5) * 0.78
            y = 0.72 + math.sin(t * math.pi) * 0.09
            pinta(x, y, 0.17, 0.045, 'oro', giro=-(t - 0.5) * 30 * s_)           # la ceja
        for k in range(6):
            pinta(cx - s_ * 0.22, 0.12 - k * 0.22, 0.1, 0.24, 'hilo_luz')        # la lagrima
    pinta(0.0, 1.32, 0.2, 0.2, 'hilo_luz', giro=45)                              # la marca de la frente
    pinta(0.0, 1.62, 0.1, 0.1, 'oro', giro=45)
    for k in range(9):
        a = (k - 4) / 4
        pinta(a * 0.85, 1.72 + (1 - a * a) * 0.12, 0.16, 0.08, 'oro', dz=0.05)  # la diadema
    for x in (-0.55, 0.0, 0.55):
        pinta(x, 1.9 + (0.12 if x == 0 else 0.0), 0.08, 0.3, 'oro', dz=0.05)
    if partida <= 0:
        pinta(0.0, -0.98, 0.42, 0.1, 'laca')                                     # los labios, cerrados
        pinta(0.0, -0.98, 0.5, 0.035, 'oro', dz=0.05)
    else:
        # dentro: la boca de agujas y la luz del fondo
        caja(out, M, -partida / 2 - 0.05, -1.5, -0.65, partida + 0.1, 2.9, 0.4, 'fauce')
        caja(out, M, -0.16, -0.9, -0.55, 0.32, 1.5, 0.12, 'hilo_luz')
        for s_ in (1, -1):
            for k in range(9):
                y = -1.3 + k * 0.3
                L = 0.6 if k % 2 else 0.38
                Mn = M @ vr.T(s_ * (partida / 2 + 0.02), y, 0.1) @ vr.Rz(90 * s_ * D)
                caja(out, Mn, -0.03, 0, -0.03, 0.06, L, 0.06, 'oro')


def _i_cabeza(out, M, partida=0.0, rng=None):
    rng = rng or random.Random(4)
    M = M @ vr.S(1.35)
    # el cuello de laca y la gorguera de agujas
    oct_y(out, M, -2.6, -1.6, 0.75, 'laca')
    oct_y(out, M, -1.75, -1.6, 0.95, 'oro')
    for k in range(18):
        a = k * 20 * D
        Mn = M @ vr.T(0, -1.68, 0) @ vr.Ry(a) @ vr.T(0, 0, 0.85) @ vr.Rx(78 * D)
        caja(out, Mn, -0.03, 0, -0.03, 0.06, 0.9 + (k % 2) * 0.45, 0.06, 'oro')
    # la mascara
    _i_mascara(out, M, partida)
    # el craneo de laca detras de la mascara
    caja(out, M, -1.05, -1.4, -1.5, 2.1, 2.9, 1.0, 'laca')
    # el halo: un aro de oro con ocho husos pequenos y una corona de agujas, detras
    Mh = M @ vr.T(0, 0.3, -1.3)
    for k in range(20):
        a = k * TAU / 20
        caja(out, Mh @ vr.Rz(a) @ vr.T(0, 2.6, 0), -0.43, -0.07, -0.07, 0.86, 0.14, 0.14, 'oro')
    for k in range(8):
        Mk = Mh @ vr.Rz(k * TAU / 8 + 0.2) @ vr.T(0, 2.6, 0.05) @ vr.Rz(90 * D)
        oct_y(out, Mk, -0.3, -0.22, 0.2, 'oro')
        oct_y(out, Mk, 0.22, 0.3, 0.2, 'oro')
        oct_y(out, Mk, -0.22, 0.22, 0.12, 'hilo')
    for k in range(16):
        a = (k + 0.5) * TAU / 16
        caja(out, Mh @ vr.Rz(a) @ vr.T(0, 2.75, 0), -0.04, 0, -0.04, 0.08, 2.0 if k % 2 else 1.2, 0.08, 'oro')
    # el velo de hilos que cae de la nuca
    for k in range(14):
        x = -1.0 + k * (2.0 / 13)
        p = punto(M, (x, 1.2 - abs(x) * 0.4, -1.45))
        dirs = [np.array((x * 0.05, -1.0, -0.35)), np.array((x * 0.08, -1.0, -0.15)), np.array((x * 0.12, -1.0, 0.1))]
        largo = rng.uniform(2.0, 3.2)
        for d in dirs:
            d = d / np.linalg.norm(d)
            q = p + d * largo
            hebra(out, p, q, 0.05, 'hilo_luz')
            p = q


def camino_ixtara():
    return [(10.0, 1.3, 7.0), (5.0, 1.3, 10.5), (-1.5, 1.3, 10.0), (-6.5, 1.3, 6.0), (-7.5, 1.3, 0.0),
            (-4.0, 1.3, -4.5), (1.5, 1.4, -5.0), (5.5, 1.6, -1.5), (5.0, 2.0, 3.0), (1.5, 3.2, 4.2),
            (-0.5, 6.0, 2.6), (-0.6, 9.5, 1.0), (-0.2, 13.0, 0.4), (0.2, 16.0, 0.8), (0.4, 17.4, 1.6)]


def ixtara(camino=None, partida=0.0, R=1.15, semilla=7):
    rng = random.Random(semilla)
    out = []
    camino = camino or camino_ixtara()
    M_cab, M_cola, segs, pts = _cuerpo(out, camino, R, _i_perfil, _i_seg, rng=rng)
    # los cinco pares de brazos, en la parte que se alza: un abanico alrededor del cuerpo
    altos = [s_ for s_ in segs if 0.62 < s_[1] < 0.94]
    paso = max(1, len(altos) // 5)
    elegidos = list(reversed(altos[::paso][:5]))
    puntas = []
    for k, (i, along, M, r, L) in enumerate(elegidos):
        p = M[:3, 3]
        Mw = vr.T(*p)
        fila = []
        for s_ in (1, -1):
            Mb = Mw @ vr.T(r * 0.95 * s_, 0, 0.15)
            abre = 12 + k * 21
            fila.append(_brazo(out, Mb, s_, 4.3 - k * 0.15, 3.8, abre, -12, -16 + k * 7, palma=10))
        puntas.append(fila)
    # el telar de luz: alas de hilo entre brazo y brazo, a cada lado (como un arpa)
    for k in range(len(puntas) - 1):
        for lado in (0, 1):
            for j in range(4):
                hebra(out, puntas[k][lado][j], puntas[k + 1][lado][j], 0.045, 'hilo_luz')
            hebra(out, puntas[k][lado][0], puntas[k + 1][lado][3], 0.035, 'hilo_luz')
    # por encima de la cabeza, de mano a mano, y anclas al suelo desde las de abajo
    for j in range(4):
        hebra(out, puntas[0][0][j], puntas[0][1][3 - j], 0.05, 'hilo_luz')
    for lado in (0, 1):
        q = puntas[-1][lado][2]
        hebra(out, q, np.array((q[0] * 1.4, 0.05, q[2] + 3.0)), 0.04, 'hilo_luz')
        hebra(out, q, np.array((q[0] * 1.2, 0.05, q[2] - 2.0)), 0.04, 'hilo_luz')
    # tapices colgados de las vueltas del cuerpo
    bajos = [s for s in segs if 0.2 < s[1] < 0.5]
    for (i, along, M, r, L) in bajos[::7][:3]:
        p = M[:3, 3]
        f = np.array(M[:3, 2])
        lado = np.cross(f, (0, 1, 0))
        lado = lado / max(np.linalg.norm(lado), 1e-6)
        panel(out, vr.T(*(p + lado * (r * 1.02) + np.array((0, -p[1] + 0.05, 0)))) @ vr.Ry(math.degrees(math.atan2(lado[0], lado[2])) * D),
              1.6, p[1] + r * 0.6, 'tapiz')
    # la cola que se deshace en hilo por el suelo
    pc = punto(M_cola, (0, 0, 0))
    for k in range(5):
        p = pc.copy()
        a = rng.uniform(-0.6, 0.6)
        d = -np.array(M_cola[:3, 2])
        for paso_ in range(4):
            d2 = d + np.array((math.sin(a) * 0.5, 0, math.cos(a) * 0.5))
            q = p + d2 / np.linalg.norm(d2) * 1.6
            q[1] = 0.06
            hebra(out, p, q, 0.04, 'hilo_luz')
            p = q
            a += rng.uniform(-0.5, 0.5)
    # la cabeza: mirando al frente, algo hacia abajo
    p = M_cab[:3, 3]
    Mc = em.marco(p + np.array((0, 1.2, 0.2)), (0, -0.22, 1.0))
    _i_cabeza(out, Mc, partida, rng)
    return out, {}


# ======================================================================
#  C · ESPINARA, la Zarza que Florece
# ======================================================================
def _e_perfil(along, R):
    if along < 0.15:
        return R * (0.45 + 0.55 * (along / 0.15) ** 0.8)
    if along > 0.86:
        return R * (1.0 - 0.18 * (along - 0.86) / 0.14)
    return R


def _flor(out, M, tam, rng, abierta=1.0):
    """Una rosa de la zarza: caliz, sepalos, tres coronas de petalos y el corazon que brilla."""
    oct_y(out, M, 0, 0.35 * tam, 0.22 * tam, 'tallo')
    for k in range(5):
        Ms = M @ vr.Ry(k * 72 * D) @ vr.T(0, 0.25 * tam, 0.16 * tam) @ vr.Rx(70 * D)
        panel(out, Ms, 0.26 * tam, 0.55 * tam, 'hoja')
    for anillo, (n, rad, inc, h) in enumerate(((4, 0.08, 12, 0.7), (5, 0.16, 32, 0.85), (6, 0.24, 52 * abierta + 8, 0.95))):
        for k in range(n):
            a = k * 360 / n + anillo * 25 + rng.uniform(-6, 6)
            Mp = M @ vr.Ry(a * D) @ vr.T(0, 0.3 * tam, rad * tam) @ vr.Rx(inc * D)
            panel(out, Mp, 0.62 * tam, h * tam, 'petalo')
    oct_y(out, M, 0.3 * tam, 0.55 * tam, 0.1 * tam, 'savia')


def _e_seg(out, M, i, along, r, L, recto, rng, rosas=None):
    oct_z(out, M, r * 0.78, -L / 2, L / 2, 'tallo_savia' if i % 6 == 0 else 'tallo')
    for v in range(3):
        a = along * TAU * 9 + v * TAU / 3
        Mv = M @ vr.T(math.cos(a) * r * 0.58, math.sin(a) * r * 0.58, 0) @ vr.Rz(a) @ vr.Ry(12 * D)
        oct_z(out, Mv, r * 0.44, -L * 0.58, L * 0.58, 'tallo')
    for _ in range(rng.randint(3, 5)):
        a = rng.uniform(0, TAU)
        Mt = M @ vr.Rz(a) @ vr.T(0, r * 0.95, rng.uniform(-L / 2, L / 2)) @ vr.Rx(-rng.uniform(15, 45) * D)
        ln = rng.uniform(0.7, 1.5)
        caja(out, Mt, -0.14, 0, -0.14, 0.28, ln * 0.5, 0.28, 'espina')
        caja(out, Mt @ vr.T(0, ln * 0.45, 0), -0.08, 0, -0.08, 0.16, ln * 0.4, 0.16, 'espina')
        caja(out, Mt @ vr.T(0, ln * 0.8, 0), -0.035, 0, -0.035, 0.07, ln * 0.3, 0.07, 'hueso')
    if i % 4 == 1:
        Mh = M @ vr.Rz(rng.uniform(0, TAU)) @ vr.T(0, r * 0.9, 0) @ vr.Rx(-rng.uniform(30, 60) * D)
        panel(out, Mh, 0.75, 1.3, 'hoja')
    if i % 5 == 3 and 0.12 < along < 0.86:
        _flor(out, M @ vr.Rz(rng.uniform(-35, 35) * D) @ vr.T(0, r * 0.85, 0), rng.uniform(1.0, 1.5), rng)
    if i % 5 == 2 and 0.15 < along < 0.8:
        s = rng.choice((1, -1))
        p0 = punto(M, (r * 0.9 * s, 0, 0))
        p1 = p0 + np.array((s * 0.4, 0.5, 0))
        p2 = p1 + np.array((s * 0.6, -0.4, 0))
        p3 = p2 + np.array((s * 0.1, -0.9, 0))
        hebra(out, p0, p1, 0.1, 'tallo')
        hebra(out, p1, p2, 0.09, 'tallo')
        hebra(out, p2, p3, 0.07, 'tallo')
        Mv = vr.T(*p3)
        oct_y(out, Mv, -0.85, -0.05, 0.3, 'vaina')
        oct_y(out, Mv, -0.95, -0.85, 0.18, 'vaina')
        oct_y(out, Mv, -0.12, 0.0, 0.18, 'tallo')
        oct_y(out, Mv, -0.6, -0.35, 0.12, 'savia')


def _e_cabeza(out, M, abre=48.0, rng=None):
    """La flor-fauce: caliz y gorguera de sepalos con espinas, seis petalos-mandibula
    curvos con dientes de espina por dentro, el craneo en el centro con los ojos de
    savia, los estambres que muerden con su polen y el pistilo-lengua."""
    rng = rng or random.Random(9)
    M = M @ vr.T(0, 0, 0.6) @ vr.S(1.55)
    for (rr, z0, z1) in ((0.95, -0.6, -0.1), (1.15, -0.15, 0.35), (1.3, 0.3, 0.75)):
        oct_z(out, M, rr, z0, z1, 'tallo')
    for k in range(8):
        a = k * 45 + 22.5
        Ms = M @ vr.Rz(a * D) @ vr.T(0, 1.15, 0.1) @ vr.Rx(-112 * D)
        panel(out, Ms, 0.8, 2.0, 'hoja')
        for j in range(2):
            caja(out, Ms @ vr.T(0.2 * (1 if j else -1), 0.6 + j * 0.6, 0) @ vr.Rx(-60 * D), -0.05, 0, -0.05, 0.1, 0.35, 0.1, 'espina')
    # el nectar: el fondo de la flor arde verde detras del craneo
    disco_z(out, M, 1.0, 0.28, 0.34, 'savia')
    disco_z(out, M, 0.62, 0.34, 0.4, 'polen')
    for k in range(7):
        caja(out, M @ vr.Rz((k * 360 / 7 + 26 + 180 / 7) * D) @ vr.T(0, 0.3, 0.36), -0.05, 0, -0.03, 0.1, 0.72, 0.06, 'tallo')
    # el craneo, dentro, mirando al frente: de una bestia que no existe (cuatro
    # orbitas en dos filas, hocico de pico ganchudo, arcos en las sienes y dos
    # cuernecillos), atado por la zarza
    Mk = M @ vr.T(0, 0.12, 0.62) @ vr.S(1.18)
    caja(out, Mk, -0.55, -0.32, -0.55, 1.1, 0.92, 1.05, 'hueso')
    caja(out, Mk @ vr.Rx(-8 * D), -0.42, 0.55, -0.48, 0.84, 0.22, 0.86, 'hueso')
    caja(out, Mk, -0.5, -0.38, 0.45, 1.0, 0.72, 0.18, 'hueso')
    for (x, y, w, h) in ((0.24, 0.3, 0.3, 0.22), (0.3, -0.02, 0.22, 0.16)):
        for s_ in (1, -1):
            caja(out, Mk @ vr.T(x * s_, y, 0.62), -w / 2, -h / 2, 0, w, h, 0.03, 'fauce')
            caja(out, Mk @ vr.T(x * s_, y, 0.64), -w * 0.28, -h * 0.3, 0, w * 0.56, h * 0.6, 0.04, 'savia')
    Mh_ = Mk @ vr.T(0, -0.22, 0.6) @ vr.Rx(10 * D)
    caja(out, Mh_, -0.3, -0.22, 0, 0.6, 0.42, 0.62, 'hueso')
    Mh2 = Mh_ @ vr.T(0, -0.05, 0.6) @ vr.Rx(16 * D)
    caja(out, Mh2, -0.2, -0.18, 0, 0.4, 0.32, 0.5, 'hueso')
    caja(out, Mh2 @ vr.T(0, -0.1, 0.48) @ vr.Rx(55 * D), -0.11, -0.4, -0.09, 0.22, 0.42, 0.2, 'hueso')     # el gancho
    for s_ in (1, -1):
        caja(out, Mh_ @ vr.T(0.12 * s_, 0.12, 0.3), -0.02, -0.02, -0.12, 0.04, 0.04, 0.3, 'fauce')         # las narinas
        for j in range(4):
            caja(out, Mh_ @ vr.T(0.26 * s_, -0.22, 0.1 + j * 0.16), -0.03, -0.24 + j * 0.03, -0.03, 0.06, 0.24 - j * 0.03, 0.06, 'diente')
        caja(out, Mk @ vr.T(0.6 * s_, -0.05, 0.1), -0.06, -0.08, -0.45, 0.12, 0.16, 0.9, 'hueso')        # el arco de la sien
        caja(out, Mk @ vr.T(0.35 * s_, 0.72, -0.25) @ vr.Rz(-28 * s_ * D) @ vr.Rx(-35 * D), -0.07, 0, -0.07, 0.14, 0.45, 0.14, 'hueso')
    for k in range(3):
        a = (k - 1) * 0.5
        hebra(out, punto(Mk, (-0.75, 0.15 + a, -0.2)), punto(Mk, (0.0, 0.7 + a * 0.3, 0.1)), 0.1, 'tallo')
        hebra(out, punto(Mk, (0.0, 0.7 + a * 0.3, 0.1)), punto(Mk, (0.75, 0.15 + a, -0.2)), 0.1, 'tallo')
    # los estambres
    for k in range(10):
        a = k * 36 + 10
        Ms = Mk @ vr.Rz(a * D) @ vr.T(0, 0.75, 0.2) @ vr.Rx(-35 * D)
        p = punto(Ms, (0, 0, 0))
        for j, (dl, curva) in enumerate(((0.9, 20), (0.8, 25), (0.6, 30))):
            Ms = Ms @ vr.Rx(curva * D)
            q = punto(Ms, (0, dl, 0))
            hebra(out, p, q, 0.09 - j * 0.02, 'tallo')
            Ms = Ms @ vr.T(0, dl, 0)
            p = q
        oct_y(out, vr.T(*p), -0.14, 0.14, 0.14, 'polen')
    # el pistilo-lengua
    Mp = Mk @ vr.T(0, -0.6, 0.6) @ vr.Rx(70 * D)
    p = punto(Mp, (0, 0, 0))
    for j, (dl, curva) in enumerate(((0.9, -10), (0.8, -18), (0.7, -26), (0.5, -30))):
        Mp = Mp @ vr.Rx(curva * D)
        q = punto(Mp, (0, dl, 0))
        hebra(out, p, q, 0.22 - j * 0.04, 'tallo')
        Mp = Mp @ vr.T(0, dl, 0)
        p = q
    for s in (1, -1):
        hebra(out, p, punto(Mp @ vr.Rz(25 * s * D), (0, 0.45, 0)), 0.07, 'savia')
    # los seis petalos-mandibula, curvos, de tres laminas, con dientes de espina por dentro
    for k in range(7):
        a = k * 360 / 7 + 26
        M1 = M @ vr.Rz(a * D) @ vr.T(0, 1.0, 0.55) @ vr.Rx((90 - abre) * D)
        panel(out, M1, 2.1, 1.7, 'petalo_base')
        panel(out, M1 @ vr.T(0, 0, -0.06), 2.1, 1.7, 'dorso_base')
        M2 = M1 @ vr.T(0, 1.7, 0) @ vr.Rx(22 * D)
        panel(out, M2, 2.1, 1.6, 'petalo_medio')
        panel(out, M2 @ vr.T(0, 0, -0.06), 2.1, 1.6, 'dorso_medio')
        M3 = M2 @ vr.T(0, 1.6, 0) @ vr.Rx(30 * D)
        panel(out, M3, 2.1, 1.5, 'petalo_punta')
        panel(out, M3 @ vr.T(0, 0, -0.06), 2.1, 1.5, 'dorso_punta')
        for Mx, n, ancho in ((M1, 3, 0.9), (M2, 3, 0.85), (M3, 2, 0.55)):
            for j in range(n):
                y = 0.3 + j * 0.45
                for s in (1, -1):
                    caja(out, Mx @ vr.T(ancho * s, y, 0.02) @ vr.Rx(-75 * D), -0.06, 0, -0.06, 0.12, 0.38, 0.12, 'espina')


def camino_espinara():
    pts = []
    for k in range(11):
        a = 0.2 + k * 0.62
        rr = 9.5 - k * 0.48
        pts.append((math.cos(a) * rr, 1.5 + k * 0.28, math.sin(a) * rr))
    pts += [(-1.5, 6.5, -2.0), (-1.0, 10.0, -3.0), (0.6, 13.2, -2.0), (1.6, 14.8, 0.4), (2.0, 14.6, 2.6)]
    return pts


def espinara(camino=None, abre=48.0, R=1.6, semilla=11):
    rng = random.Random(semilla)
    out = []
    camino = camino or camino_espinara()
    M_cab, M_cola, segs, pts = _cuerpo(out, camino, R, _e_perfil, _e_seg, rng=rng)
    # las raices de la cola, que se hunden
    pc = punto(M_cola, (0, 0, 0))
    for k in range(5):
        a = k * TAU / 5 + rng.uniform(-0.3, 0.3)
        p = pc.copy()
        for paso_ in range(3):
            q = p + np.array((math.cos(a) * 0.9, -0.55, math.sin(a) * 0.9))
            hebra(out, p, q, 0.28 - paso_ * 0.07, 'tallo')
            p = q
            a += rng.uniform(-0.4, 0.4)
    _e_cabeza(out, M_cab, abre, rng)
    return out, {}


# ----------------------------------------------------------------------
#  Dibujo
# ----------------------------------------------------------------------
def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.5):
    for P, UV, mat in qs:
        tex = MAT[mat]
        if mat in EMISIVOS:
            luz, emis = np.ones(3), tex
        else:
            luz, emis = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, ambiente), EMIS.get(mat)
        envolver = mat not in ESTIRA
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], tex, luz, emis, niebla,
                         brillo=brillo, envolver=envolver)

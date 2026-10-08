"""
Boceto 3D de Novilis, el Caballero Solar (jefe elemental del fuego), para la
ficha de diseno.

Malla de cajas al estilo Minecraft, en pixeles de modelo (16 = 1 bloque, Y
hacia abajo, el frente mira a -Z, los pies en y = +24), con MATERIALES en
mosaico como el boceto de Nerea: sirve para decidir forma, tamano y color, no
es la textura final.

Una armadura forjada con lava y el poder del sol: placas de acero quemado con
grietas de lava que brillan, oro solar en los bordes, una capa roja que arde
por abajo, el nucleo solar en el pecho y una espada flamigera.

Tres opciones (variante):
  A  Corona de llamas  yelmo con cuernos y corona de llamas (el boceto de Juan)
  B  Halo de sol       sin cuernos: un halo de sol con rayos detras de la cabeza
  C  Brasa Viva        la armadura rota: se ve la lava de dentro, cuernos hacia
                       atras y la capa hecha jirones

Alto: ~130 px = 8,1 bloques hasta el yelmo (las llamas de la corona suben
casi un bloque mas).

Las grietas, el nucleo, la corona y la hoja cambian de color con la fase:
I ambar, II oro, III blanco solar, IV carmesi; y la Furia, fuego azul.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm

# ----------------------------------------------------------------------
#  Colores de cada fase: (nucleo, principal, hondo)
# ----------------------------------------------------------------------
FASE = {
    1: ('ffe2a0', 'ff8a1e', 'b8420c'),
    2: ('fff2b8', 'ffc23a', 'c8780c'),
    3: ('fffbe8', 'fff0b0', 'e8a838'),
    4: ('ffb4a8', 'ff2a3a', '8a0a1a'),
    'furia': ('e8fbff', '5ad8ff', '1a5ab8'),
}
NOMBRE_FASE = {1: 'Brasa', 2: 'Llamarada', 3: 'Mediodía', 4: 'Dios de la Guerra', 'furia': 'Furia'}

ACERO_Q = nm._rampa('140e10', '1f1617', '2c2020', '3d2c28', '553c32')   # acero quemado
ACERO_O = nm._rampa('0d090b', '160f11', '1f1617', '2a1e1d', '3a2a26')
COTA = nm._rampa('0e0b0c', '1d1718', '2e2524', '463a36', '5e4f48')
ORO = nm._rampa('5a3410', '8a5418', 'c07c22', 'e8a83a', 'ffd77a')
CAPA = nm._rampa('320a0c', '540d12', '7a1618', 'a02420', 'c23c28')
HOJA = nm._rampa('4a3c3a', '6e5c56', '948078', 'b8a498', 'dccabc')
OBSID = nm._rampa('0c0812', '150e1e', '201530', '2e2044', '3e2e5a')
CUERO = nm._rampa('1c120c', '2c1c12', '3e2818', '523622', '68462e')


def _mezcla(a, b, t):
    t = min(1.0, max(0.0, t))
    return tuple(max(0, min(255, int(int(a[i]) + (int(b[i]) - int(a[i])) * t))) for i in range(3))


def _vacia():
    return np.zeros((16, 16, 4), np.uint8)


def _ruido(rampa, semilla, pesos=(0, 1, 2, 2, 2, 3), juntas=True):
    r = random.Random(semilla)
    t = _vacia()
    for y in range(16):
        for x in range(16):
            b = r.choice(pesos)
            if juntas and (x % 16 == 0 or y % 16 == 0):
                b = 0
            t[y, x] = (*rampa[b], 255)
    return t


def _grietas(semilla, n=2, largo=14):
    """Grietas: trazos continuos que tuercen poco a poco y a veces se parten.
    Dan la vuelta a la loseta (para que case al repetirse)."""
    r = random.Random(semilla)
    m = np.zeros((16, 16), np.uint8)

    def trazo(x, y, a, pasos, valor):
        for _ in range(pasos):
            m[int(round(y)) % 16, int(round(x)) % 16] = max(m[int(round(y)) % 16, int(round(x)) % 16], valor)
            a += r.uniform(-0.55, 0.55)
            x += math.cos(a)
            y += math.sin(a)
            if valor == 2 and r.random() < 0.13:
                trazo(x, y, a + r.choice((-1.1, 1.1)), r.randint(2, 4), 1)

    for _ in range(n):
        trazo(r.uniform(0, 16), r.uniform(0, 16), r.uniform(0, math.tau), largo, 2)
    return m


def _placa(rampa, semilla, col, n_grietas, tono_calor=0.35, largo=11):
    """Acero quemado con grietas de lava que brillan del color de la fase (sin
    juntas: las placas ya las marcan las cajas)."""
    nuc, pri, hon = (nm._hex(c) for c in col)
    r = random.Random(semilla)
    t = _vacia()
    for y in range(16):
        for x in range(16):
            b = r.choice((1, 2, 2, 2, 2, 3))
            if r.random() < 0.05:
                b = 4                                    # un brillo de metal
            t[y, x] = (*rampa[b], 255)
    e = _vacia()
    g = _grietas(semilla + 100, n_grietas, largo) if n_grietas else np.zeros((16, 16), np.uint8)
    for y in range(16):
        for x in range(16):
            if g[y, x] == 2:
                c = nuc if (x * 3 + y) % 6 == 0 else pri
                t[y, x] = (*c, 255)
                e[y, x] = (*c, 210)
            elif g[y, x] == 1:
                t[y, x] = (*hon, 255)
                e[y, x] = (*hon, 150)
            else:
                # el acero de alrededor de una grieta se calienta (rojo oscuro, sin brillo)
                cerca = any(g[(y + j) % 16, (x + i) % 16] == 2 for i in (-1, 0, 1) for j in (-1, 0, 1))
                if cerca:
                    t[y, x, :3] = _mezcla(t[y, x, :3], hon, tono_calor)
    return t, e


def _emisivo_radial(c1, c2, semilla=0, motas=0.0, c3=None):
    a, b = nm._hex(c1), nm._hex(c2)
    r = random.Random(semilla)
    t = _vacia()
    for y in range(16):
        for x in range(16):
            d = max(abs(x - 7.5), abs(y - 7.5)) / 7.5
            c = _mezcla(a, b, d)
            if motas and r.random() < motas:
                c = _mezcla(c, nm._hex(c3) if c3 else a, 0.6)
            t[y, x] = (*c, 255)
    return t


def _llama(col, semilla, punta=False):
    """Llama (se estira sobre la cara): abajo el nucleo, arriba el hondo, con
    lenguas que suben. La punta va del principal al hondo, que se enfria."""
    nuc, pri, hon = (nm._hex(c) for c in col)
    rojo = _mezcla(hon, (60, 8, 6), 0.35)
    r = random.Random(semilla)
    t = _vacia()
    for x in range(16):
        lengua = r.uniform(-0.12, 0.12) + 0.08 * math.sin(x * 1.3)
        for y in range(16):
            v = y / 15 + lengua            # 0 arriba, 1 abajo
            if punta:
                c = _mezcla(rojo, pri, v)
            elif v > 0.62:
                c = _mezcla(pri, nuc, (v - 0.62) / 0.38)
            else:
                c = _mezcla(hon, pri, v / 0.62)
            t[y, x] = (*c, 255)
    return t


def _lava(col, semilla):
    nuc, pri, hon = (nm._hex(c) for c in col)
    r = random.Random(semilla)
    t = _vacia()
    for y in range(16):
        for x in range(16):
            k = 0.5 + 0.5 * math.sin(x * 0.9 + math.sin(y * 0.7) * 2.2 + r.uniform(-0.4, 0.4))
            c = _mezcla(hon, pri, k) if k < 0.75 else _mezcla(pri, nuc, (k - 0.75) / 0.25)
            t[y, x] = (*c, 255)
    return t


def _capa(semilla, col, arde=False):
    """Pano rojo con pliegues verticales; si arde, la parte de abajo son brasas."""
    nuc, pri, hon = (nm._hex(c) for c in col)
    r = random.Random(semilla)
    t = _vacia()
    e = _vacia()
    for y in range(16):
        for x in range(16):
            pl = (0, 1, 2, 3, 3, 2, 1, 2, 3, 4, 3, 2, 1, 1, 2, 3)[x]
            b = max(0, min(4, pl + r.choice([-1, 0, 0, 0, 1])))
            c = CAPA[b]
            if arde:
                k = y / 15
                if k > 0.45:
                    q = (k - 0.45) / 0.55
                    if r.random() < q * 0.9:
                        c2 = pri if r.random() < 0.6 else nuc
                        c = _mezcla(c, c2, q)
                        e[y, x] = (*c, int(255 * q))
                    else:
                        c = _mezcla(c, (20, 8, 8), q * 0.8)   # chamuscado
            t[y, x] = (*c, 255)
    return t, e


def _cota(semilla):
    t = _vacia()
    r = random.Random(semilla)
    for y in range(16):
        for x in range(16):
            anillo = ((x + (y // 2) % 2 * 2) % 4 in (0, 1)) and y % 2 == 0
            b = r.choice([2, 3]) if anillo else r.choice([0, 1])
            t[y, x] = (*COTA[b], 255)
    return t


def _oro(semilla):
    r = random.Random(semilla)
    t = _vacia()
    for y in range(16):
        for x in range(16):
            b = r.choice([2, 2, 3, 3, 4]) if (x + y) % 9 else 1
            if y in (0, 15):
                b = 1
            t[y, x] = (*ORO[b], 255)
    return t


_CACHE = {}
GRIETAS = {1: 1, 2: 2, 3: 2, 4: 3, 'furia': 2}     # la armadura se va rajando con las fases
ESTIRA = {'llama', 'llama_p', 'hoja'}                 # se estiran sobre la cara (no se repiten)
nm.ESTIRADOS.update(ESTIRA)


def _hoja(col):
    """La hoja de la espada (estirada): acero oscuro en el centro y los filos al rojo."""
    nuc, pri, hon = (nm._hex(c) for c in col)
    t = _vacia()
    for y in range(16):
        for x in range(16):
            d = abs(x - 7.5) / 7.5              # 0 centro, 1 filo
            if d > 0.8:
                c = _mezcla(pri, nuc, (d - 0.8) / 0.2)
            elif d > 0.55:
                c = _mezcla(HOJA[1], hon, (d - 0.55) / 0.25)
            else:
                c = HOJA[2] if (x + y) % 5 else HOJA[3]
            t[y, x] = (*c, 255)
    e = _vacia()
    for y in range(16):
        for x in range(16):
            d = abs(x - 7.5) / 7.5
            if d > 0.62:
                e[y, x] = (*t[y, x, :3], int(255 * min(1.0, (d - 0.62) / 0.3)))
    return t, e


def _grabado(semilla, col, n_grietas):
    """Acero oscuro con un grabado de oro fino (un rombo con un punto) y alguna grieta."""
    t, e = _placa(ACERO_O, semilla, col, n_grietas, 0.2)
    for y in range(16):
        for x in range(16):
            d = abs(x - 7.5) + abs(y - 7.5)
            if 6.0 <= d < 7.0 or (x in (7, 8) and y in (7, 8)):
                if e[y, x, 3] == 0:
                    t[y, x] = (*ORO[2 if (x + y) % 3 else 3], 255)
    return t, e


def materiales(fase=1):
    """(texturas, brillos, plenos) de la fase. plenos: brillan enteros, sin luz."""
    if fase in _CACHE:
        return _CACHE[fase]
    col = FASE[fase]
    nuc, pri, hon = col
    n = GRIETAS[fase]
    tex, emi = {}, {}
    tex['placa'], emi['placa'] = _placa(ACERO_Q, 11, col, n)
    tex['placa_b'], emi['placa_b'] = _placa(ACERO_Q, 17, col, n + 2, largo=14)      # la rota (opcion C)
    tex['placa_osc'], emi['placa_osc'] = _placa(ACERO_O, 13, col, max(0, n - 1), 0.2)
    tex['grabado'], emi['grabado'] = _grabado(26, col, max(0, n - 1))
    tex['cota'] = _cota(14)
    tex['oro'] = _oro(15)
    tex['capa'], _ = _capa(16, col)
    tex['capa_arde'], emi['capa_arde'] = _capa(16, col, True)
    tex['hoja'], emi['hoja'] = _hoja(col)
    tex['acero'] = _ruido(HOJA, 18, (1, 2, 3, 3, 4), juntas=False)
    tex['obsidiana'] = _ruido(OBSID, 19, (0, 1, 2, 2, 3, 4))
    tex['cuero'] = _ruido(CUERO, 20, (0, 1, 1, 2, 3), juntas=False)
    tex['lava'] = _lava(col, 21)
    tex['nucleo'] = _emisivo_radial(nuc, pri, 22)
    tex['llama'] = _llama(col, 23)
    tex['llama_p'] = _llama(col, 24, punta=True)
    tex['visor'] = _emisivo_radial(nuc, pri, 25)
    plenos = {'lava', 'nucleo', 'llama', 'llama_p', 'visor'}
    _CACHE[fase] = (tex, emi, plenos)
    return _CACHE[fase]


def registrar(nombre, tex, emis=None, pleno=False):
    """Para los materiales de las escenas (suelo, estatuas...): en todas las fases."""
    for f in FASE:
        t, e, p = materiales(f)
        t[nombre] = tex
        if emis is not None:
            e[nombre] = emis
        if pleno:
            p.add(nombre)


# ----------------------------------------------------------------------
#  Ayudas
# ----------------------------------------------------------------------
nodo = nm.nodo


def llama_nodo(nombre, off, rot, alto, ancho=4.0):
    """Una llama de cajas: la base ancha y amarilla, la punta fina y roja."""
    a = ancho
    return nodo(nombre, off, rot, [((-a / 2, -alto * 0.62, -a / 2, a, alto * 0.62, a), 'llama')], [
        nodo(nombre + '_p', (0, -alto * 0.62, 0), (rot[0] * 0.4, 0, rot[2] * 0.5),
             [((-a * 0.32, -alto * 0.42, -a * 0.32, a * 0.64, alto * 0.42, a * 0.64), 'llama_p')])])


def rayos_pecho(r_in, largo, z, n=8, ancho=2.0):
    return [nodo(f'rayo_pecho_{k}', (0, 0, 0), (0, 0, k * 360 / n),
                 [((-ancho / 2, -r_in - (largo if k % 2 == 0 else largo * 0.6), z, ancho,
                    (largo if k % 2 == 0 else largo * 0.6), 1.0), 'oro')]) for k in range(n)]


# ----------------------------------------------------------------------
#  La espada solar: flamigera de filos al rojo, con el canal de lava y el sol
#  en la cruz. +Y es hacia la punta; la empunadura en el origen.
# ----------------------------------------------------------------------
LARGO_HOJA = 58


def espada(variante='A', nombre='espada'):
    L = LARGO_HOJA
    hoja = [((-3.2, 12, -1.0, 6.4, L, 2.0), 'hoja'),
            ((-1.1, 14, -1.25, 2.2, L - 6, 2.5), 'lava')]        # el canal, por las dos caras
    paso = (L - 6) / 7
    for i in range(7):                                         # filo ondulado
        o = 1.1 if i % 2 == 0 else -1.1
        hoja.append(((-4.8 + o, 13 + paso * i, -0.8, 9.6, paso, 1.6), 'hoja'))
    hoja += [((-2.6, 12 + L, -0.8, 5.2, 6, 1.6), 'hoja'), ((-1.2, 18 + L, -0.6, 2.4, 5, 1.2), 'hoja')]
    cruz = [((-13, 8, -2.4, 26, 4, 4.8), 'oro'),
            ((-15, 3, -2, 3.5, 6, 4), 'oro'), ((11.5, 3, -2, 3.5, 6, 4), 'oro'),
            ((-4, 5.5, -3.2, 8, 8, 6.4), 'nucleo')]                     # el sol de la cruz
    if variante == 'B':
        cruz += [((-17, 9, -1, 4, 2, 2), 'oro'), ((13, 9, -1, 4, 2, 2), 'oro')]   # la N lleva la de la A
    empu = [((-1.6, -9, -1.6, 3.2, 17, 3.2), 'cuero'),
            ((-2.6, -13, -2.6, 5.2, 4.5, 5.2), 'oro'),
            ((-1.8, -15, -1.8, 3.6, 2.2, 3.6), 'nucleo')]
    return nodo(nombre, (0, 0, 0), (0, 0, 0), empu + cruz, [nodo(nombre + '_hoja', (0, 0, 0), (0, 0, 0), hoja)])


PUNTA_ESPADA = 23 + LARGO_HOJA     # la punta, en el espacio de la espada


# ----------------------------------------------------------------------
#  El esqueleto
# ----------------------------------------------------------------------
HOMBRO_X = 18.5


def _brazo(s, nombre, variante, mano_hijos):
    c = variante == 'C'
    x0 = 3.5 * s - 8.5                                         # la hombrera, echada hacia fuera
    hombrera = [((x0, -7, -11, 17, 9, 22), 'placa'),
                ((x0 - 0.5, -7.6, -11.5, 18, 1.4, 23), 'oro'),
                ((x0 - 0.6 + 0.8 * s, 1.5, -10.5, 17, 4.5, 21), 'placa_osc'),
                ((x0 - 0.8 + 1.6 * s, 5.5, -10, 16.6, 4.5, 20), 'placa'),
                ((x0 - 1.0 + 1.6 * s, 9.6, -9.6, 16.8, 1.2, 19.2), 'oro'),
                ((12.6 * s - 2.3, -3.6, -3.6, 4.6, 7.2, 7.2), 'nucleo')]   # el sol, por fuera
    hijos_h = []
    if variante in ('A', 'C'):
        hijos_h += [llama_nodo(f'llama_h1_{nombre}', (6 * s, -7, -5), (-12, 0, 16 * s), 11 if c else 9, 4.2),
                    llama_nodo(f'llama_h2_{nombre}', (9 * s, -7, 3), (14, 0, 26 * s), 9 if c else 7, 3.6),
                    llama_nodo(f'llama_h3_{nombre}', (2 * s, -7, 6), (20, 0, 8 * s), 6, 3.0)]
    if variante == 'B':
        hijos_h += [nodo(f'pua_h_{nombre}', (7 * s, -7, 0), (0, 0, 18 * s), [((-1.5, -8, -1.5, 3, 8, 3), 'oro')])]
    brazo_cajas = [((-5, 0, -5, 10, 22, 10), 'lava' if c else 'cota'),
                   ((-5.6, 4, -5.6, 11.2, 12, 11.2), 'placa_b' if c else 'placa')]
    ante_cajas = [((-5.4, -2.5, -6, 10.8, 6, 12), 'oro'),                   # codera
                  ((-5.6, 3, -5.6, 11.2, 12, 11.2), 'placa'),
                  ((-6.8, 13, -6.8, 13.6, 7, 13.6), 'placa'),                 # vuelo del brazal
                  ((-7.1, 18.6, -7.1, 14.2, 1.4, 14.2), 'oro')]
    if c:
        ante_cajas[1] = ((-5.6, 3, -5.6, 11.2, 6, 11.2), 'placa_b')
        ante_cajas.append(((-5, 8.5, -5, 10, 5, 10), 'lava'))
    return nodo('hombro_' + nombre, (HOMBRO_X * s, -38, 0), (0, 0, 0), hombrera, hijos_h + [
        nodo('brazo_' + nombre, (0, 4, 0), (0, 0, 0), brazo_cajas, [
            nodo('antebrazo_' + nombre, (0, 22, 0), (0, 0, 0), ante_cajas, [
                nodo('mano_' + nombre, (0, 20, 0), (0, 0, 0), [
                    ((-5.2, 0, -5.2, 10.4, 8, 10.4), 'placa_osc'),
                    ((-5.5, 1, -5.8, 11, 2, 2), 'oro'),                      # nudillos
                    ((-5, 8, -4.2, 10, 3.5, 8.4), 'placa_osc'),              # dedos
                ], mano_hijos),
            ]),
        ]),
    ])


def _pierna(s, nombre, variante):
    c = variante == 'C'
    return nodo('pierna_' + nombre, (8 * s, 2, 0), (0, 0, 0), [
        ((-6, 0, -6, 12, 26, 12), 'cota'),
        ((-7, 1, -7.6, 14, 18, 8.4), 'placa_b' if c else 'placa'),          # quijote
        ((-7.3, 0.2, -7.9, 14.6, 1.5, 8.8), 'oro'),
        ((6 * s - 0.6, 3, -6, 1.2, 14, 12), 'placa_osc'),                    # la placa de fuera
    ], [
        nodo('espinilla_' + nombre, (0, 26, 0), (0, 0, 0), [
            ((-6.4, -4, -9, 12.8, 8, 4.6), 'placa'),                          # rodillera
            ((-6.6, -4.4, -9.3, 13.2, 1.2, 5), 'oro'),
            ((-2, -6.5, -10.2, 4, 5, 2.4), 'oro'),                            # su pua
            ((-6, 0, -6.4, 12, 26, 12.8), 'placa'),
            ((-1, 4, -7.1, 2, 19, 1), 'oro'),                                 # arista de la greba
            *([((-5.4, 12, -6.9, 10.8, 6, 0.6), 'lava')] if c else []),
        ], [
            nodo('pie_' + nombre, (0, 26, 0), (0, 0, 0), [
                ((-6.8, -7, -11, 13.6, 7, 18), 'placa_osc'),
                ((-5.8, -4.5, -14, 11.6, 4.5, 3.4), 'placa'),
                ((-7.1, -7.5, -11.3, 14.2, 1.2, 18.6), 'oro'),
            ]),
        ]),
    ])


def _cabeza(variante):
    v = variante
    cajas = [
        ((-9.5, -20, -9.5, 19, 20, 19), 'placa'),
        ((-10, -15, -10.3, 20, 2.8, 2.6), 'oro'),                 # ceja del yelmo
        ((-7, -11.8, -10.25, 14, 2.4, 0.8), 'visor'),             # la T: la raja de los ojos
        ((-1.2, -11.8, -10.3, 2.4, 9.2, 0.9), 'visor'),           # y la de la boca
        ((-10.2, -11, -9.4, 3.2, 11, 8), 'placa_osc'),            # carrilleras
        ((7, -11, -9.4, 3.2, 11, 8), 'placa_osc'),
        ((-7.6, -3, -10.8, 15.2, 3.6, 3.4), 'placa_osc'),         # barbote
        ((-1.3, -23.5, -9, 2.6, 4.8, 19), 'oro'),                 # cresta
    ]
    hijos = []
    if v == 'A':
        cajas.append(((-10.2, -22, -10.2, 20.4, 2.8, 20.4), 'oro'))     # aro de la corona
        for s, n in ((1, 'izq'), (-1, 'der')):
            # cuernos de toro: salen de lado, se curvan hacia arriba y hacia delante
            hijos.append(nodo('cuerno_' + n, (9 * s, -14, 1), (8, 0, 78 * s), [((-3, -8, -3, 6, 8, 6), 'obsidiana')], [
                nodo('cuerno2_' + n, (0, -8, 0), (18, 0, -38 * s), [((-2.4, -8, -2.4, 4.8, 8, 4.8), 'obsidiana')], [
                    nodo('cuerno3_' + n, (0, -8, 0), (20, 0, -34 * s), [((-1.7, -7, -1.7, 3.4, 7, 3.4), 'obsidiana')], [
                        nodo('cuerno4_' + n, (0, -7, 0), (16, 0, -18 * s), [((-1, -6, -1, 2, 6, 2), 'oro')])])])]))
        # la corona de llamas: mas alta delante, en el centro
        for k in range(9):
            a = math.radians(-90 + k * 40)
            x, z = math.cos(a) * 7.6, math.sin(a) * 7.6
            alto = (20, 14, 10, 8, 7, 7, 8, 10, 14)[k]
            hijos.append(llama_nodo(f'corona_{k}', (x, -22, z), (-z * 2.0, 0, -x * 2.0), alto, 4.0))
    elif v == 'B':
        cajas += [((-10.2, -22, -10.2, 20.4, 2.8, 20.4), 'oro')]
        for k in range(7):                                         # corona de puas de oro
            x = -7.8 + k * 2.6
            alto = (5, 7, 9, 12, 9, 7, 5)[k]
            cajas.append(((x - 1.0, -22 - alto, -10.4, 2.0, alto, 2.0), 'oro'))
        cajas.append(((-1.5, -31, -10.9, 3.0, 3.0, 1.2), 'nucleo'))
        # el halo: un aro de oro y rayos de fuego detras de la cabeza
        halo = []
        n = 24
        R = 24.0
        for k in range(n):
            halo.append(nodo(f'halo_aro_{k}', (0, 0, 0), (0, 0, k * 360 / n), [((-3.4, -R - 1.6, -1, 6.8, 3.2, 2), 'oro'),
                                                                               ((-3.2, -R + 1.6, -0.6, 6.4, 1.2, 1.2), 'nucleo')]))
        for k in range(12):
            largo = 16 if k % 2 == 0 else 9
            halo.append(nodo(f'halo_rayo_{k}', (0, 0, 0), (0, 0, k * 30 + 15), [], [
                llama_nodo(f'halo_rayo_{k}_l', (0, -R - 1.4, 0), (0, 0, 0), largo, 3.6)]))
        hijos.append(nodo('halo', (0, -11, 13), (0, 0, 0), [((-4, -4, -0.5, 8, 8, 1), 'nucleo')], halo))
    else:  # C
        cajas += [((-9.7, -16, -9.7, 4, 4, 0.5), 'lava'), ((4.5, -6, -9.8, 4, 3, 0.5), 'lava'),     # el yelmo rajado
                  ((-10.2, -22, -10.2, 20.4, 2.8, 20.4), 'placa_osc')]
        for s, n in ((1, 'izq'), (-1, 'der')):
            # cuernos de demonio: salen hacia arriba y se curvan hacia atras
            hijos.append(nodo('cuerno_' + n, (8.5 * s, -18, 2), (-10, 0, 40 * s), [((-3, -9, -3, 6, 9, 6), 'obsidiana')], [
                nodo('cuerno2_' + n, (0, -9, 0), (-38, 0, -12 * s), [((-2.4, -9, -2.4, 4.8, 9, 4.8), 'obsidiana')], [
                    nodo('cuerno3_' + n, (0, -9, 0), (-40, 0, -8 * s), [((-1.7, -8, -1.7, 3.4, 8, 3.4), 'obsidiana')], [
                        nodo('cuerno4_' + n, (0, -8, 0), (-36, 0, 0), [((-1, -6, -1, 2, 6, 2), 'lava')])])])]))
        for k in range(11):
            a = math.radians(-90 + k * 360 / 11)
            x, z = math.cos(a) * 7.8, math.sin(a) * 7.8
            alto = (24, 18, 13, 10, 9, 8, 8, 9, 10, 13, 18)[k]
            hijos.append(llama_nodo(f'corona_{k}', (x, -22, z), (-z * 2.4, 0, -x * 2.4), alto, 4.4))
    return nodo('cabeza', (0, -4, 0), (0, 0, 0), cajas, hijos)


def _capa_nodo(variante):
    if variante == 'C':
        # jirones: cinco tiras de largos distintos, todas ardiendo por abajo
        tiras = []
        for k, (x, largo, giro) in enumerate(((-17, 70, -4), (-8.5, 84, 2), (0, 62, -2), (8.5, 88, 3), (17, 74, 5))):
            tiras.append(nodo(f'capa_t{k}', (x, 0, 0), (0, giro, giro * 0.5), [
                ((-4.4, 0, 0, 8.8, largo - 16, 1.5), 'capa'), ((-4.4, largo - 16, 0, 8.8, 16, 1.5), 'capa_arde')]))
        return nodo('capa_1', (0, -40, 9.5), (6, 0, 0), [((-20, -1, -1, 40, 4, 3), 'capa')], tiras)
    ancho = (40, 43, 46) if variante == 'A' else (40, 45, 50)
    flecos = [((-ancho[2] / 2 + 2 + 6.0 * i, 26, 0, 4.0, 4 + (i * 7) % 7, 1.5), 'capa_arde') for i in range(int(ancho[2] / 6.0))]
    return nodo('capa_1', (0, -40, 9.5), (7, 0, 0), [((-ancho[0] / 2, 0, 0, ancho[0], 30, 1.5), 'capa')], [
        nodo('capa_2', (0, 30, 0), (4, 0, 0), [((-ancho[1] / 2, 0, 0, ancho[1], 30, 1.5), 'capa')], [
            nodo('capa_3', (0, 30, 0), (5, 0, 0), [((-ancho[2] / 2, 0, 0, ancho[2], 14, 1.5), 'capa'),
                                                   ((-ancho[2] / 2, 14, 0, ancho[2], 12, 1.5), 'capa_arde'), *flecos]),
        ]),
    ])


def esqueleto(variante='A', con_espada=True):
    if variante == 'N':
        return esqueleto_n(con_espada)
    v = variante
    c = v == 'C'
    pecho = [
        ((-14, -12, -9, 28, 12, 18), 'cota'),                      # vientre
        *[((-14.6 + i * 0.6, -12 + 4 * i, -10.2, 29.2 - i * 1.2, 3.6, 20.4), 'placa' if i % 2 == 0 else 'placa_osc') for i in range(3)],
        ((-18, -40, 5, 36, 28, 6.5), 'placa'),                     # espaldar
        ((-9.5, -45, -8.5, 19, 5.5, 17), 'placa'),                 # gola
        ((-10, -45.6, -9, 20, 1.4, 18), 'oro'),
    ]
    if c:
        # el peto abierto: dos mitades y la lava en medio
        pecho += [((-19, -40, -11, 13, 16, 16), 'placa_b'), ((6, -40, -11, 13, 16, 16), 'placa_b'),
                  ((-16, -24, -10.5, 10, 12, 15), 'placa_b'), ((6, -24, -10.5, 10, 12, 15), 'placa_b'),
                  ((-6, -38, -8.5, 12, 26, 12), 'lava'),
                  ((-6.6, -39, -11.4, 1.4, 27, 2), 'oro'), ((5.2, -39, -11.4, 1.4, 27, 2), 'oro'),
                  ((-4, -33, -9.6, 8, 8, 1.4), 'nucleo')]
        rayos = []
    else:
        pecho += [((-19, -40, -11, 38, 16, 16), 'placa'),               # el peto: ancho arriba
                  ((-16, -24.5, -10.6, 32, 12.5, 15), 'placa'),         # y estrecho abajo
                  ((-19.6, -40.6, -11.6, 39.2, 1.6, 17), 'oro'),
                  ((-16.4, -14, -11, 32.8, 1.5, 15.6), 'oro'),
                  ((-5, -33, -12.4, 10, 10, 1.6), 'nucleo')]            # el nucleo solar
        rayos = [nodo('rayos_pecho', (0, -28, 0), (0, 0, 0), [], rayos_pecho(6.5, 7 if v == 'A' else 9, -12.2))]
    faldas = [nodo('falda_' + n, (8.5 * s, 1, -10.6), (-4, 0, 6 * s), [
        ((-7, 0, 0, 14, 15, 2.2), 'placa'), ((-7.3, 13.6, -0.3, 14.6, 1.6, 2.8), 'oro')]) for s, n in ((1, 'izq'), (-1, 'der'))]
    faldas += [nodo('falda_l' + n, (15.6 * s, 1, 0), (0, 0, 6 * s), [((-1.1, 0, -9, 2.2, 13, 18), 'placa')]) for s, n in ((1, 'izq'), (-1, 'der'))]
    mano_der = [nodo('agarre', (0, 5, 0), (-90, 0, 0), [], [espada(v)] if con_espada else [])]
    return nodo('raiz', (0, 0, 0), (0, 0, 0), [], [
        nodo('pelvis', (0, -36, 0), (0, 0, 0), [
            ((-15, -6, -10, 30, 8, 20), 'placa_osc'),
            ((-15.5, -2.4, -10.5, 31, 3, 21), 'cuero'),               # cinturon
            ((-3.4, -4.4, -11.4, 6.8, 6.8, 1.4), 'oro'),              # hebilla
            ((-1.8, -2.8, -11.9, 3.6, 3.6, 0.8), 'nucleo'),
        ], faldas + [
            _pierna(1, 'izq', v), _pierna(-1, 'der', v),
            nodo('torso', (0, -6, 0), (0, 0, 0), pecho, rayos + [
                _capa_nodo(v),
                nodo('manto', (0, -42, 3), (0, 0, 0), [((-19, -1, 0, 38, 5, 9), 'capa')]),
                nodo('cuello', (0, -44, -1), (0, 0, 0), [((-5, -4, -5, 10, 4, 10), 'cota')], [_cabeza(v)]),
                _brazo(1, 'izq', v, [nodo('sol_mano', (0, 4, -2), (0, 0, 0), [])]),
                _brazo(-1, 'der', v, mano_der),
            ]),
        ]),
    ])


# ----------------------------------------------------------------------
#  Novilis (ronda 2): la cabeza con los cuernos de la A y el halo de la B, y
#  un cuerpo nuevo, mas imponente: hombreras por capas que suben hacia fuera,
#  peto en V con el sol en relieve, gola alta que enmarca el yelmo, tabardo,
#  escarcelas por capas, rodilleras con su sol, grebas que se abren abajo y
#  una capa doble con el sol bordado. Los pies, por fin, en el suelo (y = 24).
# ----------------------------------------------------------------------
HOMBRO_X_N = 21.0


def _rayos_relieve(nombre, centro, r_in, z, largos=(7, 4.5), ancho=2.4):
    """Los ocho rayos del sol del pecho, en relieve, con la punta encendida."""
    hijos = []
    for k in range(8):
        L = largos[k % 2]
        hijos.append(nodo(f'{nombre}_{k}', (0, 0, 0), (0, 0, k * 45), [
            ((-ancho / 2, -r_in - L, z, ancho, L, 2.0), 'oro'),
            ((-ancho * 0.3, -r_in - L - 1.6, z + 0.3, ancho * 0.6, 1.8, 1.4), 'nucleo')]))
    return nodo(nombre, centro, (0, 0, 0), [], hijos)


def _brazo_n(s, nombre, mano_hijos):
    x0 = 3.5 * s - 10
    hombrera = [
        ((x0, -9, -13, 20, 11, 26), 'placa'),                              # la cupula
        ((x0 + 1, -12.4, -11.5, 18, 3.6, 23), 'grabado'),                  # la cresta, grabada
        ((x0 + 0.6, -13.2, -12, 18.8, 1.2, 24), 'oro'),
        ((x0 - 0.4, -9.6, -13.6, 20.8, 1.2, 27.2), 'oro'),
        ((x0 + 6 + 6 * s, -7, 10.5, 8, 8, 3), 'oro'),                      # el broche de la capa
        ((x0 + 7.5 + 6 * s, -5.5, 13.2, 5, 5, 1), 'nucleo'),
    ]
    lamas = []
    for k in range(3):
        lamas.append(nodo(f'lama{k}_{nombre}', (6 * s, 2 + 4.6 * k, 0), (0, 0, (9 + 7 * k) * s), [
            ((-9.5, 0, -12.4 + k, 20, 5, 24.8 - 2 * k), 'placa' if k % 2 == 0 else 'placa_osc'),
            ((-9.8, 4.2, -12.7 + k, 20.6, 1.0, 25.4 - 2 * k), 'oro')]))
    disco = 1.7 if s > 0 else -2.7
    guarda = nodo('guarda_' + nombre, (13 * s, -7, 0), (0, 0, 40 * s), [
        ((-1.7, -9, -11.5, 3.4, 11, 23), 'placa'),                          # la aleta: se afina hacia arriba
        ((-1.5, -13, -8.5, 3.0, 4, 17), 'placa'),
        ((-1.3, -16, -5, 2.6, 3, 10), 'placa_osc'),
        ((-1.9, -9.6, -11.8, 3.8, 1.0, 23.6), 'oro'),
        ((-1.7, -13.6, -8.8, 3.4, 1.0, 17.6), 'oro'),
        ((-1.5, -16.6, -5.3, 3.0, 1.0, 10.6), 'oro'),
        ((disco, -7, -4.5, 1.0, 8, 8), 'oro'),
        ((disco + (0.5 if s > 0 else -0.5), -5.5, -3, 1.0, 5, 5), 'nucleo'),
    ])
    llamas = [llama_nodo(f'llama_h{k}_{nombre}', ((2 + 4.5 * k) * s, -13, -6 + 6 * k), (-12 + 12 * k, 0, 14 * s), alto, 3.8)
              for k, alto in enumerate((8, 11, 7))]
    brazo = nodo('brazo_' + nombre, (0, 4, 0), (0, 0, 0), [
        ((-5.5, 0, -5.5, 11, 22, 11), 'cota'),
        ((-6, 6, -6, 12, 11, 12), 'placa'),
        ((-6.3, 16.4, -6.3, 12.6, 1.2, 12.6), 'oro'),
    ], [
        nodo('antebrazo_' + nombre, (0, 22, 0), (0, 0, 0), [
            ((-6, -3, -6.5, 12, 7, 13), 'placa'),                          # codera
            ((-6.3, 3.4, -6.8, 12.6, 1.0, 13.6), 'oro'),
            ((-6, 4, -6, 12, 9, 12), 'placa'),
            ((-7.6, 12, -7.6, 15.2, 8, 15.2), 'placa'),                     # el vuelo del guantelete
            ((-7.9, 19.2, -7.9, 15.8, 1.2, 15.8), 'oro'),
            ((-7.9, 12, -7.9, 15.8, 1.0, 15.8), 'oro'),
            ((7.6 * s - (0 if s > 0 else 1.0), 14, -2.5, 1.0, 5, 5), 'nucleo'),
        ], [
            nodo('pua_codo_' + nombre, (0, 0, 6.5), (-70, 0, 0), [((-1.5, -6, -1.5, 3, 6, 3), 'oro')]),
            nodo('mano_' + nombre, (0, 21, 0), (0, 0, 0), [
                ((-5.6, 0, -5.6, 11.2, 8.5, 11.2), 'placa_osc'),
                ((-5.9, 0.8, -6.4, 11.8, 2.4, 2.4), 'oro'),                 # nudillos
                *[((x, 0.4, -8.0, 1.8, 1.8, 1.8), 'oro') for x in (-4.4, -0.9, 2.6)],
                ((-5.2, 8.5, -4.4, 10.4, 3.8, 8.8), 'placa_osc'),            # dedos
            ], mano_hijos),
        ]),
    ])
    return nodo('hombro_' + nombre, (HOMBRO_X_N * s, -42, 0), (0, 0, 0), hombrera, lamas + [guarda] + llamas + [brazo])


def _pierna_n(s, nombre):
    return nodo('pierna_' + nombre, (8.5 * s, 2, 0), (0, 0, 0), [
        ((-6.5, 0, -6.5, 13, 30, 13), 'cota'),
        ((-7.5, 1, -8, 15, 11, 9), 'placa'),                               # quijote, por capas
        ((-7.8, 11, -8.4, 15.6, 10, 9.4), 'placa_osc'),
        ((-7.8, 0.4, -8.3, 15.6, 1.2, 9.6), 'oro'),
        ((-8.1, 20.4, -8.7, 16.2, 1.2, 10), 'oro'),
        ((6.5 * s - 0.8, 2, -6, 1.6, 18, 12), 'placa_osc'),
    ], [
        nodo('espinilla_' + nombre, (0, 30, 0), (0, 0, 0), [
            ((-7, -5, -10, 14, 9, 5.5), 'placa'),                           # rodillera
            ((-7.3, -5.4, -10.3, 14.6, 1.0, 6), 'oro'),
            ((-3, -3, -10.8, 6, 6, 1), 'oro'), ((-1.5, -1.5, -11.4, 3, 3, 0.8), 'nucleo'),
            ((-6.5, 0, -7, 13, 15, 14), 'placa'),                           # greba: ancha en la pantorrilla
            ((-6, 15, -6.6, 12, 6, 13.2), 'placa'),
            ((-7.2, 21, -7.6, 14.4, 5, 15.2), 'placa_osc'),                 # y se abre en el tobillo
            ((-7.5, 25.2, -7.9, 15, 1, 15.8), 'oro'),
            ((-1, 3, -7.6, 2, 16, 1), 'oro'),
        ], [
            nodo('aleta_rodilla_' + nombre, (6.6 * s, -1, -6), (0, 0, 22 * s), [
                ((-0.8, -7, -3, 1.6, 10, 9), 'placa'), ((-1.0, -7.8, -3.2, 2.0, 1.0, 9.4), 'oro')]),
            nodo('pie_' + nombre, (0, 34, 0), (0, 0, 0), [
                ((-7, -8, -9, 14, 8, 16), 'placa_osc'),
                ((-6.4, -5, -13, 12.8, 5, 4.4), 'placa'),
                ((-5.4, -3.6, -16, 10.8, 3.6, 3.4), 'placa_osc'),
                ((-7.3, -8.4, -9.3, 14.6, 1.2, 16.6), 'oro'),
                ((-1, -4, 6.5, 2, 2, 4), 'oro'),                             # espuela
            ]),
        ]),
    ])


def _cabeza_n():
    """El yelmo de siempre, con los cuernos de la A, la corona y el halo de la B."""
    cajas = [
        ((-9.5, -20, -9.5, 19, 20, 19), 'placa'),
        ((-10, -15, -10.3, 20, 2.8, 2.6), 'oro'),                 # ceja
        ((-7, -11.8, -10.25, 14, 2.4, 0.8), 'visor'),             # la T
        ((-1.2, -11.8, -10.3, 2.4, 9.2, 0.9), 'visor'),
        ((-10.4, -11.5, -9.6, 3.4, 11.5, 8), 'placa_osc'),        # carrilleras, con su filo de oro
        ((7, -11.5, -9.6, 3.4, 11.5, 8), 'placa_osc'),
        ((-10.6, -11.5, -10, 1.0, 11.5, 1.0), 'oro'), ((9.6, -11.5, -10, 1.0, 11.5, 1.0), 'oro'),
        ((-7.6, -3, -10.8, 15.2, 3.6, 3.4), 'placa_osc'),         # barbote
        ((-1.5, -19.4, -10.1, 3, 3, 0.8), 'nucleo'),              # el sol de la frente
        ((-10.2, -10, -2, 1, 6, 6), 'oro'), ((9.2, -10, -2, 1, 6, 6), 'oro'),
        ((-1.3, -23.5, -9, 2.6, 4.8, 19), 'oro'),                 # cresta
        ((-10.2, -22, -10.2, 20.4, 2.8, 20.4), 'oro'),            # aro de la corona
    ]
    for k in range(7):                                             # corona de puas de oro
        x = -7.8 + k * 2.6
        alto = (5, 7, 9, 12, 9, 7, 5)[k]
        cajas.append(((x - 1.0, -22 - alto, -10.4, 2.0, alto, 2.0), 'oro'))
    cajas.append(((-1.5, -31, -10.9, 3.0, 3.0, 1.2), 'nucleo'))
    hijos = []
    for s, n in ((1, 'izq'), (-1, 'der')):
        hijos.append(nodo('cuerno_' + n, (9 * s, -14, 1), (8, 0, 78 * s), [((-3, -8, -3, 6, 8, 6), 'obsidiana')], [
            nodo('cuerno2_' + n, (0, -8, 0), (18, 0, -38 * s), [((-2.4, -8, -2.4, 4.8, 8, 4.8), 'obsidiana')], [
                nodo('cuerno3_' + n, (0, -8, 0), (20, 0, -34 * s), [((-1.7, -7, -1.7, 3.4, 7, 3.4), 'obsidiana')], [
                    nodo('cuerno4_' + n, (0, -7, 0), (16, 0, -18 * s), [((-1, -6, -1, 2, 6, 2), 'oro')])])])]))
    halo = []
    n = 24
    R = 25.0
    for k in range(n):
        halo.append(nodo(f'halo_aro_{k}', (0, 0, 0), (0, 0, k * 360 / n), [((-3.6, -R - 1.6, -1, 7.2, 3.2, 2), 'oro'),
                                                                           ((-3.4, -R + 1.6, -0.6, 6.8, 1.2, 1.2), 'nucleo')]))
    for k in range(12):
        largo = 16 if k % 2 == 0 else 9
        halo.append(nodo(f'halo_rayo_{k}', (0, 0, 0), (0, 0, k * 30 + 15), [], [
            llama_nodo(f'halo_rayo_{k}_l', (0, -R - 1.4, 0), (0, 0, 0), largo, 3.6)]))
        halo.append(nodo(f'halo_pua_{k}', (0, 0, 0), (0, 0, k * 30), [((-0.9, -R - 6, -0.6, 1.8, 4.6, 1.2), 'oro')]))
    hijos.append(nodo('halo', (0, -16, 13.5), (0, 0, 0), [((-4, -4, -0.5, 8, 8, 1), 'nucleo')], halo))
    return nodo('cabeza', (0, -4, 0), (0, 0, 0), cajas, hijos)


def _capa_n():
    flecos = [((-28 + 2 + 5.6 * i, 26, 0, 3.8, 4 + (i * 7) % 8, 1.5), 'capa_arde') for i in range(10)]
    borde = lambda ancho, alto: [((-ancho / 2 - 0.6, 0, -0.3, 1.2, alto, 2.1), 'oro'), ((ancho / 2 - 0.6, 0, -0.3, 1.2, alto, 2.1), 'oro')]
    return nodo('capa_1', (0, -44, 11), (7, 0, 0), [
        ((-26, -2, -1, 52, 4, 3), 'capa'),
        ((-24, 0, 0, 48, 32, 1.5), 'capa'), *borde(48, 32),
        ((-7, 8, 1.5, 14, 14, 0.8), 'oro'), ((-4.5, 10.5, 2.0, 9, 9, 0.8), 'nucleo'),     # el sol bordado
        *[((-0.8 + math.cos(math.radians(a)) * 10, 14.2 + math.sin(math.radians(a)) * 10, 1.6, 1.6, 1.6, 0.6), 'oro')
          for a in range(0, 360, 45)],
    ], [
        nodo('capa_2', (0, 32, 0), (4, 0, 0), [((-26, 0, 0, 52, 32, 1.5), 'capa'), *borde(52, 32)], [
            nodo('capa_3', (0, 32, 0), (5, 0, 0), [((-28, 0, 0, 56, 16, 1.5), 'capa'),
                                                   ((-28, 16, 0, 56, 12, 1.5), 'capa_arde'), *borde(56, 16), *flecos]),
        ]),
    ])


def esqueleto_n(con_espada=True):
    pecho = [
        ((-14, -14, -9.5, 28, 14, 19), 'cota'),
        *[((-15 + 0.6 * i, -4 - 4 * i, -10.6, 30 - 1.2 * i, 4, 21.2), 'placa' if i % 2 == 0 else 'placa_osc') for i in range(3)],
        *[((-15.3 + 0.6 * i, -4.6 - 4 * i, -10.9, 30.6 - 1.2 * i, 0.8, 21.8), 'oro') for i in range(3)],
        ((-21, -46, -12, 42, 12, 18), 'placa'),                    # el peto en V: ancho arriba
        ((-19.5, -34, -12.6, 39, 10, 18), 'placa'),
        ((-16.5, -24, -12, 33, 10, 16.5), 'placa_osc'),            # y estrecho abajo
        ((-19, -34.4, -12.9, 38, 0.8, 0.6), 'lava'),               # costuras de lava entre las placas
        ((-16, -24.4, -12.3, 32, 0.8, 0.6), 'lava'),
        ((-19, -44, -13.6, 17, 13, 2), 'grabado'), ((2, -44, -13.6, 17, 13, 2), 'grabado'),     # pectorales
        ((-19.4, -31.4, -14, 17.8, 1.4, 2.4), 'oro'), ((1.6, -31.4, -14, 17.8, 1.4, 2.4), 'oro'),
        ((-21.4, -46.6, -12.4, 42.8, 1.4, 18.8), 'oro'),
        ((-1.5, -44, -14.4, 3, 30, 2), 'oro'),                     # la quilla
        ((-8, -42, -15.4, 16, 2, 1.6), 'oro'), ((-8, -28, -15.4, 16, 2, 1.6), 'oro'),          # el aro del sol
        ((-8, -40, -15.4, 2, 12, 1.6), 'oro'), ((6, -40, -15.4, 2, 12, 1.6), 'oro'),
        ((-6, -40, -15.8, 12, 12, 1.6), 'nucleo'),                 # el nucleo solar
        ((-20, -46, 5, 40, 32, 7), 'placa'),                       # espaldar
        ((-1.5, -46, 11.8, 3, 32, 1.5), 'oro'),
        ((-11, -51, -10, 22, 6, 19), 'placa'),                     # gola alta
        ((-11.5, -51.8, -10.5, 23, 1.4, 20), 'oro'),
    ]
    alas_gola = [nodo('gola_' + n, (11 * s, -50, -2), (0, 0, 16 * s), [
        ((-1.5, -10, -7, 3, 10, 14), 'placa'), ((-1.8, -10.8, -7.3, 3.6, 1.2, 14.6), 'oro')]) for s, n in ((1, 'izq'), (-1, 'der'))]
    faldas = [nodo('falda_' + n, (9.5 * s, 1, -10.4), (-6, 0, 10 * s), [
        ((-7, 0, 0, 14, 7, 2.4), 'placa'), ((-7.5, 6, -0.4, 15, 7, 2.6), 'placa_osc'), ((-8, 12, -0.8, 16, 6, 2.8), 'placa'),
        ((-7.3, 6.0, -0.7, 14.6, 0.8, 0.6), 'oro'), ((-7.8, 12.0, -1.1, 15.6, 0.8, 0.6), 'oro'),
        ((-8.3, 17.6, -1.0, 16.6, 1.2, 3.0), 'oro')]) for s, n in ((1, 'izq'), (-1, 'der'))]
    faldas += [nodo('falda_l' + n, (16 * s, 1, 0), (0, 0, 12 * s), [
        ((-1.2, 0, -10, 2.4, 16, 20), 'placa'), ((-1.5, 15.4, -10.3, 3.0, 1.2, 20.6), 'oro')]) for s, n in ((1, 'izq'), (-1, 'der'))]
    tabardo = nodo('tabardo', (0, 1, -11.4), (-4, 0, 0), [
        ((-6, 0, 0, 12, 40, 1.2), 'capa'), ((-6, 40, 0, 12, 10, 1.2), 'capa_arde'),
        ((-6.4, 0, -0.3, 0.8, 48, 1.6), 'oro'), ((5.6, 0, -0.3, 0.8, 48, 1.6), 'oro'),
        ((-2.5, 6, -0.6, 5, 5, 0.8), 'oro'), ((-1.5, 7, -0.9, 3, 3, 0.6), 'nucleo')])
    mano_der = [nodo('agarre', (0, 5, 0), (-90, 0, 0), [], [espada('N')] if con_espada else [])]
    return nodo('raiz', (0, 0, 0), (0, 0, 0), [], [
        nodo('pelvis', (0, -42, 0), (0, 0, 0), [
            ((-15, -6, -10, 30, 8, 20), 'placa_osc'),
            ((-16, -2.5, -11, 32, 3.5, 22), 'cuero'),              # cinturon
            *[((x - 1, -2, -11.6, 2, 2, 0.8), 'oro') for x in (-12, -7, 7, 12)],
            ((-4.5, -5, -12.2, 9, 9, 1.6), 'oro'),                 # la hebilla: un sol
            ((-2.5, -3, -13, 5, 5, 1), 'nucleo'),
        ], faldas + [tabardo,
            _pierna_n(1, 'izq'), _pierna_n(-1, 'der'),
            nodo('torso', (0, -6, 0), (0, 0, 0), pecho, alas_gola + [
                _rayos_relieve('rayos_pecho', (0, -34, 0), 8.2, -15.6),
                _capa_n(),
                nodo('cuello', (0, -50, -1), (0, 0, 0), [((-5, -4, -5, 10, 4, 10), 'cota')], [_cabeza_n()]),
                _brazo_n(1, 'izq', [nodo('sol_mano', (0, 4, -2), (0, 0, 0), [])]),
                _brazo_n(-1, 'der', mano_der),
            ]),
        ]),
    ])


# ----------------------------------------------------------------------
#  Matrices de cada pieza (para poner cosas en las manos, apuntar la espada...)
# ----------------------------------------------------------------------
def matrices(raiz, pose):
    out = {}

    def visitar(n, M):
        nombre, off, rot, cajas, hijos = n
        ex = pose.get(nombre, {})
        r = [rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
        p = [off[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
        Mn = M @ vr.T(*p) @ vr.Rz(r[2] * vr.D2R) @ vr.Ry(r[1] * vr.D2R) @ vr.Rx(r[0] * vr.D2R) @ vr.S(ex.get('esc', 1.0))
        out[nombre] = Mn
        for h in hijos:
            visitar(h, Mn)

    visitar(raiz, np.eye(4))
    return out


VARIANTE_IK = 'N'      # el esqueleto sobre el que se buscan las poses
_ESQ_IK = {}


def mano(pose, lado, local=(0, 6, 0)):
    """Donde cae el puno (en px de modelo) con esta pose."""
    if VARIANTE_IK not in _ESQ_IK:
        _ESQ_IK[VARIANTE_IK] = esqueleto(VARIANTE_IK, con_espada=False)
    return (matrices(_ESQ_IK[VARIANTE_IK], pose)['mano_' + lado] @ np.array([*local, 1.0]))[:3]


def codo_hacia(pose, lado):
    """Hacia donde sale el codo (unitario), apartado de la recta del hombro al puno."""
    if VARIANTE_IK not in _ESQ_IK:
        _ESQ_IK[VARIANTE_IK] = esqueleto(VARIANTE_IK, con_espada=False)
    M = matrices(_ESQ_IK[VARIANTE_IK], pose)
    hombro = M['brazo_' + lado][:3, 3]
    codo = M['antebrazo_' + lado][:3, 3]
    eje = mano(pose, lado) - hombro
    eje = eje / max(1e-6, np.linalg.norm(eje))
    e = codo - hombro
    e = e - (e @ eje) * eje
    n = np.linalg.norm(e)
    return e / n if n > 1e-6 else np.zeros(3)


def alcanzar(pose, lado, objetivo, semilla=(-40, 0, 0, -30), codo=None):
    """Busca el giro del brazo (x, y, z) y del antebrazo (x) que lleva el puno
    a 'objetivo' (px de modelo). Devuelve la pose con los dos huesos puestos y
    el error que queda (px). Con 'codo' (una direccion), de las soluciones que
    llegan prefiere la que saca el codo hacia alli: si no, con el puno cerca del
    hombro sale cualquiera (el codo en alto, el brazo retorcido)."""
    from scipy.optimize import minimize
    obj = np.array(objetivo, float)
    base = {k: dict(v) for k, v in pose.items()}
    hacia = None if codo is None else np.array(codo, float) / np.linalg.norm(codo)

    def con(xs):
        p = {k: dict(v) for k, v in base.items()}
        p['brazo_' + lado] = {**p.get('brazo_' + lado, {}), 'rot': (xs[0], xs[1], xs[2])}
        p['antebrazo_' + lado] = {**p.get('antebrazo_' + lado, {}), 'rot': (xs[3], 0, 0)}
        return p

    def coste(xs):
        p = con(xs)
        d = mano(p, lado) - obj
        doblez = max(0.0, xs[3]) ** 2 * 0.05        # el codo no se dobla al reves
        c = float(d @ d) + doblez + 0.0005 * (xs[1] ** 2)
        if hacia is not None:
            c += 12.0 * (1.0 - float(codo_hacia(p, lado) @ hacia))
        return c

    mejor = None
    for s0 in (semilla, (-90, 0, 0, -20), (-150, 0, 0, -10), (-20, 0, 30, -40), (-20, 0, -30, -40)):
        r = minimize(coste, np.array(s0, float), method='Nelder-Mead', options={'maxiter': 2500, 'xatol': 0.05, 'fatol': 0.01})
        if mejor is None or r.fun < mejor.fun:
            mejor = r
    return con(mejor.x), float(np.sqrt(max(0.0, mejor.fun)))


def apuntar_espada(pose, direccion, giro_filo=0.0):
    """Busca el giro del agarre que pone la hoja (hacia la punta) en 'direccion'
    (px de modelo; -Y es arriba, -Z delante)."""
    from scipy.optimize import minimize
    d = np.array(direccion, float)
    d /= np.linalg.norm(d)
    esq = esqueleto(VARIANTE_IK)

    def con(xs):
        p = {k: dict(v) for k, v in pose.items()}
        p['agarre'] = {'rot': (xs[0], xs[1], giro_filo + xs[2])}
        return p

    def coste(xs):
        R = matrices(esq, con(xs))['espada'][:3, :3]
        b = R @ np.array([0, 1.0, 0])
        return float(((b / np.linalg.norm(b) - d) ** 2).sum()) + 1e-6 * float((xs ** 2).sum())

    mejor = None
    for s0 in ((0, 0, 0), (90, 0, 0), (-90, 0, 0), (0, 90, 0), (0, 0, 90), (180, 0, 0)):
        r = minimize(coste, np.array(s0, float), method='Nelder-Mead', options={'maxiter': 3000, 'xatol': 0.02, 'fatol': 1e-7})
        if mejor is None or r.fun < mejor.fun:
            mejor = r
    return con(mejor.x)


# ----------------------------------------------------------------------
#  Poses
# ----------------------------------------------------------------------
def _p(**k):
    return {a: dict(b) for a, b in k.items()}


HEROICA = _p(
    torso={'rot': (-4, 14, 0)},
    cabeza={'rot': (6, -16, 0)},
    brazo_der={'rot': (-150, 10, -20)}, antebrazo_der={'rot': (-28, 0, 0)},
    agarre={'rot': (10, 0, 22)},
    brazo_izq={'rot': (-52, 0, 48)}, antebrazo_izq={'rot': (-48, 0, 0)},
    pierna_izq={'rot': (-18, 0, -6)}, espinilla_izq={'rot': (20, 0, 0)}, pie_izq={'rot': (-2, 0, 0)},
    pierna_der={'rot': (16, 0, 8)}, espinilla_der={'rot': (10, 0, 0)}, pie_der={'rot': (-24, 0, 0)},
    capa_1={'rot': (22, 0, 0)}, capa_2={'rot': (10, 0, 0)}, capa_3={'rot': (12, 0, 0)},
)


def quads(variante, pose, M, con_espada=True):
    return nm.quads(esqueleto(variante, con_espada), pose, M)


def quads_espada(variante, M, nombre='espada'):
    return nm.quads(espada(variante, nombre), {}, M)


def dibujar(lz, cam, qs, luces, amb, niebla=None, brillo=1.4, fase=1):
    tex, emi, plenos = materiales(fase)
    for P, UV, mat in qs:
        t = tex[mat]
        if mat in plenos:
            luz, e = np.ones(3), t
        else:
            luz = vr.iluminar(vr.normal(P), cam, np.mean(P, axis=0), luces, amb)
            e = emi.get(mat)
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [P[i] for i in tri], [UV[i] for i in tri], t, luz, e, niebla, brillo=brillo,
                         envolver=mat not in ESTIRA)


ESCALA = 1.3         # en el juego: unos 11,5 bloques hasta el yelmo (13 con los cuernos y el halo)


def entidad_a_mundo(x, y, z, guinada, escala=ESCALA):
    return vr.entidad_a_mundo(x, y, z, guinada, escala)


def modelo_a_mundo(M_entidad, p):
    """Un punto en px de modelo -> mundo."""
    return (M_entidad @ np.array([*p, 1.0]))[:3]

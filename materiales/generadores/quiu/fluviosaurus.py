"""El Fluviosaurus (DEDsafío 4, cuevas altas y ríos del Centro de Quiu): un anfibio largo, bajo y plano que repta por
las cuevas rompiendo la piedra y trepa por las paredes. Copia fiel de lo que se ve en el directo de Soarinng del 07-10
(0:38:45, la principal, leída téxel a téxel en el fotograma crudo, y el clip 0:17-0:27) y del icono del libro:

  la cabeza     una punta de flecha plana de 4 de alto: dos brazos de 5 de ancho echados hacia atrás a 36° que se
                juntan en la punta del hocico (16 de ancho y 10,5 de fondo); violeta, con el ▼ púrpura en la punta, una
                banda azul violeta por dentro que con la del otro brazo hace una V y, entre los brazos, la V baja azul
                oscuro del cuello; cada brazo acaba atrás en dos púas de 1 x 1 con la punta magenta; la boca, una raya
                índigo a lo largo del canto de fuera, a 1 del suelo, hasta debajo del ojo (la mandíbula, la tira de
                abajo, que se abre al morder)
  los ojos      dos bloques de 3 x 2 x 3 a la mitad del borde de fuera de cada brazo, asomando 1 por fuera: la cara de
                delante amarillo verdoso con la pupila negra vertical, la de fuera amarilla y la tapa con una raya
                magenta
  el cuerpo     cinco tramos rectos y planos de 6 x 4 x 5, cada uno con su chevron magenta que apunta a la cabeza (el
                primero, flanqueado por los brazos de la cabeza, con la V oscura del cuello); los costados azul violeta
                con una mancha magenta alta por tramo y la junta índigo entre tramo y tramo
  las ramas     un par en cada una de las 4 juntas (branquias que hacen de patas): cintas planas y horizontales de 7,
                con dos cruces «+» magenta (a 3 y a 6 del cuerpo) y la punta magenta
  la cola       un trozo corto y un abanico de cinco varillas paralelas hacia atrás: las dos de dentro, las más largas;
                la del medio, azul oscuro; las de fuera, cortas y saliendo de un codo

Semiacuático: al andar (en tierra o en el agua) el cuerpo ondula en S, más hacia la cola, y las ramas reman en una
onda de delante atrás; al trepar (estado1) se pone de pie contra la pared, con las ramas pegadas a ella.
"""
import math

import numpy as np

import bestiario as B

ID = 'fluviosaurus'
TAM = 1.0      # el téxel del mob mide lo mismo que el de la piedra de al lado (ficha): 16 por bloque, sin agrandar

# El huevo: la piel violeta (claro, medio, oscuro), el contorno magenta y azul violeta, y sus señas: los dos ojos
# amarillos con la pupila, la punta de flecha y un chevron magenta.
HUEVO = (('9346a8', '6b3e98', '332970'), ('cc4ecc', '413e8b'),
         [((5, 6), '929f31'), ((6, 6), '1c1420'), ((9, 6), '1c1420'), ((10, 6), '929f31'),
          ((7, 4), 'cc4ecc'), ((8, 4), 'cc4ecc'), ((6, 3), 'cc4ecc'), ((9, 3), 'cc4ecc'),
          ((7, 10), 'cc4ecc'), ((8, 10), 'cc4ecc'), ((6, 9), 'cc4ecc'), ((9, 9), 'cc4ecc'),
          ((7, 11), '9346a8'), ((8, 11), '9346a8')])

# ======================================================================================================================
#  Los colores (paleta.json de la ficha: las caras más iluminadas del clip)
# ======================================================================================================================
COLORES_FLUVIOSAURUS = {
    'V': '6b3e98',   # violeta: la piel de fondo
    'P': '9346a8',   # púrpura: la fila ancha de los chevrones, el hocico
    'M': 'cc4ecc',   # magenta: chevrones, cuadros de los brazos, cruces, varillas
    'L': 'de5ee3',   # magenta claro (el brillo)
    'A': '413e8b',   # azul violeta: costados, bordes del lomo, tallos, banda de la cabeza
    'O': '332970',   # azul oscuro: la V interior de la cabeza, cuadros oscuros del lomo
    'I': '2c1e40',   # índigo: juntas, boca, sombras
    'Y': '929f31',   # ojo, amarillo verdoso
    'y': '798c21',   # ojo, el tono de sombra
    'K': '1c1420',   # pupila
    'R': '5a2a5a',   # el interior de la boca (solo se ve al morder)
}
RGB_FLUVIOSAURUS = {k: B.H(v) for k, v in COLORES_FLUVIOSAURUS.items()}

# Las medidas, en píxeles de Minecraft (16 por bloque). El boceto: +Z delante, Y arriba, el suelo en y = 0; se dibuja
# con la punta del hocico en z = 0 y luego se corre todo DZ para que el mob quede centrado.
MEDIDAS_FLUVIOSAURUS = dict(
    alto_cabeza=4.0,      # de la cabeza (con la mandíbula), como el cuerpo: medido en la ficha y en el icono del libro
    alto_mandibula=1.0,
    brazo_angulo=36.0,    # grados de cada brazo respecto al eje
    brazo_tiras=5,        # el ancho del brazo (en téxeles; delante va en tiras de 1: ver piezas_brazo_fluviosaurus)
    brazo_largo=12.0,     # el borde de fuera, de la punta al final de la caja del brazo
    puas=(0.5, 2.5),      # el extremo de atrás acaba en dos púas de 1 x 1 (q de su centro), de t = 12 a 13
    banda=(3.0, 4.0),     # la banda azul violeta de cada brazo (distancia desde el borde de fuera)
    brazo_t0=2.0,         # donde acaba la caja entera de cada brazo, a lo largo del borde, desde la punta
    ojo=(3, 2, 3),        # ancho, alto y fondo del ojo (de frente 3 x 2: 0:25.52 y 0:27.37; desde arriba 3 x 3)
    ojo_t=7.5,            # el centro del ojo, a lo largo del borde de fuera desde la punta (principal: t = 6 a 9)
    ojo_dentro=-1.0,      # lo que entra el ojo desde el borde de fuera (negativo: asoma 1 por fuera, como en la
                          # principal, donde su tapa queda centrada sobre el borde)
    cuello=(-6.0, -9.6, 2.0),   # la pieza baja de la V: de z a z, alto
    tramo1=-9.1,          # el frente del primer tramo
    # cinco tramos de 5 filas (el chevron se repite cada 5 filas: 0:38:45 y 0:18.47); las ramas, en las 4 juntas
    tramos=((6, 4, 5),) * 5,   # ancho, alto, largo
    cola=(5, 3, 4),
    ramas=(7, 7, 7, 7),
    rama_y=3.0,
    rama_atras=0.5,       # la rama, a tanto del final de su tramo (en la junta con el siguiente)
    trepar=dict(sube=33.0, atras=-6.45, ramas=25.0),   # estado1: lo que sube y retrocede el cuerpo de pie y lo que se
                                                       # doblan las ramas hacia la pared
    # el abanico (0:18.47 y 0:24.98): cinco varillas paralelas hacia atrás; las de fuera salen de un codo hacia el lado
    # (en L) y la del medio es azul oscuro; las de en medio, las más largas. (x, largo, color)
    varillas=((0, 3, 'O'), (-2, 4, 'M'), (2, 4, 'M'), (-4, 2, 'M'), (4, 2, 'M')),
    varilla_y=1.5,
)


# ======================================================================================================================
#  Los pintores: cada cara, un mapa de letras (un téxel cada una), limpio, sin ruido
# ======================================================================================================================
def _a_tam_fluviosaurus(filas, th, tw):
    """Las filas del mapa a th x tw: recorta o repite el mapa (en mosaico) si la cara no mide lo mismo."""
    a = np.array([list(f) for f in filas])
    if a.shape[0] < th:
        a = np.concatenate([a] * (th // a.shape[0] + 1), 0)
    if a.shape[1] < tw:
        a = np.concatenate([a] * (tw // a.shape[1] + 1), 1)
    return a[:th, :tw]


def mapa_fluviosaurus(nombre, mapas, fondo='V'):
    """Un pintor de mapas de letras por cara ({cara: filas o fn(tw, th) -> filas}; '*' para las demás). Las caras de
    lado se escriben de atrás (columna 0) hacia delante, como se ve el mob de lado con la cabeza a la derecha; la de
    arriba, de atrás (fila 0) hacia delante, con la columna 0 a la derecha del mob (-X); '.' deja la cara vacía."""
    def fn(tw, th, cara, s):
        mp = mapas.get(cara, mapas.get('*'))
        if mp is None:
            a = np.full((th, tw), fondo)
        else:
            if callable(mp):
                mp = mp(tw, th)
            a = _a_tam_fluviosaurus(mp, th, tw)
        if cara == 'der':
            a = a[:, ::-1]
        tex = np.zeros((th, tw, 4), np.uint8)
        for letra, rgb in RGB_FLUVIOSAURUS.items():
            tex[a == letra, :3] = rgb
        tex[..., 3] = np.where(a == '.', 0, 255)
        return tex, None
    return B.Pintor(nombre, fn)


# El lomo de un tramo (de atrás hacia delante): el chevron ▼ que apunta a la cabeza (contado en el fotograma 0:38:45).
LOMO_FLUVIOSAURUS = ['PVVVVP',
                     'OMPPMO',
                     'AOMMOA',
                     'AVOOVA',
                     'AAVVAA']

def costado_fluviosaurus(junta=True):
    """El costado de un tramo (de atrás hacia delante): azul violeta con una mancha magenta de 2 de ancho que baja del
    canto de arriba casi hasta abajo, y la junta índigo detrás (0:17.92 de lado; el icono del libro)."""
    def fn(tw, th):
        filas = []
        for j in range(th):
            f = ''
            for i in range(tw):
                if junta and i == 0:
                    c = 'I'
                elif 2 <= i <= 3 and j <= th - 2:
                    c = 'M'                    # la mancha magenta, del canto de arriba casi hasta abajo (0:17.92)
                elif j == th - 1:
                    c = 'O'
                elif j == 0:
                    c = 'V'
                else:
                    c = 'A'
                f += c
            filas.append(f)
        return filas
    return fn


def rama_fluviosaurus(largo):
    """La cinta de una rama (3 de ancho; la fila 0, la punta): el tallo en medio, azul violeta junto al cuerpo y violeta
    hacia fuera, dos cruces magenta (a 3 y a 6 del cuerpo) y la punta magenta."""
    filas = []
    for k in range(largo):
        d = largo - k                 # la distancia al cuerpo (1, junto al cuerpo)
        tallo = 'A' if d <= 2 else 'V'
        if d == largo:
            filas.append('.M.')
        elif d in (3, min(6, largo - 1)):
            filas.append('M' + tallo + 'M')
        else:
            filas.append('.' + tallo + '.')
    return filas


# ======================================================================================================================
#  La cabeza
# ======================================================================================================================
def ejes_brazo_fluviosaurus(lado, P):
    """Los ejes de un brazo en el plano (x, z), con la punta del hocico en el origen: u, hacia atrás a lo largo del brazo;
    n_in, hacia dentro (hacia el eje del mob). Lado -1: el brazo de x < 0; +1: el de x > 0."""
    th = math.radians(P['brazo_angulo'])
    s, c = math.sin(th), math.cos(th)
    return np.array((lado * s, -c)), np.array((-lado * c, -s))


def diseno_cabeza_fluviosaurus(x, z, P):
    """El dibujo de arriba de la punta de flecha en un punto (x, z) del plano (la punta en el origen), leído en la
    principal en la rejilla de cada brazo (scripts/rejilla_brazo.py): violeta, con la banda azul violeta por dentro que
    con la del otro brazo hace una V; junto a la punta, el ▼ púrpura; atrás, entre las bases de las dos púas, una raya
    azul violeta y púrpura en las bases. Se pinta en el mundo para que donde un brazo tapa al otro se vea lo mismo que si
    se vieran los dos."""
    w, L = P['brazo_tiras'], P['brazo_largo']
    p = np.array((x, z))
    letras = []
    for lado in (-1, 1):
        u, n_in = ejes_brazo_fluviosaurus(lado, P)
        t, q = float(p @ u), float(p @ n_in)
        if not (-0.01 <= q <= w + 0.01 and t <= L + 0.01):
            continue
        if t > L - 2 and q < 3:
            # el extremo de atrás: las bases de las dos púas (púrpura en la última fila) y la raya azul entre ellas
            if 1 <= q < 2:
                letras.append('A')
            else:
                letras.append('P' if t > L - 1 else 'V')
        elif t < 1 or (t < 2 and q < 3) or (t < 3 and q < 1):
            letras.append('P')          # el ▼ púrpura de la punta (2 filas)
        elif P['banda'][0] <= q <= P['banda'][1] and t <= 8.0 and lado * x >= -0.01:
            letras.append('A')          # la banda de dentro llega hasta el eje: las dos hacen una V azul
        elif 4.0 <= q <= 5.0 and t >= 10.0:
            letras.append('A')          # detrás del ojo se corta y vuelve, un téxel más adentro, hasta el final
        else:
            letras.append('V')
    for c in ('M', 'P', 'A', 'V'):
        if c in letras:
            return c
    return 'V'


def puas_fluviosaurus(m, lado, ld, P, dz, parte):
    """Las dos púas del extremo de atrás de un brazo (1 x alto x 1, magenta arriba), giradas con el brazo."""
    u, n_in = ejes_brazo_fluviosaurus(lado, P)
    L, hc = P['brazo_largo'], P['alto_cabeza']
    pint = mapa_fluviosaurus('pua_fluviosaurus', {'arriba': ['M'], '*': ['P', 'A', 'A', 'O'], 'abajo': ['O']})
    for q in P['puas']:
        c = (L + 0.5) * u + q * n_in
        m.caja(parte, (c[0], hc / 2 + 0.01, c[1] + dz), (1.0, hc - 0.02, 1.0), pint, rot=(0, -lado * P['brazo_angulo'], 0))


def piezas_brazo_fluviosaurus(lado, P):
    """Las cajas de un brazo: (centro (x, z), ancho en tiras, largo, primera tira). Dos cajas giradas 36° no hacen una
    punta limpia (el frente de cada una asoma por fuera del otro brazo como un pincho), así que cada brazo es una caja
    entera que acaba a 'brazo_t0' de la punta (su frente queda dentro del otro brazo) y, delante, unas tiras de 1 que
    llegan hasta el borde de fuera del otro brazo; lo poco que les falta lo tapa el otro brazo."""
    u, n_in = ejes_brazo_fluviosaurus(lado, P)
    u_otro, _ = ejes_brazo_fluviosaurus(-lado, P)
    L, w, t0 = P['brazo_largo'], P['brazo_tiras'], P['brazo_t0']
    piezas = [((w / 2) * n_in + (t0 + L) / 2 * u, w, L - t0, 0)]
    for k in range(w):
        # la esquina delantera de dentro de la tira, sobre el borde del otro brazo: (k + 1) n_in + t u = r u_otro
        t, r = np.linalg.solve(np.column_stack((u, -u_otro)), -(k + 1) * n_in)
        t = max(0.0, float(t))
        if t >= t0 - 1e-6:
            continue
        largo = math.ceil((t0 + 1.0 - t) * 2) / 2          # que monte 1 sobre la caja entera (y de medio en medio)
        piezas.append(((k + 0.5) * n_in + (t + largo / 2) * u, 1, largo, k))
    return piezas


def brazo_fluviosaurus(m, lado, ld, P, dz, parte_alta, parte_baja):
    """Un brazo de la punta de flecha: lo de arriba (en la cabeza) y lo de la mandíbula, con el dibujo de
    diseno_cabeza_fluviosaurus pintado en sus téxeles."""
    g = -lado * P['brazo_angulo']
    R = B.girar((0, g, 0))[:3, :3]
    ex, ez = R @ np.array((1.0, 0, 0)), R @ np.array((0, 0, 1.0))       # los ejes de la caja en el mundo
    u, n_in = ejes_brazo_fluviosaurus(lado, P)
    hc, hm = P['alto_cabeza'], P['alto_mandibula']
    ha = hc - hm
    fuera = 'izq' if lado < 0 else 'der'          # el lado de fuera es -X en las cajas del de x < 0 y +X en el de x > 0
    dentro = 'der' if lado < 0 else 'izq'
    t_boca = P['ojo_t'] + 2.0                      # la raya de la boca llega hasta debajo del ojo
    for i, (c, ancho, largo, k0) in enumerate(piezas_brazo_fluviosaurus(lado, P)):
        nw, nl = int(ancho), int(math.ceil(largo - 1e-6))
        # arriba: filas de atrás (-Z de la caja) hacia delante; columnas de -X a +X de la caja
        filas = []
        for r in range(nl):
            zl = -largo / 2 + r + 0.5
            f = ''
            for cc in range(nw):
                xl = -ancho / 2 + cc + 0.5
                pw = c + xl * np.array((ex[0], ex[2])) + zl * np.array((ez[0], ez[2]))
                f += diseno_cabeza_fluviosaurus(pw[0], pw[1], P)
            filas.append(f)
        # los lados: columnas de atrás hacia delante; la de fuera lleva la boca (fila de abajo) hasta debajo del ojo
        lado_f = []
        t_atras = float(c @ u) + largo / 2
        for r in range(int(math.ceil(ha))):
            fila = ''
            for j in range(nl):
                t = t_atras - (j + 0.5)
                fila += 'V' if r == 0 else ('I' if (r == int(ha) - 1 and t < t_boca) else 'A')
            lado_f.append(fila)
        caras_alta = {'arriba': filas, 'frente': ['A'], 'atras': ['A'], 'abajo': ['R'], fuera: lado_f,
                      dentro: ['A', 'O', 'O']}
        pa = mapa_fluviosaurus(f'brazo_{ld}{i}_fluviosaurus', caras_alta)
        caras_baja = {'arriba': ['R'], 'abajo': ['O'], 'frente': ['A'], 'atras': ['A'], fuera: ['P'], dentro: ['O']}
        pb = mapa_fluviosaurus(f'mand_{ld}{i}_fluviosaurus', caras_baja)
        if ancho == 1:
            # en las tiras solo se ve el lado de fuera de la primera
            quita = [x for x, si in ((fuera, k0 > 0), (dentro, True)) if si]
        else:
            quita = []
        # alturas: el brazo de x > 0, un pelo más alto que el otro; las tiras, un pelo más que su caja entera
        y_off = 0.03 + 0.02 * (1 + lado) / 2 + (0.01 if ancho == 1 else 0.0)
        m.caja(parte_alta, (c[0], hm + ha / 2 + y_off, c[1] + dz), (ancho, ha, largo),
               {x: (None if x in quita else pa) for x in B.CARAS}, rot=(0, g, 0))
        m.caja(parte_baja, (c[0], hm / 2 + y_off - 0.03, c[1] + dz), (ancho, hm, largo),
               {x: (None if x in quita else pb) for x in B.CARAS}, rot=(0, g, 0))


def ojo_fluviosaurus(m, lado, ld, P, dz, parte):
    """El ojo: un bloque encima del brazo, en su borde de fuera, girado con el brazo (ancho x alto x fondo de 'ojo'). La
    cara de delante, amarillo verdoso con la pupila negra vertical en medio; la de fuera, amarillo verdoso; la de
    arriba, magenta."""
    ow, oh, od = P['ojo']
    u, n_in = ejes_brazo_fluviosaurus(lado, P)
    c = P['ojo_t'] * u + (ow / 2 + P['ojo_dentro']) * n_in
    frente = ['Y' * (ow // 2) + 'K' + 'Y' * (ow // 2)] * (oh - 1) + ['y' * (ow // 2) + 'K' + 'y' * (ow // 2)]
    lado_y = ['Y' * od] * (oh - 1) + ['y' * od]
    # la cara de dentro (hacia el eje), púrpura como se ve junto a cada ojo en la principal (0:38:45)
    fuera, dentro = ('izq', 'der') if lado < 0 else ('der', 'izq')
    tapa = ['P' * (ow // 2) + 'M' + 'P' * (ow // 2)]          # desde arriba, una raya magenta en medio (principal)
    pint = mapa_fluviosaurus(f'ojo_{ld}_fluviosaurus', {'frente': frente, 'arriba': tapa, fuera: lado_y,
                                                       dentro: ['P'], 'atras': ['V'], 'abajo': ['V']})
    # el ojo se hunde un poco en la cabeza (sin hueco por debajo); su tapa queda a alto_cabeza + oh
    y0 = P['alto_cabeza'] - 0.1
    m.caja(parte, (c[0], y0 + (oh + 0.1) / 2, c[1] + dz), (ow, oh + 0.1, od), pint,
           rot=(0, -lado * P['brazo_angulo'], 0))


# ======================================================================================================================
#  Las animaciones
# ======================================================================================================================
def anims_fluviosaurus(m, tramos, P):  # noqa: C901
    """reposo: respira, ondea un poco y las ramas aletean despacio; andar (en tierra o en el agua): la onda en S que va
    de la cabeza a la cola, más fuerte hacia atrás, con la cabeza firme, y las ramas que reman alternas como las patas
    de una salamandra (la del par 1 izquierda con la del par 2 derecha); ataque: echa la cabeza atrás, abre la boca y
    lanza el mordisco; especial: el cabezazo con que rompe la piedra (dos golpes); estado1: agarrado a la pared al
    trepar (el cuerpo recto y las ramas abiertas que se agarran alternas); aparece: sale del suelo desplegando las
    ramas; muerte: se da la vuelta panza arriba y encoge las ramas."""
    cadena = tramos + ['cola', 'abanico']               # de delante hacia atrás
    ramas = [(k + 1, lado, ld) for k in range(len(P['ramas'])) for lado, ld in ((1, 'i'), (-1, 'd'))]

    # ---- reposo
    r = m.anim('reposo', 3.2, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.15, periodo=1.6)
    for i, n in enumerate(cadena[1:]):
        r.onda(n, 'r', 1, 1.5 + 0.8 * i, periodo=3.2, fase=0.1 * i)
    r.onda('cabeza', 'r', 1, -1.5, periodo=3.2)
    for k, lado, ld in ramas:
        r.onda(f'rama{k}_{ld}', 'r', 2, 5 * lado, periodo=1.6, fase=0.12 * k)

    # ---- andar: la onda en S y las ramas que reman
    T = 1.0
    a = m.anim('andar', T, bucle=True)
    amp = [3.0 + 10.0 * i / max(1, len(cadena) - 2) for i in range(len(cadena) - 1)] + [12.0]
    for i, n in enumerate(cadena):
        a.onda(n, 'r', 1, amp[i], periodo=T, fase=-0.13 * i)
    a.onda('cabeza', 'r', 1, -amp[0] * 0.9, periodo=T)            # la cabeza, siempre recta
    a.onda('cuerpo', 'm', 1, 0.25, periodo=T / 2)
    for k, lado, ld in ramas:
        # una onda que recorre las ramas de delante atrás con la del cuerpo (como las patas de un ciempiés) y los dos
        # lados a contrapaso: las vecinas casi van juntas y no se cruzan aunque el cuerpo se doble
        f = 0.5 * (lado > 0) - 0.13 * (k - 1)
        a.onda(f'rama{k}_{ld}', 'r', 1, -18 * lado, periodo=T, fase=f)          # adelante y atrás (sin cruzarse)
        a.onda(f'rama{k}_{ld}', 'r', 2, 9 * lado, periodo=T, fase=f + 0.25,    # se levanta al ir hacia delante
               forma=lambda v: max(0.0, v))

    # ---- ataque: atrás, boca abierta y el mordisco
    at = m.anim('ataque', 0.6)
    at.rot('cabeza', [(0, 0, 0, 0), (0.18, -16, 0, 0), (0.3, 6, 0, 0), (0.45, 2, 0, 0), (0.6, 0, 0, 0)])
    at.mov('cabeza', [(0, 0, 0, 0), (0.18, 0, 0.6, -1.0), (0.3, 0, 0, 3.0), (0.45, 0, 0, 1.0), (0.6, 0, 0, 0)])
    at.rot('mandibula', [(0, 0, 0, 0), (0.18, 22, 0, 0), (0.3, 0, 0, 0), (0.6, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.18, -3, 0, 0), (0.3, 2, 0, 0), (0.6, 0, 0, 0)])
    for k, lado, ld in ramas[:4]:
        at.rot(f'rama{k}_{ld}', [(0, 0, 0, 0), (0.18, 0, 14 * lado, 0), (0.3, 0, -8 * lado, 0), (0.6, 0, 0, 0)])

    # ---- especial: el cabezazo que rompe la piedra
    e = m.anim('especial', 1.0)
    e.rot('cabeza', [(0, 0, 0, 0), (0.2, -24, 0, 0), (0.32, 14, 0, 0), (0.45, -18, 0, 0), (0.6, 14, 0, 0),
                     (1.0, 0, 0, 0)])
    e.rot('cuerpo', [(0, 0, 0, 0), (0.2, -4, 0, 0), (0.32, 3, 0, 0), (0.45, -3, 0, 0), (0.6, 3, 0, 0), (1.0, 0, 0, 0)])
    e.mov('cuerpo', [(0, 0, 0, 0), (0.2, 0, 0, -0.8), (0.32, 0, 0, 0.6), (0.45, 0, 0, -0.5), (0.6, 0, 0, 0.6),
                     (1.0, 0, 0, 0)])

    # ---- estado1: trepando (en bucle mientras la entidad trepa: el cuerpo no gira solo). Como en la principal, el
    # cuerpo se pone de pie, recto contra la pared, con la tripa en ella y la cabeza arriba; las ramas, pegadas a la
    # pared, se agarran en una onda; la cola cuelga y se mece. La tripa queda a 8 px por delante del centro (la pared,
    # con una caja de colisión de un bloque de ancho) y la punta de la cola, en el suelo.
    s1 = m.anim('estado1', 1.2, bucle=True)
    giro = P['trepar']
    s1.rot('cuerpo', [(0, -90, 0, 0), (1.2, -90, 0, 0)])
    s1.mov('cuerpo', [(0, 0, giro['sube'], giro['atras']), (1.2, 0, giro['sube'], giro['atras'])])
    s1.rot('cabeza', [(0, -12, 0, 0), (0.6, -16, 0, 0), (1.2, -12, 0, 0)])
    for i, n in enumerate(cadena[1:]):
        s1.onda(n, 'r', 1, 2.0 + 1.0 * i, periodo=1.2, fase=-0.13 * (i + 1))
    for k, lado, ld in ramas:
        f = 0.5 * (lado > 0) - 0.13 * (k - 1)
        s1.onda(f'rama{k}_{ld}', 'r', 1, -12 * lado, periodo=1.2, fase=f)                 # suben y bajan por la pared
        s1.onda(f'rama{k}_{ld}', 'r', 2, 4 * lado, periodo=1.2, fase=f + 0.25,           # y se despegan al subir
                base=-giro['ramas'] * lado, forma=lambda v: max(0.0, v))

    # ---- aparece: sale del suelo y despliega las ramas
    ap = m.anim('aparece', 1.0)
    ap.mov('cuerpo', [(0, 0, -6, 0), (0.6, 0, 0.5, 0), (0.8, 0, 0, 0), (1.0, 0, 0, 0)])
    ap.rot('cabeza', [(0, 0, 0, 0), (0.5, -18, 0, 0), (0.8, 4, 0, 0), (1.0, 0, 0, 0)])
    for k, lado, ld in ramas:
        ap.rot(f'rama{k}_{ld}', [(0, 0, 70 * lado, 0), (0.5, 0, 50 * lado, 0), (0.9, 0, -5 * lado, 0),
                                 (1.0, 0, 0, 0)])

    # ---- muerte: panza arriba
    mu = m.anim('muerte', 1.2)
    mu.rot('cuerpo', [(0, 0, 0, 0), (0.25, 0, 0, -12), (0.8, 0, 0, 180), (1.2, 0, 0, 180)])
    mu.mov('cuerpo', [(0, 0, 0, 0), (0.4, 0, 3, 0), (0.8, 0, 0, 0), (1.2, 0, 0, 0)])
    mu.rot('cola', [(0, 0, 0, 0), (1.2, 0, 22, 0)])
    mu.rot('abanico', [(0, 0, 0, 0), (1.2, 0, 15, 0)])
    mu.rot('mandibula', [(0, 0, 0, 0), (0.8, 12, 0, 0), (1.2, 10, 0, 0)])
    for k, lado, ld in ramas:
        mu.rot(f'rama{k}_{ld}', [(0, 0, 0, 0), (0.8, 0, 0, 30 * lado), (1.2, 0, 0, 35 * lado)])


# ======================================================================================================================
#  El mob
# ======================================================================================================================
def construir():
    P = MEDIDAS_FLUVIOSAURUS
    m = B.Modelo(ID, K=2, ancho=128)
    m.escala = 1.0
    m.texel = 1.0      # los mapas de letras van a un téxel por letra: 16 por bloque, pase lo que pase con B.TEXEL

    # Dónde empieza y acaba cada pieza (la punta en z = 0) y cuánto se corre todo para centrarlo.
    zs = []
    z = P['tramo1']
    for (w, h, l) in P['tramos']:
        zs.append((z, z - l))
        z -= l
    z_cola = z
    cw, ch, cl = P['cola']
    z_fin = z_cola - cl - max(v[1] for v in P['varillas']) - 1
    dz = -(0.0 + z_fin) / 2

    # ------------------------------------------------------------------ los tramos
    def piel_tramo(nombre, lomo):
        return mapa_fluviosaurus(nombre, {'arriba': lomo, 'izq': costado_fluviosaurus(), 'der': costado_fluviosaurus(),
                                          'frente': ['A'], 'atras': ['I'], 'abajo': ['A']})
    # el primer tramo, con lo de delante oscuro: es la V azul oscuro que asoma entre los brazos de la cabeza
    piel1 = piel_tramo('lomo1_fluviosaurus', LOMO_FLUVIOSAURUS[:3] + ['AOPPOA', 'AOOOOA'])
    piel = piel_tramo('lomo_fluviosaurus', LOMO_FLUVIOSAURUS)
    padre = None
    nombres = []
    for k, ((w, h, l), (z0, z1)) in enumerate(zip(P['tramos'], zs)):
        n = 'cuerpo' if k == 0 else f'tramo{k + 1}'
        m.parte(n, padre, (0, h / 2, z0 + dz))
        m.caja(n, (0, h / 2, (z0 + z1) / 2 + dz), (w, h, l), piel1 if k == 0 else piel)
        nombres.append(n)
        padre = n

    # ------------------------------------------------------------------ la cola y el abanico
    piel_cola = mapa_fluviosaurus('cola_fluviosaurus', {'arriba': ['VVVVV', 'AVPVA', 'AAMAA', 'AAVAA'],
                                                        '*': ['VVVV', 'AAAA', 'OOOO'], 'atras': ['V'],
                                                        'abajo': ['A']})
    m.parte('cola', padre, (0, ch / 2, z_cola + dz))
    m.caja('cola', (0, ch / 2, z_cola - cl / 2 + dz), (cw, ch, cl), piel_cola)
    z_ab = z_cola - cl
    yv = P['varilla_y']
    m.parte('abanico', 'cola', (0, yv, z_ab + dz))
    for (xv, lv, col) in P['varillas']:
        base = 'V' if col == 'M' else 'A'
        lados = [col * (lv - 1) + base]               # de la punta (columna 0) a la raíz
        pint = mapa_fluviosaurus(f'varilla_{col}{lv}_fluviosaurus', {'izq': lados, 'der': lados,
                                                                    'arriba': [col] * (lv - 1) + [base],
                                                                    'abajo': [base] * lv, 'frente': [base],
                                                                    'atras': [col]})
        dzv = 1.0 if abs(xv) > cw / 2 else 0.0          # las de fuera, detrás del codo
        m.caja('abanico', (xv, yv, z_ab - dzv - lv / 2 + dz), (1, 1, lv), pint)
        if dzv:
            # el codo: sale de lado de la cola hasta la varilla
            codo = mapa_fluviosaurus('codo_fluviosaurus', {'*': ['V'], 'arriba': ['V']})
            xs = math.copysign((cw / 2 + abs(xv) + 0.5) / 2, xv)
            m.caja('abanico', (xs, yv, z_ab - 0.5 + dz), (abs(xv) + 0.5 - cw / 2, 1, 1), codo)

    # ------------------------------------------------------------------ las ramas (un par en cada junta)
    rama_pint = {L: mapa_fluviosaurus(f'rama{L}_fluviosaurus', {'frente': rama_fluviosaurus(L)})
                 for L in sorted(set(P['ramas']))}
    for k, (n, (w, h, l), (z0, z1), L) in enumerate(zip(nombres, P['tramos'], zs, P['ramas'])):
        zr = z1 + P['rama_atras'] + dz
        for lado, ld in ((1, 'i'), (-1, 'd')):
            nr = m.parte(f'rama{k + 1}_{ld}', n, (lado * w / 2, P['rama_y'], zr))
            # una lámina horizontal que mira hacia arriba y sale hacia el lado
            M = B.T(lado * w / 2, P['rama_y'], zr) @ B.girar((-90, -90 * lado, 0))
            m._caja(nr, M, -1.5, 0.0, 0.0, 3.0, float(L), 0.0, None,
                    {c: (rama_pint[L] if c == 'frente' else None) for c in B.CARAS})

    # ------------------------------------------------------------------ la cabeza, el cuello y la mandíbula
    hc, hm = P['alto_cabeza'], P['alto_mandibula']
    cz0, cz1, chh = P['cuello']
    m.parte('cabeza', 'cuerpo', (0, hc / 2, P['tramo1'] + dz))
    cuello = mapa_fluviosaurus('cuello_fluviosaurus', {'arriba': ['O'], '*': ['O'], 'abajo': ['O']})
    m.caja('cabeza', (0, chh / 2, (cz0 + cz1) / 2 + dz), (6, chh, cz0 - cz1), cuello)
    # la bisagra de la mandíbula, atrás, a su altura
    th = math.radians(P['brazo_angulo'])
    z_bisagra = -P['brazo_largo'] * math.cos(th)
    m.parte('mandibula', 'cabeza', (0, hm, z_bisagra + dz))
    for lado, ld in ((-1, 'd'), (1, 'i')):
        brazo_fluviosaurus(m, lado, ld, P, dz, 'cabeza', 'mandibula')
        puas_fluviosaurus(m, lado, ld, P, dz, 'cabeza')
        ojo_fluviosaurus(m, lado, ld, P, dz, 'cabeza')

    m.mirar(('cabeza', 0.5))

    anims_fluviosaurus(m, nombres, P)
    return m

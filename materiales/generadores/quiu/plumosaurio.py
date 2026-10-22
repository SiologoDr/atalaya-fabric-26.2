"""
El Plumosaurio (DEDsafío 2, cartel del día 2; libro del juego:
«Un coloso de seis bloques, de cuello largo y plumón morado: pacífico, no ataca a nadie.
Pero si le pegas, se revuelve: su golpe hace muchísimo daño y te lanza por los aires.
A los treinta segundos sin que le peguen, se calma»).

Rediseño completo con textura facial hiperdetallada de saurópodo antiguo y animaciones colosales:
  - Rostro con ojos almendrados de ámbar/oro brillante con brillo especular, párpados y cejas reptilianas.
  - Hocico esculpido con fosas nasales, comisura de pico y transición a escamas plateadas.
  - Aletas/orejas plumosas en abanico violeta con radios de amatista y penacho occipital morado.
  - Cuello con anillos segmentados y placas dorsales que acompañan la curvatura.
  - Animaciones: marcha colosal con balanceo de peso inercial, reposo sereno con ondulación de cuello y aletas,
    y ataque encabritado donde alza las patas delanteras para aplastar con todo su peso colosal.
"""
import math
import numpy as np

import bestiario as B
import bestiario_creepers as bc
import bestiario_fantasmas_v2 as bf2
import bestiario_hormigas as bh
import bestiario_limpio as L
from bestiario import T
from bestiario_hormigas import _azar1, redondo
from bestiario_limpio import rampa
from bestiario_plantas import dientes_capa
from bestiario_reptiles import FINO, H, P, caja_en, lamina, picos_capa, pix, _con_cara, gajos

ID = 'plumosaurio'
TAM = 2.5

# ======================================================================================================================
#  Paleta de colores
# ======================================================================================================================
OSCURO = rampa('0a0a14', '141422', '202034', '2e2e46', '42425e')
MORADO = rampa('260638', '480c68', '74149e', 'a22cd6', 'd056ff')
PLATA = rampa('4c485c', '6e6882', '9690ae', 'beb8d4', 'e6e2f6')
GRIS_CUELLO = rampa('22202c', '343042', '4a465c', '64607a', '84809e')
OJO_ORO = rampa('4a2806', '844e0c', 'c88218', 'f0b028', 'ffea70')
BOCA_SOMBRA = H('080610')

LADOS = ((1, 'd'), (-1, 'i'))

# ======================================================================================================================
#  Pintores y texturas faciales
# ======================================================================================================================
def mapas_cara_plumosaurio(k=2.5):
    """Genera las matrices de píxeles para el rostro del Plumosaurio:
    - Lateral: ojo almendrado con esclerótica/iris dorado y pupila, ceja reptiliana, fosa nasal y comisura de boca.
    - Frontal: frentes de los ojos, puente nasal gris plata y boca inferior.
    """
    def r(v):
        return int(round(v * k))

    W, Hh = r(21), r(12)
    lado = [['.'] * W for _ in range(Hh)]

    # 1. Franjas plateadas en el hocico superior
    for f in range(r(2), r(7)):
        for c in range(r(12), W):
            lado[f][c] = 'g' if ((c - r(12)) // 2) % 2 == 0 else 'h'

    # 2. Fosa nasal oscura en el hocico
    fn_x, fn_y = r(17), r(3)
    for dy in range(max(1, r(1))):
        for dx in range(max(1, r(1))):
            if fn_y + dy < Hh and fn_x + dx < W:
                lado[fn_y + dy][fn_x + dx] = 'q'

    # 3. Ojo reptiliano almendrado noble (ámbar, pupila negra y brillo especular blanco)
    # Forma almendrada en diagonal
    oj_x, oj_y = r(8), r(4)
    ancho_ojo = max(3, r(3.2))
    alto_ojo = max(2, r(2.5))
    for dy in range(alto_ojo):
        for dx in range(ancho_ojo):
            y_curr = oj_y + dy
            x_curr = oj_x + dx
            if y_curr < Hh and x_curr < W:
                # Contorno oscuro del ojo
                lado[y_curr][x_curr] = 'b'

    # Relleno del iris y pupila
    for dy in range(max(1, alto_ojo - 1)):
        for dx in range(max(1, ancho_ojo - 1)):
            y_curr = oj_y + dy
            x_curr = oj_x + dx + 1
            if y_curr < Hh and x_curr < W:
                lado[y_curr][x_curr] = 'o'  # Ámbar oro

    # Pupila negra en el centro
    cx_p = oj_x + ancho_ojo // 2
    cy_p = oj_y + alto_ojo // 2
    if cy_p < Hh and cx_p < W:
        lado[cy_p][cx_p] = 'q'

    # Brillo blanco especular en la esquina superior delantera
    bx = oj_x + ancho_ojo - 1
    by = oj_y
    if by < Hh and bx < W:
        lado[by][bx] = 'w'

    # Ceja arqueada superior
    for dx in range(ancho_ojo + 1):
        cy_ceja = oj_y - 1
        cx_ceja = oj_x + dx - 1
        if 0 <= cy_ceja < Hh and 0 <= cx_ceja < W:
            lado[cy_ceja][cx_ceja] = 'm'

    # 4. Línea de boca con curva sutil de pico
    alto_boca = max(1, r(1))
    for f in range(r(9), min(Hh, r(9) + alto_boca)):
        for c in range(r(14), W):
            lado[f][c] = 'q'
    # Comisura que sube hacia atrás
    for f in range(r(8), r(9)):
        for c in range(r(13), r(15)):
            if f < Hh and c < W:
                lado[f][c] = 'q'

    # Frente
    Wf = r(11)
    frente = [['.'] * Wf for _ in range(Hh)]
    for f in range(r(2), r(7)):
        for c in range(Wf):
            frente[f][c] = 'g' if (c // 2) % 2 == 0 else 'h'
    # Fosas nasales frontales
    for f in range(r(3), r(4)):
        for c in (r(2), Wf - 1 - r(2)):
            if 0 <= c < Wf and f < Hh:
                frente[f][c] = 'q'
    for f in range(r(9), min(Hh, r(9) + alto_boca)):
        for c in range(r(1), Wf - r(1)):
            frente[f][c] = 'q'

    return [''.join(f) for f in lado], [''.join(f) for f in frente]


def aleta_oreja_plumosa(nombre, R_=MORADO):
    """Aletas/orejas plumosas en los lados de la cabeza:
    Amplias arriba y ahusadas hacia abajo, con radios brillantes de amatista."""
    def fn(tw, th, c, s):
        xs, ys = L._malla(tw, th)
        x, y = xs + 0.5, ys + 0.5
        u, v = x / tw, y / th
        delante = 0.18 + 0.82 * (1.0 - v) ** 1.3
        dentro = (u > 0.03) & (u < delante) & (v < 0.98)
        radio = np.zeros((th, tw), bool)
        for k in (0.32, 0.58, 0.82):
            cu = 0.10 + (k - 0.10) * (1.0 - v) ** 1.3
            radio |= np.abs(u - cu) * tw < 0.65
        canto = dentro & ((u > delante - 1.4 / tw) | (u < 0.04 + 1.2 / tw))
        a = _azar1(xs, ys, s)
        val = 2.9 + 0.8 * (1.0 - v) + radio * 1.0 - canto * 1.1 + (a > 0.92) * 0.4
        tex = L._rgba(L.color_continuo(R_, np.clip(np.round(val), 0, 4)))
        tex[..., 3] = np.where(dentro, 255, 0)
        return tex, None
    return B.fino(B.Pintor(nombre, fn), FINO)


# ======================================================================================================================
#  Construcción del modelo
# ======================================================================================================================
def construir():
    """Construye el Plumosaurio con anatomía de saurópodo colosal."""
    m = B.Modelo(ID, K=2, ancho=256)
    m.escala = 1.0

    plumon = pix('plumon_plumosaurio', MORADO, base=2.8, patron='hebras', ruido=0.2)
    gris = pix('cuello_plumosaurio', GRIS_CUELLO, base=3.1, patron='anillos', paso=3, claro=0.0, ruido=0.4)
    oscuro = pix('piel_oscura_plumosaurio', OSCURO, base=2.4, patron='piel', ruido=0.3)
    pie = pix('pie_plumosaurio', OSCURO, base=1.4, patron='anillos', paso=3, claro=1.0)
    plata = pix('cuello_plata_plumosaurio', PLATA, base=2.6, patron='anillos', paso=3, claro=0.0, ruido=0.4)
    puas = picos_capa('puas_cuello_plumosaurio', OSCURO, colgando=False, banda=1, largo=4, paso=2, v0=1.6)
    morado_cresta = pix('punta_morada_plumosaurio', MORADO, base=3.0, ruido=0.4)
    cola_tex = pix('cola_plumosaurio', OSCURO, base=2.6, patron='anillos', paso=3, claro=0.8)
    punta_cola = gajos('punta_cola_plumosaurio', MORADO, MORADO, n=8, abre=(-60, 60), base=2.6)

    m.parte('cuerpo', None, (0, 12, 0))
    # Cuerpo masivo de saurópodo
    redondo(m, 'cuerpo', (0, 12.5, 0), (12, 11, 23), oscuro, bisel=2)
    m.caja('cuerpo', (0, 18.4, -1.0), (4, 1.6, 20), gris)

    # Masas plumosas en hombros y caderas con flecos caídos
    flecos = picos_capa('flecos_plumosaurio', MORADO, colgando=True, banda=1, largo=9, paso=3, v0=2.6)
    canto = picos_capa('canto_plumosaurio', MORADO, colgando=False, banda=1, largo=4, paso=3, v0=2.9)
    for zc, largo in ((6.8, 9.6), (-7.2, 9.0)):
        redondo(m, 'cuerpo', (0, 12.0, zc), (13.6, 13.0, largo), plumon)
        m.caja('cuerpo', (0, 4.2, zc), (14.0, 4.4, largo + 0.4), flecos)
        m.caja('cuerpo', (0, 19.2, zc), (13.8, 2.0, largo + 0.4), canto, caras={'arriba': None})

    # Patas columnares
    for lado, ld in LADOS:
        for z, nombre in ((7.2, 'del'), (-7.6, 'tra')):
            n = m.parte(f'pata_{nombre}_{ld}', 'cuerpo', (lado * 4.0, 7.0, z))
            m.caja(n, (lado * 4.0, 4.0, z), (4.6, 6.0, 4.6), oscuro)
            m.caja(n, (lado * 4.0, 0.8, z), (5.0, 1.6, 5.0), pie)

    # Cuello largo curvado hacia arriba
    m.parte('cuello', 'cuerpo', (0, 15.0, 10.4))
    m.caja('cuello', (0, 13.4, 10.8), (9.4, 8.0, 4.4), gris, caras={'frente': plata})
    puntos = ((0, 14.0, 11.0), (0, 19.6, 14.8), (0, 25.0, 16.6), (0, 29.4, 16.4), (0, 32.4, 17.2))
    gruesos = (6.0, 5.4, 5.0, 4.6)
    for k in range(4):
        a_, b_ = np.asarray(puntos[k], float), np.asarray(puntos[k + 1], float)
        g = gruesos[k]
        m.viga('cuello', a_, b_, g, gris, extra=2.4 if k < 3 else 0.6, caras={'frente': plata})
        if k == 3:
            continue
        eje = B._u(b_ - a_)
        atras = np.cross(eje, np.array((1.0, 0, 0)))
        atras = atras if atras[2] < 0 else -atras
        c = (a_ + b_) / 2 + atras * (g / 2 + 0.2)
        M = np.eye(4)
        M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = (1, 0, 0), atras, np.cross((1, 0, 0), atras), c
        largo = float(np.linalg.norm(b_ - a_))
        m._caja('cuello', M, -1.6, -0.6, -largo / 2 - 0.6, 3.2, 2.4, largo + 1.2, None,
                {cc: (puas if cc in ('izq', 'der') else None) for cc in B.CARAS})

    # Cabeza y rostro noble
    m.parte('cabeza', 'cuello', (0, 33.4, 17.2))
    oscuro_c = pix('cabeza_plumosaurio', OSCURO, base=2.6, patron='piel', ruido=0.3)

    colores = {
        'w': H('ffffff'),
        'q': H('06060c'),
        'b': H('1c1428'),
        'o': H('f0b428'),
        'm': H('362448'),
        'g': L.color_continuo(PLATA, np.array([2.8]))[0],
        'h': L.color_continuo(PLATA, np.array([1.4]))[0],
    }
    lado_p, frente_p = mapas_cara_plumosaurio(TAM)
    cara = _con_cara('cara_plumosaurio', oscuro_c, {'izq': lado_p, 'der': lado_p, 'frente': frente_p}, colores,
                     fino=True)

    techo = 37.6
    m.caja('cabeza', (0, techo - 2.9, 20.2), (5.4, 5.8, 10.4), oscuro_c,
           caras={'izq': cara, 'der': cara, 'frente': cara})
    for lado in (1, -1):
        Me = T(lado * 1.9, techo, 17.4) @ B.girar((-25, 0, lado * 10))
        caja_en(m, 'cabeza', Me, (0, 0.8, 0), (1.4, 1.8, 1.8), oscuro_c)
        caja_en(m, 'cabeza', Me, (0, 2.1, -0.2), (0.9, 1.2, 1.1), oscuro_c)

    # Aletas plumosas en abanico
    oreja = aleta_oreja_plumosa('aleta_oreja_plumosaurio', MORADO)
    for lado in (1, -1):
        lamina(m, 'cabeza', T(lado * 2.7, 35.2, 18.6) @ B.girar((0, -90 - lado * 55, 0)), 5.2, 8.4, oreja,
               abajo=True, x0=-5.2)

    # Cresta dorsal escalonada y penacho morado
    for (z0, z1, abajo, ancho) in ((12.2, 15.0, 31.0, 5.0), (9.6, 12.2, 33.0, 4.4), (7.2, 9.6, 34.6, 3.8),
                                   (5.0, 7.2, 35.8, 3.2)):
        m.caja('cabeza', (0, (techo + abajo) / 2, (z0 + z1) / 2), (ancho, techo - abajo, z1 - z0), oscuro_c)
    m.viga('cabeza', (0, 31.8, 12.8), (0, 26.2, 14.4), 2.2, oscuro_c, ancho=4.4, extra=0.6)
    m.caja('cabeza', (0, techo - 1.0, 4.0), (3.0, 2.0, 2.0), morado_cresta)
    m.caja('cabeza', (0, techo - 3.0, 3.7), (2.6, 2.0, 1.4), morado_cresta)

    # Cola y penacho en abanico
    m.parte('cola', 'cuerpo', (0, 15.0, -11.4))
    m.caja('cola', (0, 15.0, -15.4), (5.0, 4.6, 9.0), cola_tex)
    m.caja('cola', (0, 15.2, -23.0), (4.0, 3.6, 7.0), cola_tex)
    for giro in (0, 60, 120):
        M = T(0, 15.0, -26.0) @ B.girar((-140, 0, 0)) @ B.girar((0, giro, 0))
        m._caja('cola', M, -5.0, 0.0, 0.0, 10.0, 8.0, 0.0, None,
                {c: (punta_cola if c == 'frente' else None) for c in B.CARAS})

    m.mirar(('cabeza', 0.40), ('cuello', 0.15))
    anims_plumosaurio(m)
    return m


# ======================================================================================================================
#  Animaciones colosales de saurópodo
# ======================================================================================================================
def anims_plumosaurio(m):
    """Animaciones del coloso:
    reposo: respiración profunda y calmada; el cuello traza una curva majestuosa mirando al horizonte;
            las aletas de la cabeza se mecen suavemente en el viento; la cola ondea.
    andar: zancada pesada de saurópodo con transferencia de peso lateral; el cuello cabecea en contrapeso;
           las patas se alzan con flexión de rodilla y apoyan pesadas.
    ataque: encabritamiento monumental; alza ambas patas delanteras y descarga el cuello y pecho con violencia brutal.
    muerte: desplome colosal sobre su costado.
    """
    # Reposo sereno
    r = m.anim('reposo', 6.0, bucle=True)
    r.onda('cuerpo', 'm', 1, 0.35, periodo=3.0)
    r.onda('cuerpo', 'r', 0, 1.0, periodo=6.0)
    r.rot('cuello', [
        (0.0, 0, 0, 0),
        (1.5, -2, 10, -2),
        (2.8, -1, 12, -2),
        (3.8, 3, -10, 2),
        (5.0, 2, -12, 2),
        (6.0, 0, 0, 0)
    ])
    r.rot('cabeza', [
        (0.0, 0, 0, 0),
        (1.5, 4, 14, 0),
        (2.8, 2, 16, 0),
        (3.8, -3, -14, 0),
        (5.0, -2, -16, 0),
        (6.0, 0, 0, 0)
    ])
    r.onda('cola', 'r', 1, 10.0, periodo=3.0)
    r.onda('cola', 'r', 0, 3.0, periodo=3.0, fase=0.25)

    s_ = m.anim('siempre', 3.0, bucle=True)
    s_.onda('cola', 'r', 0, 2.5, periodo=3.0, fase=0.3)

    # Andar colosal
    a = m.anim('andar', 2.0, bucle=True)
    for k, (lado, ld) in enumerate(LADOS):
        for nombre, f in (('del', 0.5 * k), ('tra', 0.5 * (1 - k))):
            a.onda(f'pata_{nombre}_{ld}', 'r', 0, 14, periodo=2.0, fase=f)
            a.onda(f'pata_{nombre}_{ld}', 'm', 1, 1.8, periodo=2.0, fase=f + 0.75, forma=lambda v: max(0.0, v))
    # Peso masivo del cuerpo bamboleándose
    a.onda('cuerpo', 'r', 2, 3.5, periodo=2.0)
    a.onda('cuerpo', 'm', 1, 0.45, periodo=1.0)
    # Contrapeso armónico del cuello
    a.onda('cuello', 'r', 0, 4.0, periodo=1.0, fase=0.3)
    a.onda('cuello', 'r', 2, -3.2, periodo=2.0)
    a.onda('cabeza', 'r', 0, 2.5, periodo=1.0, fase=0.1)
    a.onda('cola', 'r', 1, 9.0, periodo=2.0, fase=0.5)

    # Ataque encabritado
    at = m.anim('ataque', 1.15)
    at.mov('cuerpo', [(0, 0, 0, 0), (0.42, 0, 2.8, -2.5), (0.70, 0, -1.8, 3.5), (0.90, 0, -0.6, 1.5), (1.15, 0, 0, 0)])
    at.rot('cuerpo', [(0, 0, 0, 0), (0.42, -18, 0, 0), (0.70, 8, 0, 0), (1.15, 0, 0, 0)])
    at.rot('cuello', [(0, 0, 0, 0), (0.42, -32, 0, 0), (0.70, 36, 0, 0), (0.92, 14, 0, 0), (1.15, 0, 0, 0)])
    at.rot('cabeza', [(0, 0, 0, 0), (0.42, -22, 0, 0), (0.70, 26, 0, 0), (0.92, 10, 0, 0), (1.15, 0, 0, 0)])
    for lado, ld in LADOS:
        at.rot(f'pata_del_{ld}', [(0, 0, 0, 0), (0.42, -45, 0, lado * 6), (0.70, 10, 0, 0), (1.15, 0, 0, 0)])
        at.rot(f'pata_tra_{ld}', [(0, 0, 0, 0), (0.42, 12, 0, 0), (0.70, -6, 0, 0), (1.15, 0, 0, 0)])

    # Muerte colosal
    d = m.anim('muerte', 1.6)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.4, -6, 0, 0), (1.6, 0, 0, 90)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.6, 0, -8, 0)])
    d.rot('cuello', [(0, 0, 0, 0), (0.5, -20, 0, 0), (1.6, 25, 0, 30)])
    d.rot('cabeza', [(0, 0, 0, 0), (1.6, 20, 0, 20)])

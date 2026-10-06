"""
Propuesta de remake de Nerea, Guardian de los Mares (octubre de 2026): la misma
malla del juego (nerea_juego.py) con lo que la hace mas imponente, como se hizo
con Aeralis y Rajang. Solo para la ficha: no escribe nada en el repo.

Lo que cambia:
  - Tamano: de unos 10 bloques a unos 15 (el renderer escala x2,4 en vez de x1,6).
  - La CONCHA: un abanico de venera detras de la cabeza, de nacar, con el filo
    encendido y una perla que brilla en el centro (el halo de un dios del mar).
  - La CORONA: puas de prismarina y cuernos de coral mucho mas largos.
  - La BARBA: algas que le cuelgan de la mandibula, como tentaculos.
  - La CAPA: tiras de algas desde los hombros hasta el suelo.
  - Las ESPINAS: tres espinas de hueso por el lomo, entre las algas de la capa.
  - La CARACOLA: una caracola enorme de hombrera en el hombro izquierdo; los
    corales del derecho, mas grandes.
  - El ANCLA: el gancho de la cadena-latigo pasa a ser un ancla de verdad.
  - El TRIDENTE: mas largo, con las puntas mas grandes y una espiral de espuma
    que brilla subiendole por el asta.
  - El CORAZON, un cuarto mas grande.

Uso: import nerea_remake as nr; nr.usar('antes') / nr.usar('despues') y despues
nerea_juego.quads(...) con nr.ESCALA[cual].
"""
import copy, math, os
os.environ.setdefault('NEREA_SIN_FISICA', '1')
import numpy as np
import nerea_juego as nj
import nerea_modelo as nm
import nerea_juego_anim as nja      # construye la malla del juego y sus poses

ESCALA = {'antes': 1.6, 'despues': 2.4}

# ----------------------------------------------------------------------
#  Materiales nuevos (losetas 16x16, el mismo metodo que nerea_modelo.py)
# ----------------------------------------------------------------------
NACAR = nm._rampa('6a4862', 'a0788e', 'd0a6bc', 'f0d2e2', 'fff4fa')
ALGA_OSC = nm._rampa('0c200e', '143214', '1e4a1a', '2a6222', '3a7a2e')
ALETA = nm._rampa('0e2e34', '16424a', '205a60', '2c7276', '3e8c8c')


def _nacar(x, y, r):
    # bandas de nacar con un reflejo iridiscente (rosa y turquesa)
    b = [1, 2, 3, 3, 2][(y // 3) % 5]
    if r.random() < 0.12:
        b = 4
    c = NACAR[b]
    if (x + y * 2) % 11 == 0:
        c = (c[0] - 20, c[1] + 18, c[2] + 22)
    elif (x * 3 + y) % 13 == 0:
        c = (c[0] + 24, c[1] - 6, c[2] + 4)
    return tuple(max(0, min(255, v)) for v in c)


def _nacar_osc(x, y, r):
    # el surco entre lomos: el mismo nacar, mas apagado y rosado
    c = _nacar(x, y, r)
    return tuple(max(0, min(255, int(v))) for v in (c[0] * 0.78 + 12, c[1] * 0.66, c[2] * 0.74))


def _alga_osc(x, y, r):
    b = r.choice([1, 2, 2, 3])
    if x in (0, 15):
        b = 0
    elif x == 8 and r.random() < 0.7:
        b = 4                       # el nervio de la hoja
    return ALGA_OSC[b]


def _aleta(x, y, r):
    b = 2 if x % 4 else 0           # radios de la aleta
    if r.random() < 0.1:
        b = 3
    return ALETA[b]


NUEVOS = {
    'concha': nm._loseta(30, _nacar),
    'concha_osc': nm._loseta(35, _nacar_osc),
    'alga_osc': nm._loseta(31, _alga_osc),
    'aleta': nm._loseta(32, _aleta),
    'perla': nm._loseta(33, nm.emisivo('ffffff', '9fe8ff')),
    'nacar_luz': nm._loseta(36, nm.emisivo('fff4fa', 'ff9ac8')),
    'espuma': nm._loseta(34, nm.emisivo('f0ffff', '3fe0ff')),
}
nj.MAT.update(NUEVOS)
nj.EMISIVOS.update({'perla', 'espuma', 'nacar_luz'})
nj.CON_VENAS.update({'concha', 'concha_osc'})      # la maldicion tambien le sube por la concha
nj.BRILLO.update({'perla': ('ffffff', '9fe8ff'), 'espuma': ('f0ffff', '3fe0ff'), 'nacar_luz': ('fff4fa', 'ff9ac8')})
nj.BRILLO_LIBRE.update({'perla': ('fffbe0', 'ffd86a'), 'espuma': ('fff6d0', 'ffcf5a'), 'nacar_luz': ('fffbe0', 'ffd86a')})

# ----------------------------------------------------------------------
#  Las dos mallas
# ----------------------------------------------------------------------
_ANTES = (nj.PARTES, nj.ORDEN)


def _copia():
    partes = copy.deepcopy(nj.PARTES)
    return partes, list(nj.ORDEN)


def _escalar_y(nombre, k, partes):
    """Alarga una pieza (y sus hijos) a lo largo de su Y local: cajas y pivotes."""
    p = partes[nombre]
    p.cajas = [(c[0], c[1] * k, c[2], c[3], c[4] * k, c[5], c[6]) for c in p.cajas]
    for h in p.hijos:
        h.pivote = (h.pivote[0], h.pivote[1] * k, h.pivote[2])
        _escalar_y(h.nombre, k, partes)


def _escalar(nombre, k, partes):
    """Agranda las cajas de una pieza alrededor de su pivote."""
    p = partes[nombre]
    p.cajas = [tuple(v * k for v in c[:6]) + (c[6],) for c in p.cajas]


def _engordar(nombre, k, partes):
    """Engorda una pieza (x y z de sus cajas) sin alargarla."""
    p = partes[nombre]
    p.cajas = [(c[0] * k, c[1], c[2] * k, c[3] * k, c[4], c[5] * k, c[6]) for c in p.cajas]


def construir_remake():
    partes, orden = _copia()

    def parte(nombre, padre, pivote, rot=(0, 0, 0), cajas=()):
        p = nj.Parte(nombre, padre, pivote, rot, cajas)
        partes[nombre] = p
        orden.append(nombre)
        if padre:
            partes[padre].hijos.append(p)
        return p

    # --- La corona: puas y cuernos de coral mucho mas largos
    for i in range(6):
        _escalar_y(f'puas_{i}', 1.9, partes)
    for n in ('corona_c1', 'corona_c2', 'corona_c3', 'corona_c4'):
        _escalar_y(n, 1.7, partes)
    for n in [k for k in partes if k.startswith('coral_h')]:
        _escalar_y(n, 1.5, partes)

    # --- La concha: un abanico de venera detras de la cabeza, con la perla
    # Una venera: costillas anchas que se solapan (lomos y surcos alternos) y
    # un borde ondulado, mas oscuro, en la punta de cada una.
    parte('concha', 'cabeza', (0, -8, 10), (10, 0, 0), [
        (-4, -4, -1.2, 8, 8, 2.4, 'concha_osc')])
    for i in range(15):
        a = -70 + i * 10
        lomo = i % 2 == 0
        largo = 30 if lomo else 28
        ancho = 5.6
        parte(f'concha_r{i}', 'concha', (0, 0, 0.0 if lomo else 0.6), (0, 0, a), [
            (-ancho / 2, -largo, -0.7 if lomo else -0.5, ancho, largo, 1.4 if lomo else 1.0,
             'concha' if lomo else 'concha_osc'),
            (-ancho / 2 - 0.2, -largo - 1.4, -0.8, ancho + 0.4, 1.6, 1.6, 'nacar_luz')])   # el filo, que brilla
    parte('perla', 'concha', (0, 0, -1.8), cajas=[(-2.4, -2.4, -1.4, 4.8, 4.8, 2.8, 'perla')])

    # --- La barba: algas de la mandibula, como tentaculos
    for i, x in enumerate((-4.5, -2.5, -0.5, 1.5, 3.5)):
        largo = (20, 27, 32, 26, 19)[i]
        parte(f'barba_{i}', 'mandibula', (x + 0.5, 3.6, -11.2), (14, 0, (i - 2) * 5), [
            (-1.2, 0, 0, 2.6, largo, 0, 'alga')])

    # --- La capa de algas: de los hombros al suelo, por la espalda
    for i, x in enumerate((-11, -5.5, 0, 5.5, 11)):
        largo = (52, 60, 64, 60, 52)[i]
        parte(f'capa_{i}', 'torso', (x, -27, 8.2), (24, 0, (i - 2) * -3), [
            (-3, 0, 0, 6, largo, 0, 'alga_osc')])

    # --- Espinas de hueso por el lomo, entre las algas de la capa
    for i, y in enumerate((-26, -20, -14)):
        parte(f'espina_{i}', 'torso', (0, y, 8), (-55, 0, 0), [
            (-1.1, -12 + i * 2, -1.1, 2.2, 12 - i * 2, 2.2, 'hueso')])

    # --- Hombreras mas grandes
    for n in ('hombro_izq', 'hombro_der'):
        _escalar(n, 1.3, partes)

    # --- La caracola del hombro izquierdo
    parte('caracola', 'hombro_izq', (1, -7, 0), (0, 0, 18), [
        (-7, -5, -7, 14, 5, 14, 'concha'),
        (-5.5, -9.5, -5.5, 11, 4.5, 11, 'concha'),
        (-4, -13, -4, 8, 3.5, 8, 'concha'),
        (-2.6, -16, -2.6, 5.2, 3, 5.2, 'concha'),
        (-1.3, -19.5, -1.3, 2.6, 3.5, 2.6, 'concha'),
        (6.5, -4, -1, 5, 2, 2, 'concha'), (-1, -8, 5, 2, 2, 5, 'concha'),
        (-9.5, -7, -1, 4, 2, 2, 'concha'), (-1, -3, -10, 2, 2, 4, 'concha')])

    # --- El ancla al final de la cadena-latigo (en lugar del gancho)
    g = partes['gancho_mano']
    g.cajas = [
        (-2.6, -2.5, -0.9, 5.2, 3, 1.8, 'oxido'),           # la argolla
        (-1.3, 0, -1.3, 2.6, 13, 2.6, 'prisma_osc'),        # la cana
        (-1.1, 2.5, -8, 2.2, 2.2, 16, 'oxido'),             # el cepo, de fondo
        (-2, 12, -2, 4, 3.5, 4, 'prisma_osc'),              # la cruz
        (-1, 5, 1.2, 2, 2, 2, 'percebe'), (0.6, 9, -2.2, 2, 2, 1.5, 'percebe')]
    for s, n in ((1, 'izq'), (-1, 'der')):
        parte('ancla_' + n, 'gancho_mano', (0, 14, 0), (0, 0, s * 128), [
            (-1.2, 0, -1.2, 2.4, 11, 2.4, 'prisma_osc'),
            (-3.4, 7, -1.4, 6.8, 6, 2.8, 'prisma_osc')])  # la una

    # --- El tridente: mas largo, puntas mas grandes y la espiral de espuma
    t = partes['tridente']
    t.cajas = [(-1.3, -30, -1.3, 2.6, 96, 2.6, 'prisma_osc'),
               (-2, 64, -2, 4, 4, 4, 'punta'),
               (-11, 67, -2, 22, 3.5, 4, 'prisma'),
               (-1.8, 70, -1.8, 3.6, 20, 3.6, 'punta'),
               (-10.5, 70, -1.5, 3, 14, 3, 'punta'),
               (7.5, 70, -1.5, 3, 14, 3, 'punta'),
               (-4.5, 81, -1, 2.5, 4, 2, 'punta'),
               (2, 81, -1, 2.5, 4, 2, 'punta'),
               (-11.5, 81, -1, 2, 4, 2, 'punta'), (9.5, 81, -1, 2, 4, 2, 'punta')]
    espiral = []
    for k in range(26):
        a = k * 0.62
        y = -22 + k * 3.3
        espiral.append((math.cos(a) * 3.2 - 0.8, y, math.sin(a) * 3.2 - 0.8, 1.6, 1.6, 1.6, 'espuma'))
    parte('espiral', 'tridente', (0, 0, 0), cajas=espiral)

    # --- Brazos y piernas mas gruesos (iban flacos bajo las hombreras nuevas)
    for n in ('brazo', 'antebrazo', 'mano', 'pierna', 'espinilla', 'pie'):
        for lado in ('izq', 'der'):
            _engordar(f'{n}_{lado}', 1.22, partes)
    # --- Ojos mas grandes; algas del faldon mas largas
    for n in ('ojo_izq', 'ojo_der'):
        _escalar(n, 1.35, partes)
    for n in ('algas_del', 'algas_tras'):
        _escalar_y(n, 1.35, partes)
    return partes, orden


_DESPUES = construir_remake()


def usar(cual):
    """Cambia la malla que usan las funciones de nerea_juego (quads, matrices...)."""
    nj.PARTES, nj.ORDEN = _ANTES if cual == 'antes' else _DESPUES


# ----------------------------------------------------------------------
#  Atlas de cada una (la espuma lleva el color de las puntas de la fase)
# ----------------------------------------------------------------------
_ATLAS = {}


def atlas(cual, fase):
    k = (cual, fase)
    if k not in _ATLAS:
        usar(cual)
        nj.BRILLO['espuma'] = nj.PUNTAS_FASE[fase] if fase in nj.PUNTAS_FASE else nj.BRILLO['espuma']
        uv, alto = nj.empaquetar()
        base, brillo, libre = nj.pintar_atlas(uv, alto, fase if fase != 'libre' else 1)
        if fase == 'libre':
            brillo = libre
        _ATLAS[k] = (base, brillo, uv, alto)
    return _ATLAS[k]

"""
Animaciones de Novilis, escritas pose a pose.

Las poses se escriben como en la ficha (fuego_escenas.py): offsets sobre el
esqueleto del boceto, con los brazos colocados por cinematica inversa
(fm.alcanzar: donde cae el puno) y la espada apuntada (fm.apuntar_espada). La
guardia (la espada baja en la derecha, la izquierda suelta) va HORNEADA en la
malla: es la postura de reposo de las piezas, asi que al mezclar un ataque con
andar el cuerpo no pasa por los brazos colgando.

Convenciones de las poses (todo SE SUMA al boceto, como en la ficha):
  rot   grados (x, y, z)
  pos   pixeles del modelo con Y hacia ABAJO (al exportar pasa a posVec)
Al exportar se resta la guardia de las piezas en las que va horneada.

De aqui salen NovilisAnimaciones.java, NovilisGeometria.java (duraciones,
ticks de cada golpe y puntos del cuerpo para el servidor), NovilisMalla.java y
las pieles.

Uso: python novilis_juego_anim.py <raiz del proyecto> [carpeta de hojas] [ANIM,ANIM]
"""
import math, os, sys, copy
import numpy as np
from PIL import Image, ImageDraw
import vigia_render as vr
import fuego_modelo as fm
import novilis_juego as nj

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
RENDERS = sys.argv[2] if len(sys.argv) > 2 else None
fm.VARIANTE_IK = 'N'


# ----------------------------------------------------------------------
#  Ayudas de pose (en el espacio del boceto)
# ----------------------------------------------------------------------
def r(x, y=0, z=0):
    return {'rot': (x, y, z)}


def P(x, y, z):
    return {'pos': (x, y, z)}


def mezcla(*poses):
    out = {}
    for p in poses:
        for k, v in p.items():
            d = out.setdefault(k, {})
            d.update(copy.deepcopy(v))
    return out


def ik(base, izq=None, der=None, espada=None, giro_filo=0.0):
    """Coloca los punos (px de modelo) y apunta la espada."""
    p = copy.deepcopy(base)
    if der is not None:
        p, err = fm.alcanzar(p, 'der', der)
        assert err < 6.0, ('puno der no llega', der, err)
    if izq is not None:
        p, err = fm.alcanzar(p, 'izq', izq)
        assert err < 6.0, ('puno izq no llega', izq, err)
    if espada is not None:
        p = fm.apuntar_espada(p, espada, giro_filo)
    return p


# ----------------------------------------------------------------------
#  Posturas base
# ----------------------------------------------------------------------
# Hombros en (+-21, -86, 0); de hombro a puno caben 49 px.
GUARDIA = ik({}, izq=(26, -44, -6), der=(-25, -46, -20), espada=(-0.14, 0.55, -0.82))
HORNEADAS = ['brazo_izq', 'antebrazo_izq', 'brazo_der', 'antebrazo_der', 'agarre']

RODILLA = {'pelvis': P(0, 30, 0), 'tabardo': r(-70),
           'pierna_izq': r(-86, 0, -6), 'espinilla_izq': r(86), 'pie_izq': r(0),
           'pierna_der': r(6, 0, 5), 'espinilla_der': r(86), 'pie_der': r(-62),
           'capa_1': r(8), 'capa_2': r(24), 'capa_3': r(50)}
CAPA_VIENTO = {'capa_1': r(20), 'capa_2': r(10), 'capa_3': r(12)}


def con_guardia(p):
    """Lo que no dice una pose de los brazos, igual que en la guardia."""
    out = copy.deepcopy(p)
    for k in HORNEADAS:
        if k not in out or 'rot' not in out[k]:
            out.setdefault(k, {})['rot'] = GUARDIA[k]['rot']
    return out


def a_juego(p):
    """De la pose del boceto a la del juego: menos la guardia horneada."""
    out = {}
    for k, v in con_guardia(p).items():
        d = dict(v)
        if k in HORNEADAS and 'rot' in d:
            g = GUARDIA[k]['rot']
            d['rot'] = tuple(d['rot'][i] - g[i] for i in range(3))
        out[k] = d
    return out


N = {}

# --- Posturas de los ataques (como en la ficha) ---
ALZA = ik(mezcla({'cabeza': r(-24), 'torso': r(-6)}, CAPA_VIENTO), der=(0, -128, -8), izq=(1, -117, -8),
          espada=(0, -1, 0.02))
ARRODILLADO_CLAVA = ik(mezcla(RODILLA, {'torso': r(12), 'cabeza': r(10)}), der=(0, -12, -32), izq=(0, -22, -32),
                       espada=(0, 1, 0.05))
ARRODILLADO_SOL = ik(mezcla(RODILLA, {'torso': r(8), 'cabeza': r(-30)}), der=(0, -20, -30), izq=(0, -30, -30),
                     espada=(0, 1, 0.05))
DORMIDO = ik(mezcla(RODILLA, {'torso': r(18), 'cuello': r(8), 'cabeza': r(26)}), der=(0, -14, -30), izq=(0, -24, -30),
             espada=(0, 1, 0.05))
GRITO = ik(mezcla({'cabeza': r(-26), 'torso': r(-10), 'pelvis': P(0, 1, 0),
                   'pierna_izq': r(-14, 0, -8), 'espinilla_izq': r(16), 'pierna_der': r(12, 0, 8), 'pie_der': r(-14)},
                  CAPA_VIENTO), izq=(40, -50, -14), der=(-40, -50, -14), espada=(-0.5, 0.3, -0.8))
SOL_ARRIBA = ik(mezcla({'cabeza': r(-24, 10), 'torso': r(-6, -10), 'pierna_izq': r(-16, 0, -6), 'espinilla_izq': r(18),
                        'pierna_der': r(14, 0, 8), 'pie_der': r(-20)}, CAPA_VIENTO),
                izq=(38, -124, -10), der=(-26, -44, -16), espada=(-0.2, 0.55, -0.81))
SOL_LANZA = ik(mezcla({'cabeza': r(4, -10), 'torso': r(10, 18), 'pierna_izq': r(-24, 0, -6), 'espinilla_izq': r(24),
                       'pierna_der': r(18, 0, 8), 'pie_der': r(-24)}, CAPA_VIENTO),
               izq=(8, -60, -46), der=(-30, -44, -10), espada=(-0.3, 0.5, -0.8))
# Clavar la espada a un lado (Ofrenda y Dios de la Guerra): el puno a su derecha y la hoja al suelo.
CLAVA_LADO = ik(mezcla({'torso': r(14, 10), 'cabeza': r(14), 'pelvis': P(0, 4, 0), 'pierna_der': r(-10, 0, 6),
                        'espinilla_der': r(14)}), der=(-34, -34, -14), izq=(24, -44, -6), espada=(-0.12, 1, -0.08))
OFRENDA_AGARRA = ik(mezcla({'torso': r(24), 'cabeza': r(18), 'pelvis': P(0, 6, 0),
                            'pierna_izq': r(-20, 0, -6), 'espinilla_izq': r(30), 'pierna_der': r(14, 0, 6), 'espinilla_der': r(20)}),
                    izq=(10.5, -46, -42), der=(-10.5, -46, -42))
OFRENDA_ALZA = ik(mezcla({'cabeza': r(-34), 'torso': r(-6)}, CAPA_VIENTO), izq=(10.5, -112, -30), der=(-10.5, -112, -30))
DIOS = ik(mezcla({'cabeza': r(-16), 'torso': r(-8), 'pierna_izq': r(-16, 0, -8), 'espinilla_izq': r(18),
                  'pierna_der': r(14, 0, 8), 'pie_der': r(-18)}, CAPA_VIENTO), izq=(44, -118, -10), der=(-44, -118, -10))
DIOS_LANZA = ik(mezcla({'cabeza': r(4), 'torso': r(14), 'pierna_izq': r(-22, 0, -8), 'espinilla_izq': r(24),
                        'pierna_der': r(18, 0, 8), 'pie_der': r(-22)}, CAPA_VIENTO), izq=(30, -70, -42), der=(-30, -70, -42))


# --- Los tajos del Barrido: carga y golpe de cada uno ---
def tajo(puno, hoja, torso_y, paso_izq=0.0, extra=None):
    base = mezcla({'torso': r(4, torso_y), 'cabeza': r(0, -torso_y * 0.6), 'pelvis': P(0, 2, 0),
                   'pierna_izq': r(-14 - paso_izq, 0, -8), 'espinilla_izq': r(18 + paso_izq), 'pierna_der': r(14, 0, 8),
                   'espinilla_der': r(10), 'pie_der': r(-20)}, CAPA_VIENTO, extra or {})
    izq = (32, -54, 12) if torso_y < 0 else (28, -56, -22)
    return ik(base, izq=izq, der=puno, espada=hoja)


T1_CARGA = tajo((-34, -70, 8), (-0.75, -0.3, 0.6), 26)
T1_GOLPE = tajo((18, -62, -40), (0.88, 0.05, -0.47), -26, 6)
T2_CARGA = tajo((26, -72, -2), (0.8, -0.25, 0.55), -22)
T2_GOLPE = tajo((-26, -60, -38), (-0.88, 0.05, -0.47), 24, 6)
T3_CARGA = tajo((-12, -124, -2), (-0.3, -0.9, 0.3), 8, 0, {'cabeza': r(-14)})
T3_GOLPE = tajo((10, -40, -40), (0.35, 0.65, -0.68), -14, 10, {'torso': r(22, -14)})
T4_CARGA = tajo((-36, -66, 14), (-0.72, -0.1, 0.68), 32)
T4_GOLPE = tajo((26, -64, -36), (0.92, 0.02, -0.39), -32, 10)
T_TAJOS = (0.6, 1.4, 2.2, 3.1)


# ----------------------------------------------------------------------
#  Las animaciones
# ----------------------------------------------------------------------
ANIMS = {}


def anim(nombre, dur, claves, loop=False):
    ANIMS[nombre] = {'dur': dur, 'loop': loop, 'claves': [(t, a_juego(p), i) for t, p, i in claves]}


G = GUARDIA

# --- Reposo: respira, el peso de la espada, la capa se mece ---
_rep = mezcla(G, {'torso': r(1.8), 'cabeza': r(-2, 4), 'pelvis': P(0, 0.8, 0), 'capa_1': r(3), 'capa_2': r(2),
                  'brazo_der': {'rot': tuple(G['brazo_der']['rot'][i] + (2.5, 0, 0)[i] for i in range(3))}})
anim('REPOSO', 4.0, [(0, G, 'c'), (2.0, _rep, 'c'), (4.0, G, 'c')], loop=True)


# --- Andar: zancada pesada de gigante con armadura ---
def _paso(k):
    """k=0: la izquierda delante; k=1: pasa la derecha; k=2: la derecha delante; k=3: pasa la izquierda."""
    s = 1 if k in (0, 1) else -1
    if k % 2 == 0:
        piernas = {'pierna_izq': r(-24 * s), 'espinilla_izq': r(8 if s > 0 else 26), 'pie_izq': r(6 if s > 0 else -10),
                   'pierna_der': r(24 * s), 'espinilla_der': r(26 if s > 0 else 8), 'pie_der': r(-10 if s > 0 else 6),
                   'pelvis': P(0, 2.0, 0)}
    else:
        apoyo, aire = ('izq', 'der') if k == 1 else ('der', 'izq')
        piernas = {'pierna_' + apoyo: r(4), 'espinilla_' + apoyo: r(6), 'pie_' + apoyo: r(-4),
                   'pierna_' + aire: r(-18), 'espinilla_' + aire: r(46), 'pie_' + aire: r(-6), 'pelvis': P(0, -0.6, 0)}
    tronco = {'torso': r(3, 5 * s), 'cabeza': r(0, -4 * s), 'capa_1': r(6 + 3 * (k % 2)), 'capa_2': r(3), 'capa_3': r(4)}
    bi = G['brazo_izq']['rot']
    brazos = {'brazo_izq': {'rot': (bi[0] + 14 * s, bi[1], bi[2])}}
    return mezcla(G, piernas, tronco, brazos)


anim('ANDAR', 2.0, [(0, _paso(0), 'c'), (0.5, _paso(1), 'c'), (1.0, _paso(2), 'c'), (1.5, _paso(3), 'c'),
                    (2.0, _paso(0), 'c')], loop=True)
ZANCADA_PX = 2 * (math.sin(math.radians(24)) * 64) * 2      # lo que avanza el cuerpo por vuelta, en px

# --- Dormido: de rodilla, la espada clavada delante y la cabeza gacha ---
anim('DORMIDO', 6.0, [(0, DORMIDO, 'c'), (3.0, mezcla(DORMIDO, {'torso': r(20), 'cabeza': r(30)}), 'c'),
                      (6.0, DORMIDO, 'c')], loop=True)

# --- Despertar: alza la cabeza, se pone en pie, arranca la espada y ruge ---
_de_pie = ik(mezcla({'pelvis': P(0, 12, 0), 'torso': r(16), 'cabeza': r(-4), 'pierna_izq': r(-50, 0, -6),
                     'espinilla_izq': r(60), 'pierna_der': r(10, 0, 5), 'espinilla_der': r(50), 'pie_der': r(-30)}),
             der=(-6, -30, -30), izq=(24, -40, -10), espada=(0, 1, 0.1))
_arranca = ik(mezcla({'cabeza': r(-20), 'torso': r(-6)}, CAPA_VIENTO), der=(-14, -126, -10), izq=(40, -56, -12),
              espada=(-0.1, -1, 0.05))
anim('DESPERTAR', 3.4, [(0, DORMIDO, 'c'), (0.5, mezcla(DORMIDO, {'cabeza': r(-10)}), 'c'), (1.3, _de_pie, 'c'),
                        (1.9, _arranca, 'c'), (2.4, GRITO, 'l'), (2.9, mezcla(GRITO, {'cabeza': r(-30, 4)}), 'c'),
                        (3.4, G, 'c')])
T_DESPERTAR_RUGE = 2.4

# --- Barrido de fuego: cuatro tajos ---
anim('BARRIDO', 3.8, [(0, G, 'c'), (0.32, T1_CARGA, 'c'), (T_TAJOS[0], T1_GOLPE, 'l'), (0.85, T1_GOLPE, 'c'),
                      (1.12, T2_CARGA, 'c'), (T_TAJOS[1], T2_GOLPE, 'l'), (1.62, T2_GOLPE, 'c'),
                      (1.9, T3_CARGA, 'c'), (T_TAJOS[2], T3_GOLPE, 'l'), (2.45, T3_GOLPE, 'c'),
                      (2.78, T4_CARGA, 'c'), (T_TAJOS[3], T4_GOLPE, 'l'), (3.35, T4_GOLPE, 'c'), (3.8, G, 'c')])

# --- Castigo solar: alza la espada al sol; los rayos caen; desde la II, la clava ---
T_CASTIGO_ALZA = 0.7
T_CASTIGO_MARCA = 1.0
T_CASTIGO_RAYO = 2.1
_alza_tiembla = mezcla(ALZA, {'torso': r(-8, 2), 'cabeza': r(-28, -3)})
anim('CASTIGO', 2.8, [(0, G, 'c'), (T_CASTIGO_ALZA, ALZA, 'c'), (1.4, _alza_tiembla, 'c'), (T_CASTIGO_RAYO, ALZA, 'c'),
                      (2.8, G, 'c')])
T_ONDA_SALTA = 2.35
T_ONDA_CLAVA = 2.6
_salta = mezcla(ALZA, {'pelvis': P(0, -6, 0), 'torso': r(-12)})
anim('CASTIGO_ONDA', 4.2, [(0, G, 'c'), (T_CASTIGO_ALZA, ALZA, 'c'), (1.4, _alza_tiembla, 'c'), (T_CASTIGO_RAYO, ALZA, 'c'),
                           (T_ONDA_SALTA, _salta, 'c'), (T_ONDA_CLAVA, ARRODILLADO_CLAVA, 'l'),
                           (3.3, mezcla(ARRODILLADO_CLAVA, {'cabeza': r(-6)}), 'c'), (4.2, G, 'c')])

# --- Sol x3: alza la mano, el sol se forma y lo lanza; tres veces ---
T_SOL_LANZA = (1.0, 2.0, 3.0)
anim('SOL', 3.8, [(0, G, 'c'), (0.55, SOL_ARRIBA, 'c'), (T_SOL_LANZA[0], SOL_LANZA, 'l'), (1.45, SOL_ARRIBA, 'c'),
                  (T_SOL_LANZA[1], SOL_LANZA, 'l'), (2.45, SOL_ARRIBA, 'c'), (T_SOL_LANZA[2], SOL_LANZA, 'l'),
                  (3.8, G, 'c')])

# --- Trompetas: alza la espada al cielo y las estatuas salen del suelo ---
T_TROMPETAS_ALZA = 1.1
_invoca = ik(mezcla({'cabeza': r(-22), 'torso': r(-8)}, CAPA_VIENTO), der=(-16, -128, -6), izq=(42, -64, -18),
             espada=(-0.15, -1, 0.0))
anim('TROMPETAS', 2.6, [(0, G, 'c'), (0.8, _invoca, 'c'), (T_TROMPETAS_ALZA, mezcla(_invoca, {'cabeza': r(-26)}), 'l'),
                        (1.9, _invoca, 'c'), (2.6, G, 'c')])

# --- Fuentes solares: se arrodilla, clava la espada y carga el sol (luego, en bucle) ---
T_FUENTES_CLAVA = 0.8
anim('FUENTES', 1.6, [(0, G, 'c'), (0.45, mezcla(_salta, {'pelvis': P(0, -3, 0)}), 'c'),
                      (T_FUENTES_CLAVA, ARRODILLADO_CLAVA, 'l'), (1.6, ARRODILLADO_SOL, 'c')])
anim('FUENTES_CARGA', 2.0, [(0, ARRODILLADO_SOL, 'c'), (1.0, mezcla(ARRODILLADO_SOL, {'torso': r(4, 2), 'cabeza': r(-34, 3)}), 'c'),
                            (2.0, ARRODILLADO_SOL, 'c')], loop=True)

# --- Ofrenda al Sol: clava la espada, coge al elegido con las dos manos y lo alza ---
T_OFRENDA_SUELTA = 0.7       # suelta la espada: desde aqui se ve la clavada
T_OFRENDA_AGARRA = 1.3       # el jugador ya esta en sus manos
T_OFRENDA_ALZADO = 2.4
anim('OFRENDA', 2.6, [(0, G, 'c'), (0.45, CLAVA_LADO, 'c'), (T_OFRENDA_SUELTA, CLAVA_LADO, 'c'),
                      (1.0, OFRENDA_AGARRA, 'c'), (T_OFRENDA_AGARRA, OFRENDA_AGARRA, 'c'),
                      (T_OFRENDA_ALZADO, OFRENDA_ALZA, 'c'), (2.6, OFRENDA_ALZA, 'c')])
anim('OFRENDA_SOSTIENE', 2.0, [(0, OFRENDA_ALZA, 'c'), (1.0, mezcla(OFRENDA_ALZA, {'torso': r(-8, 2), 'cabeza': r(-37)}), 'c'),
                               (2.0, OFRENDA_ALZA, 'c')], loop=True)

# --- Dios de la Guerra: clava la espada, se envuelve en llamas y lanza soles a tres zonas ---
T_DIOS_SUELTA = 0.6
T_DIOS_MARCA = 1.0
T_DIOS_LANZA = (1.6, 2.6, 3.6)
T_DIOS_RECOGE = 4.5
anim('DIOS', 5.0, [(0, G, 'c'), (0.4, CLAVA_LADO, 'c'), (T_DIOS_SUELTA, CLAVA_LADO, 'c'), (T_DIOS_MARCA, DIOS, 'c'),
                   (T_DIOS_LANZA[0], DIOS_LANZA, 'l'), (2.1, DIOS, 'c'), (T_DIOS_LANZA[1], DIOS_LANZA, 'l'), (3.1, DIOS, 'c'),
                   (T_DIOS_LANZA[2], DIOS_LANZA, 'l'), (4.1, DIOS, 'c'), (T_DIOS_RECOGE, CLAVA_LADO, 'c'), (5.0, G, 'c')])

# --- Grito de guerra: se encoge y ruge al cielo ---
T_GRITO = 0.9
_encoge = ik(mezcla({'torso': r(18), 'cabeza': r(14), 'pelvis': P(0, 4, 0)}), izq=(18, -56, -24), der=(-18, -56, -24),
             espada=(-0.4, 0.5, -0.75))
anim('GRITO', 2.4, [(0, G, 'c'), (0.5, _encoge, 'c'), (T_GRITO, GRITO, 'l'), (1.9, mezcla(GRITO, {'cabeza': r(-30, 3)}), 'c'),
                    (2.4, G, 'c')])

# --- Aturdido: cae de rodilla sobre la espada, la cabeza le cuelga (luego, en bucle) ---
_aturdido = ik(mezcla(RODILLA, {'torso': r(26, 8), 'cabeza': r(30, 12)}), der=(-6, -10, -30), izq=(22, -20, -24),
               espada=(0, 1, 0.05))
anim('ATURDIDO', 1.2, [(0, G, 'c'), (0.3, mezcla(G, {'torso': r(-14), 'cabeza': r(-18)}), 'c'), (1.2, _aturdido, 'c')])
anim('ATURDIDO_BUCLE', 2.4, [(0, _aturdido, 'c'), (1.2, mezcla(_aturdido, {'torso': r(30, -6), 'cabeza': r(36, -14)}), 'c'),
                             (2.4, _aturdido, 'c')], loop=True)

# --- Tambaleo (cambio de fase): el golpe le echa atras, la armadura se raja, ruge ---
_recula = ik(mezcla({'torso': r(-16, -6), 'cabeza': r(-20), 'pelvis': P(0, 3, 4), 'pierna_der': r(24, 0, 8),
                     'espinilla_der': r(30), 'pierna_izq': r(-6)}), izq=(36, -70, 6), der=(-30, -52, 8),
             espada=(-0.4, 0.6, 0.6))
_dobla = ik(mezcla({'torso': r(26), 'cabeza': r(20), 'pelvis': P(0, 8, 0), 'pierna_izq': r(-24), 'espinilla_izq': r(40),
                    'pierna_der': r(10), 'espinilla_der': r(36)}), izq=(16, -34, -26), der=(-20, -30, -30),
            espada=(0, 1, 0.1))
anim('TAMBALEO', 3.0, [(0, G, 'c'), (0.15, _recula, 'l'), (0.7, _recula, 'c'), (1.3, _dobla, 'c'), (2.1, GRITO, 'c'),
                       (2.5, mezcla(GRITO, {'cabeza': r(-30)}), 'c'), (3.0, G, 'c')])
T_TAMBALEO_RUGE = 2.1

# --- Liberacion: cae de rodilla sobre la espada, mira a su sol y le ofrece la mano ---
_li_mira = mezcla(ARRODILLADO_SOL, {'cabeza': r(-36)})
_li_mano = ik(mezcla(RODILLA, {'torso': r(2), 'cabeza': r(-38)}), der=(0, -22, -28), izq=(30, -100, -20),
              espada=(0, 1, 0.05))
anim('LIBERACION', 10.0, [(0, G, 'c'), (0.6, _recula, 'c'), (1.6, ARRODILLADO_CLAVA, 'c'), (3.5, _li_mira, 'c'),
                          (6.0, _li_mano, 'c'), (10.0, _li_mano, 'c')])
T_LIBERACION_ORO = 3.5


# ----------------------------------------------------------------------
#  De poses a canales y a Java (como nerea_juego_anim.py, sin fisica)
# ----------------------------------------------------------------------
NULO = {'rot': (0, 0, 0), 'pos': (0, 0, 0), 'esc': (1, 1, 1)}


def canales(a):
    claves = a['claves']
    usados = {}
    for _, p, _ in claves:
        for pieza, d in p.items():
            for tipo in d:
                if tipo in NULO:
                    usados.setdefault((pieza, tipo), True)
    out = []
    for (pieza, tipo) in usados:
        ks = [(t, tuple(float(x) for x in p.get(pieza, {}).get(tipo, NULO[tipo])), i) for t, p, i in claves]
        if all(np.allclose(k[1], NULO[tipo]) for k in ks):
            continue
        out.append((pieza, tipo, ks))
    return out


def catmull(a, p0, p1, p2, p3):
    return 0.5 * (2 * p1 + (p2 - p0) * a + (2 * p0 - 5 * p1 + 4 * p2 - p3) * a * a + (3 * p1 - p0 - 3 * p2 + p3) * a ** 3)


def muestrear(ks, s, tipo):
    """Como KeyframeAnimation.Entry.apply. Devuelve el OFFSET que se suma."""
    n = len(ks)
    idx = n
    for i, k in enumerate(ks):
        if s <= k[0]:
            idx = i
            break
    prev = max(0, idx - 1)
    nxt = min(n - 1, prev + 1)
    al = min(1.0, max(0.0, (s - ks[prev][0]) / (ks[nxt][0] - ks[prev][0]))) if nxt != prev else 0.0

    def val(i):
        v = np.array(ks[i][1], float)
        return v - 1 if tipo == 'esc' else v
    if ks[nxt][2] == 'l':
        return val(prev) + (val(nxt) - val(prev)) * al
    return catmull(al, val(max(0, prev - 1)), val(prev), val(nxt), val(min(n - 1, nxt + 1)))


def pose_en(nombre, s):
    """La pose del juego (offsets sobre la malla con la guardia horneada) a s segundos."""
    a = ANIMS[nombre]
    if a['loop']:
        s = s % a['dur']
    pose = {}
    for pieza, tipo, ks in canales(a):
        v = muestrear(ks, s, tipo)
        d = pose.setdefault(pieza, {'rot': np.zeros(3), 'pos': np.zeros(3), 'esc': np.ones(3)})
        if tipo == 'esc':
            d['esc'] = d['esc'] + v
        else:
            d[tipo] = d[tipo] + v
    return {k: {'rot': tuple(v['rot']), 'pos': tuple(v['pos']), 'esc': tuple(v['esc'])} for k, v in pose.items()}


def fj(x):
    s = ('%.3f' % x).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s + 'F'


def java_anims():
    L = ['package com.atalaya.client;', '',
         'import net.minecraft.client.animation.AnimationChannel;',
         'import net.minecraft.client.animation.AnimationDefinition;',
         'import net.minecraft.client.animation.Keyframe;',
         'import net.minecraft.client.animation.KeyframeAnimations;', '',
         '/**',
         ' * Las animaciones de Novilis. GENERADO por materiales/generadores/novilis_juego_anim.py:',
         ' * no se editan a mano. El servidor saca de las mismas poses por donde pasan las',
         ' * manos y la espada (NovilisGeometria).',
         ' */',
         'public final class NovilisAnimaciones {', '']
    for nombre in ANIMS:
        L.append(f'    public static final AnimationDefinition {nombre} = {nombre.lower()}();')
    L += ['', '    private NovilisAnimaciones() {', '    }', '',
          '    private static Keyframe rot(float t, float x, float y, float z) {',
          '        return new Keyframe(t, KeyframeAnimations.degreeVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);',
          '    }', '',
          '    private static Keyframe seco(float t, float x, float y, float z) {',
          '        return new Keyframe(t, KeyframeAnimations.degreeVec(x, y, z), AnimationChannel.Interpolations.LINEAR);',
          '    }', '',
          '    private static Keyframe pos(float t, float x, float y, float z) {',
          '        return new Keyframe(t, KeyframeAnimations.posVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);',
          '    }', '',
          '    private static Keyframe posSeco(float t, float x, float y, float z) {',
          '        return new Keyframe(t, KeyframeAnimations.posVec(x, y, z), AnimationChannel.Interpolations.LINEAR);',
          '    }', '',
          '    private static Keyframe esc(float t, float x, float y, float z) {',
          '        return new Keyframe(t, KeyframeAnimations.scaleVec(x, y, z), AnimationChannel.Interpolations.CATMULLROM);',
          '    }', '',
          '    private static Keyframe escSeco(float t, float x, float y, float z) {',
          '        return new Keyframe(t, KeyframeAnimations.scaleVec(x, y, z), AnimationChannel.Interpolations.LINEAR);',
          '    }', '',
          '    private static AnimationChannel giro(Keyframe... k) {',
          '        return new AnimationChannel(AnimationChannel.Targets.ROTATION, k);', '    }', '',
          '    private static AnimationChannel mover(Keyframe... k) {',
          '        return new AnimationChannel(AnimationChannel.Targets.POSITION, k);', '    }', '',
          '    private static AnimationChannel escala(Keyframe... k) {',
          '        return new AnimationChannel(AnimationChannel.Targets.SCALE, k);', '    }', '']
    for nombre, a in ANIMS.items():
        L.append(f'    private static AnimationDefinition {nombre.lower()}() {{')
        L.append(f'        return AnimationDefinition.Builder.withLength({fj(a["dur"])})' + ('.looping()' if a['loop'] else ''))
        for pieza, tipo, ks in canales(a):
            fn = {'rot': ('rot', 'seco', 'giro'), 'pos': ('pos', 'posSeco', 'mover'), 'esc': ('esc', 'escSeco', 'escala')}[tipo]
            partes = []
            for t, v, i in ks:
                x, y, z = v
                if tipo == 'pos':
                    y = -y   # posVec invierte la Y: aqui se escribe hacia abajo
                partes.append(f'{fn[0] if i == "c" else fn[1]}({fj(t)}, {fj(x)}, {fj(y)}, {fj(z)})')
            L.append(f'                .addAnimation("{pieza}", {fn[2]}(' + ',\n                        '.join(partes) + '))')
        L.append('                .build();')
        L.append('    }')
        L.append('')
    L.append('}')
    return '\n'.join(L) + '\n'


# ----------------------------------------------------------------------
#  La guardia horneada en la malla y la espada suelta clavada
# ----------------------------------------------------------------------
def euler_zyx(R):
    """Angulos (x, y, z) en grados de R = Rz Ry Rx (el orden de ModelPart)."""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    a = math.atan2(R[2, 1], R[2, 2])
    c = math.atan2(R[1, 0], R[0, 0])
    return (math.degrees(a), math.degrees(b), math.degrees(c))


def preparar_malla():
    nj.construir()
    # La espada clavada a su derecha: donde la deja CLAVA_LADO (en el espacio de la raiz).
    Ms = fm.matrices(fm.esqueleto('N'), CLAVA_LADO)
    M = Ms['espada']
    R = M[:3, :3] / np.linalg.norm(M[:3, :3], axis=0)
    pivote = M[:3, 3]
    # que la punta quede hundida en el suelo (y=24): baja la espada lo que haga falta
    punta = (M @ np.array([0, fm.PUNTA_ESPADA, 0, 1.0]))[:3]
    pivote = pivote + np.array([0, 24 + 10 - punta[1], 0])
    nj.ESPADA_SUELTA['pose'] = (tuple(pivote), euler_zyx(R))
    nj.construir()
    # La guardia, horneada: la postura de reposo de los brazos y del agarre.
    for k in HORNEADAS:
        g = GUARDIA[k]['rot']
        p = nj.PARTES[k]
        p.rot = tuple(p.rot[i] + g[i] for i in range(3))


preparar_malla()


# ----------------------------------------------------------------------
#  Puntos y tiempos para el servidor
# ----------------------------------------------------------------------
def p_bloques(anim_nombre, s, pieza, local=(0, 0, 0)):
    pose = pose_en(anim_nombre, s) if anim_nombre else {}
    return nj.a_bloques(nj.punto(pose, pieza, local))


PUNTA = (0, fm.PUNTA_ESPADA, 0)


def tick(s):
    return int(round(s * 20))


def java_geometria():
    puntos = {
        'PECHO': p_bloques(None, 0, 'torso', (0, -34, -16)),
        'CABEZA': p_bloques(None, 0, 'cabeza', (0, -10, 0)),
        'HALO': p_bloques(None, 0, 'halo'),
        'PUNTA_ALZA': p_bloques('CASTIGO', T_CASTIGO_MARCA, 'espada', PUNTA),
        'PUNTA_CLAVA': p_bloques('CASTIGO_ONDA', T_ONDA_CLAVA, 'espada', PUNTA),
        'PUNTA_FUENTES': p_bloques('FUENTES', 1.6, 'espada', PUNTA),
        'PECHO_FUENTES': p_bloques('FUENTES_CARGA', 0.0, 'torso', (0, -34, -16)),
        'MANO_SOL': p_bloques('SOL', 0.55, 'mano_izq', (0, 6, 0)),
        'MANO_INVOCA': p_bloques('TROMPETAS', T_TROMPETAS_ALZA, 'espada', PUNTA),
        'OFRENDA_ALZADO_P': tuple(np.mean([p_bloques('OFRENDA_SOSTIENE', 0.0, 'mano_' + l, (0, 6, 0)) for l in ('izq', 'der')], axis=0)),
        'DIOS_MANO_IZQ': p_bloques('DIOS', T_DIOS_MARCA, 'mano_izq', (0, 6, 0)),
        'DIOS_MANO_DER': p_bloques('DIOS', T_DIOS_MARCA, 'mano_der', (0, 6, 0)),
        # Su sol: sobre el halo, un poco atras (el cliente lo pinta ahi; el Castigo saca de el su fuego).
        'SOL_PROPIO': (0.0, 24.5, -1.5),
    }
    for i, t in enumerate(T_TAJOS):
        puntos[f'PUNTA_TAJO_{i + 1}'] = p_bloques('BARRIDO', t, 'espada', PUNTA)
    for i, t in enumerate(T_SOL_LANZA):
        puntos[f'MANO_LANZA_{i + 1}'] = p_bloques('SOL', t, 'mano_izq', (0, 6, 0))
    for i, t in enumerate(T_DIOS_LANZA):
        a = p_bloques('DIOS', t, 'mano_izq', (0, 6, 0))
        b = p_bloques('DIOS', t, 'mano_der', (0, 6, 0))
        puntos[f'DIOS_LANZA_{i + 1}_P'] = tuple((np.array(a) + np.array(b)) / 2)
    # alcance de la hoja: lo lejos que llega la punta en horizontal en cada tajo
    alcance = max(math.hypot(puntos[f'PUNTA_TAJO_{i + 1}'][0], puntos[f'PUNTA_TAJO_{i + 1}'][2]) for i in range(4))
    tiempos = {'DURACION_' + n: tick(a['dur']) for n, a in ANIMS.items()}
    tiempos.update({
        'DESPERTAR_RUGE': tick(T_DESPERTAR_RUGE),
        'TAJO_1': tick(T_TAJOS[0]), 'TAJO_2': tick(T_TAJOS[1]), 'TAJO_3': tick(T_TAJOS[2]), 'TAJO_4': tick(T_TAJOS[3]),
        'CASTIGO_ALZA': tick(T_CASTIGO_ALZA), 'CASTIGO_MARCA': tick(T_CASTIGO_MARCA), 'CASTIGO_RAYO': tick(T_CASTIGO_RAYO),
        'ONDA_CLAVA': tick(T_ONDA_CLAVA),
        'SOL_LANZA_1': tick(T_SOL_LANZA[0]), 'SOL_LANZA_2': tick(T_SOL_LANZA[1]), 'SOL_LANZA_3': tick(T_SOL_LANZA[2]),
        'TROMPETAS_ALZA': tick(T_TROMPETAS_ALZA),
        'FUENTES_CLAVA': tick(T_FUENTES_CLAVA),
        'OFRENDA_SUELTA': tick(T_OFRENDA_SUELTA), 'OFRENDA_AGARRA': tick(T_OFRENDA_AGARRA), 'OFRENDA_ALZADO': tick(T_OFRENDA_ALZADO),
        'DIOS_SUELTA': tick(T_DIOS_SUELTA), 'DIOS_MARCA': tick(T_DIOS_MARCA), 'DIOS_RECOGE': tick(T_DIOS_RECOGE),
        'DIOS_LANZA_1': tick(T_DIOS_LANZA[0]), 'DIOS_LANZA_2': tick(T_DIOS_LANZA[1]), 'DIOS_LANZA_3': tick(T_DIOS_LANZA[2]),
        'GRITO_RUGE': tick(T_GRITO),
        'TAMBALEO_RUGE': tick(T_TAMBALEO_RUGE),
        'LIBERACION_ORO': tick(T_LIBERACION_ORO),
    })
    L = ['package com.atalaya.entity;', '',
         'import net.minecraft.world.phys.Vec3;', '',
         '/**',
         ' * Medidas de Novilis que comparten servidor y cliente. GENERADO por',
         ' * materiales/generadores/novilis_juego_anim.py desde las mismas poses que las',
         ' * animaciones: si una animacion cambia, estos puntos cambian.',
         ' *',
         ' * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,',
         ' * y hacia arriba desde los pies, z hacia delante. NovilisEntity los pasa al',
         ' * mundo con el giro del cuerpo.',
         ' */',
         'public final class NovilisGeometria {', '',
         '    private NovilisGeometria() {', '    }', '',
         f'    /** Lo que alcanza la hoja en el Barrido, desde sus pies (bloques). */',
         f'    public static final double ALCANCE_HOJA = {alcance:.2f};',
         f'    /** Lo que avanza el cuerpo por vuelta de la animacion de andar (bloques). */',
         f'    public static final float ZANCADA = {ZANCADA_PX * nj.ESCALA / 16:.3f}F;', '']
    for k, (x, y, z) in puntos.items():
        L.append(f'    public static final Vec3 {k} = new Vec3({x:.3f}, {y:.3f}, {z:.3f});')
    L.append('')
    for k, v in tiempos.items():
        L.append(f'    public static final int {k} = {v};')
    L.append('')
    # Las manos en la Ofrenda, tick a tick (de cuando lo coge a cuando lo tiene en alto).
    filas = []
    for k in range(tick(T_OFRENDA_AGARRA), tick(ANIMS['OFRENDA']['dur']) + 1):
        a = p_bloques('OFRENDA', k / 20.0, 'mano_izq', (0, 6, 0))
        b = p_bloques('OFRENDA', k / 20.0, 'mano_der', (0, 6, 0))
        x, y, z = (np.array(a) + np.array(b)) / 2
        filas.append(f'{{{x:.2f}F, {y:.2f}F, {z:.2f}F}}')
    L.append('    /** Entre las dos manos en la Ofrenda, desde OFRENDA_AGARRA hasta el final, tick a tick. */')
    L.append('    public static final float[][] MANOS_OFRENDA = {' + ', '.join(filas) + '};')
    L.append('')
    L.append('    /** Donde estan las manos en la Ofrenda a los tantos ticks (de animacion) de empezar. */')
    L.append('    public static Vec3 manosOfrenda(float ticks) {')
    L.append('        float t = ticks - OFRENDA_AGARRA;')
    L.append('        int n = MANOS_OFRENDA.length - 1;')
    L.append('        if (t >= n) {')
    L.append('            return OFRENDA_ALZADO_P;')
    L.append('        }')
    L.append('        t = Math.max(0, t);')
    L.append('        int i = Math.min((int) t, n - 1);')
    L.append('        float k = t - i;')
    L.append('        float[] a = MANOS_OFRENDA[i];')
    L.append('        float[] b = MANOS_OFRENDA[i + 1];')
    L.append('        return new Vec3(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k);')
    L.append('    }')
    L.append('}')
    return '\n'.join(L) + '\n', puntos, tiempos


# ----------------------------------------------------------------------
#  Hojas de control
# ----------------------------------------------------------------------
LUCES = [((-0.5, 0.8, -0.6), (1.0, 0.95, 0.88), 0.85, 'llave'), ((0.7, 0.3, 0.6), (1.0, 0.55, 0.3), 0.5, 'contra')]


def render_pose(pose, tex, emis, uv, alto, W=300, H=400, guinada=-30):
    k = nj.ESCALA / 1.25
    cam = vr.Camara(ojo=(9 * k, 7.0 * k, -16 * k), objetivo=(0, 6.0 * k, 0), fov=50, ancho=W, alto=H)
    lz = vr.Lienzo(W, H)
    M = vr.entidad_a_mundo(0, 0, 0, guinada, nj.ESCALA)
    g = np.zeros((16, 16, 4), np.uint8)
    g[...] = (196, 196, 190, 255)
    g[0, :] = g[:, 0] = (150, 150, 144, 255)
    for i in range(-14, 14):
        for j in range(-14, 14):
            Pq = [(i, 0, j), (i + 1, 0, j), (i + 1, 0, j + 1), (i, 0, j + 1)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [Pq[q] for q in tri], [((0, 0), (1, 0), (1, 1), (0, 1))[q] for q in tri], g,
                             np.array([0.9, 0.9, 0.9]))
    for Pq, UV, _ in nj.quads(pose, uv, alto, M):
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), LUCES, (0.4, 0.38, 0.38))
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[q] for q in tri], [UV[q] for q in tri], tex, luz, emis)
    col = np.clip(lz.color + lz.emis * 0.4, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.93, 0.94, 0.95]) * (1 - a)
    return Image.fromarray((arr * 255).astype(np.uint8))


def pose_hoja(nombre, s):
    pose = pose_en(nombre, s)
    suelta = (nombre == 'OFRENDA' and s >= T_OFRENDA_SUELTA) or nombre == 'OFRENDA_SOSTIENE' or \
             (nombre == 'DIOS' and T_DIOS_SUELTA <= s < T_DIOS_RECOGE)
    if suelta:
        pose['espada'] = {**pose.get('espada', {}), 'oculto': True}
    else:
        pose['espada_suelta'] = {'oculto': True}
    return pose


def hoja(nombre, tiempos, tex, emis, uv, alto, out):
    ims = []
    for s in tiempos:
        im = render_pose(pose_hoja(nombre, s), tex, emis, uv, alto)
        ImageDraw.Draw(im).text((8, 6), f'{nombre} {s:.2f}s', fill=(20, 20, 20))
        ims.append(im)
    W, H = ims[0].size
    h = Image.new('RGB', (W * len(ims), H), (255, 255, 255))
    for i, im in enumerate(ims):
        h.paste(im, (i * W, 0))
    h.save(os.path.join(out, f'novilis_anim_{nombre.lower()}.jpg'), quality=88)


# ----------------------------------------------------------------------
if __name__ == '__main__':
    uv, alto = nj.empaquetar()
    TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/novilis')
    os.makedirs(TEX, exist_ok=True)
    pieles = {}
    if not os.environ.get('NOVILIS_SIN_TEXTURAS'):
        for piel in nj.PIELES:
            base, brillo = nj.pintar_atlas(uv, alto, piel)
            nombre = nj.NOMBRE_PIEL[piel]
            Image.fromarray(base).save(os.path.join(TEX, f'novilis_{nombre}.png'))
            Image.fromarray(brillo).save(os.path.join(TEX, f'novilis_brillo_{nombre}.png'))
            pieles[piel] = (base, brillo)
    CLI = os.path.join(RAIZ, 'src/client/java/com/atalaya/client')
    with open(os.path.join(CLI, 'NovilisMalla.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(nj.java_malla(uv, alto))
    with open(os.path.join(CLI, 'NovilisAnimaciones.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(java_anims())
    geo, puntos, tiempos = java_geometria()
    with open(os.path.join(RAIZ, 'src/main/java/com/atalaya/entity/NovilisGeometria.java'), 'w', encoding='utf-8',
              newline='\n') as fh:
        fh.write(geo)
    print('atlas', nj.ANCHO_ATLAS, 'x', alto, '|', len(nj.ORDEN), 'piezas |', len(ANIMS), 'animaciones')
    for k, v in puntos.items():
        print(f'  {k:16s} izq {v[0]:6.2f}  alto {v[1]:6.2f}  frente {v[2]:6.2f}')

    if RENDERS:
        os.makedirs(RENDERS, exist_ok=True)
        base, brillo = pieles.get(1) or nj.pintar_atlas(uv, alto, 1)
        tex = base
        emis = brillo
        solo = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ANIMS)
        for nombre in solo:
            a = ANIMS[nombre]
            ts = sorted(set([round(t, 2) for t, _, _ in a['claves']]))
            if len(ts) > 9:
                ts = ts[::max(1, len(ts) // 9)]
            hoja(nombre, ts, tex, emis, uv, alto, RENDERS)
            print('hoja', nombre, flush=True)

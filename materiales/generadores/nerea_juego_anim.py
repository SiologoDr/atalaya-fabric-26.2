"""
Animaciones de Nerea, escritas pose a pose y pasadas por fisica.

Cada animacion es una lista de (tiempo, pose, interpolacion). Las poses dicen
lo que el gigante HACE; nerea_fisica.py anade lo que su cuerpo no puede dejar
de hacer: pies plantados por cinematica inversa, inercia en cadenas, corales y
algas, y el retraso de la cabeza y los antebrazos. El resultado se hornea en
keyframes de vanilla (NereaAnimaciones.java) y se pinta en las hojas de control.

Convenciones de las poses (todo SE SUMA a la postura de reposo):
  rot          grados (x, y, z), como degreeVec
  pos          pixeles del modelo con Y hacia ABAJO (al exportar pasa a posVec)
  esc          multiplicadores (x, y, z)
  apoyo_izq/der  {'en': (x, y, z) tobillo en el espacio del modelo,
                  'pie': inclinacion del pie (0 plano, + punta abajo),
                  'giro': giro de la pierna}
Para los brazos se escribe el angulo ABSOLUTO con A(): 0 es colgar recto.

De aqui salen tambien NereaGeometria.java (duraciones, ticks clave y puntos del
cuerpo para el servidor), NereaMalla.java y las texturas.

Uso: python nerea_juego_anim.py <raiz del proyecto> [carpeta de renders] [ANIM,ANIM]
     (con NEREA_SIN_TEXTURAS=1 no reescribe las texturas: solo el codigo)
"""
import math, os, sys, copy
import numpy as np
from PIL import Image
import nerea_juego as nj
import nerea_modelo as nm
import nerea_fisica as nf

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
RENDERS = sys.argv[2] if len(sys.argv) > 2 else None

nj.MOLINO_CADENAS.clear()
nj.construir()


# ----------------------------------------------------------------------
#  Ayudas de pose
# ----------------------------------------------------------------------
def r(x, y=0, z=0):
    return {'rot': (x, y, z)}


def A(pieza, x, y=0, z=0):
    """Angulo absoluto de una pieza (respecto a su padre), pasado a offset."""
    rx, ry, rz = nj.PARTES[pieza].rot
    return {'rot': (x - rx, y - ry, z - rz)}


def P(x, y, z):
    return {'pos': (x, y, z)}


def mezcla(*poses):
    out = {}
    for p in poses:
        for k, v in p.items():
            d = out.setdefault(k, {})
            d.update(copy.deepcopy(v))
    return out


def con(pose, **piezas):
    return mezcla(pose, piezas)


def brazo(lado, bx, bz=0, ax=None, by=0):
    """Atajo: brazo (absoluto) y, si se da, antebrazo (absoluto)."""
    out = {'brazo_' + lado: A('brazo_' + lado, bx, by, bz)}
    if ax is not None:
        out['antebrazo_' + lado] = A('antebrazo_' + lado, ax)
    return out


def apoyo(lado, x, y, z, pie=0.0, giro=0.0):
    return {'apoyo_' + lado: {'en': (x, y, z), 'pie': pie, 'giro': giro}}


SUELO = 20.9                     # altura del tobillo con el pie plano en el suelo
T_EMP = nj.giro_empunar()        # tridente con las puntas hacia donde va el antebrazo
N = {}

# Arrodillado: la rodilla derecha en el suelo, el pie izquierdo plantado delante.
ARRODILLADO = mezcla({'pelvis': P(0, 15, 0), 'torso': r(6)},
                     apoyo('izq', 6.5, SUELO, -15), apoyo('der', -6.5, SUELO, 15, pie=70))
# Paso: un pie en el aire a medio camino.
def en_el_aire(lado, x, z, alto=6.0):
    return apoyo(lado, x, SUELO - alto, z, pie=10)


# ----------------------------------------------------------------------
#  Las animaciones
# ----------------------------------------------------------------------
ANIMS = {}


def tridente_vertical(pose):
    """Offset del tridente para que siga a plomo con esta postura del brazo: la
    muneca lo compensa, como quien lleva un baston pesado."""
    Ms = nj.matrices(pose)
    Rm = Ms['mano_der'][:3, :3]
    Rm = Rm / np.linalg.norm(Rm, axis=0)
    t = Rm.T @ np.array([0, -1.0, 0])
    x = math.degrees(math.asin(max(-1.0, min(1.0, t[2]))))
    z = math.degrees(math.atan2(-t[0], t[1]))
    rx, _, rz = nj.PARTES['tridente'].rot
    return ((x - rx + 180) % 360 - 180, 0.0, (z - rz + 180) % 360 - 180)


def anim(nombre, dur, claves, loop=False, extra=(), apoyos=None, sin_fisica=()):
    # Donde no se dice que hace el tridente, va a plomo en el puno.
    claves = [(t, p if 'tridente' in p else con(p, tridente=r(*tridente_vertical(p))), i) for t, p, i in claves]
    ANIMS[nombre] = {'dur': dur, 'loop': loop, 'claves': claves, 'extra': list(extra),
                     'apoyos': apoyos, 'sin_fisica': set(sin_fisica)}


# --- Reposo: respira, carga el peso y se mece como bajo el agua ---
_rep = mezcla({'torso': r(2.5), 'cabeza': r(-3, 5), 'mandibula': r(3), 'pelvis': P(0, 0.7, 0),
               'hombro_izq': r(0, 0, -2), 'hombro_der': r(0, 0, 2),
               'corona_c1': r(0, 0, 4), 'corona_c2': r(0, 0, -4), 'coral_h1_izq': r(0, 0, 5), 'coral_h1_der': r(0, 0, -5)},
              brazo('izq', -4, -6), brazo('der', -26, 7))
anim('REPOSO', 4.0, [(0, N, 'c'), (2.0, _rep, 'c'), (4.0, N, 'c')], loop=True)


# --- Andar: pisadas de gigante con los pies clavados en el suelo ---
def apoyos_andar(s):
    """El pie de apoyo se queda en el suelo mientras el cuerpo avanza (en el
    espacio del modelo, retrocede); el otro vuela adelante levantando la punta."""
    out = {}
    for lado, desfase, x in (('izq', 0.0, 6.0), ('der', 0.5, -6.0)):
        p = (s / 2.0 + desfase) % 1.0
        zancada = 9.0
        if p < 0.5:
            k = p / 0.5
            z = -zancada + 2 * zancada * k
            y = SUELO
            pie = -8 * (1 - k) + 18 * max(0.0, k - 0.75) / 0.25
        else:
            k = (p - 0.5) / 0.5
            suave = 0.5 - 0.5 * math.cos(math.pi * k)
            z = zancada - 2 * zancada * suave
            y = SUELO - 6.5 * math.sin(math.pi * k)
            pie = 18 * (1 - k) - 8 * k
        out[lado] = ((x, y, z), pie, 0.0)
    return out


_a0 = mezcla({'pelvis': {'pos': (0, 3.6, 0), 'rot': (0, 5, 2)}, 'torso': r(4, -7, -1.5), 'cabeza': r(0, 5)},
             brazo('izq', 12, -6), brazo('der', -30, 7))
_a1 = mezcla({'pelvis': {'pos': (0, 1.8, 0), 'rot': (0, 0, 0)}, 'torso': r(4, 0, 0)},
             brazo('izq', -6, -6), brazo('der', -24, 6))
_a2 = mezcla({'pelvis': {'pos': (0, 3.6, 0), 'rot': (0, -5, -2)}, 'torso': r(4, 7, 1.5), 'cabeza': r(0, -5)},
             brazo('izq', -24, -6), brazo('der', -18, 5))
anim('ANDAR', 2.0, [(0, _a0, 'c'), (0.5, _a1, 'c'), (1.0, _a2, 'c'), (1.5, _a1, 'c'), (2.0, _a0, 'c')],
     loop=True, apoyos=apoyos_andar)

# --- Dormido: arrodillado, la cabeza gacha, apoyado en su baston ---
_dorm = mezcla(ARRODILLADO, {'torso': r(20), 'cuello': r(10), 'cabeza': r(28), 'mandibula': r(4)},
               brazo('izq', -34, -8, -44), brazo('der', -40, 8, -46))
anim('DORMIDO', 6.0, [(0, _dorm, 'c'), (3.0, con(_dorm, torso=r(23), cabeza=r(31), mandibula=r(8)), 'c'),
                      (6.0, _dorm, 'c')], loop=True)

# --- Despertar (la presentacion, 9,5 s). La camara del cliente cuenta con
#     estos tiempos (NereaGeometria.DESPERTAR_*), los mismos en los cuatro jefes:
#       0-2     dormido: respira cada vez mas hondo, da un respingo y se agita
#       2       ABRE: se le encienden los ojos y alza la cabeza
#       3,5     SE_ALZA: tira de las cadenas del pecho temblando hasta que se
#               suelta del fondo (4,3), se apoya en la rodilla y en el tridente,
#               se pone en pie y recoge el pie de delante
#       6       ALZADO: alza el tridente al cielo, la corona y la venera se
#               abren y la capa de algas ondea con el giro
#       7,25    RUGE: se encoge un instante y ruge con todo el cuerpo, los
#               brazos abiertos y la cabeza atras; aguanta temblando
#       8,9-9,5 vuelve al reposo (de ahi sale la de andar) ---
T_DESPERTAR_ABRE = 2.0
T_DESPERTAR_SE_ALZA = 3.5
T_DESPERTAR_ROMPE = 4.3
T_DESPERTAR_ALZADO = 6.0
T_DESPERTAR_RUGE = 7.25
T_DESPERTAR_PISA_DER = 5.45      # el pie derecho sale de la rodilla y pisa
T_DESPERTAR_PISA_IZQ = 5.95      # el izquierdo, que estaba delante, pisa a su lado


def brazo_dir(lado, fuera, arriba, delante, ax=None):
    """Brazo que apunta hacia (fuera, arriba, delante) en el espacio del torso,
    pasado a los angulos absolutos de brazo() (Rz*Rx sobre el brazo colgando)."""
    s = 1 if lado == 'izq' else -1
    d = np.array([s * fuera, -arriba, -delante], float)
    d /= np.linalg.norm(d)
    return brazo(lado, math.degrees(math.asin(d[2])), math.degrees(math.atan2(-d[0], d[1])), ax)


def tridente_a_plomo(nombre, paso=0.05):
    """El tridente a plomo en el puno a lo largo de toda la animacion, no solo
    en las claves: entre dos claves con la muneca muy girada, interpolar los
    angulos lo tumbaria. Se muestrea cada "paso" y se quitan las muestras que
    la interpolacion ya da."""
    a = ANIMS[nombre]
    a['claves'] = [(t, {k: v for k, v in p.items() if k != 'tridente'}, i) for t, p, i in a['claves']]
    muestras = []
    ant = None
    for j in range(int(round(a['dur'] / paso)) + 1):
        s = min(j * paso, a['dur'])
        x, y, z = tridente_vertical(pose_autor(nombre, s))
        if ant is not None:
            x = ant[0] + (x - ant[0] + 180) % 360 - 180
            z = ant[2] + (z - ant[2] + 180) % 360 - 180
        ant = (x, y, z)
        muestras.append((round(s, 3), (round(x, 2), 0.0, round(z, 2))))
    a['extra'].append(('tridente', 'rot', [(t, v, 'c') for t, v in nf.simplificar(muestras, 0.5)]))


def corona_abierta(k):
    """La corona se abre: las puas y los corales se separan k veces mas de su reposo."""
    out = {}
    for n in [f'puas_{i}' for i in range(6)] + ['corona_c1', 'corona_c2', 'corona_c3', 'corona_c4']:
        rx, _, rz = nj.PARTES[n].rot
        out[n] = r(rx * k, 0, rz * k)
    return out


def capa_al_viento(k):
    """La capa de algas se hincha hacia atras y se abre (k veces)."""
    return {f'capa_{i}': r(20 * k, 0, (i - 2) * -4 * k) for i in range(5)}


def apoyos_despertar(s):
    """Arrodillado hasta que se levanta: el pie derecho sale de la rodilla y se
    planta en su sitio de reposo; luego el izquierdo, que estaba delante, da un
    paso atras hasta el suyo. Nada patina."""
    def paso(a, b, t0, t1, alto, pie_a, pie_b):
        u = (s - t0) / (t1 - t0)
        if u <= 0.0:
            return (tuple(a), pie_a, 0.0)
        if u >= 1.0:
            return (tuple(b), pie_b, 0.0)
        k = u * u * (3 - 2 * u)
        p = np.array(a, float) + (np.array(b, float) - np.array(a, float)) * k
        p[1] -= alto * math.sin(math.pi * u)
        return (tuple(p), pie_a + (pie_b - pie_a) * k + 10 * math.sin(math.pi * u), 0.0)
    rep_i, rep_d = nf.tobillo_reposo('izq'), nf.tobillo_reposo('der')
    return {'izq': paso((6.5, SUELO, -15), rep_i, T_DESPERTAR_PISA_IZQ - 0.4, T_DESPERTAR_PISA_IZQ, 5.0, 0.0, 0.0),
            'der': paso((-6.5, SUELO, 15), rep_d, T_DESPERTAR_PISA_DER - 0.45, T_DESPERTAR_PISA_DER, 4.0, 70.0, 0.0)}


# dormido: respira hondo, suelta el aire, un respingo y otra vez mas hondo
_de_inspira = mezcla(_dorm, {'pelvis': P(0, 14.2, 0), 'torso': r(15), 'cuello': r(8), 'cabeza': r(25), 'mandibula': r(9),
                             'hombro_izq': r(0, 0, -6), 'hombro_der': r(0, 0, 6)})
_de_espira = mezcla(_dorm, {'pelvis': P(0, 15.6, 0), 'torso': r(24), 'cuello': r(11), 'cabeza': r(31), 'mandibula': r(12)})
_de_respingo = mezcla(_dorm, {'torso': r(18, 0, 3), 'cuello': r(8), 'cabeza': r(22, -12, -6), 'mandibula': r(3)},
                      brazo('izq', -48, -16, -66))
_de_hondo = mezcla(_dorm, {'pelvis': P(0, 13.6, 0), 'torso': r(13), 'cuello': r(6), 'cabeza': r(20), 'mandibula': r(10),
                           'hombro_izq': r(0, 0, -8), 'hombro_der': r(0, 0, 8)})
# abre los ojos y alza la cabeza: mira al frente, a un lado y al otro
_de_abre = mezcla(_dorm, {'pelvis': P(0, 14, 0), 'torso': r(14), 'cuello': r(2), 'cabeza': r(8), 'mandibula': r(3)})
_de_mira = mezcla(_dorm, {'pelvis': P(0, 14, 0), 'torso': r(13), 'cuello': r(-4), 'cabeza': r(-6, -9), 'mandibula': r(12)})
_de_mira2 = mezcla(_dorm, {'pelvis': P(0, 14, 0), 'torso': r(12), 'cuello': r(-4), 'cabeza': r(-8, 8), 'mandibula': r(7)})


def _de_tira(k, lado):
    """Tira de las cadenas del pecho como quien revienta una cuerda: los codos
    fuera y los punos delante del pecho, que se hincha; los hombros arriba y la
    cabeza gacha. k es la fuerza (0-1) y lado el temblor (+1/-1)."""
    return mezcla(_dorm, {'pelvis': P(0.5 * lado, 14 - 1.5 * k, 0), 'torso': r(20 - 10 * k + lado, 0, 2 * lado),
                          'cuello': r(4 - 4 * k), 'cabeza': r(14 - 10 * k, 0, -2 * lado), 'mandibula': r(1 + 3 * k),
                          'hombro_izq': r(0, 0, -6 - 4 * k), 'hombro_der': r(0, 0, 6 + 4 * k)},
                  brazo_dir('izq', 0.7 + 0.5 * k, -0.25 + 0.25 * k, 0.8 - 0.4 * k, -100 + 10 * k),
                  brazo_dir('der', 0.55 + 0.4 * k, -0.3 + 0.2 * k, 0.8 - 0.3 * k, -90 + 10 * k))


# se suelta: el pecho arriba, el brazo fuera de un tiron y la boca abierta
_de_rompe = mezcla(_dorm, {'pelvis': P(0, 12, 1), 'torso': r(-4), 'cuello': r(-8), 'cabeza': r(-20), 'mandibula': r(30)},
                   brazo_dir('izq', 1.0, 0.45, 0.35, -24), brazo_dir('der', 1.0, 0.0, 0.55, -40))
# se levanta: el peso sobre el pie de delante, la mano en la rodilla y el tridente de baston
_de_empuja = {'pelvis': P(0, 10, -4), 'torso': r(32), 'cuello': r(2), 'cabeza': r(-8), 'mandibula': r(8),
              **brazo('izq', -46, -6, -40), **brazo('der', -30, 22, -50)}
_de_sube1 = {'pelvis': P(0, 7, -4), 'torso': r(26), 'cuello': r(0), 'cabeza': r(-6), 'mandibula': r(6),
             **brazo('izq', -32, -10, -40), **brazo('der', -26, 20, -42)}
_de_sube2 = {'pelvis': P(0, 4.5, -3), 'torso': r(16), 'cabeza': r(-6), 'mandibula': r(6),
             **brazo('izq', -14, -14, -30), **brazo('der', -26, 16, -52)}
_de_sube3 = {'pelvis': P(0, 2, -1), 'torso': r(6), 'cuello': r(-2), 'cabeza': r(-8), 'mandibula': r(6),
             **brazo('izq', -8, -12, -24), **brazo('der', -30, 14, -60)}
# en pie: alza el tridente al cielo, abre la corona y la venera, gira el torso
_de_alzado0 = mezcla({'pelvis': P(0, 0.6, 0), 'torso': r(-2, -6), 'cuello': r(-2), 'cabeza': r(-10, 6), 'mandibula': r(8)},
                     brazo_dir('der', 0.65, 0.45, 0.8, -40), brazo_dir('izq', 0.7, -0.6, 0.4, -24), corona_abierta(0.3))
_de_alzado = mezcla({'pelvis': P(0, 0.3, 0.5), 'torso': r(-8, 10, -2), 'cuello': r(-6), 'cabeza': r(-18, -6), 'mandibula': r(16),
                     'concha': {'esc': (1.15, 1.15, 1.15)}},
                    brazo_dir('der', 0.2, 1.0, 0.12, -8), brazo_dir('izq', 1.0, -0.25, 0.35, -16), corona_abierta(1.0),
                    capa_al_viento(1.0))
_de_alzado2 = mezcla(con(_de_alzado, torso=r(-9, 3, -1), cabeza=r(-20, 5), mandibula=r(20)), capa_al_viento(0.3))
# se encoge (la anticipacion) y RUGE con todo el cuerpo
_de_carga = mezcla({'pelvis': P(0, 3.4, 1.5), 'torso': r(18, -4), 'cuello': r(8), 'cabeza': r(16), 'mandibula': r(4),
                    'concha': {'esc': (0.95, 0.95, 0.95)}},
                   brazo('der', -64, 22, -60), brazo('izq', -30, -16, -90), corona_abierta(0.2))
_de_ruge = mezcla({'pelvis': P(0, 1.2, -1), 'torso': r(-18), 'cuello': r(-5), 'cabeza': r(-9), 'mandibula': r(44),
                   'concha': {'esc': (1.22, 1.22, 1.22)}},
                  brazo_dir('izq', 1.0, 0.4, 0.3, -20), brazo_dir('der', 0.85, 0.8, 0.3, -20), corona_abierta(1.3),
                  capa_al_viento(0.8))
_de_suelta = mezcla({'pelvis': P(0, 1.6, 0), 'torso': r(6), 'cuello': r(2), 'cabeza': r(5), 'mandibula': r(8)},
                    brazo('izq', -10, -14, -24), brazo('der', -30, 12, -66))

_claves = [(0, _dorm, 'c'), (0.55, _de_inspira, 'c'), (1.05, _de_espira, 'c'), (1.3, _de_respingo, 'l'),
           (1.45, con(_dorm, torso=r(21)), 'c'), (1.8, _de_hondo, 'c'),
           (T_DESPERTAR_ABRE, _de_abre, 'c'), (2.5, _de_mira, 'c'), (3.0, _de_mira2, 'c'),
           (T_DESPERTAR_SE_ALZA, _de_tira(0.0, 0), 'c')]
for i in range(1, 7):
    _claves.append((T_DESPERTAR_SE_ALZA + 0.12 * i, _de_tira(i / 6.0, 1 if i % 2 else -1), 'c'))
_claves += [(T_DESPERTAR_ROMPE, _de_rompe, 'l'),
            (4.6, con(_de_rompe, torso=r(-7), cuello=r(-9), cabeza=r(-25), mandibula=r(26)), 'c'),
            (4.95, _de_empuja, 'c'), (5.25, _de_sube1, 'c'), (5.5, _de_sube2, 'c'), (5.8, _de_sube3, 'c'),
            (T_DESPERTAR_ALZADO, _de_alzado0, 'c'), (6.4, _de_alzado, 'c'), (6.8, _de_alzado2, 'c'),
            (7.05, _de_carga, 'c'), (T_DESPERTAR_RUGE, _de_ruge, 'l')]
for i in range(1, 9):
    lado = 1 if i % 2 else -1
    _claves.append((T_DESPERTAR_RUGE + 0.15 * i, con(_de_ruge, torso=r(-18 - 1.5 * lado, 0, 1.5 * lado),
                                                     cabeza=r(-9 - lado, 4 * lado), mandibula=r(44 - 2 * lado),
                                                     pelvis=P(0.5 * lado, 1.2, -1)), 'c'))
_claves += [(8.95, _de_suelta, 'c'), (9.5, N, 'c')]


def _pulso(piezas, *picos):
    """Canales de escala que estan a 1 salvo en los picos (t, escala, sube, baja):
    sube de golpe y baja suave; entre pico y pico, recto (sin ondular)."""
    ks = [(0, (1, 1, 1), 'l')]
    for t, e, sube, baja in picos:
        ks += [(t - sube, (1, 1, 1), 'l'), (t, (e,) * 3, 'l'), (t + baja, (1, 1, 1), 'c')]
    ks.append((9.5, (1, 1, 1), 'l'))
    return [(p, 'esc', ks) for p in piezas]


anim('DESPERTAR', 9.5, _claves, apoyos=apoyos_despertar,
     extra=_pulso(('ojo_izq', 'ojo_der'), (T_DESPERTAR_ABRE + 0.05, 1.7, 0.1, 0.6), (T_DESPERTAR_RUGE + 0.05, 1.45, 0.15, 1.5)) +
     _pulso(('corazon',), (T_DESPERTAR_ABRE + 0.05, 1.35, 0.1, 0.4), (T_DESPERTAR_ROMPE, 1.3, 0.1, 0.4)))
ANIMS['DESPERTAR']['aterriza'] = 9.0

# --- Rompeolas: paso al frente, el tridente gira en la muneca y cae a plomo ---
_ro_carga = mezcla({'pelvis': P(0, 1, 2), 'torso': r(-6, 14), 'tridente': r(*[c * 0.5 for c in T_EMP])},
                   brazo('der', -110, 20, -50), brazo('izq', -10, -30), en_el_aire('izq', 6.5, -5))
_ro_alza = mezcla({'pelvis': P(0, -0.5, 2), 'torso': r(-16, 20), 'cuello': r(-6), 'cabeza': r(-12, -14),
                   'mandibula': r(10), 'tridente': r(*T_EMP)},
                  brazo('der', -175, 12, -20), brazo('izq', -20, -30), apoyo('izq', 7, SUELO, -12))
_ro_golpe = mezcla({'pelvis': P(0, 5, -5), 'torso': r(24, -6), 'cabeza': r(14, 4), 'mandibula': r(28),
                    'tridente': r(*T_EMP)},
                   brazo('der', -54, 5, -50), brazo('izq', -30, -24), apoyo('izq', 7, SUELO, -12))
anim('ROMPEOLAS', 1.05, [
    (0, N, 'c'), (0.18, _ro_carga, 'c'), (0.38, _ro_alza, 'c'), (0.5, _ro_golpe, 'l'),
    (0.72, con(_ro_golpe, pelvis=P(0, 4, -4), torso=r(21, -6)), 'c'),
    (0.84, mezcla({'pelvis': P(0, 2, -1), 'torso': r(6), 'tridente': r(*[c * 0.4 for c in T_EMP])},
                  brazo('der', -40, 8, -60), en_el_aire('izq', 6.5, -6)), 'c'),
    (1.05, N, 'c')])

# --- Remolino: clava el tridente, alza la otra mano y remueve el agua ---
_re_clava = mezcla({'pelvis': P(0, 3, 0), 'torso': r(16), 'cabeza': r(-6)}, brazo('der', -14, 8, -40),
                   brazo('izq', -40, -20, -20))
_re_alza = mezcla(_re_clava, brazo('izq', -160, -18, -10), {'cabeza': r(-22), 'mandibula': r(22)})
_claves = [(0, N, 'c'), (0.3, _re_clava, 'l'), (0.75, _re_alza, 'c')]
_circ = [(-150, -40), (-166, -20), (-150, 0), (-134, -20)]
for k in range(8):
    t = 1.0 + 0.375 * (k + 1)
    x, z = _circ[k % 4]
    _claves.append((t, mezcla(_re_alza, brazo('izq', x, z, -10),
                              {'torso': r(16, 8 if k % 2 else -8), 'pelvis': P(1.2 if k % 2 else -1.2, 3, 0)}), 'c'))
_claves += [(4.1, _re_clava, 'c'), (4.4, N, 'c')]
anim('REMOLINO', 4.4, _claves)

# --- Burbujas: toma aire, el corazon bombea y las escupe de golpe ---
_bu_abre = mezcla({'pelvis': P(0, -0.5, 1.5), 'torso': r(-14), 'cuello': r(-6), 'cabeza': r(-18), 'mandibula': r(10)},
                  brazo('izq', -20, -50, -25), brazo('der', -34, 30, -50))
_bu_suelta = mezcla({'pelvis': P(0, 2.5, -2), 'torso': r(14), 'cabeza': r(8), 'mandibula': r(36)},
                    brazo('izq', -6, -40, -10), brazo('der', -20, 22, -60))
anim('BURBUJAS', 1.1, [(0, N, 'c'), (0.25, _bu_abre, 'c'), (0.4, _bu_suelta, 'l'), (0.65, _bu_suelta, 'c'), (1.1, N, 'c')],
     extra=[('corazon', 'esc', [(0, (1, 1, 1), 'c'), (0.15, (1.2,) * 3, 'c'), (0.3, (1, 1, 1), 'c'),
                                (0.38, (1.55,) * 3, 'l'), (0.45, (0.9,) * 3, 'l'), (0.6, (1.25,) * 3, 'c'),
                                (0.8, (1, 1, 1), 'c'), (1.1, (1, 1, 1), 'c')])])

# --- Molino: brazos abiertos, pasos de lanzador de martillo y dos vueltas ---
POSE_MOLINO = mezcla({'torso': r(-8), 'cabeza': r(10), 'mandibula': r(16), 'pelvis': P(0, 2.5, 0)},
                     brazo('izq', -10, -62, -10), brazo('der', -10, 62, -10))
MOLINO_GIRO = [(0, 0), (0.25, 0), (0.6, -25), (0.8, 12), (2.2, 630), (2.4, 686), (2.7, 712), (3.0, 720)]


def giro_molino(s):
    for (t0, a0), (t1, a1) in zip(MOLINO_GIRO, MOLINO_GIRO[1:]):
        if s <= t1:
            return a0 + (a1 - a0) * (s - t0) / (t1 - t0)
    return MOLINO_GIRO[-1][1]


def apoyos_molino(s):
    """Cada pie se planta cada 90 grados de giro (el derecho, desfasado 45) y
    vuela al siguiente apoyo en el ultimo tramo: pasos cortos y rapidos, como
    quien gira con un peso enorme en las manos."""
    phi = giro_molino(s)
    out = {}
    for lado, adelanto in (('izq', 0.0), ('der', 45.0)):
        rep = nf.tobillo_reposo(lado)
        a = (phi + adelanto) / 90.0
        k = math.floor(a)
        f = a - k
        if phi <= 0.0:
            ang, alto = 0.0, 0.0
        elif f < 0.55:
            ang, alto = k * 90.0, 0.0
        else:
            u = (f - 0.55) / 0.45
            u = 0.5 - 0.5 * math.cos(math.pi * u)
            ang = (k + u) * 90.0
            alto = 5.0 * math.sin(math.pi * u)
        R = nj.Ry(ang * nf.D2R)[:3, :3]
        p = R @ np.array([rep[0], 0.0, rep[2]])
        out[lado] = ((p[0], SUELO - alto, p[2]), 6.0 if alto > 0 else 0.0, ang - phi)
    return out


anim('MOLINO', 3.0, [(0, N, 'c'), (0.25, POSE_MOLINO, 'c'), (2.4, POSE_MOLINO, 'c'), (3.0, N, 'c')],
     extra=[('pelvis', 'rot', [(t, (0, a, 0), 'l') for t, a in MOLINO_GIRO])], apoyos=apoyos_molino)

# --- Arpon: voltea el gancho como un lazo y lo lanza de un latigazo ---
_ar_suelta = mezcla({'torso': r(12, 18), 'cabeza': r(4, -6), 'pelvis': P(0, 2, -3)}, brazo('izq', -78, -4, -4))
_ar_espera = mezcla({'torso': r(6, 10), 'cabeza': r(4, -6), 'pelvis': P(0, 1, -1)}, brazo('izq', -84, -4, -6))
# El lazo: el gancho gira en cono sobre la cabeza, acelerando (unas dos vueltas
# en total), y la mano traza su circulito acompasada con el giro. Luego el
# latigazo hacia delante.
LAZO = [(0.1, 0.0), (0.3, 120.0), (0.5, 330.0), (0.68, 590.0), (0.8, 760.0)]
_claves = [(0, N, 'c')]
for t, phi in LAZO:
    k = math.radians(phi)
    _claves.append((t, mezcla({'torso': r(-8 - 4 * (t / 0.8), -12 - 8 * (t / 0.8)), 'cabeza': r(-8, 10),
                               'pelvis': P(0, 1, 1.5)},
                              brazo('izq', -162 + 7 * math.sin(k), -10 + 7 * math.cos(k), -18)), 'c'))
_claves += [(0.86, _ar_suelta, 'l'), (1.1, _ar_espera, 'c')]
anim('ARPON_LANZAR', 1.1, _claves,
     extra=[('cadena_mano', 'rot', [(0, (0, 0, 0), 'c'), (0.1, (-70, 0, 0), 'c')] +
             [(t, (-70, phi, 0), 'l') for t, phi in LAZO[1:]] + [(1.1, (-70, 760, 0), 'l')])],
     sin_fisica={'cadena_mano'})
anim('ARPON_ESPERA', 1.0, [(0, _ar_espera, 'c'), (0.5, mezcla(_ar_espera, brazo('izq', -81, -6, -8)), 'c'), (1.0, _ar_espera, 'c')],
     loop=True)
# Agarre invertido: las puntas hacia abajo para clavarlo a sus propios pies.
T_ABAJO = (89.1, 0.0, 21.6)
_ar_estoca = mezcla({'tridente': r(*T_ABAJO), 'torso': r(22, -4), 'cabeza': r(20), 'mandibula': r(28),
                     'pelvis': P(0, 4, -2)}, brazo('der', -122, 4, -76), brazo('izq', -30, -30))
anim('ARPON_TIRAR', 1.1, [
    (0, _ar_espera, 'c'),
    # primer tiron: se sienta atras y se lleva la mano al pecho de un golpe
    (0.08, mezcla({'torso': r(-14, 24), 'cabeza': r(-6, -12), 'pelvis': P(0, 2.5, 3), 'mandibula': r(14)},
                  brazo('izq', -12, -14, -100)), 'l'),
    # segundo tiron: el brazo pasa por detras del cuerpo, todo el peso atras
    (0.22, mezcla({'torso': r(-10, 32), 'cabeza': r(-4, -16), 'pelvis': P(0, 2.5, 3.5)},
                  brazo('izq', 22, -22, -60)), 'c'),
    # ya lo tiene a los pies: alza el tridente con las puntas hacia abajo
    (0.42, mezcla({'tridente': r(*T_ABAJO), 'torso': r(-8, -6), 'cabeza': r(4), 'pelvis': P(0, 0.5, 1)},
                  brazo('der', -150, 6, -60), brazo('izq', -20, -30, -40)), 'c'),
    (0.62, _ar_estoca, 'l'), (0.75, _ar_estoca, 'c'),
    (1.1, N, 'c')])

# --- Mirada del Abismo: ruge, se clava, los ojos crecen ---
_mi_ruge = mezcla({'torso': r(-12), 'cabeza': r(-26), 'mandibula': r(36), 'pelvis': P(0, -0.5, 0)},
                  brazo('izq', -20, -40), brazo('der', -40, 35, -40))
_mi_fija = mezcla({'torso': r(8), 'cuello': r(6), 'cabeza': r(4), 'mandibula': r(10), 'pelvis': P(0, 1.5, 0),
                   'ojo_izq': {'esc': (1.6, 1.6, 1.6)}, 'ojo_der': {'esc': (1.6, 1.6, 1.6)}},
                  brazo('izq', -12, -14, -30), brazo('der', -30, 10, -58))
_claves = [(0, N, 'c'), (0.3, _mi_ruge, 'c'), (0.6, _mi_fija, 'c')]
for k in range(1, 9):
    t = 0.6 + 0.5 * k
    _claves.append((t, con(_mi_fija, torso=r(8 + (1 if k % 2 else -1), 0, 0.6 if k % 2 else -0.6),
                           mandibula=r(10 + 4 * (k % 2))), 'c'))
_claves += [(5.1, N, 'c')]
anim('MIRADA', 5.1, _claves)

# --- Aturdido: le han apagado los ojos. Se tambalea cargando el peso ---
_at = mezcla({'cabeza': r(32), 'cuello': r(10), 'torso': r(18, 0, 6), 'pelvis': {'pos': (1.5, 4, 0), 'rot': (0, 0, 4)},
              'mandibula': r(16)}, brazo('izq', 4, -4, -6), brazo('der', -14, 4, -40))
anim('ATURDIDO', 3.5, [(0, N, 'c'), (0.25, _at, 'c'),
                       (0.9, con(_at, torso=r(18, 0, -6), cabeza=r(32, 14), pelvis={'pos': (-1.5, 4, 0), 'rot': (0, 0, -4)}), 'c'),
                       (1.6, _at, 'c'),
                       (2.3, con(_at, torso=r(18, 0, -6), cabeza=r(32, 14), pelvis={'pos': (-1.5, 4, 0), 'rot': (0, 0, -4)}), 'c'),
                       (3.0, con(_at, torso=r(12, 0, 2), cabeza=r(20, -6)), 'c'), (3.5, N, 'c')])

# --- Tambaleo: se le parte una cadena. Recula un paso, se dobla, ruge ---
_ta_golpe = mezcla({'torso': r(-20, 0, 6), 'cabeza': r(-26), 'mandibula': r(30), 'pelvis': P(0, 0, 3)},
                   brazo('izq', -40, -45), brazo('der', -50, 30, -30), en_el_aire('der', -6.5, 5))
_ta_dobla = mezcla({'pelvis': P(0, 7, 4), 'torso': r(26, 0, -6), 'cabeza': r(14), 'mandibula': r(12)},
                   brazo('izq', -70, 20, -80), brazo('der', -20, 8, -50), apoyo('der', -7, SUELO, 10))
_ta_ruge = mezcla({'torso': r(-14), 'cabeza': r(-28), 'mandibula': r(36), 'pelvis': P(0, 1, 1)},
                  brazo('izq', -30, -50), brazo('der', -50, 45, -30), apoyo('der', -7, SUELO, 10))
anim('TAMBALEO', 3.0, [(0, N, 'c'), (0.12, _ta_golpe, 'l'), (0.45, mezcla(_ta_golpe, apoyo('der', -7, SUELO, 10)), 'c'),
                       (0.8, _ta_dobla, 'c'), (1.3, con(_ta_dobla, torso=r(29, 0, -6)), 'c'), (1.7, _ta_dobla, 'c'),
                       (2.1, _ta_ruge, 'c'), (2.4, mezcla(_ta_ruge, en_el_aire('der', -6.5, 5)), 'c'), (3.0, N, 'c')])

# --- Agotado: le fallan las piernas, cae de rodilla, la mano al suelo ---
_ag = mezcla(ARRODILLADO, {'torso': r(16), 'cabeza': r(18), 'mandibula': r(14)},
             brazo('izq', -44, -12, -50), brazo('der', -36, 8, -40))
anim('AGOTADO', 4.5, [(0, N, 'c'),
                      (0.25, mezcla({'pelvis': P(0, 6, 1), 'torso': r(20)}, en_el_aire('der', -6.5, 6)), 'c'),
                      (0.6, _ag, 'c'), (1.5, con(_ag, torso=r(20)), 'c'), (2.4, _ag, 'c'), (3.3, con(_ag, torso=r(20)), 'c'),
                      (3.8, mezcla(_ag, {'pelvis': P(0, 9, -1), 'torso': r(26)}), 'c'),
                      (4.15, mezcla({'pelvis': P(0, 3, 0), 'torso': r(10)}, en_el_aire('der', -6, 6)), 'c'),
                      (4.5, N, 'c')])

# --- Liberacion (su "muerte"): grita, cae de rodillas, mira arriba y ofrece el tridente ---
_li_grito = mezcla({'torso': r(-18), 'cabeza': r(-30), 'mandibula': r(34), 'pelvis': P(0, 0, 2)},
                   brazo('izq', -50, -50), brazo('der', -60, 40, -30))
_li_cae = mezcla(ARRODILLADO, {'torso': r(20), 'cabeza': r(30)}, brazo('izq', -12, -6, -20), brazo('der', -30, 8, -50))
_li_mira = mezcla(ARRODILLADO, {'torso': r(-2), 'cabeza': r(-18), 'mandibula': r(4)},
                  brazo('izq', -30, -30, -30), brazo('der', -40, 30, -40))
_li_ofrece = mezcla(ARRODILLADO, {'torso': r(16), 'cabeza': r(24)},
                    brazo('izq', -20, -8, -50), brazo('der', -64, 4, -36))
anim('LIBERACION', 10.0, [(0, N, 'c'), (0.3, _li_grito, 'l'), (1.0, con(_li_grito, cabeza=r(-33)), 'c'),
                          (1.5, mezcla({'pelvis': P(0, 7, 1), 'torso': r(20)}, en_el_aire('der', -6.5, 7)), 'c'),
                          (2.3, _li_cae, 'c'), (3.0, _li_cae, 'c'), (4.4, _li_mira, 'c'), (6.0, _li_mira, 'c'),
                          (7.2, _li_ofrece, 'c'), (10.0, _li_ofrece, 'c')])


# --- Geiser del Abismo (remake): alza el tridente con las dos manos y clava el
#     cuento en el suelo; bajo los pies de los jugadores se abre el abismo ---
T_GEISER = 0.55
_ge_alza = mezcla({'pelvis': P(0, -1, 1), 'torso': r(-7), 'cuello': r(-3), 'cabeza': r(-8), 'mandibula': r(18)},
                  brazo('der', -150, 10, -24), brazo('izq', -140, -16, -30), en_el_aire('izq', 6.5, -4))
_ge_clava = mezcla({'pelvis': P(0, 6, -2), 'torso': r(22), 'cabeza': r(10), 'mandibula': r(30)},
                   brazo('der', -36, 8, -46), brazo('izq', -40, -10, -56), apoyo('izq', 7, SUELO, -10))
anim('GEISER', 1.6, [(0, N, 'c'), (0.32, _ge_alza, 'c'), (T_GEISER, _ge_clava, 'l'), (0.8, _ge_clava, 'c'),
                     (1.15, con(_ge_clava, torso=r(16), pelvis=P(0, 4, -1)), 'c'), (1.6, N, 'c')])

# --- La Gran Marea (remake): alza el tridente al cielo con los brazos abiertos
#     y el mar se retira; al bajarlo de un tajo, la ola sale hacia delante ---
T_MAREA = 2.0
_ma_alza = mezcla({'pelvis': P(0, -1.5, 1), 'torso': r(-9), 'cuello': r(-4), 'cabeza': r(-14), 'mandibula': r(32)},
                  brazo('der', -172, 8, -8), brazo('izq', -120, -60, -20))
_ma_baja = mezcla({'pelvis': P(0, 6, -5), 'torso': r(26, -4), 'cabeza': r(12), 'mandibula': r(36),
                   'tridente': r(*T_EMP)},
                  brazo('der', -58, 6, -44), brazo('izq', -30, -40, -20), apoyo('izq', 7, SUELO, -13))
_claves = [(0, N, 'c'), (0.5, _ma_alza, 'c')]
for k in range(1, 5):
    _claves.append((0.5 + 0.3 * k, con(_ma_alza, torso=r(-9 + (1.5 if k % 2 else -1.5), 0, 0.8 if k % 2 else -0.8),
                                        mandibula=r(30 + 4 * (k % 2))), 'c'))
_claves += [(1.78, mezcla(_ma_alza, {'torso': r(-12)}, brazo('der', -180, 8, -4)), 'c'), (T_MAREA, _ma_baja, 'l'),
            (2.4, _ma_baja, 'c'), (3.0, N, 'c')]
anim('MAREA', 3.0, _claves)


# ----------------------------------------------------------------------
#  De poses a canales
# ----------------------------------------------------------------------
NULO = {'rot': (0, 0, 0), 'pos': (0, 0, 0), 'esc': (1, 1, 1)}


def canales_autor(a):
    claves = a['claves']
    usados = {}
    for _, p, _ in claves:
        for pieza, d in p.items():
            if pieza.startswith('apoyo_'):
                continue
            for tipo in d:
                if tipo in NULO:
                    usados.setdefault((pieza, tipo), True)
    out = []
    for (pieza, tipo) in usados:
        ks = [(t, tuple(p.get(pieza, {}).get(tipo, NULO[tipo])), i) for t, p, i in claves]
        if all(k[1] == NULO[tipo] for k in ks):
            continue
        out.append((pieza, tipo, ks))
    return out + list(a['extra'])


def canales(a):
    return a.get('horneado') or canales_autor(a)


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
    if nxt != prev:
        al = min(1.0, max(0.0, (s - ks[prev][0]) / (ks[nxt][0] - ks[prev][0])))
    else:
        al = 0.0

    def val(i):
        v = np.array(ks[i][1], float)
        return v - 1 if tipo == 'esc' else v
    if ks[nxt][2] == 'l':
        return val(prev) + (val(nxt) - val(prev)) * al
    return catmull(al, val(max(0, prev - 1)), val(prev), val(nxt), val(min(n - 1, nxt + 1)))


def _pose(chs, s):
    pose = {}
    for pieza, tipo, ks in chs:
        v = muestrear(ks, s, tipo)
        d = pose.setdefault(pieza, {'rot': np.zeros(3), 'pos': np.zeros(3), 'esc': np.ones(3)})
        if tipo == 'esc':
            d['esc'] = d['esc'] + v
        else:
            d[tipo] = d[tipo] + v
    return {k: {'rot': tuple(v['rot']), 'pos': tuple(v['pos']), 'esc': tuple(v['esc'])} for k, v in pose.items()}


def pose_autor(nombre, s):
    a = ANIMS[nombre]
    if a['loop']:
        s = s % a['dur']
    return _pose(canales_autor(a), s)


def pose_en(nombre, s):
    """La pose final (con fisica) a s segundos."""
    a = ANIMS[nombre]
    if a['loop']:
        s = s % a['dur']
    return _pose(canales(a), s)


# ----------------------------------------------------------------------
#  Las cadenas del molino: de la mano (pose del molino) al suelo a 10 bloques
# ----------------------------------------------------------------------
def preparar_molino():
    nj.MOLINO_CADENAS.clear()
    nj.construir()
    pose = pose_autor('MOLINO', 0.6)
    pose['pelvis'] = {'rot': (0, 0, 0), 'pos': pose.get('pelvis', {}).get('pos', (0, 0, 0))}
    Ms = nj.matrices(pose)
    inv = np.linalg.inv(Ms['pelvis'])
    radio = 14.0 / (nj.ESCALA / 16)               # 14 bloques: arena de 30-40 jugadores
    for n, s in (('izq', 1), ('der', -1)):
        mano = (Ms['mano_' + n] @ np.array([0, 4, 0, 1.0]))[:3]
        suelo = np.array([s * radio, 24 - 3.5, mano[2]])
        a = (inv @ np.array([*mano, 1.0]))[:3]
        b = (inv @ np.array([*suelo, 1.0]))[:3]
        nj.MOLINO_CADENAS[n] = (tuple(a), tuple(b))
    nj.construir()


preparar_molino()
tridente_a_plomo('DESPERTAR')


# ----------------------------------------------------------------------
#  El pase de fisica
# ----------------------------------------------------------------------
def aterrizar(ks, desde, dur, paso=0.05):
    """Lleva un canal horneado a 0 entre "desde" y el final, suave: lo que
    aun se mueve por inercia (la cadena con el ancla, las algas) acaba quieto
    en su reposo y la animacion empalma sin salto con la siguiente."""
    antes = [k for k in ks if k[0] < desde - 1e-6]
    n = int(round((dur - desde) / paso))
    fin = []
    for j in range(n + 1):
        s = desde + (dur - desde) * j / n
        v = muestrear(ks, s, 'rot')
        u = j / n
        w = 1.0 - u * u * (3 - 2 * u)
        fin.append((round(s, 3), tuple(round(float(c) * w, 2) for c in v), 'c'))
    return antes + fin


def hornear_una(nombre):
    a = ANIMS[nombre]
    nuevos, sustituye = nf.hornear(nombre, a, pose_autor, muestrear, a['apoyos'], a['sin_fisica'])
    if a.get('aterriza'):
        nuevos = [(p, t, aterrizar(ks, a['aterriza'], a['dur'])) for p, t, ks in nuevos]
    quedan = [c for c in canales_autor(a) if not (c[0] in sustituye and c[1] == 'rot')]
    a['horneado'] = quedan + nuevos


def hornear_todo():
    for nombre in ANIMS:
        hornear_una(nombre)


if not os.environ.get('NEREA_SIN_FISICA'):
    hornear_todo()


# ----------------------------------------------------------------------
#  Exportar animaciones (un metodo por animacion: cada uno por debajo del
#  limite de 64 KB de bytecode de Java)
# ----------------------------------------------------------------------
def fj(x):
    s = ('%.3f' % x).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s + 'F'


# Lo que cabe en un metodo de Java (64 KB de bytecode: unos 20 bytes por keyframe)
MAX_CLAVES_METODO = 1400


def java_anims():
    L = ['package com.atalaya.client;', '',
         'import net.minecraft.client.animation.AnimationChannel;',
         'import net.minecraft.client.animation.AnimationDefinition;',
         'import net.minecraft.client.animation.Keyframe;',
         'import net.minecraft.client.animation.KeyframeAnimations;', '',
         '/**',
         ' * Las animaciones de Nerea. GENERADO por materiales/generadores/nerea_juego_anim.py',
         ' * (poses) y nerea_fisica.py (pies plantados, inercia y retraso horneados). No se',
         ' * editan a mano: el servidor saca de las mismas poses por donde pasan las manos,',
         ' * los ojos y el tridente (NereaGeometria).',
         ' */',
         'public final class NereaAnimaciones {', '']
    for nombre in ANIMS:
        L.append(f'    public static final AnimationDefinition {nombre} = {nombre.lower()}();')
    L += ['', '    private NereaAnimaciones() {', '    }', '',
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
        lineas = []
        for pieza, tipo, ks in canales(a):
            fn = {'rot': ('rot', 'seco', 'giro'), 'pos': ('pos', 'posSeco', 'mover'), 'esc': ('esc', 'escSeco', 'escala')}[tipo]
            partes = []
            for t, v, i in ks:
                x, y, z = v
                if tipo == 'pos':
                    y = -y   # posVec invierte la Y: aqui se escribe hacia abajo
                partes.append(f'{fn[0] if i == "c" else fn[1]}({fj(t)}, {fj(x)}, {fj(y)}, {fj(z)})')
            lineas.append((len(ks), f'                .addAnimation("{pieza}", {fn[2]}(' + ',\n                        '.join(partes) + '))'))
        if sum(n for n, _ in lineas) <= MAX_CLAVES_METODO:
            L.append(f'    private static AnimationDefinition {nombre.lower()}() {{')
            L.append(f'        return AnimationDefinition.Builder.withLength({fj(a["dur"])})' + ('.looping()' if a['loop'] else ''))
            L += [x for _, x in lineas]
            L.append('                .build();')
            L.append('    }')
            L.append('')
            continue
        # Demasiados keyframes para un metodo (64 KB de bytecode): los canales
        # se reparten en varios que van llenando el mismo Builder.
        tandas = [[]]
        for n, x in lineas:
            if tandas[-1] and sum(m for m, _ in tandas[-1]) + n > MAX_CLAVES_METODO:
                tandas.append([])
            tandas[-1].append((n, x))
        L.append(f'    private static AnimationDefinition {nombre.lower()}() {{')
        L.append(f'        AnimationDefinition.Builder b = AnimationDefinition.Builder.withLength({fj(a["dur"])})'
                 + ('.looping()' if a['loop'] else '') + ';')
        for k in range(len(tandas)):
            L.append(f'        {nombre.lower()}{k + 1}(b);')
        L.append('        return b.build();')
        L.append('    }')
        L.append('')
        for k, tanda in enumerate(tandas):
            L.append(f'    private static void {nombre.lower()}{k + 1}(AnimationDefinition.Builder b) {{')
            L.append('        b' + '\n'.join(x for _, x in tanda).lstrip() + ';')
            L.append('    }')
            L.append('')
    L.append('}')
    return '\n'.join(L) + '\n'


# ----------------------------------------------------------------------
#  Puntos y tiempos para el servidor
# ----------------------------------------------------------------------
def p_bloques(anim_nombre, s, pieza, local=(0, 0, 0)):
    pose = pose_en(anim_nombre, s) if anim_nombre else {}
    return nj.a_bloques(nj.punto(pose, pieza, local))


def punta_tridente(anim_nombre, s):
    # la punta central del tridente largo del remake
    return p_bloques(anim_nombre, s, 'tridente', (0, 90, 0))


T_IMPACTO = 0.5
T_ESTOCADA = 0.62


def java_geometria():
    puntos = {
        'OJO_IZQ': p_bloques(None, 0, 'ojo_izq'),
        'OJO_DER': p_bloques(None, 0, 'ojo_der'),
        'OJO_IZQ_MIRADA': p_bloques('MIRADA', 2.0, 'ojo_izq'),
        'OJO_DER_MIRADA': p_bloques('MIRADA', 2.0, 'ojo_der'),
        'CORAZON': p_bloques(None, 0, 'corazon'),
        'CORAZON_BURBUJAS': p_bloques('BURBUJAS', 0.42, 'corazon'),
        'CORAZON_AGOTADO': p_bloques('AGOTADO', 2.4, 'corazon'),
        'PECHO': p_bloques(None, 0, 'torso', (0, -17, -9)),
        'BOCA': p_bloques(None, 0, 'mandibula', (0, 2, -9)),
        'MANO_IZQ_LANZAR': p_bloques('ARPON_LANZAR', 0.84, 'mano_izq', (0, 4, 0)),
        'MANO_IZQ_ESPERA': p_bloques('ARPON_ESPERA', 0, 'mano_izq', (0, 4, 0)),
        'MANO_IZQ_REMOLINO': p_bloques('REMOLINO', 2.0, 'mano_izq', (0, 4, 0)),
        'PUNTA_ROMPEOLAS': punta_tridente('ROMPEOLAS', T_IMPACTO),
        'PUNTA_ESTOCADA': punta_tridente('ARPON_TIRAR', T_ESTOCADA),
        'PUNTA_REMOLINO': p_bloques('REMOLINO', 1.0, 'tridente', (0, -30, 0)),
        'PUNTA_GEISER': p_bloques('GEISER', T_GEISER, 'tridente', (0, -30, 0)),
        'PUNTA_MAREA': punta_tridente('MAREA', T_MAREA),
    }

    def tick(s):
        return int(round(s * 20))
    tiempos = {
        'DURACION_DESPERTAR': tick(ANIMS['DESPERTAR']['dur']),
        'DESPERTAR_ABRE': tick(T_DESPERTAR_ABRE), 'DESPERTAR_SE_ALZA': tick(T_DESPERTAR_SE_ALZA),
        'DESPERTAR_ROMPE': tick(T_DESPERTAR_ROMPE), 'DESPERTAR_ALZADO': tick(T_DESPERTAR_ALZADO),
        'DESPERTAR_RUGE': tick(T_DESPERTAR_RUGE), 'DESPERTAR_PISA_DER': tick(T_DESPERTAR_PISA_DER),
        'DESPERTAR_PISA_IZQ': tick(T_DESPERTAR_PISA_IZQ),
        'DURACION_ROMPEOLAS': tick(ANIMS['ROMPEOLAS']['dur']), 'IMPACTO_ROMPEOLAS': tick(T_IMPACTO),
        'DURACION_REMOLINO': tick(ANIMS['REMOLINO']['dur']), 'REMOLINO_TIRA': tick(1.0), 'REMOLINO_SUELTA': tick(4.0),
        'DURACION_BURBUJAS': tick(ANIMS['BURBUJAS']['dur']), 'BURBUJAS_SUELTA': tick(0.38),
        'DURACION_MOLINO': tick(ANIMS['MOLINO']['dur']), 'MOLINO_VISIBLE': tick(0.25), 'MOLINO_GOLPEA': tick(0.6),
        'MOLINO_PARA': tick(2.4),
        'DURACION_ARPON_LANZAR': tick(ANIMS['ARPON_LANZAR']['dur']), 'ARPON_SUELTA': tick(0.84),
        'DURACION_ARPON_TIRAR': tick(ANIMS['ARPON_TIRAR']['dur']), 'ARPON_ARRASTRE': tick(0.38), 'ARPON_ESTOCADA': tick(T_ESTOCADA),
        'DURACION_MIRADA': tick(ANIMS['MIRADA']['dur']), 'MIRADA_FIJA': tick(0.6),
        'DURACION_ATURDIDO': tick(ANIMS['ATURDIDO']['dur']),
        'DURACION_TAMBALEO': tick(ANIMS['TAMBALEO']['dur']),
        'DURACION_AGOTADO': tick(ANIMS['AGOTADO']['dur']),
        'DURACION_LIBERACION': tick(ANIMS['LIBERACION']['dur']), 'LIBERACION_OJOS_ORO': tick(3.5),
        'DURACION_GEISER': tick(ANIMS['GEISER']['dur']), 'GEISER_GOLPE': tick(T_GEISER),
        'DURACION_MAREA': tick(ANIMS['MAREA']['dur']), 'MAREA_LANZA': tick(T_MAREA),
    }
    L = ['package com.atalaya.entity;', '',
         'import net.minecraft.world.phys.Vec3;', '',
         '/**',
         ' * Medidas de Nerea que comparten servidor y cliente. GENERADO por',
         ' * materiales/generadores/nerea_juego_anim.py desde las mismas poses que las',
         ' * animaciones (ya con la fisica): si una animacion cambia, estos puntos cambian.',
         ' *',
         ' * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,',
         ' * y hacia arriba desde los pies, z hacia delante. NereaEntity los pasa al',
         ' * mundo con el giro del cuerpo.',
         ' */',
         'public final class NereaGeometria {', '',
         '    private NereaGeometria() {', '    }', '']
    for k, (x, y, z) in puntos.items():
        L.append(f'    public static final Vec3 {k} = new Vec3({x:.3f}, {y:.3f}, {z:.3f});')
    L.append('')
    for k, v in tiempos.items():
        L.append(f'    public static final int {k} = {v};')
    L.append('')
    L.append('    /** La mano izquierda (donde nace la cadena del gancho), tick a tick, en el espacio del cuerpo. */')
    for nombre in ('ARPON_LANZAR', 'ARPON_ESPERA', 'ARPON_TIRAR'):
        n_ticks = int(round(ANIMS[nombre]['dur'] * 20))
        filas = []
        for k in range(n_ticks + 1):
            x, y, z = p_bloques(nombre, k / 20.0, 'mano_izq', (0, 5, 0))
            filas.append(f'{{{x:.2f}F, {y:.2f}F, {z:.2f}F}}')
        L.append(f'    public static final float[][] MANO_{nombre} = {{' + ', '.join(filas) + '};')
    L.append('')
    L.append('    /** Donde esta la mano del gancho a los tantos ticks de un estado del arpon. */')
    L.append('    public static Vec3 manoArpon(float[][] tabla, float tick, boolean bucle) {')
    L.append('        int n = tabla.length - 1;')
    L.append('        float t = bucle ? tick % n : Math.max(0, Math.min(tick, n));')
    L.append('        int i = Math.min((int) t, n - 1);')
    L.append('        float k = t - i;')
    L.append('        float[] a = tabla[i];')
    L.append('        float[] b = tabla[i + 1];')
    L.append('        return new Vec3(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k);')
    L.append('    }')
    L.append('')
    L.append('    /** El giro de la pelvis en el molino (grados que se suman al rumbo), por tramos lineales. */')
    L.append('    public static final float[] MOLINO_GIRO_T = {' + ', '.join(fj(t * 20) for t, _ in MOLINO_GIRO) + '};')
    L.append('    public static final float[] MOLINO_GIRO_ANG = {' + ', '.join(fj(a) for _, a in MOLINO_GIRO) + '};')
    L.append('')
    L.append('    /** Grados de giro del molino a los tantos ticks de empezar. */')
    L.append('    public static float giroMolino(float tick) {')
    L.append('        float[] t = MOLINO_GIRO_T;')
    L.append('        float[] a = MOLINO_GIRO_ANG;')
    L.append('        if (tick <= t[0]) {')
    L.append('            return a[0];')
    L.append('        }')
    L.append('        for (int i = 1; i < t.length; i++) {')
    L.append('            if (tick <= t[i]) {')
    L.append('                float k = (tick - t[i - 1]) / (t[i] - t[i - 1]);')
    L.append('                return a[i - 1] + (a[i] - a[i - 1]) * k;')
    L.append('            }')
    L.append('        }')
    L.append('        return a[a.length - 1];')
    L.append('    }')
    # La cara (entre los ojos) y el pecho en el despertar, cada 5 ticks: la
    # camara de la presentacion los sigue mientras se levanta.
    for nombre, pieza, local, que in (('CABEZA', 'cabeza', (0, -6, -7.6), 'La cara (entre los ojos)'),
                                      ('PECHO', 'torso', (0, -17, -9), 'El pecho')):
        filas = []
        for k in range(0, tick(ANIMS['DESPERTAR']['dur']) + 1, 5):
            x, y, z = p_bloques('DESPERTAR', k / 20.0, pieza, local)
            filas.append(f'{{{x:.2f}F, {y:.2f}F, {z:.2f}F}}')
        L.append('')
        L.append(f'    /** {que} en el despertar, cada 5 ticks (bloques; la camara de la presentacion lo sigue). */')
        L.append(f'    public static final float[][] {nombre}_DESPERTAR = {{' + ', '.join(filas) + '};')
    for nombre, que in (('cabeza', 'la cara'), ('pecho', 'el pecho')):
        L.append('')
        L.append(f'    /** Donde esta {que} a los tantos ticks del despertar. */')
        L.append(f'    public static Vec3 {nombre}Despertar(float ticks) {{')
        L.append(f'        return tabla({nombre.upper()}_DESPERTAR, ticks / 5.0F);')
        L.append('    }')
    L.append('')
    L.append('    private static Vec3 tabla(float[][] t, float f) {')
    L.append('        int n = t.length - 1;')
    L.append('        f = Math.max(0.0F, Math.min(n, f));')
    L.append('        int i = Math.min((int) f, n - 1);')
    L.append('        float k = f - i;')
    L.append('        return new Vec3(t[i][0] + (t[i + 1][0] - t[i][0]) * k, t[i][1] + (t[i + 1][1] - t[i][1]) * k,')
    L.append('                t[i][2] + (t[i + 1][2] - t[i][2]) * k);')
    L.append('    }')
    L.append('}')
    return '\n'.join(L) + '\n', puntos, tiempos


# ----------------------------------------------------------------------
#  Hojas de control
# ----------------------------------------------------------------------
LUCES = [((-0.5, 0.8, -0.6), (1.0, 0.97, 0.9), 0.85, 'llave'), ((0.7, 0.3, 0.6), (0.4, 0.8, 0.9), 0.5, 'contra')]


def render_pose(pose, tex, emis, uv, alto, W=300, H=360, guinada=-30, ojo=(9, 6.0, -13), objetivo=(0, 4.6, 0), fov=50,
                suelo=True):
    # la camara de las hojas se penso para 10 bloques: crece con la escala del remake
    k = nj.ESCALA / 1.6
    ojo = tuple(c * k for c in ojo)
    objetivo = tuple(c * k for c in objetivo)
    cam = nm.vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W, alto=H)
    lz = nm.vr.Lienzo(W, H)
    M = nm.vr.entidad_a_mundo(0, 0, 0, guinada, nj.ESCALA)
    qs = nj.quads(pose, uv, alto, M)
    if suelo:
        g = np.zeros((16, 16, 4), np.uint8)
        g[...] = (196, 204, 198, 255)
        g[0, :] = g[:, 0] = (150, 160, 154, 255)
        for i in range(-12, 12):
            for j in range(-12, 12):
                Pq = [(i, 0, j), (i + 1, 0, j), (i + 1, 0, j + 1), (i, 0, j + 1)]
                for tri in ((0, 1, 2), (0, 2, 3)):
                    lz.triangulo(cam, [Pq[k] for k in tri], [((0, 0), (1, 0), (1, 1), (0, 1))[k] for k in tri], g,
                                 np.array([0.9, 0.9, 0.9]))
    for Pq, UV, _ in qs:
        n = nm.vr.normal(Pq)
        luz = nm.vr.iluminar(n, cam, np.mean(Pq, axis=0), LUCES, (0.42, 0.44, 0.48))
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UV[k] for k in tri], tex, luz, emis)
    col = np.clip(lz.color + lz.emis * 0.35, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.93, 0.95, 0.96]) * (1 - a)
    return Image.fromarray((arr * 255).astype(np.uint8))


def pose_hoja(nombre, s):
    pose = pose_en(nombre, s)
    if nombre != 'MOLINO' or s < 0.25:
        pose['molino_izq'] = {'oculto': True}
        pose['molino_der'] = {'oculto': True}
    if nombre == 'MOLINO' and s >= 0.25:
        pose['cadena_mano'] = {**pose.get('cadena_mano', {}), 'oculto': True}
    if (nombre == 'ARPON_LANZAR' and s >= 0.84) or nombre == 'ARPON_ESPERA' or (nombre == 'ARPON_TIRAR' and s < 0.42):
        pose['cadena_mano'] = {**pose.get('cadena_mano', {}), 'oculto': True}
    return pose


def hoja(nombre, tiempos, tex, emis, uv, alto, out, **kw):
    from PIL import ImageDraw
    ims = []
    for s in tiempos:
        im = render_pose(pose_hoja(nombre, s), tex, emis, uv, alto, **kw)
        ImageDraw.Draw(im).text((8, 6), f'{nombre} {s:.2f}s', fill=(20, 40, 50))
        ims.append(im)
    W, H = ims[0].size
    hojai = Image.new('RGB', (W * len(ims), H), (255, 255, 255))
    for i, im in enumerate(ims):
        hojai.paste(im, (i * W, 0))
    hojai.save(os.path.join(out, f'nerea_anim_{nombre.lower()}.png'))


# ----------------------------------------------------------------------
if __name__ == '__main__':
    uv, alto = nj.empaquetar()
    TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/nerea')
    # NEREA_SIN_TEXTURAS=1: solo el codigo; las texturas no se tocan (la piel de
    # la fase I se pinta igual, para las hojas).
    SIN_TEXTURAS = bool(os.environ.get('NEREA_SIN_TEXTURAS'))
    # Una piel y una capa de brillo por fase: la maldicion se extiende.
    for fase in ((1,) if SIN_TEXTURAS else (4, 3, 2, 1)):
        base, brillo, libre = nj.pintar_atlas(uv, alto, fase)
        if not SIN_TEXTURAS:
            os.makedirs(TEX, exist_ok=True)
            Image.fromarray(base).save(os.path.join(TEX, f'nerea_f{fase}.png'))
            Image.fromarray(brillo).save(os.path.join(TEX, f'nerea_brillo_f{fase}.png'))
    if not SIN_TEXTURAS:
        Image.fromarray(libre).save(os.path.join(TEX, 'nerea_brillo_libre.png'))
        for viejo in ('nerea.png', 'nerea_brillo.png'):
            if os.path.exists(os.path.join(TEX, viejo)):
                os.remove(os.path.join(TEX, viejo))

    CLI = os.path.join(RAIZ, 'src/client/java/com/atalaya/client')
    with open(os.path.join(CLI, 'NereaMalla.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(nj.java_malla(uv, alto))
    with open(os.path.join(CLI, 'NereaAnimaciones.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(java_anims())
    geo, puntos, tiempos = java_geometria()
    with open(os.path.join(RAIZ, 'src/main/java/com/atalaya/entity/NereaGeometria.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(geo)
    print('atlas', nj.ANCHO_ATLAS, 'x', alto, '|', len(nj.ORDEN), 'piezas |', len(ANIMS), 'animaciones')
    for k, v in puntos.items():
        print(f'  {k:20s} izq {v[0]:6.2f}  alto {v[1]:6.2f}  frente {v[2]:6.2f}')

    if RENDERS:
        os.makedirs(RENDERS, exist_ok=True)
        solo = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ANIMS)
        for nombre in solo:
            a = ANIMS[nombre]
            ts = sorted(set([round(t, 2) for t, _, _ in a['claves']]))
            if len(ts) > 8:
                ts = ts[::max(1, len(ts) // 8)]
            hoja(nombre, ts, base, brillo, uv, alto, RENDERS)

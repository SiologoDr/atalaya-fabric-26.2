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

# --- Despertar: alza la cabeza, se empuja sobre la rodilla, se pone en pie y ruge ---
_rugido = mezcla({'pelvis': P(0, -1, 0), 'torso': r(-14), 'cuello': r(-10), 'cabeza': r(-28), 'mandibula': r(38)},
                 brazo('izq', -40, -70, -20), brazo('der', -50, 60, -30))
anim('DESPERTAR', 3.2, [
    (0, _dorm, 'c'),
    (0.4, con(_dorm, cabeza=r(-6), cuello=r(0)), 'c'),
    (0.85, mezcla(_dorm, {'pelvis': P(0, 10, -2), 'torso': r(28), 'cabeza': r(-10)}, brazo('izq', -52, -8, -52)), 'c'),
    (1.15, mezcla({'pelvis': P(0, 5, -1), 'torso': r(16)}, apoyo('izq', 6.5, SUELO, -9), en_el_aire('der', -6, 5),
                  brazo('izq', -30, -8, -30)), 'c'),
    (1.45, mezcla({'pelvis': P(0, 1, 0), 'torso': r(-2)}, apoyo('izq', 6, SUELO, -4)), 'c'),
    (1.75, mezcla({'pelvis': P(0, 3.5, 1), 'torso': r(12), 'cabeza': r(10)}, brazo('izq', -10, -10, -40), brazo('der', -20, 10, -70)), 'c'),
    (2.0, _rugido, 'l'), (2.6, con(_rugido, cabeza=r(-31, 3)), 'c'), (3.2, N, 'c')])

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


# ----------------------------------------------------------------------
#  El pase de fisica
# ----------------------------------------------------------------------
def hornear_todo():
    for nombre, a in ANIMS.items():
        nuevos, sustituye = nf.hornear(nombre, a, pose_autor, muestrear, a['apoyos'], a['sin_fisica'])
        quedan = [c for c in canales_autor(a) if not (c[0] in sustituye and c[1] == 'rot')]
        a['horneado'] = quedan + nuevos


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
    os.makedirs(TEX, exist_ok=True)
    # Una piel y una capa de brillo por fase: la maldicion se extiende.
    for fase in (4, 3, 2, 1):
        base, brillo, libre = nj.pintar_atlas(uv, alto, fase)
        Image.fromarray(base).save(os.path.join(TEX, f'nerea_f{fase}.png'))
        Image.fromarray(brillo).save(os.path.join(TEX, f'nerea_brillo_f{fase}.png'))
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

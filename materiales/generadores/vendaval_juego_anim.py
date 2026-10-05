"""
Animaciones de Aeralis, la Mariposa del Vendaval, escritas pose a pose y pasadas por
fisica (vendaval_fisica.py: retraso de cabeza, antenas, abdomen y alas de
abajo; las cintas como pendulos).

Convenciones (todo SE SUMA a la postura de reposo):
  rot   grados (x, y, z), como degreeVec
  pos   pixeles del modelo con Y hacia ABAJO (al exportar pasa a posVec)
  esc   multiplicadores (x, y, z)
Para las alas se usa alas(adelante, arriba): grados que el ala barre hacia
delante (negativo: hacia atras, sobre el lomo) y que sube (negativo: baja).

De aqui salen AeralisMalla.java, AeralisAnimaciones.java,
AeralisGeometria.java (duraciones, ticks clave y puntos para el servidor) y
las texturas de cada fase.

Uso: python vendaval_juego_anim.py <raiz del proyecto> [carpeta de renders] [ANIM,ANIM]
"""
import math, os, sys, copy
import numpy as np
from PIL import Image
import vendaval_juego as vj
import vendaval_fisica as vf
import nerea_modelo as nm

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
RENDERS = sys.argv[2] if len(sys.argv) > 2 else None


# ----------------------------------------------------------------------
#  Ayudas de pose
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


def con(pose, **piezas):
    return mezcla(pose, piezas)


def sumar(*poses):
    """Suma poses (rotaciones y posiciones se suman; escalas se multiplican)."""
    out = {}
    for p in poses:
        for k, v in p.items():
            d = out.setdefault(k, {})
            for tipo, val in v.items():
                if tipo == 'esc':
                    d[tipo] = tuple(a * b for a, b in zip(d.get(tipo, (1, 1, 1)), val))
                else:
                    d[tipo] = tuple(a + b for a, b in zip(d.get(tipo, (0, 0, 0)), val))
    return out


def alas(adelante, arriba, inf=None, giro=0.0):
    """Las cuatro alas. adelante: grados que barren hacia delante (negativo:
    hacia atras, sobre el lomo); arriba: lo que suben; giro: la membrana se
    tuerce sobre su eje largo (el borde de ataque adelante o atras). inf:
    (adelante, arriba) de las de abajo; si no se da, siguen al 75 %."""
    ai, ri = inf if inf is not None else (adelante * 0.75, arriba * 0.6)
    return {'ala_sup_izq': r(giro, adelante, -arriba), 'ala_sup_der': r(giro, -adelante, arriba),
            'ala_inf_izq': r(giro * 0.6, ai, -ri), 'ala_inf_der': r(giro * 0.6, -ai, ri)}


def alas2(izq, der, giro_izq=0.0, giro_der=0.0):
    """Cada lado por su cuenta: izq y der son (adelante, arriba) de la de arriba."""
    return {'ala_sup_izq': r(giro_izq, izq[0], -izq[1]), 'ala_sup_der': r(giro_der, -der[0], der[1]),
            'ala_inf_izq': r(giro_izq * 0.6, izq[0] * 0.75, -izq[1] * 0.6),
            'ala_inf_der': r(giro_der * 0.6, -der[0] * 0.75, der[1] * 0.6)}


def antenas(x, abre=0.0):
    """Antenas: x positivo las echa hacia delante; abre las separa."""
    return {'antena_izq': r(x, 0, abre), 'antena_der': r(x, 0, -abre)}


def colmillos(abre):
    return {'colmillo_izq': r(0, 0, -abre), 'colmillo_der': r(0, 0, abre)}


def patas(delante=0.0, resto=0.0, tibia=0.0):
    out = {}
    for n in ('izq', 'der'):
        out[f'pata0_{n}'] = r(delante, 0, 0)
        out[f'pata1_{n}'] = r(resto, 0, 0)
        out[f'pata2_{n}'] = r(resto, 0, 0)
        if tibia:
            for i in range(3):
                out[f'pata{i}_{n}_tibia'] = r(tibia, 0, 0)
    return out


def abdomen(x, cola=None):
    """El abdomen entero se curva: x positivo lleva la punta atras."""
    c = cola if cola is not None else x
    return {'abdomen': r(x), 'abdomen2': r(x * 0.8), 'abdomen3': r(c * 0.7), 'abdomen4': r(c * 0.7), 'punta': r(c * 0.5)}


def cuerpo(x=0.0, y=0.0, z=0.0, sube=0.0, avanza=0.0, lado=0.0):
    """Todo el cuerpo: giro (cabeceo, guinada, alabeo) y desplazamiento en
    pixeles (sube hacia arriba, avanza hacia delante)."""
    return {'cuerpo': {'rot': (x, y, z), 'pos': (lado, -sube, -avanza)}}


N = {}
ANIMS = {}


def anim(nombre, dur, claves, loop=False, extra=(), sin_fisica=()):
    ANIMS[nombre] = {'dur': dur, 'loop': loop, 'claves': claves, 'extra': list(extra), 'sin_fisica': set(sin_fisica)}


def muestreada(f, dur, pasos):
    """Claves sacadas de una funcion continua f(s) -> pose."""
    return [(dur * k / pasos, f(dur * k / pasos), 'c') for k in range(pasos + 1)]


def temblor(base, t0, t1, cada, delta, claves):
    """Anade a claves un temblor sobre la pose base: alterna base+delta y
    base-delta cada 'cada' segundos, apagandose al final."""
    k = 0
    t = t0
    while t < t1 - 1e-6:
        g = 1.0 - 0.6 * (t - t0) / max(1e-6, t1 - t0)
        s = 1 if k % 2 == 0 else -1
        d = {pz: {tp: tuple(c * s * g for c in v) for tp, v in dd.items()} for pz, dd in delta.items()}
        claves.append((round(t, 3), sumar(base, d), 'c'))
        t += cada
        k += 1
    return claves


# ----------------------------------------------------------------------
#  El vuelo: una batida en ocho. Las alas barren adelante deprisa (el golpe
#  que la sostiene) y vuelven despacio, torciendo la membrana en cada cambio
#  de sentido; las de abajo, un pelo por detras. El cuerpo sube con cada
#  golpe y la cabeza lo compensa para no perder de vista a su presa; el
#  abdomen, las patas y las antenas se quedan atras.
# ----------------------------------------------------------------------
T_VUELO = 1.1
T_AVANCE = 1.1   # el mismo periodo que el vuelo: se mezclan sin desfasarse


def batida(f, amp=1.0, adel0=6.0, arr0=12.0, retraso=0.55):
    w = f + 0.32 * math.sin(f)
    adel = adel0 + 44 * amp * math.sin(w)
    arr = arr0 + 18 * amp * math.cos(w) + 7 * amp * math.cos(2 * w)
    giro = -16 * amp * math.cos(w)
    wi = w - retraso
    adel_i = adel0 * 0.7 + 36 * amp * math.sin(wi)
    arr_i = arr0 * 0.4 + 11 * amp * math.cos(wi)
    gi = -12 * amp * math.cos(wi)
    return {'ala_sup_izq': r(giro, adel, -arr), 'ala_sup_der': r(giro, -adel, arr),
            'ala_inf_izq': r(gi, adel_i, -arr_i), 'ala_inf_der': r(gi, -adel_i, arr_i)}, w


def colgantes(w, k=1.0):
    """Lo que cuelga y se queda atras con cada golpe de alas."""
    p = {}
    p.update(abdomen(-6 * k * math.sin(w + 2.0), -4 * k * math.sin(w + 2.8)))
    p.update(antenas(7 * k * math.sin(w + 2.6), 4 * k * math.cos(w + 2.0)))
    for i in range(3):
        for n in ('izq', 'der'):
            p[f'pata{i}_{n}'] = r(6 * k * math.sin(w + 2.2 + 0.4 * i))
            p[f'pata{i}_{n}_tibia'] = r(-5 * k * math.sin(w + 2.7 + 0.4 * i))
    p.update(colmillos(2.5 * math.sin(w + 1.0)))
    return p


def pose_vuelo(s):
    f = 2 * math.pi * s / T_VUELO
    p, w = batida(f)
    p.update(colgantes(w))
    p.update(cuerpo(x=2.5 * math.sin(w + 0.9), sube=10 * math.sin(w - 0.35), avanza=1.5 * math.cos(w)))
    p['torax'] = r(4 * math.sin(w + 1.2))
    p['cabeza'] = r(2 - 4 * math.sin(w + 1.2))
    return p


def pose_avance(s):
    """Vuelo rapido: el cuerpo se tumba hacia delante, las alas barren mas
    hondo y mas deprisa, las patas se recogen y el abdomen va detras."""
    f = 2 * math.pi * s / T_AVANCE
    p, w = batida(f, 1.25, adel0=-8.0, arr0=6.0, retraso=0.5)
    p.update(colgantes(w, 0.7))
    p.update(abdomen(16 - 5 * math.sin(w + 2.0), 18 - 4 * math.sin(w + 2.8)))
    p.update(antenas(-28 + 5 * math.sin(w + 2.6), 8))
    p.update(patas(26, 32, -20))
    p.update(cuerpo(x=24 + 3 * math.sin(w + 0.9), sube=7 * math.sin(w - 0.35)))
    p['torax'] = r(3 * math.sin(w + 1.2))
    p['cabeza'] = r(-20 - 3 * math.sin(w + 1.2))
    return p


anim('VUELO', T_VUELO, muestreada(pose_vuelo, T_VUELO, 16), loop=True)
anim('AVANCE', T_AVANCE, muestreada(pose_avance, T_AVANCE, 16), loop=True)

# --- Dormida: posada y envuelta en sus alas, como en un capullo, la cabeza gacha ---
_dorm = sumar(alas(74, -26, (62, -18), giro=6), antenas(-24, -6), patas(18, 12), abdomen(-10),
              cuerpo(x=4, sube=-10), {'cabeza': r(28), 'torax': r(10)})
anim('DORMIDA', 6.0, [(0, _dorm, 'c'), (1.4, sumar(_dorm, antenas(6, 2)), 'c'), (1.6, _dorm, 'c'),
                      (3.0, sumar(_dorm, {'torax': r(3), 'cabeza': r(3)}, alas(-2, -3)), 'c'),
                      (4.2, _dorm, 'c'), (4.35, sumar(_dorm, alas2((-8, 8), (0, 0))), 'c'), (4.6, _dorm, 'c'),
                      (6.0, _dorm, 'c')], loop=True)

# --- Despertar: se estremece, despliega las alas de golpe, dos batidas la
#     despegan y chilla con las alas en alto ---
_chillido = sumar(alas(4, 46, (2, 30), giro=-10), antenas(-20, 22), colmillos(34), abdomen(-14),
                  patas(-24, -16), cuerpo(sube=20), {'cabeza': r(-34), 'torax': r(-18)})
_cl = [(0, _dorm, 'c'),
       (0.4, sumar(_dorm, antenas(18, 6), {'cabeza': r(-18)}), 'c'),
       (0.5, sumar(_dorm, antenas(18, 6), {'cabeza': r(-18)}, alas(4, 4)), 'c'),
       (0.6, sumar(_dorm, antenas(18, 6), {'cabeza': r(-18)}, alas(-4, -4)), 'c'),
       (0.7, sumar(_dorm, antenas(18, 6), {'cabeza': r(-18)}, alas(4, 4)), 'c'),
       (0.85, sumar(alas(-30, 10, giro=-10), cuerpo(sube=-4), {'torax': r(-4), 'cabeza': r(-6)}), 'c'),
       (1.0, sumar(alas(18, 34, giro=-18), antenas(-12, 16), {'cabeza': r(-12)}), 'c'),
       (1.25, sumar(alas(48, -24, giro=16), cuerpo(sube=14), {'torax': r(8)}), 'l'),
       (1.5, sumar(alas(-34, 26, giro=-12), cuerpo(sube=12)), 'c'),
       (1.75, sumar(alas(44, -20, giro=14), cuerpo(sube=22), {'torax': r(6)}), 'l'),
       (2.0, sumar(alas(-20, 40, giro=-8), colmillos(16), cuerpo(sube=20), {'torax': r(-14), 'cabeza': r(-20)}), 'c'),
       (2.2, _chillido, 'l')]
temblor(_chillido, 2.3, 2.9, 0.07, {'cabeza': {'rot': (2.5, 2.0, 0)}, 'ala_sup_izq': {'rot': (0, 2, -2)},
                                     'ala_sup_der': {'rot': (0, -2, 2)}}, _cl)
_cl += [(3.1, sumar(alas(-10, 20), cuerpo(sube=6), {'cabeza': r(-6)}), 'c'), (3.6, N, 'c')]
anim('DESPERTAR', 3.6, _cl)

# --- Aleteo Cortante: se retuerce como un lanzador, con las alas en alto
#     temblando de tension, y suelta un tajo horizontal girando el cuerpo y
#     lanzandose con el ---
_al_carga = sumar(alas2((-28, 52), (-8, 40), -16, -8), antenas(-26, 10), abdomen(-14), patas(-10, -6),
                  cuerpo(y=-24, z=-8, sube=6, avanza=-10), {'torax': r(-16), 'cabeza': {'rot': (-12, 14, 0)}})
_al_golpe = sumar(alas2((74, -10), (60, -16), 22, 18), antenas(26, 6), colmillos(22), abdomen(16), patas(20, 14),
                  cuerpo(x=6, y=20, z=6, sube=-2, avanza=18), {'torax': r(22), 'cabeza': {'rot': (16, -10, 0)}})
_cl = [(0, N, 'c'),
       (0.12, sumar(alas(12, -8), cuerpo(sube=-4, avanza=4), {'torax': r(6)}), 'c'),
       (0.46, _al_carga, 'c')]
temblor(_al_carga, 0.5, 0.64, 0.035, {'ala_sup_izq': {'rot': (0, -2.5, -1.5)}, 'ala_sup_der': {'rot': (0, 2.5, 1.5)},
                                       'torax': {'rot': (-1.5, 0, 0)}}, _cl)
_cl += [(0.68, _al_golpe, 'l'),
        (0.8, sumar(alas2((86, -20), (78, -24), 18, 14), antenas(30, 6), colmillos(18), abdomen(20),
                    cuerpo(x=8, y=26, z=8, avanza=20), {'torax': r(28), 'cabeza': r(14)}), 'c'),
        (1.0, sumar(alas(48, -6), abdomen(6), cuerpo(avanza=8), {'torax': r(10), 'cabeza': r(4)}), 'c'),
        (1.2, sumar(alas(-12, 12), cuerpo(avanza=-2)), 'c'),
        (1.5, N, 'c')]
anim('ALETEO', 1.5, _cl)

# --- Tornados: sube con las alas en alto y golpea el aire contra el suelo ---
_to_alza = sumar(alas(-6, 58, (-4, 40), giro=-10), antenas(-14, 14), abdomen(-10), patas(-16, -10),
                 cuerpo(sube=26, avanza=-4), {'torax': r(-14), 'cabeza': r(-16)})
_to_golpe = sumar(alas(30, -58, (22, -46), giro=20), antenas(30), colmillos(24), abdomen(18), patas(24, 20),
                  cuerpo(x=8, sube=-14, avanza=4), {'torax': r(30), 'cabeza': r(22)})
_cl = [(0, N, 'c'), (0.15, sumar(alas(-10, 10), cuerpo(sube=4)), 'c'), (0.56, _to_alza, 'c')]
temblor(_to_alza, 0.6, 0.7, 0.035, {'ala_sup_izq': {'rot': (0, 0, -2.5)}, 'ala_sup_der': {'rot': (0, 0, 2.5)}}, _cl)
_cl += [(0.75, _to_golpe, 'l'),
        (0.95, sumar(_to_golpe, alas(4, -4), cuerpo(sube=-2)), 'c'),
        (1.15, sumar(alas(20, -40, giro=10), abdomen(8), cuerpo(sube=-6), {'torax': r(14), 'cabeza': r(8)}), 'c'),
        (1.45, sumar(alas(-16, 18), cuerpo(sube=4)), 'c'),
        (1.9, N, 'c')]
anim('TORNADOS', 1.9, _cl)

# --- La Caceria: se echa atras, clava la mirada en la presa, las antenas
#     apuntan como lanzas y las alas vibran de rabia ---
_ma_fija = sumar(alas(-26, 30, giro=-10), antenas(78, -8), colmillos(30), abdomen(-8), patas(-30, -12),
                 cuerpo(x=4, avanza=8), {'cabeza': r(18), 'torax': r(10)})
_cl = [(0, N, 'c'),
       (0.22, sumar(alas(-36, 22), antenas(-20, 18), colmillos(18), cuerpo(avanza=-6), {'cabeza': r(-18), 'torax': r(-8)}), 'c'),
       (0.62, _ma_fija, 'l')]
temblor(_ma_fija, 0.66, 1.05, 0.045, {'ala_sup_izq': {'rot': (0, 3, -2)}, 'ala_sup_der': {'rot': (0, -3, 2)},
                                       'ala_inf_izq': {'rot': (0, 2, -1)}, 'ala_inf_der': {'rot': (0, -2, 1)},
                                       'antena_izq': {'rot': (2, 0, 0)}, 'antena_der': {'rot': (-2, 0, 0)}}, _cl)
_cl += [(1.4, N, 'c')]
anim('MARCA', 1.4, _cl)

# --- Rafaga: una batida seca hacia la presa; el retroceso la echa atras ---
anim('RAFAGA', 0.75, [(0, N, 'c'),
                      (0.18, sumar(alas(-50, 20, giro=-14), cuerpo(avanza=4), {'torax': r(-8)}), 'c'),
                      (0.36, sumar(alas(46, -12, giro=18), colmillos(16), cuerpo(x=-4, avanza=-6),
                                   {'torax': r(12), 'cabeza': r(6)}), 'l'),
                      (0.5, sumar(alas(30, -6), cuerpo(avanza=-4)), 'c'),
                      (0.75, N, 'c')])
# --- Doble rafaga: primero el ala izquierda, luego la derecha, girando el cuerpo ---
anim('DOBLE_RAFAGA', 1.1, [(0, N, 'c'),
                           (0.14, sumar(alas2((-50, 20), (-20, 10), -14, -4), cuerpo(y=-8)), 'c'),
                           (0.32, sumar(alas2((52, -12), (-30, 18), 18, -6), colmillos(14), cuerpo(y=12, avanza=-4),
                                        {'torax': r(10)}), 'l'),
                           (0.48, sumar(alas2((20, 0), (-55, 22), 4, -14), cuerpo(y=6)), 'c'),
                           (0.7, sumar(alas2((-10, 10), (54, -12), -4, 18), colmillos(18), cuerpo(y=-12, avanza=-4),
                                       {'torax': r(12)}), 'l'),
                           (0.85, sumar(alas(16, -4), cuerpo(y=-4)), 'c'),
                           (1.1, N, 'c')])

# --- Juicio del Ciclon: sube con dos batidas lentas y se queda en cruz,
#     con las alas abiertas de par en par y la cabeza al cielo; sostiene el
#     ciclon y da la palmada ---
_ju_cruz = sumar(alas(14, 34, (12, 22), giro=-6), antenas(-16, 20), abdomen(-4), patas(-20, -14),
                 {'cabeza': r(-22), 'torax': r(-6)})
anim('JUICIO_SUBE', 3.2, [(0, N, 'c'),
                          (0.4, sumar(alas(-40, 30, giro=-14), {'cabeza': r(-6)}), 'c'),
                          (0.9, sumar(alas(40, -14, giro=16), cuerpo(sube=8)), 'c'),
                          (1.4, sumar(alas(-30, 36, giro=-12), cuerpo(sube=6), {'cabeza': r(-12)}), 'c'),
                          (1.9, sumar(alas(32, -6, giro=10), cuerpo(sube=12)), 'c'),
                          (2.5, _ju_cruz, 'c'), (3.2, sumar(_ju_cruz, alas(2, 2)), 'c')])
anim('JUICIO_SOSTIENE', 2.4, [(0, _ju_cruz, 'c'),
                              (0.6, sumar(_ju_cruz, alas(6, -6), cuerpo(sube=4), {'cabeza': r(-3)}), 'c'),
                              (1.2, sumar(_ju_cruz, alas(-4, 6), cuerpo(sube=-2)), 'c'),
                              (1.8, sumar(_ju_cruz, alas(6, -4), cuerpo(sube=3), {'cabeza': r(3)}), 'c'),
                              (2.4, _ju_cruz, 'c')], loop=True)
_ju_carga = sumar(alas(-16, 62, (-12, 42), giro=-14), antenas(-16, 16), colmillos(26), abdomen(-12),
                  cuerpo(sube=8, avanza=-8), {'torax': r(-20), 'cabeza': r(-14)})
_ju_golpe = sumar(alas(84, -6, (66, -4), giro=26), antenas(34), colmillos(36), abdomen(18), patas(20, 16),
                  cuerpo(x=8, sube=-6, avanza=14), {'torax': r(26), 'cabeza': r(26)})
_cl = [(0, _ju_cruz, 'c'), (0.42, _ju_carga, 'c')]
temblor(_ju_carga, 0.46, 0.68, 0.04, {'ala_sup_izq': {'rot': (0, -2, -2)}, 'ala_sup_der': {'rot': (0, 2, 2)},
                                       'cabeza': {'rot': (1.5, 0, 0)}}, _cl)
_cl += [(0.72, _ju_golpe, 'l'),
        (0.95, sumar(_ju_golpe, alas(4, -4), {'torax': r(2)}), 'c'),
        (1.25, sumar(alas(40, 0), abdomen(6), cuerpo(avanza=4), {'torax': r(10)}), 'c'),
        (1.7, N, 'c')]
anim('JUICIO_GOLPE', 1.7, _cl)

# --- Aturdida: los cuatro nucleos rotos. Se derrumba en el suelo con las
#     alas caidas, se retuerce, intenta batir y no puede ---
_at = sumar(alas(-6, -48, (-4, -36), giro=12), antenas(36, -10), abdomen(-10), patas(24, 26, 20),
            cuerpo(x=6, sube=-10), {'torax': r(30), 'cabeza': r(34)})
anim('ATURDIDA', 5.0, [(0, N, 'c'),
                       (0.25, sumar(alas(-30, 30, giro=-20), cuerpo(sube=4), {'cabeza': r(-20)}), 'c'),
                       (0.6, _at, 'c'),
                       (1.3, sumar(_at, alas2((-4, 18), (0, 0))), 'c'), (1.5, _at, 'c'),
                       (2.3, sumar(_at, {'cabeza': {'rot': (-6, 14, 0)}}), 'c'),
                       (2.5, sumar(_at, {'cabeza': {'rot': (-4, -12, 0)}}), 'c'), (2.7, _at, 'c'),
                       (3.1, sumar(_at, alas(-14, 26, giro=-8), {'torax': r(-8)}), 'c'),
                       (3.3, sumar(_at, alas(10, -4)), 'c'), (3.5, _at, 'c'),
                       (4.2, sumar(alas(-30, 24, giro=-10), cuerpo(sube=-2), {'torax': r(10)}), 'c'),
                       (4.55, sumar(alas(34, -14, giro=14), cuerpo(sube=6)), 'l'),
                       (5.0, N, 'c')])

# --- Agotada (fase IV): se estrella, rebota, las alas planas en el suelo y
#     jadea; luego se arranca con dos batidas ---
_ag = sumar(alas(22, -60, (16, -48), giro=10), antenas(44, -12), abdomen(-14), patas(20, 36, 18),
            cuerpo(x=6, sube=-12), {'torax': r(42), 'cabeza': r(30)})
_cl = [(0, N, 'c'),
       (0.15, sumar(alas(-20, 40, giro=-16), cuerpo(sube=6), {'cabeza': r(-14)}), 'c'),
       (0.3, _ag, 'l'),
       (0.45, sumar(_ag, cuerpo(sube=5), {'torax': r(-8)}), 'c'),
       (0.6, _ag, 'c')]
for k in range(5):
    tt = 1.0 + k * 0.5
    _cl.append((tt, sumar(_ag, {'torax': r(-6 if k % 2 == 0 else 0)}, alas(0, 4 if k % 2 == 0 else 0)), 'c'))
_cl += [(3.6, sumar(alas(-16, 20, giro=-10), cuerpo(sube=-4), {'torax': r(16), 'cabeza': r(4)}), 'c'),
        (3.95, sumar(alas(40, -24, giro=16), cuerpo(sube=10), {'torax': r(10)}), 'l'),
        (4.3, sumar(alas(-30, 24, giro=-12), cuerpo(sube=8)), 'c'),
        (4.65, sumar(alas(30, -10, giro=10), cuerpo(sube=6)), 'c'),
        (5.0, N, 'c')]
anim('AGOTADA', 5.0, _cl)

# --- Tambaleo (cambio de fase): un rayo la sacude de lado, se estremece y
#     chilla con las alas en alto ---
_ta_golpe = sumar(alas2((-60, 40), (-20, -10), -20, 8), colmillos(28), cuerpo(z=14, sube=4, avanza=-10),
                  {'torax': r(-28), 'cabeza': r(-30)})
_cl = [(0, N, 'c'), (0.08, _ta_golpe, 'l')]
temblor(_ta_golpe, 0.16, 0.8, 0.06, {'cuerpo': {'rot': (0, 0, 7)}, 'cabeza': {'rot': (3, 4, 0)}}, _cl)
_ta_grito = sumar(alas(2, 40, giro=-10), antenas(-18, 18), colmillos(32), cuerpo(sube=6), abdomen(-10),
                  {'cabeza': r(-24), 'torax': r(-10)})
_cl += [(0.95, _ta_grito, 'c')]
temblor(_ta_grito, 1.0, 1.5, 0.07, {'cabeza': {'rot': (2, 2, 0)}, 'ala_sup_izq': {'rot': (0, 2, -1)},
                                     'ala_sup_der': {'rot': (0, -2, 1)}}, _cl)
_cl += [(1.9, sumar(alas(10, 10), {'cabeza': r(-4)}), 'c'), (2.6, N, 'c')]
anim('TAMBALEO', 2.6, _cl)

# --- Liberacion: el ultimo chillido, baja planeando con batidas lentas, se
#     posa y abre las alas al sol, respirando despacio ---
_li_abre = sumar(alas(22, 24, (18, 16), giro=-6), antenas(-14, 16), patas(10, 8), cuerpo(sube=-6),
                 {'cabeza': r(-16), 'torax': r(-4)})
anim('LIBERACION', 10.0, [(0, N, 'c'),
                          (0.4, sumar(alas(-34, 34, giro=-12), colmillos(30), {'cabeza': r(-30)}), 'c'),
                          (1.2, sumar(alas(-10, 20), {'cabeza': r(-10)}), 'c'),
                          (1.8, sumar(alas(26, -10, giro=10), cuerpo(sube=4)), 'c'),
                          (2.4, sumar(alas(-20, 20, giro=-8), cuerpo(sube=2)), 'c'),
                          (3.0, sumar(alas(20, -8, giro=8), cuerpo(sube=2)), 'c'),
                          (3.6, sumar(alas(-10, 24), patas(-14, -10)), 'c'),
                          (4.2, sumar(alas(10, 8), cuerpo(sube=-6), {'torax': r(6)}), 'c'),
                          (5.0, _li_abre, 'c'),
                          (6.5, sumar(_li_abre, alas(4, 4), {'cabeza': r(-2)}), 'c'),
                          (8.0, sumar(_li_abre, alas(-2, -2)), 'c'),
                          (10.0, _li_abre, 'c')])


# ----------------------------------------------------------------------
#  De poses a canales (como nerea_juego_anim)
# ----------------------------------------------------------------------
NULO = {'rot': (0, 0, 0), 'pos': (0, 0, 0), 'esc': (1, 1, 1)}


def canales_autor(a):
    usados = {}
    for _, p, _ in a['claves']:
        for pieza, d in p.items():
            for tipo in d:
                if tipo in NULO:
                    usados.setdefault((pieza, tipo), True)
    out = []
    for (pieza, tipo) in usados:
        ks = [(t, tuple(p.get(pieza, {}).get(tipo, NULO[tipo])), i) for t, p, i in a['claves']]
        if all(k[1] == NULO[tipo] for k in ks):
            continue
        out.append((pieza, tipo, ks))
    return out + list(a['extra'])


def canales(a):
    return a.get('horneado') or canales_autor(a)


def catmull(a, p0, p1, p2, p3):
    return 0.5 * (2 * p1 + (p2 - p0) * a + (2 * p0 - 5 * p1 + 4 * p2 - p3) * a * a + (3 * p1 - p0 - 3 * p2 + p3) * a ** 3)


def muestrear(ks, s, tipo):
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
    a = ANIMS[nombre]
    if a['loop']:
        s = s % a['dur']
    return _pose(canales(a), s)


def hornear_todo():
    for nombre, a in ANIMS.items():
        nuevos, sustituye = vf.hornear(nombre, a, pose_autor, a['sin_fisica'])
        quedan = [c for c in canales_autor(a) if not (c[0] in sustituye and c[1] == 'rot')]
        a['horneado'] = quedan + nuevos


if not os.environ.get('VENDAVAL_SIN_FISICA'):
    hornear_todo()


# ----------------------------------------------------------------------
#  Exportar animaciones
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
         ' * Las animaciones de Aeralis, la Mariposa del Vendaval. GENERADO por',
         ' * materiales/generadores/vendaval_juego_anim.py (poses) y vendaval_fisica.py',
         ' * (retraso de cabeza, antenas y abdomen; cintas como pendulos). No se editan a',
         ' * mano: el servidor saca de las mismas poses los puntos y los ticks de cada golpe',
         ' * (AeralisGeometria).',
         ' */',
         'public final class AeralisAnimaciones {', '']
    for nombre in ANIMS:
        L.append(f'    public static final AnimationDefinition {nombre} = {nombre.lower()}();')
    L += ['', '    private AeralisAnimaciones() {', '    }', '',
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
                    y = -y
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
    return vj.a_bloques(vj.punto(pose, pieza, local))


T_ALETEO = 0.68
T_TORNADOS = 0.75
T_MARCA = 0.62
T_RAFAGA = 0.36
T_DOBLE = (0.32, 0.7)
T_JUICIO = 0.72
T_AGOTADA = 0.3


def java_geometria():
    W, H = vj.TAM_SUP
    puntos = {
        'NUCLEO': p_bloques(None, 0, 'nucleo'),
        'CABEZA': p_bloques(None, 0, 'cabeza', (0, -12, -10)),
        'OJO_IZQ': p_bloques(None, 0, 'ojo_izq'),
        'OJO_DER': p_bloques(None, 0, 'ojo_der'),
        'BOCA': p_bloques(None, 0, 'cabeza', (0, -4, -16)),
        'BOCA_MARCA': p_bloques('MARCA', T_MARCA, 'cabeza', (0, -4, -16)),
        'NUCLEO_JUICIO': p_bloques('JUICIO_GOLPE', T_JUICIO, 'nucleo'),
        'NUCLEO_TORNADOS': p_bloques('TORNADOS', T_TORNADOS, 'nucleo'),
        'PUNTA_ALA_IZQ_ALETEO': p_bloques('ALETEO', T_ALETEO, 'ala_sup_izq', (W * 0.9, -H * 0.3, 0)),
        'PUNTA_ALA_DER_ALETEO': p_bloques('ALETEO', T_ALETEO, 'ala_sup_der', (-W * 0.9, -H * 0.3, 0)),
        'PUNTA_ALA_IZQ': p_bloques(None, 0, 'ala_sup_izq', (W * 0.9, -H * 0.3, 0)),
        'PUNTA_ALA_DER': p_bloques(None, 0, 'ala_sup_der', (-W * 0.9, -H * 0.3, 0)),
        'PUNTA_ABDOMEN': p_bloques(None, 0, 'punta', (0, 9, 0)),
    }

    def tick(s):
        return int(round(s * 20))
    tiempos = {
        'DURACION_DESPERTAR': tick(ANIMS['DESPERTAR']['dur']), 'DESPERTAR_ALZA': tick(1.25), 'DESPERTAR_CHILLA': tick(2.2),
        'DURACION_ALETEO': tick(ANIMS['ALETEO']['dur']), 'ALETEO_CARGA': tick(0.12), 'ALETEO_SUELTA': tick(T_ALETEO),
        'DURACION_TORNADOS': tick(ANIMS['TORNADOS']['dur']), 'TORNADOS_GOLPE': tick(T_TORNADOS),
        'DURACION_MARCA': tick(ANIMS['MARCA']['dur']), 'MARCA_FIJA': tick(T_MARCA),
        'DURACION_RAFAGA': tick(ANIMS['RAFAGA']['dur']), 'RAFAGA_SUELTA': tick(T_RAFAGA),
        'DURACION_DOBLE_RAFAGA': tick(ANIMS['DOBLE_RAFAGA']['dur']), 'DOBLE_SUELTA_1': tick(T_DOBLE[0]),
        'DOBLE_SUELTA_2': tick(T_DOBLE[1]),
        'DURACION_JUICIO_SUBE': tick(ANIMS['JUICIO_SUBE']['dur']),
        'DURACION_JUICIO_GOLPE': tick(ANIMS['JUICIO_GOLPE']['dur']), 'JUICIO_GOLPE': tick(T_JUICIO),
        'DURACION_ATURDIDA': tick(ANIMS['ATURDIDA']['dur']),
        'DURACION_AGOTADA': tick(ANIMS['AGOTADA']['dur']), 'AGOTADA_CAE': tick(T_AGOTADA), 'AGOTADA_ALZA': tick(3.9),
        'DURACION_TAMBALEO': tick(ANIMS['TAMBALEO']['dur']),
        'DURACION_LIBERACION': tick(ANIMS['LIBERACION']['dur']), 'LIBERACION_OJOS_ORO': tick(3.5),
        'PERIODO_VUELO': tick(ANIMS['VUELO']['dur']), 'VUELO_GOLPE': 1,
    }
    L = ['package com.atalaya.entity;', '',
         'import net.minecraft.world.phys.Vec3;', '',
         '/**',
         ' * Medidas de Aeralis que comparten servidor y cliente. GENERADO',
         ' * por materiales/generadores/vendaval_juego_anim.py desde las mismas poses que',
         ' * las animaciones (ya con la fisica): si una animacion cambia, esto cambia.',
         ' *',
         ' * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,',
         ' * y hacia arriba desde la base de la caja, z hacia delante. AeralisEntity los',
         ' * pasa al mundo con el giro del cuerpo.',
         ' */',
         'public final class AeralisGeometria {', '',
         '    private AeralisGeometria() {', '    }', '']
    for k, (x, y, z) in puntos.items():
        L.append(f'    public static final Vec3 {k} = new Vec3({x:.3f}, {y:.3f}, {z:.3f});')
    L.append('')
    for k, v in tiempos.items():
        L.append(f'    public static final int {k} = {v};')
    L.append('}')
    return '\n'.join(L) + '\n', puntos, tiempos


# ----------------------------------------------------------------------
#  Hojas de control
# ----------------------------------------------------------------------
LUCES = [((-0.5, 0.8, -0.6), (1.0, 0.97, 0.9), 0.85, 'llave'), ((0.7, 0.3, 0.6), (0.5, 0.75, 1.0), 0.5, 'contra')]


def render_pose(pose, tex, emis, uv, alto, W=300, H=380, guinada=-30, ojo=(14, 8.0, -22), objetivo=(0, 7.0, 0), fov=50):
    cam = nm.vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W, alto=H)
    lz = nm.vr.Lienzo(W, H)
    M = nm.vr.entidad_a_mundo(0, 0, 0, guinada, vj.ESCALA)
    g = np.zeros((16, 16, 4), np.uint8)
    g[...] = (196, 204, 210, 255)
    g[0, :] = g[:, 0] = (150, 160, 170, 255)
    for i in range(-14, 14):
        for j in range(-14, 14):
            Pq = [(i, 0, j), (i + 1, 0, j), (i + 1, 0, j + 1), (i, 0, j + 1)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [Pq[k] for k in tri], [((0, 0), (1, 0), (1, 1), (0, 1))[k] for k in tri], g, np.array([0.9, 0.9, 0.9]))
    qs = vj.quads(pose, uv, alto, M)
    planos = set(vj.PLANOS)
    for Pq, UV, _, mat in [q for q in qs if q[3] not in planos]:
        luz = nm.vr.iluminar(nm.vr.normal(Pq), cam, np.mean(Pq, axis=0), LUCES, (0.42, 0.44, 0.5))
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UV[k] for k in tri], tex, luz, emis)
    for Pq, UV, _, mat in sorted([q for q in qs if q[3] in planos], key=lambda q: -cam.proyectar(np.mean(q[0], axis=0))[2]):
        luz = 0.6 + 0.6 * nm.vr.iluminar(nm.vr.normal(Pq), cam, np.mean(Pq, axis=0), LUCES, (0.42, 0.44, 0.5))
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UV[k] for k in tri], tex, luz, None, None, translucido=1.0)
    col = np.clip(lz.color + lz.emis * 0.35, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.26, 0.3, 0.38]) * (1 - a)
    return Image.fromarray((arr * 255).astype(np.uint8))


def hoja(nombre, tiempos, tex, emis, uv, alto, out, **kw):
    from PIL import ImageDraw
    ims = []
    for s in tiempos:
        im = render_pose(pose_en(nombre, s), tex, emis, uv, alto, **kw)
        ImageDraw.Draw(im).text((8, 6), f'{nombre} {s:.2f}s', fill=(230, 236, 245))
        ims.append(im)
    W, H = ims[0].size
    hojai = Image.new('RGB', (W * len(ims), H), (255, 255, 255))
    for i, im in enumerate(ims):
        hojai.paste(im, (i * W, 0))
    hojai.save(os.path.join(out, f'vendaval_anim_{nombre.lower()}.png'))


# ----------------------------------------------------------------------
if __name__ == '__main__':
    uv, alto = vj.empaquetar()
    TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/aeralis')
    os.makedirs(TEX, exist_ok=True)
    for fase in (4, 3, 2, 1):
        base, brillo = vj.pintar_atlas(uv, alto, fase)
        Image.fromarray(base).save(os.path.join(TEX, f'aeralis_f{fase}.png'))
        Image.fromarray(brillo).save(os.path.join(TEX, f'aeralis_brillo_f{fase}.png'))
    base_l, brillo_l = vj.pintar_atlas(uv, alto, 'libre')
    Image.fromarray(brillo_l).save(os.path.join(TEX, 'aeralis_brillo_libre.png'))
    base, brillo = vj.pintar_atlas(uv, alto, 1)

    CLI = os.path.join(RAIZ, 'src/client/java/com/atalaya/client')
    with open(os.path.join(CLI, 'AeralisMalla.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(vj.java_malla(uv, alto))
    with open(os.path.join(CLI, 'AeralisAnimaciones.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(java_anims())
    geo, puntos, tiempos = java_geometria()
    with open(os.path.join(RAIZ, 'src/main/java/com/atalaya/entity/AeralisGeometria.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(geo)
    print('atlas', vj.ANCHO_ATLAS, 'x', alto, '|', len(vj.ORDEN), 'piezas |', len(ANIMS), 'animaciones')
    for k, v in puntos.items():
        print(f'  {k:22s} izq {v[0]:6.2f}  alto {v[1]:6.2f}  frente {v[2]:6.2f}')

    if RENDERS:
        os.makedirs(RENDERS, exist_ok=True)
        solo = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ANIMS)
        for nombre in solo:
            a = ANIMS[nombre]
            ts = sorted(set([round(t, 2) for t, _, _ in a['claves']]))
            if len(ts) > 8:
                ts = ts[::max(1, len(ts) // 8)]
            hoja(nombre, ts, base, brillo, uv, alto, RENDERS)

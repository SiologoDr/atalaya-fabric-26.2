"""
Animaciones de Rajang, el Jaguar de Jade, escritas pose a pose.

Convenciones (todo SE SUMA a la postura de reposo de tierra_modelo.py):
  rot   grados (x, y, z), como degreeVec. En las patas, x negativo las lleva
        hacia delante; en el cuerpo, x positivo baja el hocico; en la cabeza,
        x negativo la levanta; en la mandibula, x positivo abre la boca; en la
        cola, x positivo la sube.
  pos   pixeles del modelo con Y hacia ABAJO (al exportar pasa a posVec)
  esc   multiplicadores (x, y, z)

Es el primer jefe que corre: anda con el paso lateral de los felinos (pata de
atras, la de delante del mismo lado, la otra de atras, la otra de delante),
la cabeza baja de acecho y los hombros que suben y bajan con cada mano, y
corre al galope rotatorio de los felinos grandes (el lomo que se encoge y se
estira, mucho tiempo en el aire). La cola se queda atras como un latigo (cada
segmento con algo de retraso).

Las mejoras de octubre de 2026 (tras las pruebas: "tosco y lento") anaden la
Embestida (aviso, carga y frenada), el golpe contra un muro, la Tumba de
Raices, y acortan las cargas de la Garra y el Terremoto.

De aqui salen RajangMalla.java, RajangAnimaciones.java, RajangGeometria.java
(duraciones, ticks clave y puntos para el servidor) y las texturas.

Uso: python rajang_juego_anim.py <raiz del proyecto> [carpeta de renders] [ANIM,ANIM]
"""
import math, os, sys, copy
import numpy as np
from PIL import Image
import rajang_juego as rj
import vigia_render as vr

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
RENDERS = sys.argv[2] if len(sys.argv) > 2 else None


# ----------------------------------------------------------------------
#  Ayudas de pose
# ----------------------------------------------------------------------
def r(x, y=0, z=0):
    return {'rot': (x, y, z)}


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


def cuerpo(x=0.0, y=0.0, z=0.0, baja=0.0, avanza=0.0, lado=0.0):
    """Todo el cuerpo: cabeceo (x positivo baja el hocico), guinada, alabeo y
    desplazamiento en pixeles (baja hacia el suelo, avanza hacia delante)."""
    return {'cuerpo': {'rot': (x, y, z), 'pos': (lado, baja, -avanza)}}


def mano(lado, brazo=0.0, ante=0.0, zarpa=0.0, abre=0.0):
    n = 'izq' if lado > 0 else 'der'
    return {f'brazo_{n}': r(brazo, 0, abre * lado), f'antebrazo_{n}': r(ante), f'mano_{n}': r(zarpa)}


def pata(lado, muslo=0.0, tibia=0.0, tarso=0.0, pie=0.0, abre=0.0):
    n = 'izq' if lado > 0 else 'der'
    return {f'muslo_{n}': r(muslo, 0, abre * lado), f'tibia_{n}': r(tibia), f'tarso_{n}': r(tarso), f'pie_{n}': r(pie)}


def cabeza(x=0.0, y=0.0, z=0.0, boca=0.0, cuello=0.0, cuello_y=0.0, orejas=0.0):
    return {'cabeza': r(x, y, z), 'mandibula': r(boca), 'cuello': r(cuello, cuello_y),
            'oreja_izq': r(orejas), 'oreja_der': r(orejas)}


def cola(sube=0.0, lado=0.0, fase=0.0, onda=0.0, retraso=0.55):
    """La cola: sube la base y una onda lateral que viaja hacia la punta."""
    out = {'cola0': r(sube, lado)}
    for i in range(1, 7):
        out[f'cola{i}'] = r(sube * 0.15 * (1 if i < 4 else -0.5),
                            onda * math.sin(fase - retraso * i) * (0.5 + 0.12 * i))
    return out


N = {}
ANIMS = {}


def anim(nombre, dur, claves, loop=False):
    ANIMS[nombre] = {'dur': dur, 'loop': loop, 'claves': claves}


def muestreada(f, dur, pasos):
    """Claves sacadas de una funcion continua f(s) -> pose."""
    return [(dur * k / pasos, f(dur * k / pasos), 'c') for k in range(pasos + 1)]


def temblor(base, t0, t1, cada, delta, claves):
    """Anade a claves un temblor sobre la pose base."""
    k = 0
    t = t0
    while t < t1 - 1e-6:
        g = 1.0 - 0.6 * (t - t0) / max(1e-6, t1 - t0)
        s = 1 if k % 2 == 0 else -1
        d = {pz: {tp_: tuple(c * s * g for c in v) for tp_, v in dd.items()} for pz, dd in delta.items()}
        claves.append((round(t, 3), sumar(base, d), 'c'))
        t += cada
        k += 1
    return claves


# ----------------------------------------------------------------------
#  Reposo, andar y correr
# ----------------------------------------------------------------------
T_REPOSO = 4.0
T_ANDAR = 1.3
# El paso largo: a 6-7 bloques/s, con la zancada corta, las patas iban a toda
# prisa y se veia agitado; con un 30 % mas de barrido va mas suelto.
PASO_ANDAR = 1.3
T_CORRER = 0.8


def pose_reposo(s):
    w = 2 * math.pi * s / T_REPOSO
    return sumar(cuerpo(x=0.6 * math.sin(w), baja=1.2 * math.sin(w)),
                 {'peto': {'pos': (0, 0, -0.5 * math.sin(w))}},
                 cabeza(x=2 * math.sin(w + 0.6), y=6 * math.sin(w * 0.5), boca=-6 + 3 * math.sin(w + 1.0),
                        cuello=1.5 * math.sin(w + 0.3)),
                 cola(sube=2 * math.sin(w), fase=w, onda=10, retraso=0.6))


def _pierna_del(fase, amp=1.0, paso=1.0):
    """Una pata de delante en el paso: apoyo (de -A a +B, la mano en el
    suelo) el 65 % del ciclo y vuelo (levanta y adelanta, el antebrazo
    doblado) el resto. fase en [0, 1). paso alarga la zancada (el barrido del
    brazo) sin levantar mas la mano."""
    if fase < 0.65:
        k = fase / 0.65
        brazo = (-18 + 36 * k) * amp * paso
        return brazo, -4 * amp * math.sin(math.pi * k), 6 * amp * k
    k = (fase - 0.65) / 0.35
    brazo = (18 - 36 * (0.5 - 0.5 * math.cos(math.pi * k))) * amp * paso
    return brazo, 44 * amp * math.sin(math.pi * k), -30 * amp * math.sin(math.pi * k)


def _pierna_tras(fase, amp=1.0, paso=1.0):
    if fase < 0.65:
        k = fase / 0.65
        muslo = (-14 + 32 * k) * amp * paso
        return muslo, -6 * amp * k, 6 * amp * k, -8 * amp * k
    k = (fase - 0.65) / 0.35
    muslo = (18 - 32 * (0.5 - 0.5 * math.cos(math.pi * k))) * amp * paso
    sube = math.sin(math.pi * k)
    return muslo, 26 * amp * sube, -24 * amp * sube, 20 * amp * sube


def pose_andar(s):
    """El paso lateral de los felinos: cada pata apoya en su momento (atras
    izquierda 0, delante izquierda 0.25, atras derecha 0.5, delante derecha
    0.75). El fase de cada pata es (f - momento): con + salia la secuencia
    diagonal. Al acecho: la cabeza baja y por delante de los hombros, que suben
    y bajan con cada mano; el peso cae justo despues de que apoye cada mano."""
    f = s / T_ANDAR
    w = 2 * math.pi * f
    p = {}
    for lado, off_d, off_t in ((1, 0.25, 0.0), (-1, 0.75, 0.5)):
        b, a, m = _pierna_del((f - off_d) % 1.0, 1.1, PASO_ANDAR)
        p.update(mano(lado, b, a, m))
        mu, ti, ta, pi_ = _pierna_tras((f - off_t) % 1.0, 1.05, PASO_ANDAR)
        p.update(pata(lado, mu, ti, ta, pi_))
    # el peso cae tras cada mano (0.25 y 0.75) y el lomo rueda hacia la que apoya
    cae = 0.5 + 0.5 * math.cos(4 * math.pi * (f - 0.32))
    rueda = math.cos(2 * math.pi * (f - 0.57))
    return sumar(p, cuerpo(x=1.6 * math.cos(4 * math.pi * (f - 0.3)), z=3.0 * rueda, baja=2.6 * cae, y=1.8 * rueda),
                 cabeza(x=5 + 2.5 * math.cos(4 * math.pi * (f - 0.42)), y=-2.5 * rueda, boca=-6, cuello=7 - 2 * cae, orejas=4),
                 cola(sube=6, lado=-5 * rueda, fase=w, onda=14, retraso=0.7))


def _ciclo(fase, apoyo, a0, a1):
    """Una pata en el galope: en el apoyo va de a0 (delante) a a1 (atras) con
    la zarpa en el suelo; en el vuelo vuelve a a0 recogida. Devuelve (angulo,
    cuanto se recoge de 0 a 1)."""
    if fase < apoyo:
        k = fase / apoyo
        return a0 + (a1 - a0) * k, 0.0
    k = (fase - apoyo) / (1.0 - apoyo)
    return a1 + (a0 - a1) * (0.5 - 0.5 * math.cos(math.pi * k)), math.sin(math.pi * k)


def pose_correr(s):
    """El galope rotatorio de los felinos grandes, en cuatro tiempos: atras
    izquierda, atras derecha, delante derecha, delante izquierda. Cada pata
    apoya poco (el 38 % del ciclo) y se recoge mucho al volver; el lomo se
    encoge cuando las de atras llegan bajo el cuerpo y se estira cuando las de
    delante se alargan; la cabeza va baja y firme, compensando, y la cola
    estirada detras hace de timon."""
    f = s / T_CORRER
    w = 2 * math.pi * f
    p = {}
    for lado, n, golpe_del, golpe_tras in ((1, 'izq', 0.55, 0.0), (-1, 'der', 0.43, 0.11)):
        b, rec = _ciclo((f - golpe_del) % 1.0, 0.36, -32.0, 32.0)
        p.update(mano(lado, b, 80 * rec, -42 * rec))
        m, rec = _ciclo((f - golpe_tras) % 1.0, 0.36, -30.0, 40.0)
        p.update(pata(lado, m, 48 * rec, -44 * rec, 32 * rec))
    # el lomo: encogido (hocico abajo) a 0.15, estirado a 0.65; y al final del
    # ciclo, cuando la mano izquierda ya ha despegado y la trasera aun no ha
    # caido (0.91 a 1.0), en el aire: el cuerpo sube
    enc = math.cos(2 * math.pi * (f - 0.15))
    vuela = max(0.0, math.cos(2 * math.pi * (f - 0.955))) ** 6
    return sumar(p, cuerpo(x=8.0 * enc, baja=7.0 - 2.5 * math.cos(4 * math.pi * (f - 0.05)) - 3.5 * vuela, avanza=3.0 * enc),
                 # la cabeza firme, mirando a la presa: compensa el cabeceo del lomo
                 cabeza(x=11 - 7.5 * enc, boca=8 + 8 * max(0.0, math.sin(w)), cuello=9 - 4.5 * enc, orejas=-24),
                 cola(sube=-2 + 4 * math.sin(w + 1.6), fase=w, onda=4, retraso=0.45))


anim('REPOSO', T_REPOSO, muestreada(pose_reposo, T_REPOSO, 16), loop=True)
anim('ANDAR', T_ANDAR, muestreada(pose_andar, T_ANDAR, 24), loop=True)
anim('CORRER', T_CORRER, muestreada(pose_correr, T_CORRER, 16), loop=True)

# ----------------------------------------------------------------------
#  Dormido como una esfinge ante su templo, y el despertar
# ----------------------------------------------------------------------
_esfinge = sumar(cuerpo(x=-2, baja=58),
                 mano(1, -68, 52, 16), mano(-1, -64, 50, 14),
                 pata(1, -58, 88, -66, 40, 8), pata(-1, -58, 88, -66, 40, 8),
                 cabeza(x=-14, boca=-14, cuello=-22, orejas=-10),
                 cola(sube=-4, lado=34, fase=0.0, onda=0))
_esfinge['cola2'] = r(-4, 26)
_esfinge['cola4'] = r(-2, 28)
_esfinge['cola6'] = r(0, 22)


def pose_dormido(s):
    w = 2 * math.pi * s / 6.0
    return sumar(_esfinge, cuerpo(baja=1.5 * math.sin(w)), cabeza(x=1.5 * math.sin(w + 0.5)),
                 {'cola6': r(0, 8 * math.sin(w * 0.5))})


anim('DORMIDO', 6.0, muestreada(pose_dormido, 6.0, 12), loop=True)

_ruge = sumar(cabeza(x=-26, boca=34, cuello=-8, orejas=-24), cuerpo(x=-4, avanza=4), mano(1, -6, 0), mano(-1, 4, 0),
              cola(sube=10, fase=0.0, onda=0))
_cl = [(0, _esfinge, 'c'),
       (0.6, sumar(_esfinge, cabeza(x=-10, orejas=14)), 'c'),
       (1.0, sumar(_esfinge, cabeza(x=-14, y=12, orejas=12)), 'c'),
       (1.5, sumar(cuerpo(x=6, baja=30), mano(1, -30, 30, 8), mano(-1, -40, 34, 10), pata(1, -40, 60, -40, 26),
                   pata(-1, -40, 60, -40, 26), cabeza(x=4, boca=-10)), 'c'),
       (2.0, sumar(cuerpo(x=-2, baja=4), mano(1, -10, 6), mano(-1, 6, 0), cabeza(x=-6, boca=6)), 'c'),
       (2.3, _ruge, 'c')]
temblor(_ruge, 2.35, 3.1, 0.07, {'cabeza': {'rot': (2.0, 2.0, 0)}, 'mandibula': {'rot': (3, 0, 0)}}, _cl)
_cl += [(3.6, N, 'c')]
anim('DESPERTAR', 3.6, _cl)

# ----------------------------------------------------------------------
#  Garra Terrestre: se echa atras con la garra derecha en alto y la clava
# ----------------------------------------------------------------------
T_GARRA = 0.42
T_GARRA_CARGA = 0.3
# Carga: se echa atras y tuerce el cuerpo, la zarpa derecha arriba y abierta
# hacia fuera, las garras en alto y la cabeza girada hacia la presa.
_carga_zarpa = sumar(cuerpo(x=-12, y=10, z=5, baja=-4, avanza=-8), mano(-1, -100, 32, -42, -28), mano(1, 8, -4, 2),
                     pata(1, 12, -4), pata(-1, 14, -4), cabeza(x=-10, y=-10, boca=22, cuello=-4, orejas=-22),
                     cola(sube=20, lado=-16, fase=0.0, onda=0))
# El tajo: la zarpa barre en diagonal de arriba a la derecha a abajo a la
# izquierda y el cuerpo entero entra detras de ella: se lanza, baja y gira.
_tajo = sumar(cuerpo(x=8, y=-9, z=-7, baja=6, avanza=15), mano(-1, -44, -6, 30, 22), mano(1, 14, -12, 8),
              pata(1, -14, 4), pata(-1, -18, 4), cabeza(x=0, y=7, boca=32, cuello=2, orejas=-26),
              cola(sube=6, lado=18, fase=0.0, onda=0))
_remate = sumar(cuerpo(x=9, y=-10, z=-4, baja=7, avanza=14), mano(-1, -16, -14, 40, 30), mano(1, 14, -10, 6),
                pata(1, -12, 4), pata(-1, -14, 4), cabeza(x=2, y=8, boca=20, cuello=4, orejas=-22),
                cola(sube=0, lado=22, fase=0.0, onda=0))
_cl = [(0, N, 'c'), (0.1, sumar(cuerpo(baja=3, avanza=-2), cabeza(boca=10)), 'c'), (T_GARRA_CARGA, _carga_zarpa, 'c')]
temblor(_carga_zarpa, 0.32, 0.38, 0.025, {'brazo_der': {'rot': (2, 0, 1.5)}}, _cl)
_cl += [(T_GARRA, _tajo, 'l'),
        (0.5, _remate, 'c'),
        (0.72, sumar(_remate, cabeza(x=-4, boca=-10)), 'c'),
        (1.05, N, 'c')]
anim('GARRA', 1.05, _cl)

# ----------------------------------------------------------------------
#  Terremoto Ancestral: se alza sobre las patas de atras y golpea con las dos
# ----------------------------------------------------------------------
T_TERREMOTO = 0.8
_te_alza = sumar(cuerpo(x=-32, baja=-15, avanza=-10), mano(1, -72, 40, -20, 8), mano(-1, -76, 42, -20, 8),
                 pata(1, 20, 10, -6), pata(-1, 20, 10, -6), cabeza(x=-22, boca=28, orejas=-22),
                 cola(sube=18, fase=0.0, onda=0))
# El golpe con todo el peso: el pecho cae casi al suelo detras de las zarpas.
_te_golpe = sumar(cuerpo(x=13, baja=10, avanza=10), mano(1, -40, -14, 36, 10), mano(-1, -42, -14, 36, 10),
                  pata(1, -18, 8), pata(-1, -18, 8), cabeza(x=2, boca=32, cuello=4, orejas=-26),
                  cola(sube=-4, fase=0.0, onda=0))
_cl = [(0, N, 'c'), (0.15, sumar(cuerpo(baja=9), cabeza(x=6)), 'c'), (0.6, _te_alza, 'c'),
       (T_TERREMOTO, _te_golpe, 'l')]
temblor(_te_golpe, 0.85, 1.3, 0.05, {'cuerpo': {'rot': (1.5, 0, 1.5)}, 'cabeza': {'rot': (2, 2, 0)}}, _cl)
_cl += [(1.5, sumar(_te_golpe, cuerpo(baja=-6), cabeza(x=-8, boca=-20)), 'c'), (1.9, N, 'c')]
anim('TERREMOTO', 1.9, _cl)

# ----------------------------------------------------------------------
#  Rugido (el del Sello y los cambios de fase) y el Sello sosteniendo
# ----------------------------------------------------------------------
T_RUGIDO = 0.5
_cl = [(0, N, 'c'), (0.3, sumar(cuerpo(x=6, baja=6), cabeza(x=10, boca=-6)), 'c'), (T_RUGIDO, _ruge, 'c')]
temblor(_ruge, 0.55, 1.6, 0.07, {'cabeza': {'rot': (2.5, 2.0, 0)}, 'mandibula': {'rot': (3, 0, 0)}}, _cl)
_cl += [(2.0, N, 'c')]
anim('RUGIDO', 2.0, _cl)

_carga = sumar(cuerpo(x=4, baja=10), mano(1, -10, 8, 0, 10), mano(-1, -10, 8, 0, 10), pata(1, -4, 6, 0, 0, 8),
               pata(-1, -4, 6, 0, 0, 8), cabeza(x=6, boca=22, cuello=6, orejas=-24))


def pose_sello(s):
    w = 2 * math.pi * s / 2.4
    return sumar(_carga, cabeza(x=2 * math.sin(w * 2), y=8 * math.sin(w), boca=4 * math.sin(w * 3)),
                 cuerpo(baja=1.5 * math.sin(w * 2)), cola(sube=10, fase=w * 2, onda=22, retraso=0.5))


anim('SELLO', 2.4, muestreada(pose_sello, 2.4, 16), loop=True)

# ----------------------------------------------------------------------
#  Cataclismo de Jade: se alza y ruge al cielo; lo sostiene mientras caen
#  los fragmentos; y vuelve al suelo de un golpe
# ----------------------------------------------------------------------
_alzado = sumar(cuerpo(x=-32, baja=-18, avanza=-2), mano(1, -50, 56, 10, -10), mano(-1, -40, 48, 10, 10),
                pata(1, 30, 14, -10, 6), pata(-1, 26, 14, -10, 6), cabeza(x=-30, boca=32, cuello=-10, orejas=-24),
                cola(sube=30, fase=0.0, onda=0))
_alzado['cola2'] = r(14)
T_CATACLISMO = 1.3
_cl = [(0, N, 'c'), (0.3, sumar(cuerpo(baja=10), pata(1, -10, 20, -10), pata(-1, -10, 20, -10)), 'c'),
       (0.9, sumar(_alzado, cabeza(boca=-30)), 'c'), (T_CATACLISMO, _alzado, 'c')]
temblor(_alzado, 1.35, 2.3, 0.07, {'cabeza': {'rot': (2.5, 2.5, 0)}, 'mandibula': {'rot': (3, 0, 0)}}, _cl)
_cl += [(2.6, _alzado, 'c')]
anim('CATACLISMO', 2.6, _cl)


def pose_alzado(s):
    w = 2 * math.pi * s / 2.0
    return sumar(_alzado, cuerpo(x=2 * math.sin(w), z=2 * math.sin(w * 0.5)), cabeza(y=10 * math.sin(w * 0.5), boca=-8 + 6 * math.sin(w)),
                 mano(1, 8 * math.sin(w), 0), mano(-1, -8 * math.sin(w), 0))


anim('CATACLISMO_SOSTIENE', 2.0, muestreada(pose_alzado, 2.0, 12), loop=True)
T_BAJA = 0.55
# Vuelve al suelo sin moverse del sitio: las zarpas de delante caen algo por
# delante de donde estaban (no hundidas en el suelo) y las de atras no resbalan.
_aterriza = sumar(cuerpo(x=2, baja=0, avanza=4), mano(1, -22, 10, 6), mano(-1, -18, 8, 6), pata(1, -4, 4), pata(-1, -4, 4),
                  cabeza(x=10, boca=26, cuello=6, orejas=-20), cola(sube=10, fase=0.0, onda=0))
anim('CATACLISMO_BAJA', 1.3, [(0, _alzado, 'c'), (0.3, sumar(_alzado, cuerpo(x=10, baja=6, avanza=16)), 'c'),
                              (T_BAJA, _aterriza, 'l'), (0.85, sumar(_aterriza, cabeza(boca=-24)), 'c'), (1.3, N, 'c')])

# ----------------------------------------------------------------------
#  Aturdido (el Sello roto) y paralizado (el Cataclismo sin victimas)
# ----------------------------------------------------------------------
_tirado = sumar(cuerpo(x=6, z=10, baja=52, lado=4), mano(1, -50, 40, 10, 14), mano(-1, -36, 30, 10, -6),
                pata(1, -40, 70, -50, 30, 14), pata(-1, -36, 66, -46, 26, -4),
                cabeza(x=18, y=14, z=10, boca=10, cuello=20, orejas=10), cola(sube=-8, lado=26, fase=0.0, onda=0))
_cl = [(0, N, 'c'), (0.3, sumar(cuerpo(z=-14, lado=-6), cabeza(x=-20, boca=30)), 'c'), (0.8, _tirado, 'l'),
       (0.95, sumar(_tirado, cuerpo(baja=-4)), 'c'), (1.1, _tirado, 'c')]
for k in range(6):
    tt = 1.6 + k * 0.6
    _cl.append((tt, sumar(_tirado, cabeza(x=-4 if k % 2 == 0 else 2, y=4 if k % 2 else -4, boca=6 if k % 2 == 0 else 0)), 'c'))
_cl += [(5.2, sumar(cuerpo(x=8, baja=28), mano(1, -30, 30), mano(-1, -30, 30), pata(1, -30, 50, -30, 20),
                    pata(-1, -30, 50, -30, 20), cabeza(x=10)), 'c'), (6.0, N, 'c')]
anim('ATURDIDO', 6.0, _cl)

_rigido = sumar(cuerpo(x=3, baja=0), mano(1, -14, 10), mano(-1, -8, 6), pata(1, -6, 6), pata(-1, -6, 6),
                cabeza(x=12, boca=14, cuello=8, orejas=-20), cola(sube=-10, fase=0.0, onda=0))
_cl = [(0, N, 'c'), (0.4, _rigido, 'c')]
temblor(_rigido, 0.5, 9.0, 0.09, {'cuerpo': {'rot': (0.6, 0.0, 0.8)}, 'cabeza': {'rot': (0.8, 1.2, 0)},
                                   'cola0': {'rot': (0, 2, 0)}}, _cl)
_cl += [(9.3, sumar(_rigido, cuerpo(z=8), cabeza(y=20)), 'c'), (9.6, sumar(_rigido, cuerpo(z=-8), cabeza(y=-20)), 'c'),
        (10.0, N, 'c')]
anim('PARALIZADO', 10.0, _cl)

# ----------------------------------------------------------------------
#  El salto de la fase IV: se encoge, salta con las zarpas por delante y cae
# ----------------------------------------------------------------------
T_DESPEGA = 0.36
T_ATERRIZA = 1.2
_encoge = sumar(cuerpo(x=8, baja=18, avanza=-6), mano(1, 14, 20), mano(-1, 14, 20), pata(1, -30, 50, -36, 24),
                pata(-1, -30, 50, -36, 24), cabeza(x=10, boca=10, orejas=-24), cola(sube=-10, fase=0.0, onda=0))
_vuela = sumar(cuerpo(x=-10, baja=-10, avanza=6), mano(1, -70, -10, -20), mano(-1, -66, -6, -20),
               pata(1, 50, -10, 20, 10), pata(-1, 46, -10, 20, 10), cabeza(x=-8, boca=32, orejas=-28),
               cola(sube=12, fase=0.0, onda=0))
anim('SALTO', 1.8, [(0, N, 'c'), (0.3, _encoge, 'c'), (T_DESPEGA, sumar(_encoge, cuerpo(baja=-6)), 'l'),
                    (0.52, _vuela, 'c'), (0.85, sumar(_vuela, cuerpo(x=-4)), 'c'),
                    (1.08, sumar(_vuela, mano(1, 20, 0), mano(-1, 20, 0), cuerpo(x=6)), 'c'),
                    (T_ATERRIZA, _te_golpe, 'l'), (1.4, sumar(_te_golpe, cuerpo(baja=4)), 'c'), (1.8, N, 'c')])

# ----------------------------------------------------------------------
#  Tambaleo (cambio de fase): la grieta le cruza el cuerpo, se tambalea y ruge
# ----------------------------------------------------------------------
_ta = sumar(cuerpo(x=-6, z=-14, lado=-6), cabeza(x=-18, y=16, boca=26, orejas=-20), mano(1, -20, 10, 0, 14),
            pata(-1, 10, 0, 0, 0, 10))
_cl = [(0, N, 'c'), (0.1, _ta, 'l')]
temblor(_ta, 0.18, 0.9, 0.06, {'cuerpo': {'rot': (0, 0, 5)}, 'cabeza': {'rot': (3, 4, 0)}}, _cl)
_cl += [(1.1, _ruge, 'c')]
temblor(_ruge, 1.15, 1.9, 0.07, {'cabeza': {'rot': (2, 2, 0)}}, _cl)
_cl += [(2.5, N, 'c')]
anim('TAMBALEO', 2.5, _cl)

# ----------------------------------------------------------------------
#  Liberacion: el ultimo rugido, se tumba despacio como una esfinge y alza
#  la cabeza al sol, respirando cada vez mas despacio
# ----------------------------------------------------------------------
_orgullo = sumar(_esfinge, cabeza(x=6, boca=4, cuello=10, orejas=8))
anim('LIBERACION', 10.0, [(0, N, 'c'), (0.5, _ruge, 'c'), (1.5, sumar(_ruge, cabeza(boca=-30)), 'c'),
                          (2.4, sumar(cuerpo(x=6, baja=24), mano(1, -30, 30), mano(-1, -30, 30), pata(1, -30, 50, -30, 20),
                                      pata(-1, -30, 50, -30, 20), cabeza(x=14, boca=-10)), 'c'),
                          (4.0, sumar(_esfinge, cabeza(x=10)), 'c'),
                          (5.5, _orgullo, 'c'), (7.5, sumar(_orgullo, cuerpo(baja=1.5)), 'c'), (10.0, _orgullo, 'c')])

# ----------------------------------------------------------------------
#  Embestida de Jade: se agazapa y rasca el suelo con la mano derecha
#  mientras la flecha se llena; carga al galope con la cabeza baja y los
#  sables por delante; y frena derrapando con las cuatro, jadeando despues
# ----------------------------------------------------------------------
T_EMB_AVISO = 1.2
_agazapado = sumar(cuerpo(x=3, baja=12, avanza=-5), mano(1, -12, 18, 8, 6), mano(-1, -14, 20, 8, -6),
                   pata(1, -30, 50, -36, 24), pata(-1, -30, 50, -36, 24),
                   cabeza(x=0, boca=12, cuello=2, orejas=-20), cola(sube=8, fase=0.0, onda=0))
_rasca_alza = mano(-1, -34, 46, -24)            # la mano derecha, adelantada y en alto
_rasca_tira = mano(-1, 26, -8, 22)              # la arrastra hacia atras rayando el suelo
_resorte = sumar(cuerpo(x=4, baja=15, avanza=-9), mano(1, -16, 22, 10, 8), mano(-1, -16, 22, 10, -8),
                 pata(1, -36, 58, -42, 28), pata(-1, -36, 58, -42, 28),
                 cabeza(x=0, boca=30, cuello=0, orejas=-28), cola(sube=14, lado=0, fase=0.0, onda=0))
_cl = [(0, N, 'c'), (0.15, _agazapado, 'c'),
       (0.3, sumar(_agazapado, _rasca_alza, cola(lado=22, fase=0.0, onda=0)), 'c'),
       (0.42, sumar(_agazapado, _rasca_tira, cola(lado=-18, fase=0.0, onda=0)), 'l'),
       (0.56, sumar(_agazapado, _rasca_alza, cola(lado=20, fase=0.0, onda=0)), 'c'),
       (0.68, sumar(_agazapado, _rasca_tira, cola(lado=-16, fase=0.0, onda=0)), 'l'),
       (0.95, _resorte, 'c')]
temblor(_resorte, 0.98, T_EMB_AVISO - 0.02, 0.04, {'cuerpo': {'rot': (0.8, 0, 0.6)}, 'cola0': {'rot': (0, 4, 0)}}, _cl)
_cl += [(T_EMB_AVISO, _resorte, 'c')]
anim('EMBESTIDA_AVISO', T_EMB_AVISO, _cl)

T_EMBESTIDA = 0.56


def pose_carga(s):
    """El galope de la carga: el mismo ciclo, mas rapido, con la cabeza baja y
    los sables por delante, la boca abierta y las orejas pegadas."""
    return sumar(pose_correr(s * T_CORRER / T_EMBESTIDA), cabeza(x=10, boca=16, cuello=6, orejas=-10), cuerpo(x=3, baja=2))


anim('EMBESTIDA', T_EMBESTIDA, muestreada(pose_carga, T_EMBESTIDA, 14), loop=True)

T_FRENA_PARA = 0.7
_derrapa = sumar(cuerpo(x=-6, z=4, baja=11, avanza=-6), mano(1, -40, 6, 22, 12), mano(-1, -38, 6, 22, -12),
                 pata(1, -30, 50, -30, 20, 6), pata(-1, -28, 50, -30, 20, 6),
                 cabeza(x=-6, boca=24, cuello=-2, orejas=-20), cola(sube=26, lado=12, fase=0.0, onda=0))
_jadea = sumar(cuerpo(x=6, baja=9, avanza=2), mano(1, -8, 6), mano(-1, -6, 6), pata(1, -6, 10, -6, 4), pata(-1, -6, 10, -6, 4),
               cabeza(x=12, boca=20, cuello=10, orejas=-6), cola(sube=-2, fase=0.0, onda=0))
_cl = [(0, pose_carga(0.0), 'c'), (0.12, _derrapa, 'c')]
temblor(_derrapa, 0.16, 0.6, 0.05, {'cuerpo': {'rot': (0.8, 0.5, 1.2)}, 'cabeza': {'rot': (1.5, 1.5, 0)}}, _cl)
_cl += [(T_FRENA_PARA, _jadea, 'c')]
# el jadeo: la boca se abre y se cierra y los costados suben y bajan
for k in range(4):
    tt = T_FRENA_PARA + 0.12 + k * 0.22
    _cl.append((round(tt, 3), sumar(_jadea, cabeza(boca=-12 if k % 2 == 0 else 6, x=-2 if k % 2 == 0 else 2),
                                    cuerpo(baja=-2 if k % 2 == 0 else 1)), 'c'))
_cl += [(1.7, N, 'c')]
anim('EMBESTIDA_FRENA', 1.7, _cl)

# ----------------------------------------------------------------------
#  Estampado: la Embestida contra un muro. Le rebota la cabeza, se tambalea
#  de lado y sacude la cabeza, aturdido
# ----------------------------------------------------------------------
_choca = sumar(cuerpo(x=-12, baja=4, avanza=-9), mano(1, -40, 10, 20, 16), mano(-1, -38, 10, 20, -16),
               pata(1, -10, 20, -10, 6), pata(-1, -10, 20, -10, 6),
               cabeza(x=-26, y=10, boca=22, cuello=-10, orejas=12), cola(sube=20, lado=-20, fase=0.0, onda=0))
_tambalea = sumar(cuerpo(x=3, z=-12, baja=6, lado=-4), mano(1, -20, 20, 0, 14), mano(-1, -10, 12),
                  pata(1, -16, 30, -16, 10, 8), pata(-1, -8, 16), cabeza(x=2, y=-14, z=10, boca=10, cuello=2, orejas=10),
                  cola(sube=-6, lado=20, fase=0.0, onda=0))
_cl = [(0, pose_carga(0.0), 'c'), (0.08, _choca, 'l'), (0.4, _tambalea, 'c')]
temblor(_tambalea, 0.5, 1.6, 0.09, {'cabeza': {'rot': (0, 14, 4)}, 'cuello': {'rot': (0, 6, 0)}}, _cl)
_cl += [(2.0, N, 'c')]
anim('ESTAMPADO', 2.0, _cl)

# ----------------------------------------------------------------------
#  Tumba de Raices: clava las garras abiertas y ruge contra el suelo
#  mientras el circulo se llena (6 s fijos, no van con la fase), con un
#  respiro a mitad y un segundo rugido; al llenarse, se alza de golpe y la
#  tierra revienta; y se recompone
# ----------------------------------------------------------------------
T_TUMBA_ESTALLA = 6.0
T_TUMBA_RUGE_2 = 3.45
_planta = sumar(cuerpo(x=6, baja=11, avanza=4), mano(1, -20, 22, 30, 22), mano(-1, -20, 22, 30, -22),
                pata(1, -22, 40, -30, 20, 10), pata(-1, -22, 40, -30, 20, 10),
                cabeza(x=4, boca=8, cuello=4, orejas=-24), cola(sube=20, fase=0.0, onda=0))
_ruge_suelo = sumar(_planta, cabeza(x=6, boca=28, cuello=2, orejas=-4))
_alza_tumba = sumar(cuerpo(x=-16, baja=-6, avanza=-2), mano(1, -54, 30, -10, 14), mano(-1, -52, 30, -10, -14),
                    pata(1, 10, 6, -4), pata(-1, 10, 6, -4), cabeza(x=-24, boca=34, cuello=-8, orejas=-26),
                    cola(sube=26, fase=0.0, onda=0))
_respira = sumar(_planta, cuerpo(baja=-2), cabeza(x=-6, boca=6, cuello=4))
_tiembla_tumba = {'cuerpo': {'rot': (0.8, 0, 0.8)}, 'cabeza': {'rot': (2.5, 2.5, 0)}, 'mandibula': {'rot': (3, 0, 0)}}
_cl = [(0, N, 'c'), (0.35, _planta, 'c'), (0.6, _ruge_suelo, 'c')]
temblor(_ruge_suelo, 0.65, 2.95, 0.07, _tiembla_tumba, _cl)
_cl += [(3.15, _respira, 'c'), (T_TUMBA_RUGE_2, _ruge_suelo, 'c')]
temblor(_ruge_suelo, T_TUMBA_RUGE_2 + 0.05, T_TUMBA_ESTALLA - 0.2, 0.07, _tiembla_tumba, _cl)
_cl += [(T_TUMBA_ESTALLA - 0.15, sumar(_planta, cuerpo(baja=3)), 'c'), (T_TUMBA_ESTALLA, _alza_tumba, 'l'),
        (T_TUMBA_ESTALLA + 0.4, _te_golpe, 'c'), (T_TUMBA_ESTALLA + 1.1, N, 'c')]
anim('TUMBA', T_TUMBA_ESTALLA + 1.1, _cl)

# ----------------------------------------------------------------------
#  De poses a canales
# ----------------------------------------------------------------------
NULO = {'rot': (0, 0, 0), 'pos': (0, 0, 0), 'esc': (1, 1, 1)}


def canales(a):
    usados = {}
    for _, p, _ in a['claves']:
        for pieza, d in p.items():
            for tipo in d:
                if tipo in NULO:
                    usados.setdefault((pieza, tipo), True)
    out = []
    for (pieza, tipo) in usados:
        if pieza not in rj.PARTES:
            continue
        ks = [(t, tuple(p.get(pieza, {}).get(tipo, NULO[tipo])), i) for t, p, i in a['claves']]
        if all(np.allclose(k[1], NULO[tipo]) for k in ks):
            continue
        out.append((pieza, tipo, ks))
    return out


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


def pose_en(nombre, s):
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
         ' * Las animaciones de Rajang, el Jaguar de Jade. GENERADO por',
         ' * materiales/generadores/rajang_juego_anim.py: no se editan a mano. El servidor',
         ' * saca de las mismas poses los puntos y los ticks de cada golpe (RajangGeometria).',
         ' */',
         'public final class RajangAnimaciones {', '']
    for nombre in ANIMS:
        L.append(f'    public static final AnimationDefinition {nombre} = {nombre.lower()}();')
    L += ['', '    private RajangAnimaciones() {', '    }', '',
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
    return rj.a_bloques(rj.punto(pose, pieza, local))


def java_geometria():
    puntos = {
        'CABEZA': p_bloques(None, 0, 'cabeza', (0, -8, -30)),
        'BOCA': p_bloques(None, 0, 'cabeza', (0, 6, -54)),
        'BOCA_RUGIDO': p_bloques('RUGIDO', 1.0, 'cabeza', (0, 6, -54)),
        'BOCA_CATACLISMO': p_bloques('CATACLISMO_SOSTIENE', 0, 'cabeza', (0, 6, -54)),
        'PECHO': p_bloques(None, 0, 'sol', (0, 3, -118.5)),
        'LOMO': p_bloques(None, 0, 'cuerpo', (0, -36, -70)),
        'GRUPA': p_bloques(None, 0, 'cuerpo', (0, -4, 40)),
        'COSTILLAS': p_bloques(None, 0, 'cuerpo', (0, -4, -30)),
        'ZARPA_GARRA': p_bloques('GARRA', T_GARRA, 'mano_der', (0, 8, -8)),
        'ZARPA_CARGA': p_bloques('GARRA', T_GARRA_CARGA, 'mano_der', (0, 8, -8)),
        'ZARPA_RASCA': p_bloques('EMBESTIDA_AVISO', 0.42, 'mano_der', (0, 8, -8)),
        'ZARPA_IZQ_TERREMOTO': p_bloques('TERREMOTO', T_TERREMOTO, 'mano_izq', (0, 8, -8)),
        'ZARPA_DER_TERREMOTO': p_bloques('TERREMOTO', T_TERREMOTO, 'mano_der', (0, 8, -8)),
        'ZARPA_IZQ': p_bloques(None, 0, 'mano_izq', (0, 8, -8)),
        'ZARPA_DER': p_bloques(None, 0, 'mano_der', (0, 8, -8)),
        'PATA_IZQ': p_bloques(None, 0, 'pie_izq', (0, 8, -8)),
        'PATA_DER': p_bloques(None, 0, 'pie_der', (0, 8, -8)),
        'PUNTA_COLA': p_bloques(None, 0, 'punta_cola', (0, 0, 6)),
    }

    def tick(s):
        return int(round(s * 20))
    tiempos = {
        'DURACION_DESPERTAR': tick(ANIMS['DESPERTAR']['dur']), 'DESPERTAR_SE_ALZA': tick(1.5), 'DESPERTAR_RUGE': tick(2.3),
        'DURACION_GARRA': tick(ANIMS['GARRA']['dur']), 'GARRA_ALZA': tick(0.12), 'GARRA_GOLPE': tick(T_GARRA),
        'DURACION_TERREMOTO': tick(ANIMS['TERREMOTO']['dur']), 'TERREMOTO_GOLPE': tick(T_TERREMOTO),
        'DURACION_RUGIDO': tick(ANIMS['RUGIDO']['dur']), 'RUGIDO_RUGE': tick(T_RUGIDO),
        'DURACION_CATACLISMO': tick(ANIMS['CATACLISMO']['dur']), 'CATACLISMO_RUGE': tick(T_CATACLISMO),
        'DURACION_CATACLISMO_BAJA': tick(ANIMS['CATACLISMO_BAJA']['dur']), 'CATACLISMO_BAJA_GOLPE': tick(T_BAJA),
        'DURACION_ATURDIDO': tick(ANIMS['ATURDIDO']['dur']), 'ATURDIDO_CAE': tick(0.8),
        'DURACION_PARALIZADO': tick(ANIMS['PARALIZADO']['dur']),
        'DURACION_SALTO': tick(ANIMS['SALTO']['dur']), 'SALTO_DESPEGA': tick(T_DESPEGA), 'SALTO_ATERRIZA': tick(T_ATERRIZA),
        'DURACION_TAMBALEO': tick(ANIMS['TAMBALEO']['dur']), 'TAMBALEO_RUGE': tick(1.1),
        'DURACION_LIBERACION': tick(ANIMS['LIBERACION']['dur']), 'LIBERACION_OJOS_ORO': tick(4.0),
        'PERIODO_ANDAR': tick(T_ANDAR), 'PERIODO_CORRER': tick(T_CORRER),
        'DURACION_EMBESTIDA_AVISO': tick(T_EMB_AVISO), 'EMBESTIDA_RASCA_1': tick(0.42), 'EMBESTIDA_RASCA_2': tick(0.68),
        'DURACION_EMBESTIDA_FRENA': tick(ANIMS['EMBESTIDA_FRENA']['dur']), 'EMBESTIDA_FRENA_PARA': tick(T_FRENA_PARA),
        'DURACION_ESTAMPADO': tick(ANIMS['ESTAMPADO']['dur']),
        'DURACION_TUMBA': tick(ANIMS['TUMBA']['dur']), 'TUMBA_ESTALLA': tick(T_TUMBA_ESTALLA), 'TUMBA_RUGE_2': tick(T_TUMBA_RUGE_2),
    }
    # Lo que corren las zarpas que apoyan, en bloques por tick con el reloj a su
    # ritmo: el cliente adelanta cada reloj lo justo para que no resbalen.
    zancadas = {'ZANCADA_ANDAR': zancada('ANDAR'), 'ZANCADA_CORRER': zancada('CORRER')}
    L = ['package com.atalaya.entity;', '',
         'import net.minecraft.world.phys.Vec3;', '',
         '/**',
         ' * Medidas de Rajang que comparten servidor y cliente. GENERADO por',
         ' * materiales/generadores/rajang_juego_anim.py desde las mismas poses que las',
         ' * animaciones: si una animacion cambia, esto cambia.',
         ' *',
         ' * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,',
         ' * y hacia arriba desde los pies, z hacia delante. RajangEntity los pasa al',
         ' * mundo con el giro del cuerpo.',
         ' */',
         'public final class RajangGeometria {', '',
         '    private RajangGeometria() {', '    }', '']
    for k, (x, y, z) in puntos.items():
        L.append(f'    public static final Vec3 {k} = new Vec3({x:.3f}, {y:.3f}, {z:.3f});')
    L.append('')
    for k, v in tiempos.items():
        L.append(f'    public static final int {k} = {v};')
    L.append('')
    for k, v in zancadas.items():
        L.append(f'    public static final float {k} = {fj(v)};')
    L.append('}')
    return '\n'.join(L) + '\n', puntos, tiempos


def zancada(nombre, pieza='pie_izq', local=(0, 8, -8), n=400):
    """Lo deprisa que va hacia atras la zarpa trasera mientras apoya (bloques por
    tick a ritmo nominal), que es lo que tiene que avanzar el cuerpo para que no
    resbale. Con un 10 % menos: la zarpa no apoya plana todo el apoyo."""
    T = ANIMS[nombre]['dur']
    ps = np.array([rj.a_bloques(rj.punto(pose_en(nombre, T * k / n), pieza, local)) for k in range(n)])
    dz = np.diff(ps[:, 2]) / (T / n * 20)
    apoyo = ps[:-1, 1] < ps[:, 1].min() + 0.08
    return round(float(-dz[apoyo].mean()) * 0.9, 3)


# ----------------------------------------------------------------------
#  Hojas de control
# ----------------------------------------------------------------------
LUCES = [((-0.5, 0.8, -0.6), (1.0, 0.97, 0.9), 0.9, 'llave'), ((0.7, 0.3, 0.6), (0.5, 1.0, 0.6), 0.5, 'contra')]


def render_pose(pose, tex, emis, uv, alto, W=360, H=300, guinada=-50, ojo=(-16, 7.0, -20), objetivo=(0, 4.5, -2), fov=50):
    cam = vr.Camara(ojo=ojo, objetivo=objetivo, fov=fov, ancho=W, alto=H)
    lz = vr.Lienzo(W, H)
    M = vr.entidad_a_mundo(0, 0, 0, guinada)
    g = np.zeros((16, 16, 4), np.uint8)
    g[...] = (196, 204, 196, 255)
    g[0, :] = g[:, 0] = (150, 160, 150, 255)
    for i in range(-16, 16):
        for j in range(-16, 16):
            Pq = [(i, 0, j), (i + 1, 0, j), (i + 1, 0, j + 1), (i, 0, j + 1)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [Pq[k] for k in tri], [((0, 0), (1, 0), (1, 1), (0, 1))[k] for k in tri], g, np.array([0.9, 0.9, 0.9]))
    for Pq, UV, _, mat in rj.quads(pose, uv, alto, M):
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), LUCES, (0.36, 0.38, 0.36))
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[k] for k in tri], [UV[k] for k in tri], tex, luz, emis)
    col = np.clip(lz.color + lz.emis * 0.35, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.3, 0.36, 0.32]) * (1 - a)
    return Image.fromarray((arr * 255).astype(np.uint8))


def hoja(nombre, tiempos, tex, emis, uv, alto, out, **kw):
    from PIL import ImageDraw
    ims = []
    for s in tiempos:
        im = render_pose(pose_en(nombre, s), tex, emis, uv, alto, **kw)
        ImageDraw.Draw(im).text((8, 6), f'{nombre} {s:.2f}s', fill=(230, 240, 230))
        ims.append(im)
    W, H = ims[0].size
    hojai = Image.new('RGB', (W * len(ims), H), (255, 255, 255))
    for i, im in enumerate(ims):
        hojai.paste(im, (i * W, 0))
    hojai.save(os.path.join(out, f'rajang_anim_{nombre.lower()}.png'))


# ----------------------------------------------------------------------
if __name__ == '__main__':
    uv, alto = rj.empaquetar()
    TEX = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/rajang')
    os.makedirs(TEX, exist_ok=True)
    solo_codigo = os.environ.get('RAJANG_SIN_TEXTURAS')
    if not solo_codigo:
        for fase in (1, 2, 3, 4, 'libre'):
            base, brillo = rj.pintar_atlas(uv, alto, fase)
            nombre = f'f{fase}' if isinstance(fase, int) else fase
            Image.fromarray(base).save(os.path.join(TEX, f'rajang_{nombre}.png'))
            Image.fromarray(brillo).save(os.path.join(TEX, f'rajang_brillo_{nombre}.png'))
            print('atlas', nombre, flush=True)
    CLI = os.path.join(RAIZ, 'src/client/java/com/atalaya/client')
    with open(os.path.join(CLI, 'RajangMalla.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(rj.java_malla(uv, alto))
    with open(os.path.join(CLI, 'RajangAnimaciones.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(java_anims())
    geo, puntos, tiempos = java_geometria()
    with open(os.path.join(RAIZ, 'src/main/java/com/atalaya/entity/RajangGeometria.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(geo)
    print('atlas', rj.ANCHO_ATLAS, 'x', alto, '|', len(rj.ORDEN), 'piezas |', len(ANIMS), 'animaciones')
    for k, v in puntos.items():
        print(f'  {k:22s} izq {v[0]:6.2f}  alto {v[1]:6.2f}  frente {v[2]:6.2f}')

    if RENDERS:
        os.makedirs(RENDERS, exist_ok=True)
        tex = np.array(Image.open(os.path.join(TEX, 'rajang_f1.png')).convert('RGBA'))
        emis = np.array(Image.open(os.path.join(TEX, 'rajang_brillo_f1.png')).convert('RGBA'))
        solo = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ANIMS)
        for nombre in solo:
            a = ANIMS[nombre]
            ts = [a['dur'] * k / 5 for k in range(6)] if not a['loop'] else [a['dur'] * k / 6 for k in range(6)]
            hoja(nombre, ts, tex, emis, uv, alto, RENDERS)
            print('hoja', nombre, flush=True)

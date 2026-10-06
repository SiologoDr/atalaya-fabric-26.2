"""
Animaciones de Novilis, escritas pose a pose y pasadas por fisica (segunda
version, octubre de 2026: "rapidas, fluidas y con anatomia de verdad").

Las poses dicen lo que HACE el caballero; novilis_fisica.py anade lo que su
cuerpo no puede dejar de hacer (pies plantados por cinematica inversa, capa y
tabardo con inercia, cabeza y torso que siguen a la pelvis con retraso).

Como se escribe una animacion:
  anim(NOMBRE, duracion, [(t, pose, curva), ...])
  pose   lo que se suma al boceto (rot en grados, pos en px con Y abajo), con
         los brazos colocados por cinematica inversa (ik: donde cae el puno) y
         la espada apuntada. Ademas, pies(...) dice donde apoya cada pie: si un
         pie cambia de sitio entre dos claves, da el paso (lo levanta en arco).
         Si una clave no dice nada de los pies, se quedan donde estaban.
  curva  como se llega a ESA clave desde la anterior:
           'e'  arranca y frena suave (anticipaciones, recogidas)
           'i'  acelera hasta el final (el golpe: llega a toda velocidad)
           'o'  sale rapido y frena (el impulso que se apaga, el rebote)
           'b'  sale rapido, se pasa un poco y vuelve (el peso que se asienta)
           'c'  pasa de largo, suave (Catmull-Rom: ciclos, respiracion)
           'l'  lineal

La guardia (la espada baja en la derecha) y la postura de pie (los pies algo
abiertos y escalonados, las rodillas un poco dobladas) van HORNEADAS en la
malla: son su reposo. Toda animacion que no es un bucle empieza y acaba en ese
reposo, y asi el paso de andar a atacar (que el juego funde en 4-5 ticks) no
da saltos.

De aqui salen NovilisAnimaciones.java (los canales, ya horneados, como texto
compacto), NovilisGeometria.java (duraciones, ticks de cada golpe, puntos del
cuerpo, el paso), NovilisEstelas.java (por donde pasa la hoja, para la estela
del cliente), NovilisMalla.java y las pieles.

Uso: python novilis_juego_anim.py <raiz del proyecto> [carpeta de hojas] [ANIM,ANIM]
     NOVILIS_SIN_TEXTURAS=1 no rehace las pieles.
"""
import math, os, sys, copy
import numpy as np
from PIL import Image
import fuego_modelo as fm
import novilis_juego as nj
import novilis_fisica as nf

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


def sumar(base, extra):
    """Como mezcla, pero las rotaciones y posiciones se SUMAN a las de base."""
    out = copy.deepcopy(base)
    for k, v in extra.items():
        d = out.setdefault(k, {})
        for tipo, val in v.items():
            if tipo in ('rot', 'pos') and tipo in d:
                d[tipo] = tuple(d[tipo][i] + val[i] for i in range(3))
            else:
                d[tipo] = copy.deepcopy(val)
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
#  La postura de reposo (horneada en la malla)
# ----------------------------------------------------------------------
# Hombros en (+-21, -86, 0); de hombro a puno caben 49 px.
GUARDIA = ik({}, izq=(26, -44, -6), der=(-25, -46, -20), espada=(-0.14, 0.55, -0.82))
HORNEADAS = ['brazo_izq', 'antebrazo_izq', 'brazo_der', 'antebrazo_der', 'agarre']
# De pie: la pelvis 2,5 px mas baja (rodillas algo dobladas), el pie izquierdo un
# poco adelantado y el derecho atras, las puntas un poco hacia fuera.
PELVIS_REPOSO = 2.5
PIE_REPOSO = {'izq': ((11.0, 24.0, -5.0), 0.0, -6.0), 'der': ((-11.0, 24.0, 6.0), 0.0, 6.0)}


def pies(izq=None, der=None):
    """Donde apoya cada pie: (x, z) o (x, z, inclinacion, giro, alto). Alto en px
    sobre el suelo (para un pie en el aire). Inclinacion en grados respecto al
    suelo: positiva, el talon arriba y la punta abajo (de puntillas, de rodilla);
    negativa, la punta arriba (el talon que entra). El pivote del pie sube solo
    lo que haga falta para que ni la punta ni el talon se metan en el suelo."""
    out = {}
    for lado, v in (('izq', izq), ('der', der)):
        if v is None:
            continue
        x, z = v[0], v[1]
        pie = v[2] if len(v) > 2 else 0.0
        giro = v[3] if len(v) > 3 else PIE_REPOSO[lado][2]
        alto = v[4] if len(v) > 4 else 0.0
        out['apoyo_' + lado] = {'en': (x, nf.SUELO - alto, z), 'pie': pie, 'giro': giro}
    return out


PIES_REPOSO = pies(izq=(11.0, -5.0), der=(-11.0, 6.0))
CAPA_VIENTO = {'capa_1': r(20), 'capa_2': r(10), 'capa_3': r(12)}


def a_juego(p):
    """De la pose del boceto a la del juego: menos la guardia horneada (brazos)."""
    out = {}
    for k, v in p.items():
        d = dict(v)
        if k in HORNEADAS and 'rot' in d:
            g = GUARDIA[k]['rot']
            d['rot'] = tuple(d['rot'][i] - g[i] for i in range(3))
        out[k] = d
    for k in HORNEADAS:
        if k not in out:
            out[k] = {'rot': (0.0, 0.0, 0.0)}
    return out


# ----------------------------------------------------------------------
#  Posturas de los ataques (las de la ficha, con los pies y la pelvis)
# ----------------------------------------------------------------------
G = GUARDIA

# De rodilla: la izquierda delante con el pie plano, la derecha en el suelo con
# los dedos apoyados.
RODILLA = mezcla({'pelvis': P(0, 30, 0), 'tabardo': r(-60), 'capa_1': r(8), 'capa_2': r(20), 'capa_3': r(40)},
                 pies(izq=(11, -30, 0, -4), der=(-10, 30, 62, 4)))
ALZA = ik(mezcla({'cabeza': r(-24), 'torso': r(-6), 'pelvis': P(0, -1, 0)}, CAPA_VIENTO),
          der=(0, -128, -8), izq=(1, -117, -8), espada=(0, -1, 0.02))
ARRODILLADO_CLAVA = ik(mezcla(RODILLA, {'torso': r(12), 'cabeza': r(10)}), der=(0, -12, -32), izq=(0, -22, -32),
                       espada=(0, 1, 0.05))
ARRODILLADO_SOL = ik(mezcla(RODILLA, {'torso': r(8), 'cabeza': r(-30)}), der=(0, -20, -30), izq=(0, -30, -30),
                     espada=(0, 1, 0.05))
DORMIDO = ik(mezcla(RODILLA, {'torso': r(18), 'cuello': r(8), 'cabeza': r(26)}), der=(0, -14, -30), izq=(0, -24, -30),
             espada=(0, 1, 0.05))
GRITO = ik(mezcla({'cabeza': r(-30), 'torso': r(-12), 'pelvis': P(0, 4, 0)}, CAPA_VIENTO,
                  pies(izq=(14, -10), der=(-14, 10))),
           izq=(42, -52, -14), der=(-42, -52, -14), espada=(-0.5, 0.3, -0.8))
SOL_ARRIBA = ik(mezcla({'cabeza': r(-24, 10), 'torso': r(-8, -14), 'pelvis': P(0, 3, 2)}, CAPA_VIENTO),
                izq=(38, -124, 0), der=(-26, -44, -16), espada=(-0.2, 0.55, -0.81))
SOL_LANZA = ik(mezcla({'cabeza': r(6, -10), 'torso': r(14, 22), 'pelvis': P(0, 6, -4)}, CAPA_VIENTO),
               izq=(8, -60, -50), der=(-30, -44, -10), espada=(-0.3, 0.5, -0.8))
# Clavar la espada a un lado (Ofrenda y Dios de la Guerra): el puno a su derecha y la hoja al suelo.
CLAVA_LADO = ik(mezcla({'torso': r(16, 12), 'cabeza': r(14), 'pelvis': P(-2, 7, 0)},
                       pies(der=(-16, 0, 0, 14))), der=(-34, -48, -14), izq=(24, -44, -6), espada=(-0.12, 1, -0.08))
OFRENDA_AGARRA = ik(mezcla({'torso': r(26), 'cabeza': r(18), 'pelvis': P(0, 9, -4)},
                           pies(izq=(12, -26))), izq=(10.5, -46, -44), der=(-10.5, -46, -44))
OFRENDA_ALZA = ik(mezcla({'cabeza': r(-34), 'torso': r(-6), 'pelvis': P(0, 1, 0)}, CAPA_VIENTO),
                  izq=(10.5, -112, -30), der=(-10.5, -112, -30))
DIOS = ik(mezcla({'cabeza': r(-16), 'torso': r(-8), 'pelvis': P(0, 3, 0)}, CAPA_VIENTO,
                 pies(izq=(15, -12), der=(-15, 10))),
          izq=(44, -118, -10), der=(-44, -118, -10))
DIOS_LANZA = ik(mezcla({'cabeza': r(4), 'torso': r(16), 'pelvis': P(0, 7, -3)}, CAPA_VIENTO),
                izq=(30, -70, -44), der=(-30, -70, -44))


# --- Los tajos del Barrido: carga y golpe de cada uno ---
def tajo(puno, hoja, torso_y, extra=None):
    base = mezcla({'torso': r(4, torso_y), 'cabeza': r(0, -torso_y * 0.6), 'pelvis': {'pos': (0, 5, 0), 'rot': (0, torso_y * 0.45, 0)}},
                  CAPA_VIENTO, extra or {})
    izq = (32, -54, 12) if torso_y < 0 else (28, -56, -22)
    return ik(base, izq=izq, der=puno, espada=hoja)


T1_CARGA = tajo((-34, -72, 10), (-0.75, -0.3, 0.6), 30)
T1_GOLPE = tajo((18, -62, -42), (0.88, 0.05, -0.47), -30, {'pelvis': P(0, 8, -6)})
T2_CARGA = tajo((26, -74, 0), (0.8, -0.25, 0.55), -26)
T2_GOLPE = tajo((-26, -60, -40), (-0.88, 0.05, -0.47), 28, {'pelvis': P(0, 8, -6)})
T3_CARGA = tajo((-12, -126, 2), (-0.3, -0.9, 0.3), 8, {'cabeza': r(-14), 'torso': r(-10, 8), 'pelvis': P(0, 0, 2)})
T3_GOLPE = tajo((10, -38, -42), (0.35, 0.65, -0.68), -14, {'torso': r(26, -14), 'pelvis': P(0, 14, -6)})
T4_CARGA = tajo((-36, -68, 16), (-0.72, -0.1, 0.68), 36)
T4_GOLPE = tajo((26, -64, -38), (0.92, 0.02, -0.39), -36, {'pelvis': P(0, 9, -8)})


# ----------------------------------------------------------------------
#  Curvas
# ----------------------------------------------------------------------
def _back(a, k=0.9):
    c1 = 1.70158 * k
    c3 = c1 + 1
    return 1 + c3 * (a - 1) ** 3 + c1 * (a - 1) ** 2


CURVAS = {
    'l': lambda a: a,
    'e': lambda a: a * a * a * (a * (a * 6 - 15) + 10),
    'i': lambda a: a ** 2.3,
    'o': lambda a: 1 - (1 - a) ** 2.3,
    'b': _back,
}


def catmull(a, p0, p1, p2, p3):
    return 0.5 * (2 * p1 + (p2 - p0) * a + (2 * p0 - 5 * p1 + 4 * p2 - p3) * a * a + (3 * p1 - p0 - 3 * p2 + p3) * a ** 3)


def _tramo(ts, s, loop, dur):
    n = len(ts)
    if loop:
        s = s % dur
    idx = n
    for i, t in enumerate(ts):
        if s <= t + 1e-9:
            idx = i
            break
    prev = max(0, idx - 1)
    nxt = min(n - 1, prev + 1)
    al = 0.0 if nxt == prev else min(1.0, max(0.0, (s - ts[prev]) / (ts[nxt] - ts[prev])))
    return prev, nxt, al


def curva(ks, s, loop=False, dur=None):
    """ks: [(t, valor np, tipo)]. El tipo de la clave de llegada manda el tramo."""
    ts = [k[0] for k in ks]
    prev, nxt, al = _tramo(ts, s, loop, dur)
    v0, v1 = ks[prev][1], ks[nxt][1]
    tipo = ks[nxt][2]
    if tipo == 'c':
        n = len(ks)
        if loop:
            a = ks[(prev - 1) % (n - 1)][1] if prev > 0 else ks[n - 2][1]
            b = ks[nxt + 1][1] if nxt + 1 < n else ks[1][1]
        else:
            a = ks[max(0, prev - 1)][1]
            b = ks[min(n - 1, nxt + 1)][1]
        return catmull(al, a, v0, v1, b), al
    k = CURVAS[tipo](al)
    return v0 + (v1 - v0) * k, k


# ----------------------------------------------------------------------
#  Las animaciones
# ----------------------------------------------------------------------
ANIMS = {}
PIERNAS = set(nf.PIERNAS)


def anim(nombre, dur, claves, loop=False, auto_paso=True, sin_fisica=(), sin_retraso=(), asienta=0.22):
    """Guarda las claves (ya en el espacio del juego) y los apoyos de los pies."""
    canales_autor = {}
    apoyos = []
    ult = {l: (np.array(PIE_REPOSO[l][0], float), PIE_REPOSO[l][1], PIE_REPOSO[l][2]) for l in ('izq', 'der')}
    for i, (t, p, tipo) in enumerate(claves):
        pj = a_juego(p)
        ap = {}
        for lado in ('izq', 'der'):
            d = pj.pop('apoyo_' + lado, None)
            if d is not None:
                ap[lado] = (np.array(d['en'], float), d['pie'], d['giro'])
            elif not loop and (i == 0 or i == len(claves) - 1):
                # empieza y acaba en el reposo
                ap[lado] = (np.array(PIE_REPOSO[lado][0], float), PIE_REPOSO[lado][1], PIE_REPOSO[lado][2])
            else:
                ap[lado] = ult[lado]
            ult[lado] = ap[lado]
        for k in list(pj):
            if k in PIERNAS:
                pj.pop(k)
        apoyos.append((t, ap, tipo))
        canales_autor[i] = (t, pj, tipo)
    # canales de autor: todo lo que alguna clave toca
    usados = {}
    for i, (t, pj, tipo) in canales_autor.items():
        for pieza, d in pj.items():
            for tp in d:
                if tp in ('rot', 'pos', 'esc'):
                    usados[(pieza, tp)] = True
    canales = []
    for (pieza, tp) in usados:
        nulo = (1.0, 1.0, 1.0) if tp == 'esc' else (0.0, 0.0, 0.0)
        ks = []
        for i in sorted(canales_autor):
            t, pj, tipo = canales_autor[i]
            v = pj.get(pieza, {}).get(tp, nulo)
            if not isinstance(v, (tuple, list)):
                v = (v, v, v)
            ks.append((t, np.array(v, float), tipo))
        canales.append((pieza, tp, ks))
    ANIMS[nombre] = {'dur': dur, 'loop': loop, 'autor': canales, 'apoyos': apoyos, 'auto_paso': auto_paso,
                     'sin_fisica': set(sin_fisica), 'sin_retraso': set(sin_retraso), 'asienta': asienta}


def muestreada(f, dur, pasos, tipo='c'):
    """Claves de una funcion pose(s) cada dur/pasos (para ciclos y temblores)."""
    return [(dur * i / pasos, f(dur * i / pasos), tipo) for i in range(pasos + 1)]


# --- Reposo: respira; el peso pasa de un pie al otro; la espada pesa ---
T_REPOSO = 3.2


def pose_reposo(s):
    a = 2 * math.pi * s / T_REPOSO
    return mezcla(G, {'torso': r(-1.6 * math.sin(a), 1.2 * math.sin(a * 0.5), 0.6 * math.sin(a * 0.5)),
                      'cabeza': r(1.2 * math.sin(a + 0.6), -3 * math.sin(a * 0.5 + 0.4)),
                      'pelvis': {'pos': (1.2 * math.sin(a * 0.5), 0.6 * (1 - math.cos(a)), 0), 'rot': (0, 0, -0.8 * math.sin(a * 0.5))},
                      'brazo_der': {'rot': tuple(G['brazo_der']['rot'][i] + (1.8 * math.sin(a + 1.0), 0, 0)[i] for i in range(3))},
                      'brazo_izq': {'rot': tuple(G['brazo_izq']['rot'][i] + (2.2 * math.sin(a + 0.4), 0, -1.2 * math.sin(a))[i] for i in range(3))}})


anim('REPOSO', T_REPOSO, muestreada(pose_reposo, T_REPOSO, 16), loop=True)

# --- Andar: zancada larga y viva, con el peso de verdad ---
# Una vuelta = dos pasos. Cada pie apoya el 60 % de la vuelta y en ese tiempo va
# hacia atras al ritmo del cuerpo (en el suelo no se mueve); el resto vuela hacia
# delante en arco. La pelvis baja en cada apoyo y sube al pasar, se mece hacia
# el pie que carga y gira con la pierna que avanza; el torso gira al reves y los
# brazos van contrarios a las piernas.
T_ANDAR = 1.6
ZANCADA_PX = 76.0              # lo que avanza el cuerpo por vuelta (px de modelo): lo que dan de si sus piernas
APOYO = 0.6


def _pie_andar(fase, lado):
    """(x, z, alto, inclinacion) del pie a la fase (0..1) de su propia vuelta (0 = toca el suelo)."""
    s = 1 if lado == 'izq' else -1
    x = 11.5 * s
    largo = ZANCADA_PX * APOYO          # lo que recorre en el suelo mientras apoya
    if fase < APOYO:
        u = fase / APOYO
        z = -largo / 2 + largo * u          # de delante (-z) a atras
        alto = 0.0
        incl = -8.0 * max(0.0, 1 - u / 0.15) + 24.0 * max(0.0, (u - 0.78) / 0.22)   # entra de talon, sale de punta
    else:
        u = (fase - APOYO) / (1 - APOYO)
        k = CURVAS['e'](u)
        z = largo / 2 - largo * k
        alto = 13.0 * math.sin(math.pi * u) ** 0.8
        incl = 24.0 - 32.0 * CURVAS['e'](u)
    return x, z, alto, incl


def pose_andar(s):
    f = s / T_ANDAR
    a = 2 * math.pi * f
    pi_ = _pie_andar(f % 1.0, 'izq')
    pd = _pie_andar((f + 0.5) % 1.0, 'der')
    baja = 1.2 + 1.8 * math.cos(2 * a)            # mas baja con los dos pies en el suelo, arriba al pasar
    lado = 2.4 * math.sin(a + 0.5)                # hacia el pie que carga
    giro = 7.0 * math.cos(a)                      # la pelvis gira con la pierna que avanza
    bi = G['brazo_izq']['rot']
    bd = G['brazo_der']['rot']
    return mezcla(G, {
        'pelvis': {'pos': (lado, baja, 0), 'rot': (2.0, giro, -2.2 * math.sin(a))},
        'torso': r(5.0 + 1.5 * math.cos(2 * a), -giro * 1.4, 1.6 * math.sin(a)),
        'cabeza': r(-3.0 - 1.2 * math.cos(2 * a), giro * 0.5, -1.0 * math.sin(a)),
        'brazo_izq': {'rot': (bi[0] - 18 * math.cos(a), bi[1], bi[2] + 2 * math.sin(a))},
        'antebrazo_izq': {'rot': tuple(G['antebrazo_izq']['rot'][i] + (-8 * max(0.0, -math.cos(a)), 0, 0)[i] for i in range(3))},
        'brazo_der': {'rot': (bd[0] + 7 * math.cos(a), bd[1], bd[2])},
        'capa_1': r(10), 'capa_2': r(4), 'capa_3': r(4),
    }, pies(izq=(pi_[0], pi_[1], pi_[3], -6, pi_[2]), der=(pd[0], pd[1], pd[3], 6, pd[2])))


anim('ANDAR', T_ANDAR, muestreada(pose_andar, T_ANDAR, 32), loop=True, auto_paso=False)

# --- Dormido: de rodilla, la espada clavada delante, la cabeza gacha; respira ---
anim('DORMIDO', 6.0, muestreada(lambda s: sumar(DORMIDO, {'torso': r(2.5 * math.sin(2 * math.pi * s / 6.0)),
                                                       'cabeza': r(2 * math.sin(2 * math.pi * s / 6.0 - 0.6))}), 6.0, 12),
     loop=True)

# --- Despertar: alza la cabeza, se pone en pie de un tiron, arranca la espada y ruge ---
_mira = sumar(DORMIDO, {'cabeza': r(-36), 'cuello': r(-8), 'torso': r(-6)})
_de_pie = ik(mezcla({'pelvis': P(0, 10, -2), 'torso': r(18), 'cabeza': r(-8)},
                    pies(izq=(11, -22), der=(-11, 10))), der=(-6, -30, -30), izq=(24, -40, -10), espada=(0, 1, 0.1))
_arranca = ik(mezcla({'cabeza': r(-22), 'torso': r(-8), 'pelvis': P(0, 2, 0)}, CAPA_VIENTO,
                     pies(izq=(12, -12), der=(-12, 9))), der=(-14, -126, -10), izq=(40, -56, -12), espada=(-0.1, -1, 0.05))
T_DESPERTAR_RUGE = 1.45
anim('DESPERTAR', 2.4, [(0, DORMIDO, 'e'), (0.4, _mira, 'e'), (0.85, _de_pie, 'o'), (1.15, _arranca, 'i'),
                        (T_DESPERTAR_RUGE, GRITO, 'o'), (1.75, sumar(GRITO, {'cabeza': r(-4, 6)}), 'e'),
                        (1.95, sumar(GRITO, {'cabeza': r(-2, -5)}), 'e'), (2.4, G, 'e')])

# --- Barrido Solar: cuatro tajos encadenados, cada uno con su paso ---
# carga (anticipacion corta) -> golpe (llega a toda velocidad) -> el impulso se
# apaga (la hoja se pasa un poco) -> la carga del siguiente.
T_TAJOS = (0.42, 0.98, 1.52, 2.12)


def _sigue(golpe, mas):
    return sumar(golpe, mas)


anim('BARRIDO', 2.6, [
    (0, G, 'e'),
    (0.24, mezcla(T1_CARGA, pies(izq=(11, -5), der=(-12, 9))), 'e'),
    (T_TAJOS[0], mezcla(T1_GOLPE, pies(izq=(13, -24))), 'i'),
    (0.54, _sigue(T1_GOLPE, {'torso': r(2, -8), 'pelvis': P(0, 1, -1)}), 'o'),
    (0.8, mezcla(T2_CARGA, pies(der=(-12, 4))), 'e'),
    (T_TAJOS[1], mezcla(T2_GOLPE, pies(der=(-13, -16))), 'i'),
    (1.1, _sigue(T2_GOLPE, {'torso': r(2, 8)}), 'o'),
    (1.32, mezcla(T3_CARGA, pies(izq=(15, -14), der=(-15, 8))), 'e'),
    (T_TAJOS[2], mezcla(T3_GOLPE, pies(izq=(16, -26), der=(-16, 10))), 'i'),
    (1.66, _sigue(T3_GOLPE, {'torso': r(4), 'pelvis': P(0, 2, 0)}), 'b'),
    (1.92, mezcla(T4_CARGA, pies(izq=(14, -18), der=(-12, 6))), 'e'),
    (T_TAJOS[3], mezcla(T4_GOLPE, pies(der=(-12, -12))), 'i'),
    (2.26, _sigue(T4_GOLPE, {'torso': r(2, -10), 'cabeza': r(0, 6)}), 'o'),
    (2.6, G, 'e'),
])

# --- Castigo Divino: alza la espada al sol de un tiron; los rayos caen; desde la II, la clava ---
T_CASTIGO_ALZA = 0.3
T_CASTIGO_MARCA = 0.5
T_CASTIGO_RAYO = 1.6          # 1,1 s de aviso entre el sello y el rayo (como antes)
_alza = mezcla(ALZA, pies(izq=(12, -8), der=(-12, 8)))
_alza_tiembla = sumar(_alza, {'torso': r(-3, 2), 'cabeza': r(-5, -3)})
_llama = sumar(_alza, {'torso': r(6), 'pelvis': P(0, 4, 0), 'cabeza': r(6)})       # tira del rayo hacia abajo
_previa = ik(mezcla({'torso': r(10, -6), 'pelvis': P(0, 6, 0), 'cabeza': r(6)}, pies(izq=(12, -8), der=(-12, 8))),
             der=(-20, -52, -24), izq=(20, -50, -22), espada=(0, 0.2, -1))
anim('CASTIGO', 2.2, [(0, G, 'e'), (0.14, _previa, 'e'), (T_CASTIGO_ALZA, _alza, 'o'), (T_CASTIGO_MARCA, _alza_tiembla, 'b'),
                      (1.05, _alza, 'e'), (1.4, _alza_tiembla, 'e'), (T_CASTIGO_RAYO, _llama, 'i'),
                      (1.72, _alza, 'o'), (2.2, G, 'e')])
T_ONDA_CLAVA = 2.1
_agacha = sumar(_alza, {'pelvis': P(0, 12, 2), 'torso': r(10), 'cabeza': r(8)})
_salta = mezcla(sumar(ALZA, {'pelvis': P(0, -12, 0), 'torso': r(-8)}),
                pies(izq=(12, -10, -20, -6, 10), der=(-12, 6, -20, 6, 10)))
anim('CASTIGO_ONDA', 3.0, [(0, G, 'e'), (0.14, _previa, 'e'), (T_CASTIGO_ALZA, _alza, 'o'), (T_CASTIGO_MARCA, _alza_tiembla, 'b'),
                           (1.05, _alza, 'e'), (1.4, _alza_tiembla, 'e'), (T_CASTIGO_RAYO, _llama, 'i'),
                           (1.78, _agacha, 'e'), (1.95, _salta, 'o'), (T_ONDA_CLAVA, ARRODILLADO_CLAVA, 'i'),
                           (2.24, sumar(ARRODILLADO_CLAVA, {'pelvis': P(0, 2, 0), 'torso': r(4)}), 'o'),
                           (2.5, sumar(ARRODILLADO_CLAVA, {'cabeza': r(-8)}), 'e'), (3.0, G, 'e')],
     sin_fisica=())

# --- Sol Abrasador: el sol se le forma en la mano en alto y lo lanza; tres veces ---
T_SOL_LANZA = (0.6, 1.2, 1.8)
_sol_alto = mezcla(SOL_ARRIBA, pies(izq=(12, -6), der=(-13, 12)))
_sol_tira = mezcla(SOL_LANZA, pies(izq=(13, -20), der=(-13, 12)))
_sol_sigue = sumar(_sol_tira, {'torso': r(4, 6), 'cabeza': r(2)})
anim('SOL', 2.5, [(0, G, 'e'), (0.36, _sol_alto, 'e'), (T_SOL_LANZA[0], _sol_tira, 'i'), (0.72, _sol_sigue, 'o'),
                  (0.98, _sol_alto, 'e'), (T_SOL_LANZA[1], _sol_tira, 'i'), (1.32, _sol_sigue, 'o'),
                  (1.58, _sol_alto, 'e'), (T_SOL_LANZA[2], _sol_tira, 'i'), (1.94, _sol_sigue, 'o'), (2.5, G, 'e')])

# --- Trompetas: se agacha y alza la espada al cielo de golpe; las estatuas salen del suelo ---
T_TROMPETAS_ALZA = 0.7
_invoca = ik(mezcla({'cabeza': r(-26), 'torso': r(-10), 'pelvis': P(0, 0, 0)}, CAPA_VIENTO, pies(izq=(13, -8), der=(-13, 8))),
             der=(-16, -128, -6), izq=(42, -64, -18), espada=(-0.15, -1, 0.0))
_carga_invoca = ik(mezcla({'cabeza': r(12), 'torso': r(16, 10), 'pelvis': P(0, 9, 0)}, pies(izq=(13, -8), der=(-13, 8))),
                   der=(-26, -40, -26), izq=(30, -46, -20), espada=(-0.2, 0.6, -0.78))
anim('TROMPETAS', 1.8, [(0, G, 'e'), (0.4, _carga_invoca, 'e'), (T_TROMPETAS_ALZA, _invoca, 'i'),
                        (0.86, sumar(_invoca, {'cabeza': r(-6), 'torso': r(-3)}), 'o'), (1.3, _invoca, 'e'), (1.8, G, 'e')])

# --- Fuentes solares: salta, clava la espada de rodilla y carga el sol (luego, en bucle) ---
T_FUENTES_CLAVA = 0.55
anim('FUENTES', 1.2, [(0, G, 'e'), (0.18, _agacha, 'e'), (0.36, _salta, 'o'), (T_FUENTES_CLAVA, ARRODILLADO_CLAVA, 'i'),
                      (0.7, sumar(ARRODILLADO_CLAVA, {'pelvis': P(0, 2, 0)}), 'o'), (1.2, ARRODILLADO_SOL, 'e')])


def pose_fuentes_carga(s):
    a = 2 * math.pi * s / 2.0
    return sumar(ARRODILLADO_SOL, {'torso': r(3 * math.sin(a), 2 * math.sin(a * 0.5)), 'cabeza': r(-4 * math.sin(a + 0.5), 3 * math.sin(a * 0.5)),
                                   'pelvis': P(0, 1.2 * math.sin(a), 0)})


anim('FUENTES_CARGA', 2.0, muestreada(pose_fuentes_carga, 2.0, 12), loop=True)

# --- Ofrenda al Sol: clava la espada, se lanza a por el elegido, lo coge y lo alza ---
T_OFRENDA_SUELTA = 0.4       # suelta la espada: desde aqui se ve la clavada
T_OFRENDA_AGARRA = 0.95      # el jugador ya esta en sus manos
T_OFRENDA_ALZADO = 1.7
_ofrenda_alza = mezcla(OFRENDA_ALZA, pies(izq=(12, -10), der=(-12, 8)))
anim('OFRENDA', 2.0, [(0, G, 'e'), (0.3, CLAVA_LADO, 'o'), (T_OFRENDA_SUELTA, CLAVA_LADO, 'e'),
                      (0.8, OFRENDA_AGARRA, 'i'), (T_OFRENDA_AGARRA, sumar(OFRENDA_AGARRA, {'pelvis': P(0, 2, 0)}), 'o'),
                      (1.25, sumar(OFRENDA_AGARRA, {'torso': r(-12), 'pelvis': P(0, -2, 0)}), 'e'),
                      (T_OFRENDA_ALZADO, _ofrenda_alza, 'o'), (2.0, _ofrenda_alza, 'e')])
anim('OFRENDA_SOSTIENE', 2.0, muestreada(lambda s: sumar(_ofrenda_alza, {
    'torso': r(-3 * math.sin(2 * math.pi * s / 2.0), 2 * math.sin(math.pi * s / 2.0)),
    'cabeza': r(-3 * math.sin(2 * math.pi * s / 2.0 + 0.6))}), 2.0, 12), loop=True)

# --- Dios de la Guerra: clava la espada, abre los brazos en llamas y lanza soles a tres zonas ---
T_DIOS_SUELTA = 0.4
T_DIOS_MARCA = 0.75
T_DIOS_LANZA = (1.25, 2.05, 2.85)
T_DIOS_RECOGE = 3.5
_dios_tira = mezcla(DIOS_LANZA, pies(izq=(16, -22), der=(-15, 12)))
_dios_sigue = sumar(_dios_tira, {'torso': r(4), 'cabeza': r(4)})
claves_dios = [(0, G, 'e'), (0.3, CLAVA_LADO, 'o'), (T_DIOS_SUELTA, CLAVA_LADO, 'e'), (T_DIOS_MARCA, DIOS, 'o')]
for t in T_DIOS_LANZA:
    claves_dios += [(t - 0.26, sumar(DIOS, {'torso': r(-4), 'pelvis': P(0, -1, 2)}), 'e'), (t, _dios_tira, 'i'), (t + 0.14, _dios_sigue, 'o')]
claves_dios += [(T_DIOS_RECOGE, CLAVA_LADO, 'e'), (4.0, G, 'e')]
anim('DIOS', 4.0, claves_dios)

# --- Grito de guerra: se encoge y estalla rugiendo al cielo ---
T_GRITO = 0.55
_encoge = ik(mezcla({'torso': r(22), 'cabeza': r(18), 'pelvis': P(0, 8, 0)}, pies(izq=(13, -8), der=(-13, 8))),
             izq=(18, -54, -26), der=(-18, -54, -26), espada=(-0.4, 0.5, -0.75))
anim('GRITO', 1.8, [(0, G, 'e'), (0.38, _encoge, 'e'), (T_GRITO, GRITO, 'i'), (0.7, sumar(GRITO, {'torso': r(-4), 'cabeza': r(-6)}), 'o'),
                    (1.0, sumar(GRITO, {'cabeza': r(-2, 6)}), 'e'), (1.25, sumar(GRITO, {'cabeza': r(-2, -6)}), 'e'), (1.8, G, 'e')])

# --- Aturdido: le fallan las piernas, cae de rodilla sobre la espada (luego, en bucle) ---
_aturdido = ik(mezcla(RODILLA, {'torso': r(28, 8), 'cabeza': r(32, 12)}), der=(-6, -10, -30), izq=(22, -20, -24),
               espada=(0, 1, 0.05))
_tumbo = ik(mezcla({'torso': r(-14, -6), 'cabeza': r(-18), 'pelvis': P(0, 4, 4)}, pies(der=(-12, 18))),
            izq=(38, -62, 4), der=(-30, -52, 6), espada=(-0.3, 0.6, -0.6))
anim('ATURDIDO', 0.9, [(0, G, 'e'), (0.25, _tumbo, 'o'), (0.75, _aturdido, 'i'), (0.9, sumar(_aturdido, {'pelvis': P(0, -1, 0)}), 'b')])
anim('ATURDIDO_BUCLE', 2.4, muestreada(lambda s: sumar(_aturdido, {
    'torso': r(2.5 * math.sin(2 * math.pi * s / 2.4), -4 * math.sin(math.pi * s / 2.4 * 2)),
    'cabeza': r(4 * math.sin(2 * math.pi * s / 2.4 - 0.7), -8 * math.sin(math.pi * s / 2.4 * 2 - 0.5))}), 2.4, 12), loop=True)

# --- Tambaleo (cambio de fase): la armadura se raja, el golpe le echa atras,
#     da un paso para no caer, se apoya en la rodilla y se alza rugiendo ---
_recula = ik(mezcla({'torso': r(-16, -8), 'cabeza': r(-22, 6), 'pelvis': P(0, 3, 5)}, CAPA_VIENTO),
             izq=(40, -72, 8), der=(-32, -54, 10), espada=(-0.4, 0.6, 0.6))
_paso_atras = ik(mezcla({'torso': r(-6, -4), 'cabeza': r(-10), 'pelvis': P(0, 7, 8)}, pies(der=(-13, 24))),
                 izq=(34, -60, 2), der=(-28, -50, 0), espada=(-0.3, 0.7, 0.2))
_apoya = ik(mezcla({'torso': r(28, 6), 'cabeza': r(22), 'pelvis': P(0, 13, 4)}, pies(izq=(13, -16), der=(-13, 22))),
            izq=(14, -38, -30), der=(-24, -34, -26), espada=(-0.05, 1, -0.2))
_alza_ruge = mezcla(GRITO, pies(izq=(14, -10), der=(-14, 14)))
T_TAMBALEO_RUGE = 1.2
anim('TAMBALEO', 2.2, [(0, G, 'e'), (0.12, _recula, 'o'), (0.42, _paso_atras, 'e'), (0.82, _apoya, 'e'),
                       (1.0, sumar(_apoya, {'torso': r(4), 'pelvis': P(0, 1, 0)}), 'e'), (T_TAMBALEO_RUGE, _alza_ruge, 'i'),
                       (1.4, sumar(_alza_ruge, {'cabeza': r(-6), 'torso': r(-4)}), 'o'),
                       (1.7, sumar(_alza_ruge, {'cabeza': r(-2, 6)}), 'e'), (2.2, G, 'e')])

# --- Liberacion: cae de rodilla sobre la espada, mira a su sol y le ofrece la mano ---
_li_mira = sumar(ARRODILLADO_SOL, {'cabeza': r(-6)})
_li_mano = ik(mezcla(RODILLA, {'torso': r(2), 'cabeza': r(-38)}), der=(0, -22, -28), izq=(30, -100, -20),
              espada=(0, 1, 0.05))
anim('LIBERACION', 10.0, [(0, G, 'e'), (0.5, _recula, 'o'), (1.6, ARRODILLADO_CLAVA, 'i'), (1.8, sumar(ARRODILLADO_CLAVA, {'pelvis': P(0, 2, 0)}), 'b'),
                          (3.5, _li_mira, 'e'), (6.0, _li_mano, 'e'), (10.0, _li_mano, 'e')])
T_LIBERACION_ORO = 3.5


# ----------------------------------------------------------------------
#  La malla: la guardia y la postura de pie horneadas, la espada suelta clavada
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
    punta = (M @ np.array([0, fm.PUNTA_ESPADA, 0, 1.0]))[:3]
    pivote = pivote + np.array([0, 24 + 10 - punta[1], 0])
    nj.ESPADA_SUELTA['pose'] = (tuple(pivote), euler_zyx(R))
    nj.construir()
    # La guardia, horneada: la postura de reposo de los brazos y del agarre.
    for k in HORNEADAS:
        g = GUARDIA[k]['rot']
        p = nj.PARTES[k]
        p.rot = tuple(p.rot[i] + g[i] for i in range(3))
    # La postura de pie: la pelvis mas baja y las piernas por cinematica inversa.
    pel = nj.PARTES['pelvis']
    pel.pivote = (pel.pivote[0], pel.pivote[1] + PELVIS_REPOSO, pel.pivote[2])
    Mp = nj.matrices({})['pelvis']
    for lado in ('izq', 'der'):
        en, incl, giro = PIE_REPOSO[lado]
        (mx, my, mz), rod, pie = nf.ik_pierna(Mp, lado, en, incl, giro)
        nj.PARTES['pierna_' + lado].rot = (mx, my, mz)
        nj.PARTES['espinilla_' + lado].rot = (rod, 0.0, 0.0)
        nj.PARTES['pie_' + lado].rot = (pie, 0.0, 0.0)


preparar_malla()


def ajustar_espada_suelta():
    """La espada clavada, donde la deja la mano en la pose HORNEADA (con la fisica)
    al soltarla en la Ofrenda: asi el cambio de la de la mano a la clavada no
    salta. Devuelve lo que hubo que hundirla (px) para que la punta entre 10 px."""
    pose = pose_en('OFRENDA', T_OFRENDA_SUELTA)
    M = nj.matrices(pose)['espada']
    R = M[:3, :3] / np.linalg.norm(M[:3, :3], axis=0)
    punta = (M @ np.array([0, fm.PUNTA_ESPADA, 0, 1.0]))[:3]
    baja = 24 + 10 - punta[1]
    piv = M[:3, 3] + np.array([0, baja, 0])
    nj.PARTES['espada_suelta'].pivote = tuple(float(v) for v in piv)
    nj.PARTES['espada_suelta'].rot = euler_zyx(R)
    return baja


# ----------------------------------------------------------------------
#  El horneado: poses de autor + fisica -> canales (en el espacio del juego)
# ----------------------------------------------------------------------
TOL = {'rot': 0.3, 'pos': 0.06, 'esc': 0.004}


def pose_autor(nombre):
    a = ANIMS[nombre]

    def f(s):
        pose = {}
        for pieza, tp, ks in a['autor']:
            v, _ = curva(ks, s, a['loop'], a['dur'])
            pose.setdefault(pieza, {})[tp] = tuple(float(x) for x in v)
        return pose
    return f


def apoyos_de(nombre):
    a = ANIMS[nombre]
    ks = a['apoyos']
    ts = [k[0] for k in ks]

    def f(s):
        prev, nxt, al = _tramo(ts, s, a['loop'], a['dur'])
        out = {}
        for lado in ('izq', 'der'):
            p0, i0, g0 = ks[prev][1][lado]
            p1, i1, g1 = ks[nxt][1][lado]
            tipo = ks[nxt][2]
            if tipo == 'c':
                n = len(ks)
                pa = ks[max(0, prev - 1)][1][lado] if not a['loop'] else ks[(prev - 1) % (n - 1)][1][lado]
                pb = ks[min(n - 1, nxt + 1)][1][lado] if not a['loop'] else (ks[nxt + 1][1][lado] if nxt + 1 < n else ks[1][1][lado])
                en = catmull(al, pa[0], p0, p1, pb[0])
                incl = float(catmull(al, pa[1], i0, i1, pb[1]))
                giro = float(catmull(al, pa[2], g0, g1, pb[2]))
            else:
                k = CURVAS['e' if tipo in ('i', 'b') else tipo](al)     # los pies no se pasan de largo
                en = p0 + (p1 - p0) * k
                incl = i0 + (i1 - i0) * k
                giro = g0 + (g1 - g0) * k
                d = float(np.hypot(p1[0] - p0[0], p1[2] - p0[2]))
                if a['auto_paso'] and d > 3.0:
                    # el paso: el pie se levanta en arco (mas cuanto mas lejos va) y la punta baja
                    en = en.copy()
                    en[1] -= min(16.0, 0.3 * d + 3.0) * math.sin(math.pi * k)
                    incl += 16.0 * math.sin(math.pi * k)
            # el pivote del pie (en la suela, a 16 px de la punta y 7 del talon) sube
            # lo justo para que la punta (de puntillas) o el talon no se hundan
            en = np.array(en, float)
            en[1] -= 16.0 * math.sin(math.radians(max(0.0, incl))) + 7.0 * math.sin(math.radians(max(0.0, -incl)))
            out[lado] = (tuple(float(x) for x in en), float(incl), float(giro))
        return out
    return f


def _quitar_reposo_piernas(pose):
    """La IK da angulos absolutos; la malla ya trae la postura de pie: offsets."""
    for k in nf.PIERNAS:
        if k in pose:
            r0 = nj.PARTES[k].rot
            v = pose[k]['rot']
            pose[k]['rot'] = (v[0] - r0[0], v[1] - r0[1], v[2] - r0[2])
    return pose


_EQUILIBRIO = {}


def equilibrio():
    """Lo que la gravedad separa la ropa de su reposo, estando quieto: se resta
    para que el reposo de la fisica sea el de la malla (y no salte al fundir)."""
    if not _EQUILIBRIO:
        def autor(s):
            return {}

        def apo(s):
            return {l: PIE_REPOSO[l] for l in ('izq', 'der')}
        reg = nf.hornear(3.0, False, autor, apo, paso=0.5)
        for (pieza, tp), serie in reg.items():
            if pieza in nf.SIMULADAS and tp == 'rot':
                _EQUILIBRIO[pieza] = np.array(serie[-1][1])
    return _EQUILIBRIO


def hornear(nombre):
    a = ANIMS[nombre]
    autor = pose_autor(nombre)

    def autor_juego(s):
        return autor(s)
    apo = apoyos_de(nombre)
    reg = nf.hornear(a['dur'], a['loop'], autor_juego, apo, a['sin_fisica'], a['sin_retraso'])
    eq = equilibrio()
    canales = []
    for (pieza, tp), serie in reg.items():
        serie = [(t, np.array(v, float)) for t, v in serie]
        if pieza in eq and tp == 'rot':
            serie = [(t, v - eq[pieza]) for t, v in serie]
        if not a['loop'] and pieza in nf.SIMULADAS and a['asienta'] > 0:
            # al acabar, la ropa se asienta en su reposo (el juego funde con el reposo)
            ultimo_autor = np.array(autor(a['dur']).get(pieza, {}).get('rot', (0, 0, 0)), float)
            dur, tA = a['dur'], a['asienta']
            serie = [(t, v if t < dur - tA else ultimo_autor + (v - ultimo_autor) * max(0.0, (dur - t) / tA)) for t, v in serie]
        muestras = [(t, tuple(round(float(c), 3) for c in v)) for t, v in serie]
        nulo = 1.0 if tp == 'esc' else 0.0
        mayor = max(max(abs(c - nulo) for c in v) for _, v in muestras)
        if mayor < TOL[tp]:
            continue
        ks = nf.simplificar(muestras, TOL[tp])
        canales.append((pieza, tp, ks))
    a['canales'] = canales


def pose_en(nombre, s):
    """La pose final del juego (con fisica) a s segundos: lineal entre las claves horneadas."""
    a = ANIMS[nombre]
    if a['loop']:
        s = s % a['dur']
    pose = {}
    for pieza, tp, ks in a['canales']:
        ts = [k[0] for k in ks]
        prev, nxt, al = _tramo(ts, s, False, a['dur'])
        v0 = np.array(ks[prev][1])
        v1 = np.array(ks[nxt][1])
        v = v0 + (v1 - v0) * al
        pose.setdefault(pieza, {})[tp] = tuple(float(x) for x in v)
    return pose


# ----------------------------------------------------------------------
#  A Java
# ----------------------------------------------------------------------
def fj(x):
    s = ('%.3f' % x).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s + 'F'


def fs(x, dec=2):
    s = ('%.*f' % (dec, x)).rstrip('0').rstrip('.')
    if s in ('-0', ''):
        s = '0'
    return s


def texto_canal(tp, ks):
    out = []
    for t, v in ks:
        x, y, z = v
        if tp == 'esc':
            x, y, z = x - 1, y - 1, z - 1
        out += [fs(t, 3), fs(x, 3 if tp == 'esc' else 2), fs(y, 3 if tp == 'esc' else 2), fs(z, 3 if tp == 'esc' else 2)]
    return ' '.join(out)


def java_anims():
    L = ['package com.atalaya.client;', '',
         'import net.minecraft.client.animation.AnimationChannel;',
         'import net.minecraft.client.animation.AnimationDefinition;',
         'import net.minecraft.client.animation.Keyframe;',
         'import org.joml.Vector3f;', '',
         '/**',
         ' * Las animaciones de Novilis. GENERADO por materiales/generadores/novilis_juego_anim.py',
         ' * (poses) y novilis_fisica.py (pies plantados, inercia y retraso horneados): no se',
         ' * editan a mano. El servidor saca de las mismas poses por donde pasan las manos y',
         ' * la espada (NovilisGeometria).',
         ' *',
         ' * Cada canal va como texto ("t x y z t x y z ..."): son miles de claves y, escritas',
         ' * como llamadas, la clase pasaria del limite de Java (64 KB por metodo y 65 535',
         ' * constantes). Las rotaciones en grados, las posiciones en px (Y abajo, lo que se',
         ' * suma a la pieza) y las escalas como lo que se suma a 1. Entre claves, lineal: el',
         ' * horneado ya las pone donde la curva lo pide.',
         ' */',
         'public final class NovilisAnimaciones {', '']
    for nombre in ANIMS:
        L.append(f'    public static final AnimationDefinition {nombre} = {nombre.lower()}();')
    L += ['', '    private NovilisAnimaciones() {', '    }', '',
          '    private static AnimationChannel canal(AnimationChannel.Target objetivo, float k, String datos) {',
          '        String[] v = datos.split(" ");',
          '        Keyframe[] claves = new Keyframe[v.length / 4];',
          '        for (int i = 0; i < claves.length; i++) {',
          '            claves[i] = new Keyframe(Float.parseFloat(v[4 * i]), new Vector3f(Float.parseFloat(v[4 * i + 1]) * k,',
          '                    Float.parseFloat(v[4 * i + 2]) * k, Float.parseFloat(v[4 * i + 3]) * k),',
          '                    AnimationChannel.Interpolations.LINEAR);',
          '        }',
          '        return new AnimationChannel(objetivo, claves);',
          '    }', '',
          '    private static AnimationChannel giro(String datos) {',
          '        return canal(AnimationChannel.Targets.ROTATION, (float) (Math.PI / 180.0), datos);',
          '    }', '',
          '    private static AnimationChannel mover(String datos) {',
          '        return canal(AnimationChannel.Targets.POSITION, 1.0F, datos);',
          '    }', '',
          '    private static AnimationChannel escala(String datos) {',
          '        return canal(AnimationChannel.Targets.SCALE, 1.0F, datos);',
          '    }', '']
    for nombre, a in ANIMS.items():
        L.append(f'    private static AnimationDefinition {nombre.lower()}() {{')
        L.append(f'        return AnimationDefinition.Builder.withLength({fj(a["dur"])})' + ('.looping()' if a['loop'] else ''))
        for pieza, tp, ks in a['canales']:
            fn = {'rot': 'giro', 'pos': 'mover', 'esc': 'escala'}[tp]
            L.append(f'                .addAnimation("{pieza}", {fn}("{texto_canal(tp, ks)}"))')
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


PUNTA = (0, fm.PUNTA_ESPADA, 0)
BASE_HOJA = (0, 26, 0)


def tick(s):
    return int(round(s * 20))


def java_geometria():
    puntos = {
        'PECHO': p_bloques(None, 0, 'torso', (0, -34, -16)),
        'CABEZA': p_bloques(None, 0, 'cabeza', (0, -10, 0)),
        'HALO': p_bloques(None, 0, 'halo'),
        'PUNTA_ALZA': p_bloques('CASTIGO', T_CASTIGO_MARCA, 'espada', PUNTA),
        'PUNTA_CLAVA': p_bloques('CASTIGO_ONDA', T_ONDA_CLAVA, 'espada', PUNTA),
        'PUNTA_FUENTES': p_bloques('FUENTES', ANIMS['FUENTES']['dur'], 'espada', PUNTA),
        'PECHO_FUENTES': p_bloques('FUENTES_CARGA', 0.0, 'torso', (0, -34, -16)),
        'MANO_SOL': p_bloques('SOL', T_SOL_LANZA[0] - 0.24, 'mano_izq', (0, 6, 0)),
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
         ' * animaciones (ya con la fisica): si una animacion cambia, estos puntos cambian.',
         ' *',
         ' * Los puntos van en bloques y en el espacio del cuerpo: x hacia SU izquierda,',
         ' * y hacia arriba desde los pies, z hacia delante. NovilisEntity los pasa al',
         ' * mundo con el giro del cuerpo.',
         ' */',
         'public final class NovilisGeometria {', '',
         '    private NovilisGeometria() {', '    }', '',
         f'    /** Lo que alcanza la hoja en el Barrido, desde sus pies (bloques). */',
         f'    public static final double ALCANCE_HOJA = {alcance:.2f};',
         f'    /** Lo que avanza el cuerpo por vuelta de la animacion de andar (bloques): con los pies en el suelo, sin patinar. */',
         f'    public static final float ZANCADA = {ZANCADA_PX * nj.ESCALA / 16:.3f}F;',
         f'    /** Lo que dura una vuelta de la animacion de andar (segundos de animacion). */',
         f'    public static final float PERIODO_ANDAR = {T_ANDAR:.3f}F;', '']
    for k, (x, y, z) in puntos.items():
        L.append(f'    public static final Vec3 {k} = new Vec3({x:.3f}, {y:.3f}, {z:.3f});')
    L.append('')
    for k, v in tiempos.items():
        L.append(f'    public static final int {k} = {v};')
    L.append('')
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
#  La estela de la hoja: por donde pasan la base y la punta, en cada animacion
#  con espada en la mano, cada 1/30 s (bloques, espacio del cuerpo)
# ----------------------------------------------------------------------
ESTELAS = ['BARRIDO', 'CASTIGO', 'CASTIGO_ONDA', 'DESPERTAR', 'TAMBALEO', 'GRITO', 'TROMPETAS', 'FUENTES', 'SOL']
HZ_ESTELA = 30


def java_estelas():
    L = ['package com.atalaya.client;', '',
         '/**',
         ' * Por donde pasa la hoja de Novilis en cada animacion: la base y la punta, cada',
         f' * 1/{HZ_ESTELA} s, en bloques y en el espacio del cuerpo (x a su izquierda, y arriba',
         ' * desde los pies, z delante). GENERADO por novilis_juego_anim.py desde las mismas',
         ' * poses horneadas: el cliente dibuja con esto la estela de los tajos.',
         ' */',
         'public final class NovilisEstelas {', '',
         f'    public static final float HZ = {HZ_ESTELA}.0F;', '']
    nombres = []
    for nombre in ESTELAS:
        a = ANIMS[nombre]
        n = int(round(a['dur'] * HZ_ESTELA))
        vals = []
        for i in range(n + 1):
            s = i / HZ_ESTELA
            b = p_bloques(nombre, s, 'espada', BASE_HOJA)
            p = p_bloques(nombre, s, 'espada', PUNTA)
            vals += [*b, *p]
        L.append(f'    private static final String {nombre}_T = "' + ' '.join(fs(v, 2) for v in vals) + '";')
        nombres.append(nombre)
    L += ['']
    for nombre in nombres:
        L.append(f'    public static final float[] {nombre} = leer({nombre}_T);')
    L += ['',
          '    private NovilisEstelas() {', '    }', '',
          '    private static float[] leer(String datos) {',
          '        String[] v = datos.split(" ");',
          '        float[] out = new float[v.length];',
          '        for (int i = 0; i < v.length; i++) {',
          '            out[i] = Float.parseFloat(v[i]);',
          '        }',
          '        return out;',
          '    }', '',
          '    /**',
          '     * La base (0..2) y la punta (3..5) de la hoja a "s" segundos de animacion, en',
          '     * "out"; falso si la tabla no llega (la animacion ya acabo).',
          '     */',
          '    public static boolean en(float[] tabla, float s, float[] out) {',
          '        int n = tabla.length / 6 - 1;',
          '        float f = s * HZ;',
          '        if (f < 0 || f > n) {',
          '            return false;',
          '        }',
          '        int i = Math.min((int) f, n - 1);',
          '        float k = f - i;',
          '        for (int c = 0; c < 6; c++) {',
          '            out[c] = tabla[i * 6 + c] + (tabla[(i + 1) * 6 + c] - tabla[i * 6 + c]) * k;',
          '        }',
          '        return true;',
          '    }',
          '}']
    return '\n'.join(L) + '\n'


# ----------------------------------------------------------------------
#  Hojas de control
# ----------------------------------------------------------------------
def pose_hoja(nombre, s):
    pose = pose_en(nombre, s)
    suelta = (nombre == 'OFRENDA' and s >= T_OFRENDA_SUELTA) or nombre == 'OFRENDA_SOSTIENE' or \
             (nombre == 'DIOS' and T_DIOS_SUELTA <= s < T_DIOS_RECOGE)
    if suelta:
        pose['espada'] = {**pose.get('espada', {}), 'oculto': True}
    else:
        pose['espada_suelta'] = {'oculto': True}
    return pose


MARCAS = {'BARRIDO': T_TAJOS, 'SOL': T_SOL_LANZA, 'DIOS': T_DIOS_LANZA, 'CASTIGO': (T_CASTIGO_MARCA, T_CASTIGO_RAYO),
          'CASTIGO_ONDA': (T_CASTIGO_RAYO, T_ONDA_CLAVA), 'TAMBALEO': (T_TAMBALEO_RUGE,), 'GRITO': (T_GRITO,),
          'OFRENDA': (T_OFRENDA_AGARRA,), 'TROMPETAS': (T_TROMPETAS_ALZA,), 'FUENTES': (T_FUENTES_CLAVA,),
          'DESPERTAR': (T_DESPERTAR_RUGE,)}


def tiempos_hoja(nombre):
    a = ANIMS[nombre]
    n = min(12, max(6, int(round(a['dur'] / 0.2)) + 1))
    ts = [round(a['dur'] * i / (n - 1), 2) for i in range(n)]
    for m in MARCAS.get(nombre, ()):
        if all(abs(m - t) > 0.06 for t in ts):
            ts.append(round(m, 2))
    return sorted(ts)


# ----------------------------------------------------------------------
if __name__ == '__main__':
    import time
    t0 = time.time()
    for nombre in ANIMS:
        hornear(nombre)
    print('horneado en', round(time.time() - t0, 1), 's')
    print('espada clavada: se hunde', round(ajustar_espada_suelta(), 1), 'px al soltarla')
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
    texto = java_anims()
    with open(os.path.join(CLI, 'NovilisAnimaciones.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(texto)
    with open(os.path.join(CLI, 'NovilisEstelas.java'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(java_estelas())
    geo, puntos, tiempos = java_geometria()
    with open(os.path.join(RAIZ, 'src/main/java/com/atalaya/entity/NovilisGeometria.java'), 'w', encoding='utf-8',
              newline='\n') as fh:
        fh.write(geo)
    claves = sum(len(ks) for a in ANIMS.values() for _, _, ks in a['canales'])
    print('atlas', nj.ANCHO_ATLAS, 'x', alto, '|', len(nj.ORDEN), 'piezas |', len(ANIMS), 'animaciones |', claves, 'claves |',
          len(texto) // 1024, 'KB de Java')
    for k, v in puntos.items():
        print(f'  {k:16s} izq {v[0]:6.2f}  alto {v[1]:6.2f}  frente {v[2]:6.2f}')

    if RENDERS:
        import novilis_hojas as nh
        os.makedirs(RENDERS, exist_ok=True)
        base, brillo = pieles.get(1) or (np.array(Image.open(os.path.join(TEX, 'novilis_f1.png')).convert('RGBA')),
                                         np.array(Image.open(os.path.join(TEX, 'novilis_brillo_f1.png')).convert('RGBA')))
        solo = sys.argv[3].split(',') if len(sys.argv) > 3 else list(ANIMS)
        for nombre in solo:
            nh.tira(pose_hoja, nombre, tiempos_hoja(nombre), uv, alto, base, brillo, RENDERS, '', MARCAS.get(nombre, ()))
            print('hoja', nombre, flush=True)

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

# ----------------------------------------------------------------------
#  El despertar de la presentacion (190 ticks): la camara le da vueltas
#  mientras despierta por partes, y acaba con su gran rugido. Los tiempos son
#  los mismos en los cuatro jefes (la camara va con ellos):
#    0        duerme como una esfinge, cada vez respira mas hondo; le tiembla
#             la punta de la cola y se le mueve una oreja
#    ABRE     se le encienden los ojos; alza la cabeza con las orejas tiesas
#             y mira alrededor
#    SE_ALZA  saca las manos de la tierra y se estira como un gato: las manos
#             muy por delante, el pecho abajo y la grupa arriba, y bosteza;
#             luego se echa adelante sobre ellas, recoge las manos, estira las
#             patas de atras una a una y arquea el lomo
#    ALZADO   agazapado, la cabeza baja y grune, la cola como un latigo y la
#             cresta de jade que se eriza de delante atras
#    RUGE     se alza sobre las patas de atras y ruge con todo el cuerpo; lo
#             sostiene temblando, vuelve a apoyar las manos (APOYA) y se queda
#             como en el reposo, de donde sale el resto del juego
#  Las zarpas que apoyan no resbalan: las piernas salen de una IK sobre la
#  pose (los angulos escritos solo eligen hacia donde se doblan).
# ----------------------------------------------------------------------
T_DESPERTAR = 9.5
T_DESP_ABRE = 2.0
T_DESP_SE_ALZA = 3.5
T_DESP_ALZADO = 6.0
T_DESP_RUGE = 7.25
T_DESP_APOYA = 8.7


def pista(*claves):
    """Una curva suave que pasa por las claves (t, valor): Hermite monotona
    (no se pasa de las claves y se para en los extremos)."""
    ts = np.array([c[0] for c in claves], float)
    vs = np.array([c[1] for c in claves], float)
    h = np.diff(ts)
    d = np.diff(vs) / h
    m = np.zeros(len(ts))
    for i in range(1, len(ts) - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(s):
        if s <= ts[0]:
            return float(vs[0])
        if s >= ts[-1]:
            return float(vs[-1])
        i = int(np.searchsorted(ts, s)) - 1
        u = (s - ts[i]) / h[i]
        return float((2 * u ** 3 - 3 * u ** 2 + 1) * vs[i] + (u ** 3 - 2 * u ** 2 + u) * h[i] * m[i]
                     + (-2 * u ** 3 + 3 * u ** 2) * vs[i + 1] + (u ** 3 - u ** 2) * h[i] * m[i + 1])
    return f


def _suave(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def _ventana(s, t0, t1, sube=0.15, baja=0.15):
    """1 entre t0 y t1, con rampas suaves de sube y baja segundos."""
    return _suave((s - t0) / sube) * (1 - _suave((s - t1 + baja) / baja))


def _toques(s, toques):
    """Sacudidas cortas (t0, dura, amplitud): van y vuelven una vez."""
    v = 0.0
    for t0, d, a in toques:
        if t0 <= s <= t0 + d:
            v += a * math.sin(2 * math.pi * (s - t0) / d) * math.sin(math.pi * (s - t0) / d)
    return v


# --- La IK de las piernas -----------------------------------------------
_CADENAS = {'mano_izq': ('brazo_izq', 'antebrazo_izq', 'mano_izq'), 'mano_der': ('brazo_der', 'antebrazo_der', 'mano_der'),
            'pie_izq': ('muslo_izq', 'tibia_izq', 'tarso_izq', 'pie_izq'), 'pie_der': ('muslo_der', 'tibia_der', 'tarso_der', 'pie_der')}
_APOYO = (0, 8, -8)


def _local(nombre, pose):
    p = rj.PARTES[nombre]
    ex = pose.get(nombre, {})
    a = [p.rot[i] + ex.get('rot', (0, 0, 0))[i] for i in range(3)]
    q = [p.pivote[i] + ex.get('pos', (0, 0, 0))[i] for i in range(3)]
    e = ex.get('esc', (1, 1, 1))
    return vr.T(*q) @ vr.Rz(a[2] * rj.D2R) @ vr.Ry(a[1] * rj.D2R) @ vr.Rx(a[0] * rj.D2R) @ np.diag([e[0], e[1], e[2], 1.0])


def _fk_pierna(Mc, cadena, ang, giro):
    """Donde apoya la zarpa (pixeles del modelo) y su cabeceo (grados; positivo,
    los dedos hacia abajo) con los angulos x de la cadena y el giro de lado de la
    primera pieza."""
    M = Mc
    for i, n in enumerate(cadena):
        p = rj.PARTES[n]
        M = M @ vr.T(*p.pivote) @ vr.Rz((p.rot[2] + (giro if i == 0 else 0.0)) * rj.D2R) @ vr.Ry(p.rot[1] * rj.D2R) \
            @ vr.Rx((p.rot[0] + ang[i]) * rj.D2R)
    c = (M @ np.array([*_APOYO, 1.0]))[:3]
    v = M[:3, :3] @ np.array([0.0, 0.0, -1.0])
    return c, math.degrees(math.atan2(v[1], -v[2]))


def _ik_pierna(Mc, cadena, ang0, giro0, objetivo, cabeceo, x0=None):
    """Levenberg-Marquardt: la zarpa al objetivo y con el cabeceo pedido, lo mas
    cerca posible de los angulos escritos (que deciden hacia donde dobla).
    Arranca de x0 si se le da."""
    ref = np.array([*ang0, giro0], float)
    x = ref.copy() if x0 is None else np.array(x0, float)
    wr = np.array([0.02] * len(ang0) + [0.25])

    def res(x):
        c, cab = _fk_pierna(Mc, cadena, x[:-1], x[-1])
        return np.concatenate([c - objetivo, [0.4 * (cab - cabeceo)], wr * (x - ref)])
    r0 = res(x)
    e0 = r0 @ r0
    lam = 1e-2
    for _ in range(60):
        J = np.empty((len(r0), len(x)))
        for j in range(len(x)):
            dx = np.zeros(len(x))
            dx[j] = 1e-3
            J[:, j] = (res(x + dx) - r0) / 1e-3
        A, g = J.T @ J, J.T @ r0
        paso = None
        while lam < 1e9:
            paso = np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), -g)
            r1 = res(x + paso)
            if r1 @ r1 < e0:
                x, r0, e0 = x + paso, r1, r1 @ r1
                lam = max(lam / 3, 1e-8)
                break
            lam *= 4
        if paso is None or lam >= 1e9 or np.abs(paso).max() < 1e-5:
            break
    return x


# --- Las poses del despertar ----------------------------------------------
# El cuerpo (cabeceo: positivo baja el hocico; baja y avanza en pixeles).
_d_cuerpo_x = pista((0, -2), (3.5, -2), (3.9, 2), (4.55, 19), (4.85, 18), (5.3, -3), (5.6, -2), (5.85, 5),
                    (6.0, 5), (6.3, 7), (6.85, 6), (7.05, 10), (7.27, -30), (7.6, -32), (8.3, -26), (8.55, -4),
                    (T_DESP_APOYA, 5), (8.95, -1.5), (9.5, 0))
_d_baja = pista((0, 58), (3.3, 58), (3.5, 59.5), (3.9, 52), (4.55, 31), (4.85, 30), (5.3, 10), (5.6, 8), (5.85, -4),
                (6.0, -4), (6.3, 19), (6.85, 17), (7.05, 24), (7.27, -14), (7.6, -15), (8.3, -11), (8.55, 2),
                (T_DESP_APOYA, 6), (8.95, 0.6), (9.2, 1.2), (9.5, 0))
_d_avanza = pista((0, 0), (3.5, 0), (3.9, -4), (4.55, -10), (4.85, -10), (5.35, 21), (5.65, 22), (6.0, 0),
                  (6.3, -4), (6.85, -4), (7.05, -6), (7.27, -4), (8.3, -4), (T_DESP_APOYA, 2), (9.5, 0))
# La cabeza y el cuello (x negativo la levanta), la boca y las orejas.
_d_cuello = pista((0, -22), (2.0, -22), (2.25, -46), (2.45, -42), (3.3, -41), (3.55, -30), (3.95, -18), (4.4, -26),
                  (4.6, -30), (4.85, -26), (5.3, -6), (5.6, 2), (5.85, 22), (6.0, 22), (6.3, 12), (6.85, 10),
                  (7.05, 18), (7.27, -6), (7.6, -8), (8.3, -2), (8.55, 2), (T_DESP_APOYA, 8), (9.0, 2), (9.5, 0))
_d_cabeza_x = pista((0, -14), (2.0, -14), (2.25, 2), (2.45, 0), (3.5, 0), (3.95, -4),
                    (4.3, -14), (4.6, -30), (4.85, -24), (5.3, -2), (5.6, 4), (5.85, 16), (6.0, 16), (6.3, 6),
                    (6.85, 4), (7.05, 12), (7.27, 4), (7.6, 4), (8.3, 12), (8.55, 2), (T_DESP_APOYA, 6),
                    (9.0, 0), (9.5, 0))
_d_cabeza_y = pista((0, 0), (1.4, 0), (1.7, 5), (2.0, 3), (2.5, 0), (2.8, 17), (3.1, 16), (3.4, -7), (3.7, -4),
                    (4.2, 0), (6.0, 0), (6.4, 9), (6.75, -8), (7.0, -2), (7.27, 0), (9.5, 0))
_d_boca = pista((0, -14), (2.0, -14), (2.15, -8), (2.7, -7), (2.95, 5), (3.25, -5), (3.6, -8), (4.25, -6),
                (4.6, 24), (4.8, 26), (5.05, -4), (5.6, -6), (6.0, 0), (6.3, 10), (6.85, 9), (7.05, 2),
                (7.27, 40), (7.5, 43), (8.2, 35), (8.55, 18), (8.85, 4), (9.15, -4), (9.5, 0))
_d_orejas = pista((0, -10), (2.0, -10), (2.1, 17), (2.3, 12), (3.4, 12), (4.3, 8), (4.6, -14), (4.85, -12),
                  (5.1, 6), (6.0, 4), (6.3, -22), (6.85, -20), (7.05, -28), (7.27, -26), (8.4, -24), (8.9, 2),
                  (9.5, 0))
# La cola: sube la base, se desenrosca de alrededor del cuerpo y se pone a latiguear.
_d_cola_sube = pista((0, -4), (3.5, -4), (4.55, 26), (4.85, 24), (5.3, 16), (5.6, 4), (5.85, -28), (6.0, -26),
                     (6.3, 8), (6.85, 10), (7.05, 2), (7.27, 22), (8.3, 22), (T_DESP_APOYA, 4), (9.5, 0))
_d_cola_lado = pista((0, 34), (3.6, 34), (4.6, 4), (5.6, 0), (9.5, 0))
_d_enrosca = pista((0, 1), (3.6, 1), (4.6, 0), (9.5, 0))
_d_onda = pista((0, 0), (3.6, 0), (4.4, 7), (5.6, 5), (6.1, 6), (6.35, 20), (6.95, 20), (7.15, 6), (8.3, 5),
                (T_DESP_APOYA, 10), (9.5, 0))
_enrosca = {'cola2': (-3.4, 26), 'cola4': (-2.3, 28), 'cola6': (-0.3, 22)}
# Los ojos: una rendija mientras duerme; al abrir, de golpe y algo de mas.
_d_ojo = pista((0, 0.15), (T_DESP_ABRE, 0.15), (2.08, 1.35), (2.25, 0.95), (2.4, 1.0), (4.4, 1.0), (4.6, 0.45),
               (4.8, 0.45), (5.0, 1.0), (7.15, 1.0), (7.27, 1.2), (8.4, 1.15), (8.8, 1.0), (9.5, 1.0))
# La cresta de jade se eriza de delante atras (cada pieza un poco despues).
_CRESTA = ['corona_c', 'cresta_cuello'] + [f'cresta{i}' for i in range(8)]
_d_cresta = pista((0, 0), (6.15, 0), (6.55, 1.0), (7.15, 1.0), (7.27, 1.25), (7.5, 1.0), (8.4, 1.0), (9.25, 0), (9.5, 0))
# Los coletazos de la punta de la cola (t0, dura, grados).
_PUNTA = [(0.55, 0.45, 18), (1.45, 0.4, -16), (2.35, 0.35, 22), (2.95, 0.4, -18), (3.3, 0.35, 14)]


def _respiracion(s):
    """La respiracion del que duerme, cada vez mas honda y deprisa (de un ciclo
    de 6 s a uno de 2,4 s); se apaga al levantarse."""
    f0, f1 = 1 / 6.0, 1 / 2.4
    fase = 2 * math.pi * (f0 * s + (f1 - f0) * min(s, 2.0) ** 2 / 4.0 + (f1 - f0) * max(0.0, s - 2.0))
    amp = (1.0 + 1.0 * _suave(s / 2.0)) * (1 - _suave((s - 3.4) / 0.4))
    return amp, fase


def _pose_cuerpo(s):
    """Todo menos las piernas."""
    amp, fase = _respiracion(s)
    tiembla = 0.0
    if 7.3 <= s <= 8.4:
        # el temblor del rugido: va y viene cada 0,075 s, cada vez menos
        tiembla = math.cos(math.pi * (s - 7.3) / 0.075) * (1 - 0.6 * (s - 7.3) / 1.1)
    lado = 2.5 * math.sin(2 * math.pi * (s - 6.2) / 1.1) * _ventana(s, 6.2, 7.0, 0.2, 0.2)
    sacude = 12 * math.sin(2 * math.pi * (s - 8.85) / 0.42) * _ventana(s, 8.85, 9.45, 0.05, 0.3)
    p = sumar(cuerpo(x=_d_cuerpo_x(s) + 0.4 * amp * math.sin(fase), z=lado + 0.8 * tiembla,
                     baja=_d_baja(s) + 1.5 * amp * math.sin(fase), avanza=_d_avanza(s), lado=0.6 * lado),
              {'peto': {'pos': (0, 0, -0.8 * amp * math.sin(fase))}},
              cabeza(x=_d_cabeza_x(s) + 1.5 * amp * math.sin(fase + 0.5) + 2.5 * tiembla,
                     y=_d_cabeza_y(s) + 2.0 * tiembla + sacude, z=6 * _ventana(s, 2.8, 3.15, 0.12, 0.15) + 0.4 * sacude,
                     boca=_d_boca(s) + 3 * tiembla + 4 * math.sin(2 * math.pi * s / 0.6) * _ventana(s, 6.3, 6.95, 0.1, 0.1),
                     cuello=_d_cuello(s), cuello_y=0.4 * _d_cabeza_y(s), orejas=_d_orejas(s)),
              # una oreja que se mueve en suenos y otra al mirar
              {'oreja_izq': r(_toques(s, [(1.0, 0.35, 22), (3.0, 0.3, -14)])),
               'oreja_der': r(_toques(s, [(2.6, 0.3, 16)]))})
    # la cola: se desenrosca, sube y latiguea; la punta tiembla mientras duerme
    w = 2 * math.pi * (s - 6.2) / 0.95
    p = sumar(p, cola(sube=_d_cola_sube(s), lado=_d_cola_lado(s) + 26 * math.sin(w) * _ventana(s, 6.2, 7.05, 0.2, 0.15),
                      fase=2 * math.pi * s / 1.3 + 1.5 * w * _suave((s - 6.0) / 0.3), onda=_d_onda(s), retraso=0.6))
    k = _d_enrosca(s)
    for n, (x, y) in _enrosca.items():
        p = sumar(p, {n: r(x * k, y * k)})
    p = sumar(p, {'cola5': r(0, 0.5 * _toques(s, _PUNTA)), 'cola6': r(0, _toques(s, _PUNTA))})
    o = _d_ojo(s)
    p = sumar(p, {'ojo_izq': {'esc': (1 + 0.3 * (o - 1) * (o > 1), o, 1)}, 'ojo_der': {'esc': (1 + 0.3 * (o - 1) * (o > 1), o, 1)}})
    for i, n in enumerate(_CRESTA):
        e = _d_cresta(s - 0.05 * i if s < 7.0 else s)
        p = sumar(p, {n: {'esc': (1 + 0.12 * e, 1 + 0.3 * e, 1 + 0.12 * e)}})
    return p


# Los angulos escritos de cada pierna (x de cada pieza y el giro de lado):
# dormido, estirado, de pie, agazapado y alzado. Con la IK solo eligen como dobla.
_ESF = {'mano_izq': (-68, 52, 16, 0), 'mano_der': (-64, 50, 14, 0),
        'pie_izq': (-58, 88, -66, 40, 8), 'pie_der': (-58, 88, -66, 40, 8)}


def _escritos(pieza, s):
    lado = 1 if pieza.endswith('izq') else -1
    e = _ESF[pieza]
    if pieza.startswith('mano'):
        claves = [(0, e), (3.5, e), (4.0, (-44, -80, 107, 0)), (4.85, (-44, -80, 107, 0)), (5.4, (0, 0, 0, 0)),
                  (6.0, (0, 0, 0, 0)), (6.3, (37, -78, 33, 6)), (6.95, (37, -78, 33, 6)),
                  (7.3, (-40, -30, 40, -12)), (8.3, (-36, -34, 36, -12)), (8.6, (-20, -20, 20, 0)), (9.5, (0, 0, 0, 0))]
    else:
        claves = [(0, e), (3.85, e), (4.3, (-24, 30, -16, 10, 6)), (4.85, (-24, 30, -16, 10, 6)), (5.4, (0, 0, 0, 0, 0)),
                  (6.0, (0, 0, 0, 0, 0)), (6.3, (-30, 50, -36, 24, 0)), (6.95, (-30, 50, -36, 24, 0)),
                  (7.05, (-36, 58, -42, 28, 0)), (7.3, (24, 18, -14, 8, 0)), (8.3, (24, 18, -14, 8, 0)),
                  (8.7, (-8, 14, -8, 4, 0)), (9.5, (0, 0, 0, 0, 0))]
    out = []
    for j in range(len(claves[0][1])):
        out.append(pista(*[(t, v[j]) for t, v in claves])(s))
    out[-1] *= lado
    return out


def _poner_pierna(p, pieza, ang):
    lado = 1 if pieza.endswith('izq') else -1
    if pieza.startswith('mano'):
        return sumar(p, mano(lado, ang[0], ang[1], ang[2], ang[3] * lado))
    return sumar(p, pata(lado, ang[0], ang[1], ang[2], ang[3], ang[4] * lado))


def _apoyo_de(pose, pieza):
    """Donde apoya la zarpa en la pose (bloques, espacio del cuerpo)."""
    Mc = _local('raiz', pose) @ _local('cuerpo', pose)
    ex = [pose[n]['rot'][0] for n in _CADENAS[pieza]]
    return np.array(rj.a_bloques(_fk_pierna(Mc, _CADENAS[pieza], ex, pose[_CADENAS[pieza][0]]['rot'][2])[0]))


# Las marcas de las zarpas (bloques, espacio del cuerpo): las de pie salen de la pose de reposo.
_DE_PIE = {n: _apoyo_de(_poner_pierna({}, n, (0, 0, 0, 0) if n.startswith('mano') else (0, 0, 0, 0, 0)), n)
           for n in _CADENAS}
_ESTIRADO = {n: _DE_PIE[n] + np.array([0, 0, 2.6]) for n in ('mano_izq', 'mano_der')}
_ESTIRADO.update({n: np.array([1.15 * (1 if n.endswith('izq') else -1), _DE_PIE[n][1], -4.21]) for n in ('pie_izq', 'pie_der')})

# Cada zarpa: (t0, t1, de, a, lo que sube en el paso, cabeceo en medio, por donde
# pasa). 'libre' es la pose escrita: al soltarse o apoyar desde ella, la pierna
# pasa de unos angulos a otros (sin camino). Las manos salen de la tierra y se
# estiran, se recogen bajo los hombros, se sueltan al alzarse y apoyan al bajar;
# las patas salen y se estiran hacia atras una a una (el paso por arriba y atras).
_ATRAS = (np.array([0, 1.3, -7.3]), np.array([0, 1.1, -7.4]))
_PLAN = {
    'mano_izq': [(3.5, 3.92, 'libre', 'estirado', 0, 0, None), (4.85, 5.15, 'estirado', 'de_pie', 0.9, 25, None),
                 (7.05, 7.25, 'de_pie', 'libre', 0, 0, None), (8.4, T_DESP_APOYA, 'libre', 'de_pie', 0, 0, None)],
    'mano_der': [(3.6, 4.0, 'libre', 'estirado', 0, 0, None), (5.0, 5.3, 'estirado', 'de_pie', 0.9, 25, None),
                 (7.08, 7.28, 'de_pie', 'libre', 0, 0, None), (8.45, T_DESP_APOYA + 0.03, 'libre', 'de_pie', 0, 0, None)],
    'pie_izq': [(3.85, 4.2, 'libre', 'estirado', 0, 0, None), (5.2, 5.6, 'estirado', 'de_pie', 0, -50, _ATRAS)],
    'pie_der': [(3.9, 4.25, 'libre', 'estirado', 0, 0, None), (5.45, 5.85, 'estirado', 'de_pie', 0, -50, _ATRAS)],
}


def _marca(pieza, nombre):
    return {'estirado': _ESTIRADO, 'de_pie': _DE_PIE}[nombre][pieza]


def _objetivo(pieza, s):
    """Lo que hace la zarpa en s: None si va suelta (la pose escrita);
    ('ik', donde, cabeceo) si apoya o da un paso (bloques); o ('mezcla', donde,
    cabeceo, k, t) al soltarse o al apoyar desde suelta: los angulos pasan de los
    escritos a los que la dejan apoyada (con k de 0 a 1; t, de donde se toman los
    escritos que eligen como dobla la pierna apoyada)."""
    plan = _PLAN[pieza]
    if s < plan[0][0]:
        return None
    for i, (t0, t1, de, a, alto, cab, por) in enumerate(plan):
        sig = plan[i + 1][0] if i + 1 < len(plan) else 1e9
        if t1 < s < sig:
            return None if a == 'libre' else ('ik', _marca(pieza, a), 0.0)
        if t0 <= s <= t1:
            u = (s - t0) / (t1 - t0)
            if de == 'libre':
                return 'mezcla', _marca(pieza, a), 0.0, _suave(u), t1
            if a == 'libre':
                return 'mezcla', _marca(pieza, de), 0.0, 1 - _suave(u), t0
            pa, pb = _marca(pieza, de), _marca(pieza, a)
            if por is not None:
                pts = [(0, pa), (0.45, np.array([pa[0], *por[0][1:]])), (0.65, np.array([pa[0], *por[1][1:]])), (1, pb)]
                pos = np.array([pista(*[(t, q[j]) for t, q in pts])(u) for j in range(3)])
                pos[0] = pa[0] + (pb[0] - pa[0]) * _suave(u)
            else:
                pos = pa + (pb - pa) * _suave(u)
                pos[1] += alto * math.sin(math.pi * u)
            return 'ik', pos, cab * math.sin(math.pi * u)
    return None


_IK_ANTES = {}


def pose_despertar(s):
    p = _pose_cuerpo(s)
    Mc = _local('raiz', p) @ _local('cuerpo', p)
    for pieza, cadena in _CADENAS.items():
        ang = _escritos(pieza, s)
        obj = _objetivo(pieza, s)
        if obj is not None:
            ref = ang if obj[0] == 'ik' else _escritos(pieza, obj[4])
            b = np.array(obj[1])
            dest = np.array([b[0] * 16, 24.016 - b[1] * 16, -b[2] * 16])
            # se arranca de la solucion del tick anterior: asi la pierna no cambia de
            # golpe hacia donde dobla
            antes = _IK_ANTES.get(pieza)
            x0 = antes[1] if antes is not None and 0 < s - antes[0] <= 0.06 else None
            x = _ik_pierna(Mc, cadena, ref[:-1], ref[-1], dest, obj[2], x0)
            _IK_ANTES[pieza] = (s, x)
            ang = list(x) if obj[0] == 'ik' else [e + (v - e) * obj[3] for e, v in zip(ang, x)]
        p = _poner_pierna(p, pieza, ang)
    return p


def _tiempos_despertar():
    """Las claves: una por tick (cada media en el temblor del rugido); al
    exportar, cada pieza se queda solo con las que necesita (simplificar)."""
    ts = {round(k * 0.05, 3) for k in range(int(round(T_DESPERTAR / 0.05)) + 1)}
    ts.update(round(7.3 + k * 0.025, 3) for k in range(45))
    return sorted(ts)


anim('DESPERTAR', T_DESPERTAR, [(t, pose_despertar(t), 'c') for t in _tiempos_despertar()])
ANIMS['DESPERTAR']['simplifica'] = True

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


def _catmull_vec(K, V, T):
    """Lo que da un canal (claves en K, valores V) en los tiempos T, como en el
    juego: Catmull-Rom con la clave anterior y la siguiente de cada tramo."""
    n = len(K)
    idx = np.searchsorted(K, T, side='left')
    prev = np.maximum(0, idx - 1)
    nxt = np.minimum(n - 1, prev + 1)
    den = np.where(nxt != prev, K[nxt] - K[prev], 1.0)
    al = np.clip((T - K[prev]) / den, 0.0, 1.0)[:, None]
    al = np.where((nxt != prev)[:, None], al, 0.0)
    p0, p1, p2, p3 = V[np.maximum(0, prev - 1)], V[prev], V[nxt], V[np.minimum(n - 1, nxt + 1)]
    return catmull(al, p0, p1, p2, p3)


def simplificar(ks, tol, paso=0.0125):
    """Quita las claves que sobran en un canal (todas suaves) mientras la curva
    no se aparte mas de tol de la que dan todas: en las animaciones largas
    muestreadas cada pieza solo guarda las claves donde se mueve."""
    K = np.array([k[0] for k in ks], float)
    V = np.array([k[1] for k in ks], float)
    T = np.arange(0.0, K[-1] + 1e-9, paso)
    ref = _catmull_vec(K, V, T)
    vivas = list(range(len(ks)))
    cambia = True
    while cambia:
        cambia = False
        j = 1
        while j < len(vivas) - 1:
            prueba = vivas[:j] + vivas[j + 1:]
            lo, hi = K[vivas[max(0, j - 2)]], K[vivas[min(len(vivas) - 1, j + 2)]]
            m = (T >= lo) & (T <= hi)
            err = np.abs(_catmull_vec(K[prueba], V[prueba], T[m]) - ref[m]).max()
            if err < tol:
                vivas = prueba
                cambia = True
            else:
                j += 1
    return [ks[i] for i in vivas]


# Lo que se puede apartar cada canal al simplificar: las piernas y el cuerpo,
# poco (las zarpas que apoyan no deben resbalar); lo demas, algo mas.
def _tolerancia(pieza, tipo):
    if tipo == 'esc':
        return 0.006
    if tipo == 'pos':
        return 0.08
    piernas = ('brazo', 'antebrazo', 'mano', 'muslo', 'tibia', 'tarso', 'pie', 'cuerpo')
    return 0.15 if pieza.split('_')[0] in piernas else 0.4


def canales(a):
    if a.get('simplifica'):
        if '_canales' not in a:
            a['_canales'] = [(pz, tp, simplificar(ks, _tolerancia(pz, tp))) for pz, tp, ks in _canales(a)]
        return a['_canales']
    return _canales(a)


def _canales(a):
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
        # por donde saca las manos de la tierra al despertar (entre las dos)
        'MANOS_DESPERTAR': tuple(np.mean([p_bloques('DESPERTAR', T_DESP_SE_ALZA + 0.5, n, _APOYO)
                                          for n in ('mano_izq', 'mano_der')], axis=0)),
    }

    def tick(s):
        return int(round(s * 20))
    tiempos = {
        'DURACION_DESPERTAR': tick(ANIMS['DESPERTAR']['dur']), 'DESPERTAR_ABRE': tick(T_DESP_ABRE),
        'DESPERTAR_SE_ALZA': tick(T_DESP_SE_ALZA), 'DESPERTAR_ALZADO': tick(T_DESP_ALZADO), 'DESPERTAR_RUGE': tick(T_DESP_RUGE),
        'DESPERTAR_APOYA': tick(T_DESP_APOYA),
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
    L.append('')
    # La cabeza (el centro de la cara) y el pecho en el despertar, cada 5 ticks:
    # la camara de la presentacion los sigue.
    for nombre, pieza, local in (('CABEZA', 'cabeza', (0, -8, -30)), ('PECHO', 'sol', (0, 3, -118.5))):
        filas = []
        for k in range(0, tick(ANIMS['DESPERTAR']['dur']) + 1, 5):
            x, y, z = (round(v, 2) + 0.0 for v in p_bloques('DESPERTAR', k / 20.0, pieza, local))
            filas.append(f'{{{x:.2f}F, {y:.2f}F, {z:.2f}F}}')
        L.append(f'    /** {nombre.capitalize()} en el despertar, cada 5 ticks (bloques; la camara de la presentacion la sigue). */')
        L.append(f'    public static final float[][] {nombre}_DESPERTAR = {{' + ', '.join(filas) + '};')
    L.append('')
    for nombre in ('cabeza', 'pecho'):
        L.append(f'    /** Donde esta {"la cabeza" if nombre == "cabeza" else "el pecho"} a los tantos ticks del despertar (entre filas, en linea recta). */')
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

"""
Pase de fisica de las animaciones de Nerea.

Las poses que se escriben a mano (nerea_juego_anim.py) dicen lo que HACE: el
brazo que sube, el torso que se inclina. Lo que aqui se calcula es lo que un
cuerpo de diez bloques no puede dejar de hacer:

  PIES PLANTADOS   las piernas salen de cinematica inversa (dos huesos): cada
                   pie tiene un punto de apoyo en el suelo y la pierna se dobla
                   lo que haga falta cuando la pelvis baja, gira o se inclina.
                   Nada de pies que patinan o rodillas que atraviesan el suelo.
  INERCIA          la cadena de la mano (con el gancho), los corales de la
                   corona y los hombros y las algas del faldon se simulan como
                   masas con gravedad, muelle y rozamiento de agua: se quedan
                   atras, se pasan de largo y se asientan.
  RETRASO          cuello, cabeza, mandibula y antebrazos siguen a lo que los
                   lleva con un muelle amortiguado: un poco tarde y con un leve
                   rebote, como la carne sobre el hueso.

Todo se simula a 80 Hz y se hornea en keyframes de vanilla, asi que en el juego
no cuesta nada. Las animaciones en bucle se simulan tres vueltas y se guarda la
ultima, para que empalmen sin salto.
"""
import math
import numpy as np
import nerea_juego as nj

D2R = math.pi / 180
R2D = 180 / math.pi
HZ = 80
L_MUSLO = 16.0
L_ESPINILLA = 15.0
REPOSO_PIERNA = -6.0
REPOSO_ESPINILLA = 10.0
REPOSO_PIE = -4.0

# --- piezas con inercia: (punta en su espacio local, modo, parametros) ---
#  modo 'cuelga': pendulo con gravedad (y un muelle flojo hacia su reposo)
#  modo 'muelle': vuelve a su reposo respecto al padre, empujado por la inercia
SIMULADAS = {
    'cadena_mano': ((0, 24.0, 0), 'cuelga', dict(g=98.0, roce=2.2, k=4.0)),
    'algas_del': ((0, 17.5, 0), 'cuelga', dict(g=40.0, roce=5.0, k=30.0)),
    'algas_tras': ((0, 17.5, 0), 'cuelga', dict(g=40.0, roce=5.0, k=30.0)),
}
# (desde el remake la corona y los corales son mas largos: x1,7 y x1,5)
for _c, _alto in (('corona_c1', 17), ('corona_c2', 13.6), ('corona_c3', 11.9), ('corona_c4', 10.2)):
    SIMULADAS[_c] = ((0, -_alto, 0), 'muelle', dict(g=0.0, roce=7.0, k=260.0))
for _n in ('izq', 'der'):
    for _c, _alto in (('coral_h1_', 13.5), ('coral_h2_', 9), ('coral_h3_', 10.5)):
        SIMULADAS[_c + _n] = ((0, -_alto, 0), 'muelle', dict(g=0.0, roce=7.0, k=220.0))
# La barba y la capa de algas del remake: cuelgan y ondean como en el agua.
for _i, _largo in enumerate((20, 27, 32, 26, 19)):
    SIMULADAS[f'barba_{_i}'] = ((0, _largo, 0), 'cuelga', dict(g=30.0, roce=4.0, k=24.0))
for _i, _largo in enumerate((52, 60, 64, 60, 52)):
    SIMULADAS[f'capa_{_i}'] = ((0, _largo, 0), 'cuelga', dict(g=26.0, roce=3.6, k=18.0))

# --- piezas con retraso: (frecuencia en Hz, amortiguamiento) ---
RETRASADAS = {
    'cuello': (3.2, 0.6), 'cabeza': (2.8, 0.55), 'mandibula': (4.5, 0.5),
    # el antebrazo derecho no: lleva el tridente y es el brazo el que manda
    'antebrazo_izq': (4.0, 0.6),
}

PIERNAS = [p + '_' + l for l in ('izq', 'der') for p in ('pierna', 'espinilla', 'pie')]


def tobillo_reposo(lado):
    return nj.punto({}, 'pie_' + lado)


# ----------------------------------------------------------------------
#  Cinematica inversa de una pierna
# ----------------------------------------------------------------------
def ik_pierna(M_pelvis, lado, objetivo, pie_grados=0.0, giro=0.0):
    """Angulos (pierna xyz, espinilla x, pie x) en grados ABSOLUTOS respecto
    al padre para que el tobillo caiga en "objetivo" (espacio del modelo).

    giro: rotacion Y de la pierna (el pie apunta a otro lado que la pelvis).
    pie_grados: inclinacion del pie respecto al suelo (0 = plano).
    """
    s = 1 if lado == 'izq' else -1
    inv = np.linalg.inv(M_pelvis)
    T = (inv @ np.array([*objetivo, 1.0]))[:3]
    H = np.array([6.0 * s, 2.0, 0.0])
    D = T - H
    ry = giro * D2R
    rz = math.atan2(-D[0], D[1])
    for _ in range(4):
        D2 = nj.Ry(-ry)[:3, :3] @ nj.Rz(-rz)[:3, :3] @ D
        rz += math.atan2(-D2[0], D2[1])
    D2 = nj.Ry(-ry)[:3, :3] @ nj.Rz(-rz)[:3, :3] @ D
    d = float(np.linalg.norm(D2))
    d = min(max(d, abs(L_MUSLO - L_ESPINILLA) + 0.5), L_MUSLO + L_ESPINILLA - 0.05)
    phi = math.atan2(D2[2], D2[1])
    alfa = math.acos(max(-1.0, min(1.0, (L_MUSLO ** 2 + d * d - L_ESPINILLA ** 2) / (2 * L_MUSLO * d))))
    rodilla = math.pi - math.acos(max(-1.0, min(1.0, (L_MUSLO ** 2 + L_ESPINILLA ** 2 - d * d) / (2 * L_MUSLO * L_ESPINILLA))))
    muslo = phi - alfa
    # El pie: lo que haga falta para quedar a "pie_grados" del suelo, contando
    # con la inclinacion de la pelvis.
    pelvis_x = math.atan2(M_pelvis[2, 1], M_pelvis[1, 1])
    pie = pie_grados * D2R - (pelvis_x + muslo + rodilla)
    return (muslo * R2D, giro, rz * R2D), rodilla * R2D, pie * R2D


# ----------------------------------------------------------------------
#  Muestreo de los apoyos (pseudo-canales de las poses: apoyo_izq/apoyo_der)
# ----------------------------------------------------------------------
def apoyos_autor(a, s, muestrear):
    """{lado: (objetivo xyz, pie_grados, giro)} a s segundos, de las poses."""
    out = {}
    for lado in ('izq', 'der'):
        rep = tobillo_reposo(lado)
        clave = 'apoyo_' + lado
        ks_en = [(t, tuple(p.get(clave, {}).get('en', rep)), i) for t, p, i in a['claves']]
        ks_pie = [(t, (p.get(clave, {}).get('pie', 0.0), p.get(clave, {}).get('giro', 0.0), 0.0), i)
                  for t, p, i in a['claves']]
        en = muestrear(ks_en, s, 'rot')
        pg = muestrear(ks_pie, s, 'rot')
        out[lado] = (tuple(en), float(pg[0]), float(pg[1]))
    return out


# ----------------------------------------------------------------------
#  El horneado
# ----------------------------------------------------------------------
def _envolver(x):
    return (x + 180.0) % 360.0 - 180.0


def _dir_xz(t):
    """Angulos (x, z) en grados con Rz*Rx (y=0) que llevan +Y local a t."""
    t = t / (np.linalg.norm(t) + 1e-12)
    x = math.asin(max(-1.0, min(1.0, t[2])))
    z = math.atan2(-t[0], t[1])
    return x * R2D, z * R2D


def simplificar(puntos, tol=0.35):
    """Ramer-Douglas-Peucker sobre (t, (x, y, z)): quita los keyframes que la
    interpolacion entre sus vecinos ya reproduce con menos de "tol" grados."""
    if len(puntos) <= 2:
        return puntos
    t0, v0 = puntos[0]
    t1, v1 = puntos[-1]
    v0 = np.array(v0)
    v1 = np.array(v1)
    peor, idx = -1.0, -1
    for i in range(1, len(puntos) - 1):
        t, v = puntos[i]
        k = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
        e = float(np.max(np.abs(np.array(v) - (v0 + (v1 - v0) * k))))
        if e > peor:
            peor, idx = e, i
    if peor <= tol:
        return [puntos[0], puntos[-1]]
    izq = simplificar(puntos[:idx + 1], tol)
    der = simplificar(puntos[idx:], tol)
    return izq[:-1] + der


def hornear(nombre, a, pose_autor, muestrear, apoyos_fn=None, sin_fisica=()):
    """Devuelve los canales nuevos [(pieza, tipo, ks)] y las piezas que sustituyen."""
    dur = a['dur']
    loop = a['loop']
    vueltas = 3 if loop else 1
    n = int(round(dur * HZ * vueltas))
    dt = 1.0 / HZ
    paso_horneo = 0.05 if dur <= 1.5 else 0.1
    G = np.array([0.0, 1.0, 0.0])       # la gravedad, hacia +Y del modelo

    # estado de la simulacion
    sim = {}
    ret = {}
    registro = {}                       # (pieza) -> lista de (t, rot offset)

    for paso in range(n + 1):
        t_abs = paso * dt
        s = t_abs % dur if loop else min(t_abs, dur)
        pose = pose_autor(nombre, s)

        # --- 1. piernas por cinematica inversa ---
        Ms = nj.matrices(pose)
        apo = apoyos_fn(s) if apoyos_fn else apoyos_autor(a, s, muestrear)
        for lado in ('izq', 'der'):
            obj, pie_g, giro = apo[lado]
            (mx, my, mz), rod, pie = ik_pierna(Ms['pelvis'], lado, obj, pie_g, giro)
            pose['pierna_' + lado] = {**pose.get('pierna_' + lado, {}),
                                      'rot': (mx - REPOSO_PIERNA, my, mz)}
            pose['espinilla_' + lado] = {**pose.get('espinilla_' + lado, {}), 'rot': (rod - REPOSO_ESPINILLA, 0, 0)}
            pose['pie_' + lado] = {**pose.get('pie_' + lado, {}), 'rot': (pie - REPOSO_PIE, 0, 0)}

        # --- 2. retraso con muelle sobre los offsets de rotacion ---
        for pieza, (hz, zeta) in RETRASADAS.items():
            objetivo = np.array(pose.get(pieza, {}).get('rot', (0, 0, 0)), float)
            if pieza not in ret:
                ret[pieza] = [objetivo.copy(), np.zeros(3)]
            x, v = ret[pieza]
            w = 2 * math.pi * hz
            acc = w * w * (objetivo - x) - 2 * zeta * w * v
            v = v + acc * dt
            x = x + v * dt
            ret[pieza] = [x, v]
            pose[pieza] = {**pose.get(pieza, {}), 'rot': tuple(x)}

        # --- 3. masas con inercia (en el espacio del modelo) ---
        Ms = nj.matrices(pose)
        for pieza, (punta, modo, par) in SIMULADAS.items():
            if pieza in sin_fisica:
                continue
            p = nj.PARTES[pieza]
            Mpadre = Ms[p.padre]
            reposo_rot = p.rot
            M_rep = Mpadre @ nj.T(*p.pivote) @ nj.Rz(reposo_rot[2] * D2R) @ nj.Ry(reposo_rot[1] * D2R) @ nj.Rx(reposo_rot[0] * D2R)
            pivote = (Mpadre @ np.array([*p.pivote, 1.0]))[:3]
            # Lo que la pose de autor pide para esta pieza (si pide algo), como reposo.
            extra = pose.get(pieza, {}).get('rot', (0, 0, 0))
            M_obj = Mpadre @ nj.T(*p.pivote) @ nj.Rz((reposo_rot[2] + extra[2]) * D2R) @ \
                nj.Ry((reposo_rot[1] + extra[1]) * D2R) @ nj.Rx((reposo_rot[0] + extra[0]) * D2R)
            objetivo = (M_obj @ np.array([*punta, 1.0]))[:3]
            L = float(np.linalg.norm(punta))
            if pieza not in sim:
                sim[pieza] = [objetivo.copy(), objetivo.copy()]
            E, E_ant = sim[pieza]
            sub = 4
            h = dt / sub
            for _ in range(sub):
                acc = par['g'] * G + par['k'] * (objetivo - E)
                vel = (E - E_ant) * math.exp(-par['roce'] * h)
                E_nuevo = E + vel + acc * h * h
                dirv = E_nuevo - pivote
                E_nuevo = pivote + dirv / (np.linalg.norm(dirv) + 1e-9) * L
                E_ant, E = E, E_nuevo
            sim[pieza] = [E, E_ant]
            # de la direccion en el mundo a los angulos de la pieza
            Rp = Mpadre[:3, :3]
            Rp = Rp / np.linalg.norm(Rp, axis=0)
            d_local = Rp.T @ (E - pivote)
            if punta[1] < 0:
                d_local = -d_local
            x, z = _dir_xz(d_local)
            off = (_envolver(x - reposo_rot[0]), 0.0, _envolver(z - reposo_rot[2]))
            pose[pieza] = {**pose.get(pieza, {}), 'rot': off}

        # --- registrar (solo la ultima vuelta en los bucles) ---
        if t_abs >= dur * (vueltas - 1) - 1e-9:
            tt = round(t_abs - dur * (vueltas - 1), 4)
            for pieza in PIERNAS + list(RETRASADAS) + [q for q in SIMULADAS if q not in sin_fisica]:
                registro.setdefault(pieza, []).append((tt, tuple(pose[pieza]['rot'])))

    # --- hornear a keyframes ---
    canales = []
    for pieza, serie in registro.items():
        muestras = []
        siguiente = 0.0
        for tt, v in serie:
            if tt + 1e-6 >= siguiente or tt >= dur - 1e-6:
                muestras.append((round(tt, 3), tuple(round(c, 2) for c in v)))
                siguiente = tt + paso_horneo - 1e-6
        if muestras[-1][0] < dur - 1e-6:
            muestras.append((dur, muestras[-1][1]))
        if loop:
            muestras[-1] = (muestras[-1][0], muestras[0][1])
        ks = [(t, v, 'c') for t, v in simplificar(muestras)]
        # quita los canales que apenas se mueven
        mayor = max(max(abs(c) for c in v) for _, v, _ in ks)
        if mayor < 0.25:
            continue
        canales.append((pieza, 'rot', ks))
    sustituye = set(PIERNAS) | set(RETRASADAS) | (set(SIMULADAS) - set(sin_fisica))
    return canales, sustituye

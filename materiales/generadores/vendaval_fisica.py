"""
Pase de fisica de las animaciones de la Mariposa del Vendaval.

Las poses (vendaval_juego_anim.py) dicen lo que HACE: la batida, el giro del
cuerpo. Aqui se calcula lo que su cuerpo no puede dejar de hacer:

  RETRASO   la cabeza, las antenas, los segmentos del abdomen, las patas y
            las alas de abajo siguen a lo que las lleva con un muelle amortiguado: un poco
            tarde y con un leve rebote. Las alas de abajo van asi un pelo por
            detras de las de arriba, como en una mariposa de verdad.
  INERCIA   las cintas de viento del abdomen cuelgan como pendulos con
            gravedad y rozamiento de aire: se quedan atras al subir, se pasan
            de largo y se asientan.

Se simula a 80 Hz y se hornea en keyframes de vanilla. Las animaciones en
bucle se simulan tres vueltas y se guarda la ultima, para que empalmen.
"""
import math
import numpy as np
import vendaval_juego as vj

D2R = math.pi / 180
R2D = 180 / math.pi
HZ = 80

RETRASADAS = {
    'cabeza': (3.0, 0.55),
    'antena_izq': (2.0, 0.32), 'antena_der': (2.0, 0.32),
    'antena_punta_izq': (2.8, 0.28), 'antena_punta_der': (2.8, 0.28),
    'abdomen': (2.6, 0.5), 'abdomen2': (2.4, 0.45), 'abdomen3': (2.4, 0.42), 'abdomen4': (2.6, 0.4), 'punta': (3.0, 0.4),
    'ala_inf_izq': (4.2, 0.5), 'ala_inf_der': (4.2, 0.5),
    'colmillo_izq': (5.0, 0.5), 'colmillo_der': (5.0, 0.5),
    # Las patas cuelgan: siguen al cuerpo blandas, con un poco de rebote.
    **{f'pata{i}_{n}': (2.4, 0.45) for i in range(3) for n in ('izq', 'der')},
    **{f'pata{i}_{n}_tibia': (2.8, 0.4) for i in range(3) for n in ('izq', 'der')},
}
SIMULADAS = {
    'cinta_izq': ((0, 96.0, 0), dict(g=60.0, roce=2.6, k=6.0)),
    'cinta_der': ((0, 84.0, 0), dict(g=60.0, roce=2.6, k=6.0)),
}


def _envolver(x):
    return (x + 180.0) % 360.0 - 180.0


def _dir_xz(t):
    t = t / (np.linalg.norm(t) + 1e-12)
    x = math.asin(max(-1.0, min(1.0, t[2])))
    z = math.atan2(-t[0], t[1])
    return x * R2D, z * R2D


def simplificar(puntos, tol=0.35):
    """Ramer-Douglas-Peucker sobre (t, (x, y, z))."""
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


def hornear(nombre, a, pose_autor, sin_fisica=()):
    """Devuelve los canales nuevos [(pieza, tipo, ks)] y las piezas que sustituyen."""
    dur = a['dur']
    loop = a['loop']
    vueltas = 3 if loop else 1
    n = int(round(dur * HZ * vueltas))
    dt = 1.0 / HZ
    paso_horneo = 0.05 if dur <= 2.0 else 0.1
    G = np.array([0.0, 1.0, 0.0])
    ret, sim, registro = {}, {}, {}
    for paso in range(n + 1):
        t_abs = paso * dt
        s = t_abs % dur if loop else min(t_abs, dur)
        pose = pose_autor(nombre, s)
        for pieza, (hz, zeta) in RETRASADAS.items():
            if pieza in sin_fisica:
                continue
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
        Ms = vj.matrices(pose)
        for pieza, (punta, par) in SIMULADAS.items():
            if pieza in sin_fisica:
                continue
            p = vj.PARTES[pieza]
            Mpadre = Ms[p.padre]
            rr = p.rot
            extra = pose.get(pieza, {}).get('rot', (0, 0, 0))
            M_obj = Mpadre @ vj.T(*p.pivote) @ vj.Rz((rr[2] + extra[2]) * D2R) @ vj.Ry((rr[1] + extra[1]) * D2R) @ \
                vj.Rx((rr[0] + extra[0]) * D2R)
            pivote = (Mpadre @ np.array([*p.pivote, 1.0]))[:3]
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
            Rp = Mpadre[:3, :3]
            Rp = Rp / np.linalg.norm(Rp, axis=0)
            d_local = Rp.T @ (E - pivote)
            x, z = _dir_xz(d_local)
            off = (_envolver(x - rr[0]), extra[1], _envolver(z - rr[2]))
            pose[pieza] = {**pose.get(pieza, {}), 'rot': off}
        if t_abs >= dur * (vueltas - 1) - 1e-9:
            tt = round(t_abs - dur * (vueltas - 1), 4)
            for pieza in [q for q in RETRASADAS if q not in sin_fisica] + [q for q in SIMULADAS if q not in sin_fisica]:
                registro.setdefault(pieza, []).append((tt, tuple(pose[pieza]['rot'])))
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
        mayor = max(max(abs(c) for c in v) for _, v, _ in ks)
        if mayor < 0.25:
            continue
        canales.append((pieza, 'rot', ks))
    sustituye = (set(RETRASADAS) | set(SIMULADAS)) - set(sin_fisica)
    return canales, sustituye

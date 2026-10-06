"""
Pase de fisica de las animaciones de Novilis (como nerea_fisica.py, adaptado a
su cuerpo de 16 bloques).

Las poses de novilis_juego_anim.py dicen lo que HACE el caballero: el brazo que
sube, el torso que gira, la pelvis que baja. Aqui se calcula lo que un cuerpo
asi no puede dejar de hacer:

  PIES PLANTADOS   las piernas salen de cinematica inversa (dos huesos: muslo
                   de 30 px, espinilla de 34 hasta la suela). Cada pie tiene su
                   punto de apoyo en el suelo y la pierna se dobla lo que haga
                   falta cuando la pelvis baja, gira o se inclina: nada de pies
                   que patinan, flotan o se hunden, ni rodillas al reves.
  INERCIA          la capa (tres tramos), el tabardo y las escarcelas son masas
                   con gravedad, muelle y rozamiento: se quedan atras al arrancar
                   un tajo, se pasan de largo al frenar y se asientan.
  RETRASO          cuello, cabeza y torso siguen a lo que los lleva con un muelle
                   amortiguado: la pelvis manda, el torso llega un pelo despues
                   y la cabeza despues (la cadena de un golpe de verdad).

Se simula a 60 Hz y se hornea en keyframes de vanilla (en el juego no cuesta
nada). Las animaciones en bucle se simulan tres vueltas y se guarda la ultima,
para que empalmen sin salto.
"""
import math
import numpy as np
import novilis_juego as nj

D2R = math.pi / 180
R2D = 180 / math.pi
HZ = 60
L_MUSLO = 30.0
L_ESPINILLA = 34.0
CADERA_X = 8.5
CADERA_Y = 2.0
SUELO = 24.0

# --- piezas con inercia ---
# Cada una es un muelle angular en el MUNDO: la direccion de la pieza (de su
# pivote a su punta) persigue un objetivo, que es la pose de autor tirada hacia
# abajo por la gravedad (peso g, de 0 a 1). Como el objetivo se mueve con el
# cuerpo y la pieza llega tarde, se queda atras al arrancar, se pasa al frenar y
# se asienta (hz: lo rapido que responde; zeta: lo que frena el rebote). Los
# limites (grados sobre su reposo) la mantienen fuera del cuerpo, y nunca baja
# del suelo. Antes eran pendulos encadenados y la capa se volvia loca.
SIMULADAS = {
    'capa_1': dict(g=0.55, hz=1.7, zeta=0.5, x=(-3, 80), z=(-18, 18)),
    'capa_2': dict(g=0.55, hz=1.9, zeta=0.45, x=(-10, 70), z=(-14, 14)),
    'capa_3': dict(g=0.55, hz=2.1, zeta=0.42, x=(-14, 70), z=(-14, 14)),
    'tabardo': dict(g=0.5, hz=2.0, zeta=0.5, x=(-85, 8), z=(-12, 12)),
    'falda_izq': dict(g=0.0, hz=4.5, zeta=0.45, x=(-25, 25), z=(-14, 14)),
    'falda_der': dict(g=0.0, hz=4.5, zeta=0.45, x=(-25, 25), z=(-14, 14)),
    'falda_lizq': dict(g=0.0, hz=4.5, zeta=0.45, x=(-14, 14), z=(-25, 25)),
    'falda_lder': dict(g=0.0, hz=4.5, zeta=0.45, x=(-14, 14), z=(-25, 25)),
}
# lo que mide cada una (px), para no meterla en el suelo
LARGO = {'capa_1': 32.0, 'capa_2': 32.0, 'capa_3': 28.0, 'tabardo': 50.0}

# --- piezas con retraso: (frecuencia en Hz, amortiguamiento) ---
# El torso lleva los dos brazos (y la espada): un muelle rapido y casi critico,
# para que siga a la pelvis sin bailar.
RETRASADAS = {
    'torso': (6.5, 0.8),
    'cuello': (4.0, 0.62),
    'cabeza': (3.4, 0.58),
}

PIERNAS = [p + '_' + l for l in ('izq', 'der') for p in ('pierna', 'espinilla', 'pie')]


def reposo_pie(lado):
    s = 1 if lado == 'izq' else -1
    return (CADERA_X * s, SUELO, 0.0)


# ----------------------------------------------------------------------
#  Cinematica inversa de una pierna
# ----------------------------------------------------------------------
def ik_pierna(M_pelvis, lado, objetivo, pie_grados=0.0, giro=0.0):
    """Angulos (pierna xyz, espinilla x, pie x) en grados para que la suela (el
    pivote del pie) caiga en 'objetivo' (px de modelo, Y abajo, frente -Z).

    giro: rotacion Y de la pierna (hacia donde apunta el pie).
    pie_grados: inclinacion del pie respecto al suelo (0 = plano; negativo, la
    punta abajo).
    Las piernas de Novilis descansan rectas (0, 0, 0): los angulos son offsets.
    """
    s = 1 if lado == 'izq' else -1
    inv = np.linalg.inv(M_pelvis)
    T = (inv @ np.array([*objetivo, 1.0]))[:3]
    H = np.array([CADERA_X * s, CADERA_Y, 0.0])
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
    pelvis_x = math.atan2(M_pelvis[2, 1], M_pelvis[1, 1])
    pie = pie_grados * D2R - (pelvis_x + muslo + rodilla)
    return (muslo * R2D, giro, rz * R2D), rodilla * R2D, pie * R2D


def apoyo_fk(pose, lado):
    """Donde deja el pie la pose tal cual (cinematica directa): (punto, inclinacion, giro)."""
    Ms = nj.matrices(pose)
    M = Ms['pie_' + lado]
    p = (M @ np.array([0, 0, 0, 1.0]))[:3]
    # la inclinacion: la suma de los giros X de la cadena (la pelvis incluida)
    pel = Ms['pelvis']
    pelvis_x = math.atan2(pel[2, 1], pel[1, 1]) * R2D
    x = pelvis_x
    for k in ('pierna_', 'espinilla_', 'pie_'):
        x += pose.get(k + lado, {}).get('rot', (0, 0, 0))[0] + nj.PARTES[k + lado].rot[0]
    giro = pose.get('pierna_' + lado, {}).get('rot', (0, 0, 0))[1]
    return tuple(float(v) for v in p), float(x), float(giro)


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


def simplificar(puntos, tol):
    """Ramer-Douglas-Peucker sobre (t, (x, y, z)): quita los keyframes que la
    interpolacion LINEAL entre sus vecinos ya reproduce con menos de 'tol'."""
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


def hornear(dur, loop, pose_autor, apoyos, sin_fisica=(), sin_retraso=(), paso=0.05):
    """pose_autor(s) -> pose del juego (offsets); apoyos(s) -> {lado: (punto, pie, giro)}.

    Devuelve {(pieza, tipo): [(t, (x, y, z)), ...]} con TODOS los canales de la
    pose final muestreados cada 'paso' segundos (aun sin simplificar).
    """
    vueltas = 3 if loop else 1
    n = int(round(dur * HZ * vueltas))
    dt = 1.0 / HZ
    G = np.array([0.0, 1.0, 0.0])       # la gravedad, hacia +Y del modelo
    sim = {}
    ret = {}
    registro = {}
    siguiente = 0.0

    for k in range(n + 1):
        t_abs = k * dt
        s = t_abs % dur if loop else min(t_abs, dur)
        if loop and k == n:
            s = dur
        pose = pose_autor(s)

        # --- 1. retraso con muelle sobre los offsets de rotacion (pelvis -> torso -> cabeza) ---
        for pieza, (hz, zeta) in RETRASADAS.items():
            if pieza in sin_retraso:
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

        # --- 2. piernas por cinematica inversa (con la pelvis ya puesta) ---
        Ms = nj.matrices(pose)
        apo = apoyos(s)
        for lado in ('izq', 'der'):
            obj, pie_g, giro = apo[lado]
            (mx, my, mz), rod, pie = ik_pierna(Ms['pelvis'], lado, obj, pie_g, giro)
            # la IK da angulos absolutos; la malla ya trae su postura de pie: offsets
            r0 = nj.PARTES['pierna_' + lado].rot
            pose['pierna_' + lado] = {**pose.get('pierna_' + lado, {}), 'rot': (mx - r0[0], my - r0[1], mz - r0[2])}
            pose['espinilla_' + lado] = {**pose.get('espinilla_' + lado, {}),
                                         'rot': (rod - nj.PARTES['espinilla_' + lado].rot[0], 0, 0)}
            pose['pie_' + lado] = {**pose.get('pie_' + lado, {}), 'rot': (pie - nj.PARTES['pie_' + lado].rot[0], 0, 0)}

        # --- 3. piezas con inercia (muelle angular en el mundo) ---
        Ms = nj.matrices(pose)
        for pieza, par in SIMULADAS.items():
            if pieza in sin_fisica:
                continue
            p = nj.PARTES[pieza]
            Mpadre = Ms[p.padre]
            Rp = Mpadre[:3, :3] / np.linalg.norm(Mpadre[:3, :3], axis=0)
            rx0, ry0, rz0 = p.rot
            extra = pose.get(pieza, {}).get('rot', (0, 0, 0))
            R_aut = nj.Rz((rz0 + extra[2]) * D2R)[:3, :3] @ nj.Ry((ry0 + extra[1]) * D2R)[:3, :3] @                 nj.Rx((rx0 + extra[0]) * D2R)[:3, :3]
            t_aut = Rp @ (R_aut @ np.array([0.0, 1.0, 0.0]))
            objetivo = (1 - par['g']) * t_aut + par['g'] * G
            objetivo = objetivo / (np.linalg.norm(objetivo) + 1e-9)
            if pieza not in sim:
                sim[pieza] = [objetivo.copy(), np.zeros(3)]
            d, v = sim[pieza]
            w = 2 * math.pi * par['hz']
            acc = w * w * (objetivo - d) - 2 * par['zeta'] * w * v
            v = v + acc * dt
            d = d + v * dt
            d = d / (np.linalg.norm(d) + 1e-9)
            v = v - (v @ d) * d
            # a angulos de la pieza, con sus limites
            x, z = _dir_xz(Rp.T @ d)
            ox = min(max(_envolver(x - rx0), par['x'][0]), par['x'][1])
            oz = min(max(_envolver(z - rz0), par['z'][0]), par['z'][1])
            # que no se meta en el suelo: la capa se levanta hacia atras, el tabardo hacia delante
            if pieza in LARGO:
                piv = (Mpadre @ np.array([*p.pivote, 1.0]))[:3]
                paso_x = -4.0 if pieza == 'tabardo' else 4.0
                for _ in range(20):
                    R = nj.Rz((rz0 + oz) * D2R)[:3, :3] @ nj.Rx((rx0 + ox) * D2R)[:3, :3]
                    punta = piv + Rp @ (R @ np.array([0.0, LARGO[pieza], 0.0]))
                    if punta[1] <= SUELO - 0.5:
                        break
                    ox += paso_x
            R = nj.Rz((rz0 + oz) * D2R)[:3, :3] @ nj.Rx((rx0 + ox) * D2R)[:3, :3]
            d_lim = Rp @ (R @ np.array([0.0, 1.0, 0.0]))
            if float(np.linalg.norm(d_lim - d)) > 1e-4:
                v = v * 0.3
            sim[pieza] = [d_lim, v]
            pose[pieza] = {**pose.get(pieza, {}), 'rot': (ox, 0.0, oz)}
            if pieza in ('capa_1', 'capa_2'):
                # el tramo siguiente cuelga de este: hay que recolocarlo
                Ms = nj.matrices(pose)

        # --- registrar (solo la ultima vuelta en los bucles) ---
        t_rel = t_abs - dur * (vueltas - 1)
        if t_rel >= -1e-9 and (t_rel + 1e-6 >= siguiente or k == n):
            tt = round(max(0.0, t_rel), 4)
            for pieza, d in pose.items():
                for tipo in ('rot', 'pos', 'esc'):
                    if tipo in d:
                        registro.setdefault((pieza, tipo), []).append((tt, tuple(float(c) for c in d[tipo])))
            siguiente = tt + paso
    # los bucles acaban donde empiezan
    if loop:
        for clave, serie in registro.items():
            if serie[-1][0] < dur - 1e-6:
                serie.append((dur, serie[0][1]))
            else:
                serie[-1] = (dur, serie[0][1])
    else:
        for clave, serie in registro.items():
            if serie[-1][0] < dur - 1e-6:
                serie.append((dur, serie[-1][1]))
    return registro

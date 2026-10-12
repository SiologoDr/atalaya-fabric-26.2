"""
Boceto de un jefe en tres tipos (12-10-2026). Juan, tras Simara: «me gustaron este
monstruo y sus variables; ahora sigue haciendo mas, ya no de este monstruo sino otro
y sus variables».

  Riscara, la Dragona de los Riscos: se planta en lo alto de un risco sobre dos patas,
  con las alas abiertas y el cuello en ese, y lanza la cabeza con las fauces abiertas
  (dientes en peine y la garganta encendida). Lo nuevo: las alas tienen los nervios de
  una libelula, y por esos nervios le corre su elemento. La misma dragona en tres tipos:

    A  de Tormenta   pizarra con escamas, nervios de rayo, cuernos como pararrayos; neon amarillo
    B  de Escarcha   escamas de escarcha, nervios de hielo, corona de carambanos; neon blanco azulado
    C  de Ponzona    escamas oscuras con manchas de veneno, nervios verdes, gorguera de
                     membrana y bulbos de esporas; neon verde

Mismo oficio que Simara (sierpe_modelo): cajas con las caras pintadas a 8 px por bloque y
texturas dibujadas, sin ruido ni motas sueltas.
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
import sierpe_modelo as sm
from bestias_modelo import cubo, viga, pua, punto, _imagen, _emis
from sierpe_modelo import _borde_de, _limpiar, _manchas, _bisel, _escamas_cara, _escudos, _degradado, lamina, bola

TAU = math.tau
D = vr.D2R
_r = bm._r
bm.PPB = 8

TIPOS = {
    'A': dict(
        clave='A', nombre='de Tormenta',
        piel=_r('0e121a', '1a222e', '2a3646', '3e5064', '5e7690'),
        vientre=_r('2a2e36', '42484f', '5e6670', '868e98', 'b4bcc4'),
        hueso=_r('1a1c22', '2e323a', '464c56', '646c78', '8a94a2'),
        ala=_r('06080e', '0c1018', '141a26', '1e2636', '2a3448'),
        diente=_r('5a5e66', '989ea8', 'cdd2da', 'e8ecf0', 'fafcff'),
        neon=('fffbe0', 'ffe03a', '6a5408'),
    ),
    'B': dict(
        clave='B', nombre='de Escarcha',
        piel=_r('3a5a78', '6a8eae', 'a2c0d8', 'd0e4f0', 'f2f8fc'),
        vientre=_r('2a4660', '4a6e8c', '7a9cb8', 'aec8dc', 'e0eef8'),
        hueso=_r('4a6680', '7e9cb6', 'b4cee0', 'dceaf4', 'f6fbff'),
        ala=_r('16304a', '25486a', '386690', '5a8ab4', '8ab4d8'),
        diente=_r('6a8098', 'a6bccc', 'd6e6f0', 'eef6fa', 'ffffff'),
        neon=('ffffff', 'b4ecff', '2a6aa0'),
    ),
    'C': dict(
        clave='C', nombre='de Ponzona',
        piel=_r('0a0c08', '141a10', '222c18', '34421e', '4c5e28'),
        vientre=_r('2a2c10', '464a1a', '666c26', '8c9434', 'b4bc4a'),
        hueso=_r('2a2418', '4a4028', '6e6040', '948664', 'bcb088'),
        ala=_r('080a06', '10140c', '1a2012', '262e1a', '344024'),
        diente=_r('6a6650', 'a6a28a', 'd2cfb8', 'ecead8', 'fbfaf0'),
        neon=('f4ffd0', '96ff2a', '2a6a06'),
    ),
}


def pintores(T):
    k = T['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'ris%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = T['neon']

    # ---------------- la piel ----------------
    if k == 'C':
        def cuerpo(tw, th, cara, s):
            """Escamas oscuras con manchas de veneno grandes y limpias, que brillan un poco."""
            idx = _escamas_cara(tw, th, cara)
            tex = _imagen(idx, T['piel'])
            m = _manchas(tw, th, s, celda=7.0, umbral=0.66, alto=0.84)
            mancha = m >= 3
            if mancha.any():
                verde = np.array(nm._hex(neo))
                tex[mancha, :3] = (tex[mancha, :3] * 0.35 + verde * 0.65).astype(np.uint8)
                centro = m == 4
                tex[centro, :3] = (np.array(nm._hex(nuc)) * 0.5 + verde * 0.5).astype(np.uint8)
                tex[m == 1, :3] = (tex[m == 1, :3] * 0.6).astype(np.uint8)
                return tex, _emis(tex, mancha, 90)
            return tex, None
    else:
        def cuerpo(tw, th, cara, s):
            return _imagen(_escamas_cara(tw, th, cara), T['piel']), None
    reg('cuerpo', cuerpo)

    def vientre(tw, th, cara, s):
        return _imagen(_escudos(tw, th), T['vientre']), None
    reg('vientre', vientre)

    def hueso(tw, th, cara, s):
        idx = np.full((th, tw), 2)
        if cara in ('der', 'izq', 'frente', 'atras') and tw >= 4:
            idx[:, 1] = 3
        return _imagen(_bisel(idx), T['hueso']), None
    reg('hueso', hueso)

    def diente(tw, th, cara, s):
        idx = np.full((th, tw), 3)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 2
        if th >= 3:
            idx[-1, :] = 2
        return _imagen(idx, T['diente']), None
    reg('diente', diente)

    def fauces(tw, th, cara, s):
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def nucleo(tw, th, cara, s):
        """El fondo de la garganta: anillos limpios del elemento, blanco en el centro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        dentro = r < 1.0
        anillo = (np.floor(r * 5) % 2) == 0
        col = np.where(anillo[..., None], np.array(c_m), np.array(qm._mezcla(c_h, c_m, 0.4)))
        col = np.where((r < 0.3)[..., None], np.array(c_n), col)
        col = np.where(((r > 0.88) & dentro)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = np.where(dentro, 255, 0)
        return t, _emis(t, dentro & (r < 0.88), 240)
    reg('nucleo', nucleo)

    def ojo(tw, th, cara, s):
        t = qm._emisivo(nuc, neo, max(2, tw), max(2, th))
        th2, tw2 = t.shape[:2]
        if tw2 >= 3:
            t[:, tw2 // 2] = (*nm._hex(hon), 255)
        return t, None
    reg('ojo', ojo, pleno=True)

    def luz(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('luz', luz, pleno=True)

    def fosa(tw, th, cara, s):
        return _imagen(np.zeros((th, tw), int), T['piel']), None
    reg('fosa', fosa)

    def _membrana(tw, th, s, libre):
        """El ala: membrana oscura en bandas (la raiz abajo, el borde arriba) con tres nervios
        largos un poco mas claros. Si el borde es libre, va en festones y encendido con el neon,
        y lleva los pocos acentos del tipo: rayos, estrellas de escarcha o pustulas."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw]
        u = (xs + 0.5) / tw
        v = 1 - (ys + 0.5) / th
        idx = np.where(v < 0.35, 1, np.where(v < 0.75, 2, 3))
        venas = np.zeros((th, tw), bool)
        for j in range(1, 4):
            x0 = j * tw / 4 + 1.2 * np.sin(v * 4 + j * 1.3)
            venas |= np.abs(xs - x0) < 0.55
        idx = np.where(venas, np.minimum(idx + 1, 4), idx)
        img = _imagen(idx, T['ala'])
        borde = (th - 1) * (0.05 + 0.2 * np.sin(np.pi * u)) if libre else np.zeros_like(u)
        fuera = ys < borde
        brillo = np.zeros((th, tw), bool)
        if libre:
            filo = (~fuera) & (ys < borde + 2.0)
            img[filo] = (*nm._hex(neo), 255)
            brillo |= filo
            rng = random.Random(s)
            if k == 'A':                                  # dos rayos en zigzag desde la raiz
                for _ in range(2):
                    x = rng.uniform(0.25, 0.75) * tw
                    y = th - 2.0
                    while y > borde.mean() + 3:
                        y2 = y - rng.uniform(2.5, 4.5)
                        x2 = min(tw - 2, max(1, x + rng.choice((-1, 1)) * rng.uniform(1.5, 3.0)))
                        n = int(max(abs(x2 - x), abs(y2 - y))) + 1
                        for q in range(n + 1):
                            xx, yy = int(round(x + (x2 - x) * q / n)), int(round(y + (y2 - y) * q / n))
                            if 0 <= xx < tw and 0 <= yy < th and not fuera[yy, xx]:
                                img[yy, xx] = (*nm._hex(nuc), 255)
                                brillo[yy, xx] = True
                        x, y = x2, y2
            elif k == 'B':                                # estrellas de escarcha cerca del borde
                for _ in range(max(2, tw // 8)):
                    cx = int(rng.uniform(0.15, 0.85) * tw)
                    cy = int(borde[0, min(tw - 1, cx)] + rng.uniform(3, 7))
                    for (dx, dy) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
                        xx, yy = cx + dx, cy + dy
                        if 0 <= xx < tw and 0 <= yy < th and not fuera[yy, xx]:
                            img[yy, xx] = (*nm._hex(nuc), 255) if (dx, dy) == (0, 0) else (*T['ala'][4], 255)
                            brillo[yy, xx] = (dx, dy) == (0, 0)
            else:                                         # pustulas que brillan
                for _ in range(max(2, tw // 9)):
                    cx, cy = rng.uniform(0.15, 0.85) * tw, rng.uniform(0.3, 0.8) * th
                    rr = rng.uniform(1.2, 2.2)
                    m = (np.hypot(xs - cx, ys - cy) < rr) & ~fuera
                    img[m] = (*nm._hex(neo), 255)
                    img[m & (np.hypot(xs - cx + 0.6, ys - cy + 0.6) < rr * 0.45)] = (*nm._hex(nuc), 255)
                    brillo |= m
        t[~fuera] = img[~fuera]
        return t, _emis(t, brillo & ~fuera, 215)

    def membrana(tw, th, cara, s):
        return _membrana(tw, th, s, True)
    reg('membrana', membrana)

    def membrana_lisa(tw, th, cara, s):
        return _membrana(tw, th, s, False)
    reg('membrana_lisa', membrana_lisa)

    # ---------------- lo propio de cada tipo ----------------
    if k == 'B':
        def hielo(tw, th, cara, s):
            idx = np.full((th, tw), 3)
            ys, xs = np.mgrid[0:th, 0:tw]
            idx = np.where(((xs - ys) % 6) == 0, 4, idx)
            idx = np.where(((xs + 2 * ys) % 9) == 0, 2, idx)
            return _imagen(_bisel(idx), T['hueso']), None
        reg('hielo', hielo)
    if k == 'C':
        def bulbo(tw, th, cara, s):
            return qm._emisivo('f4ffd0', '7aee1a', max(2, tw), max(2, th), oscuro='2a5a06', semilla=s % 5), None
        reg('bulbo', bulbo, pleno=True)
    return P


# ----------------------------------------------------------------------
#  Ayudas de forma
# ----------------------------------------------------------------------
def bloque(out, M, w, h, d, pintor, caras=None, semilla=0, redondeo=0.78):
    """Una caja centrada con las esquinas comidas por otra mas estrecha y mas alta (se lee redonda)."""
    cubo(out, M, -w / 2, -h / 2, -d / 2, w, h, d, pintor, caras, semilla)
    cubo(out, M, -w * redondeo / 2, -h / 2 - h * (1 - redondeo) / 4, -d / 2 + 0.02, w * redondeo, h * (1 + (1 - redondeo) / 2), d - 0.04,
         pintor, caras, semilla + 1)


def cuello(out, ctrl, radios, P, n=9, semilla=0, espinas=None):
    """Una cadena de tramos cuadrados que siguen una curva (el lomo siempre arriba)."""
    pts, _ = em.catmull(ctrl, n + 1)
    pts = [np.asarray(p, float) for p in pts]
    marcos = sm._marcos(pts, (0, 1, 0))
    for i, M in enumerate(marcos):
        k = i / max(len(marcos) - 1, 1)
        r = radios[0] + (radios[1] - radios[0]) * k
        L = float(np.linalg.norm(pts[i + 1] - pts[i]))
        cubo(out, M, -r, -r, -0.1, 2 * r, 2 * r, L + 0.2, P['cuerpo'], semilla=semilla + i)
        cubo(out, M, -r * 0.55, -r - 0.12, -0.1, r * 1.1, 0.26, L + 0.2, P['vientre'], semilla=semilla + i)
        if espinas:
            espinas(out, M, r, L, k, i)
    return pts, marcos


# ======================================================================
#  RISCARA
# ======================================================================
def riscara(tipo='A', abre=40.0, semilla=1):
    T = TIPOS[tipo]
    P = pintores(T)
    k = T['clave']
    rng = random.Random(semilla)
    out = []

    def espina_lomo(out_, M, r, L, t, i):
        h = 0.5 + 0.5 * math.sin(math.pi * min(1.0, t + 0.15))
        Mt = M @ vr.T(0, r - 0.1, L * 0.4) @ vr.Rx(-35 * D)
        if k == 'B':
            bm.cristal(out_, Mt, 0.2, h * 1.6, P['hielo'], semilla=i)
        elif k == 'C':
            pua(out_, Mt, 0.16, h * 1.2, P['hueso'], semilla=i)
            if i % 2 == 0:
                bola(out_, M @ vr.T(0, r + 0.1, L * 0.8), 0.22, P['bulbo'], semilla=i)
        else:
            pua(out_, Mt, 0.18, h * 1.4, P['hueso'], semilla=i)
            cubo(out_, Mt @ vr.T(0, h * 1.4 - 0.05, 0), -0.06, 0, -0.06, 0.12, 0.25, 0.12, P['luz'], semilla=i)

    # el cuerpo: pecho alzado, vientre y caderas
    Mpe = vr.T(0, 7.7, 0.6) @ vr.Rx(-28 * D)
    bloque(out, Mpe, 4.8, 4.0, 3.8, P['cuerpo'], semilla=1)
    cubo(out, Mpe, -1.25, -2.1, 1.75, 2.5, 4.0, 0.32, P['vientre'], semilla=2)
    Mvi = vr.T(0, 6.3, -1.7) @ vr.Rx(-12 * D)
    bloque(out, Mvi, 4.1, 3.4, 3.3, P['cuerpo'], semilla=3)
    cubo(out, Mvi, -1.1, -1.98, -1.6, 2.2, 0.3, 3.2, P['vientre'], semilla=4)
    bloque(out, vr.T(0, 5.7, -3.7) @ vr.Rx(8 * D), 3.4, 3.0, 2.8, P['cuerpo'], semilla=5)
    for j, (y, z) in enumerate(((9.5, 0.4), (8.6, -1.2), (7.6, -2.6), (7.0, -3.9))):
        espina_lomo(out, vr.T(0, y - 1.0, z) @ vr.Rx(-10 * D), 1.0, 1.0, j / 4, j)

    # las patas: muslo, espinilla, pie de tres dedos con sus garras
    for s in (1, -1):
        cad, rod, tob = np.array((s * 1.7, 5.4, -2.0)), np.array((s * 2.4, 3.2, 0.2)), np.array((s * 2.2, 1.2, -1.2))
        viga(out, cad, rod, 1.5, 1.6, P['cuerpo'], extra=0.3, semilla=6)
        viga(out, rod, tob, 1.0, 1.0, P['cuerpo'], extra=0.2, semilla=7)
        viga(out, tob, tob + np.array((0, -1.0, 0.3)), 0.8, 0.8, P['cuerpo'], semilla=8)
        pie = tob + np.array((0, -1.1, 0.4))
        for j, dx in enumerate((-0.5, 0.0, 0.5)):
            p1 = pie + np.array((dx, 0.0, 1.2))
            viga(out, pie, p1, 0.36, 0.3, P['cuerpo'], semilla=9)
            viga(out, p1, p1 + np.array((dx * 0.2, -0.25, 0.55)), 0.24, 0.24, P['hueso'], semilla=10)
        viga(out, pie, pie + np.array((0, 0.1, -0.9)), 0.3, 0.3, P['hueso'], semilla=11)

    # la cola, larga, que se curva atras y acaba en su punta
    ctrl = [(0, 5.4, -4.4), (0.6, 4.0, -7.0), (2.6, 2.6, -9.4), (5.6, 1.8, -10.8), (8.8, 2.4, -11.0), (11.0, 3.6, -10.0)]
    pts, marcos = cuello(out, ctrl, (1.1, 0.35), P, n=12, semilla=12, espinas=espina_lomo)
    Mfin = marcos[-1] @ vr.T(0, 0, float(np.linalg.norm(pts[-1] - pts[-2])))
    if k == 'A':
        for j in range(3):
            pua(out, Mfin @ vr.Rz((j * 120) * D) @ vr.Rx(-60 * D), 0.16, 1.4, P['hueso'], semilla=j)
        cubo(out, Mfin, -0.2, -0.2, 0, 0.4, 0.4, 1.4, P['hueso'], semilla=3)
        cubo(out, Mfin @ vr.T(0, 0, 1.3), -0.12, -0.12, 0, 0.24, 0.24, 0.5, P['luz'], semilla=4)
    elif k == 'B':
        for j in range(4):
            bm.cristal(out, Mfin @ vr.Rz((j * 90 + 45) * D) @ vr.Rx(-55 * D), 0.22, 1.6, P['hielo'], semilla=j)
    else:
        bola(out, Mfin @ vr.T(0, 0, 0.5), 0.6, P['bulbo'], semilla=5)
        pua(out, Mfin @ vr.T(0, 0, 0.9) @ vr.Rx(90 * D), 0.16, 1.0, P['hueso'], semilla=6)

    # el cuello en ese y la cabeza que se lanza hacia delante
    ctrl = [(0, 8.6, 1.4), (0, 10.4, 2.6), (0, 12.4, 2.8), (0, 14.0, 3.6), (0, 14.6, 5.0)]
    pts, marcos = cuello(out, ctrl, (1.35, 0.95), P, n=8, semilla=20, espinas=espina_lomo)
    Mh = em.marco(pts[-1] + np.array((0, 0.0, 1.2)), (0, -0.2, 1.0)) @ np.diag([1.2, 1.2, 1.2, 1.0])
    cabeza(out, Mh, T, P, abre)

    # las alas: brazo, antebrazo y cuatro dedos con la membrana entre ellos
    for s in (1, -1):
        hom = np.array((s * 1.8, 8.6, 0.8))
        codo = np.array((s * 5.4, 13.0, -0.6))
        mun = np.array((s * 9.0, 15.0, -1.6))
        viga(out, hom, codo, 0.85, 0.85, P['cuerpo'], extra=0.25, semilla=30)
        viga(out, codo, mun, 0.6, 0.6, P['hueso'], extra=0.2, semilla=31)
        bola(out, vr.T(*codo), 0.55, P['cuerpo'], semilla=32)
        pua(out, vr.T(*mun) @ vr.Rz(s * 20 * D), 0.18, 1.1, P['hueso'], semilla=33)          # el pulgar
        puntas = [np.array((s * 10.6, 21.4, -3.0)), np.array((s * 15.4, 19.0, -3.4)), np.array((s * 17.6, 13.6, -3.0)),
                  np.array((s * 15.2, 8.0, -2.4))]
        for j, tp in enumerate(puntas):
            viga(out, mun, tp, 0.3 - j * 0.03, 0.3 - j * 0.03, P['hueso'], semilla=34 + j)
        flanco = np.array((s * 2.2, 5.6, -2.6))

        def pano(raiz, a, b, pintor, semilla):
            lamina(out, (raiz, raiz, b, a), pintor, float(np.linalg.norm(b - a)), float(np.linalg.norm((a + b) / 2 - raiz)), semilla)

        pano(mun, codo, puntas[0], P['membrana_lisa'], 40)                 # el borde de ataque, junto al brazo
        for j in range(3):
            pano(mun, puntas[j], puntas[j + 1], P['membrana'], 41 + j)     # el abanico entre los dedos
        pano(mun, puntas[3], flanco, P['membrana'], 44)                    # del ultimo dedo al costado
        pano(mun, flanco, codo, P['membrana_lisa'], 45)                    # lo de dentro, hasta el cuerpo
        pano(codo, flanco, hom, P['membrana_lisa'], 46)
    return out, {'cabeza': Mh}


def cabeza(out, Mh, T, P, abre):
    """La cabeza de la dragona (en su marco): craneo, hocico, fauces y adornos del tipo."""
    k = T['clave']
    cubo(out, Mh, -1.5, -0.8, -1.8, 3.0, 2.2, 3.2, P['cuerpo'], caras={'abajo': P['vientre']}, semilla=1)
    cubo(out, Mh @ vr.T(0, 1.05, -0.4) @ vr.Rx(8 * D), -1.62, 0, 0, 3.24, 0.5, 2.2, P['hueso'], semilla=2)       # la ceja
    cubo(out, Mh, -1.2, -0.7, 1.3, 2.4, 1.6, 1.9, P['cuerpo'], caras={'abajo': P['fauces']}, semilla=3)
    Ms2 = Mh @ vr.T(0, 0, 3.1) @ vr.Rx(5 * D)
    cubo(out, Ms2, -0.9, -0.65, 0, 1.8, 1.3, 1.9, P['cuerpo'], caras={'abajo': P['fauces']}, semilla=4)
    cubo(out, Ms2, -0.3, 0.6, 0.2, 0.6, 0.3, 1.5, P['hueso'], semilla=5)                                        # cresta del hocico
    for s in (1, -1):
        cubo(out, Ms2, s * 0.45 - 0.15, 0.4, 1.85, 0.3, 0.18, 0.08, P['fosa'], semilla=6)
        x0 = 1.5 if s > 0 else -1.56
        cubo(out, Mh, x0, 0.4, 0.5, 0.06, 0.38, 0.7, P['ojo'], semilla=7)
    # los dientes de arriba, en peine, y los colmillos
    for s in (1, -1):
        for j in range(5):
            pua(out, Mh @ vr.T(s * 1.05, -0.7, 1.5 + j * 0.36) @ vr.Rx(180 * D), 0.09, 0.85 + 0.25 * (j % 2), P['diente'], semilla=8 + j)
        for j in range(5):
            pua(out, Ms2 @ vr.T(s * 0.75, -0.65, 0.2 + j * 0.36) @ vr.Rx(180 * D), 0.09, 0.8 + 0.2 * (j % 2), P['diente'], semilla=13 + j)
    for j in range(5):
        x = -0.6 + j * 0.3
        largo = 1.6 if j in (0, 4) else 0.9
        pua(out, Ms2 @ vr.T(x, -0.65, 1.75) @ vr.Rx(180 * D), 0.12 if j in (0, 4) else 0.09, largo, P['diente'], semilla=18 + j)
    # la mandibula, abierta
    Mj = Mh @ vr.T(0, -0.8, -1.3) @ vr.Rx(abre * D)
    cubo(out, Mj, -1.3, -0.85, 0, 2.6, 0.85, 3.4, P['cuerpo'], caras={'arriba': P['fauces'], 'abajo': P['vientre']}, semilla=23)
    Mj2 = Mj @ vr.T(0, 0, 3.35) @ vr.Rx(-8 * D)
    cubo(out, Mj2, -0.95, -0.75, 0, 1.9, 0.75, 2.6, P['cuerpo'], caras={'arriba': P['fauces'], 'abajo': P['vientre']}, semilla=24)
    for s in (1, -1):
        for j in range(7):
            pua(out, Mj @ vr.T(s * 1.15, 0, 0.55 + j * 0.4), 0.09, 0.75 + 0.2 * (j % 2), P['diente'], semilla=25 + j)
        for j in range(5):
            pua(out, Mj2 @ vr.T(s * 0.8, 0, 0.3 + j * 0.42), 0.09, 0.7 + 0.18 * (j % 2), P['diente'], semilla=32 + j)
    for j in range(4):
        x = -0.55 + j * 0.37
        pua(out, Mj2 @ vr.T(x, 0, 2.45), 0.12 if j in (0, 3) else 0.09, 1.3 if j in (0, 3) else 0.8, P['diente'], semilla=37 + j)
    # al fondo de la garganta, el nucleo del elemento
    Mv = Mh @ vr.T(0, -1.25, 0.8) @ vr.Rx(abre * 0.5 * D)
    cubo(out, Mv, -0.95, -0.95, 0, 1.9, 1.9, 0.05, None, caras={'frente': P['nucleo']}, semilla=41)
    # la corona de cada tipo
    if k == 'A':
        for s in (1, -1):                                 # dos cuernos como pararrayos, con la punta encendida
            p = punto(Mh, (s * 1.0, 1.4, -0.6))
            for j, (d, g) in enumerate((((s * 0.4, 1.0, -0.6), 0.42), ((s * 0.2, 1.0, -0.7), 0.32), ((0.0, 0.9, -0.6), 0.22))):
                q = p + (punto(Mh, d) - punto(Mh, (0, 0, 0))) * 1.3
                viga(out, p, q, g, g, P['hueso'], extra=0.05, semilla=42 + j)
                p = q
            bola(out, vr.T(*p), 0.24, P['luz'], semilla=45)
        for j in range(4):
            pua(out, Mh @ vr.T(0, 1.5, 1.0 - j * 0.8) @ vr.Rx(-40 * D), 0.14, 0.7, P['hueso'], semilla=46)
    elif k == 'B':
        for j, (x, ang, h) in enumerate(((-1.0, 22, 2.2), (-0.35, 8, 2.8), (0.35, -8, 2.8), (1.0, -22, 2.2))):
            bm.cristal(out, Mh @ vr.T(x, 1.4, -0.6) @ vr.Rz(ang * D) @ vr.Rx(-30 * D), 0.24, h, P['hielo'], semilla=47 + j)
        for s in (1, -1):                                 # carambanos de la quijada
            for j in range(3):
                bm.cristal(out, Mj @ vr.T(s * 1.0, -0.85, 1.2 + j * 0.8) @ vr.Rx(180 * D), 0.1, 0.6 + 0.2 * j, P['hielo'], semilla=51)
    else:
        nuca = punto(Mh, (0, 0.8, -1.6))                 # la gorguera de membrana, abierta detras de la cabeza
        puntas = []
        for j in range(6):
            phi = math.radians(-75 + j * 30)
            d = punto(Mh, (math.sin(phi) * 1.0, math.cos(phi) * 0.8 + 0.3, -0.45)) - punto(Mh, (0, 0, 0))
            fin = nuca + d * 3.0
            viga(out, nuca, fin, 0.16, 0.16, P['hueso'], semilla=52)
            puntas.append(fin)
        for a, b in zip(puntas, puntas[1:]):
            lamina(out, (nuca, nuca, b, a), P['membrana'], float(np.linalg.norm(b - a)), float(np.linalg.norm(a - nuca)), 53)
        for s in (1, -1):                                 # bulbos de esporas por la quijada
            for j in range(3):
                bola(out, Mj @ vr.T(s * 1.3, -0.4, 0.8 + j * 0.9), 0.24 - j * 0.03, P['bulbo'], semilla=54)


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

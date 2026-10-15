"""
El Minotauro y sus formas (13-10-2026). Juan, tras quitar a Vulpina de las fichas: «la Gorgona si tiene
ese estilo que buscamos... puedes ver como tenemos la carpeta de fichas, bosses, ahi esta todo para que te
guies en general; ahora si creamos al siguiente boss con sus subtipos».

Del mismo mito que la Gorgona y con la receta de la guia (materiales/fichas/COMO_HACEMOS_LOS_MONSTRUOS.md):
un coloso con cabeza de toro que no es un toro. La cabeza manda: grande, mirando a camara, con las fauces
abiertas (dos mandibulas, los dientes dibujados en hojas, dos colmillos arriba y dos defensas abajo) que
arden por dentro con un solo neon en escalones y un nucleo al fondo de la garganta, y los ojos encendidos
bajo un ceno de hueso. Los cuernos enmarcan la cabeza. El cuerpo es oscuro y macizo, con la giba de pelo
detras de la nuca, las pezunas hendidas y la cola. Todo de cajas, con texturas limpias (manchas grandes de
borde limpio, anillos en los cuernos, placas con remaches de 2 x 2), en pixeles de piel como la Gorgona y
escalado a la escena (ESCALA).

Las tres formas cambian la silueta:

    A  Asterion, el del Laberinto   de pie, con el hacha de doble filo en alto y la cadena rota colgando
                                    del grillete; cuernos hacia delante; faldon de tiras de cuero; ambar
    B  el Calcotauro                el toro de bronce que echa fuego: encorvado para embestir, con un puno
                                    en el suelo, cubierto de placas de bronce con las juntas encendidas;
                                    cuernos muy abiertos con la punta de bronce; turquesa
    C  el Bucentauro                medio toro: el torso del minotauro sobre un cuerpo de toro de cuatro
                                    patas, con el tridente (el toro de Creta salio del mar, de Poseidon);
                                    cuernos en lira; carmesi
"""
import math, random
import numpy as np
import vigia_render as vr
import nerea_modelo as nm
import eclipse_modelo as em
import quimeras_modelo as qm
import bestias_modelo as bm
from bestias_modelo import _imagen, _emis
from sierpe_modelo import _bisel, _manchas, _remaches, _degradado, lamina, cadena
import jefa_modelo as jm
from jefa_modelo import caja, pt

TAU = math.tau
D = vr.D2R
_r = bm._r
PPB = 4                                          # pixeles de textura por unidad (unos 7 por bloque en la escena)
ESCALA = 0.58
CABEZA = 1.45                                    # la cabeza manda: se hace sin escala y se agranda (el pixel no cambia)

BRONCE = _r('3a2410', '6a4420', '9a6a34', 'c8964c', 'f0c878')
VARIANTES = {
    'A': dict(
        clave='A', nombre='Asterion, el del Laberinto', corto='asterion',
        piel=_r('120c0a', '1e1512', '2c201b', '3d2d26', '544036'),
        pelaje=_r('140c08', '22150e', '332016', '4a2e1e', '66422a'),
        cuerno=_r('5a4a36', '8a7656', 'b8a27c', 'dccaa2', 'f6ecd2'),
        punta=_r('0e0a08', '1a1410', '2a221c', '3c322a', '50443a'),
        pezuna=_r('0a0808', '161212', '241e1c', '342c28', '4a3e38'),
        cuero=_r('1e0e08', '34190e', '4c2616', '68361e', '8a4a2a'),
        metal=BRONCE, filo=_r('6a5a40', '9a8a68', 'c8b896', 'e8dcc0', 'fffaf0'),
        dientes=_r('8a8070', 'b8ad98', 'dcd2bc', 'f2eada', 'fffcf2'),
        neon=('fff2d8', 'ffa02a', '6a2a04'),
    ),
    'B': dict(
        clave='B', nombre='el Calcotauro', corto='calcotauro',
        piel=_r('0c0e0e', '161a1a', '202626', '2c3434', '3c4646'),
        pelaje=_r('0a0c0c', '141818', '1e2424', '2a3232', '3a4444'),
        cuerno=_r('1a1a1a', '2c2a28', '403c38', '58524c', '746c64'),
        punta=BRONCE,
        pezuna=_r('0a0c0c', '141818', '1e2424', '2a3232', '3a4444'),
        cuero=_r('101414', '1a2020', '262e2e', '343e3e', '465252'),
        metal=_r('3a2410', '6a4420', '9a6a34', 'c8964c', 'f0c878'), filo=_r('2a4a44', '3e6a62', '5a9488', 'a0d2c4', 'e0fff4'),
        dientes=_r('7a8a86', 'a8b8b2', 'ccdcd6', 'e6f2ee', 'fafffe'),
        neon=('e8fff8', '2affd2', '04584a'),
    ),
    'C': dict(
        clave='C', nombre='el Bucentauro', corto='bucentauro',
        piel=_r('0e0a0c', '1a1216', '261a20', '34242c', '46323c'),
        pelaje=_r('0c080a', '181014', '24181e', '322128', '442c36'),
        cuerno=_r('0a0808', '161012', '22181c', '302228', '423038'),
        punta=_r('3a0610', '68101c', '9a1a28', 'c82a3a', 'f04a5a'),
        pezuna=_r('0a0808', '161012', '22181c', '302228', '423038'),
        cuero=_r('1a0a0c', '2c1216', '401c20', '58262c', '74343a'),
        metal=_r('2a2a30', '44444e', '66666e', '9494a0', 'd0d0da'), filo=_r('5a1a24', '8a2a36', 'c04452', 'e87a86', 'ffd2d8'),
        dientes=_r('8a7a7a', 'b8a8a6', 'dccccb', 'f2e6e4', 'fffafa'),
        neon=('ffe6e8', 'ff2a46', '6a0414'),
    ),
}


# ----------------------------------------------------------------------
#  Los pintores (texturas limpias, paletas de 5 tonos)
# ----------------------------------------------------------------------
def pintores(V):
    k = V['clave']
    P = {}

    def reg(nombre, fn, pleno=False):
        fn.__name__ = 'min%s_%s' % (k, nombre)
        if pleno:
            bm.PLENOS.add(fn)
        P[nombre] = fn
        return fn

    nuc, neo, hon = V['neon']

    def piel(tw, th, cara, s):
        """La piel: oscura, con manchas grandes de borde limpio un tono mas claras."""
        idx = _manchas(tw, th, s, celda=7.0, umbral=0.6, alto=0.8)
        idx = np.array([1, 2, 2, 3, 3])[idx]
        return _imagen(_bisel(idx, 1, 1), V['piel']), None
    reg('piel', piel)

    def pelaje(tw, th, cara, s):
        """El pelo de la giba, la crin y las patas: mechones a lo largo en dos tonos, con alguno claro."""
        return jm.hebras(tw, th, s, V['pelaje'], 2, 4), None
    reg('pelaje', pelaje)

    def cuerno(tw, th, cara, s):
        """Los cuernos: anillos claros y oscuros de traves, como los de un toro viejo."""
        largo_x = tw >= th
        n_l = tw if largo_x else th
        a = np.arange(n_l)
        fila = np.where((a % 5) == 0, 1, np.where((a % 5) == 1, 3, 2))
        idx = np.tile(fila, ((th if largo_x else tw), 1))
        if not largo_x:
            idx = idx.T
        return _imagen(_bisel(idx, 1, 1), V['cuerno']), None
    reg('cuerno', cuerno)
    reg('punta', jm.liso(V['punta'], 2, 2, 1))
    reg('pezuna', jm.liso(V['pezuna'], 2, 2, 1))

    def cuero(tw, th, cara, s):
        """El cuero de las tiras del faldon y las correas: liso con un pespunte claro a los lados."""
        idx = np.full((th, tw), 2)
        if th >= tw and tw >= 4:
            idx[:, 1] = 3
            idx[:, -2] = 3
        elif tw >= 4 and th >= 4:
            idx[1, :] = 3
            idx[-2, :] = 3
        return _imagen(_bisel(idx, 1, 1), V['cuero']), None
    reg('cuero', cuero)

    def metal(tw, th, cara, s):
        """El bronce (o el hierro): placa con su canto claro y una fila de remaches de 2 x 2."""
        idx = _remaches(np.full((th, tw), 2), cara, paso=5) if min(tw, th) >= 4 else np.full((th, tw), 2)
        return _imagen(_bisel(idx, 2, 1), V['metal']), None
    reg('metal', metal)
    reg('metal_liso', jm.liso(V['metal'], 3, 1, 1))

    def placa(tw, th, cara, s):
        """B: la placa de bronce con las juntas encendidas: el canto de la placa brilla del neon."""
        tex = _imagen(_bisel(_remaches(np.full((th, tw), 2), cara, paso=6) if min(tw, th) >= 5 else np.full((th, tw), 2), 1, 1),
                      V['metal'])
        if tw < 3 or th < 3:
            return tex, None
        m = np.zeros((th, tw), bool)
        if cara in ('arriba', 'abajo'):
            return tex, None
        m[-1, :] = True                                    # la junta de abajo, donde monta sobre la siguiente
        if th >= 6:
            m[-2, 1:-1] = True
        tex[m] = (*nm._hex(neo), 255)
        return tex, _emis(tex, m, 210)
    reg('placa', placa)

    def filo(tw, th, cara, s):
        """La hoja del hacha y del tridente: el metal con el filo claro."""
        idx = np.full((th, tw), 2)
        if tw >= 3:
            idx[:, -1] = 4
            idx[:, -2] = 3
        return _imagen(_bisel(idx, 1, 1), V['filo']), None
    reg('filo', filo)

    def fauces(tw, th, cara, s):
        """El paladar: escalones de luz (blanco al fondo, el neon, la sombra) con sus estrias."""
        t = _degradado(th, tw, cara == 'abajo', nuc, neo, hon)
        return t, _emis(t, np.ones((th, tw), bool), 235)
    reg('fauces', fauces)

    def boca(tw, th, cara, s):
        """El suelo de la boca: bandas en V del neon, hondas en los bordes y casi blancas en el centro."""
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        u = (xs + 0.5) / tw
        dd = np.minimum(u, 1 - u) * 2
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        col = np.where((dd < 0.2)[..., None], np.array(c_h),
                       np.where((dd < 0.46)[..., None], np.array(qm._mezcla(c_h, c_m, 0.6)),
                                np.where((dd < 0.76)[..., None], np.array(c_m), np.array(qm._mezcla(c_m, c_n, 0.65)))))
        t = np.zeros((th, tw, 4), np.uint8)
        t[..., :3] = col
        t[..., 3] = 255
        return t, _emis(t, dd >= 0.2, 230)
    reg('boca', boca)

    def nucleo(tw, th, cara, s):
        """El fondo de la garganta: un resplandor redondo, blanco en el centro."""
        t = np.zeros((th, tw, 4), np.uint8)
        ys, xs = np.mgrid[0:th, 0:tw].astype(float)
        cx, cy = (tw - 1) / 2, (th - 1) / 2
        r = np.hypot(xs - cx, ys - cy) / max(min(tw, th) / 2, 1)
        c_n, c_m, c_h = nm._hex(nuc), nm._hex(neo), nm._hex(hon)
        dentro = r < 1.0
        col = np.where((r < 0.45)[..., None], np.array(c_n),
                       np.where((r < 0.75)[..., None], np.array(qm._mezcla(c_m, c_n, 0.4)), np.array(c_m)))
        col = np.where(((r > 0.9) & dentro)[..., None], np.array(c_h), col)
        t[..., :3] = col
        t[..., 3] = np.where(dentro, 255, 0)
        return t, _emis(t, dentro & (r < 0.9), 240)
    reg('nucleo', nucleo)

    def _hojas_de_dientes(tw, th, rampa, colgando):
        """Una fila de dientes dibujada en una hoja (no hecha de cubos): cada diente de cuatro pixeles de
        ancho, con la raya clara por el medio, el borde oscuro y la punta en escalon; uno largo y uno corto;
        entre uno y otro, hueco."""
        t = np.zeros((th, tw, 4), np.uint8)
        c = [(*cc, 255) for cc in rampa]
        n = max(1, (tw + 1) // 5)
        x0 = (tw - (n * 5 - 1)) // 2
        for i in range(n):
            x = x0 + i * 5
            largo = th if i % 2 == 0 else max(2, int(round(th * 0.68)))
            for k_ in range(largo):
                y = k_ if colgando else th - 1 - k_
                f = k_ / max(largo - 1, 1)
                if f > 0.85:
                    pix = ((x + 1, c[4]),)
                elif f > 0.6:
                    pix = ((x + 1, c[4]), (x + 2, c[3]))
                else:
                    pix = ((x, c[2]), (x + 1, c[4]), (x + 2, c[3]), (x + 3, c[1]))
                for xx, col in pix:
                    if 0 <= xx < tw:
                        t[y, xx] = col
            y = 0 if colgando else th - 1
            for xx in range(max(x, 0), min(x + 4, tw)):
                t[y, xx] = c[1]
        return t, None
    reg('dientes_arriba', lambda tw, th, c, s: _hojas_de_dientes(tw, th, V['dientes'], True))
    reg('dientes_abajo', lambda tw, th, c, s: _hojas_de_dientes(tw, th, V['dientes'], False))

    def colmillo(tw, th, cara, s):
        """Los colmillos y las defensas: marfil con una raya clara a lo largo y la punta clara."""
        idx = np.full((th, tw), 2)
        if tw >= 2:
            idx[:, 0] = 4
            idx[:, -1] = 1
        return _imagen(idx, V['dientes']), None
    reg('colmillo', colmillo)

    def ojo(tw, th, cara, s):
        return qm._emisivo(nuc, neo, max(2, tw), max(2, th)), None
    reg('ojo', ojo, pleno=True)

    def nariz(tw, th, cara, s):
        """El morro: la piel mas oscura y lisa con un pliegue claro de traves (sin ollares pintados: en un
        morro de caja, dos manchas se leen como ojos; lo que dice "nariz de toro" es el aro)."""
        idx = np.full((th, tw), 1)
        if th >= 5:
            idx[th // 2, 1:-1] = 2
        return _imagen(_bisel(idx, 1, 1), V['piel']), None
    reg('nariz', nariz)
    P['_reg'] = reg
    return P


# ----------------------------------------------------------------------
#  La cabeza
# ----------------------------------------------------------------------
def hilera(out, M, puntos, y, alto, pintor, semilla=0):
    """Una fila de dientes en hojas a lo largo de una linea quebrada en el plano de la mandibula (x, z), de
    y a y + alto en el marco M (con alto negativo cuelgan; con alto positivo estan de pie)."""
    for j, ((x0, z0), (x1, z1)) in enumerate(zip(puntos, puntos[1:])):
        A, B = pt(M, (x0, y, z0)), pt(M, (x1, y, z1))
        A2, B2 = pt(M, (x0, y + alto, z0)), pt(M, (x1, y + alto, z1))
        lado, h = float(np.linalg.norm(B - A)), float(np.linalg.norm(A2 - A))
        if alto < 0:
            lamina(out, (A2, B2, B, A), pintor, lado, h, semilla + j)
        else:
            lamina(out, (A, B, B2, A2), pintor, lado, h, semilla + j)


def cuernos(out, Mh, P, forma):
    """Los cuernos, que enmarcan la cabeza: tubos de bloques de seccion de ocho lados que se afinan, con
    anillos; la punta de otro color. 'adelante' (A): salen a los lados y se curvan hacia delante y arriba;
    'abiertos' (B): muy largos hacia los lados, con la punta de bronce; 'lira' (C): salen, suben y abren
    la punta hacia fuera."""
    for s in (1, -1):
        b = np.array((s * 3.8, 5.6, 0.4))
        if forma == 'adelante':
            ctrl = [b, b + (s * 3.0, 0.8, -0.4), b + (s * 6.4, 2.6, 1.0), b + (s * 8.0, 5.4, 4.0), b + (s * 7.4, 7.6, 6.8)]
            perfil = ((0.0, 1.55), (0.5, 1.1), (1.0, 0.35))
        elif forma == 'abiertos':
            ctrl = [b, b + (s * 4.0, 0.4, 0.0), b + (s * 9.0, 0.6, 0.6), b + (s * 13.5, 2.2, 1.6), b + (s * 16.0, 4.6, 2.4)]
            perfil = ((0.0, 1.7), (0.5, 1.15), (1.0, 0.4))
        else:
            ctrl = [b, b + (s * 2.6, 1.6, -0.6), b + (s * 4.2, 5.4, -0.6), b + (s * 3.8, 9.6, 0.0), b + (s * 5.8, 12.6, 0.6)]
            perfil = ((0.0, 1.5), (0.5, 1.0), (1.0, 0.35))
        pts, rs, ts = jm.a_lo_largo([pt(Mh, c) for c in ctrl], 10, perfil)
        pin = [P['punta'] if (t0 + t1) / 2 > 0.8 else P['cuerno'] for t0, t1 in zip(ts, ts[1:])]
        jm.tubo(out, pts, rs, pin, semilla=60 + (s > 0))
        if forma == 'abiertos':                                         # el casquillo de bronce
            d = pts[-1] - pts[-2]
            M = em.marco(pts[-2], d)
            caja(out, M, -0.75, 0.75, -0.75, 0.75, -0.3, float(np.linalg.norm(d)) + 0.6, P['metal_liso'], semilla=63)


def cabeza(out, Mh, P, V, abre=30.0, forma_cuernos='adelante', aro=True):
    """La cabeza de toro, grande y maciza, con el morro hacia +z: el craneo ancho; el ceno de hueso que
    sobresale y, bajo el, los ojos encendidos; las orejas; el mechon de la frente; el morro largo con los
    ollares y el aro; la mandibula de arriba con el paladar encendido en escalones, los dientes dibujados
    en hojas y dos colmillos; la de abajo, abierta, con el suelo de la boca encendido, los dientes de pie,
    dos defensas que suben y la barba; al fondo de la garganta, el nucleo; y los cuernos."""
    piel, pelo = P['piel'], P['pelaje']
    caja(out, Mh, -4.2, 4.2, 0.0, 6.6, -3.8, 3.0, piel, semilla=1)                                   # el craneo
    caja(out, Mh, -3.6, 3.6, 0.6, 6.0, -4.4, -3.6, piel, semilla=2)
    caja(out, Mh, -2.6, 2.6, 6.4, 8.0, -1.4, 2.8, pelo, semilla=3)                                   # el mechon de la frente
    caja(out, Mh, -4.6, 4.6, 3.8, 5.2, 2.2, 3.9, piel, semilla=4)                                     # el ceno
    caja(out, Mh, -1.0, 1.0, 4.2, 5.5, 3.0, 4.2, piel, semilla=5)
    for s in (1, -1):
        x0, x1 = sorted((s * 1.3, s * 3.9))
        caja(out, Mh, x0, x1, 2.55, 3.75, 2.85, 3.2, P['ojo'], semilla=6)                            # los ojos
        Mc = Mh @ vr.T(s * 2.5, 3.9, 3.25) @ vr.Rz(s * 14 * D)                                       # el ceno en angulo
        caja(out, Mc, -1.9, 1.9, -0.25, 0.65, -0.5, 0.75, piel, semilla=21)
        Mo = Mh @ vr.T(s * 4.1, 3.6, 0.2) @ vr.Rz(-s * 22 * D)                                       # las orejas
        caja(out, Mo, 0.0 if s > 0 else -2.4, 2.4 if s > 0 else 0.0, -0.5, 0.6, -0.8, 0.8, piel, semilla=7)
    # la mandibula de arriba: el morro, con el paladar encendido por debajo
    bm.cubo(out, Mh, -3.1, 0.9, 2.9, 6.2, 3.0, 6.4, piel, caras={'abajo': P['fauces']}, semilla=8)
    bm.cubo(out, Mh, -2.4, 1.2, 9.2, 4.8, 2.5, 1.0, P['nariz'], semilla=9)
    caja(out, Mh, -1.6, 1.6, 3.6, 4.4, 3.4, 9.0, piel, semilla=22)                                   # el puente del morro
    hilera(out, Mh, [(-2.85, 3.3), (-2.85, 9.1), (2.85, 9.1), (2.85, 3.3)], 0.95, -1.0, P['dientes_arriba'], semilla=10)
    for s in (1, -1):                                                                                  # los colmillos
        M = Mh @ vr.T(s * 2.3, 0.95, 8.4)
        caja(out, M, -0.4, 0.4, -2.4, 0.0, -0.35, 0.35, P['colmillo'], semilla=11)
        caja(out, M, -0.25, 0.25, -3.0, -2.3, -0.2, 0.2, P['colmillo'], semilla=12)
    if aro:                                                                                            # el aro, colgando del tabique
        for (x0, x1, y0, y1) in ((-0.85, 0.85, -0.55, -0.25), (-0.85, -0.55, -0.55, 1.7), (0.55, 0.85, -0.55, 1.7)):
            caja(out, Mh, x0, x1, y0, y1, 10.15, 10.4, P['metal_liso'], semilla=13)
    # el nucleo, al fondo de la garganta
    caja(out, Mh, -2.2, 2.2, -1.6, 0.95, 2.6, 2.95, P['nucleo'], semilla=14)
    # la mandibula de abajo, abierta
    Mj = Mh @ vr.T(0, 0.9, 1.2) @ vr.Rx(abre * D)
    bm.cubo(out, Mj, -2.8, -1.7, 0.0, 5.6, 1.7, 7.6, piel, caras={'arriba': P['boca']}, semilla=15)
    hilera(out, Mj, [(-2.55, 1.0), (-2.55, 7.35), (2.55, 7.35), (2.55, 1.0)], 0.0, 1.0, P['dientes_abajo'], semilla=16)
    for s in (1, -1):                                                                                  # las defensas
        M = Mj @ vr.T(s * 2.2, 0.0, 6.6) @ vr.Rz(-s * 12 * D) @ vr.Rx(-10 * D)
        caja(out, M, -0.45, 0.45, 0.0, 2.4, -0.4, 0.4, P['colmillo'], semilla=17)
        caja(out, M, -0.28, 0.28, 2.3, 3.2, -0.25, 0.25, P['colmillo'], semilla=18)
    caja(out, Mj, -1.7, 1.7, -3.6, -1.6, 3.4, 7.0, pelo, semilla=19)                                 # la barba
    caja(out, Mj, -1.1, 1.1, -4.6, -3.5, 4.0, 6.6, pelo, semilla=20)
    cuernos(out, Mh, P, forma_cuernos)
    return pt(Mh, (0.0, 0.4, 5.0))                                                                    # donde brilla la boca


# ----------------------------------------------------------------------
#  El cuerpo: torso, brazos, piernas y pezunas
# ----------------------------------------------------------------------
def torso(out, P, faldon=None):
    """El torso de toro, macizo como el del Calcotauro: la cadera y el vientre de barril (sin cintura de
    hombre), el pecho ancho y hondo con los pectorales, los hombros anchos y la giba de pelo detras de la
    nuca, alta y grande, con la crin que baja por la espalda."""
    piel, pelo = P['piel'], P['pelaje']
    caja(out, jm.I4, -5.6, 5.6, 21.0, 27.2, -3.8, 3.8, piel, semilla=100)                            # la cadera
    caja(out, jm.I4, -5.6, 5.6, 27.0, 32.4, -3.8, 3.8, piel, semilla=101)                            # el vientre
    for j, y in enumerate((27.6, 29.3, 31.0)):                                                       # los abdominales
        caja(out, jm.I4, -3.0, 3.0, y, y + 1.4, 3.7, 4.25, piel, semilla=102 + j)
    caja(out, jm.I4, -7.8, 7.8, 32.0, 41.0, -4.6, 4.6, piel, semilla=105)                            # el pecho
    for s_ in (1, -1):                                                                                 # los pectorales
        x0, x1 = sorted((s_ * 0.3, s_ * 7.0))
        caja(out, jm.I4, x0, x1, 34.8, 40.4, 4.5, 5.8, piel, semilla=106)
    caja(out, jm.I4, -9.4, 9.4, 38.6, 42.8, -4.2, 4.2, piel, semilla=107)                            # los hombros
    caja(out, jm.I4, -6.6, 6.6, 39.5, 48.0, -5.4, 1.8, pelo, semilla=108)                            # la giba
    caja(out, jm.I4, -5.0, 5.0, 47.0, 51.4, -4.4, 0.6, pelo, semilla=109)
    caja(out, jm.I4, -5.6, 5.6, 33.0, 42.0, -5.8, -4.4, pelo, semilla=110)                           # la crin por la espalda


HOMBRO = np.array((11.0, 39.6, 0.0))
L_BRAZO, L_ANTEBRAZO = 10.0, 9.0


def brazo(out, P, s, pose, guante=None, grillete=False):
    """Un brazo enorme: el brazo y el antebrazo (mas grueso), que dobla por la espalda del codo; el pelo
    del antebrazo y el puno de bloque. Devuelve el marco de la mano."""
    Mh = (vr.T(s * HOMBRO[0], HOMBRO[1], HOMBRO[2]) @ vr.Rz(s * pose.get('abd', 10) * D) @ vr.Rx(-pose.get('flex', 0) * D)
          @ vr.Ry(-s * pose.get('giro', 0) * D))
    Mc = Mh @ vr.T(0, -L_BRAZO, -3.3) @ vr.Rx(-pose.get('codo', 10) * D) @ vr.T(0, 0, 3.6)
    Mm = Mc @ vr.T(0, -L_ANTEBRAZO, 0) @ vr.Rx(-pose.get('mun', 0) * D)
    caja(out, Mh, -3.3, 3.3, -L_BRAZO, 2.0, -3.3, 3.3, P['piel'], semilla=120)
    caja(out, Mh, -4.0, 4.0, -3.6, 3.2, -4.0, 4.0, P['piel'], semilla=125)                          # el deltoide
    caja(out, Mc, -3.6, 3.6, -L_ANTEBRAZO, 0.0, -3.6, 3.6, P['piel'], semilla=121)
    caja(out, Mc, -3.95, 3.95, -4.2, 0.2, -3.95, 3.95, P['pelaje'], semilla=122)                      # el pelo del antebrazo
    if guante is not None:
        caja(out, Mc, -4.1, 4.1, -L_ANTEBRAZO + 0.2, -3.8, -4.1, 4.1, guante, semilla=123)
    if grillete:
        caja(out, Mc, -4.2, 4.2, -L_ANTEBRAZO + 0.4, -L_ANTEBRAZO + 2.2, -4.2, 4.2, P['metal'], semilla=124)
    return jm.mano(out, Mm, s, 'bloque', P['piel'], k=2.8, cierra=pose.get('cierra', 1.0)), Mm


CADERA = np.array((3.7, 24.0, 0.0))
L_MUSLO, L_PIERNA = 11.0, 10.5


def pierna(out, P, s, pose, placa=None):
    """Una pierna maciza que acaba en pezuna hendida: el muslo, la rodilla que dobla por delante, la
    pierna con el pelo largo que cae sobre la pezuna, y la pezuna en dos."""
    Mt = vr.T(s * CADERA[0], CADERA[1], CADERA[2]) @ vr.Rz(s * pose.get('abd', 4) * D) @ vr.Rx(-pose.get('flex', 0) * D)
    Mr = Mt @ vr.T(0, -L_MUSLO, 3.2) @ vr.Rx(pose.get('rodilla', 5) * D) @ vr.T(0, 0, -2.8)
    Mp = (Mr @ vr.T(0, -L_PIERNA, 0) @ vr.Rx((pose.get('flex', 0) - pose.get('rodilla', 5) - pose.get('pie', 0)) * D)
          @ vr.Rz(-s * pose.get('abd', 4) * D))
    piel = P['piel']
    caja(out, Mt, -3.7, 3.7, -5.6, 1.5, -4.0, 3.3, piel, semilla=130)
    caja(out, Mt, -3.2, 3.2, -L_MUSLO, -5.5, -3.3, 3.2, piel, semilla=131)
    caja(out, Mr, -3.0, 3.0, -5.0, 0.0, -3.6, 2.8, piel, semilla=132)
    caja(out, Mr, -2.5, 2.5, -L_PIERNA, -4.9, -2.6, 2.8, piel, semilla=133)
    caja(out, Mr, -3.15, 3.15, -L_PIERNA + 0.3, -5.6, -3.2, 3.3, P['pelaje'], semilla=134)       # el pelo de la pierna
    if placa is not None:
        caja(out, Mr, -3.3, 3.3, -4.6, 0.6, 2.7, 3.5, placa, semilla=135)
        caja(out, Mt, -3.5, 3.5, -L_MUSLO - 0.4, -L_MUSLO + 1.6, 3.0, 3.9, placa, semilla=136)
    for x0, x1 in ((-2.7, -0.15), (0.15, 2.7)):                                                       # la pezuna hendida
        caja(out, Mp, x0, x1, -2.5, 0.2, -2.4, 3.6, P['pezuna'], semilla=137)
    return Mt, Mr, Mp


def cola(out, P, base, puntos):
    """La cola: un tubo fino que acaba en un penacho de pelo."""
    ctrl = [np.asarray(base, float)] + [np.asarray(p, float) for p in puntos]
    pts, rs, ts = jm.a_lo_largo(ctrl, 8, ((0.0, 0.9), (0.7, 0.6), (1.0, 0.5)))
    jm.tubo(out, pts, rs, [P['piel']] * (len(pts) - 1), semilla=140)
    d = pts[-1] - pts[-2]
    M = em.marco(pts[-1], d)
    caja(out, M, -1.4, 1.4, -1.4, 1.4, -0.4, 4.2, P['pelaje'], semilla=141)
    caja(out, M, -0.9, 0.9, -0.9, 0.9, 4.0, 5.6, P['pelaje'], semilla=142)


# ----------------------------------------------------------------------
#  Las armas y lo de cada forma
# ----------------------------------------------------------------------
def labrys(out, P, puno, largo=30.0):
    """A: el hacha de doble filo, derecha, con el mango que pasa por el puno: las dos hojas en media luna
    en escalones con el filo claro y la punta de arriba."""
    M = vr.T(*puno)
    caja(out, M, -0.6, 0.6, -6.0, largo - 6.0, -0.6, 0.6, P['cuero'], semilla=150)
    caja(out, M, -0.85, 0.85, -6.6, -5.6, -0.85, 0.85, P['metal_liso'], semilla=151)
    Mt = M @ vr.T(0, largo - 9.0, 0)
    for t in (1, -1):
        for j, (x0, x1, h) in enumerate(((0.6, 3.6, 5.0), (3.6, 6.0, 3.9), (6.0, 7.4, 2.5))):
            a0, a1 = sorted((t * x0, t * x1))
            caja(out, Mt, a0, a1, -h, h, -0.32, 0.32, P['filo'] if j == 2 else P['metal'], semilla=152 + j)
    caja(out, Mt, -0.45, 0.45, 4.8, 8.0, -0.45, 0.45, P['metal_liso'], semilla=155)
    caja(out, Mt, -1.0, 1.0, -0.9, 0.9, -0.75, 0.75, P['metal_liso'], semilla=156)


def tridente(out, P, puno, largo=34.0):
    """C: el tridente, derecho, con el asta que pasa por el puno: la cruceta y tres puntas con su lengueta
    (la del medio, mas larga)."""
    M = vr.T(*puno)
    caja(out, M, -0.55, 0.55, -10.0, largo - 10.0, -0.55, 0.55, P['metal_liso'], semilla=160)
    Mt = M @ vr.T(0, largo - 10.0, 0)
    caja(out, Mt, -3.6, 3.6, 0.0, 0.9, -0.5, 0.5, P['metal_liso'], semilla=161)
    for x, l in ((-3.1, 4.8), (0.0, 6.4), (3.1, 4.8)):
        caja(out, Mt, x - 0.45, x + 0.45, 0.8, 0.8 + l, -0.45, 0.45, P['filo'], semilla=162)
        caja(out, Mt, x - 0.25, x + 0.25, 0.8 + l, 1.9 + l, -0.3, 0.3, P['filo'], semilla=163)
        caja(out, Mt, x + 0.35, x + 1.1, l - 0.6, l + 0.3, -0.3, 0.3, P['filo'], semilla=164)


def faldon(out, P):
    """A: el cinturon ancho con la hebilla de bronce y el faldon de tiras de cuero con la punta de bronce."""
    caja(out, jm.I4, -5.85, 5.85, 25.6, 27.8, -4.05, 4.05, P['cuero'], semilla=170)
    caja(out, jm.I4, -1.4, 1.4, 25.4, 28.0, 4.0, 4.4, P['metal_liso'], semilla=171)
    n = 16
    for j in range(n):
        a = j * TAU / n
        p = np.array((math.sin(a) * 5.95, 26.0, math.cos(a) * 4.15))
        M = vr.T(*p) @ vr.Ry(a) @ vr.Rx(-6 * D)
        caja(out, M, -0.85, 0.85, -9.5, 0.0, -0.22, 0.22, P['cuero'], semilla=172 + j % 3)
        caja(out, M, -0.95, 0.95, -10.3, -9.2, -0.3, 0.3, P['metal_liso'], semilla=175)


def armadura_bronce(out, P):
    """B: las placas de bronce con las juntas encendidas: sobre la giba, el pecho y el vientre."""
    for j, (y0, y1, w, z0) in enumerate(((46.0, 52.0, 5.4, -4.8), (39.4, 46.4, 7.2, -5.8))):
        caja(out, jm.I4, -w, w, y0, y1, z0 - 0.6, z0 + 4.2, P['placa'], semilla=180 + j)            # la giba acorazada
    for s in (1, -1):                                                                                  # las placas del pecho
        x0, x1 = sorted((s * 0.4, s * 7.2))
        caja(out, jm.I4, x0, x1, 35.0, 40.6, 5.6, 6.4, P['placa'], semilla=184)
    for j, y in enumerate((27.4, 29.7)):                                                              # el vientre en lamas
        caja(out, jm.I4, -5.95, 5.95, y, y + 2.1, -4.1, 4.25, P['placa'], semilla=185 + j)


def hombrera(out, P, s, pose):
    """B: la hombrera de tres placas de bronce, sobre el hombro."""
    Mh = (vr.T(s * HOMBRO[0], HOMBRO[1], HOMBRO[2]) @ vr.Rz(s * pose.get('abd', 10) * D) @ vr.Rx(-pose.get('flex', 0) * D))
    for j in range(2):
        Mj = Mh @ vr.T(s * (0.5 + 0.5 * j), 3.6 - 3.0 * j, 0) @ vr.Rz(s * (14 + 14 * j) * D)
        w = 4.7 - 0.3 * j
        caja(out, Mj, -w, w, -3.2, 0.0, -4.4 + 0.2 * j, 4.4 - 0.2 * j, P['placa'], semilla=187 + j)


def cuerpo_de_toro(out, P):
    """C: el cuerpo de toro de cuatro patas, macizo: el barril, el pecho del toro bajo el torso, el lomo de
    pelo, las patas de delante rectas y las de atras con el corvejon, cada una con su pezuna hendida, y la
    cola."""
    piel = P['piel']
    caja(out, jm.I4, -7.2, 7.2, 14.0, 28.0, -21.0, 2.0, piel, semilla=190)                            # el barril
    caja(out, jm.I4, -6.2, 6.2, 13.0, 14.2, -19.0, 0.0, piel, semilla=191)
    caja(out, jm.I4, -6.6, 6.6, 27.6, 29.6, -19.5, 0.5, P['pelaje'], semilla=192)                    # el lomo de pelo
    caja(out, jm.I4, -6.4, 6.4, 15.0, 28.5, 1.0, 5.8, piel, semilla=193)                              # el pecho del toro
    caja(out, jm.I4, -6.8, 6.8, 21.0, 29.4, -23.0, -20.4, piel, semilla=194)                          # la grupa
    for s in (1, -1):
        for z, atras in ((0.0, False), (-17.0, True)):
            M = vr.T(s * 5.0, 18.0, z)
            caja(out, M, -3.0, 3.0, -6.5, 3.0, -3.3, 3.3, piel, semilla=195)                         # el muslo
            if atras:                                                                                  # el corvejon atras
                Mk = M @ vr.T(0, -6.5, -2.4) @ vr.Rx(-18 * D)
                caja(out, Mk, -2.1, 2.1, -6.6, 0.4, -2.1, 2.3, piel, semilla=196)
                Mp = Mk @ vr.T(0, -6.6, 0.4) @ vr.Rx(18 * D)
            else:
                Mk = M @ vr.T(0, -6.5, 0.0)
                caja(out, Mk, -2.2, 2.2, -7.6, 0.4, -2.2, 2.2, piel, semilla=196)
                Mp = Mk @ vr.T(0, -7.6, 0.0)
            caja(out, Mk, -2.6, 2.6, -7.0, -3.4, -2.6, 2.6, P['pelaje'], semilla=197)                 # el pelo sobre la pezuna
            for x0, x1 in ((-2.4, -0.12), (0.12, 2.4)):
                caja(out, Mp, x0, x1, -3.4, 0.0, -2.2, 3.0, P['pezuna'], semilla=198)
    cola(out, P, (0.0, 26.0, -22.6), [(0.0, 23.0, -25.4), (1.2, 16.0, -26.0), (2.0, 10.0, -24.4)])


# ======================================================================
#  EL MINOTAURO
# ======================================================================
POSES = {
    'A': dict(brazos={-1: dict(abd=150, flex=-10, codo=40, giro=-70, mun=-20, cierra=1.0),
                      1: dict(abd=24, flex=10, codo=40, giro=10, mun=-10, cierra=0.25)},
              piernas={1: dict(abd=9, flex=-22, rodilla=10), -1: dict(abd=8, flex=36, rodilla=54)},
              cabeza=(-10, 0), cuernos='adelante', abre=32.0, encorva=26.0),
    'B': dict(brazos={-1: dict(abd=18, flex=22, codo=34, giro=0, mun=10, cierra=1.0),
                      1: dict(abd=24, flex=-4, codo=44, giro=-10, mun=0, cierra=1.0)},
              piernas={1: dict(abd=9, flex=-25, rodilla=10), -1: dict(abd=8, flex=40, rodilla=60)},
              cabeza=(-14, 0), cuernos='abiertos', abre=34.0, encorva=34.0),
    'C': dict(brazos={-1: dict(abd=46, flex=26, codo=44, giro=-20, mun=-20, cierra=1.0),
                      1: dict(abd=30, flex=10, codo=60, giro=-30, mun=0, cierra=0.3)},
              cabeza=(-6, 0), cuernos='lira', abre=32.0, encorva=22.0),
}


def minotauro(tipo='A'):
    V = VARIANTES[tipo]
    P = pintores(V)
    pose = POSES[tipo]
    ppb = bm.PPB
    bm.PPB = PPB
    out = []
    try:
        arriba = []                                                     # del vientre para arriba, con los brazos y la cabeza
        torso(arriba, P)
        manos = {}
        for s in (1, -1):
            guante = P['placa'] if tipo == 'B' else None
            manos[s] = brazo(arriba, P, s, pose['brazos'][s], guante=guante, grillete=(tipo == 'A'))
            if tipo == 'B':
                hombrera(arriba, P, s, pose['brazos'][s])
        if tipo == 'B':
            armadura_bronce(arriba, P)
        if tipo == 'A':
            labrys(arriba, P, pt(manos[-1][1], (0, -3.0, 0)))
            c0 = pt(manos[1][1], (0, -1.0, 0))                          # la cadena rota que cuelga del grillete
            cadena(arriba, c0, c0 + np.array((0.6, -9.0, 0.8)), 1.5, P['metal_liso'], semilla=200)
        if tipo == 'C':
            tridente(arriba, P, pt(manos[-1][1], (0, -3.0, 0)))
        tx, tz = pose['cabeza']
        Mh = vr.T(0.0, 42.4, 4.2) @ vr.Rx(tx * D) @ vr.Rz(tz * D) @ np.diag([CABEZA] * 3 + [1.0])
        bm.PPB = PPB / CABEZA
        boca = cabeza(arriba, Mh, P, V, abre=pose['abre'], forma_cuernos=pose['cuernos'], aro=(tipo != 'C'))
        bm.PPB = PPB
        if tipo == 'C':                                                 # el torso, encorvado, sobre el pecho del toro
            Mt = vr.T(0.0, 4.0, 4.5) @ vr.T(0, 26.0, 0) @ vr.Rx(pose['encorva'] * D) @ vr.T(0, -26.0, 0)
            out += qm.transformar(arriba, Mt)
            boca = pt(Mt, boca)
            cuerpo_de_toro(out, P)
        else:
            if tipo == 'A':
                faldon(arriba, P)
            enc = pose.get('encorva', 0.0)
            Mt = vr.T(0, 26.0, 0) @ vr.Rx(enc * D) @ vr.T(0, -26.0, 0)
            out += qm.transformar(arriba, Mt)
            boca = pt(Mt, boca)
            for s in (1, -1):
                pierna(out, P, s, pose['piernas'][s], placa=P['placa'] if tipo == 'B' else None)
            cola(out, P, (0.0, 24.0, -4.0), [(0.6, 20.0, -6.6), (1.4, 13.0, -7.6), (2.0, 7.0, -6.0)])
    finally:
        bm.PPB = ppb
    y0 = min(min(p[1] for p in q[0]) for q in out)                    # que pise el suelo
    E = np.diag([ESCALA] * 3 + [1.0]) @ vr.T(0, -y0, 0)
    out = qm.transformar(out, E)
    boca = pt(E, boca)
    return out, {'boca': boca, 'luces': [boca]}


def dibujar(lz, cam, qs, luces, ambiente, niebla=None, brillo=1.4):
    qm.dibujar(lz, cam, qs, luces, ambiente, niebla, brillo)

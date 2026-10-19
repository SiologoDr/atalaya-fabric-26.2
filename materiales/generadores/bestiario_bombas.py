"""
Las bombas voladoras del bestiario (Juan, 18-10-2026: «las bombas no deberían tener cara ni nada, solo sus alas y su
mecha»): el cubo de la bomba con su material bien trabajado, la mecha gruesa en su tapa con la chispa, y dos alas de
verdad, de dos tramos (el brazo y la mano) que se doblan al batir, vistas de frente (la bomba viene hacia ti). Al píxel
de Minecraft (van a escala 1: 16 por bloque).

  ambar    (la «Bomba Truco»)               de ámbar: la miel con hondura (más oscura por dentro del canto), burbujitas y
                                            vetas claras; alas de pluma doradas
  carmesi  (la bomba roja)                   de chapa lacada roja: la junta, los remaches de las esquinas y los arañazos;
                                            alas de murciélago rojas
  negra    (la Bomba Negra)                  de hierro negro en placas con remaches, los cantos gastados y el brillo
                                            azulado; alas de cuervo; la más grande: no se la puede empujar
  abismo   (las Bombas Warden Voladoras)     de sculk, con las motas de cian que brillan y las venas oscuras; alas de
                                            sculk con las venas encendidas; la mecha, detrás

Vuelan siempre: las alas baten («siempre»); con la mecha encendida, la chispa crece y el cubo tiembla («especial» y
«hinchado»); al morir caen dando vueltas.

Uso: python bestiario_bombas.py <raíz> [carpeta de las fotos] [ids]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
import bestiario_limpio as L
import bestiario_creepers as bc
import bestiario_creepers_v7 as v7
from bestiario import T, Rx
from bestiario_limpio import rampa
from bestiario_creepers_v7 import _azar1

CUERDA = rampa('4a3a28', '6e5840', '927a5c', 'b49c7c', 'd4c0a0')
CHISPA = rampa('c04a0a', 'ff8a1a', 'ffc23a', 'fff0a0', 'ffffff')
HIERRO = rampa('101114', '1a1c20', '26292e', '34383e', '464b52')
PIEDRA = rampa('3a3a3e', '55565b', '74757b', '94959b', 'b4b5ba')


# ======================================================================================================================
#  Las alas de verdad: de dos tramos (el brazo y la mano), que se doblan al batir
# ======================================================================================================================
def ala_pluma(nombre, r, tramo, espejo=False):
    """Un tramo de ala de pájaro, al píxel de Minecraft (en la textura: la raíz a la izquierda, el borde de ataque
    arriba). El brazo: las coberteras en escamas (filas de plumitas redondas que se solapan, la de arriba más clara) y
    debajo las secundarias, en tiras de dos píxeles con el cañón más oscuro y la punta clara, de largos alternos (el borde
    de salida en sierra). La mano: las coberteras arriba y las primarias, largas y abiertas como dedos hacia la punta."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        xx = tw - 1 - xs if espejo else xs
        u = (xx + 0.5) / tw
        v = np.zeros((th, tw))
        a = np.zeros((th, tw), bool)
        if tramo == 'brazo':
            cob = max(3, int(round(th * 0.45)))
            borde = ys < 2
            v = np.where(borde, 3.3 - ys * 0.4 - ((xx % 3) == 2) * 0.3, v)
            banda = (ys - 2) // 2
            enb = (ys - 2) % 2
            gx = (xx + (banda % 2)) % 3
            esc = (ys >= 2) & (ys < cob)
            v = np.where(esc, 2.7 - banda * 0.25 + (enb == 0) * 0.5 - (gx == 0) * 0.45, v)
            k = xx // 2
            fin = th - 1 - (k % 2)
            sec = (ys >= cob) & (ys <= fin)
            v = np.where(sec, 1.7 + (ys - cob) * 0.12 - ((xx % 2) == 0) * 0.35 + (ys == fin) * 0.8, v)
            a = borde | esc | sec
        else:
            cob = np.maximum(2, np.round(th * 0.42 * (1 - 0.55 * u))).astype(int)
            borde = ys < 1
            v = np.where(borde, 3.4 - ((xx % 3) == 2) * 0.3, v)
            esc = (ys >= 1) & (ys < cob)
            v = np.where(esc, 2.8 - (ys - 1) * 0.25 - ((xx % 3) == 0) * 0.4, v)
            # Las primarias: tiras de dos píxeles inclinadas hacia la punta, más largas cuanto más afuera, y las de la
            # punta separadas (los dedos del ala).
            k = (xx + (ys - cob) // 2) // 2
            largo = np.round(th * (0.55 + 0.5 * u)).astype(int)
            fin = np.minimum(th - 1, cob + largo - (k % 2) - 1)
            dedos = (u > 0.62) & (((xx + (ys - cob) // 2) % 2) == 1) & (ys > cob + 1)
            pri = (ys >= cob) & (ys <= fin) & ~dedos
            v = np.where(pri, 1.8 + (ys - cob) * 0.13 + u * 0.5 - (((xx + (ys - cob) // 2) % 2) == 0) * 0.3
                         + (ys == fin) * 0.8, v)
            a = borde | esc | pri
        tex = L._rgba(L.color_continuo(r, v))
        tex[..., 3] = np.where(a, 255, 0)
        return tex, None
    return B.Pintor(nombre, fn)


def ala_membrana(nombre, r, rh, tramo, espejo=False, venas=None):
    """Un tramo de ala de murciélago, al píxel de Minecraft (la raíz a la izquierda, el borde de ataque arriba). El
    brazo: el hueso del brazo arriba y la membrana debajo, con el borde de salida en un arco. La mano: los huesos de los
    dedos que salen de la muñeca (arriba a la izquierda) hacia el borde, la membrana entre ellos con los bordes en arco
    (cóncavos entre punta y punta) y una uña en la muñeca. Con 'venas' (una rampa), venas encendidas por la membrana."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        xx = tw - 1 - xs if espejo else xs
        x, y = xx + 0.5, ys + 0.5
        v = np.zeros((th, tw))
        hueso = np.zeros((th, tw), bool)
        vena = np.zeros((th, tw), bool)
        if tramo == 'brazo':
            hueso = ys < 2
            arco = th - 1.0 - 2.4 * np.sin(np.clip(x / tw, 0, 1) * math.pi)
            memb = (ys >= 2) & (y <= arco + 0.5)
            v = np.where(memb, 1.5 + (ys - 2) * 0.22 - (((xx + 1) % 4) == 0) * 0.35, v)
            vena = memb & (((xx + 1) % 4) == 0) & (ys > 2)
        else:
            puntas = ((tw - 0.5, 0.5), (tw - 0.5, th * 0.62), (tw * 0.42, th - 0.5))
            dedo_d = np.full((th, tw), 99.0)
            ang = np.arctan2(y - 0.5, x - 0.5)
            for (px, py) in puntas:
                dx, dy = px - 0.5, py - 0.5
                L_ = math.hypot(dx, dy)
                t = np.clip(((x - 0.5) * dx + (y - 0.5) * dy) / (L_ * L_), 0, 1)
                d = np.hypot(x - 0.5 - t * dx, y - 0.5 - t * dy)
                dedo_d = np.minimum(dedo_d, d)
            hueso = dedo_d < 0.5
            # La membrana: entre el primer dedo (el borde de ataque) y el último; el borde, en arcos entre las puntas.
            angs = [math.atan2(py - 0.5, px - 0.5) for (px, py) in puntas]
            r_ = np.hypot(x - 0.5, y - 0.5)
            dentro = (ang >= angs[0] - 0.05) & (ang <= angs[-1] + 0.05)
            tope = np.zeros((th, tw))
            for k in range(len(puntas) - 1):
                a0, a1 = angs[k], angs[k + 1]
                r0 = math.hypot(puntas[k][0] - 0.5, puntas[k][1] - 0.5)
                r1 = math.hypot(puntas[k + 1][0] - 0.5, puntas[k + 1][1] - 0.5)
                f = np.clip((ang - a0) / max(1e-6, a1 - a0), 0, 1)
                en = (ang >= a0) & (ang <= a1)
                rr = r0 + (r1 - r0) * f
                rr = rr - min(2.2, 0.16 * max(tw, th)) * np.sin(f * math.pi)
                tope = np.where(en, rr, tope)
            memb = dentro & (r_ <= tope + 0.6) & ~hueso
            v = np.where(memb, 1.5 + r_ / max(tw, th) * 1.8 - (dedo_d < 1.3) * 0.3, v)
            vena = memb & (np.abs(np.sin(ang * 9.0)) < 0.18) & (r_ > 2.0)
            una = (xx == 0) & (ys == 0)
            hueso |= una
        v = np.where(hueso, 3.0 - ys * 0.03, v)
        rgb = L.color_continuo(r, v)
        rgb = np.where(hueso[..., None], L.color_continuo(rh, 2.6 + (xx % 3 == 0) * 0.5), rgb)
        a = (v > 0) | hueso
        tex = L._rgba(rgb)
        tex[..., 3] = np.where(a, 255, 0)
        emis = None
        if venas is not None:
            vv = vena & a & ~hueso
            tex[vv, :3] = np.clip(np.round(L.color_continuo(venas, np.full(vv.sum(), 3.2))), 0, 255)
            emis = np.zeros_like(tex)
            emis[vv] = tex[vv]
        return tex, emis
    return B.Pintor(nombre, fn)


def ala(m, padre, lado, ld, hombro, brazo, mano, cuerda, P_brazo, P_mano, diedro=24, barrido=16, pliegue=-14, atras=28):
    """Un ala de dos tramos desde el 'hombro': el brazo (de 'brazo' de largo) y la mano (de 'mano'), con su 'cuerda'.
    El ala se ve de frente (como en los carteles: la bomba viene hacia ti): el borde de ataque arriba y las plumas o la
    membrana colgando hacia abajo, echada hacia atrás ('atras'), hacia arriba ('diedro') y hacia atrás en planta
    ('barrido'), con la mano algo caída ('pliegue'). Cada tramo, su parte (el giro en Z la sube y la baja al batir)."""
    hombro = np.asarray(hombro, float)
    r0 = (0, lado * barrido, lado * diedro)
    n0 = m.parte(f'ala_{ld}0', padre, tuple(hombro), rot=r0)
    caras = {c: (P_brazo if c == 'frente' else None) for c in B.CARAS}
    M0 = T(*hombro) @ B.girar(r0)
    m._caja(n0, M0 @ T(lado * brazo / 2, 0, 0) @ Rx(-atras * B.D) @ T(0, -cuerda / 2 + 1.0, 0), -brazo / 2, -cuerda / 2,
            0.0, brazo, cuerda, 0.0, None, caras)
    punta = (M0 @ np.array((lado * brazo, 0.0, 0.0, 1.0)))[:3]
    r1 = (0, lado * (barrido + 8), lado * (diedro + pliegue))
    n1 = m.parte(f'ala_{ld}1', n0, tuple(punta), rot=r1)
    M1 = T(*punta) @ B.girar(r1)
    caras = {c: (P_mano if c == 'frente' else None) for c in B.CARAS}
    m._caja(n1, M1 @ T(lado * mano / 2, 0, 0) @ Rx(-atras * B.D) @ T(0, -cuerda / 2 + 1.0, 0), -mano / 2, -cuerda / 2,
            0.0, mano, cuerda, 0.0, None, caras)


def alas(m, tam, yc, pintores, brazo, mano, cuerda, diedro=24, barrido=16):
    """Las dos alas, de los cantos de arriba de los costados del cubo. 'pintores': ((brazo_i, mano_i), (brazo_d,
    mano_d))."""
    for (lado, ld), (pb, pm) in zip(((1, 'i'), (-1, 'd')), pintores):
        ala(m, 'cuerpo', lado, ld, (lado * tam / 2, yc + tam * 0.38, -tam * 0.15), brazo, mano, cuerda, pb, pm,
            diedro=diedro, barrido=barrido)


def pintores_pluma(nombre, r):
    return ((ala_pluma(f'{nombre}_brazo_i', r, 'brazo'), ala_pluma(f'{nombre}_mano_i', r, 'mano')),
            (ala_pluma(f'{nombre}_brazo_d', r, 'brazo', True), ala_pluma(f'{nombre}_mano_d', r, 'mano', True)))


def pintores_membrana(nombre, r, rh, venas=None):
    return ((ala_membrana(f'{nombre}_brazo_i', r, rh, 'brazo', venas=venas),
             ala_membrana(f'{nombre}_mano_i', r, rh, 'mano', venas=venas)),
            (ala_membrana(f'{nombre}_brazo_d', r, rh, 'brazo', True, venas),
             ala_membrana(f'{nombre}_mano_d', r, rh, 'mano', True, venas)))


# ======================================================================================================================
#  El cubo de la bomba (su material), la mecha y la chispa
# ======================================================================================================================
def cubo16(r, material, base=2.3, luz=0.9):
    """La piel del cubo de la bomba, al píxel de Minecraft, con su material: el tono que corre por la rampa (más claro
    arriba a la izquierda, de donde viene la luz), el bisel de un bloque (los cantos de arriba y de la izquierda más
    claros, los de abajo y la derecha más oscuros) y una mancha de brillo arriba a la izquierda. Y lo de cada material:
    'ambar', la hondura (el anillo de dentro del canto más oscuro), burbujitas y vetas claras de miel; 'lacado', la junta de
    través, los remaches de las esquinas y arañazos claros; 'hierro', placas con su junta y remaches, y los cantos
    gastados; 'sculk', las manchas oscuras, las motas de cian (alguna encendida) y las venas."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        a = _azar1(xs, ys, s)
        v = L.tono_suave(tw, th, cara, s, base, luz, 0.05, 3.0)
        v = v + (1.0 - (xs + ys) / max(1, tw + th - 2)) * 0.5
        borde = np.minimum(np.minimum(xs, ys), np.minimum(tw - 1 - xs, th - 1 - ys))
        claro = (ys == 0) | (xs == 0)
        oscuro = (ys == th - 1) | (xs == tw - 1)
        v = v + claro * 0.55 - oscuro * 0.6
        luz_a = np.zeros((th, tw))
        extra = None
        if material == 'ambar':
            v = v - (borde == 1) * 0.35
            burbuja = (a < 0.035) & (borde >= 2)
            v = np.where(burbuja, v + 1.3, v)
            v = np.where(np.roll(burbuja, 1, 0) & ~burbuja, v - 0.45, v)
            v = v + np.clip(np.sin((xs + ys * 0.6) * 0.7 + s) - 0.7, 0, 1) * 0.6
        elif material == 'lacado':
            junta = ys == int(th * 0.34)
            v = v - junta * 0.9 + (ys == int(th * 0.34) - 1) * 0.3
            esq = ((xs == 1) | (xs == tw - 2)) & ((ys == 1) | (ys == th - 2))
            v = np.where(esq, v + 1.2, v)
            v = np.where(np.roll(esq, 1, 0) & ~esq, v - 0.5, v)
            rasp = (a < 0.05) & (borde >= 2) & ~junta
            v = np.where(rasp, v + 0.7, v)
        elif material == 'hierro':
            junta = ((ys % 5) == 4) | ((xs % 7) == 6)
            v = v - junta * 0.8
            rem = ((ys % 5) == 1) & (((xs % 7) == 1) | ((xs % 7) == 4))
            v = np.where(rem, v + 1.3, v)
            v = np.where(np.roll(rem, 1, 0) & ~rem, v - 0.4, v)
            v = v + (borde == 0) * 0.35
        elif material == 'sculk':
            n = L._ruido(tw, th, s * 13 + 1, 2.5)
            v = v - (n > 0.62) * 0.8
            vena = np.abs(L._ruido(tw, th, s * 5 + 9, 3.0) - 0.5) < 0.05
            v = np.where(vena, v - 0.9, v)
            extra = (a < 0.07) & (n <= 0.62) & ~vena
            luz_a = ((a < 0.022) & (n <= 0.62) & ~vena).astype(float)
        if cara != 'abajo':
            d = np.hypot((xs + 0.5 - tw * 0.26) / max(1.2, tw * 0.13), (ys + 0.5 - th * 0.22) / max(1.2, th * 0.13))
            v = v + np.clip(1.25 - d, 0.0, 1.0) * 0.9
        rgb = L.color_continuo(r, v)
        if extra is not None:
            rgb = np.where(extra[..., None], L.color_continuo(v7.CIAN, np.full(v.shape, 0.9)), rgb)
        tex = L._rgba(rgb)
        if luz_a.any():
            return v7.encender(tex, luz_a, v7.CIAN, 3.0)
        return tex, None
    return fn


def cuerda16(quemada=False):
    """La mecha, al píxel de Minecraft: la cuerda gruesa trenzada y, si 'quemada', la punta negra de lo que ya ardió."""
    def fn(tw, th, cara, s):
        xs, ys = L._malla(tw, th)
        v = L.tono_suave(tw, th, cara, s, 2.4, 0.4, 0.05, 3.0)
        v = v - (((xs + ys) % 3) == 0) * 0.7
        rgb = L.color_continuo(CUERDA, v)
        if quemada:
            if cara == 'arriba':
                rgb[:] = L.color_continuo(HIERRO, np.full(rgb.shape[:2], 1.0))
            elif cara != 'abajo':
                rgb[0, :] = L.color_continuo(HIERRO, np.full(tw, 1.4))
        return L._rgba(rgb), None
    return fn


def bomba(m, piel, tam, pintores, brazo, mano, cuerda, mecha='arriba', mecha_largo=6.0, diedro=24, barrido=16):
    """La bomba: el cubo (de 'tam'), la tapa de piedra con la mecha gruesa en dos tramos (el segundo, quemado en la
    punta) y la chispa; y las dos alas. 'mecha': 'arriba' o 'atras'."""
    m.escala = 1.0
    yc = tam / 2 + 2.0
    m.parte('cuerpo', None, (0, yc, 0))
    m.caja('cuerpo', (0, yc, 0), (tam, tam, tam), piel)
    tapa = L.grueso('tapa_bomba', cubo16(PIEDRA, 'hierro', base=2.2, luz=0.4))
    ct = float(round(tam * 0.45))
    if mecha == 'arriba':
        top = yc + tam / 2
        m.caja_desde('cuerpo', (0, top - 0.01, 0), (ct, 2.0, ct), tapa)
        a = np.array((0.0, top + 2.0, 0.0))
        b = a + np.array((0.4, mecha_largo * 0.55, -0.6))
        c = b + np.array((2.2, mecha_largo * 0.4, -0.6))
        sube = np.array((0.0, 1.8, 0.0))
    else:
        zb = -tam / 2
        m.caja('cuerpo', (0, yc, zb - 1.0), (ct, ct, 2.0), tapa)
        a = np.array((0.0, yc, zb - 2.0))
        b = a + np.array((0.4, -0.8, -mecha_largo * 0.55))
        c = b + np.array((1.6, -2.2, -mecha_largo * 0.4))
        sube = np.array((0.0, 1.2, -1.0))
    m.parte('mecha', 'cuerpo', tuple(a))
    m.viga('mecha', a, b, 3.0, L.grueso('cuerda_bomba', cuerda16()), extra=0.6)
    m.viga('mecha', b, c, 2.6, L.grueso('cuerda_quemada_bomba', cuerda16(quemada=True)), extra=0.4)
    m.parte('chispa', 'mecha', tuple(c))
    chispa = L.llama('chispa_bomba', CHISPA)
    for rot in ((0, 0, 0), (0, 90, 0)):
        m.hoja('chispa', tuple(c + sube), 4.0, 5.0, chispa, rot=rot)
    m.caja('chispa', tuple(c), (1.6, 1.6, 1.6), L.luz_suave('nucleo_chispa', CHISPA))
    alas(m, tam, yc, pintores, brazo, mano, cuerda, diedro=diedro, barrido=barrido)


def anims_bomba(m, aleteo=0.36, amp=34):
    """siempre: las alas baten (el brazo sube y baja y la mano le sigue con retraso, doblándose), el cubo sube y baja y
    se mece, y la chispa parpadea; especial (la mecha encendida): tiembla y se hincha; hinchado: la chispa crece con la
    mecha; muerte: cae dando vueltas con las alas plegadas."""
    s = m.anim('siempre', 2.16, bucle=True)
    for lado, ld in ((1, 'i'), (-1, 'd')):
        s.onda(f'ala_{ld}0', 'r', 2, amp * lado, periodo=aleteo)
        s.onda(f'ala_{ld}1', 'r', 2, amp * 0.7 * lado, periodo=aleteo, fase=0.18)
    s.onda('cuerpo', 'm', 1, 0.9, periodo=aleteo)
    s.onda('cuerpo', 'r', 2, 4, periodo=2.16, fase=0.2)
    s.esc('chispa', [(0, 1, 1, 1), (0.1, 1.4, 1.4, 1.4), (0.2, 0.8, 0.8, 0.8), (0.3, 1.3, 1.3, 1.3), (0.45, 0.9, 0.9, 0.9),
                     (0.6, 1.2, 1.2, 1.2), (0.8, 1, 1, 1), (2.16, 1, 1, 1)])
    s.onda('mecha', 'r', 2, 6, periodo=0.54)
    e = m.anim('especial', 1.0)
    e.esc('cuerpo', [(0, 1, 1, 1), (0.1, 1.08, 0.94, 1.08), (0.2, 0.96, 1.06, 0.96), (0.3, 1.12, 0.92, 1.12),
                     (0.4, 0.97, 1.05, 0.97), (0.5, 1.15, 0.9, 1.15), (0.6, 1.0, 1.04, 1.0), (0.75, 1.2, 0.9, 1.2),
                     (1.0, 1.25, 0.95, 1.25)])
    h = m.anim('hinchado', 1.0)
    h.esc('chispa', [(0, 1, 1, 1), (1.0, 2.6, 2.6, 2.6)])
    d = m.anim('muerte', 1.0)
    d.rot('cuerpo', [(0, 0, 0, 0), (0.4, 80, 0, 30), (1.0, 170, 0, 60)])
    d.mov('cuerpo', [(0, 0, 0, 0), (1.0, 0, -6, 0)])
    for lado, ld in ((1, 'i'), (-1, 'd')):
        d.rot(f'ala_{ld}0', [(0, 0, 0, 0), (0.5, 0, 0, -lado * 50), (1.0, 0, 0, -lado * 70)])
        d.rot(f'ala_{ld}1', [(0, 0, 0, 0), (0.5, 0, 0, -lado * 60), (1.0, 0, 0, -lado * 90)])


def huevo_bomba(px, filas, c, piel, ala, motas=()):
    for f in range(2, 15):
        a, b = filas[f]
        for x in range(a + 1, b):
            px[x, f] = c(piel)
    for x, f in ((2, 5), (2, 6), (3, 6), (13, 5), (13, 6), (12, 6)):
        px[x, f] = c(ala)
    for x in range(6, 10):
        px[x, 2] = c('74757b')
    for x, f in ((7, 1), (8, 1), (8, 0), (9, 0)):
        px[x, f] = c('b49c7c')
    px[10, 0] = c('ffc23a')
    for x, y, col in motas:
        px[x, y] = c(col)


# ======================================================================================================================
#  Las cuatro bombas
# ======================================================================================================================
AMBAR = rampa('5a2e04', '9a5a0a', 'd08a16', 'f4ba3a', 'fff09a')
ORO_PLUMA = rampa('5a3606', '9a620e', 'd09a20', 'f2c84a', 'fff2a8')
ROJO = rampa('4a0a0a', '761212', 'a61c1c', 'd02e28', 'f06450')
MEMBRANA_R = rampa('2a0606', '4a0c0e', '701418', '962024', 'b8343a')
NEGRO = rampa('0a0b0e', '15171c', '21242b', '30353f', '4a5466')
CUERVO = rampa('06070c', '10121c', '1c2030', '2c3450', '465482')
SCULK = rampa('061418', '0a2026', '102e36', '183e48', '224e5a')


def ambar(raiz):
    m = B.Modelo('ambar', K=2, ancho=128)
    bomba(m, L.grueso('piel_ambar', cubo16(AMBAR, 'ambar')), 12.0, pintores_pluma('ala_ambar', ORO_PLUMA),
          brazo=10.0, mano=12.0, cuerda=9.0)
    anims_bomba(m)

    def dib(px, filas, c):
        huevo_bomba(px, filas, c, 'd08a16', 'f2c84a', motas=((5, 5, 'fff09a'), (9, 9, '5a2e04')))
    return bc.terminar(m, raiz, 'Bomba Ámbar', 'Amber Bomb', (('fff09a', 'f4ba3a', '9a5a0a'), ('f2c84a', '5a2e04'), dib),
                       ((1.6, 1.3, 2.2), (0, 0.6, 0)),
                       particulas=(('vapor', bc.anillo((210, 230, 240))), ('chispa', bc.chispa((255, 194, 58))),
                                   ('cristal', bc.esquirla((210, 162, 26)))))


def carmesi(raiz):
    m = B.Modelo('carmesi', K=2, ancho=128)
    bomba(m, L.grueso('piel_carmesi', cubo16(ROJO, 'lacado')), 11.0,
          pintores_membrana('ala_carmesi', MEMBRANA_R, HIERRO), brazo=9.0, mano=12.0, cuerda=10.0, diedro=30, barrido=20)
    anims_bomba(m, aleteo=0.27)

    def dib(px, filas, c):
        huevo_bomba(px, filas, c, 'a61c1c', '701418', motas=((5, 5, 'f06450'), (4, 4, '464b52'), (11, 4, '464b52')))
    return bc.terminar(m, raiz, 'Bomba Carmesí', 'Crimson Bomb', (('f06450', 'd02e28', '761212'), ('701418', '2a0606'), dib),
                       ((1.6, 1.3, 2.2), (0, 0.55, 0)),
                       particulas=(('brasa', bc.chispa((255, 138, 26))), ('esquirla', bc.esquirla((154, 28, 28)))))


def negra(raiz):
    m = B.Modelo('negra', K=2, ancho=128)
    bomba(m, L.grueso('piel_negra', cubo16(NEGRO, 'hierro', base=2.2, luz=0.7)), 15.0, pintores_pluma('ala_negra', CUERVO),
          brazo=12.0, mano=15.0, cuerda=11.0, mecha_largo=7.0, diedro=20, barrido=14)
    anims_bomba(m, aleteo=0.54, amp=28)

    def dib(px, filas, c):
        huevo_bomba(px, filas, c, '21242b', '2c3450', motas=((5, 5, '4a5466'), (5, 9, '30353f'), (10, 9, '30353f')))
    return bc.terminar(m, raiz, 'Bomba Negra', 'Black Bomb', (('4a5466', '30353f', '15171c'), ('2c3450', '0a0b0e'), dib),
                       ((2.0, 1.7, 2.7), (0, 0.75, 0)),
                       particulas=(('humo', bc.esquirla((60, 64, 70))), ('esquirla', bc.esquirla((52, 56, 62)))))


def abismo(raiz):
    m = B.Modelo('abismo', K=2, ancho=128)
    bomba(m, L.grueso('piel_abismo', cubo16(SCULK, 'sculk', base=2.0, luz=0.6)), 12.0,
          pintores_membrana('ala_abismo', SCULK, rampa('1a2e2a', '2e4a44', '4a6e64', '6e968a', 'a0c6ba'), venas=v7.CIAN),
          brazo=9.0, mano=12.0, cuerda=10.0, mecha='atras', diedro=26, barrido=18)
    anims_bomba(m, aleteo=0.36)

    def dib(px, filas, c):
        huevo_bomba(px, filas, c, '102e36', '2e4a44', motas=((5, 6, '3ad8ff'), (10, 10, '3ad8ff'), (8, 4, '183e48')))
    return bc.terminar(m, raiz, 'Bomba del Abismo', 'Abyss Bomb', (('224e5a', '183e48', '102e36'), ('3ad8ff', '040e12'), dib),
                       ((1.6, 1.5, 2.2), (0, 0.7, 0)),
                       particulas=(('alma', bc.chispa((58, 216, 255))), ('sculk', bc.esquirla((20, 58, 68)))))


MOBS = {'ambar': ambar, 'carmesi': carmesi, 'negra': negra, 'abismo': abismo}


def main():
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    carpeta = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(MOBS)
    # El píxel de Minecraft (16 por bloque): las bombas van a escala 1, así que es de 1 píxel del modelo.
    B.TEXEL = 1.0
    hechos = [MOBS[p](raiz) for p in pedidos]
    B.TEXEL = None
    if carpeta:
        import bestiario_escenas as be
        os.makedirs(carpeta, exist_ok=True)
        sitios = {'ambar': 'noche', 'carmesi': 'nether', 'negra': 'noche', 'abismo': 'cueva'}
        for mm in hechos:
            be.heroe(mm, sitios[mm.id], os.path.join(carpeta, f'{mm.id}_heroe.jpg'), alto=1.4)
        if len(hechos) > 1:
            be.fila([(mm, None, 0.0) for mm in hechos], 'noche', os.path.join(carpeta, 'bombas_juntas.jpg'), separa=2.8)


if __name__ == '__main__':
    main()

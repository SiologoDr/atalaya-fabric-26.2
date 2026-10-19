"""
Los iconos de los momentos (momento/<id>, 16 x 16): en rojo fractura lo que amenaza y, si hay que ponerse a salvo, hacia
dónde. Se apuntan en catalogo_iconos.ICONOS al importar este módulo (lo hace catalogo.py).
"""
import math

import numpy as np

import catalogo_iconos as ci
import catalogo_piezas as cp
import menus_cambios as mc
from catalogo_iconos import (ICONOS, OSCURO, R_AGUA, R_BLANCO, R_FUEGO, R_GAS, R_PIEDRA, R_ROJO, R_ZOMBI, calavera,
                             cara_creeper, cara_zombi, cifras, corazon, flecha, gota, llama, luna, nube, nuevo, ojo, rayo,
                             reloj, sol, tachado)
from ruleta import H, Lienzo, esfera, rampa, sd_caja, sd_circulo, sd_elipse, sd_poligono, sd_segmento, tono, union

R_FRACTURA = rampa('3a0408', '7a0a12', 'c01a22', 'f04a40', 'ffb0a0')


def icono(nombre):
    def reg(fn):
        ICONOS['momento/' + nombre] = fn
        return fn
    return reg


def capa(n):
    return Lienzo(n)


# ------------------------------------------------------------------------------------------------------------
#  Ponte a salvo
# ------------------------------------------------------------------------------------------------------------
@icono('gas_que_sube')
def _(n=16):
    x, y, k, L = nuevo(n)
    nube(L, x, y, k, cx=14, cy=22, rampa_=R_GAS)
    flecha(L, x, y, arriba=True, cx=24, cy=9, color='e0ff9a')
    return L


@icono('gas_que_baja')
def _(n=16):
    x, y, k, L = nuevo(n)
    nube(L, x, y, k, cx=14, cy=10, rampa_=R_GAS)
    flecha(L, x, y, arriba=False, cx=24, cy=22, color='e0ff9a')
    return L


@icono('la_franja')
def _(n=16):
    x, y, k, L = nuevo(n)
    nube(L, x, y, k, cx=16, cy=6, rampa_=R_GAS, esc=0.8)
    T = capa(n)
    nube(T, x, y, k, cx=16, cy=27, rampa_=R_GAS, esc=0.8)
    L.encima(T)
    L.pintar((np.abs(y - 16.5) < 2.4) & (np.abs(x - 16) < 13), H('fff2b0')[:3])
    L.contorno(OSCURO)
    return L


@icono('el_rayo')
def _(n=16):
    x, y, k, L = nuevo(n)
    nube(L, x, y, k, cx=16, cy=8, rampa_=rampa('1a1a2a', '2e2e44', '4a4a66', '6a6a8a', '9a9ab8'))
    T = capa(n)
    rayo(T, x, y, k, cx=16, cy=21, esc=0.75)
    L.encima(T)
    return L


@icono('lluvia_de_meteoritos')
def _(n=16):
    x, y, k, L = nuevo(n)
    for (ax, ay, bx, by, r) in ((4, 2, 14, 14, 4.5), (18, 2, 26, 11, 3.2), (12, 18, 18, 26, 3.0)):
        estela = sd_segmento(x, y, ax, ay, bx, by, r * 0.5)
        L.pintar(estela < 0, H('ffc84a')[:3])
        L.pintar(sd_circulo(x, y, bx, by, r) < 0, tono(rampa('3a1a0a', '6a3014', 'a85a24', 'e08a3a', 'ffd08a'),
                                                       esfera(x, y, bx - 1, by - 1, r, r, amb=0.3)))
    L.contorno(H('3a0a02')[:3])
    return L


@icono('el_agujero_negro')
def _(n=16):
    x, y, k, L = nuevo(n)
    rr = np.hypot(x - 16, y - 16)
    ang = np.arctan2(y - 16, x - 16)
    espiral = (np.sin(ang * 2 + rr * 0.5) > 0.2) & (rr < 14) & (rr > 6)
    L.pintar(espiral, tono(rampa('2a0a4a', '5a1aa0', '8a3ae0', 'c080ff', 'f0d8ff'), np.clip(1 - rr / 14, 0, 1)))
    L.pintar(rr < 6.5, H('020104')[:3])
    L.pintar(np.abs(rr - 6.5) < 0.7, H('f0d8ff')[:3])
    L.contorno(OSCURO)
    return L


@icono('la_supernova')
def _(n=16):
    x, y, k, L = nuevo(n)
    for i in range(12):
        a = math.tau * i / 12
        largo = 14 if i % 2 == 0 else 9
        L.pintar(sd_segmento(x, y, 16, 16, 16 + math.cos(a) * largo, 16 + math.sin(a) * largo, 1.2) < 0, H('fff6d0')[:3])
    L.pintar(sd_circulo(x, y, 16, 16, 6) < 0, tono(rampa('ffd23a', 'fff070', 'fffcd0', 'ffffff'), esfera(x, y, 15, 15, 6, 6, amb=0.6)))
    L.contorno(H('5a3a04')[:3])
    return L


@icono('luna_de_sangre')
def _(n=16):
    x, y, k, L = nuevo(n)
    L.pintar(sd_circulo(x, y, 16, 16, 12) < 0, tono(R_FRACTURA, esfera(x, y, 12, 12, 12, 12, amb=0.3)))
    for cx, cy, r in ((12, 12, 2.5), (20, 18, 3.0), (14, 21, 1.8)):
        L.pintar(sd_circulo(x, y, cx, cy, r) < 0, H('5a0a10')[:3])
    L.contorno(OSCURO)
    return L


@icono('tormenta_marchita')
def _(n=16):
    x, y, k, L = nuevo(n)
    nube(L, x, y, k, cx=16, cy=9, rampa_=rampa('0a0a0e', '1a1a22', '2a2a36', '3e3e4e', '5a5a6e'))
    T = capa(n)
    calavera(T, x, y, k, cx=16, cy=22, esc=0.55, rampa_=rampa('0a0a0e', '18181e', '2a2a32', '3e3e48', '5a5a66'), ojos='e8e8f0')
    L.encima(T)
    return L


@icono('bajo_el_agua')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.onda(L, x, y, k, cy=10)
    T = capa(n)
    cp.persona(T, x, y, k, cx=16, base=31, esc=0.75)
    T.a *= 0.7
    L.encima(T)
    cp.burbujas(L, x, y, k, puntos=((24, 16, 2.2), (26, 22, 1.6)))
    return L


@icono('el_encadenado')
def _(n=16):
    x, y, k, L = nuevo(n)
    for cx, cy in ((9, 9), (16, 16), (23, 23)):
        aro = np.abs(sd_elipse(x, y, cx, cy, 5.5, 3.5)) - 1.3
        L.pintar(aro < 0, tono(rampa('3a3e48', '6a707c', 'a0a6b2', 'd2d6de', 'f6f8fc'), np.clip(0.7 - (y - cy) * 0.05, 0, 1)))
    L.contorno(OSCURO)
    return L


# ------------------------------------------------------------------------------------------------------------
#  Pruebas
# ------------------------------------------------------------------------------------------------------------
@icono('la_gran_caza')
def _(n=16):
    x, y, k, L = nuevo(n)
    cara_zombi(L, x, y, k, cx=12, cy=13, lado=8)
    T = capa(n)
    cp.espada(T, x, y, k, a=(8, 30), b=(28, 10))
    L.encima(T)
    return L


@icono('el_grito_del_abismo')
def _(n=16):
    x, y, k, L = nuevo(n)
    base = sd_caja(x, y, 16, 24, 11, 4, 1)
    L.pintar(base < 0, tono(rampa('041014', '08222a', '0e3a46', '18606e', '3ab0c0'), np.clip(0.5 - (y - 24) * 0.05, 0, 1)))
    boca = sd_caja(x, y, 16, 15, 7, 6, 1)
    L.pintar(boca < 0, H('e8e0c8')[:3])
    L.pintar(sd_caja(x, y, 16, 15, 4, 3, 0.5) < 0, H('3ae8f0')[:3])
    for i in range(3):
        aro = np.abs(sd_circulo(x, y, 16, 15, 9 + i * 3.5)) - 0.6
        L.pintar((aro < 0) & (y < 12), H('3ab0c0')[:3])
    L.contorno(OSCURO)
    return L


@icono('la_prueba_de_la_tierra')
def _(n=16):
    x, y, k, L = nuevo(n)
    ci.bloque(L, x, y, k, ci.R_TIERRA, vetas=lambda x, y: ((np.floor(x / 4) + np.floor(y / 3)) % 3 == 0) * 0.15)
    L.pintar((y < 9) & L.lleno(), ci.R_HIERBA[2])
    T = capa(n)
    reloj(T, x, y, k, cx=25, cy=25, r=6.5)
    L.encima(T)
    return L


# ------------------------------------------------------------------------------------------------------------
#  Mientras dura
# ------------------------------------------------------------------------------------------------------------
ICONOS['momento/vida_a_medias'] = mc.icono_vida


@icono('la_oscuridad')
def _(n=16):
    x, y, k, L = nuevo(n)
    ojo(L, x, y, k, iris=rampa('0a0a0e', '18181e', '2a2a32', '3e3e48', '5a5a66'))
    L.pintar((y < 16) & L.lleno(), H('0a0812')[:3])
    L.contorno(OSCURO)
    return L


@icono('nada_frena_la_caida')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.persona(L, x, y, k, cx=16, base=24, esc=0.7)
    flecha(L, x, y, arriba=False, cx=16, cy=27, color='ff7a60')
    return L


@icono('sequia')
def _(n=16):
    x, y, k, L = nuevo(n)
    cubo = sd_poligono(x, y, [(7, 10), (25, 10), (22, 28), (10, 28)])
    L.pintar(cubo < 0, tono(ci.R_HIERRO, np.clip(0.7 - (x - 16) * 0.03, 0, 1)))
    L.pintar(sd_elipse(x, y, 16, 10, 9, 2.2) < 0, H('3a2a1a')[:3])
    L.contorno(OSCURO)
    tachado(L, x, y)
    return L


@icono('el_intercambio')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.persona(L, x, y, k, cx=8, base=30, esc=0.6)
    T = capa(n)
    cp.persona(T, x, y, k, cx=24, base=30, esc=0.6, ropa=rampa('5a1a1a', 'a02a2a', 'd84a3a', 'f08a6a', 'ffc8b0'))
    L.encima(T)
    for a, b, s in (((9, 6), (23, 6), 1), ((23, 9), (9, 9), -1)):
        L.pintar(sd_segmento(x, y, *a, *b, 0.9) < 0, H('fff2b0')[:3])
    L.contorno(OSCURO)
    return L


@icono('todos_diminutos')
def _(n=16):
    x, y, k, L = nuevo(n)
    for cx in (8, 16, 24):
        cp.persona(L, x, y, k, cx=cx, base=30, esc=0.45)
    flecha(L, x, y, arriba=False, cx=16, cy=7, color='fff2b0')
    return L


@icono('la_infeccion')
def _(n=16):
    x, y, k, L = nuevo(n)
    nube(L, x, y, k, cx=16, cy=12, rampa_=rampa('1e4a14', '3a7a22', '5aae34', '9ad864', 'd8ffb0'))
    T = capa(n)
    calavera(T, x, y, k, cx=16, cy=22, esc=0.5, rampa_=rampa('1e4a14', '3a7a22', '5aae34', '9ad864', 'd8ffb0'), ojos='0e1a08')
    L.encima(T)
    return L


@icono('el_eclipse')
def _(n=16):
    x, y, k, L = nuevo(n)
    for i in range(8):
        a = math.tau * i / 8
        L.pintar(sd_segmento(x, y, 16 + math.cos(a) * 9, 16 + math.sin(a) * 9, 16 + math.cos(a) * 14, 16 + math.sin(a) * 14, 1.3) < 0,
                 H('ffc84a')[:3])
    L.pintar(sd_circulo(x, y, 16, 16, 8.5) < 0, H('ffe08a')[:3])
    L.pintar(sd_circulo(x, y, 17.5, 15, 8.0) < 0, H('0a0812')[:3])
    L.contorno(OSCURO)
    return L


# ------------------------------------------------------------------------------------------------------------
#  Sucesos
# ------------------------------------------------------------------------------------------------------------
@icono('lluvia_de_creepers')
def _(n=16):
    x, y, k, L = nuevo(n)
    cara_creeper(L, x, y, k, cx=11, cy=11, lado=7, cargado=True)
    T = capa(n)
    cara_creeper(T, x, y, k, cx=22, cy=22, lado=7, cargado=True)
    L.encima(T)
    return L


@icono('cualquier_cosa')
def _(n=16):
    x, y, k, L = nuevo(n)
    from ruleta import sd_interrogacion
    L.pintar(sd_circulo(x, y, 16, 16, 13) < 0, tono(R_FRACTURA, esfera(x, y, 12, 12, 13, 13, amb=0.35)))
    L.pintar(sd_interrogacion(x, y, 16, 16, 18, 2.4) < 0, H('ffe0d8')[:3])
    L.contorno(OSCURO)
    return L


@icono('tornados')
def _(n=16):
    x, y, k, L = nuevo(n)
    for i in range(6):
        cy = 5 + i * 4.2
        ancho = 12 - i * 1.6
        L.pintar(sd_caja(x, y, 16 + (i % 2) * 1.5 - 0.7, cy, ancho, 1.4, 1.2) < 0, tono(rampa('6a7a8a', '9aa8b8', 'c8d4e0', 'eef4fa'),
                                                                                    np.full_like(x, 0.4 + (i % 3) * 0.2)))
    L.contorno(OSCURO)
    return L


@icono('el_cielo_arde')
def _(n=16):
    x, y, k, L = nuevo(n)
    L.pintar(sd_caja(x, y, 16, 9, 14, 8, 2) < 0, tono(rampa('5a1a04', 'a03a0a', 'e07a1a', 'ffb84a', 'fff0b0'),
                                                    np.clip(0.7 - (y - 4) * 0.05, 0, 1)))
    T = capa(n)
    llama(T, x, y, k, cx=10, base=31, alto=13, ancho=6)
    llama(T, x, y, k, cx=22, base=31, alto=15, ancho=7)
    L.encima(T)
    return L


@icono('cambio_de_cuerpos')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.persona(L, x, y, k, cx=10, base=30, esc=0.7)
    T = capa(n)
    cp.persona(T, x, y, k, cx=22, base=30, esc=0.7, ropa=rampa('3a1a5a', '5a2aa0', '8a4ad0', 'b08af0', 'd8c8ff'))
    L.encima(T)
    for a, b in (((8, 3), (24, 3)),):
        L.pintar(sd_segmento(x, y, *a, *b, 0.9) < 0, H('fff2b0')[:3])
        L.pintar(sd_poligono(x, y, [(24, 0.5), (28, 3), (24, 5.5)]) < 0, H('fff2b0')[:3])
        L.pintar(sd_poligono(x, y, [(8, 0.5), (4, 3), (8, 5.5)]) < 0, H('fff2b0')[:3])
    return L


@icono('la_horda')
def _(n=16):
    x, y, k, L = nuevo(n)
    for cx, cy, l in ((8, 12, 6), (24, 12, 6), (16, 21, 8)):
        T = capa(n)
        cara_zombi(T, x, y, k, cx=cx, cy=cy, lado=l)
        L.encima(T)
    return L

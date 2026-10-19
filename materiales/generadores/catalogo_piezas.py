"""
Más piezas para los iconos del catálogo (catalogo_iconos.py): botas, muslos, pulmones, caras de mobs de siempre,
armas, bloques... todas en el cuadro de 32 unidades del pincel de ruleta.py.
"""
import math

import numpy as np

import menus_cambios as mc
from catalogo_iconos import (OSCURO, ORO, R_AGUA, R_BLANCO, R_FUEGO, R_GAS, R_HIERRO, R_HUESO, R_MADERA, R_PIEDRA,
                             R_ROJO, R_TIERRA, R_VERDE, luna, nube)
from ruleta import H, Lienzo, bisel, esfera, rampa, sd_caja, sd_circulo, sd_corazon, sd_elipse, sd_poligono, sd_segmento, tono, union

R_CARNE = rampa('5a1410', '9a2a1e', 'c8503a', 'e88a6a', 'ffd0b8')
R_PIEL = rampa('5a3a24', '8a5e3c', 'b8865a', 'deb284', 'f8dcb4')
R_WARDEN = rampa('04161c', '0a2e38', '125060', '1e7a8a', '4ac8d0')
R_PIGLIN = rampa('6a3a2a', 'a05a44', 'd08870', 'f0b8a0', 'ffe4d4')
R_GRIS = rampa('1a1a20', '2e2e36', '4a4a54', '70707c', 'a8a8b4')
R_NIEVE = rampa('3a5a7a', '6a90b0', 'a8c8e0', 'dcecf8', 'ffffff')
R_SCULK2 = rampa('041014', '08222a', '0e3a46', '18606e', '3ab0c0')


def bota(L, x, y, k, cx=14.0, cy=16.0, rampa_=R_MADERA):
    d = union(sd_caja(x, y, cx, cy - 3, 4.5, 8, 1.5), sd_caja(x, y, cx + 4, cy + 6, 8.5, 3.2, 1.5))
    L.pintar(d < 0, tono(rampa_, esfera(x, y, cx - 2, cy - 6, 10, 12, amb=0.35)))
    L.pintar(sd_caja(x, y, cx + 4, cy + 9, 8.5, 0.9) < 0, rampa_[0])
    L.contorno(OSCURO)


def grietas(L, x, y, color='ffffff'):
    """Unas grietas finas (cristal roto) encima de lo pintado."""
    m = np.zeros_like(x, bool)
    for a, b in (((9, 6), (14, 13)), ((14, 13), (11, 20)), ((14, 13), (20, 15)), ((20, 15), (24, 22))):
        m |= sd_segmento(x, y, *a, *b, 0.55) < 0
    L.pintar(m & L.lleno(), H(color)[:3])


def muslo(L, x, y, k, cx=15.0, cy=17.0, rampa_=R_CARNE):
    carne = sd_elipse(x, y, cx - 1, cy - 2, 8, 7.5)
    L.pintar(carne < 0, tono(rampa_, esfera(x, y, cx - 4, cy - 6, 9, 9, amb=0.3)))
    hueso = union(sd_segmento(x, y, cx + 4, cy + 3, cx + 9, cy + 9, 1.6), sd_circulo(x, y, cx + 9.5, cy + 8, 1.9),
                  sd_circulo(x, y, cx + 8, cy + 10.5, 1.9))
    L.pintar(hueso < 0, tono(R_HUESO, np.clip(0.7 - (x - cx) * 0.02, 0, 1)))
    L.contorno(OSCURO)


def burbujas(L, x, y, k, puntos=((11, 22, 4.2), (20, 13, 3.4), (12, 8, 2.4)), rampa_=R_AGUA):
    for cx, cy, r in puntos:
        aro = np.abs(sd_circulo(x, y, cx, cy, r)) - 0.9
        L.pintar(aro < 0, rampa_[3])
        L.pintar(sd_circulo(x, y, cx - r * 0.35, cy - r * 0.35, r * 0.28) < 0, H('ffffff')[:3])
    L.contorno(H('041a3a')[:3])


def pulmones(L, x, y, k, cx=16.0, cy=17.0, rampa_=rampa('6a1a2a', 'a83a4a', 'd86a7a', 'f4a4b0', 'ffe0e6')):
    for lado in (-1, 1):
        d = sd_elipse(x, y, cx + lado * 5.5, cy + 1, 5, 8.5)
        L.pintar(d < 0, tono(rampa_, esfera(x, y, cx + lado * 5.5 - 2, cy - 3, 6, 9, amb=0.3)))
    L.pintar(sd_caja(x, y, cx, cy - 8, 1.3, 4) < 0, rampa_[2])
    L.contorno(OSCURO)


def venda(L, x, y, k, cx=16.0, cy=15.0):
    d = sd_caja(x, y, cx, cy, 11, 4, 1.5)
    L.pintar(d < 0, tono(R_BLANCO, np.clip(0.75 - (y - cy) * 0.04, 0, 1)))
    L.pintar((d < 0) & (np.abs(x - cx) < 4), H('e8322a')[:3])
    L.contorno(OSCURO)


def estandarte(L, x, y, k, cx=16.0):
    """El mal presagio: el estandarte de los saqueadores (tela blanca con la cara gris)."""
    L.pintar(sd_caja(x, y, cx, 4, 10, 1.3) < 0, R_MADERA[2])
    tela = sd_poligono(x, y, [(cx - 8, 5), (cx + 8, 5), (cx + 8, 26), (cx, 30), (cx - 8, 26)])
    L.pintar(tela < 0, tono(R_BLANCO, np.clip(0.8 - (x - cx) * 0.02, 0, 1)))
    L.pintar(sd_caja(x, y, cx, 16, 5, 6, 1) < 0, H('6a6a74')[:3])
    for lado in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado * 2.5, 14, 1.4, 0.8) < 0, H('1a1a20')[:3])
    L.pintar(sd_caja(x, y, cx, 19, 3, 0.7) < 0, H('1a1a20')[:3])
    L.contorno(OSCURO)


def persona(L, x, y, k, cx=16.0, base=30.0, esc=1.0, piel=R_PIEL,
            ropa=rampa('1a3a6a', '2a5aa0', '3a7ad0', '6aa4f0', 'a8d0ff')):
    """Un jugador de cuerpo entero, de frente."""
    s = esc
    L.pintar(sd_caja(x, y, cx, base - 23 * s, 4 * s, 4 * s, 0.5) < 0, piel[3])
    L.pintar(sd_caja(x, y, cx, base - 25.5 * s, 4 * s, 1.6 * s) < 0, H('3a2410')[:3])
    L.pintar(sd_caja(x, y, cx, base - 13 * s, 4 * s, 6 * s, 0.5) < 0, ropa[2])
    for lado in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado * 6 * s, base - 13 * s, 1.8 * s, 6 * s, 0.5) < 0, piel[2])
        L.pintar(sd_caja(x, y, cx + lado * 2 * s, base - 3.5 * s, 1.9 * s, 3.5 * s, 0.3) < 0, H('3a3a5a')[:3])
    L.contorno(OSCURO)


def espada(L, x, y, k, a=(7, 25), b=(25, 7), rampa_=R_HIERRO):
    hoja = sd_segmento(x, y, a[0] + 3, a[1] - 3, b[0], b[1], 1.8)
    L.pintar(hoja < 0, rampa_[3])
    L.pintar(sd_segmento(x, y, a[0] + 1, a[1] - 5, a[0] + 5, a[1] - 1, 1.3) < 0, H('5e3c18')[:3])
    L.pintar(sd_segmento(x, y, a[0], a[1], a[0] + 2.5, a[1] - 2.5, 1.4) < 0, H('8a5a26')[:3])
    L.contorno(OSCURO)


def escudo(L, x, y, k, cx=16.0, cy=16.0):
    d = sd_poligono(x, y, [(cx - 9, cy - 11), (cx + 9, cy - 11), (cx + 9, cy + 3), (cx, cy + 12), (cx - 9, cy + 3)])
    L.pintar(d < 0, tono(R_MADERA, bisel(d, k, 2 * k, base=0.6)))
    L.pintar((d < 0) & (d > -1.6), R_HIERRO[2])
    L.pintar(sd_caja(x, y, cx, cy - 1, 1.2, 8) < 0, R_HIERRO[3])
    L.contorno(OSCURO)


def pico(L, x, y, k, rampa_=rampa('1a6a6a', '2aa0a0', '5ad8d0', 'a8fff4', 'e8fffc')):
    L.pintar(sd_segmento(x, y, 8, 26, 22, 12, 1.4) < 0, H('8a5a26')[:3])
    cabeza = union(sd_segmento(x, y, 10, 8, 18, 6, 2.0), sd_segmento(x, y, 18, 6, 26, 14, 2.0))
    L.pintar(cabeza < 0, rampa_[2])
    L.contorno(OSCURO)


def jaula(L, x, y, k, cx=16.0, cy=16.0, lado=11.0):
    m = np.zeros_like(x, bool)
    caja = sd_caja(x, y, cx, cy, lado, lado, 0.5)
    m |= (caja < 0) & (caja > -1.6)
    for i in (-5, 0, 5):
        m |= (np.abs(x - cx - i) < 0.8) & (caja < 0)
        m |= (np.abs(y - cy - i) < 0.8) & (caja < 0)
    L.pintar(caja < 0, H('1a1424')[:3])
    L.pintar(sd_circulo(x, y, cx, cy, 4.5) < 0, tono(R_FUEGO, esfera(x, y, cx - 1, cy - 1, 4.5, 4.5, amb=0.4)))
    L.pintar(m, R_GRIS[3])
    L.contorno(OSCURO)


def calabaza(L, x, y, k, cx=16.0, cy=17.0, dormida=True):
    d = sd_elipse(x, y, cx, cy, 12, 10)
    gajos = (np.abs(np.sin((x - cx) * 0.42)) < 0.18)
    L.pintar(d < 0, tono(rampa('6a2a04', 'a84a0a', 'e07a1a', 'f8a840', 'ffd890'),
                         np.clip(0.6 - gajos * 0.25 - (x - cx) * 0.012, 0, 1)))
    L.pintar(sd_caja(x, y, cx, cy - 11, 1.5, 2.5) < 0, H('3a5a1a')[:3])
    if dormida:
        for lado in (-1, 1):
            L.pintar(sd_caja(x, y, cx + lado * 5, cy - 1, 2.6, 0.7) < 0, H('3a1a04')[:3])
        L.pintar(sd_caja(x, y, cx, cy + 5, 4, 0.7) < 0, H('3a1a04')[:3])
    L.contorno(OSCURO)


def cara_aldeano(L, x, y, k, cx=16.0, cy=16.0, lado=10.0, rampa_=R_PIEL):
    cara = sd_caja(x, y, cx, cy, lado * 0.8, lado, 1.0)
    L.pintar(cara < 0, tono(rampa_, np.clip(0.6 - (x - cx) * 0.02, 0, 1)))
    L.pintar(sd_caja(x, y, cx, cy - lado * 0.85, lado * 0.8, lado * 0.25) < 0, H('5e3c18')[:3])
    for lado_ in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado_ * 3.5, cy - 1.5, 1.6, 1.2) < 0, H('3a8a3a')[:3])
    L.pintar(sd_caja(x, y, cx, cy + 3, 1.8, 4) < 0, rampa_[1])
    L.pintar(sd_caja(x, y, cx, cy - 4.2, 4.5, 0.7) < 0, H('3a240e')[:3])
    L.contorno(OSCURO)


def sombrero_bruja(L, x, y, k, cx=16.0, base=12.0):
    ala = sd_caja(x, y, cx, base, 11, 1.6, 0.8)
    cono = sd_poligono(x, y, [(cx - 6, base - 1), (cx + 6, base - 1), (cx + 3, base - 10), (cx + 8, base - 13)])
    L.pintar(union(ala, cono) < 0, tono(rampa('0e1a0a', '1e2e14', '2e4420', '446030'), np.clip(0.6 - (x - cx) * 0.02, 0, 1)))
    L.pintar(sd_caja(x, y, cx, base - 2.5, 6, 1.0) < 0, H('6a3aa0')[:3])
    L.contorno(OSCURO)


def phantom(L, x, y, k, cx=16.0, cy=16.0, rampa_=rampa('0e1430', '1e2a5a', '30448a', '4a6ac0', '8aa8f0')):
    alas = sd_poligono(x, y, [(cx - 14, cy - 2), (cx - 4, cy - 5), (cx + 4, cy - 5), (cx + 14, cy - 2), (cx + 6, cy + 3),
                              (cx - 6, cy + 3)])
    L.pintar(alas < 0, tono(rampa_, np.clip(0.55 - np.abs(x - cx) * 0.012, 0, 1)))
    L.pintar(sd_elipse(x, y, cx, cy + 1, 4, 6) < 0, rampa_[1])
    for lado in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado * 2, cy - 1, 1.2, 0.8) < 0, H('7af08a')[:3])
    L.contorno(OSCURO)


def cara_warden(L, x, y, k, cx=16.0, cy=17.0, lado=11.0):
    cara = sd_caja(x, y, cx, cy, lado, lado * 0.9, 1.5)
    L.pintar(cara < 0, tono(R_WARDEN, np.clip(0.55 - (x - cx + y - cy) * 0.01, 0, 1)))
    for lado_ in (-1, 1):
        cuerno = sd_poligono(x, y, [(cx + lado_ * lado * 0.6, cy - lado * 0.8), (cx + lado_ * (lado + 4), cy - lado - 4),
                                    (cx + lado_ * lado * 0.95, cy - lado * 0.3)])
        L.pintar(cuerno < 0, H('2ab0b8')[:3])
    L.pintar(sd_caja(x, y, cx, cy + 3, lado * 0.55, 1.4) < 0, H('3ae8f0')[:3])
    for lado_ in (-1, 1):
        L.pintar(sd_circulo(x, y, cx + lado_ * 5, cy - 3, 1.6) < 0, H('8afcff')[:3])
    L.contorno(OSCURO)


def ballesta(L, x, y, k, cx=14.0, cy=18.0):
    L.pintar(sd_segmento(x, y, cx - 2, cy + 10, cx + 2, cy - 8, 1.6) < 0, H('8a5a26')[:3])
    arco = np.abs(sd_circulo(x, y, cx, cy + 6, 11)) - 1.2
    arco = np.where(y > cy - 1, 99, arco)
    L.pintar(arco < 0, R_MADERA[1])
    L.pintar(sd_segmento(x, y, cx - 10, cy + 1, cx + 10, cy + 1, 0.5) < 0, H('e8e8f0')[:3])
    L.contorno(OSCURO)


def cohete(L, x, y, k, cx=20.0, cy=12.0):
    cuerpo = sd_segmento(x, y, cx - 6, cy + 6, cx + 3, cy - 3, 2.6)
    L.pintar(cuerpo < 0, R_ROJO[2])
    L.pintar(sd_poligono(x, y, [(cx + 2, cy - 5), (cx + 7, cy - 7), (cx + 5, cy - 2)]) < 0, H('f8f0e0')[:3])
    for i in range(3):
        L.pintar(sd_circulo(x, y, cx - 9 - i * 2.2, cy + 9 + i * 2.2, 1.4 - i * 0.3) < 0, H('ffd23a')[:3])
    L.contorno(OSCURO)


def cara_piglin(L, x, y, k, cx=16.0, cy=16.0, lado=11.0):
    cara = sd_caja(x, y, cx, cy, lado, lado * 0.85, 1.0)
    L.pintar(cara < 0, tono(R_PIGLIN, np.clip(0.55 - (x - cx) * 0.015, 0, 1)))
    L.pintar(sd_caja(x, y, cx, cy + 4, 4.5, 3, 1) < 0, R_PIGLIN[3])
    for lado_ in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado_ * 1.6, cy + 4, 0.8, 1.2) < 0, H('3a1a10')[:3])
        L.pintar(sd_caja(x, y, cx + lado_ * 5, cy - 3, 1.5, 1.5) < 0, H('1a0a08')[:3])
        oreja = sd_poligono(x, y, [(cx + lado_ * lado, cy - 6), (cx + lado_ * (lado + 4), cy + 2), (cx + lado_ * lado, cy + 1)])
        L.pintar(oreja < 0, R_PIGLIN[1])
    L.contorno(OSCURO)


def pepita(L, x, y, k, cx=24.0, cy=24.0, r=5.0):
    d = sd_poligono(x, y, [(cx - r, cy), (cx - r * 0.3, cy - r), (cx + r, cy - r * 0.4), (cx + r * 0.6, cy + r * 0.7),
                           (cx - r * 0.4, cy + r * 0.8)])
    L.pintar(d < 0, tono(ORO, bisel(d, k, 1.5 * k, base=0.62)))
    L.contorno(H('3a2204')[:3])


def cara_blaze(L, x, y, k, cx=16.0, cy=13.0, lado=8.0):
    for i, a in enumerate((0.2, 1.4, 2.6, 3.8, 5.0)):
        rx = cx + math.cos(a) * 11
        L.pintar(sd_caja(x, y, rx, cy + 12 + (i % 2) * 2, 1.5, 4.5, 0.5) < 0, H('f0b020')[:3])
    cara = sd_caja(x, y, cx, cy, lado, lado, 0.8)
    L.pintar(cara < 0, tono(rampa('7a4a04', 'c08010', 'f0c030', 'fff070', 'fffcd0'), np.clip(0.55 - (x - cx) * 0.02, 0, 1)))
    for lado_ in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado_ * 3.5, cy - 1, 2.2, 1.2) < 0, H('1a0a04')[:3])
    L.contorno(OSCURO)


def moneda(L, x, y, k, cx=16.0, cy=16.0, r=11.0):
    d = sd_circulo(x, y, cx, cy, r)
    L.pintar(d < 0, tono(ORO, bisel(d, k, 2.2 * k, base=0.62)))
    L.pintar(np.abs(d + 3.0) < 0.6, ORO[1])
    L.contorno(H('3a2204')[:3])


def libro(L, x, y, k, cx=16.0, cy=17.0, rampa_=rampa('3a0a12', '6a1a24', '9a2a36', 'c84a5a', 'f08a9a'), brillo=False):
    L.pintar(sd_caja(x, y, cx, cy, 10, 12, 1.0) < 0, rampa_[1])
    L.pintar(sd_caja(x, y, cx + 1.5, cy, 8, 11, 0.5) < 0, H('f8f0dc')[:3])
    L.pintar(sd_caja(x, y, cx - 1, cy, 8, 12, 1.0) < 0, tono(rampa_, np.clip(0.6 - (x - cx) * 0.02, 0, 1)))
    if brillo:
        L.pintar(sd_circulo(x, y, cx - 1, cy, 3.5) < 0, H('c080ff')[:3])
    L.contorno(OSCURO)


def trigo(L, x, y, k, rampa_=rampa('3a2a0a', '6a5014', '9a7a2a', 'c8a84a', 'ead884')):
    for i, cx in enumerate((10, 16, 22)):
        L.pintar(sd_segmento(x, y, cx, 30, cx + (i - 1) * 2, 10, 0.9) < 0, rampa_[1])
        for j in range(4):
            L.pintar(sd_elipse(x, y, cx + (i - 1) * 2 - 1.4, 10 + j * 3, 1.6, 2.0) < 0, rampa_[3])
            L.pintar(sd_elipse(x, y, cx + (i - 1) * 2 + 1.4, 11.5 + j * 3, 1.6, 2.0) < 0, rampa_[2])
    L.contorno(OSCURO)


def brote(L, x, y, k, cx=16.0):
    L.pintar(sd_segmento(x, y, cx, 28, cx, 14, 1.2) < 0, H('5e3c18')[:3])
    for lado in (-1, 1):
        L.pintar(sd_elipse(x, y, cx + lado * 5, 13, 5, 3) < 0, R_VERDE[2 + (lado > 0)])
    L.pintar(sd_elipse(x, y, cx, 8, 3, 5) < 0, R_VERDE[3])
    L.pintar(sd_caja(x, y, cx, 29, 7, 2) < 0, R_TIERRA[2])
    L.contorno(OSCURO)


def cara_vaca(L, x, y, k, cx=16.0, cy=16.0):
    cara = sd_caja(x, y, cx, cy, 9, 9, 1)
    manchas = (sd_circulo(x, y, cx - 5, cy - 5, 4.5) < 0) | (sd_circulo(x, y, cx + 6, cy + 2, 3.5) < 0)
    L.pintar(cara < 0, np.where(manchas[..., None], np.array(H('2a1e14')[:3], float), np.array(H('f0eee8')[:3], float)))
    L.pintar(sd_caja(x, y, cx, cy + 5, 6, 3.5, 1) < 0, H('e8a8a0')[:3])
    for lado in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado * 1.8, cy + 5, 0.8, 1) < 0, H('3a1a14')[:3])
        L.pintar(sd_caja(x, y, cx + lado * 4, cy - 2, 1.2, 1.2) < 0, H('0a0a0a')[:3])
        L.pintar(sd_segmento(x, y, cx + lado * 8, cy - 8, cx + lado * 12, cy - 11, 1.0) < 0, H('e8e0c8')[:3])
    L.contorno(OSCURO)


def panal(L, x, y, k, cx=16.0, cy=16.0):
    d = sd_caja(x, y, cx, cy, 11, 11, 1)
    L.pintar(d < 0, tono(rampa('6a4a10', 'a87a1e', 'e0b040', 'f8d870', 'fff2b8'),
                         np.clip(0.55 + ((np.floor(x / 4) + np.floor(y / 4)) % 2) * 0.1 - (x - cx) * 0.01, 0, 1)))
    L.pintar(sd_elipse(x, y, cx, cy + 2, 4.5, 3) < 0, H('3a2404')[:3])
    L.contorno(OSCURO)


def estalactita(L, x, y, k, cx=16.0, arriba=3.0, abajo=28.0, ancho=6.5,
                rampa_=rampa('3a2a20', '5e4a3a', '8a7460', 'b8a088', 'e0ccb4')):
    d = sd_poligono(x, y, [(cx - ancho, arriba), (cx + ancho, arriba), (cx, abajo)])
    L.pintar(d < 0, tono(rampa_, np.clip(0.65 - (x - cx) * 0.04, 0, 1)))
    for yy in (9, 15):
        L.pintar((np.abs(y - yy) < 0.6) & (d < 0), rampa_[1])
    L.contorno(OSCURO)


def ojo_insomne(L, x, y, k, cx=16.0, cy=16.0, r=9.0):
    """El ojo de quien no duerme: muy abierto, inyectado en sangre, con ojeras moradas debajo."""
    blanco = sd_elipse(x, y, cx, cy, r * 1.3, r * 0.75)
    L.pintar(blanco < 0, tono(R_BLANCO, esfera(x, y, cx - 2, cy - 2, r * 1.3, r, amb=0.5)))
    L.pintar(sd_circulo(x, y, cx, cy, r * 0.5) < 0, H('6a1a1a')[:3])
    L.pintar(sd_circulo(x, y, cx, cy, r * 0.22) < 0, H('0a0410')[:3])
    for i in range(3):
        L.pintar(sd_segmento(x, y, cx - r * 1.0 + i * r, cy - r * 0.5, cx - r * 1.0 + i * r + 1.5, cy - r * 0.15, 0.5) < 0,
                 H('e8322a')[:3])
    ojera = np.abs(sd_elipse(x, y, cx, cy + 2.5, r * 1.25, r * 0.85)) - 0.8
    L.pintar((ojera < 0) & (y > cy + 3), H('6a3aa0')[:3])
    L.contorno(OSCURO)


def corazon_mini(L, x, y, k, cx, cy, esc=7.0):
    d = sd_corazon(x, y, cx, cy + esc * 0.6, esc)
    L.pintar(d < 0, tono(R_ROJO, esfera(x, y, cx - 2, cy - 2, esc * 0.6, esc * 0.6, amb=0.3)))
    L.contorno(H('1a0204')[:3])


def montana(L, x, y, k):
    d = sd_poligono(x, y, [(2, 28), (12, 9), (18, 18), (22, 13), (30, 28)])
    L.pintar(d < 0, tono(R_PIEDRA, np.clip(0.5 - (x - 14) * 0.015 + (y < 14) * 0.3, 0, 1)))
    L.pintar(sd_poligono(x, y, [(9.5, 14), (12, 9), (14.5, 13), (12, 12)]) < 0, H('ffffff')[:3])
    L.contorno(OSCURO)


def onda(L, x, y, k, cy=24.0, rampa_=R_AGUA, contorno='041a3a'):
    d = y - (cy + np.sin(x * 0.55) * 1.8)
    L.pintar((d > 0) & (y < 31), tono(rampa_, np.clip(0.75 - (y - cy) * 0.05, 0, 1)))
    L.contorno(H(contorno)[:3])


def piedra_afilar(L, x, y, k, cx=16.0, cy=15.0):
    rueda = sd_circulo(x, y, cx, cy, 9)
    L.pintar(rueda < 0, tono(R_PIEDRA, esfera(x, y, cx - 2, cy - 2, 9, 9, amb=0.35)))
    L.pintar(sd_circulo(x, y, cx, cy, 2) < 0, R_MADERA[1])
    for lado in (-1, 1):
        L.pintar(sd_caja(x, y, cx + lado * 10, cy + 6, 1.6, 8, 0.5) < 0, R_MADERA[2])
    L.contorno(OSCURO)
